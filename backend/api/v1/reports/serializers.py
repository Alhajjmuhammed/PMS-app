from rest_framework import serializers
from apps.reports.models import DailyStatistics


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


class RevenueDataSerializer(serializers.Serializer):
    """Serializer for revenue report data."""
    
    date = serializers.DateField()
    room_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    fb_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    other_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
