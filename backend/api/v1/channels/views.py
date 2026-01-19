from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.channels.models import Channel, PropertyChannel, RoomTypeMapping
from .serializers import ChannelSerializer, PropertyChannelSerializer, RoomTypeMappingSerializer


class ChannelListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelSerializer
    queryset = Channel.objects.filter(is_active=True)


class ChannelDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()


class PropertyChannelListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PropertyChannelSerializer
    
    def get_queryset(self):
        queryset = PropertyChannel.objects.filter(is_active=True)
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset


class RoomTypeMappingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomTypeMappingSerializer
    
    def get_queryset(self):
        queryset = RoomTypeMapping.objects.all()
        if self.request.user.assigned_property:
            queryset = queryset.filter(property_channel__property=self.request.user.assigned_property)
        return queryset
