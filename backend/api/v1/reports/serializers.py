from rest_framework import serializers
from apps.reports.models import DailyStatistics, MonthlyStatistics, NightAudit, AuditLog


class DailyStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for daily statistics."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = DailyStatistics
        fields = [
            'id', 'property', 'property_name', 'date',
            'total_rooms', 'rooms_sold', 'rooms_ooo', 'available_rooms',
            'complimentary_rooms', 'house_use_rooms', 'occupancy_percent',
            'room_revenue', 'fb_revenue', 'other_revenue', 'total_revenue',
            'adr', 'revpar', 'arrivals', 'departures', 'in_house',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    
    date = serializers.DateField()
    total_rooms = serializers.IntegerField()
    occupied = serializers.IntegerField(required=False)
    rooms_sold = serializers.IntegerField(required=False)
    occupancy_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    arrivals = serializers.IntegerField()
    departures = serializers.IntegerField()
    in_house = serializers.IntegerField(required=False)
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    room_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    fb_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    adr = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    revpar = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class OccupancyDataSerializer(serializers.Serializer):
    """Serializer for occupancy report data."""
    
    date = serializers.DateField()
    occupancy = serializers.DecimalField(max_digits=5, decimal_places=2)
    adr = serializers.DecimalField(max_digits=10, decimal_places=2)
    revpar = serializers.DecimalField(max_digits=10, decimal_places=2)
    rooms_sold = serializers.IntegerField()


# ============= Monthly Statistics Serializers =============

class MonthlyStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for monthly statistics."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    month_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthlyStatistics
        fields = [
            'id', 'property', 'property_name', 'year', 'month', 'month_name',
            'avg_occupancy', 'avg_adr', 'avg_revpar', 'total_room_nights',
            'total_revenue', 'room_revenue', 'fb_revenue', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_month_name(self, obj):
        """Get month name."""
        import calendar
        return calendar.month_name[obj.month]


class MonthlyStatisticsCreateSerializer(serializers.ModelSerializer):
    """Create serializer for monthly statistics."""
    
    class Meta:
        model = MonthlyStatistics
        fields = [
            'property', 'year', 'month', 'avg_occupancy', 'avg_adr',
            'avg_revpar', 'total_room_nights', 'total_revenue',
            'room_revenue', 'fb_revenue'
        ]
    
    def validate_month(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError("Month must be between 1 and 12")
        return value
    
    def validate(self, data):
        # Check for duplicate
        if MonthlyStatistics.objects.filter(
            property=data['property'],
            year=data['year'],
            month=data['month']
        ).exists():
            raise serializers.ValidationError(
                "Statistics for this month already exist"
            )
        return data


# ============= Night Audit Serializers =============

class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs."""
    
    class Meta:
        model = AuditLog
        fields = ['id', 'step', 'message', 'is_error', 'created_at']
        read_only_fields = ['id', 'created_at']


class NightAuditSerializer(serializers.ModelSerializer):
    """Serializer for night audits."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    completed_by_name = serializers.CharField(source='completed_by.get_full_name', read_only=True)
    logs = AuditLogSerializer(many=True, read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = NightAudit
        fields = [
            'id', 'property', 'property_name', 'business_date', 'status',
            'no_shows_processed', 'room_rates_posted', 'folios_settled',
            'departures_checked', 'room_revenue', 'tax_amount', 'fb_revenue',
            'other_revenue', 'total_revenue', 'payments_collected',
            'rooms_sold', 'arrivals_count', 'departures_count',
            'started_at', 'completed_at', 'completed_by', 'completed_by_name',
            'notes', 'logs', 'duration_minutes'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']
    
    def get_duration_minutes(self, obj):
        """Calculate audit duration in minutes."""
        if obj.started_at and obj.completed_at:
            delta = obj.completed_at - obj.started_at
            return int(delta.total_seconds() / 60)
        return None


class NightAuditCreateSerializer(serializers.ModelSerializer):
    """Create serializer for night audit."""
    
    class Meta:
        model = NightAudit
        fields = ['property', 'business_date', 'notes']
    
    def validate(self, data):
        # Check for duplicate audit for same business date
        if NightAudit.objects.filter(
            property=data['property'],
            business_date=data['business_date']
        ).exclude(status=NightAudit.Status.ROLLED_BACK).exists():
            raise serializers.ValidationError(
                "Night audit for this business date already exists"
            )
        return data


class NightAuditUpdateSerializer(serializers.ModelSerializer):
    """Update serializer for night audit."""
    
    class Meta:
        model = NightAudit
        fields = [
            'status', 'no_shows_processed', 'room_rates_posted',
            'folios_settled', 'departures_checked', 'room_revenue',
            'tax_amount', 'fb_revenue', 'other_revenue', 'total_revenue',
            'payments_collected', 'rooms_sold', 'arrivals_count',
            'departures_count', 'notes'
        ]


class StartNightAuditSerializer(serializers.Serializer):
    """Serializer for starting night audit."""
    
    auto_process = serializers.BooleanField(default=True, required=False)
    
    class Meta:
        fields = ['auto_process']


class RevenueDataSerializer(serializers.Serializer):
    """Serializer for revenue report data."""
    
    date = serializers.DateField()
    room_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    fb_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    other_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
