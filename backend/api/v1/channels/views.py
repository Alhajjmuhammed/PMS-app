from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.channels.models import (
    Channel, PropertyChannel, RoomTypeMapping, RatePlanMapping,
    AvailabilityUpdate, RateUpdate, ChannelReservation
)
from api.permissions import IsAdminOrManager
from .serializers import (
    ChannelSerializer, PropertyChannelSerializer, RoomTypeMappingSerializer,
    RatePlanMappingSerializer, RatePlanMappingCreateSerializer,
    AvailabilityUpdateSerializer, AvailabilityUpdateCreateSerializer,
    RateUpdateSerializer, RateUpdateCreateSerializer,
    ChannelReservationSerializer, ChannelReservationCreateSerializer
)


class ChannelListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = ChannelSerializer
    queryset = Channel.objects.filter(is_active=True)


class ChannelDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()


class PropertyChannelListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = PropertyChannelSerializer
    
    def get_queryset(self):
        queryset = PropertyChannel.objects.filter(is_active=True)
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def perform_create(self, serializer):
        if self.request.user.assigned_property and 'property' not in serializer.validated_data:
            serializer.save(property=self.request.user.assigned_property)
        else:
            serializer.save()


class PropertyChannelDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = PropertyChannelSerializer
    queryset = PropertyChannel.objects.all()


class RoomTypeMappingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomTypeMappingSerializer
    
    def get_queryset(self):
        queryset = RoomTypeMapping.objects.all()
        if self.request.user.assigned_property:
            queryset = queryset.filter(property_channel__property=self.request.user.assigned_property)
        return queryset


# ============= Rate Plan Mapping Views =============

class RatePlanMappingListCreateView(generics.ListCreateAPIView):
    """List all rate plan mappings or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property_channel', 'rate_plan', 'is_active']
    search_fields = ['channel_rate_code', 'channel_rate_name']
    ordering_fields = ['id', 'channel_rate_code']
    ordering = ['-id']
    
    def get_queryset(self):
        queryset = RatePlanMapping.objects.select_related(
            'property_channel', 'property_channel__channel',
            'property_channel__property', 'rate_plan'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property_channel__property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RatePlanMappingCreateSerializer
        return RatePlanMappingSerializer


class RatePlanMappingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a rate plan mapping."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get_queryset(self):
        queryset = RatePlanMapping.objects.select_related(
            'property_channel', 'rate_plan'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property_channel__property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RatePlanMappingCreateSerializer
        return RatePlanMappingSerializer


# ============= Availability Update Views =============

class AvailabilityUpdateListCreateView(generics.ListCreateAPIView):
    """List all availability updates or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property_channel', 'room_type', 'status', 'date']
    search_fields = ['room_type__name']
    ordering_fields = ['id', 'date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = AvailabilityUpdate.objects.select_related(
            'property_channel', 'property_channel__channel',
            'property_channel__property', 'room_type'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property_channel__property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AvailabilityUpdateCreateSerializer
        return AvailabilityUpdateSerializer
    
    def perform_create(self, serializer):
        # Save the update
        availability_update = serializer.save()
        
        # TODO: Here you would typically trigger the actual sync to the channel
        # For now, we just mark it as pending
        # In production, this would call the channel's API


class AvailabilityUpdateDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update an availability update."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get_queryset(self):
        queryset = AvailabilityUpdate.objects.select_related(
            'property_channel', 'room_type'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property_channel__property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AvailabilityUpdateCreateSerializer
        return AvailabilityUpdateSerializer


class ResendAvailabilityUpdateView(APIView):
    """Resend a failed availability update."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        availability_update = get_object_or_404(AvailabilityUpdate, pk=pk)
        
        # Check if user has access
        if request.user.assigned_property:
            if availability_update.property_channel.property != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Reset status to pending
        availability_update.status = AvailabilityUpdate.Status.PENDING
        availability_update.error_message = ''
        availability_update.sent_at = None
        availability_update.save()
        
        # TODO: Trigger the actual sync
        
        return Response(AvailabilityUpdateSerializer(availability_update).data)


# ============= Rate Update Views =============

class RateUpdateListCreateView(generics.ListCreateAPIView):
    """List all rate updates or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property_channel', 'room_type', 'rate_plan', 'status', 'date']
    search_fields = ['room_type__name', 'rate_plan__name']
    ordering_fields = ['id', 'date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = RateUpdate.objects.select_related(
            'property_channel', 'property_channel__channel',
            'property_channel__property', 'room_type', 'rate_plan'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property_channel__property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RateUpdateCreateSerializer
        return RateUpdateSerializer
    
    def perform_create(self, serializer):
        # Save the update
        rate_update = serializer.save()
        
        # TODO: Trigger the actual sync to the channel


class RateUpdateDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a rate update."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get_queryset(self):
        queryset = RateUpdate.objects.select_related(
            'property_channel', 'room_type', 'rate_plan'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property_channel__property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RateUpdateCreateSerializer
        return RateUpdateSerializer


class ResendRateUpdateView(APIView):
    """Resend a failed rate update."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        rate_update = get_object_or_404(RateUpdate, pk=pk)
        
        # Check if user has access
        if request.user.assigned_property:
            if rate_update.property_channel.property != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Reset status to pending
        rate_update.status = RateUpdate.Status.PENDING
        rate_update.error_message = ''
        rate_update.sent_at = None
        rate_update.save()
        
        # TODO: Trigger the actual sync
        
        return Response(RateUpdateSerializer(rate_update).data)


# ============= Channel Reservation Views =============

class ChannelReservationListCreateView(generics.ListCreateAPIView):
    """List all channel reservations or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property_channel', 'status', 'check_in_date', 'check_out_date']
    search_fields = ['channel_booking_id', 'guest_name']
    ordering_fields = ['id', 'check_in_date', 'received_at']
    ordering = ['-received_at']
    
    def get_queryset(self):
        queryset = ChannelReservation.objects.select_related(
            'property_channel', 'property_channel__channel',
            'property_channel__property', 'reservation'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property_channel__property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChannelReservationCreateSerializer
        return ChannelReservationSerializer


class ChannelReservationDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a channel reservation."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get_queryset(self):
        queryset = ChannelReservation.objects.select_related(
            'property_channel', 'reservation'
        )
        if self.request.user.assigned_property:
            queryset = queryset.filter(property_channel__property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ChannelReservationCreateSerializer
        return ChannelReservationSerializer


class ProcessChannelReservationView(APIView):
    """Process a channel reservation (create actual reservation)."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        channel_reservation = get_object_or_404(ChannelReservation, pk=pk)
        
        # Check if user has access
        if request.user.assigned_property:
            if channel_reservation.property_channel.property != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if already processed
        if channel_reservation.status == ChannelReservation.Status.PROCESSED:
            return Response(
                {'error': 'This reservation has already been processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement actual reservation creation logic
        # This would involve:
        # 1. Finding the correct room type based on mapping
        # 2. Creating a guest record
        # 3. Creating the reservation
        # 4. Linking the channel reservation to the real reservation
        
        # For now, just mark as processed
        channel_reservation.status = ChannelReservation.Status.PROCESSED
        channel_reservation.processed_at = timezone.now()
        channel_reservation.save()
        
        return Response(ChannelReservationSerializer(channel_reservation).data)


class CancelChannelReservationView(APIView):
    """Cancel a channel reservation."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        channel_reservation = get_object_or_404(ChannelReservation, pk=pk)
        
        # Check if user has access
        if request.user.assigned_property:
            if channel_reservation.property_channel.property != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Cancel the reservation
        channel_reservation.status = ChannelReservation.Status.CANCELLED
        channel_reservation.save()
        
        # TODO: If linked to actual reservation, cancel that too
        
        return Response(ChannelReservationSerializer(channel_reservation).data)
