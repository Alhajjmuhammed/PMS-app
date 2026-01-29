from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.notifications.models import Notification, PushDeviceToken
from .serializers import NotificationSerializer, PushDeviceTokenSerializer


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
        from django.utils import timezone
        
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
