"""
Serializers for Room Configuration
"""
from rest_framework import serializers
from apps.rooms.models import RoomType, RoomAmenity, RoomTypeAmenity, RoomImage, RoomStatusLog
from apps.properties.models import Property


class RoomTypeSerializer(serializers.ModelSerializer):
    """Serializer for room types."""
    
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    total_rooms = serializers.SerializerMethodField()
    amenities_count = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'RoomTypeSerializerExtended'
        model = RoomType
        fields = [
            'id',
            'hotel',
            'name',
            'code',
            'description',
            'max_occupancy',
            'max_adults',
            'max_children',
            'size_sqm',
            'bed_type',
            'base_rate',
            'extra_adult_rate',
            'extra_child_rate',
            'is_active',
            'sort_order',
            'created_at',
            'updated_at',
            'hotel_name', 'total_rooms', 'amenities_count'
        
        ]
        
        read_only_fields = ['id', 'hotel', 'created_at', 'updated_at']
    
    def get_total_rooms(self, obj):
        return obj.rooms.count() if hasattr(obj, 'rooms') else 0
    
    def get_amenities_count(self, obj):
        return obj.amenities.count() if hasattr(obj, 'amenities') else 0
    
    def validate_code(self, value):
        """Validate room type code uniqueness within the same hotel."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Room type code must be at least 2 characters.")
        value = value.strip().upper()
        # Uniqueness is enforced per (hotel, code) at DB level.
        # We do a best-effort check here; hotel is not yet known at field-level
        # validation, so full uniqueness is caught by perform_create.
        return value

    def validate(self, data):
        """Validate room type."""
        max_occ = data.get('max_occupancy')
        max_adults = data.get('max_adults', 0)
        max_children = data.get('max_children', 0)

        if max_occ and max_occ < 1:
            raise serializers.ValidationError("Max occupancy must be at least 1.")

        if max_adults and max_adults < 1:
            raise serializers.ValidationError("Max adults must be at least 1.")

        return data


class RoomAmenitySerializer(serializers.ModelSerializer):
    """Serializer for room amenities."""
    
    class Meta:
        ref_name = 'RoomAmenitySerializerExtended'
        model = RoomAmenity
        fields = [
            'id',
            'name',
            'description',
            'icon',
            'category'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomTypeAmenitySerializer(serializers.ModelSerializer):
    """Serializer for room type amenity assignments."""
    
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    amenity_name = serializers.CharField(source='amenity.name', read_only=True)
    amenity_icon = serializers.CharField(source='amenity.icon', read_only=True)
    
    class Meta:
        ref_name = 'RoomTypeAmenitySerializerExtended'
        model = RoomTypeAmenity
        fields = [
            'id',
            'room_type',
            'amenity',
            'room_type_name', 'amenity_name', 'amenity_icon'
        
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
    
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'RoomImageSerializerExtended'
        model = RoomImage
        fields = [
            'id',
            'room',
            'image',
            'caption',
            'is_primary',
            'room_number', 'image_url'
        
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
    
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    changed_by_name = serializers.SerializerMethodField()
    
    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.email
        return None
    
    class Meta:
        model = RoomStatusLog
        fields = [
            'id',
            'room',
            'new_status',
            'notes',
            'changed_by',
            'room_number', 'changed_by_name'
        
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
            'id', 'room_number', 'status', 'floor__name'
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
