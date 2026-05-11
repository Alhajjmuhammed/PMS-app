from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
from datetime import date, datetime
import logging

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

logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='user', rate='100/m', method='GET', block=False), name='dispatch')
class ReservationListView(generics.ListCreateAPIView):
    """
    List all reservations or create a new reservation.
    
    GET:
    Returns a paginated list of reservations with filtering, search, and ordering capabilities.
    
    Query Parameters:
    - status: Filter by reservation status (PENDING, CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED, NO_SHOW)
    - source: Filter by booking source (WALK_IN, PHONE, WEBSITE, OTA, CORPORATE)
    - check_in_date: Filter by check-in date
    - check_out_date: Filter by check-out date
    - start_date: Filter reservations checking in after this date
    - end_date: Filter reservations checking out before this date
    - search: Search by confirmation number, guest name, or email
    - ordering: Sort results (check_in_date, created_at, total_amount)
    - page: Page number for pagination
    - page_size: Number of results per page
    
    POST:
    Create a new reservation. Requires room type, dates, and guest information.
    
    Example GET:
    ```
    GET /api/v1/reservations/?status=CONFIRMED&start_date=2026-04-15&ordering=-check_in_date
    ```
    
    Example POST:
    ```
    POST /api/v1/reservations/
    {
      "guest_id": 1,
      "room_type_id": 2,
      "check_in_date": "2026-04-15",
      "check_out_date": "2026-04-20",
      "adults": 2,
      "children": 1,
      "room_rate": 150.00,
      "special_requests": "Late check-out if possible"
    }
    ```
    """
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

        # Filter by property to enforce data isolation
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)

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
        qs = Reservation.objects.select_related(
            'guest', 'hotel', 'created_by'
        ).prefetch_related(
            'rooms__room__room_type'
        )
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
        return qs


class ReservationCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Get or create guest
        if 'guest_id' in data:
            prop = request.user.assigned_property
            # Scope to guests belonging to this property (uses home_property isolation)
            guest_qs = Guest.objects.filter(home_property=prop) if prop else Guest.objects.all()
            guest = get_object_or_404(guest_qs, pk=data['guest_id'])
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

        # Look up room type early so we can use its base_rate as fallback
        prop = request.user.assigned_property
        room_type = get_object_or_404(RoomType, pk=data['room_type_id'])

        nightly_rate = data.get('room_rate') or room_type.base_rate
        total = nightly_rate * nights
        
        # Create reservation
        reservation = Reservation.objects.create(
            hotel=data.get('hotel') or prop,
            guest=guest,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=data.get('adults', 1),
            children=data.get('children', 0),
            source=data.get('source', 'DIRECT'),
            total_amount=total,
            special_requests=data.get('special_requests', ''),
            created_by=request.user
        )
        
        # Create reservation room
        ReservationRoom.objects.create(
            reservation=reservation,
            room_type=room_type,
            rate_per_night=nightly_rate,
            total_rate=total,
            adults=data.get('adults', 1),
            children=data.get('children', 0)
        )
        
        return Response(
            ReservationSerializer(reservation).data,
            status=status.HTTP_201_CREATED
        )


@method_decorator(ratelimit(key='user', rate='30/m', method='POST', block=False), name='dispatch')
class CancelReservationView(APIView):
    """
    Cancel an existing reservation.
    
    Cancels a reservation and updates its status. Cannot cancel reservations
    that are already checked in.
    
    POST Parameters:
    - reason (optional): Cancellation reason
    
    Returns:
    - Updated reservation with CANCELLED status
    
    Errors:
    - 404: Reservation not found
    - 400: Cannot cancel checked-in reservation
    - 429: Rate limit exceeded
    
    Example:
    ```
    POST /api/v1/reservations/123/cancel/
    {
      "reason": "Guest changed travel plans"
    }
    ```
    """
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request, pk):
        # Check if rate limited
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        try:
            qs = Reservation.objects.all()
            if request.user.assigned_property:
                qs = qs.filter(hotel=request.user.assigned_property)
            reservation = qs.get(pk=pk)
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


class ConfirmReservationView(APIView):
    """Set reservation status to CONFIRMED. Only valid from PENDING."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]

    def post(self, request, pk):
        try:
            qs = Reservation.objects.all()
            if request.user.assigned_property:
                qs = qs.filter(hotel=request.user.assigned_property)
            reservation = qs.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)

        if reservation.status not in ('PENDING', 'WAITLIST'):
            return Response(
                {'error': f'Cannot confirm a reservation with status {reservation.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = 'CONFIRMED'
        reservation.modified_by = request.user
        reservation.save(update_fields=['status', 'modified_by'])
        return Response(ReservationSerializer(reservation).data)


class NoShowView(APIView):
    """Mark a reservation as NO_SHOW. Only valid from CONFIRMED or PENDING."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]

    def post(self, request, pk):
        try:
            qs = Reservation.objects.all()
            if request.user.assigned_property:
                qs = qs.filter(hotel=request.user.assigned_property)
            reservation = qs.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)

        if reservation.status not in ('PENDING', 'CONFIRMED'):
            return Response(
                {'error': f'Cannot mark as no-show a reservation with status {reservation.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = 'NO_SHOW'
        reservation.modified_by = request.user
        reservation.save(update_fields=['status', 'modified_by'])
        return Response(ReservationSerializer(reservation).data)


class ReservationCheckoutView(APIView):
    """
    Check out a guest. Looks up the CheckIn record by reservation, then
    sets reservation to CHECKED_OUT and room to vacant-dirty.
    """
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]

    def post(self, request, pk):
        from apps.frontdesk.models import CheckIn, CheckOut

        try:
            qs = Reservation.objects.all()
            if request.user.assigned_property:
                qs = qs.filter(hotel=request.user.assigned_property)
            reservation = qs.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)

        if reservation.status != 'CHECKED_IN':
            return Response(
                {'error': 'Only CHECKED_IN reservations can be checked out'},
                status=status.HTTP_400_BAD_REQUEST
            )

        check_in = CheckIn.objects.filter(reservation=reservation).first()
        if not check_in:
            return Response({'error': 'No check-in record found for this reservation'}, status=status.HTTP_400_BAD_REQUEST)

        # Create check-out record
        check_out = CheckOut.objects.create(
            check_in=check_in,
            checked_out_by=request.user,
        )

        # Update reservation status
        reservation.status = 'CHECKED_OUT'
        reservation.modified_by = request.user
        reservation.save(update_fields=['status', 'modified_by'])

        # Update room to vacant-dirty
        room = check_in.room
        if room:
            room.status = 'VD'
            room.fo_status = 'VACANT'
            room.save(update_fields=['status', 'fo_status'])

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
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
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
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
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
            
        except (ValidationError, ValueError, TypeError) as e:
            logger.error(f"Availability check error: {str(e)}")
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
            
        except (ValidationError, ValueError) as e:
            logger.error(f"Availability calendar error: {str(e)}")
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
            
        except (ValidationError, ValueError, KeyError) as e:
            logger.error(f"Pricing calculation error: {str(e)}")
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
            
        except (ValidationError, ValueError, KeyError) as e:
            logger.error(f"Rate plan comparison error: {str(e)}")
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
        prop = self.request.user.assigned_property
        if prop:
            serializer.save(created_by=self.request.user, hotel=prop)
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
        prop = request.user.assigned_property
        gb_qs = GroupBooking.objects.filter(hotel=prop) if prop else GroupBooking.objects.all()
        group_booking = get_object_or_404(gb_qs, pk=pk)
        
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
        prop = request.user.assigned_property
        gb_qs = GroupBooking.objects.filter(hotel=prop) if prop else GroupBooking.objects.all()
        group_booking = get_object_or_404(gb_qs, pk=pk)
        
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
        prop = request.user.assigned_property
        gb_qs = GroupBooking.objects.filter(hotel=prop) if prop else GroupBooking.objects.all()
        group_booking = get_object_or_404(gb_qs, pk=pk)
        
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