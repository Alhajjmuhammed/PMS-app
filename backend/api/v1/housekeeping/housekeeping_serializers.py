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
    inspected_by_name = serializers.CharField(source='inspected_by.get_full_name', read_only=True)
    
    class Meta:
        model = HousekeepingTask
        fields = [
            'id', 'room', 'room_number', 'task_type', 'priority', 'status',
            'assigned_to', 'assigned_to_name', 'assigned_at', 'scheduled_date',
            'scheduled_time', 'started_at', 'completed_at', 'inspected_by',
            'inspected_by_name', 'inspected_at', 'inspection_notes',
            'inspection_passed', 'notes', 'special_instructions', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
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
    
    room_number = serializers.CharField(source='room.number', read_only=True)
    inspector_name = serializers.CharField(source='inspector.get_full_name', read_only=True)
    
    class Meta:
        model = RoomInspection
        fields = [
            'id', 'room', 'room_number', 'inspector', 'inspector_name',
            'inspection_date', 'cleanliness_score', 'bed_making_score',
            'bathroom_score', 'amenities_score', 'overall_score',
            'passed', 'notes'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate room inspection."""
        rating = data.get('cleanliness_rating')
        if rating and (rating < 1 or rating > 5):
            raise serializers.ValidationError("Cleanliness rating must be between 1 and 5.")
        
        return data


class LinenInventorySerializer(serializers.ModelSerializer):
    """Serializer for linen inventory."""
    
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    quantity_available = serializers.SerializerMethodField()
    
    class Meta:
        model = LinenInventory
        fields = [
            'id', 'hotel', 'hotel_name', 'linen_type', 'quantity_total',
            'quantity_in_use', 'quantity_in_laundry', 'quantity_damaged',
            'quantity_available', 'reorder_level', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']
    
    def get_quantity_available(self, obj):
        return obj.quantity_total - obj.quantity_in_use - obj.quantity_in_laundry - obj.quantity_damaged
    
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
    
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    needs_reorder = serializers.SerializerMethodField()
    
    class Meta:
        model = AmenityInventory
        fields = [
            'id', 'hotel', 'hotel_name', 'name', 'code', 'category',
            'quantity', 'reorder_level', 'unit_cost', 'needs_reorder'
        ]
        read_only_fields = ['id']
    
    def get_needs_reorder(self, obj):
        return obj.quantity <= obj.reorder_level
    
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
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = HousekeepingSchedule
        fields = [
            'id', 'user', 'user_name', 'date', 'shift_start',
            'shift_end', 'assigned_floor', 'notes'
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
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'property', 'property_name', 'amenity_inventory',
            'linen_inventory', 'movement_type', 'quantity', 'balance_after',
            'reference', 'reason', 'notes', 'from_location', 'to_location',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'balance_after']
    
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
