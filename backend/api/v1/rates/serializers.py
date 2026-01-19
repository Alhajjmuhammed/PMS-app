from rest_framework import serializers
from apps.rates.models import RatePlan, Season, RoomRate


class SeasonSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = Season
        fields = ['id', 'property', 'property_name', 'name', 'start_date', 'end_date', 'priority', 'is_active']


class RoomRateSerializer(serializers.ModelSerializer):
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True)
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    season_name = serializers.CharField(source='season.name', read_only=True)
    
    class Meta:
        model = RoomRate
        fields = [
            'id', 'rate_plan', 'rate_plan_name', 'room_type', 'room_type_name',
            'season', 'season_name', 'single_rate', 'double_rate',
            'extra_adult', 'extra_child', 'is_active'
        ]


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
