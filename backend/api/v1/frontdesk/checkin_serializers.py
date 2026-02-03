"""
Serializers for Front Desk operations
"""
from rest_framework import serializers
from apps.frontdesk.models import CheckIn, CheckOut, RoomMove, WalkIn, GuestMessage
from apps.guests.models import Guest
from apps.rooms.models import Room
from apps.reservations.models import Reservation


class CheckInSerializer(serializers.ModelSerializer):
    """Serializer for check-in operations."""
    
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    room_number = serializers.CharField(source='room.number', read_only=True)
    reservation_number = serializers.CharField(source='reservation.confirmation_number', read_only=True)
    checked_in_by_name = serializers.CharField(source='checked_in_by.get_full_name', read_only=True)
    
    class Meta:
        model = CheckIn
        fields = [
            'id', 'reservation', 'reservation_number', 'room', 'room_number',
            'guest', 'guest_name', 'check_in_time', 'expected_check_out',
            'id_type', 'id_number', 'id_expiry', 'registration_number',
            'registration_card', 'signature', 'key_card_number', 'keys_issued',
            'deposit_amount', 'deposit_method', 'notes', 'checked_in_by',
            'checked_in_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'registration_number', 'checked_in_by', 'created_at']
    
    def validate(self, data):
        """Validate check-in data."""
        # Check if reservation already has a check-in
        reservation = data.get('reservation')
        if reservation and hasattr(reservation, 'check_in'):
            raise serializers.ValidationError("This reservation is already checked in.")
        
        # Check if room is available
        room = data.get('room')
        if room and room.status != 'CLEAN':
            if room.status == 'OCCUPIED':
                raise serializers.ValidationError("Room is currently occupied.")
            elif room.status in ['DIRTY', 'INSPECTING']:
                raise serializers.ValidationError("Room is not ready for check-in.")
        
        return data


class CheckOutSerializer(serializers.ModelSerializer):
    """Serializer for check-out operations."""
    
    guest_name = serializers.CharField(source='check_in.guest.full_name', read_only=True)
    room_number = serializers.CharField(source='check_in.room.number', read_only=True)
    check_in_time = serializers.DateTimeField(source='check_in.check_in_time', read_only=True)
    nights_stayed = serializers.SerializerMethodField()
    
    class Meta:
        model = CheckOut
        ref_name = 'CheckOutDetail'
        fields = [
            'id', 'check_in', 'guest_name', 'room_number', 'check_in_time',
            'check_out_time', 'nights_stayed', 'keys_returned',
            'total_charges', 'total_payments', 'balance',
            'is_express', 'rating', 'feedback', 'notes'
        ]
        read_only_fields = ['id', 'check_out_time']
    
    def get_nights_stayed(self, obj):
        """Calculate nights stayed."""
        if obj.actual_check_out and obj.check_in.check_in_time:
            delta = obj.actual_check_out.date() - obj.check_in.check_in_time.date()
            return delta.days
        return 0
    
    def validate(self, data):
        """Validate check-out data."""
        check_in = data.get('check_in')
        
        # Check if already checked out
        if check_in and hasattr(check_in, 'check_out'):
            raise serializers.ValidationError("This guest is already checked out.")
        
        # Check outstanding balance
        outstanding = data.get('outstanding_balance', 0)
        if outstanding > 0 and data.get('payment_status') == 'PAID':
            raise serializers.ValidationError("Cannot mark as paid with outstanding balance.")
        
        return data


class RoomMoveSerializer(serializers.ModelSerializer):
    """Serializer for room move operations."""
    
    guest_name = serializers.CharField(source='check_in.guest.full_name', read_only=True)
    from_room_number = serializers.CharField(source='from_room.number', read_only=True)
    to_room_number = serializers.CharField(source='to_room.number', read_only=True)
    moved_by_name = serializers.CharField(source='moved_by.get_full_name', read_only=True)
    
    class Meta:
        model = RoomMove
        fields = [
            'id', 'check_in', 'guest_name', 'from_room', 'from_room_number',
            'to_room', 'to_room_number', 'move_time', 'reason', 'notes',
            'moved_by', 'moved_by_name'
        ]
        read_only_fields = ['id', 'moved_by', 'move_time']
    
    def validate(self, data):
        """Validate room move."""
        from_room = data.get('from_room')
        to_room = data.get('to_room')
        
        if from_room == to_room:
            raise serializers.ValidationError("Cannot move to the same room.")
        
        # Check if target room is available
        if to_room and to_room.status == 'OCCUPIED':
            raise serializers.ValidationError("Target room is currently occupied.")
        
        if to_room and to_room.status != 'CLEAN':
            raise serializers.ValidationError("Target room is not ready for occupancy.")
        
        return data


class WalkInSerializer(serializers.ModelSerializer):
    """Serializer for walk-in guests."""
    
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WalkIn
        fields = [
            'id', 'property', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'room_type', 'room_type_name', 'check_in_date', 'check_out_date',
            'adults', 'children', 'rate_per_night', 'is_converted', 'reservation',
            'notes', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'is_converted']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def validate(self, data):
        """Validate walk-in data."""
        arrival = data.get('arrival_date')
        departure = data.get('departure_date')
        
        if arrival and departure and departure <= arrival:
            raise serializers.ValidationError("Departure date must be after arrival date.")
        
        # Check room availability for the dates
        room = data.get('room')
        if room and room.status == 'OCCUPIED':
            raise serializers.ValidationError("Room is currently occupied.")
        
        return data


class CheckInDashboardSerializer(serializers.Serializer):
    """Serializer for check-in dashboard statistics."""
    
    total_check_ins_today = serializers.IntegerField()
    total_check_outs_today = serializers.IntegerField()
    expected_arrivals = serializers.IntegerField()
    expected_departures = serializers.IntegerField()
    in_house_guests = serializers.IntegerField()
    available_rooms = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    dirty_rooms = serializers.IntegerField()
    walk_ins_today = serializers.IntegerField()
    room_moves_today = serializers.IntegerField()
