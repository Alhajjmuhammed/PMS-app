from rest_framework import serializers
from apps.housekeeping.models import (
    HousekeepingTask, RoomInspection, AmenityInventory,
    LinenInventory, StockMovement
)


class HousekeepingTaskSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    room_type = serializers.CharField(source='room.room_type.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = HousekeepingTask
        fields = [
            'id', 'room', 'room_number', 'room_type', 'task_type', 'status',
            'priority', 'assigned_to', 'assigned_to_name',
            'scheduled_date', 'started_at', 'completed_at',
            'notes', 'special_instructions'
        ]


class TaskUpdateSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class RoomInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomInspection
        fields = [
            'id', 'task', 'inspected_by', 'inspection_time',
            'cleanliness_score', 'amenities_score', 'overall_score',
            'passed', 'comments'
        ]


# ============= Inventory Management Serializers =============

class AmenityInventorySerializer(serializers.ModelSerializer):
    """Amenity inventory read serializer."""
    property_name = serializers.CharField(source='hotel.name', read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = AmenityInventory
        fields = [
            'id', 'hotel', 'property_name', 'name', 'code', 'category',
            'quantity', 'reorder_level', 'unit_cost', 'is_low_stock'
        ]
        read_only_fields = ['id']
    
    def get_is_low_stock(self, obj):
        return obj.quantity <= obj.reorder_level


class AmenityInventoryCreateSerializer(serializers.ModelSerializer):
    """Amenity inventory write serializer."""
    
    class Meta:
        model = AmenityInventory
        fields = [
            'hotel', 'name', 'code', 'category', 'quantity',
            'reorder_level', 'unit_cost'
        ]
    
    def validate_code(self, value):
        """Ensure code is unique per property."""
        hotel = self.initial_data.get('hotel')
        if hotel:
            if self.instance:
                # Update - exclude self
                exists = AmenityInventory.objects.filter(
                    hotel_id=hotel, code=value
                ).exclude(id=self.instance.id).exists()
            else:
                # Create
                exists = AmenityInventory.objects.filter(
                    hotel_id=hotel, code=value
                ).exists()
            
            if exists:
                raise serializers.ValidationError(
                    f"Amenity with code '{value}' already exists for this property."
                )
        return value
    
    def validate(self, data):
        """Validate quantity and reorder level."""
        quantity = data.get('quantity', 0)
        reorder_level = data.get('reorder_level', 0)
        
        if quantity < 0:
            raise serializers.ValidationError({
                'quantity': 'Quantity cannot be negative.'
            })
        
        if reorder_level < 0:
            raise serializers.ValidationError({
                'reorder_level': 'Reorder level cannot be negative.'
            })
        
        return data


class LinenInventorySerializer(serializers.ModelSerializer):
    """Linen inventory read serializer."""
    property_name = serializers.CharField(source='hotel.name', read_only=True)
    linen_type_display = serializers.CharField(source='get_linen_type_display', read_only=True)
    quantity_available = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = LinenInventory
        fields = [
            'id', 'hotel', 'property_name', 'linen_type', 'linen_type_display',
            'quantity_total', 'quantity_in_use', 'quantity_in_laundry',
            'quantity_damaged', 'quantity_available', 'reorder_level',
            'is_low_stock', 'updated_at'
        ]
        read_only_fields = ['id', 'quantity_available', 'updated_at']
    
    def get_is_low_stock(self, obj):
        return obj.quantity_available <= obj.reorder_level


class LinenInventoryCreateSerializer(serializers.ModelSerializer):
    """Linen inventory write serializer."""
    
    class Meta:
        model = LinenInventory
        fields = [
            'hotel', 'linen_type', 'quantity_total', 'quantity_in_use',
            'quantity_in_laundry', 'quantity_damaged', 'reorder_level'
        ]
    
    def validate(self, data):
        """Validate linen quantities."""
        total = data.get('quantity_total', 0)
        in_use = data.get('quantity_in_use', 0)
        in_laundry = data.get('quantity_in_laundry', 0)
        damaged = data.get('quantity_damaged', 0)
        
        if total < 0:
            raise serializers.ValidationError({
                'quantity_total': 'Total quantity cannot be negative.'
            })
        
        if in_use < 0 or in_laundry < 0 or damaged < 0:
            raise serializers.ValidationError(
                'Individual quantities cannot be negative.'
            )
        
        # Ensure sum doesn't exceed total
        if (in_use + in_laundry + damaged) > total:
            raise serializers.ValidationError(
                'Sum of in_use, in_laundry, and damaged cannot exceed total quantity.'
            )
        
        return data


class StockMovementSerializer(serializers.ModelSerializer):
    """Stock movement read serializer."""
    property_name = serializers.CharField(source='property.name', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    # Item details
    item_name = serializers.SerializerMethodField()
    item_type = serializers.SerializerMethodField()
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'property', 'property_name', 'amenity_inventory', 'linen_inventory',
            'item_name', 'item_type', 'movement_type', 'movement_type_display',
            'quantity', 'balance_after', 'reference', 'reason', 'notes',
            'from_location', 'to_location', 'created_by', 'created_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'balance_after', 'created_at']
    
    def get_item_name(self, obj):
        if obj.amenity_inventory:
            return obj.amenity_inventory.name
        elif obj.linen_inventory:
            return obj.linen_inventory.get_linen_type_display()
        return None
    
    def get_item_type(self, obj):
        if obj.amenity_inventory:
            return 'amenity'
        elif obj.linen_inventory:
            return 'linen'
        return None


class StockMovementCreateSerializer(serializers.ModelSerializer):
    """Stock movement write serializer."""
    
    class Meta:
        model = StockMovement
        fields = [
            'property', 'amenity_inventory', 'linen_inventory', 'movement_type',
            'quantity', 'reference', 'reason', 'notes',
            'from_location', 'to_location'
        ]
    
    def validate(self, data):
        """Validate stock movement."""
        amenity = data.get('amenity_inventory')
        linen = data.get('linen_inventory')
        
        # Must have either amenity or linen, but not both
        if not amenity and not linen:
            raise serializers.ValidationError(
                'Either amenity_inventory or linen_inventory must be provided.'
            )
        
        if amenity and linen:
            raise serializers.ValidationError(
                'Cannot specify both amenity_inventory and linen_inventory.'
            )
        
        # Validate quantity based on movement type
        movement_type = data.get('movement_type')
        quantity = data.get('quantity', 0)
        
        if movement_type in ['ISSUE', 'DAMAGE', 'TRANSFER'] and quantity < 0:
            raise serializers.ValidationError({
                'quantity': 'Quantity for issues, damage, and transfers must be positive.'
            })
        
        if movement_type == 'RECEIVE' and quantity < 0:
            raise serializers.ValidationError({
                'quantity': 'Quantity for receives must be positive.'
            })
        
        # Check if enough stock for issues/damage
        if movement_type in ['ISSUE', 'DAMAGE']:
            if amenity:
                if amenity.quantity < quantity:
                    raise serializers.ValidationError(
                        f'Insufficient stock. Available: {amenity.quantity}'
                    )
            elif linen:
                available = linen.quantity_available
                if available < quantity:
                    raise serializers.ValidationError(
                        f'Insufficient stock. Available: {available}'
                    )
        
        return data
    
    def create(self, validated_data):
        """Create stock movement and update inventory."""
        amenity = validated_data.get('amenity_inventory')
        linen = validated_data.get('linen_inventory')
        movement_type = validated_data['movement_type']
        quantity = validated_data['quantity']
        
        # Calculate new balance
        if amenity:
            current_qty = amenity.quantity
            if movement_type in ['RECEIVE', 'RETURN']:
                new_qty = current_qty + quantity
            elif movement_type in ['ISSUE', 'DAMAGE']:
                new_qty = current_qty - quantity
            else:  # ADJUST, TRANSFER
                new_qty = current_qty + quantity  # quantity can be negative
            
            validated_data['balance_after'] = new_qty
            
            # Update amenity inventory
            amenity.quantity = new_qty
            amenity.save()
        
        elif linen:
            current_qty = linen.quantity_total
            if movement_type in ['RECEIVE', 'RETURN']:
                new_qty = current_qty + quantity
                linen.quantity_total = new_qty
            elif movement_type == 'ISSUE':
                linen.quantity_in_use += quantity
                new_qty = linen.quantity_available
            elif movement_type == 'DAMAGE':
                linen.quantity_damaged += quantity
                new_qty = linen.quantity_available
            else:  # ADJUST, TRANSFER
                new_qty = current_qty + quantity
                linen.quantity_total = new_qty
            
            validated_data['balance_after'] = new_qty
            linen.save()
        
        # Set created_by from request context
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)
