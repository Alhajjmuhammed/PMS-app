from rest_framework import serializers
from apps.channels.models import Channel, PropertyChannel, RoomTypeMapping


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'name', 'code', 'channel_type', 'commission_percent', 'is_active']


class PropertyChannelSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    
    class Meta:
        model = PropertyChannel
        fields = [
            'id', 'property', 'property_name', 'channel', 'channel_name',
            'property_code', 'is_active', 'sync_rates', 'sync_availability',
            'sync_reservations', 'last_sync_at'
        ]


class RoomTypeMappingSerializer(serializers.ModelSerializer):
    property_channel_info = PropertyChannelSerializer(source='property_channel', read_only=True)
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    
    class Meta:
        model = RoomTypeMapping
        fields = [
            'id', 'property_channel', 'property_channel_info',
            'room_type', 'room_type_name', 'channel_room_code',
            'channel_room_name', 'is_active'
        ]
