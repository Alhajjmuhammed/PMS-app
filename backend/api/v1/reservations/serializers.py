from rest_framework import serializers
from django.utils import timezone
from datetime import date, timedelta
from apps.reservations.models import Reservation, ReservationRoom
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
