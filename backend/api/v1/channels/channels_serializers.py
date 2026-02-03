"""
Serializers for Channels Module
"""
from rest_framework import serializers
from apps.channels.models import (
    PropertyChannel, RoomTypeMapping, RatePlanMapping,
    AvailabilityUpdate, RateUpdate, ChannelReservation, Channel
)
from django.utils import timezone


class ChannelSerializer(serializers.ModelSerializer):
    """Serializer for channels."""
    
    class Meta:
        model = Channel
        ref_name = 'ChannelDetail'
        fields = [
            'id', 'name', 'code', 'channel_type', 'commission_percent',
            'api_url', 'logo', 'is_active'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True}
        }


class PropertyChannelSerializer(serializers.ModelSerializer):
    """Serializer for property channels."""
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    channel_code = serializers.CharField(source='channel.code', read_only=True)
    channel_type = serializers.CharField(source='channel.channel_type', read_only=True)
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True)
    room_mappings_count = serializers.IntegerField(
        source='room_mappings.count', read_only=True
    )
    rate_mappings_count = serializers.IntegerField(
        source='rate_mappings.count', read_only=True
    )
    
    class Meta:
        model = PropertyChannel
        fields = [
            'id', 'property', 'channel', 'channel_name', 'channel_code',
            'channel_type', 'property_code', 'rate_plan', 'rate_plan_name',
            'rate_markup', 'min_availability', 'max_availability',
            'sync_rates', 'sync_availability', 'sync_restrictions',
            'last_sync', 'is_active', 'room_mappings_count', 'rate_mappings_count'
        ]
        read_only_fields = ['id', 'last_sync']
    
    def validate_rate_markup(self, value):
        """Validate rate markup percentage."""
        if value < -100 or value > 100:
            raise serializers.ValidationError(
                "Rate markup must be between -100% and 100%"
            )
        return value


class RoomTypeMappingSerializer(serializers.ModelSerializer):
    """Serializer for room type mappings."""
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    room_type_code = serializers.CharField(source='room_type.code', read_only=True)
    channel_name = serializers.CharField(
        source='property_channel.channel.name', read_only=True
    )
    
    class Meta:
        model = RoomTypeMapping
        fields = [
            'id', 'property_channel', 'channel_name', 'room_type',
            'room_type_name', 'room_type_code', 'channel_room_code',
            'channel_room_name', 'is_active'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate room type mapping uniqueness."""
        property_channel = data.get('property_channel')
        room_type = data.get('room_type')
        
        if property_channel and room_type:
            # Check room type belongs to same property
            if room_type.property_id != property_channel.property_id:
                raise serializers.ValidationError(
                    "Room type must belong to the same property"
                )
        
        return data


class RatePlanMappingSerializer(serializers.ModelSerializer):
    """Serializer for rate plan mappings."""
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True)
    rate_plan_code = serializers.CharField(source='rate_plan.code', read_only=True)
    channel_name = serializers.CharField(
        source='property_channel.channel.name', read_only=True
    )
    
    class Meta:
        model = RatePlanMapping
        fields = [
            'id', 'property_channel', 'channel_name', 'rate_plan',
            'rate_plan_name', 'rate_plan_code', 'channel_rate_code',
            'channel_rate_name', 'is_active'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate rate plan mapping uniqueness."""
        property_channel = data.get('property_channel')
        rate_plan = data.get('rate_plan')
        
        if property_channel and rate_plan:
            # Check rate plan belongs to same property
            if rate_plan.property_id != property_channel.property_id:
                raise serializers.ValidationError(
                    "Rate plan must belong to the same property"
                )
        
        return data


class AvailabilityUpdateSerializer(serializers.ModelSerializer):
    """Serializer for availability updates."""
    channel_name = serializers.CharField(
        source='property_channel.channel.name', read_only=True
    )
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    
    class Meta:
        model = AvailabilityUpdate
        fields = [
            'id', 'property_channel', 'channel_name', 'room_type',
            'room_type_name', 'date', 'availability', 'status',
            'error_message', 'created_at', 'sent_at'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at']
    
    def validate_availability(self, value):
        """Validate availability is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Availability cannot be negative")
        return value
    
    def validate_date(self, value):
        """Validate date is not in the past."""
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("Cannot update availability for past dates")
        return value


class RateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for rate updates."""
    channel_name = serializers.CharField(
        source='property_channel.channel.name', read_only=True
    )
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True)
    
    class Meta:
        model = RateUpdate
        fields = [
            'id', 'property_channel', 'channel_name', 'room_type',
            'room_type_name', 'rate_plan', 'rate_plan_name', 'date',
            'rate', 'status', 'error_message', 'created_at', 'sent_at'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at']
    
    def validate_rate(self, value):
        """Validate rate is positive."""
        if value <= 0:
            raise serializers.ValidationError("Rate must be greater than 0")
        return value
    
    def validate_date(self, value):
        """Validate date is not in the past."""
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("Cannot update rates for past dates")
        return value


class ChannelReservationSerializer(serializers.ModelSerializer):
    """Serializer for channel reservations."""
    channel_name = serializers.CharField(
        source='property_channel.channel.name', read_only=True
    )
    property_name = serializers.CharField(
        source='property_channel.property.name', read_only=True
    )
    reservation_number = serializers.CharField(
        source='reservation.reservation_number', read_only=True
    )
    nights = serializers.SerializerMethodField()
    
    class Meta:
        model = ChannelReservation
        fields = [
            'id', 'property_channel', 'channel_name', 'property_name',
            'channel_booking_id', 'reservation', 'reservation_number',
            'guest_name', 'check_in_date', 'check_out_date', 'nights',
            'room_type_code', 'rate_amount', 'total_amount', 'status',
            'error_message', 'received_at', 'processed_at', 'raw_data'
        ]
        read_only_fields = ['id', 'received_at', 'processed_at']
    
    def get_nights(self, obj):
        """Calculate number of nights."""
        delta = obj.check_out_date - obj.check_in_date
        return delta.days
    
    def validate(self, data):
        """Validate channel reservation data."""
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date"
                )
        
        return data


class ChannelDashboardSerializer(serializers.Serializer):
    """Serializer for channel dashboard statistics."""
    active_channels = serializers.IntegerField()
    total_mappings = serializers.IntegerField()
    pending_updates = serializers.IntegerField()
    failed_updates = serializers.IntegerField()
    unprocessed_reservations = serializers.IntegerField()
    reservations_today = serializers.IntegerField()
    last_sync_time = serializers.DateTimeField(allow_null=True)


class BulkAvailabilityUpdateSerializer(serializers.Serializer):
    """Serializer for bulk availability updates."""
    property_channel = serializers.IntegerField()
    room_type = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    availability = serializers.IntegerField(min_value=0)
    
    def validate(self, data):
        """Validate bulk update data."""
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        return data


class BulkRateUpdateSerializer(serializers.Serializer):
    """Serializer for bulk rate updates."""
    property_channel = serializers.IntegerField()
    room_type = serializers.IntegerField()
    rate_plan = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    rate = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    
    def validate(self, data):
        """Validate bulk update data."""
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        if data['rate'] <= 0:
            raise serializers.ValidationError("Rate must be greater than 0")
        return data
