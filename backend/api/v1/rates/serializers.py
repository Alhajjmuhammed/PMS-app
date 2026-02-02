from rest_framework import serializers
from apps.rates.models import RatePlan, Season, RoomRate, DateRate, Package, Discount, YieldRule


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


# ============= Revenue Management Serializers =============

class PackageSerializer(serializers.ModelSerializer):
    """Serializer for packages."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    rate_plan_name = serializers.CharField(source='rate_plan.name', read_only=True)
    nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'property', 'property_name', 'name', 'code', 'description',
            'rate_plan', 'rate_plan_name', 'includes_breakfast', 'includes_dinner',
            'includes_spa', 'other_inclusions', 'package_price', 'discount_percent',
            'valid_from', 'valid_to', 'nights', 'min_nights', 'is_active'
        ]
        read_only_fields = ['id']
    
    def get_nights(self, obj):
        """Calculate validity duration."""
        if obj.valid_from and obj.valid_to:
            return (obj.valid_to - obj.valid_from).days
        return None


class PackageCreateSerializer(serializers.ModelSerializer):
    """Create serializer for packages."""
    
    class Meta:
        model = Package
        fields = [
            'property', 'name', 'code', 'description', 'rate_plan',
            'includes_breakfast', 'includes_dinner', 'includes_spa',
            'other_inclusions', 'package_price', 'discount_percent',
            'valid_from', 'valid_to', 'min_nights', 'is_active'
        ]
    
    def validate(self, data):
        # Validate dates
        if data['valid_to'] <= data['valid_from']:
            raise serializers.ValidationError(
                "Valid to date must be after valid from date"
            )
        
        # Validate pricing
        if not data.get('package_price') and not data.get('discount_percent'):
            raise serializers.ValidationError(
                "Must specify either package price or discount percent"
            )
        
        if data.get('package_price') and data['package_price'] <= 0:
            raise serializers.ValidationError(
                "Package price must be greater than zero"
            )
        
        if data.get('discount_percent'):
            if data['discount_percent'] < 0 or data['discount_percent'] > 100:
                raise serializers.ValidationError(
                    "Discount percent must be between 0 and 100"
                )
        
        # Check for duplicate code
        if Package.objects.filter(
            property=data['property'],
            code=data['code']
        ).exists():
            raise serializers.ValidationError(
                "Package with this code already exists for this property"
            )
        
        return data


class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for discounts."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    usage_percentage = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Discount
        fields = [
            'id', 'property', 'property_name', 'name', 'code', 'discount_type',
            'value', 'valid_from', 'valid_to', 'max_uses', 'times_used',
            'usage_percentage', 'is_valid', 'min_nights', 'min_amount', 'is_active'
        ]
        read_only_fields = ['id', 'times_used']
    
    def get_usage_percentage(self, obj):
        """Calculate usage percentage."""
        if obj.max_uses:
            return round((obj.times_used / obj.max_uses) * 100, 2)
        return None
    
    def get_is_valid(self, obj):
        """Check if discount is currently valid."""
        from django.utils import timezone
        today = timezone.now().date()
        
        if not obj.is_active:
            return False
        
        if today < obj.valid_from or today > obj.valid_to:
            return False
        
        if obj.max_uses and obj.times_used >= obj.max_uses:
            return False
        
        return True


class DiscountCreateSerializer(serializers.ModelSerializer):
    """Create serializer for discounts."""
    
    class Meta:
        model = Discount
        fields = [
            'property', 'name', 'code', 'discount_type', 'value',
            'valid_from', 'valid_to', 'max_uses', 'min_nights',
            'min_amount', 'is_active'
        ]
    
    def validate(self, data):
        # Validate dates
        if data['valid_to'] <= data['valid_from']:
            raise serializers.ValidationError(
                "Valid to date must be after valid from date"
            )
        
        # Validate value
        if data['value'] <= 0:
            raise serializers.ValidationError(
                "Discount value must be greater than zero"
            )
        
        if data['discount_type'] == 'PERCENTAGE' and data['value'] > 100:
            raise serializers.ValidationError(
                "Percentage discount cannot exceed 100%"
            )
        
        # Check for duplicate code
        if Discount.objects.filter(code=data['code']).exists():
            raise serializers.ValidationError(
                "Discount code already exists"
            )
        
        return data


class YieldRuleSerializer(serializers.ModelSerializer):
    """Serializer for yield rules."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = YieldRule
        fields = [
            'id', 'property', 'property_name', 'name', 'trigger_type',
            'min_threshold', 'max_threshold', 'adjustment_percent',
            'priority', 'is_active'
        ]
        read_only_fields = ['id']


class YieldRuleCreateSerializer(serializers.ModelSerializer):
    """Create serializer for yield rules."""
    
    class Meta:
        model = YieldRule
        fields = [
            'property', 'name', 'trigger_type', 'min_threshold',
            'max_threshold', 'adjustment_percent', 'priority', 'is_active'
        ]
    
    def validate(self, data):
        # Validate thresholds
        min_threshold = data.get('min_threshold', 0)
        max_threshold = data.get('max_threshold')
        
        if max_threshold and max_threshold <= min_threshold:
            raise serializers.ValidationError(
                "Max threshold must be greater than min threshold"
            )
        
        # Validate adjustment
        if data['adjustment_percent'] == 0:
            raise serializers.ValidationError(
                "Adjustment percent cannot be zero"
            )
        
        if abs(data['adjustment_percent']) > 100:
            raise serializers.ValidationError(
                "Adjustment percent cannot exceed +/-100%"
            )
        
        return data
