from rest_framework import serializers
from apps.frontdesk.models import CheckIn, CheckOut, RoomMove, WalkIn


class CheckInSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='reservation.guest.full_name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    
    class Meta:
        model = CheckIn
        fields = [
            'id', 'reservation', 'room', 'room_number', 'guest_name',
            'check_in_time', 'checked_in_by', 'id_verified', 'key_cards_issued'
        ]


class CheckOutSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='check_in.reservation.guest.full_name', read_only=True)
    room_number = serializers.CharField(source='check_in.room.room_number', read_only=True)
    
    class Meta:
        model = CheckOut
        ref_name = 'CheckOutBasic'
        fields = [
            'id', 'check_in', 'room_number', 'guest_name',
            'check_out_time', 'keys_returned', 'is_express',
            'rating', 'feedback'
        ]


class CheckInRequestSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()
    room_id = serializers.IntegerField()
    id_verified = serializers.BooleanField(default=True)
    key_cards_issued = serializers.IntegerField(default=2)


class CheckOutRequestSerializer(serializers.Serializer):
    check_in_id = serializers.IntegerField()
    key_cards_returned = serializers.IntegerField(default=0)
    late_check_out = serializers.BooleanField(default=False)
    late_charge = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)


class RoomMoveSerializer(serializers.Serializer):
    check_in_id = serializers.IntegerField()
    new_room_id = serializers.IntegerField()
    reason = serializers.CharField()


# ============= Walk-In Serializers =============

class WalkInSerializer(serializers.ModelSerializer):
    """Serializer for walk-ins."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    nights = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    reservation_number = serializers.CharField(source='reservation.confirmation_number', read_only=True, allow_null=True)
    
    class Meta:
        model = WalkIn
        fields = [
            'id', 'property', 'property_name', 'first_name', 'last_name',
            'email', 'phone', 'room_type', 'room_type_name', 'check_in_date',
            'check_out_date', 'nights', 'adults', 'children', 'rate_per_night',
            'total_amount', 'is_converted', 'reservation', 'reservation_number',
            'notes', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'is_converted', 'reservation', 'created_at']
    
    def get_nights(self, obj):
        """Calculate number of nights."""
        if obj.check_in_date and obj.check_out_date:
            delta = obj.check_out_date - obj.check_in_date
            return delta.days
        return 0
    
    def get_total_amount(self, obj):
        """Calculate total amount."""
        nights = self.get_nights(obj)
        return float(obj.rate_per_night * nights)


class WalkInCreateSerializer(serializers.ModelSerializer):
    """Create serializer for walk-ins."""
    
    class Meta:
        model = WalkIn
        fields = [
            'property', 'first_name', 'last_name', 'email', 'phone',
            'room_type', 'check_in_date', 'check_out_date', 'adults',
            'children', 'rate_per_night', 'notes'
        ]
    
    def validate(self, data):
        # Validate dates
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )
        
        # Validate date is not in the past
        from django.utils import timezone
        today = timezone.now().date()
        if data['check_in_date'] < today:
            raise serializers.ValidationError(
                "Check-in date cannot be in the past"
            )
        
        # Validate occupancy
        if data.get('adults', 0) < 1:
            raise serializers.ValidationError(
                "At least one adult is required"
            )
        
        if data.get('adults', 0) + data.get('children', 0) > 10:
            raise serializers.ValidationError(
                "Total occupancy exceeds maximum"
            )
        
        # Validate rate
        if data.get('rate_per_night', 0) <= 0:
            raise serializers.ValidationError(
                "Rate per night must be greater than zero"
            )
        
        return data


class WalkInUpdateSerializer(serializers.ModelSerializer):
    """Update serializer for walk-ins."""
    
    class Meta:
        model = WalkIn
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'room_type',
            'check_in_date', 'check_out_date', 'adults', 'children',
            'rate_per_night', 'notes'
        ]
    
    def validate(self, data):
        instance = self.instance
        
        # Check if already converted
        if instance.is_converted:
            raise serializers.ValidationError(
                "Cannot update walk-in that has been converted to reservation"
            )
        
        # Validate dates if provided
        check_in = data.get('check_in_date', instance.check_in_date)
        check_out = data.get('check_out_date', instance.check_out_date)
        
        if check_out <= check_in:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )
        
        return data
