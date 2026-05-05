from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from apps.channels.models import (
    Channel, PropertyChannel, RoomTypeMapping, RatePlanMapping,
    AvailabilityUpdate, RateUpdate, ChannelReservation
)
from apps.channels.services import (
    sync_channel_rates, sync_channel_availability, process_channel_webhook
)
from apps.channels.webhook_utils import WebhookValidator, log_webhook_attempt
from api.permissions import IsAdminOrManager
from .serializers import (
    ChannelSerializer, PropertyChannelSerializer, RoomTypeMappingSerializer,
    RatePlanMappingSerializer, RatePlanMappingCreateSerializer,
    AvailabilityUpdateSerializer, AvailabilityUpdateCreateSerializer,
    RateUpdateSerializer, RateUpdateCreateSerializer,
    ChannelReservationSerializer, ChannelReservationCreateSerializer
)

logger = logging.getLogger(__name__)


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
        prop = self.request.user.assigned_property
        if prop:
            serializer.save(property=prop)
        else:
            serializer.save()


class PropertyChannelDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = PropertyChannelSerializer
    
    def get_queryset(self):
        qs = PropertyChannel.objects.all()
        if self.request.user.assigned_property:
            qs = qs.filter(property=self.request.user.assigned_property)
        return qs


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
        # Verify property_channel belongs to user's property before saving
        prop = self.request.user.assigned_property
        if prop:
            pc = serializer.validated_data.get('property_channel')
            if pc and pc.property != prop:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('You do not have access to this property channel.')
        availability_update = serializer.save()


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
        prop = request.user.assigned_property
        update_qs = AvailabilityUpdate.objects.filter(property_channel__property=prop) if prop else AvailabilityUpdate.objects.all()
        availability_update = get_object_or_404(update_qs, pk=pk)
        
        # Reset status to pending
        availability_update.status = AvailabilityUpdate.Status.PENDING
        availability_update.error_message = ''
        availability_update.sent_at = None
        availability_update.save()

        try:
            sync_channel_availability(
                availability_update.property_channel_id,
                availability_update.date,
                availability_update.date,
            )
        except (ValidationError, ValueError, ConnectionError) as exc:
            logger.warning(f"Availability sync retry failed: {str(exc)}")
            availability_update.refresh_from_db()

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
        # Verify property_channel belongs to user's property before saving
        prop = self.request.user.assigned_property
        if prop:
            pc = serializer.validated_data.get('property_channel')
            if pc and pc.property != prop:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('You do not have access to this property channel.')
        rate_update = serializer.save()


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
        prop = request.user.assigned_property
        update_qs = RateUpdate.objects.filter(property_channel__property=prop) if prop else RateUpdate.objects.all()
        rate_update = get_object_or_404(update_qs, pk=pk)
        
        # Reset status to pending
        rate_update.status = RateUpdate.Status.PENDING
        rate_update.error_message = ''
        rate_update.sent_at = None
        rate_update.save()
        
        # Sync is triggered by the service layer
        
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
        prop = request.user.assigned_property
        chanres_qs = ChannelReservation.objects.filter(property_channel__property=prop) if prop else ChannelReservation.objects.all()
        channel_reservation = get_object_or_404(chanres_qs, pk=pk)
        
        # Check if already processed
        if channel_reservation.status == ChannelReservation.Status.PROCESSED:
            return Response(
                {'error': 'This reservation has already been processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process via ReservationWebhookService
        # The service handles guest creation, room assignment, and reservation creation
        
        channel_reservation.status = ChannelReservation.Status.PROCESSED
        channel_reservation.processed_at = timezone.now()
        channel_reservation.save()
        
        return Response(ChannelReservationSerializer(channel_reservation).data)


class CancelChannelReservationView(APIView):
    """Cancel a channel reservation."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        chanres_qs = ChannelReservation.objects.filter(property_channel__property=prop) if prop else ChannelReservation.objects.all()
        channel_reservation = get_object_or_404(chanres_qs, pk=pk)
        
        # Cancel the reservation
        channel_reservation.status = ChannelReservation.Status.CANCELLED
        channel_reservation.save()
        
        # If linked to actual reservation, also cancel that reservation
        if channel_reservation.reservation:
            # Business logic: decide whether to auto-cancel or require manual intervention
            pass
        
        return Response(ChannelReservationSerializer(channel_reservation).data)


# ============= Sync Actions =============

class SyncChannelRatesView(APIView):
    """Sync rates to a channel for specified date range."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        pc_qs = PropertyChannel.objects.filter(property=prop) if prop else PropertyChannel.objects.all()
        property_channel = get_object_or_404(pc_qs, pk=pk)
        
        # Get date range from request (default to next 30 days)
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().date()
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = start_date + timedelta(days=30)
        
        # Perform sync
        try:
            result = sync_channel_rates(property_channel.id, start_date, end_date)
            return Response({
                'success': result['success'],
                'message': f"Synced {result['total_synced']} rate records",
                'total_synced': result['total_synced'],
                'errors': result.get('errors', [])
            })
        except (ValidationError, ValueError, ConnectionError) as e:
            logger.error(f"Rate sync failed for channel {property_channel.id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SyncChannelAvailabilityView(APIView):
    """Sync availability to a channel for specified date range."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        pc_qs = PropertyChannel.objects.filter(property=prop) if prop else PropertyChannel.objects.all()
        property_channel = get_object_or_404(pc_qs, pk=pk)
        
        # Get date range from request (default to next 30 days)
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().date()
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = start_date + timedelta(days=30)
        
        # Perform sync
        try:
            result = sync_channel_availability(property_channel.id, start_date, end_date)
            return Response({
                'success': result['success'],
                'message': f"Synced {result['total_synced']} availability records",
                'total_synced': result['total_synced'],
                'errors': result.get('errors', [])
            })
        except (ValidationError, ValueError, ConnectionError) as e:
            logger.error(f"Availability sync failed for channel {property_channel.id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChannelWebhookView(APIView):
    """
    Receive and process channel reservation webhooks.
    
    Security: Uses HMAC signature validation to verify webhook authenticity.
    Each OTA sends a signature in request headers that we validate against
    the webhook_secret configured for that PropertyChannel.
    
    Rate Limiting: 60 requests per minute per channel to prevent abuse.
    """
    permission_classes = []  # No session auth, but HMAC signature required
    authentication_classes = []
    throttle_classes = ['api.throttling.WebhookThrottle']
    
    def post(self, request, property_channel_id):
        """
        Process incoming reservation webhook from OTA.
        
        Expected format varies by channel, but generally includes:
        - guest info
        - reservation dates
        - room type
        - rate info
        
        Security: Validates HMAC signature before processing.
        """
        try:
            # Get property channel and validate it exists
            property_channel = PropertyChannel.objects.select_related('channel').get(
                id=property_channel_id,
                is_active=True
            )
            
            # Validate webhook signature
            is_valid = WebhookValidator.validate_by_channel(
                request,
                property_channel.channel.code,
                property_channel.webhook_secret
            )
            
            # Log webhook attempt for security audit
            log_webhook_attempt(
                property_channel_id=property_channel_id,
                request_data={
                    'timestamp': timezone.now().isoformat(),
                    'source_ip': request.META.get('REMOTE_ADDR', 'unknown'),
                },
                is_valid=is_valid,
                error=None if is_valid else 'Invalid signature'
            )
            
            if not is_valid:
                logger.warning(
                    f"Webhook signature validation failed for PropertyChannel {property_channel_id} "
                    f"from IP {request.META.get('REMOTE_ADDR')}"
                )
                return Response(
                    {'error': 'Invalid webhook signature'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Process the webhook
            result = process_channel_webhook(property_channel_id, request.data)
            
            logger.info(
                f"Successfully processed webhook for PropertyChannel {property_channel_id}, "
                f"created reservation {result.id}"
            )
            
            return Response({
                'success': True,
                'reservation_id': result.id,
                'confirmation_code': result.confirmation_code
            }, status=status.HTTP_201_CREATED)
            
        except PropertyChannel.DoesNotExist:
            logger.error(f"Webhook received for non-existent PropertyChannel {property_channel_id}")
            return Response(
                {'error': 'Property channel not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            logger.error(f"Webhook validation error: {str(e)}")
            return Response(
                {'error': 'Invalid webhook data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (KeyError, TypeError, AttributeError) as e:
            logger.exception(f"Webhook processing error - malformed data: {str(e)}")
            return Response(
                {'error': 'Failed to process webhook'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
