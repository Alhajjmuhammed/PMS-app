from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from datetime import date

from apps.rooms.models import RoomBlock
from .room_block_serializers import RoomBlockSerializer, RoomBlockCreateSerializer
from api.permissions import IsAdminOrManager


class RoomBlockListCreateView(generics.ListCreateAPIView):
    """List all room blocks or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room', 'reason']
    search_fields = ['room__number', 'notes']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        queryset = RoomBlock.objects.select_related(
            'room',
            'room__room_type',
            'room__property',
            'created_by'
        ).filter(room__property=self.request.user.assigned_property)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(end_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_date__lte=end_date)
        
        # Filter active/inactive
        is_active = self.request.query_params.get('is_active')
        if is_active == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(start_date__lte=today, end_date__gte=today)
        elif is_active == 'false':
            today = timezone.now().date()
            queryset = queryset.exclude(start_date__lte=today, end_date__gte=today)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoomBlockCreateSerializer
        return RoomBlockSerializer


class RoomBlockDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room block."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get_queryset(self):
        return RoomBlock.objects.select_related(
            'room',
            'room__room_type',
            'room__property',
            'created_by'
        ).filter(room__property=self.request.user.assigned_property)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RoomBlockCreateSerializer
        return RoomBlockSerializer


class RoomBlocksByDateView(generics.ListAPIView):
    """Get all blocked rooms for a specific date."""
    permission_classes = [IsAuthenticated]
    serializer_class = RoomBlockSerializer
    
    def get_queryset(self):
        date_param = self.request.query_params.get('date')
        
        if date_param:
            try:
                check_date = date.fromisoformat(date_param)
            except ValueError:
                check_date = timezone.now().date()
        else:
            check_date = timezone.now().date()
        
        return RoomBlock.objects.select_related(
            'room',
            'room__room_type',
            'room__property',
            'created_by'
        ).filter(
            room__property=self.request.user.assigned_property,
            start_date__lte=check_date,
            end_date__gte=check_date
        )


class ActiveRoomBlocksView(generics.ListAPIView):
    """Get all currently active room blocks."""
    permission_classes = [IsAuthenticated]
    serializer_class = RoomBlockSerializer
    
    def get_queryset(self):
        today = timezone.now().date()
        return RoomBlock.objects.select_related(
            'room',
            'room__room_type',
            'room__property',
            'created_by'
        ).filter(
            room__property=self.request.user.assigned_property,
            start_date__lte=today,
            end_date__gte=today
        )


class RoomBlockStatsView(APIView):
    """Get room block statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        
        queryset = RoomBlock.objects.filter(
            room__property=request.user.assigned_property
        )
        
        total = queryset.count()
        active = queryset.filter(start_date__lte=today, end_date__gte=today).count()
        upcoming = queryset.filter(start_date__gt=today).count()
        past = queryset.filter(end_date__lt=today).count()
        
        by_reason = {}
        for reason, label in RoomBlock.BlockReason.choices:
            count = queryset.filter(reason=reason).count()
            by_reason[reason] = {
                'label': label,
                'count': count
            }
        
        return Response({
            'total': total,
            'active': active,
            'upcoming': upcoming,
            'past': past,
            'by_reason': by_reason
        })
