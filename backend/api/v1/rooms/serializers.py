from rest_framework import serializers
from apps.rooms.models import Room, RoomType, RoomAmenity, RoomImage


class RoomAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomAmenity
        fields = ['id', 'name', 'icon']


class RoomTypeSerializer(serializers.ModelSerializer):
    amenities = RoomAmenitySerializer(many=True, read_only=True, source='room_amenities')
    
    class Meta:
        model = RoomType
        fields = [
            'id', 'name', 'code', 'description', 'base_rate',
            'max_occupancy', 'max_adults', 'max_children',
            'bed_type', 'amenities'
        ]


class RoomSerializer(serializers.ModelSerializer):
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    floor_name = serializers.CharField(source='floor.name', read_only=True)
    building_name = serializers.CharField(source='floor.building.name', read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'room_type', 'room_type_name',
            'floor', 'floor_name', 'building_name',
            'status', 'fo_status', 'is_smoking', 'is_accessible',
            'is_active', 'notes'
        ]


class RoomStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Room.RoomStatus.choices)
    fo_status = serializers.ChoiceField(choices=Room.FrontOfficeStatus.choices, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class RoomImageSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = RoomImage
        fields = ['id', 'image', 'caption', 'is_primary', 'sort_order', 'uploaded_at', 'uploaded_by', 'uploaded_by_name']
        read_only_fields = ['uploaded_at', 'uploaded_by', 'uploaded_by_name']
