"""
Serializers for Rates Management
"""
from rest_framework import serializers
from apps.rates.models import RatePlan, RoomRate, DateRate, YieldRule, Season, Package, Discount
from apps.rooms.models import RoomType


class RatePlanSerializer(serializers.ModelSerializer):
    """Serializer for rate plans."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    room_rates_count = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'RatePlanSerializerExtended'
        model = RatePlan
        fields = [
            'id',
            'property',
            'name',
            'code',
            'description',
            'rate_type',
            'is_active',
            'is_refundable',
            'valid_from',
            'valid_to',
            'min_nights',
            'max_nights',
            'min_advance_booking',
            'max_advance_booking',
            'cancellation_policy',
            'cancellation_hours',
            'created_at',
            'updated_at',
            'property_name', 'room_rates_count'
        
        ]
        
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_room_rates_count(self, obj):
        return obj.room_rates.count() if hasattr(obj, 'room_rates') else 0
    
    def validate(self, data):
        """Validate rate plan dates."""
        valid_from = data.get('valid_from')
        valid_to = data.get('valid_to')
        
        if valid_from and valid_to and valid_to <= valid_from:
            raise serializers.ValidationError("Valid to date must be after valid from date.")
        
        min_nights = data.get('min_nights', 1)
        max_nights = data.get('max_nights')
        
        if max_nights and max_nights < min_nights:
            raise serializers.ValidationError("Max nights must be greater than min nights.")
        
        return data


class RoomRateSerializer(serializers.ModelSerializer):
    """Serializer for room rates."""
    
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True)
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    season_name = serializers.CharField(source='season.name', read_only=True, allow_null=True)
    
    class Meta:
        ref_name = 'RoomRateSerializerExtended'
        model = RoomRate
        fields = [
            'id',
            'rate_plan',
            'room_type',
            'season',
            'single_rate',
            'double_rate',
            'extra_adult',
            'extra_child',
            'sunday_rate',
            'monday_rate',
            'tuesday_rate',
            'wednesday_rate',
            'thursday_rate',
            'friday_rate',
            'saturday_rate',
            'is_active',
            'rate_plan_name', 'room_type_name', 'season_name'
        
        ]
        
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate room rate."""
        effective_from = data.get('effective_from')
        effective_to = data.get('effective_to')
        
        if effective_from and effective_to and effective_to <= effective_from:
            raise serializers.ValidationError("Effective to date must be after effective from date.")
        
        base_rate = data.get('base_rate')
        if base_rate and base_rate < 0:
            raise serializers.ValidationError("Base rate cannot be negative.")
        
        return data


class DateRateSerializer(serializers.ModelSerializer):
    """Serializer for date-specific rate overrides."""
    
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True, allow_null=True)
    
    class Meta:
        ref_name = 'DateRateSerializerExtended'
        model = DateRate
        fields = [
            'id',
            'room_type',
            'rate_plan',
            'date',
            'rate',
            'min_stay',
            'is_closed',
            'room_type_name', 'rate_plan_name'
        
    
        ]
    
    def validate(self, data):
        """Validate date rate."""
        rate = data.get('rate')
        if rate and rate < 0:
            raise serializers.ValidationError("Rate cannot be negative.")
        
        return data


class YieldRuleSerializer(serializers.ModelSerializer):
    """Serializer for yield management rules."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        ref_name = 'YieldRuleSerializerExtended'
        model = YieldRule
        fields = [
            'id',
            'property',
            'name',
            'trigger_type',
            'min_threshold',
            'max_threshold',
            'adjustment_percent',
            'priority',
            'is_active',
            'property_name'
        
        ]
        
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate yield rule."""
        min_occ = data.get('min_occupancy_percent')
        max_occ = data.get('max_occupancy_percent')
        
        if min_occ and (min_occ < 0 or min_occ > 100):
            raise serializers.ValidationError("Min occupancy must be between 0 and 100.")
        
        if max_occ and (max_occ < 0 or max_occ > 100):
            raise serializers.ValidationError("Max occupancy must be between 0 and 100.")
        
        if min_occ and max_occ and max_occ <= min_occ:
            raise serializers.ValidationError("Max occupancy must be greater than min occupancy.")
        
        adjustment_type = data.get('adjustment_type')
        adjustment_value = data.get('adjustment_value')
        
        if adjustment_type == 'PERCENTAGE' and adjustment_value:
            if adjustment_value < -100 or adjustment_value > 100:
                raise serializers.ValidationError("Percentage adjustment must be between -100 and 100.")
        
        return data


class RatePlanDetailSerializer(RatePlanSerializer):
    """Detailed serializer with room rates."""
    
    room_rates = RoomRateSerializer(many=True, read_only=True)
    
    class Meta(RatePlanSerializer.Meta):
        fields = RatePlanSerializer.Meta.fields + ['room_rates']


class BulkRoomRateSerializer(serializers.Serializer):
    """Serializer for bulk room rate creation."""
    
    rate_plan = serializers.PrimaryKeyRelatedField(queryset=RatePlan.objects.all())
    room_types = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=RoomType.objects.all())
    )
    base_rate = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    extra_adult_rate = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False)
    extra_child_rate = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False)
    weekend_rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    effective_from = serializers.DateField(required=False, allow_null=True)
    effective_to = serializers.DateField(required=False, allow_null=True)


class RateCalculationSerializer(serializers.Serializer):
    """Serializer for rate calculation requests."""
    
    room_type = serializers.PrimaryKeyRelatedField(queryset=RoomType.objects.all())
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    adults = serializers.IntegerField(min_value=1, default=1)
    children = serializers.IntegerField(min_value=0, default=0)
    rate_plan = serializers.PrimaryKeyRelatedField(
        queryset=RatePlan.objects.all(),
        required=False,
        allow_null=True
    )
    
    def validate(self, data):
        """Validate rate calculation request."""
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        
        if check_out <= check_in:
            raise serializers.ValidationError("Check-out must be after check-in.")
        
        return data
