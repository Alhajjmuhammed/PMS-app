from rest_framework import serializers
from django.utils import timezone
from datetime import date, timedelta
from apps.reservations.models import Reservation, ReservationRoom, GroupBooking
from apps.reservations.services import AvailabilityService
from apps.guests.models import Guest


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'nationality'
        ]


class ReservationRoomSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    
    class Meta:
        model = ReservationRoom
        fields = ['id', 'room', 'room_number', 'room_type', 'room_type_name', 'rate', 'adults', 'children']


class ReservationSerializer(serializers.ModelSerializer):
    guest = GuestSerializer(read_only=True)
    rooms = ReservationRoomSerializer(many=True, read_only=True)
    nights = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'confirmation_number', 'hotel', 'guest',
            'check_in_date', 'check_out_date', 'nights',
            'adults', 'children', 'status', 'source',
            'rate_plan', 'total_amount',
            'special_requests', 'rooms', 'created_at'
        ]


class ReservationCreateSerializer(serializers.ModelSerializer):
    guest_id = serializers.IntegerField(required=False)
    guest_first_name = serializers.CharField(required=False, max_length=100)
    guest_last_name = serializers.CharField(required=False, max_length=100)
    guest_email = serializers.EmailField(required=False)
    guest_phone = serializers.CharField(required=False, max_length=20)
    room_type_id = serializers.IntegerField()
    
    class Meta:
        model = Reservation
        fields = [
            'property', 'check_in_date', 'check_out_date',
            'adults', 'children', 'room_rate', 'special_requests',
            'guest_id', 'guest_first_name', 'guest_last_name',
            'guest_email', 'guest_phone', 'room_type_id'
        ]
    
    def validate_check_in_date(self, value):
        """Validate check-in date is not in the past."""
        if value < date.today():
            raise serializers.ValidationError("Check-in date cannot be in the past.")
        return value
    
    def validate_check_out_date(self, value):
        """Validate check-out date."""
        if value < date.today():
            raise serializers.ValidationError("Check-out date cannot be in the past.")
        return value
    
    def validate_adults(self, value):
        """Validate number of adults."""
        if value < 1:
            raise serializers.ValidationError("At least one adult is required.")
        if value > 10:
            raise serializers.ValidationError("Maximum 10 adults per reservation.")
        return value
    
    def validate_children(self, value):
        """Validate number of children."""
        if value < 0:
            raise serializers.ValidationError("Number of children cannot be negative.")
        if value > 10:
            raise serializers.ValidationError("Maximum 10 children per reservation.")
        return value
    
    def validate_room_rate(self, value):
        """Validate room rate."""
        if value <= 0:
            raise serializers.ValidationError("Room rate must be positive.")
        if value > 100000:
            raise serializers.ValidationError("Room rate exceeds maximum allowed.")
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        # Validate dates
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date."
                )
            
            nights = (check_out - check_in).days
            if nights > 365:
                raise serializers.ValidationError(
                    "Maximum stay is 365 nights."
                )
            
            # Use availability service for validation
            is_valid, error_msg = AvailabilityService.validate_booking_dates(
                check_in, check_out
            )
            if not is_valid:
                raise serializers.ValidationError(error_msg)
        
        # Validate guest info
        if not data.get('guest_id'):
            if not data.get('guest_email'):
                raise serializers.ValidationError(
                    "Either guest_id or guest_email is required."
                )
            if not data.get('guest_first_name') or not data.get('guest_last_name'):
                raise serializers.ValidationError(
                    "Guest first name and last name are required for new guests."
                )
        
        # Validate total occupancy
        adults = data.get('adults', 1)
        children = data.get('children', 0)
        if adults + children > 15:
            raise serializers.ValidationError(
                "Total occupancy exceeds maximum (15 persons)."
            )
        
        return data


# ============= Group Booking Serializers =============

class GroupBookingSerializer(serializers.ModelSerializer):
    """Serializer for group bookings."""
    
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    nights = serializers.SerializerMethodField()
    pickup_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupBooking
        fields = [
            'id', 'hotel', 'hotel_name', 'name', 'code', 'contact_name',
            'contact_email', 'contact_phone', 'company', 'company_name',
            'check_in_date', 'check_out_date', 'cutoff_date', 'nights',
            'rooms_blocked', 'rooms_picked_up', 'pickup_percentage',
            'status', 'group_rate', 'deposit_required', 'notes',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
    
    def get_nights(self, obj):
        """Calculate number of nights."""
        if obj.check_in_date and obj.check_out_date:
            delta = obj.check_out_date - obj.check_in_date
            return delta.days
        return 0
    
    def get_pickup_percentage(self, obj):
        """Calculate pickup percentage."""
        if obj.rooms_blocked > 0:
            return round((obj.rooms_picked_up / obj.rooms_blocked) * 100, 2)
        return 0


class GroupBookingCreateSerializer(serializers.ModelSerializer):
    """Create serializer for group bookings."""
    
    class Meta:
        model = GroupBooking
        fields = [
            'hotel', 'name', 'contact_name', 'contact_email', 'contact_phone',
            'company', 'check_in_date', 'check_out_date', 'cutoff_date',
            'rooms_blocked', 'status', 'group_rate', 'deposit_required', 'notes'
        ]
    
    def validate(self, data):
        # Validate dates
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )
        
        # Validate cutoff date
        if data.get('cutoff_date'):
            if data['cutoff_date'] > data['check_in_date']:
                raise serializers.ValidationError(
                    "Cutoff date must be before check-in date"
                )
        
        # Validate rooms blocked
        if data.get('rooms_blocked', 0) < 1:
            raise serializers.ValidationError(
                "Must block at least 1 room for group booking"
            )
        
        return data
    
    def create(self, validated_data):
        # Generate unique group code
        import random
        import string
        hotel = validated_data['hotel']
        prefix = hotel.code if hasattr(hotel, 'code') else 'GRP'
        suffix = ''.join(random.choices(string.digits, k=6))
        validated_data['code'] = f"{prefix}{suffix}"
        
        return super().create(validated_data)


class GroupBookingUpdateSerializer(serializers.ModelSerializer):
    """Update serializer for group bookings."""
    
    class Meta:
        model = GroupBooking
        fields = [
            'name', 'contact_name', 'contact_email', 'contact_phone',
            'company', 'check_in_date', 'check_out_date', 'cutoff_date',
            'rooms_blocked', 'rooms_picked_up', 'status', 'group_rate',
            'deposit_required', 'notes'
        ]
    
    def validate(self, data):
        # Validate dates if provided
        instance = self.instance
        check_in = data.get('check_in_date', instance.check_in_date)
        check_out = data.get('check_out_date', instance.check_out_date)
        
        if check_out <= check_in:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )
        
        # Validate cutoff date
        cutoff = data.get('cutoff_date')
        if cutoff and cutoff > check_in:
            raise serializers.ValidationError(
                "Cutoff date must be before check-in date"
            )
        
        # Validate picked up rooms
        rooms_picked_up = data.get('rooms_picked_up', instance.rooms_picked_up)
        rooms_blocked = data.get('rooms_blocked', instance.rooms_blocked)
        
        if rooms_picked_up > rooms_blocked:
            raise serializers.ValidationError(
                "Rooms picked up cannot exceed rooms blocked"
            )
        
        return data
