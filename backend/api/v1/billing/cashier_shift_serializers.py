from rest_framework import serializers
from apps.billing.models import CashierShift
from django.utils import timezone


class CashierShiftSerializer(serializers.ModelSerializer):
    """Serializer for cashier shifts."""
    user_name = serializers.SerializerMethodField()
    property_name = serializers.CharField(source='property.name', read_only=True)
    duration_hours = serializers.SerializerMethodField()
    expected_closing = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()
    total_received = serializers.SerializerMethodField()
    
    class Meta:
        model = CashierShift
        fields = [
            'id', 'user', 'user_name', 'property', 'property_name',
            'shift_start', 'shift_end', 'duration_hours', 'is_open',
            'opening_balance', 'closing_balance', 'expected_closing',
            'total_cash_received', 'total_card_received', 'total_received',
            'is_balanced', 'variance', 'notes'
        ]
        read_only_fields = ['id']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()
    
    def get_duration_hours(self, obj):
        if obj.shift_end:
            duration = obj.shift_end - obj.shift_start
            return round(duration.total_seconds() / 3600, 2)
        return None
    
    def get_expected_closing(self, obj):
        return obj.opening_balance + obj.total_cash_received + obj.total_card_received
    
    def get_is_open(self, obj):
        return obj.shift_end is None
    
    def get_total_received(self, obj):
        return obj.total_cash_received + obj.total_card_received


class CashierShiftOpenSerializer(serializers.ModelSerializer):
    """Serializer for opening a cashier shift."""
    
    class Meta:
        model = CashierShift
        fields = ['opening_balance', 'notes']
    
    def validate_opening_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Opening balance cannot be negative.")
        return value
    
    def create(self, validated_data):
        # Auto-set user, property, and shift_start
        request = self.context.get('request')
        validated_data['user'] = request.user
        validated_data['property'] = request.user.assigned_property
        validated_data['shift_start'] = timezone.now()
        return super().create(validated_data)


class CashierShiftCloseSerializer(serializers.Serializer):
    """Serializer for closing a cashier shift."""
    closing_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_closing_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Closing balance cannot be negative.")
        return value


class CashierShiftReconcileSerializer(serializers.Serializer):
    """Serializer for reconciling a cashier shift."""
    actual_cash = serializers.DecimalField(max_digits=12, decimal_places=2)
    actual_card = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data.get('actual_cash', 0) < 0:
            raise serializers.ValidationError({
                'actual_cash': 'Actual cash cannot be negative.'
            })
        if data.get('actual_card', 0) < 0:
            raise serializers.ValidationError({
                'actual_card': 'Actual card cannot be negative.'
            })
        return data
