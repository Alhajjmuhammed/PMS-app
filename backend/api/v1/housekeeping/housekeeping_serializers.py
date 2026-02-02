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
    
    room_number = serializers.CharField(source='room.number', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    completed_by_name = serializers.CharField(source='completed_by.get_full_name', read_only=True)
    
    class Meta:
        model = HousekeepingTask
        fields = [
            'id', 'room', 'room_number', 'task_type', 'task_type_display',
            'priority', 'status', 'description', 'assigned_to', 'assigned_to_name',
            'scheduled_date', 'started_at', 'completed_at', 'duration_minutes',
            'notes', 'inspection_required', 'inspected', 'created_by',
            'created_by_name', 'completed_by', 'completed_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'completed_by']
    
    def validate(self, data):
        """Validate housekeeping task."""
        started = data.get('started_at')
        completed = data.get('completed_at')
        
        if started and completed and completed < started:
            raise serializers.ValidationError("Completed time must be after started time.")
        
        return data


class RoomInspectionSerializer(serializers.ModelSerializer):
    """Serializer for room inspections."""
    
    room_number = serializers.CharField(source='room.number', read_only=True)
    inspector_name = serializers.CharField(source='inspector.get_full_name', read_only=True)
    task_info = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomInspection
        fields = [
            'id', 'task', 'task_info', 'room', 'room_number', 'inspector',
            'inspector_name', 'inspection_date', 'cleanliness_rating',
            'maintenance_issues', 'missing_items', 'notes', 'passed',
            'requires_rework', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_task_info(self, obj):
        if obj.task:
            return {
                'id': obj.task.id,
                'task_type': obj.task.task_type,
                'completed_by': obj.task.completed_by.get_full_name() if obj.task.completed_by else None
            }
        return None
    
    def validate(self, data):
        """Validate room inspection."""
        rating = data.get('cleanliness_rating')
        if rating and (rating < 1 or rating > 5):
            raise serializers.ValidationError("Cleanliness rating must be between 1 and 5.")
        
        return data


class LinenInventorySerializer(serializers.ModelSerializer):
    """Serializer for linen inventory."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    in_use = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    
    class Meta:
        model = LinenInventory
        fields = [
            'id', 'property', 'property_name', 'item_name', 'item_type',
            'total_quantity', 'in_use', 'available', 'minimum_quantity',
            'unit_cost', 'last_counted_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_in_use(self, obj):
        return obj.in_use
    
    def get_available(self, obj):
        return obj.total_quantity - obj.in_use
    
    def validate(self, data):
        """Validate linen inventory."""
        total_qty = data.get('total_quantity', 0)
        min_qty = data.get('minimum_quantity', 0)
        
        if total_qty < 0:
            raise serializers.ValidationError("Total quantity cannot be negative.")
        
        if min_qty < 0:
            raise serializers.ValidationError("Minimum quantity cannot be negative.")
        
        return data


class AmenityInventorySerializer(serializers.ModelSerializer):
    """Serializer for amenity inventory."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    needs_reorder = serializers.SerializerMethodField()
    
    class Meta:
        model = AmenityInventory
        fields = [
            'id', 'property', 'property_name', 'item_name', 'item_type',
            'current_stock', 'minimum_stock', 'reorder_quantity',
            'unit_cost', 'supplier', 'last_restocked_at', 'needs_reorder',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_needs_reorder(self, obj):
        return obj.current_stock <= obj.minimum_stock
    
    def validate(self, data):
        """Validate amenity inventory."""
        current = data.get('current_stock', 0)
        minimum = data.get('minimum_stock', 0)
        
        if current < 0:
            raise serializers.ValidationError("Current stock cannot be negative.")
        
        if minimum < 0:
            raise serializers.ValidationError("Minimum stock cannot be negative.")
        
        return data


class HousekeepingScheduleSerializer(serializers.ModelSerializer):
    """Serializer for housekeeping schedules."""
    
    staff_name = serializers.CharField(source='staff.get_full_name', read_only=True)
    rooms_assigned = serializers.SerializerMethodField()
    
    class Meta:
        model = HousekeepingSchedule
        fields = [
            'id', 'staff', 'staff_name', 'shift_date', 'shift_start',
            'shift_end', 'shift_type', 'area_assignment', 'rooms_assigned',
            'notes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_rooms_assigned(self, obj):
        if obj.area_assignment:
            return obj.area_assignment.split(',')
        return []
    
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
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'property', 'property_name', 'item_type', 'item_name',
            'movement_type', 'quantity', 'from_location', 'to_location',
            'reason', 'notes', 'performed_by', 'performed_by_name',
            'movement_date', 'created_at'
        ]
        read_only_fields = ['id', 'performed_by', 'created_at']
    
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
