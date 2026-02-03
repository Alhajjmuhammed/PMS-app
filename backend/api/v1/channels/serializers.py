from rest_framework import serializers
from apps.channels.models import (
    Channel, PropertyChannel, RoomTypeMapping, RatePlanMapping,
    AvailabilityUpdate, RateUpdate, ChannelReservation
)


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        ref_name = 'ChannelBasic'
        fields = ['id', 'name', 'code', 'channel_type', 'commission_percent', 'is_active']


class PropertyChannelSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    
    class Meta:
        model = PropertyChannel
        fields = [
            'id', 'property', 'property_name', 'channel', 'channel_name',
            'property_code', 'rate_plan', 'rate_markup', 'min_availability',
            'max_availability', 'sync_rates', 'sync_availability', 'sync_restrictions',
            'last_sync', 'is_active'
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


class RatePlanMappingSerializer(serializers.ModelSerializer):
    """Serializer for rate plan mappings to channels."""
    property_channel_info = PropertyChannelSerializer(source='property_channel', read_only=True)
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True)
    rate_plan_code = serializers.CharField(source='rate_plan.code', read_only=True)
    
    class Meta:
        model = RatePlanMapping
        fields = [
            'id', 'property_channel', 'property_channel_info',
            'rate_plan', 'rate_plan_name', 'rate_plan_code',
            'channel_rate_code', 'channel_rate_name', 'is_active'
        ]
        read_only_fields = ['id']


class RatePlanMappingCreateSerializer(serializers.ModelSerializer):
    """Create serializer for rate plan mapping."""
    
    class Meta:
        model = RatePlanMapping
        fields = [
            'property_channel', 'rate_plan', 'channel_rate_code',
            'channel_rate_name', 'is_active'
        ]
    
    def validate(self, data):
        # Check for duplicate mapping
        if RatePlanMapping.objects.filter(
            property_channel=data['property_channel'],
            rate_plan=data['rate_plan']
        ).exists():
            raise serializers.ValidationError(
                "This rate plan is already mapped to this channel"
            )
        return data


class AvailabilityUpdateSerializer(serializers.ModelSerializer):
    """Serializer for availability updates."""
    property_channel_info = PropertyChannelSerializer(source='property_channel', read_only=True)
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    channel_name = serializers.CharField(source='property_channel.channel.name', read_only=True)
    
    class Meta:
        model = AvailabilityUpdate
        fields = [
            'id', 'property_channel', 'property_channel_info', 'channel_name',
            'room_type', 'room_type_name', 'date', 'availability',
            'status', 'error_message', 'created_at', 'sent_at'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at']


class AvailabilityUpdateCreateSerializer(serializers.ModelSerializer):
    """Create serializer for availability updates."""
    
    class Meta:
        model = AvailabilityUpdate
        fields = ['property_channel', 'room_type', 'date', 'availability']
    
    def validate_date(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Cannot update availability for past dates")
        return value
    
    def validate_availability(self, value):
        if value < 0:
            raise serializers.ValidationError("Availability cannot be negative")
        return value


class RateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for rate updates."""
    property_channel_info = PropertyChannelSerializer(source='property_channel', read_only=True)
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True)
    channel_name = serializers.CharField(source='property_channel.channel.name', read_only=True)
    
    class Meta:
        model = RateUpdate
        fields = [
            'id', 'property_channel', 'property_channel_info', 'channel_name',
            'room_type', 'room_type_name', 'rate_plan', 'rate_plan_name',
            'date', 'rate', 'status', 'error_message', 'created_at', 'sent_at'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at']


class RateUpdateCreateSerializer(serializers.ModelSerializer):
    """Create serializer for rate updates."""
    
    class Meta:
        model = RateUpdate
        fields = ['property_channel', 'room_type', 'rate_plan', 'date', 'rate']
    
    def validate_date(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Cannot update rates for past dates")
        return value
    
    def validate_rate(self, value):
        if value <= 0:
            raise serializers.ValidationError("Rate must be greater than zero")
        return value


class ChannelReservationSerializer(serializers.ModelSerializer):
    """Serializer for channel reservations."""
    property_channel_info = PropertyChannelSerializer(source='property_channel', read_only=True)
    channel_name = serializers.CharField(source='property_channel.channel.name', read_only=True)
    reservation_id = serializers.IntegerField(source='reservation.id', read_only=True)
    reservation_number = serializers.CharField(source='reservation.reservation_number', read_only=True)
    
    class Meta:
        model = ChannelReservation
        fields = [
            'id', 'property_channel', 'property_channel_info', 'channel_name',
            'channel_booking_id', 'reservation', 'reservation_id', 'reservation_number',
            'guest_name', 'check_in_date', 'check_out_date', 'room_type_code',
            'rate_amount', 'total_amount', 'status', 'error_message',
            'raw_data', 'received_at', 'processed_at'
        ]
        read_only_fields = ['id', 'received_at', 'processed_at']


class ChannelReservationCreateSerializer(serializers.ModelSerializer):
    """Create serializer for channel reservations."""
    
    class Meta:
        model = ChannelReservation
        fields = [
            'property_channel', 'channel_booking_id', 'guest_name',
            'check_in_date', 'check_out_date', 'room_type_code',
            'rate_amount', 'total_amount', 'raw_data'
        ]
    
    def validate(self, data):
        # Check for duplicate booking
        if ChannelReservation.objects.filter(
            property_channel=data['property_channel'],
            channel_booking_id=data['channel_booking_id']
        ).exists():
            raise serializers.ValidationError(
                "This booking ID already exists for this channel"
            )
        
        # Validate dates
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )
        
        return data
