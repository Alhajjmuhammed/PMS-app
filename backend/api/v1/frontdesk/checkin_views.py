"""
Views for Front Desk operations
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Q, Count
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from datetime import date
import logging

from apps.frontdesk.models import CheckIn, CheckOut, RoomMove, WalkIn
from apps.rooms.models import Room
from apps.reservations.models import Reservation, ReservationRoom
from apps.guests.models import Guest
from apps.billing.models import Folio
import uuid
from .checkin_serializers import (
    CheckInSerializer,
    CheckOutSerializer,
    RoomMoveSerializer,
    WalkInSerializer,
    CheckInDashboardSerializer
)

logger = logging.getLogger(__name__)

from api.permissions import IsAdminOrManager


class CheckInListCreateView(generics.ListCreateAPIView):
    """List all check-ins or create new check-in."""
    permission_classes = [IsAuthenticated]
    serializer_class = CheckInSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room', 'guest', 'reservation']
    search_fields = ['guest__first_name', 'guest__last_name', 'registration_number', 'room__room_number']
    ordering_fields = ['check_in_time', 'created_at']
    ordering = ['-check_in_time']
    
    def get_queryset(self):
        queryset = CheckIn.objects.select_related(
            'reservation', 'room', 'guest', 'checked_in_by'
        ).filter(
            room__hotel=self.request.user.assigned_property
        )
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(check_in_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(check_in_time__date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        check_in = serializer.save(checked_in_by=self.request.user)
        
        # Update room status to occupied clean
        check_in.room.status = 'OC'
        check_in.room.save()
        
        # Update reservation status if exists
        if check_in.reservation:
            check_in.reservation.status = 'CHECKED_IN'
            check_in.reservation.save()

        # Auto-create a guest folio if one doesn't exist for the reservation
        folio_exists = (
            check_in.reservation
            and hasattr(check_in.reservation, 'folio')
            and check_in.reservation.folio is not None
        )
        if not folio_exists:
            folio_number = f"F-{uuid.uuid4().hex[:8].upper()}"
            Folio.objects.create(
                folio_number=folio_number,
                folio_type=Folio.FolioType.GUEST,
                reservation=check_in.reservation if check_in.reservation else None,
                guest=check_in.guest,
            )


class CheckInDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a check-in."""
    permission_classes = [IsAuthenticated]
    serializer_class = CheckInSerializer
    
    def get_queryset(self):
        return CheckIn.objects.select_related(
            'reservation', 'room', 'guest', 'checked_in_by'
        ).filter(
            room__hotel=self.request.user.assigned_property
        )


class TodayCheckInsView(generics.ListAPIView):
    """List today's check-ins."""
    permission_classes = [IsAuthenticated]
    serializer_class = CheckInSerializer
    
    def get_queryset(self):
        today = timezone.now().date()
        return CheckIn.objects.select_related(
            'reservation', 'room', 'guest', 'checked_in_by'
        ).filter(
            room__hotel=self.request.user.assigned_property,
            check_in_time__date=today
        ).order_by('-check_in_time')


class CheckOutListCreateView(generics.ListCreateAPIView):
    """List all check-outs or create new check-out."""
    permission_classes = [IsAuthenticated]
    serializer_class = CheckOutSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['check_in__room', 'check_in__guest']
    ordering_fields = ['check_out_time', 'created_at']
    ordering = ['-check_out_time']
    
    def get_queryset(self):
        queryset = CheckOut.objects.select_related(
            'check_in__reservation',
            'check_in__room',
            'check_in__guest',
            'checked_out_by'
        ).filter(
            check_in__room__hotel=self.request.user.assigned_property
        )
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(check_out_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(check_out_time__date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        check_out = serializer.save(
            checked_out_by=self.request.user,
            check_out_time=timezone.now()
        )
        
        # Update room status to vacant dirty
        check_out.check_in.room.status = 'VD'
        check_out.check_in.room.save()
        
        # Update reservation status if exists
        if check_out.check_in.reservation:
            check_out.check_in.reservation.status = 'CHECKED_OUT'
            check_out.check_in.reservation.save()

        # Close the folio if it's still open
        try:
            folio = check_out.check_in.reservation.folio
            if folio.status == 'OPEN':
                folio.status = 'CLOSED'
                folio.closed_at = timezone.now()
                folio.closed_by = self.request.user
                folio.close_date = timezone.now().date()
                folio.save()
        except (ObjectDoesNotExist, AttributeError) as e:
            # No folio or no reservation - non-fatal but log for monitoring
            logger.info(f"Could not close folio during checkout: {str(e)}")
            pass


class CheckOutDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a check-out."""
    permission_classes = [IsAuthenticated]
    serializer_class = CheckOutSerializer
    
    def get_queryset(self):
        return CheckOut.objects.select_related(
            'check_in__reservation',
            'check_in__room',
            'check_in__guest',
            'checked_out_by'
        ).filter(
            check_in__room__hotel=self.request.user.assigned_property
        )


class TodayCheckOutsView(generics.ListAPIView):
    """List today's check-outs."""
    permission_classes = [IsAuthenticated]
    serializer_class = CheckOutSerializer
    
    def get_queryset(self):
        today = timezone.now().date()
        return CheckOut.objects.select_related(
            'check_in__reservation',
            'check_in__room',
            'check_in__guest',
            'checked_out_by'
        ).filter(
            check_in__room__hotel=self.request.user.assigned_property,
            check_out_time__date=today
        ).order_by('-check_out_time')


class RoomMoveListCreateView(generics.ListCreateAPIView):
    """List all room moves or create new room move."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomMoveSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['check_in', 'from_room', 'to_room', 'reason']
    ordering_fields = ['move_date', 'created_at']
    ordering = ['-move_date']
    
    def get_queryset(self):
        return RoomMove.objects.select_related(
            'check_in__guest',
            'from_room',
            'to_room',
            'moved_by'
        ).filter(
            from_room__hotel=self.request.user.assigned_property
        )
    
    def perform_create(self, serializer):
        room_move = serializer.save(moved_by=self.request.user)
        
        # Update room statuses
        room_move.from_room.status = 'VD'
        room_move.from_room.save()

        room_move.to_room.status = 'OC'
        room_move.to_room.save()
        
        # Update check-in room
        room_move.check_in.room = room_move.to_room
        room_move.check_in.save()


class RoomMoveDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room move."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomMoveSerializer
    
    def get_queryset(self):
        return RoomMove.objects.select_related(
            'check_in__guest',
            'from_room',
            'to_room',
            'moved_by'
        ).filter(
            from_room__hotel=self.request.user.assigned_property
        )


class WalkInListCreateView(generics.ListCreateAPIView):
    """List all walk-ins or create new walk-in."""
    permission_classes = [IsAuthenticated]
    serializer_class = WalkInSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_converted']
    search_fields = ['first_name', 'last_name', 'phone']
    ordering_fields = ['check_in_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        prop = self.request.user.assigned_property
        qs = WalkIn.objects.select_related('room_type', 'property', 'created_by')
        if prop:
            qs = qs.filter(property=prop)
        return qs

    def perform_create(self, serializer):
        prop = self.request.user.assigned_property
        if prop:
            serializer.save(property=prop, created_by=self.request.user)
        else:
            serializer.save(created_by=self.request.user)


class WalkInDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a walk-in."""
    permission_classes = [IsAuthenticated]
    serializer_class = WalkInSerializer

    def get_queryset(self):
        prop = self.request.user.assigned_property
        qs = WalkIn.objects.select_related('room_type', 'property', 'created_by')
        if prop:
            qs = qs.filter(property=prop)
        return qs


class ConvertWalkInView(APIView):
    """Convert walk-in to reservation."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        try:
            walk_in = WalkIn.objects.get(
                pk=pk,
                room__hotel=request.user.assigned_property
            )
            
            if walk_in.is_converted:
                return Response(
                    {'error': 'Walk-in already converted to reservation'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get or create a Guest record from the walk-in contact info
            guest = None
            if walk_in.email:
                guest = Guest.objects.filter(
                    email=walk_in.email
                ).first()
            if guest is None:
                guest = Guest.objects.filter(
                    phone=walk_in.phone,
                    first_name=walk_in.first_name,
                    last_name=walk_in.last_name,
                ).first()
            if guest is None:
                guest = Guest.objects.create(
                    first_name=walk_in.first_name,
                    last_name=walk_in.last_name,
                    email=walk_in.email,
                    phone=walk_in.phone,
                )

            # Create reservation from walk-in
            reservation = Reservation.objects.create(
                hotel=request.user.assigned_property,
                guest=guest,
                check_in_date=walk_in.check_in_date,
                check_out_date=walk_in.check_out_date,
                adults=walk_in.adults,
                children=walk_in.children,
                status='CONFIRMED',
                source='WALK_IN',
                internal_notes=walk_in.notes,
                created_by=request.user,
            )

            # Link the requested room type to the reservation
            ReservationRoom.objects.create(
                reservation=reservation,
                room_type=walk_in.room_type,
                rate_per_night=walk_in.rate_per_night,
                adults=walk_in.adults,
                children=walk_in.children,
            )

            # Mark walk-in as converted
            walk_in.is_converted = True
            walk_in.reservation = reservation
            walk_in.save()
            
            return Response({
                'message': 'Walk-in converted to reservation successfully',
                'reservation_id': reservation.id,
                'confirmation_number': reservation.confirmation_number
            }, status=status.HTTP_200_OK)
            
        except WalkIn.DoesNotExist:
            return Response(
                {'error': 'Walk-in not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class FrontDeskDashboardView(APIView):
    """Get front desk dashboard statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = date.today()
        property_obj = request.user.assigned_property
        
        # Get statistics
        total_check_ins_today = CheckIn.objects.filter(
            room__hotel=property_obj,
            check_in_time__date=today
        ).count()
        
        total_check_outs_today = CheckOut.objects.filter(
            check_in__room__hotel=property_obj,
            check_out_time__date=today
        ).count()
        
        # Expected arrivals (reservations with check-in today, not yet checked in)
        expected_arrivals = Reservation.objects.filter(
            property=property_obj,
            check_in=today,
            status='CONFIRMED'
        ).exclude(
            check_in__isnull=False
        ).count()
        
        # Expected departures (check-ins with expected checkout today, not yet checked out)
        expected_departures = CheckIn.objects.filter(
            room__hotel=property_obj,
            expected_check_out=today
        ).exclude(
            check_out__isnull=False
        ).count()
        
        # In-house guests (checked in, not checked out)
        in_house_guests = CheckIn.objects.filter(
            room__hotel=property_obj
        ).exclude(
            check_out__isnull=False
        ).count()
        
        # Room statistics
        room_stats = Room.objects.filter(
            hotel=property_obj
        ).aggregate(
            available=Count('id', filter=Q(status='VC')),
            occupied=Count('id', filter=Q(fo_status='OCCUPIED')),
            dirty=Count('id', filter=Q(status__in=['VD', 'OD']))
        )
        
        walk_ins_today = WalkIn.objects.filter(
            room__hotel=property_obj,
            created_at__date=today
        ).count()
        
        room_moves_today = RoomMove.objects.filter(
            from_room__hotel=property_obj,
            move_date=today
        ).count()
        
        data = {
            'total_check_ins_today': total_check_ins_today,
            'total_check_outs_today': total_check_outs_today,
            'expected_arrivals': expected_arrivals,
            'expected_departures': expected_departures,
            'in_house_guests': in_house_guests,
            'available_rooms': room_stats['available'] or 0,
            'occupied_rooms': room_stats['occupied'] or 0,
            'dirty_rooms': room_stats['dirty'] or 0,
            'walk_ins_today': walk_ins_today,
            'room_moves_today': room_moves_today
        }
        
        serializer = CheckInDashboardSerializer(data)
        return Response(serializer.data)
