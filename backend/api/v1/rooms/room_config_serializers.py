"""
Serializers for Room Configuration
"""
from rest_framework import serializers
from apps.rooms.models import RoomType, RoomAmenity, RoomTypeAmenity, RoomImage, RoomStatusLog
from apps.properties.models import Property


class RoomTypeSerializer(serializers.ModelSerializer):
    """Serializer for room types."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    total_rooms = serializers.SerializerMethodField()
    amenities_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomType
        fields = [
            'id', 'property', 'property_name', 'name', 'code', 'description',
            'base_occupancy', 'max_occupancy', 'extra_beds_allowed',
            'size_sqm', 'view_type', 'bed_configuration', 'is_active',
            'sort_order', 'total_rooms', 'amenities_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_rooms(self, obj):
        return obj.rooms.count() if hasattr(obj, 'rooms') else 0
    
    def get_amenities_count(self, obj):
        return obj.amenities.count() if hasattr(obj, 'amenities') else 0
    
    def validate(self, data):
        """Validate room type."""
        base_occ = data.get('base_occupancy')
        max_occ = data.get('max_occupancy')
        
        if base_occ and max_occ and max_occ < base_occ:
            raise serializers.ValidationError("Max occupancy must be >= base occupancy.")
        
        if base_occ and base_occ < 1:
            raise serializers.ValidationError("Base occupancy must be at least 1.")
        
        return data


class RoomAmenitySerializer(serializers.ModelSerializer):
    """Serializer for room amenities."""
    
    class Meta:
        model = RoomAmenity
        fields = [
            'id', 'name', 'description', 'icon', 'category',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomTypeAmenitySerializer(serializers.ModelSerializer):
    """Serializer for room type amenity assignments."""
    
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    amenity_name = serializers.CharField(source='amenity.name', read_only=True)
    amenity_icon = serializers.CharField(source='amenity.icon', read_only=True)
    
    class Meta:
        model = RoomTypeAmenity
        fields = [
            'id', 'room_type', 'room_type_name', 'amenity', 'amenity_name',
            'amenity_icon', 'quantity', 'is_complimentary', 'notes'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate room type amenity."""
        quantity = data.get('quantity', 1)
        if quantity < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        
        return data


class RoomImageSerializer(serializers.ModelSerializer):
    """Serializer for room images."""
    
    room_number = serializers.CharField(source='room.number', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomImage
        fields = [
            'id', 'room', 'room_number', 'image', 'image_url',
            'caption', 'is_primary', 'display_order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class RoomStatusLogSerializer(serializers.ModelSerializer):
    """Serializer for room status change logs."""
    
    room_number = serializers.CharField(source='room.number', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = RoomStatusLog
        fields = [
            'id', 'room', 'room_number', 'old_status', 'new_status',
            'reason', 'notes', 'changed_by', 'changed_by_name',
            'changed_at', 'created_at'
        ]
        read_only_fields = ['id', 'changed_by', 'created_at']


class RoomTypeDetailSerializer(RoomTypeSerializer):
    """Detailed room type serializer with amenities."""
    
    amenities = serializers.SerializerMethodField()
    rooms = serializers.SerializerMethodField()
    
    class Meta(RoomTypeSerializer.Meta):
        fields = RoomTypeSerializer.Meta.fields + ['amenities', 'rooms']
    
    def get_amenities(self, obj):
        """Get amenities for this room type."""
        room_type_amenities = RoomTypeAmenity.objects.filter(
            room_type=obj
        ).select_related('amenity')
        
        return [{
            'id': rta.amenity.id,
            'name': rta.amenity.name,
            'icon': rta.amenity.icon,
            'quantity': rta.quantity,
            'is_complimentary': rta.is_complimentary
        } for rta in room_type_amenities]
    
    def get_rooms(self, obj):
        """Get rooms of this type."""
        from apps.rooms.models import Room
        rooms = Room.objects.filter(room_type=obj).values(
            'id', 'number', 'status', 'floor__name'
        )
        return list(rooms)


class BulkAmenityAssignSerializer(serializers.Serializer):
    """Serializer for bulk amenity assignment."""
    
    room_type = serializers.PrimaryKeyRelatedField(queryset=RoomType.objects.all())
    amenities = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=RoomAmenity.objects.all())
    )
    is_complimentary = serializers.BooleanField(default=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
