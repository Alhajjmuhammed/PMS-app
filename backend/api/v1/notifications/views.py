from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from apps.notifications.models import (
    Notification, PushDeviceToken, NotificationTemplate,
    EmailLog, SMSLog
)
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
            
            # Update or create device token
            device, created = PushDeviceToken.objects.update_or_create(
                token=token,
                defaults={
                    'user': request.user,
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
        if self.request.user.assigned_property:
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
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NotificationTemplateCreateSerializer
        return NotificationTemplateSerializer


class EmailLogListCreateView(generics.ListCreateAPIView):
    """List all email logs or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['template', 'status']
    search_fields = ['to_email', 'subject']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return EmailLog.objects.select_related('template')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmailLogCreateSerializer
        return EmailLogSerializer


class EmailLogDetailView(generics.RetrieveAPIView):
    """Retrieve an email log."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = EmailLogSerializer
    queryset = EmailLog.objects.select_related('template')


class SMSLogListCreateView(generics.ListCreateAPIView):
    """List all SMS logs or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['to_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return SMSLog.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SMSLogCreateSerializer
        return SMSLogSerializer


class SMSLogDetailView(generics.RetrieveAPIView):
    """Retrieve an SMS log."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = SMSLogSerializer
    queryset = SMSLog.objects.all()


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
        
        # Determine target users
        target_users = []
        if data.get('user_id'):
            try:
                target_users = [User.objects.get(id=data['user_id'])]
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif data.get('user_ids'):
            target_users = User.objects.filter(id__in=data['user_ids'])
        
        if not target_users:
            return Response(
                {'error': 'No valid users specified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create in-app notifications
        notifications_created = 0
        for user in target_users:
            Notification.objects.create(
                user=user,
                title=title,
                message=message,
                priority=priority
            )
            notifications_created += 1
        
        # TODO: Integrate with actual push notification service (FCM, APNs, etc.)
        # For now, we're just creating in-app notifications
        
        return Response({
            'message': 'Push notifications sent',
            'recipients': notifications_created,
            'note': 'In-app notifications created. Push notification service integration pending.'
        }, status=status.HTTP_200_OK)
