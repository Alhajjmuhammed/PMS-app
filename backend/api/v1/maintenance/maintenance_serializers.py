"""
Serializers for Maintenance Module
"""
from rest_framework import serializers
from apps.maintenance.models import MaintenanceRequest, Asset, MaintenanceLog
from django.utils import timezone


class MaintenanceLogSerializer(serializers.ModelSerializer):
    """Serializer for maintenance logs."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = MaintenanceLog
        fields = [
            'id', 'request', 'action', 'notes', 'user', 'user_name',
            'timestamp'
        ]
        read_only_fields = ['id', 'user', 'timestamp']


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """Serializer for maintenance requests."""
    room_number = serializers.CharField(source='room.number', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    logs = MaintenanceLogSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'request_number', 'property', 'room', 'room_number',
            'location', 'request_type', 'priority', 'status', 'title',
            'description', 'assigned_to', 'assigned_to_name', 'assigned_at',
            'started_at', 'completed_at', 'resolution_notes', 'parts_cost',
            'labor_hours', 'total_cost', 'duration_hours', 'is_overdue',
            'reported_by', 'reported_by_name', 'created_at', 'updated_at',
            'logs'
        ]
        read_only_fields = ['id', 'request_number', 'reported_by', 'created_at', 'updated_at']
    
    def get_total_cost(self, obj):
        """Calculate total cost (parts + labor assuming $50/hour)."""
        labor_cost = float(obj.labor_hours) * 50
        return float(obj.parts_cost) + labor_cost
    
    def get_duration_hours(self, obj):
        """Calculate duration in hours."""
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return round(duration.total_seconds() / 3600, 2)
        return None
    
    def get_is_overdue(self, obj):
        """Check if request is overdue (pending/assigned > 24h for HIGH, > 1h for EMERGENCY)."""
        if obj.status in ['COMPLETED', 'CANCELLED']:
            return False
        
        now = timezone.now()
        created = obj.created_at
        
        if obj.priority == 'EMERGENCY':
            return (now - created).total_seconds() > 3600  # 1 hour
        elif obj.priority == 'HIGH':
            return (now - created).total_seconds() > 86400  # 24 hours
        
        return False
    
    def validate(self, data):
        """Validate maintenance request data."""
        # Validate dates
        if data.get('completed_at') and data.get('started_at'):
            if data['completed_at'] < data['started_at']:
                raise serializers.ValidationError(
                    "Completed time cannot be before started time"
                )
        
        # If status is ASSIGNED, assigned_to is required
        if data.get('status') == 'ASSIGNED' and not data.get('assigned_to'):
            raise serializers.ValidationError(
                "assigned_to is required when status is ASSIGNED"
            )
        
        # If status is COMPLETED, resolution_notes and completed_at are required
        if data.get('status') == 'COMPLETED':
            if not data.get('resolution_notes'):
                raise serializers.ValidationError(
                    "resolution_notes is required when marking as completed"
                )
            if not data.get('completed_at'):
                data['completed_at'] = timezone.now()
        
        return data


class AssetSerializer(serializers.ModelSerializer):
    """Serializer for assets."""
    room_number = serializers.CharField(source='room.number', read_only=True)
    warranty_expired = serializers.SerializerMethodField()
    maintenance_due = serializers.SerializerMethodField()
    depreciation_value = serializers.SerializerMethodField()
    maintenance_history_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'property', 'name', 'code', 'category', 'location',
            'room', 'room_number', 'brand', 'model', 'serial_number',
            'purchase_date', 'warranty_expiry', 'warranty_expired',
            'purchase_cost', 'current_value', 'depreciation_value',
            'last_maintenance', 'next_maintenance', 'maintenance_interval_days',
            'maintenance_due', 'maintenance_history_count', 'is_active', 'notes'
        ]
        read_only_fields = ['id']
    
    def get_warranty_expired(self, obj):
        """Check if warranty has expired."""
        if obj.warranty_expiry:
            from datetime import date
            return date.today() > obj.warranty_expiry
        return None
    
    def get_maintenance_due(self, obj):
        """Check if maintenance is due."""
        if obj.next_maintenance:
            from datetime import date
            return date.today() >= obj.next_maintenance
        return False
    
    def get_depreciation_value(self, obj):
        """Calculate depreciation."""
        return float(obj.purchase_cost) - float(obj.current_value)
    
    def get_maintenance_history_count(self, obj):
        """Count maintenance requests for this asset's room."""
        if obj.room:
            return obj.room.maintenance_requests.count()
        return 0
    
    def validate_code(self, value):
        """Ensure asset code is unique."""
        if self.instance:
            # For updates, exclude current instance
            if Asset.objects.exclude(id=self.instance.id).filter(code=value).exists():
                raise serializers.ValidationError("Asset code must be unique")
        else:
            # For creates
            if Asset.objects.filter(code=value).exists():
                raise serializers.ValidationError("Asset code must be unique")
        return value
    
    def validate(self, data):
        """Validate asset data."""
        # Validate dates
        if data.get('warranty_expiry') and data.get('purchase_date'):
            if data['warranty_expiry'] < data['purchase_date']:
                raise serializers.ValidationError(
                    "Warranty expiry cannot be before purchase date"
                )
        
        # Current value cannot exceed purchase cost
        if data.get('current_value') and data.get('purchase_cost'):
            if data['current_value'] > data['purchase_cost']:
                raise serializers.ValidationError(
                    "Current value cannot exceed purchase cost"
                )
        
        return data


class MaintenanceDashboardSerializer(serializers.Serializer):
    """Serializer for maintenance dashboard statistics."""
    pending_requests = serializers.IntegerField()
    assigned_requests = serializers.IntegerField()
    in_progress_requests = serializers.IntegerField()
    completed_today = serializers.IntegerField()
    emergency_requests = serializers.IntegerField()
    overdue_requests = serializers.IntegerField()
    total_assets = serializers.IntegerField()
    assets_due_maintenance = serializers.IntegerField()
    assets_under_warranty = serializers.IntegerField()
    avg_resolution_hours = serializers.FloatField()


class MaintenanceRequestAssignSerializer(serializers.Serializer):
    """Serializer for assigning maintenance requests."""
    requests = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    assigned_to = serializers.IntegerField()
    
    def validate_assigned_to(self, value):
        """Validate assigned_to user exists."""
        from apps.accounts.models import User
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found")
        return value
