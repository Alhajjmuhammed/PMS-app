from rest_framework import serializers
from apps.maintenance.models import MaintenanceRequest, MaintenanceLog


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    category = serializers.CharField(source='request_type', read_only=True)  # Alias for backward compatibility
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'request_number', 'room', 'room_number', 'location',
            'request_type', 'category', 'priority', 'status', 'title', 'description',
            'assigned_to', 'assigned_to_name', 'reported_by', 'reported_by_name',
            'assigned_at', 'started_at', 'completed_at',
            'parts_cost', 'labor_hours', 'resolution_notes',
            'created_at'
        ]


class MaintenanceRequestCreateSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='request_type', write_only=True, required=False)  # Alias for backward compatibility
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'room', 'location', 'request_type', 'category', 'priority',
            'title', 'description'
        ]


class MaintenanceLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = MaintenanceLog
        fields = ['id', 'request', 'action', 'notes', 'performed_by', 'performed_by_name', 'created_at']


class RequestUpdateSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    actual_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
