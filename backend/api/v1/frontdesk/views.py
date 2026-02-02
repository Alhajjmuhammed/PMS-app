from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count
from datetime import date
from decimal import Decimal
from apps.reservations.models import Reservation
from apps.rooms.models import Room
from apps.frontdesk.models import CheckIn, CheckOut, RoomMove, WalkIn
from apps.billing.models import Folio
from apps.guests.models import Guest
from api.permissions import IsFrontDeskOrAbove
from api.v1.billing.serializers import FolioCreateSerializer
from .serializers import (
    CheckInSerializer, CheckOutSerializer, 
    CheckInRequestSerializer, CheckOutRequestSerializer, RoomMoveSerializer,
    WalkInSerializer, WalkInCreateSerializer, WalkInUpdateSerializer
)
from api.v1.reservations.serializers import ReservationSerializer


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        today = date.today()
        property_obj = request.user.assigned_property
        
        # Room statistics
        rooms = Room.objects.filter(is_active=True)
        if property_obj:
            rooms = rooms.filter(property=property_obj)
        
        room_stats = rooms.values('status').annotate(count=Count('id'))
        room_stats_dict = {stat['status']: stat['count'] for stat in room_stats}
        
        # Reservation statistics
        reservations = Reservation.objects
        if property_obj:
            reservations = reservations.filter(property=property_obj)
        
        arrivals = reservations.filter(
            check_in_date=today,
            status__in=['CONFIRMED', 'PENDING']
        ).count()
        
        departures = reservations.filter(
            check_out_date=today,
            status='CHECKED_IN'
        ).count()
        
        in_house = reservations.filter(status='CHECKED_IN').count()
        
        return Response({
            'date': today,
            'rooms': {
                'total': rooms.count(),
                'vacant_clean': room_stats_dict.get('VC', 0),
                'vacant_dirty': room_stats_dict.get('VD', 0),
                'occupied_clean': room_stats_dict.get('OC', 0),
                'occupied_dirty': room_stats_dict.get('OD', 0),
                'out_of_order': room_stats_dict.get('OOO', 0),
            },
            'arrivals': arrivals,
            'departures': departures,
            'in_house': in_house,
        })


class CheckInView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request):
        serializer = CheckInRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            reservation = Reservation.objects.get(pk=data['reservation_id'])
            room = Room.objects.get(pk=data['room_id'])
        except (Reservation.DoesNotExist, Room.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate room is available
        if room.status not in ['VC', 'VD']:
            return Response(
                {'error': 'Room is not available for check-in'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate reservation hasn't already been checked in
        if CheckIn.objects.filter(reservation=reservation).exists():
            return Response(
                {'error': 'Reservation has already been checked in'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Auto-create folio if it doesn't exist
        folio = Folio.objects.filter(reservation=reservation, status='OPEN').first()
        if not folio:
            folio_data = {
                'reservation': reservation.id,
                'guest': reservation.guest.id,
                'folio_type': 'STANDARD',
                'property': reservation.property.id,
                'currency': 'USD',
                'balance': Decimal('0.00')
            }
            folio_serializer = FolioCreateSerializer(data=folio_data, context={'request': request})
            if folio_serializer.is_valid():
                folio = folio_serializer.save()
            else:
                return Response(
                    {'error': 'Failed to create folio', 'details': folio_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create check-in
        check_in = CheckIn.objects.create(
            reservation=reservation,
            room=room,
            checked_in_by=request.user,
            id_verified=data.get('id_verified', True),
            key_cards_issued=data.get('key_cards_issued', 2)
        )
        
        # Update reservation status
        reservation.status = 'CHECKED_IN'
        reservation.save()
        
        # Update room status
        room.status = 'OC'
        room.fo_status = 'OCCUPIED'
        room.save()
        
        response_data = CheckInSerializer(check_in).data
        response_data['folio_id'] = folio.id
        response_data['folio_number'] = folio.folio_number
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class CheckOutView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request):
        serializer = CheckOutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            check_in = CheckIn.objects.get(pk=data['check_in_id'])
        except CheckIn.DoesNotExist:
            return Response({'error': 'Check-in not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create check-out
        check_out = CheckOut.objects.create(
            check_in=check_in,
            checked_out_by=request.user,
            key_cards_returned=data.get('key_cards_returned', 0),
            late_check_out=data.get('late_check_out', False),
            late_charge=data.get('late_charge', 0)
        )
        
        # Update reservation status
        check_in.reservation.status = 'CHECKED_OUT'
        check_in.reservation.save()
        
        # Update room status to dirty
        check_in.room.status = 'VD'
        check_in.room.fo_status = 'VACANT'
        check_in.room.save()
        
        return Response(CheckOutSerializer(check_out).data, status=status.HTTP_201_CREATED)


class RoomMoveView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request):
        serializer = RoomMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            check_in = CheckIn.objects.get(pk=data['check_in_id'])
            new_room = Room.objects.get(pk=data['new_room_id'])
        except (CheckIn.DoesNotExist, Room.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        old_room = check_in.room
        
        # Create room move record
        RoomMove.objects.create(
            check_in=check_in,
            from_room=old_room,
            to_room=new_room,
            reason=data['reason'],
            moved_by=request.user
        )
        
        # Update room statuses
        old_room.status = 'VD'
        old_room.fo_status = 'VACANT'
        old_room.save()
        
        new_room.status = 'OC'
        new_room.fo_status = 'OCCUPIED'
        new_room.save()
        
        # Update check-in
        check_in.room = new_room
        check_in.save()
        
        return Response({'message': 'Room move completed'})


class CheckInWithIDView(APIView):
    """Check-in view with reservation ID in URL."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request, pk):
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if reservation.status != 'CONFIRMED':
            return Response({'error': 'Reservation must be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use CheckInView logic
        serializer = CheckInRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create check-in record
        check_in = CheckIn.objects.create(
            reservation=reservation,
            room=serializer.validated_data.get('room'),
            check_in_time=timezone.now(),
            checked_in_by=request.user,
            notes=serializer.validated_data.get('notes', '')
        )
        
        reservation.status = 'CHECKED_IN'
        reservation.save()
        
        return Response(CheckInSerializer(check_in).data, status=status.HTTP_201_CREATED)


class CheckOutWithIDView(APIView):
    """Check-out view with reservation ID in URL."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request, pk):
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if reservation.status != 'CHECKED_IN':
            return Response({'error': 'Reservation must be checked in'}, status=status.HTTP_400_BAD_REQUEST)
        
        check_in = CheckIn.objects.filter(reservation=reservation).first()
        if not check_in:
            return Response({'error': 'Check-in record not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CheckOutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create check-out record
        check_out = CheckOut.objects.create(
            check_in=check_in,
            check_out_time=timezone.now(),
            checked_out_by=request.user,
            notes=serializer.validated_data.get('notes', '')
        )
        
        reservation.status = 'CHECKED_OUT'
        reservation.save()
        
        return Response(CheckOutSerializer(check_out).data, status=status.HTTP_201_CREATED)


class ArrivalsView(APIView):
    """Get today's expected arrivals."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        date_param = request.query_params.get('date')
        target_date = date.fromisoformat(date_param) if date_param else date.today()
        
        property_obj = request.user.assigned_property
        reservations = Reservation.objects.filter(
            check_in_date=target_date,
            status__in=['CONFIRMED', 'PENDING']
        ).select_related('guest', 'hotel')
        
        if property_obj:
            reservations = reservations.filter(hotel=property_obj)
        
        return Response(ReservationSerializer(reservations, many=True).data)


class DeparturesView(APIView):
    """Get today's expected departures."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        date_param = request.query_params.get('date')
        target_date = date.fromisoformat(date_param) if date_param else date.today()
        
        property_obj = request.user.assigned_property
        reservations = Reservation.objects.filter(
            check_out_date=target_date,
            status='CHECKED_IN'
        ).select_related('guest', 'hotel')
        
        if property_obj:
            reservations = reservations.filter(hotel=property_obj)
        
        return Response(ReservationSerializer(reservations, many=True).data)


class InHouseView(APIView):
    """Get currently checked-in guests."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        property_obj = request.user.assigned_property
        reservations = Reservation.objects.filter(
            status='CHECKED_IN'
        ).select_related('guest', 'hotel')
        
        if property_obj:
            reservations = reservations.filter(hotel=property_obj)
        
        return Response(ReservationSerializer(reservations, many=True).data)


# ============= Walk-In Views =============

class WalkInListCreateView(generics.ListCreateAPIView):
    """List all walk-ins or create a new one."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property', 'room_type', 'is_converted', 'check_in_date']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['check_in_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = WalkIn.objects.select_related(
            'property', 'room_type', 'reservation', 'created_by'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WalkInCreateSerializer
        return WalkInSerializer
    
    def perform_create(self, serializer):
        # Auto-assign property if user has one and property not specified
        if self.request.user.assigned_property and 'property' not in serializer.validated_data:
            serializer.save(created_by=self.request.user, property=self.request.user.assigned_property)
        else:
            serializer.save(created_by=self.request.user)


class WalkInDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a walk-in."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get_queryset(self):
        queryset = WalkIn.objects.select_related(
            'property', 'room_type', 'reservation', 'created_by'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return WalkInUpdateSerializer
        return WalkInSerializer
    
    def perform_destroy(self, instance):
        # Prevent deletion if already converted
        if instance.is_converted:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Cannot delete walk-in that has been converted to reservation")
        instance.delete()


class ConvertWalkInView(APIView):
    """Convert a walk-in to a full reservation."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def post(self, request, pk):
        walk_in = get_object_or_404(WalkIn, pk=pk)
        
        # Check access
        if request.user.assigned_property:
            if walk_in.property != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if already converted
        if walk_in.is_converted:
            return Response(
                {'error': 'Walk-in has already been converted to reservation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create or find guest
            guest, created = Guest.objects.get_or_create(
                email=walk_in.email if walk_in.email else f"walkin_{walk_in.id}@temp.com",
                defaults={
                    'first_name': walk_in.first_name,
                    'last_name': walk_in.last_name,
                    'phone': walk_in.phone,
                }
            )
            
            # If guest exists, update info
            if not created:
                guest.first_name = walk_in.first_name
                guest.last_name = walk_in.last_name
                guest.phone = walk_in.phone
                guest.save()
            
            # Calculate total nights and amount
            nights = (walk_in.check_out_date - walk_in.check_in_date).days
            total_amount = walk_in.rate_per_night * nights
            
            # Create reservation
            import uuid
            confirmation_number = f"WI{uuid.uuid4().hex[:8].upper()}"
            
            reservation = Reservation.objects.create(
                confirmation_number=confirmation_number,
                hotel=walk_in.property,
                guest=guest,
                check_in_date=walk_in.check_in_date,
                check_out_date=walk_in.check_out_date,
                adults=walk_in.adults,
                children=walk_in.children,
                status=Reservation.Status.CONFIRMED,
                source=Reservation.Source.WALK_IN,
                total_amount=total_amount,
                special_requests=walk_in.notes
            )
            
            # Link walk-in to reservation
            walk_in.is_converted = True
            walk_in.reservation = reservation
            walk_in.save()
            
            return Response({
                'message': 'Walk-in successfully converted to reservation',
                'reservation': ReservationSerializer(reservation).data,
                'walk_in': WalkInSerializer(walk_in).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to convert walk-in: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
