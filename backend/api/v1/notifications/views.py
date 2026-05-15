from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db import transaction
from apps.notifications.models import (
    Notification, PushDeviceToken, NotificationTemplate,
    EmailLog, SMSLog
)
from apps.notifications.services import PushNotificationService
from apps.accounts.models import User
from api.permissions import IsAdminOrManager
from .serializers import (
    NotificationSerializer, PushDeviceTokenSerializer,
    NotificationTemplateSerializer, NotificationTemplateCreateSerializer,
    EmailLogSerializer, EmailLogCreateSerializer,
    SMSLogSerializer, SMSLogCreateSerializer,
    PushNotificationSerializer
)


class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class UnreadNotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            is_read=False
        ).order_by('-created_at')


class NotificationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        # Return empty queryset for swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return Response(NotificationSerializer(notification).data, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


class RegisterDeviceView(APIView):
    """Register device for push notifications."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PushDeviceTokenSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            
            # Update or create device token — scope lookup to (user, token) so that
            # a different user cannot overwrite/claim a token registered by someone else.
            device, created = PushDeviceToken.objects.update_or_create(
                token=token,
                user=request.user,
                defaults={
                    'platform': serializer.validated_data['platform'],
                    'device_name': serializer.validated_data.get('device_name', ''),
                    'is_active': True
                }
            )
            
            return Response(
                PushDeviceTokenSerializer(device).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Unregister device."""
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count = PushDeviceToken.objects.filter(
            user=request.user,
            token=token
        ).delete()[0]
        
        if deleted_count > 0:
            return Response({'message': 'Device unregistered'}, status=status.HTTP_200_OK)
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)


# ============= Enhanced Notification Views =============

class NotificationTemplateListCreateView(generics.ListCreateAPIView):
    """List all notification templates or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property', 'template_type', 'trigger_event', 'is_active']
    search_fields = ['name', 'subject']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = NotificationTemplate.objects.select_related('property')
        if hasattr(self.request.user, 'assigned_property') and self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotificationTemplateCreateSerializer
        return NotificationTemplateSerializer


class NotificationTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a notification template."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get_queryset(self):
        queryset = NotificationTemplate.objects.select_related('property')
        if hasattr(self.request.user, 'assigned_property') and self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NotificationTemplateCreateSerializer
        return NotificationTemplateSerializer


class EmailLogListCreateView(generics.ListCreateAPIView):
    """
    List all email logs or create a new one.
    
    NOTE: Intentionally SYSTEM-WIDE - EmailLog model has no property field.
    Email logs are tracked globally for system auditing. To make property-scoped,
    would need to add a 'property' ForeignKey to the EmailLog model.
    """
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['template', 'status']
    search_fields = ['to_email', 'subject']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Intentionally system-wide - no property field in model
        return EmailLog.objects.select_related('template')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmailLogCreateSerializer
        return EmailLogSerializer


class EmailLogDetailView(generics.RetrieveAPIView):
    """
    Retrieve an email log.
    
    NOTE: Intentionally SYSTEM-WIDE - EmailLog model has no property field.
    """
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = EmailLogSerializer
    queryset = EmailLog.objects.select_related('template')


class SMSLogListCreateView(generics.ListCreateAPIView):
    """
    List all SMS logs or create a new one.
    
    NOTE: Intentionally SYSTEM-WIDE - SMSLog model has no property field.
    SMS logs are tracked globally for system auditing and billing. To make
    property-scoped, would need to add a 'property' ForeignKey to SMSLog model.
    """
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['to_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Intentionally system-wide - no property field in model
        return SMSLog.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SMSLogCreateSerializer
        return SMSLogSerializer


class SMSLogDetailView(generics.RetrieveAPIView):
    """
    Retrieve an SMS log.
    
    NOTE: Intentionally SYSTEM-WIDE - SMSLog model has no property field.
    SMS logs are system-wide. To make this multi-tenant, would need to
    add a property ForeignKey to SMSLog model.
    """
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = SMSLogSerializer
    
    def get_queryset(self):
        # Intentionally system-wide - no property field in model
        return SMSLog.objects.all()


class SendPushNotificationView(APIView):
    """Send push notification to users."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request):
        serializer = PushNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        title = data['title']
        message = data['message']
        priority = data.get('priority', 'NORMAL')
        extra_data = data.get('data', {})
        
        # Determine target users — scoped to caller's property
        prop = request.user.assigned_property
        target_users = []
        if data.get('user_id'):
            try:
                user_qs = User.objects.filter(assigned_property=prop) if prop else User.objects.all()
                target_users = [user_qs.get(id=data['user_id'])]
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif data.get('user_ids'):
            target_users = User.objects.filter(id__in=data['user_ids'])
            if prop:
                target_users = target_users.filter(assigned_property=prop)
        
        if not target_users:
            return Response(
                {'error': 'No valid users specified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create in-app notifications and collect device tokens
        notifications_created = 0
        all_device_tokens = []
        with transaction.atomic():
            for user in target_users:
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    priority=priority
                )
                notifications_created += 1
                # Collect active device tokens for this user
                tokens = list(
                    PushDeviceToken.objects.filter(user=user, is_active=True)
                    .values_list('token', flat=True)
                )
                all_device_tokens.extend(tokens)

        # Send push notification via FCM if tokens available
        push_result = {'success': False, 'error': 'No device tokens registered'}
        if all_device_tokens:
            push_service = PushNotificationService()
            push_result = push_service.send_notification(
                device_tokens=all_device_tokens,
                title=title,
                body=message,
                data=extra_data
            )

        return Response({
            'message': 'Notifications sent',
            'recipients': notifications_created,
            'device_tokens_targeted': len(all_device_tokens),
            'push_delivery': push_result,
        }, status=status.HTTP_200_OK)
