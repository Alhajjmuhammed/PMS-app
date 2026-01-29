from rest_framework import serializers
from apps.rates.models import RatePlan, Season, RoomRate, DateRate


class SeasonSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = Season
        fields = ['id', 'property', 'property_name', 'name', 'start_date', 'end_date', 'priority', 'is_active']
    
    def validate(self, data):
        """Validate season dates."""
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        return data


class RoomRateSerializer(serializers.ModelSerializer):
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True)
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    season_name = serializers.CharField(source='season.name', read_only=True, allow_null=True)
    
    class Meta:
        model = RoomRate
        fields = [
            'id', 'rate_plan', 'rate_plan_name', 'room_type', 'room_type_name',
            'season', 'season_name', 'single_rate', 'double_rate',
            'extra_adult', 'extra_child', 
            'sunday_rate', 'monday_rate', 'tuesday_rate', 'wednesday_rate',
            'thursday_rate', 'friday_rate', 'saturday_rate',
            'is_active'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate room rate data."""
        # Check uniqueness
        rate_plan = data.get('rate_plan')
        room_type = data.get('room_type')
        season = data.get('season')
        
        instance = self.instance
        qs = RoomRate.objects.filter(
            rate_plan=rate_plan,
            room_type=room_type,
            season=season
        )
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A rate already exists for this combination of rate plan, room type, and season."
            )
        
        return data
    
    def validate_single_rate(self, value):
        """Validate single rate."""
        if value < 0:
            raise serializers.ValidationError("Single rate cannot be negative.")
        return value
    
    def validate_double_rate(self, value):
        """Validate double rate."""
        if value < 0:
            raise serializers.ValidationError("Double rate cannot be negative.")
        return value


class DateRateSerializer(serializers.ModelSerializer):
    """Serializer for date-specific rate overrides."""
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True, allow_null=True)
    
    class Meta:
        model = DateRate
        fields = [
            'id', 'room_type', 'room_type_name', 'rate_plan', 'rate_plan_name',
            'date', 'rate', 'min_stay', 'is_closed'
        ]
    
    def validate_rate(self, value):
        """Validate rate is positive."""
        if value < 0:
            raise serializers.ValidationError("Rate cannot be negative.")
        return value


class RatePlanSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    room_rates = RoomRateSerializer(many=True, read_only=True)
    
    class Meta:
        model = RatePlan
        fields = [
            'id', 'property', 'property_name', 'name', 'code', 'rate_type',
            'description', 'min_nights', 'max_nights', 'min_advance_booking',
            'max_advance_booking', 'cancellation_policy', 'cancellation_hours',
            'valid_from', 'valid_to', 'is_refundable', 'is_active',
            'room_rates', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
