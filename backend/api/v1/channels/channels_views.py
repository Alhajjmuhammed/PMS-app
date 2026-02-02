"""
Views for Channels Module
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Q, Count
from datetime import date, timedelta

from apps.channels.models import (
    PropertyChannel, RoomTypeMapping, RatePlanMapping,
    AvailabilityUpdate, RateUpdate, ChannelReservation, Channel
)
from .channels_serializers import (
    PropertyChannelSerializer,
    RoomTypeMappingSerializer,
    RatePlanMappingSerializer,
    AvailabilityUpdateSerializer,
    RateUpdateSerializer,
    ChannelReservationSerializer,
    ChannelDashboardSerializer,
    BulkAvailabilityUpdateSerializer,
    BulkRateUpdateSerializer,
    ChannelSerializer
)
from api.permissions import IsAdminOrManager


# ===== Property Channels =====

class PropertyChannelListCreateView(generics.ListCreateAPIView):
    """List all property channels or create new connection."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = PropertyChannelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['channel', 'is_active']
    search_fields = ['property_code', 'channel__name']
    ordering_fields = ['last_sync', 'is_active']
    ordering = ['channel__name']
    
    def get_queryset(self):
        return PropertyChannel.objects.filter(
            property=self.request.user.property
        ).select_related('channel', 'rate_plan').prefetch_related('room_mappings', 'rate_mappings')
    
    def perform_create(self, serializer):
        serializer.save(property=self.request.user.property)


class PropertyChannelDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a property channel."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = PropertyChannelSerializer
    
    def get_queryset(self):
        return PropertyChannel.objects.filter(
            property=self.request.user.property
        ).select_related('channel', 'rate_plan')


class ActivePropertyChannelsView(generics.ListAPIView):
    """List active property channels."""
    permission_classes = [IsAuthenticated]
    serializer_class = PropertyChannelSerializer
    
    def get_queryset(self):
        return PropertyChannel.objects.filter(
            property=self.request.user.property,
            is_active=True
        ).select_related('channel')


class SyncPropertyChannelView(APIView):
    """Trigger sync for a property channel."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        try:
            property_channel = PropertyChannel.objects.get(
                pk=pk,
                property=request.user.property
            )
            
            if not property_channel.is_active:
                return Response(
                    {'error': 'Channel is not active'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update last sync time
            property_channel.last_sync = timezone.now()
            property_channel.save()
            
            # In real implementation, this would trigger actual sync logic
            serializer = PropertyChannelSerializer(property_channel)
            return Response({
                'message': 'Sync initiated successfully',
                'channel': serializer.data
            })
            
        except PropertyChannel.DoesNotExist:
            return Response(
                {'error': 'Property channel not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ===== Room Type Mappings =====

class RoomTypeMappingListCreateView(generics.ListCreateAPIView):
    """List all room type mappings or create new mapping."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomTypeMappingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property_channel', 'room_type', 'is_active']
    ordering = ['room_type__name']
    
    def get_queryset(self):
        return RoomTypeMapping.objects.filter(
            property_channel__property=self.request.user.property
        ).select_related('property_channel', 'property_channel__channel', 'room_type')


class RoomTypeMappingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room type mapping."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomTypeMappingSerializer
    
    def get_queryset(self):
        return RoomTypeMapping.objects.filter(
            property_channel__property=self.request.user.property
        ).select_related('property_channel', 'room_type')


class RoomTypeMappingsByChannelView(generics.ListAPIView):
    """Get room type mappings for a specific channel."""
    permission_classes = [IsAuthenticated]
    serializer_class = RoomTypeMappingSerializer
    
    def get_queryset(self):
        channel_id = self.kwargs.get('channel_id')
        return RoomTypeMapping.objects.filter(
            property_channel_id=channel_id,
            property_channel__property=self.request.user.property
        ).select_related('room_type')


# ===== Rate Plan Mappings =====

class RatePlanMappingListCreateView(generics.ListCreateAPIView):
    """List all rate plan mappings or create new mapping."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RatePlanMappingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property_channel', 'rate_plan', 'is_active']
    ordering = ['rate_plan__name']
    
    def get_queryset(self):
        return RatePlanMapping.objects.filter(
            property_channel__property=self.request.user.property
        ).select_related('property_channel', 'property_channel__channel', 'rate_plan')


class RatePlanMappingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a rate plan mapping."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RatePlanMappingSerializer
    
    def get_queryset(self):
        return RatePlanMapping.objects.filter(
            property_channel__property=self.request.user.property
        ).select_related('property_channel', 'rate_plan')


class RatePlanMappingsByChannelView(generics.ListAPIView):
    """Get rate plan mappings for a specific channel."""
    permission_classes = [IsAuthenticated]
    serializer_class = RatePlanMappingSerializer
    
    def get_queryset(self):
        channel_id = self.kwargs.get('channel_id')
        return RatePlanMapping.objects.filter(
            property_channel_id=channel_id,
            property_channel__property=self.request.user.property
        ).select_related('rate_plan')


# ===== Availability Updates =====

class AvailabilityUpdateListCreateView(generics.ListCreateAPIView):
    """List all availability updates or create new update."""
    permission_classes = [IsAuthenticated]
    serializer_class = AvailabilityUpdateSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property_channel', 'room_type', 'status']
    ordering_fields = ['date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = AvailabilityUpdate.objects.filter(
            property_channel__property=self.request.user.property
        ).select_related('property_channel', 'property_channel__channel', 'room_type')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset


class AvailabilityUpdateDetailView(generics.RetrieveAPIView):
    """Retrieve an availability update."""
    permission_classes = [IsAuthenticated]
    serializer_class = AvailabilityUpdateSerializer
    
    def get_queryset(self):
        return AvailabilityUpdate.objects.filter(
            property_channel__property=self.request.user.property
        ).select_related('property_channel', 'room_type')


class BulkAvailabilityUpdateView(APIView):
    """Create bulk availability updates."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request):
        serializer = BulkAvailabilityUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Verify property channel belongs to user's property
        try:
            property_channel = PropertyChannel.objects.get(
                id=data['property_channel'],
                property=request.user.property
            )
        except PropertyChannel.DoesNotExist:
            return Response(
                {'error': 'Property channel not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create updates for date range
        updates = []
        current_date = data['start_date']
        while current_date <= data['end_date']:
            update = AvailabilityUpdate.objects.create(
                property_channel=property_channel,
                room_type_id=data['room_type'],
                date=current_date,
                availability=data['availability']
            )
            updates.append(update)
            current_date += timedelta(days=1)
        
        return Response({
            'message': f'Created {len(updates)} availability updates',
            'count': len(updates)
        }, status=status.HTTP_201_CREATED)


# ===== Rate Updates =====

class RateUpdateListCreateView(generics.ListCreateAPIView):
    """List all rate updates or create new update."""
    permission_classes = [IsAuthenticated]
    serializer_class = RateUpdateSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property_channel', 'room_type', 'rate_plan', 'status']
    ordering_fields = ['date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = RateUpdate.objects.filter(
            property_channel__property=self.request.user.property
        ).select_related('property_channel', 'property_channel__channel', 'room_type', 'rate_plan')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset


class RateUpdateDetailView(generics.RetrieveAPIView):
    """Retrieve a rate update."""
    permission_classes = [IsAuthenticated]
    serializer_class = RateUpdateSerializer
    
    def get_queryset(self):
        return RateUpdate.objects.filter(
            property_channel__property=self.request.user.property
        ).select_related('property_channel', 'room_type', 'rate_plan')


class BulkRateUpdateView(APIView):
    """Create bulk rate updates."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request):
        serializer = BulkRateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Verify property channel belongs to user's property
        try:
            property_channel = PropertyChannel.objects.get(
                id=data['property_channel'],
                property=request.user.property
            )
        except PropertyChannel.DoesNotExist:
            return Response(
                {'error': 'Property channel not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create updates for date range
        updates = []
        current_date = data['start_date']
        while current_date <= data['end_date']:
            update = RateUpdate.objects.create(
                property_channel=property_channel,
                room_type_id=data['room_type'],
                rate_plan_id=data['rate_plan'],
                date=current_date,
                rate=data['rate']
            )
            updates.append(update)
            current_date += timedelta(days=1)
        
        return Response({
            'message': f'Created {len(updates)} rate updates',
            'count': len(updates)
        }, status=status.HTTP_201_CREATED)


# ===== Channel Reservations =====

class ChannelReservationListView(generics.ListAPIView):
    """List all channel reservations."""
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelReservationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_channel', 'status']
    search_fields = ['channel_booking_id', 'guest_name']
    ordering_fields = ['received_at', 'check_in_date']
    ordering = ['-received_at']
    
    def get_queryset(self):
        queryset = ChannelReservation.objects.filter(
            property_channel__property=self.request.user.property
        ).select_related('property_channel', 'property_channel__channel', 'reservation')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(check_in_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(check_in_date__lte=end_date)
        
        return queryset


class ChannelReservationDetailView(generics.RetrieveAPIView):
    """Retrieve a channel reservation."""
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelReservationSerializer
    
    def get_queryset(self):
        return ChannelReservation.objects.filter(
            property_channel__property=self.request.user.property
        ).select_related('property_channel', 'reservation')


class UnprocessedChannelReservationsView(generics.ListAPIView):
    """List unprocessed channel reservations."""
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelReservationSerializer
    
    def get_queryset(self):
        return ChannelReservation.objects.filter(
            property_channel__property=self.request.user.property,
            status='RECEIVED'
        ).select_related('property_channel', 'property_channel__channel').order_by('received_at')


# ===== Dashboard & Stats =====

class ChannelDashboardView(APIView):
    """Get channel dashboard statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db import models
        today = date.today()
        property_obj = request.user.property
        
        # Channel statistics
        active_channels = PropertyChannel.objects.filter(
            property=property_obj,
            is_active=True
        ).count()
        
        # Mapping statistics
        total_mappings = (
            RoomTypeMapping.objects.filter(
                property_channel__property=property_obj
            ).count() +
            RatePlanMapping.objects.filter(
                property_channel__property=property_obj
            ).count()
        )
        
        # Update statistics
        pending_updates = (
            AvailabilityUpdate.objects.filter(
                property_channel__property=property_obj,
                status='PENDING'
            ).count() +
            RateUpdate.objects.filter(
                property_channel__property=property_obj,
                status='PENDING'
            ).count()
        )
        
        failed_updates = (
            AvailabilityUpdate.objects.filter(
                property_channel__property=property_obj,
                status='FAILED'
            ).count() +
            RateUpdate.objects.filter(
                property_channel__property=property_obj,
                status='FAILED'
            ).count()
        )
        
        # Reservation statistics
        unprocessed_reservations = ChannelReservation.objects.filter(
            property_channel__property=property_obj,
            status='RECEIVED'
        ).count()
        
        reservations_today = ChannelReservation.objects.filter(
            property_channel__property=property_obj,
            received_at__date=today
        ).count()
        
        # Last sync time
        last_sync = PropertyChannel.objects.filter(
            property=property_obj,
            last_sync__isnull=False
        ).aggregate(latest=models.Max('last_sync'))['latest']
        
        data = {
            'active_channels': active_channels,
            'total_mappings': total_mappings,
            'pending_updates': pending_updates,
            'failed_updates': failed_updates,
            'unprocessed_reservations': unprocessed_reservations,
            'reservations_today': reservations_today,
            'last_sync_time': last_sync
        }
        
        serializer = ChannelDashboardSerializer(data)
        return Response(serializer.data)


# ===== Channels (Global) =====

class ChannelListView(generics.ListAPIView):
    """List all available channels."""
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering = ['name']
    
    def get_queryset(self):
        return Channel.objects.filter(is_active=True)
