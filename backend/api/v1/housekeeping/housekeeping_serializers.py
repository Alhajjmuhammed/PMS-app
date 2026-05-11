"""
Comprehensive Serializers for Housekeeping Module
"""
from rest_framework import serializers
from apps.housekeeping.models import (
    HousekeepingTask,
    RoomInspection,
    LinenInventory,
    AmenityInventory,
    HousekeepingSchedule,
    StockMovement
)


class HousekeepingTaskSerializer(serializers.ModelSerializer):
    """Serializer for housekeeping tasks."""
    
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    inspected_by_name = serializers.CharField(source='inspected_by.get_full_name', read_only=True)
    
    class Meta:
        ref_name = 'HousekeepingTaskSerializerExtended'
        model = HousekeepingTask
        fields = [
            'id',
            'room',
            'task_type',
            'priority',
            'status',
            'assigned_to',
            'assigned_at',
            'scheduled_date',
            'scheduled_time',
            'started_at',
            'completed_at',
            'inspected_by',
            'inspected_at',
            'inspection_notes',
            'inspection_passed',
            'notes',
            'special_instructions',
            'created_by',
            'created_at',
            'updated_at',
            'room_number', 'assigned_to_name', 'created_by_name', 'inspected_by_name'
        
        ]
        
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate housekeeping task."""
        started = data.get('started_at')
        completed = data.get('completed_at')
        
        if started and completed and completed < started:
            raise serializers.ValidationError("Completed time must be after started time.")
        
        return data


class RoomInspectionSerializer(serializers.ModelSerializer):
    """Serializer for room inspections."""
    
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    inspector_name = serializers.CharField(source='inspector.get_full_name', read_only=True)
    
    class Meta:
        ref_name = 'RoomInspectionSerializerExtended'
        model = RoomInspection
        fields = [
            'id',
            'room',
            'inspector',
            'inspection_date',
            'cleanliness_score',
            'bed_making_score',
            'bathroom_score',
            'amenities_score',
            'overall_score',
            'passed',
            'notes',
            'room_number', 'inspector_name'
        
        ]
        
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate room inspection."""
        return data


class LinenInventorySerializer(serializers.ModelSerializer):
    """Serializer for linen inventory."""
    
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    quantity_available = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'LinenInventorySerializerExtended'
        model = LinenInventory
        fields = [
            'id',
            'hotel',
            'linen_type',
            'quantity_total',
            'quantity_in_use',
            'quantity_in_laundry',
            'quantity_damaged',
            'reorder_level',
            'updated_at',
            'hotel_name', 'quantity_available'
        
        ]
        
        read_only_fields = ['id', 'updated_at']
    
    def get_quantity_available(self, obj):
        return obj.quantity_total - obj.quantity_in_use - obj.quantity_in_laundry - obj.quantity_damaged
    
    def validate(self, data):
        """Validate linen inventory."""
        return data


class AmenityInventorySerializer(serializers.ModelSerializer):
    """Serializer for amenity inventory."""
    
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    needs_reorder = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'AmenityInventorySerializerExtended'
        model = AmenityInventory
        fields = [
            'id',
            'hotel',
            'name',
            'code',
            'category',
            'quantity',
            'reorder_level',
            'unit_cost',
            'hotel_name', 'needs_reorder'
        
        ]
        
        read_only_fields = ['id']
    
    def get_needs_reorder(self, obj):
        return obj.quantity <= obj.reorder_level
    
    def validate(self, data):
        """Validate amenity inventory."""
        return data


class HousekeepingScheduleSerializer(serializers.ModelSerializer):
    """Serializer for housekeeping schedules."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = HousekeepingSchedule
        fields = [
            'id',
            'user',
            'date',
            'shift_start',
            'shift_end',
            'assigned_floor',
            'notes',
            'user_name'
        
        ]
        
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate housekeeping schedule."""
        start = data.get('shift_start')
        end = data.get('shift_end')
        
        if start and end and end <= start:
            raise serializers.ValidationError("Shift end must be after shift start.")
        
        return data


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for stock movements."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    amenity_name = serializers.CharField(source='amenity_inventory.name', read_only=True, default=None)
    linen_type_display = serializers.CharField(source='linen_inventory.linen_type', read_only=True, default=None)
    
    class Meta:
        ref_name = 'StockMovementSerializerExtended'
        model = StockMovement
        fields = [
            'id',
            'property',
            'amenity_inventory',
            'linen_inventory',
            'movement_type',
            'quantity',
            'balance_after',
            'reference',
            'reason',
            'notes',
            'from_location',
            'to_location',
            'created_by',
            'created_at',
            'property_name', 'created_by_name',
            'amenity_name', 'linen_type_display',
        ]
        
        read_only_fields = ['id', 'property', 'created_by', 'created_at', 'balance_after']
    
    def validate(self, data):
        """Validate stock movement."""
        quantity = data.get('quantity', 0)
        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        
        movement_type = data.get('movement_type')
        from_loc = data.get('from_location')
        to_loc = data.get('to_location')
        
        if movement_type == 'TRANSFER' and not (from_loc and to_loc):
            raise serializers.ValidationError("Transfer requires both from and to locations.")
        
        if from_loc and to_loc and from_loc == to_loc:
            raise serializers.ValidationError("From and to locations must be different.")
        
        return data


class HousekeepingDashboardSerializer(serializers.Serializer):
    """Serializer for housekeeping dashboard statistics."""
    
    pending_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    completed_today = serializers.IntegerField()
    inspections_today = serializers.IntegerField()
    failed_inspections = serializers.IntegerField()
    clean_rooms = serializers.IntegerField()
    dirty_rooms = serializers.IntegerField()
    inspecting_rooms = serializers.IntegerField()
    out_of_order_rooms = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()


class TaskAssignmentSerializer(serializers.Serializer):
    """Serializer for bulk task assignment."""
    
    rooms = serializers.ListField(
        child=serializers.IntegerField()
    )
    task_type = serializers.ChoiceField(choices=HousekeepingTask.TaskType.choices)
    assigned_to = serializers.IntegerField()
    scheduled_date = serializers.DateField()
    priority = serializers.ChoiceField(
        choices=HousekeepingTask.Priority.choices,
        default='MEDIUM'
    )
    description = serializers.CharField(required=False, allow_blank=True)
