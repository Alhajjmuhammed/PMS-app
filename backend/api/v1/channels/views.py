from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.channels.models import Channel, PropertyChannel, RoomTypeMapping
from api.permissions import IsAdminOrManager
from .serializers import ChannelSerializer, PropertyChannelSerializer, RoomTypeMappingSerializer


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
