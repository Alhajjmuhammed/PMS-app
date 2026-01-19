from rest_framework import serializers
from apps.frontdesk.models import CheckIn, CheckOut, RoomMove


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
        fields = [
            'id', 'check_in', 'room_number', 'guest_name',
            'check_out_time', 'checked_out_by', 'key_cards_returned',
            'late_check_out', 'late_charge'
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
