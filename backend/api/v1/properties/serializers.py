from rest_framework import serializers
from apps.properties.models import Property, Building, Floor, SystemSetting


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ['id', 'name', 'floor_number', 'building']


class BuildingSerializer(serializers.ModelSerializer):
    floors = FloorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Building
        fields = ['id', 'name', 'code', 'floors']


class PropertySerializer(serializers.ModelSerializer):
    buildings = BuildingSerializer(many=True, read_only=True)
    total_rooms = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'name', 'code', 'property_type', 'address', 'city',
            'state', 'country', 'postal_code', 'phone', 'email',
            'website', 'check_in_time', 'check_out_time', 'currency',
            'timezone', 'is_active', 'buildings', 'total_rooms'
        ]


class SystemSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = [
            'id', 'property', 'language', 'timezone', 'currency',
            'date_format', 'time_format', 'theme',
            'email_notifications', 'push_notifications', 'sms_notifications',
            'tax_rate', 'service_charge_rate',
            'check_in_time', 'check_out_time',
            'extra_settings', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']
