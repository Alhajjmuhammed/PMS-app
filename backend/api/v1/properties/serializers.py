from rest_framework import serializers
from apps.properties.models import Property, Building, Floor, SystemSetting, Department, PropertyAmenity, TaxConfiguration


class FloorSerializer(serializers.ModelSerializer):
    """Serializer for Floor model."""
    building_name = serializers.CharField(source='building.name', read_only=True)
    
    class Meta:
        model = Floor
        fields = ['id', 'building', 'building_name', 'number', 'name', 'description']
        read_only_fields = ['id']
    
    def validate_number(self, value):
        """Validate floor number."""
        if value < -10 or value > 200:
            raise serializers.ValidationError("Floor number must be between -10 and 200.")
        return value
    
    def validate(self, data):
        """Check uniqueness of floor number within building."""
        building = data.get('building')
        number = data.get('number')
        
        if building and number is not None:
            instance = self.instance
            qs = Floor.objects.filter(building=building, number=number)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'number': f"Floor {number} already exists in this building."
                })
        
        return data


class BuildingSerializer(serializers.ModelSerializer):
    """Serializer for Building model with nested floors."""
    building_floors = FloorSerializer(many=True, read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    floor_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Building
        fields = [
            'id', 'property', 'property_name', 'name', 'code', 
            'floors', 'description', 'is_active', 'building_floors', 'floor_count'
        ]
        read_only_fields = ['id']
    
    def get_floor_count(self, obj):
        """Return actual count of floor records."""
        return obj.building_floors.count()
    
    def validate_code(self, value):
        """Validate building code."""
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("Building code is required.")
        return value.strip().upper()
    
    def validate_name(self, value):
        """Validate building name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Building name must be at least 2 characters.")
        return value.strip()
    
    def validate_floors(self, value):
        """Validate number of floors."""
        if value < 1 or value > 200:
            raise serializers.ValidationError("Number of floors must be between 1 and 200.")
        return value
    
    def validate(self, data):
        """Check uniqueness of building code within property."""
        property_obj = data.get('property')
        code = data.get('code')
        
        if property_obj and code:
            instance = self.instance
            qs = Building.objects.filter(property=property_obj, code=code)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'code': f"Building with code '{code}' already exists in this property."
                })
        
        return data


class BuildingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for building list view."""
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = Building
        fields = ['id', 'property', 'property_name', 'name', 'code', 'floors', 'is_active']


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


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    property_name = serializers.CharField(source='property.name', read_only=True)
    manager_name = serializers.SerializerMethodField()
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'property', 'property_name', 'name', 'code',
            'description', 'manager', 'manager_name', 'staff_count', 'is_active'
        ]
        read_only_fields = ['id']
    
    def get_manager_name(self, obj):
        return obj.manager.get_full_name() if obj.manager else None
    
    def get_staff_count(self, obj):
        return obj.users.count()
    
    def validate(self, data):
        """Check uniqueness of department code within property."""
        property_obj = data.get('property')
        code = data.get('code')
        
        if property_obj and code:
            instance = self.instance
            qs = Department.objects.filter(property=property_obj, code=code)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'code': f"Department with code '{code}' already exists in this property."
                })
        
        return data


class PropertyAmenitySerializer(serializers.ModelSerializer):
    """Serializer for PropertyAmenity model."""
    property_name = serializers.CharField(source='property.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = PropertyAmenity
        fields = [
            'id', 'property', 'property_name', 'name', 'category',
            'category_display', 'description', 'icon',
            'is_chargeable', 'price'
        ]
        read_only_fields = ['id']
    
    def validate_price(self, value):
        """Validate price is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value


class TaxConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for TaxConfiguration model."""
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = TaxConfiguration
        fields = [
            'id', 'property', 'property_name', 'name', 'code', 'rate',
            'is_percentage', 'applies_to_room', 'applies_to_services', 'is_active'
        ]
        read_only_fields = ['id']
    
    def validate_rate(self, value):
        """Validate tax rate."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Tax rate must be between 0 and 100.")
        return value
    
    def validate(self, data):
        """Check uniqueness of tax code within property."""
        property_obj = data.get('property')
        code = data.get('code')
        
        if property_obj and code:
            instance = self.instance
            qs = TaxConfiguration.objects.filter(property=property_obj, code=code)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'code': f"Tax with code '{code}' already exists in this property."
                })
        
        return data

