"""
Serializers for Reports Module
"""
from rest_framework import serializers
from apps.reports.models import (
    DailyStatistics, MonthlyStatistics, ReportTemplate, NightAudit, AuditLog
)


class DailyStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for daily statistics."""
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = DailyStatistics
        fields = [
            'id', 'property', 'property_name', 'date', 'total_rooms',
            'occupied_rooms', 'available_rooms', 'out_of_order_rooms',
            'reserved_rooms', 'complimentary_rooms', 'occupancy_percentage',
            'room_revenue', 'food_revenue', 'other_revenue', 'total_revenue',
            'adr', 'revpar', 'total_guests', 'arrivals', 'departures',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MonthlyStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for monthly statistics."""
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = MonthlyStatistics
        fields = [
            'id', 'property', 'property_name', 'year', 'month',
            'avg_occupancy', 'avg_adr', 'avg_revpar', 'total_rooms_sold',
            'total_room_revenue', 'total_food_revenue', 'total_other_revenue',
            'total_revenue', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for report templates."""
    property_name = serializers.CharField(source='property.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'property', 'property_name', 'name', 'report_type',
            'report_type_display', 'description', 'config', 'is_scheduled',
            'schedule_frequency', 'schedule_time', 'created_by',
            'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def validate_config(self, value):
        """Validate config is a valid JSON object."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Config must be a JSON object")
        return value


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit log entries."""
    
    class Meta:
        model = AuditLog
        fields = ['id', 'night_audit', 'action', 'details', 'success', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class NightAuditSerializer(serializers.ModelSerializer):
    """Serializer for night audit."""
    property_name = serializers.CharField(source='property.name', read_only=True)
    completed_by_name = serializers.CharField(
        source='completed_by.get_full_name', read_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    logs = AuditLogSerializer(many=True, read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = NightAudit
        fields = [
            'id', 'property', 'property_name', 'audit_date', 'status',
            'status_display', 'rooms_posted', 'reservations_updated',
            'folios_closed', 'no_shows_processed', 'room_revenue',
            'tax_amount', 'total_revenue', 'payment_received',
            'account_receivable', 'cash_variance', 'check_ins_today',
            'check_outs_today', 'in_house_guests', 'started_at',
            'completed_at', 'duration_minutes', 'completed_by',
            'completed_by_name', 'notes', 'logs'
        ]
        read_only_fields = ['id', 'completed_at', 'completed_by']
    
    def get_duration_minutes(self, obj):
        """Calculate audit duration in minutes."""
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return round(duration.total_seconds() / 60, 2)
        return None


class NightAuditSummarySerializer(serializers.Serializer):
    """Serializer for night audit summary/dashboard."""
    last_audit_date = serializers.DateField(allow_null=True)
    last_audit_status = serializers.CharField()
    pending_audits = serializers.IntegerField()
    completed_this_month = serializers.IntegerField()
    avg_duration_minutes = serializers.FloatField()
    total_revenue_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)


class GenerateReportSerializer(serializers.Serializer):
    """Serializer for report generation requests."""
    report_type = serializers.ChoiceField(choices=ReportTemplate.ReportType.choices)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    filters = serializers.JSONField(required=False, default=dict)
    
    def validate(self, data):
        """Validate report request."""
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        return data
