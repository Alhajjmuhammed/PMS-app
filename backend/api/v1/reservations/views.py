from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date, datetime
from apps.reservations.models import Reservation, ReservationRoom, GroupBooking
from apps.reservations.services import AvailabilityService
from apps.rates.services import PricingService
from apps.guests.models import Guest
from apps.rooms.models import RoomType
from api.permissions import IsFrontDeskOrAbove
from .serializers import (
    ReservationSerializer, ReservationCreateSerializer,
    GroupBookingSerializer, GroupBookingCreateSerializer, GroupBookingUpdateSerializer
)


class ReservationListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = ReservationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'source', 'check_in_date', 'check_out_date']
    search_fields = ['confirmation_number', 'guest__first_name', 'guest__last_name', 'guest__email']
    ordering_fields = ['check_in_date', 'created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReservationCreateSerializer
        return ReservationSerializer
    
    def get_queryset(self):
        qs = Reservation.objects.select_related('guest', 'hotel').prefetch_related('rooms')
        
        # Filter by user's property if staff user has property assigned
        # Note: User model doesn't have property field by default
        # This would need to be customized based on your User model
        
        # Date range filter
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            qs = qs.filter(check_in_date__gte=start_date)
        if end_date:
            qs = qs.filter(check_out_date__lte=end_date)
        
        return qs


class ReservationDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = ReservationSerializer
    
    def get_queryset(self):
        return Reservation.objects.select_related(
            'guest', 'hotel', 'created_by'
        ).prefetch_related(
            'rooms__room__room_type',
            'rooms__rate_plan'
        )


class ReservationCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Get or create guest
        if 'guest_id' in data:
            guest = Guest.objects.get(pk=data['guest_id'])
        else:
            guest, created = Guest.objects.get_or_create(
                email=data.get('guest_email'),
                defaults={
                    'first_name': data.get('guest_first_name', ''),
                    'last_name': data.get('guest_last_name', ''),
                    'phone': data.get('guest_phone', ''),
                }
            )
        
        # Calculate total
        check_in = data['check_in_date']
        check_out = data['check_out_date']
        nights = (check_out - check_in).days
        total = data['room_rate'] * nights
        
        # Create reservation
        reservation = Reservation.objects.create(
            property=data['property'],
            guest=guest,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=data.get('adults', 1),
            children=data.get('children', 0),
            room_rate=data['room_rate'],
            total_amount=total,
            special_requests=data.get('special_requests', ''),
            created_by=request.user
        )
        
        # Create reservation room
        room_type = RoomType.objects.get(pk=data['room_type_id'])
        ReservationRoom.objects.create(
            reservation=reservation,
            room_type=room_type,
            rate=data['room_rate'],
            adults=data.get('adults', 1),
            children=data.get('children', 0)
        )
        
        return Response(
            ReservationSerializer(reservation).data,
            status=status.HTTP_201_CREATED
        )


class CancelReservationView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request, pk):
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if reservation.status == 'CHECKED_IN':
            return Response(
                {'error': 'Cannot cancel checked-in reservation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'CANCELLED'
        reservation.cancelled_at = timezone.now()
        reservation.cancelled_by = request.user
        reservation.cancellation_reason = request.data.get('reason', '')
        reservation.save()
        
        return Response(ReservationSerializer(reservation).data)


class ArrivalsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = ReservationSerializer
    
    def get_queryset(self):
        arrival_date = self.request.query_params.get('date', date.today().isoformat())
        
        qs = Reservation.objects.filter(
            check_in_date=arrival_date,
            status__in=['CONFIRMED', 'PENDING']
        )
        
        return qs


class DeparturesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = ReservationSerializer
    
    def get_queryset(self):
        departure_date = self.request.query_params.get('date', date.today().isoformat())
        
        qs = Reservation.objects.filter(
            check_out_date=departure_date,
            status='CHECKED_IN'
        )
        
        return qs


class CheckAvailabilityView(APIView):
    """Check room availability for given dates."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request):
        try:
            hotel_id = request.data.get('hotel_id') or request.data.get('property_id')
            room_type_id = request.data.get('room_type_id')
            check_in = datetime.fromisoformat(request.data.get('check_in_date')).date()
            check_out = datetime.fromisoformat(request.data.get('check_out_date')).date()
            count = request.data.get('count', 1)
            
            # Validate dates
            is_valid, error_msg = AvailabilityService.validate_booking_dates(check_in, check_out)
            if not is_valid:
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get available rooms
            available_rooms = AvailabilityService.get_available_rooms(
                hotel_id, room_type_id, check_in, check_out, count
            )
            
            result = {
                'available': available_rooms.exists(),
                'count': available_rooms.count(),
                'rooms': list(available_rooms.values('id', 'room_number', 'room_type__name'))
            }
            
            # If not available, suggest alternatives
            if not available_rooms.exists() and room_type_id:
                result['alternatives'] = AvailabilityService.suggest_alternative_rooms(
                    hotel_id, room_type_id, check_in, check_out
                )
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AvailabilityCalendarView(APIView):
    """Get availability calendar for a date range."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        try:
            hotel_id = request.query_params.get('hotel_id') or request.query_params.get('property_id')
            room_type_id = request.query_params.get('room_type_id')
            start_date = datetime.fromisoformat(request.query_params.get('start_date')).date()
            end_date = datetime.fromisoformat(request.query_params.get('end_date')).date()
            
            calendar = AvailabilityService.get_availability_calendar(
                hotel_id, room_type_id, start_date, end_date
            )
            
            return Response({
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'calendar': calendar
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CalculatePriceView(APIView):
    """Calculate pricing for a reservation."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request):
        try:
            room_type_id = request.data.get('room_type_id')
            rate_plan_id = request.data.get('rate_plan_id')
            check_in = datetime.fromisoformat(request.data.get('check_in_date')).date()
            check_out = datetime.fromisoformat(request.data.get('check_out_date')).date()
            adults = request.data.get('adults', 1)
            children = request.data.get('children', 0)
            
            pricing = PricingService.calculate_room_rate(
                room_type_id, rate_plan_id, check_in, check_out, adults, children
            )
            
            if 'error' in pricing:
                return Response(pricing, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(pricing)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CompareRatesView(APIView):
    """Compare rates across all rate plans."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request):
        try:
            property_id = request.data.get('property_id')
            room_type_id = request.data.get('room_type_id')
            check_in = datetime.fromisoformat(request.data.get('check_in_date')).date()
            check_out = datetime.fromisoformat(request.data.get('check_out_date')).date()
            
            comparisons = PricingService.get_rate_comparison(
                room_type_id, check_in, check_out, property_id
            )
            
            return Response({
                'room_type_id': room_type_id,
                'check_in_date': check_in.isoformat(),
                'check_out_date': check_out.isoformat(),
                'rate_plans': comparisons
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============= Group Booking Views =============

class GroupBookingListCreateView(generics.ListCreateAPIView):
    """List all group bookings or create a new one."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['hotel', 'status', 'check_in_date', 'check_out_date']
    search_fields = ['name', 'code', 'contact_name', 'contact_email']
    ordering_fields = ['check_in_date', 'created_at', 'rooms_blocked']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = GroupBooking.objects.select_related(
            'hotel', 'company', 'created_by'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(hotel=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GroupBookingCreateSerializer
        return GroupBookingSerializer
    
    def perform_create(self, serializer):
        # Auto-assign property if user has one and hotel not specified
        if self.request.user.assigned_property and 'hotel' not in serializer.validated_data:
            serializer.save(created_by=self.request.user, hotel=self.request.user.assigned_property)
        else:
            serializer.save(created_by=self.request.user)


class GroupBookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a group booking."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get_queryset(self):
        queryset = GroupBooking.objects.select_related(
            'hotel', 'company', 'created_by'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(hotel=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return GroupBookingUpdateSerializer
        return GroupBookingSerializer


class GroupBookingRoomPickupView(APIView):
    """Update room pickup for a group booking."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request, pk):
        group_booking = get_object_or_404(GroupBooking, pk=pk)
        
        # Check access
        if request.user.assigned_property:
            if group_booking.hotel != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get pickup count from request
        pickup_count = request.data.get('rooms_picked_up')
        if pickup_count is None:
            return Response(
                {'error': 'rooms_picked_up is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pickup_count = int(pickup_count)
        except (ValueError, TypeError):
            return Response(
                {'error': 'rooms_picked_up must be a number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate pickup count
        if pickup_count < 0:
            return Response(
                {'error': 'rooms_picked_up cannot be negative'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if pickup_count > group_booking.rooms_blocked:
            return Response(
                {'error': 'rooms_picked_up cannot exceed rooms_blocked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update pickup
        group_booking.rooms_picked_up = pickup_count
        group_booking.save()
        
        return Response(GroupBookingSerializer(group_booking).data)


class GroupBookingConfirmView(APIView):
    """Confirm a tentative group booking."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request, pk):
        group_booking = get_object_or_404(GroupBooking, pk=pk)
        
        # Check access
        if request.user.assigned_property:
            if group_booking.hotel != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if already confirmed
        if group_booking.status == GroupBooking.Status.CONFIRMED:
            return Response(
                {'error': 'Group booking is already confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if cancelled
        if group_booking.status == GroupBooking.Status.CANCELLED:
            return Response(
                {'error': 'Cannot confirm cancelled group booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Confirm the booking
        group_booking.status = GroupBooking.Status.CONFIRMED
        group_booking.save()
        
        return Response(GroupBookingSerializer(group_booking).data)


class GroupBookingCancelView(APIView):
    """Cancel a group booking."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request, pk):
        group_booking = get_object_or_404(GroupBooking, pk=pk)
        
        # Check access
        if request.user.assigned_property:
            if group_booking.hotel != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if already cancelled
        if group_booking.status == GroupBooking.Status.CANCELLED:
            return Response(
                {'error': 'Group booking is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel the booking
        group_booking.status = GroupBooking.Status.CANCELLED
        group_booking.save()
        
        return Response(GroupBookingSerializer(group_booking).data)