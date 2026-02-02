from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone

from apps.frontdesk.models import GuestMessage
from .guest_message_serializers import (
    GuestMessageSerializer,
    GuestMessageCreateSerializer,
    GuestMessageReplySerializer
)


class GuestMessageListCreateView(generics.ListCreateAPIView):
    """List all guest messages or create a new one."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['message_type', 'is_delivered', 'check_in']
    search_fields = ['message', 'from_name', 'check_in__guest__first_name', 'check_in__guest__last_name']
    ordering_fields = ['created_at', 'delivered_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return GuestMessage.objects.select_related(
            'check_in',
            'check_in__guest',
            'check_in__room',
            'taken_by'
        ).filter(
            check_in__room__property=self.request.user.assigned_property
        )
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GuestMessageCreateSerializer
        return GuestMessageSerializer


class GuestMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a guest message."""
    permission_classes = [IsAuthenticated]
    serializer_class = GuestMessageSerializer
    
    def get_queryset(self):
        return GuestMessage.objects.select_related(
            'check_in',
            'check_in__guest',
            'check_in__room',
            'taken_by'
        ).filter(
            check_in__room__property=self.request.user.assigned_property
        )


class MarkMessageDeliveredView(APIView):
    """Mark a message as delivered."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            message = GuestMessage.objects.select_related(
                'check_in__room'
            ).get(
                pk=pk,
                check_in__room__property=request.user.assigned_property
            )
        except GuestMessage.DoesNotExist:
            return Response(
                {'error': 'Message not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if message.is_delivered:
            return Response(
                {'error': 'Message already marked as delivered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message.is_delivered = True
        message.delivered_at = timezone.now()
        message.save()
        
        serializer = GuestMessageSerializer(message)
        return Response(serializer.data)


class UndeliveredMessagesView(generics.ListAPIView):
    """Get all undelivered messages."""
    permission_classes = [IsAuthenticated]
    serializer_class = GuestMessageSerializer
    
    def get_queryset(self):
        return GuestMessage.objects.select_related(
            'check_in',
            'check_in__guest',
            'check_in__room',
            'taken_by'
        ).filter(
            check_in__room__property=self.request.user.assigned_property,
            is_delivered=False
        ).order_by('-created_at')


class MessagesByCheckInView(generics.ListAPIView):
    """Get all messages for a specific check-in."""
    permission_classes = [IsAuthenticated]
    serializer_class = GuestMessageSerializer
    
    def get_queryset(self):
        check_in_id = self.kwargs.get('check_in_id')
        return GuestMessage.objects.select_related(
            'check_in',
            'check_in__guest',
            'check_in__room',
            'taken_by'
        ).filter(
            check_in_id=check_in_id,
            check_in__room__property=self.request.user.assigned_property
        ).order_by('-created_at')


class MessagesByRoomView(generics.ListAPIView):
    """Get all messages for a specific room."""
    permission_classes = [IsAuthenticated]
    serializer_class = GuestMessageSerializer
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return GuestMessage.objects.select_related(
            'check_in',
            'check_in__guest',
            'check_in__room',
            'taken_by'
        ).filter(
            check_in__room_id=room_id,
            check_in__room__property=self.request.user.assigned_property
        ).order_by('-created_at')


class GuestMessageStatsView(APIView):
    """Get guest message statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = GuestMessage.objects.filter(
            check_in__room__property=request.user.assigned_property
        )
        
        total = queryset.count()
        delivered = queryset.filter(is_delivered=True).count()
        undelivered = queryset.filter(is_delivered=False).count()
        
        by_type = {}
        for msg_type, label in GuestMessage.MessageType.choices:
            count = queryset.filter(message_type=msg_type).count()
            by_type[msg_type] = {
                'label': label,
                'count': count
            }
        
        return Response({
            'total': total,
            'delivered': delivered,
            'undelivered': undelivered,
            'by_type': by_type
        })
