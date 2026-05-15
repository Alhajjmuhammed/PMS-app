from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import date
from decimal import Decimal
import logging

from apps.reservations.models import Reservation, ReservationRoom
from apps.rooms.models import Room
from apps.frontdesk.models import CheckIn, CheckOut, RoomMove, WalkIn
from apps.billing.models import Folio, FolioCharge, ChargeCode
from apps.housekeeping.models import HousekeepingTask
from apps.guests.models import Guest
from api.permissions import IsFrontDeskOrAbove
from .serializers import (
    CheckInSerializer, CheckOutSerializer, 
    CheckInRequestSerializer, CheckOutRequestSerializer, RoomMoveSerializer,
    WalkInSerializer, WalkInCreateSerializer, WalkInUpdateSerializer
)
from api.v1.reservations.serializers import ReservationSerializer

logger = logging.getLogger(__name__)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        today = date.today()
        property_obj = request.user.assigned_property
        
        # Room statistics
        rooms = Room.objects.filter(is_active=True)
        if property_obj:
            rooms = rooms.filter(hotel=property_obj)
        
        room_stats = rooms.values('status').annotate(count=Count('id'))
        room_stats_dict = {stat['status']: stat['count'] for stat in room_stats}
        
        # Reservation statistics
        reservations = Reservation.objects
        if property_obj:
            reservations = reservations.filter(hotel=property_obj)
        
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

    @transaction.atomic
    def post(self, request):
        serializer = CheckInRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        prop = request.user.assigned_property
        try:
            res_qs = Reservation.objects.all()
            room_qs = Room.objects.all()
            if prop:
                res_qs = res_qs.filter(hotel=prop)
                room_qs = room_qs.filter(hotel=prop)
            reservation = res_qs.get(pk=data['reservation_id'])
            room = room_qs.get(pk=data['room_id'])
        except (Reservation.DoesNotExist, Room.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        # Validate reservation is in a checkable-in state
        if reservation.status not in ['CONFIRMED', 'PENDING']:
            return Response(
                {'error': f'Cannot check in a reservation with status {reservation.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
            import uuid as _uuid
            folio = Folio.objects.create(
                folio_number=f"F-{_uuid.uuid4().hex[:8].upper()}",
                folio_type='GUEST',
                reservation=reservation,
                guest=reservation.guest,
            )
        
        # Create check-in
        import uuid as _uuid2
        reg_number = f"REG-{_uuid2.uuid4().hex[:10].upper()}"
        check_in = CheckIn.objects.create(
            reservation=reservation,
            room=room,
            guest=reservation.guest,
            checked_in_by=request.user,
            expected_check_out=reservation.check_out_date,
            registration_number=reg_number,
        )
        
        # Update reservation status
        reservation.status = 'CHECKED_IN'
        reservation.save()
        
        # Update room status
        room.status = 'OC'
        room.fo_status = 'OCCUPIED'
        room.save()

        # Assign the checked-in room to the ReservationRoom record,
        # or create one if none exists (international standard: always track the physical room)
        unassigned_rr = reservation.rooms.filter(room__isnull=True).first()
        if unassigned_rr:
            unassigned_rr.room = room
            unassigned_rr.save(update_fields=['room'])
        elif not reservation.rooms.exists():
            room_type = room.room_type
            rate = room_type.base_rate if room_type else Decimal('0')
            nights_count = (reservation.check_out_date - reservation.check_in_date).days or 1
            ReservationRoom.objects.create(
                reservation=reservation,
                room=room,
                room_type=room_type,
                rate_per_night=rate,
                total_rate=rate * nights_count,
                adults=reservation.adults,
                children=reservation.children,
            )

        # Post first night's room rate charge immediately (international standard)
        charge_date = check_in.check_in_time.date() if check_in.check_in_time else date.today()
        charge_code, _ = ChargeCode.objects.get_or_create(
            code='ROOM',
            defaults={
                'name': 'Room Rate',
                'category': 'ROOM',
                'default_amount': Decimal('0'),
            }
        )
        for res_room in reservation.rooms.all():
            already_posted = FolioCharge.objects.filter(
                folio=folio,
                charge_code=charge_code,
                charge_date=charge_date,
                description__contains=str(charge_date),
            ).exists()
            if already_posted:
                continue
            room_label = res_room.room.room_number if res_room.room else (
                res_room.room_type.name if res_room.room_type else 'Room'
            )
            FolioCharge.objects.create(
                folio=folio,
                charge_code=charge_code,
                description=f'Room rate for {charge_date} - Room {room_label}',
                unit_price=res_room.rate_per_night,
                quantity=1,
                charge_date=charge_date,
                posted_by=request.user,
            )
        
        response_data = CheckInSerializer(check_in).data
        response_data['folio_id'] = folio.id
        response_data['folio_number'] = folio.folio_number
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class CheckOutView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]

    @transaction.atomic
    def post(self, request):
        serializer = CheckOutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        prop = request.user.assigned_property
        try:
            checkin_qs = CheckIn.objects.all()
            if prop:
                checkin_qs = checkin_qs.filter(reservation__hotel=prop)
            check_in = checkin_qs.get(pk=data['check_in_id'])
        except CheckIn.DoesNotExist:
            return Response({'error': 'Check-in not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create check-out
        check_out = CheckOut.objects.create(
            check_in=check_in,
            checked_out_by=request.user,
            keys_returned=data.get('key_cards_returned', 0),
        )
        
        # Update reservation status
        check_in.reservation.status = 'CHECKED_OUT'
        check_in.reservation.save()
        
        # Update room status to dirty
        check_in.room.status = 'VD'
        check_in.room.fo_status = 'VACANT'
        check_in.room.save()

        # Auto-close the guest folio if balance is zero (international standard)
        folio = Folio.objects.filter(reservation=check_in.reservation, status='OPEN').first()
        if folio:
            folio.recalculate_totals()
            if folio.balance == 0:
                from django.utils import timezone as _tz
                folio.status = Folio.Status.CLOSED
                folio.close_date = _tz.now().date()
                folio.save(update_fields=['status', 'close_date'])

        # Create a housekeeping CLEANING task for the vacated room (international standard)
        HousekeepingTask.objects.create(
            room=check_in.room,
            task_type=HousekeepingTask.TaskType.CLEANING,
            priority=HousekeepingTask.Priority.HIGH,
            status=HousekeepingTask.Status.PENDING,
            notes=f'Post-checkout cleaning — {check_in.guest.first_name} {check_in.guest.last_name} checked out',
        )
        
        return Response(CheckOutSerializer(check_out).data, status=status.HTTP_201_CREATED)


class RoomMoveView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    @transaction.atomic
    def post(self, request):
        serializer = RoomMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        prop = request.user.assigned_property
        try:
            checkin_qs = CheckIn.objects.all()
            room_qs = Room.objects.all()
            if prop:
                checkin_qs = checkin_qs.filter(reservation__hotel=prop)
                room_qs = room_qs.filter(hotel=prop)
            check_in = checkin_qs.get(pk=data['check_in_id'])
            new_room = room_qs.get(pk=data['new_room_id'])
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
    
    @transaction.atomic
    def post(self, request, pk):
        prop = request.user.assigned_property
        try:
            res_qs = Reservation.objects.all()
            if prop:
                res_qs = res_qs.filter(hotel=prop)
            reservation = res_qs.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if reservation.status != 'CONFIRMED':
            return Response({'error': 'Reservation must be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CheckInRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Resolve room from room_id, scoped to the user's property
        room_id = serializer.validated_data.get('room_id')
        try:
            room_qs = Room.objects.all()
            if prop:
                room_qs = room_qs.filter(hotel=prop)
            room = room_qs.get(pk=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if room.status not in ['VC', 'VD']:
            return Response({'error': 'Room is not available for check-in'}, status=status.HTTP_400_BAD_REQUEST)
        
        if CheckIn.objects.filter(reservation=reservation).exists():
            return Response({'error': 'Reservation has already been checked in'}, status=status.HTTP_400_BAD_REQUEST)
        
        import uuid as _uuid
        check_in = CheckIn.objects.create(
            reservation=reservation,
            room=room,
            guest=reservation.guest,
            checked_in_by=request.user,
            expected_check_out=reservation.check_out_date,
            registration_number=f"REG-{_uuid.uuid4().hex[:10].upper()}",
        )
        
        reservation.status = 'CHECKED_IN'
        reservation.save()
        
        room.status = 'OC'
        room.fo_status = 'OCCUPIED'
        room.save()
        
        return Response(CheckInSerializer(check_in).data, status=status.HTTP_201_CREATED)


class CheckOutWithIDView(APIView):
    """Check-out view with reservation ID in URL."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    @transaction.atomic
    def post(self, request, pk):
        prop = request.user.assigned_property
        try:
            res_qs = Reservation.objects.all()
            if prop:
                res_qs = res_qs.filter(hotel=prop)
            reservation = res_qs.get(pk=pk)
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
            keys_returned=serializer.validated_data.get('key_cards_returned', 0),
        )
        
        reservation.status = 'CHECKED_OUT'
        reservation.save()
        
        # Update room status to dirty for housekeeping
        check_in.room.status = 'VD'
        check_in.room.fo_status = 'VACANT'
        check_in.room.save()
        
        return Response(CheckOutSerializer(check_out).data, status=status.HTTP_201_CREATED)


class ArrivalsView(APIView):
    """Get today's expected arrivals."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        date_param = request.query_params.get('date')
        if date_param:
            try:
                target_date = date.fromisoformat(date_param)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = date.today()
        
        property_obj = request.user.assigned_property
        reservations = Reservation.objects.filter(
            check_in_date=target_date,
            status__in=['CONFIRMED', 'PENDING']
        ).select_related(
            'guest', 'hotel', 'created_by', 'check_in__check_out'
        ).prefetch_related('rooms__room__room_type')
        
        if property_obj:
            reservations = reservations.filter(hotel=property_obj)
        
        return Response(ReservationSerializer(reservations, many=True).data)


class DeparturesView(APIView):
    """Get today's expected departures."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        date_param = request.query_params.get('date')
        if date_param:
            try:
                target_date = date.fromisoformat(date_param)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = date.today()
        
        property_obj = request.user.assigned_property
        reservations = Reservation.objects.filter(
            check_out_date=target_date,
            status='CHECKED_IN'
        ).select_related(
            'guest', 'hotel', 'created_by', 'check_in__check_out'
        ).prefetch_related('rooms__room__room_type')
        
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
        ).select_related(
            'guest', 'hotel', 'created_by', 'check_in__check_out'
        ).prefetch_related('rooms__room__room_type')
        
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
        prop = self.request.user.assigned_property
        if prop:
            serializer.save(created_by=self.request.user, property=prop)
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
    
    @transaction.atomic
    def post(self, request, pk):
        prop = request.user.assigned_property
        walkin_qs = WalkIn.objects.filter(property=prop) if prop else WalkIn.objects.all()
        walk_in = get_object_or_404(walkin_qs, pk=pk)
        
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
            
            # Create reservation (model auto-generates a unique confirmation_number via save())
            reservation = Reservation.objects.create(
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
            
            # Create reservation room record
            ReservationRoom.objects.create(
                reservation=reservation,
                room_type=walk_in.room_type,
                rate_per_night=walk_in.rate_per_night,
                total_rate=total_amount,
                adults=walk_in.adults,
                children=walk_in.children,
                guest_name=f"{walk_in.first_name} {walk_in.last_name}",
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
            
        except ValidationError as e:
            logger.error(f"Validation error converting walk-in {pk}: {str(e)}")
            return Response(
                {'error': f'Failed to convert walk-in: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Data error converting walk-in {pk}: {str(e)}")
            return Response(
                {'error': f'Failed to convert walk-in: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
