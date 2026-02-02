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
from datetime import date

from apps.frontdesk.models import CheckIn, CheckOut, RoomMove, WalkIn
from apps.rooms.models import Room
from apps.reservations.models import Reservation
from .checkin_serializers import (
    CheckInSerializer,
    CheckOutSerializer,
    RoomMoveSerializer,
    WalkInSerializer,
    CheckInDashboardSerializer
)
from api.permissions import IsAdminOrManager


class CheckInListCreateView(generics.ListCreateAPIView):
    """List all check-ins or create new check-in."""
    permission_classes = [IsAuthenticated]
    serializer_class = CheckInSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room', 'guest', 'reservation']
    search_fields = ['guest__first_name', 'guest__last_name', 'registration_number', 'room__number']
    ordering_fields = ['check_in_time', 'created_at']
    ordering = ['-check_in_time']
    
    def get_queryset(self):
        queryset = CheckIn.objects.select_related(
            'reservation', 'room', 'guest', 'checked_in_by'
        ).filter(
            room__property=self.request.user.property
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
        
        # Update room status to occupied
        check_in.room.status = 'OCCUPIED'
        check_in.room.save()
        
        # Update reservation status if exists
        if check_in.reservation:
            check_in.reservation.status = 'CHECKED_IN'
            check_in.reservation.save()


class CheckInDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a check-in."""
    permission_classes = [IsAuthenticated]
    serializer_class = CheckInSerializer
    
    def get_queryset(self):
        return CheckIn.objects.select_related(
            'reservation', 'room', 'guest', 'checked_in_by'
        ).filter(
            room__property=self.request.user.property
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
            room__property=self.request.user.property,
            check_in_time__date=today
        ).order_by('-check_in_time')


class CheckOutListCreateView(generics.ListCreateAPIView):
    """List all check-outs or create new check-out."""
    permission_classes = [IsAuthenticated]
    serializer_class = CheckOutSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_status', 'check_in__room', 'check_in__guest']
    ordering_fields = ['check_out_time', 'created_at']
    ordering = ['-check_out_time']
    
    def get_queryset(self):
        queryset = CheckOut.objects.select_related(
            'check_in__reservation',
            'check_in__room',
            'check_in__guest',
            'checked_out_by'
        ).filter(
            check_in__room__property=self.request.user.property
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
        
        # Update room status to dirty
        check_out.check_in.room.status = 'DIRTY'
        check_out.check_in.room.save()
        
        # Update reservation status if exists
        if check_out.check_in.reservation:
            check_out.check_in.reservation.status = 'CHECKED_OUT'
            check_out.check_in.reservation.save()


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
            check_in__room__property=self.request.user.property
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
            check_in__room__property=self.request.user.property,
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
            from_room__property=self.request.user.property
        )
    
    def perform_create(self, serializer):
        room_move = serializer.save(moved_by=self.request.user)
        
        # Update room statuses
        room_move.from_room.status = 'DIRTY'
        room_move.from_room.save()
        
        room_move.to_room.status = 'OCCUPIED'
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
            from_room__property=self.request.user.property
        )


class WalkInListCreateView(generics.ListCreateAPIView):
    """List all walk-ins or create new walk-in."""
    permission_classes = [IsAuthenticated]
    serializer_class = WalkInSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'room', 'guest']
    search_fields = ['guest__first_name', 'guest__last_name', 'room__number']
    ordering_fields = ['arrival_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return WalkIn.objects.select_related(
            'guest',
            'room',
            'room_type',
            'created_by'
        ).filter(
            room__property=self.request.user.property
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WalkInDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a walk-in."""
    permission_classes = [IsAuthenticated]
    serializer_class = WalkInSerializer
    
    def get_queryset(self):
        return WalkIn.objects.select_related(
            'guest',
            'room',
            'room_type',
            'created_by'
        ).filter(
            room__property=self.request.user.property
        )


class ConvertWalkInView(APIView):
    """Convert walk-in to reservation."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        try:
            walk_in = WalkIn.objects.get(
                pk=pk,
                room__property=request.user.property
            )
            
            if walk_in.status == 'CONVERTED':
                return Response(
                    {'error': 'Walk-in already converted to reservation'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create reservation from walk-in
            reservation = Reservation.objects.create(
                property=request.user.property,
                guest=walk_in.guest,
                check_in=walk_in.arrival_date,
                check_out=walk_in.departure_date,
                adults=walk_in.adults,
                children=walk_in.children,
                status='CONFIRMED',
                source='WALK_IN',
                notes=walk_in.notes,
                created_by=request.user
            )
            
            # Mark walk-in as converted
            walk_in.status = 'CONVERTED'
            walk_in.converted_to_reservation = reservation
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
        property_obj = request.user.property
        
        # Get statistics
        total_check_ins_today = CheckIn.objects.filter(
            room__property=property_obj,
            check_in_time__date=today
        ).count()
        
        total_check_outs_today = CheckOut.objects.filter(
            check_in__room__property=property_obj,
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
            room__property=property_obj,
            expected_check_out=today
        ).exclude(
            check_out__isnull=False
        ).count()
        
        # In-house guests (checked in, not checked out)
        in_house_guests = CheckIn.objects.filter(
            room__property=property_obj
        ).exclude(
            check_out__isnull=False
        ).count()
        
        # Room statistics
        room_stats = Room.objects.filter(
            property=property_obj
        ).aggregate(
            available=Count('id', filter=Q(status='CLEAN')),
            occupied=Count('id', filter=Q(status='OCCUPIED')),
            dirty=Count('id', filter=Q(status='DIRTY'))
        )
        
        walk_ins_today = WalkIn.objects.filter(
            room__property=property_obj,
            created_at__date=today
        ).count()
        
        room_moves_today = RoomMove.objects.filter(
            from_room__property=property_obj,
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
