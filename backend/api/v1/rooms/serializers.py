from rest_framework import serializers
from apps.rooms.models import Room, RoomType, RoomAmenity, RoomImage, RoomTypeAmenity


class RoomAmenitySerializer(serializers.ModelSerializer):
    """Full serializer for RoomAmenity CRUD operations."""
    
    class Meta:
        model = RoomAmenity
        fields = ['id', 'name', 'code', 'category', 'description', 'icon']
        read_only_fields = ['id']
    
    def validate_code(self, value):
        """Validate amenity code uniqueness."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Amenity code must be at least 2 characters.")
        
        value = value.strip().upper()
        
        # Check uniqueness
        instance = self.instance
        if instance:
            if RoomAmenity.objects.exclude(pk=instance.pk).filter(code=value).exists():
                raise serializers.ValidationError("An amenity with this code already exists.")
        else:
            if RoomAmenity.objects.filter(code=value).exists():
                raise serializers.ValidationError("An amenity with this code already exists.")
        
        return value
    
    def validate_name(self, value):
        """Validate amenity name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Amenity name must be at least 2 characters.")
        if len(value) > 100:
            raise serializers.ValidationError("Amenity name is too long.")
        return value.strip()


class RoomAmenityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for amenity list view."""
    
    class Meta:
        model = RoomAmenity
        fields = ['id', 'name', 'code', 'category', 'icon']


class RoomTypeAmenitySerializer(serializers.ModelSerializer):
    """Serializer for assigning amenities to room types."""
    amenity_name = serializers.CharField(source='amenity.name', read_only=True)
    amenity_category = serializers.CharField(source='amenity.category', read_only=True)
    
    class Meta:
        model = RoomTypeAmenity
        fields = ['id', 'room_type', 'amenity', 'amenity_name', 'amenity_category']
        read_only_fields = ['id']
    
    def validate(self, data):
        """Check if amenity is already assigned to room type."""
        room_type = data.get('room_type')
        amenity = data.get('amenity')
        
        if room_type and amenity:
            instance = self.instance
            qs = RoomTypeAmenity.objects.filter(room_type=room_type, amenity=amenity)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "This amenity is already assigned to this room type."
                )
        
        return data


class RoomTypeSerializer(serializers.ModelSerializer):
    amenities = RoomAmenityListSerializer(many=True, read_only=True, source='amenities.all')
    amenity_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=RoomAmenity.objects.all(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = RoomType
        fields = [
            'id', 'name', 'code', 'description', 'base_rate',
            'max_occupancy', 'max_adults', 'max_children',
            'bed_type', 'amenities', 'amenity_ids'
        ]
        read_only_fields = ['id']
    
    def validate_code(self, value):
        """Validate room type code uniqueness."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Room type code must be at least 2 characters.")
        
        value = value.strip().upper()
        
        instance = self.instance
        if instance:
            if RoomType.objects.exclude(pk=instance.pk).filter(code=value).exists():
                raise serializers.ValidationError("A room type with this code already exists.")
        else:
            if RoomType.objects.filter(code=value).exists():
                raise serializers.ValidationError("A room type with this code already exists.")
        
        return value
    
    def validate_name(self, value):
        """Validate room type name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Room type name must be at least 2 characters.")
        return value.strip()
    
    def validate_base_rate(self, value):
        """Validate base rate."""
        if value < 0:
            raise serializers.ValidationError("Base rate cannot be negative.")
        return value
    
    def validate_max_occupancy(self, value):
        """Validate max occupancy."""
        if value < 1 or value > 20:
            raise serializers.ValidationError("Max occupancy must be between 1 and 20.")
        return value
    
    def create(self, validated_data):
        """Create room type with amenities."""
        amenity_ids = validated_data.pop('amenity_ids', [])
        room_type = RoomType.objects.create(**validated_data)
        
        # Assign amenities
        for amenity in amenity_ids:
            RoomTypeAmenity.objects.create(room_type=room_type, amenity=amenity)
        
        return room_type
    
    def update(self, instance, validated_data):
        """Update room type with amenities."""
        amenity_ids = validated_data.pop('amenity_ids', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update amenities if provided
        if amenity_ids is not None:
            # Remove existing amenities
            instance.amenities.all().delete()
            # Add new amenities
            for amenity in amenity_ids:
                RoomTypeAmenity.objects.create(room_type=instance, amenity=amenity)
        
        return instance


class RoomSerializer(serializers.ModelSerializer):
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    floor_name = serializers.CharField(source='floor.name', read_only=True)
    building_name = serializers.CharField(source='floor.building.name', read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'hotel', 'room_number', 'room_type', 'room_type_name',
            'floor', 'floor_name', 'building', 'building_name',
            'status', 'fo_status', 'is_smoking', 'is_accessible',
            'is_active', 'notes', 'name', 'description'
        ]
        read_only_fields = ['room_type_name', 'floor_name', 'building_name']


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
