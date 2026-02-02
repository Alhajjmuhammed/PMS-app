"""
Serializers for POS Module
"""
from rest_framework import serializers
from apps.pos.models import MenuCategory, MenuItem, POSOrder, POSOrderItem, Outlet
from django.utils import timezone


class OutletSerializer(serializers.ModelSerializer):
    """Serializer for outlets."""
    outlet_type_display = serializers.CharField(source='get_outlet_type_display', read_only=True)
    
    class Meta:
        model = Outlet
        fields = [
            'id', 'property', 'name', 'code', 'outlet_type', 'outlet_type_display',
            'location', 'capacity', 'opening_time', 'closing_time', 'is_active'
        ]
        read_only_fields = ['id']


class MenuCategorySerializer(serializers.ModelSerializer):
    """Serializer for menu categories."""
    outlet_name = serializers.CharField(source='outlet.name', read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = MenuCategory
        fields = [
            'id', 'outlet', 'outlet_name', 'name', 'description',
            'sort_order', 'is_active', 'items_count'
        ]
        read_only_fields = ['id']


class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for menu items."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    outlet_name = serializers.CharField(source='category.outlet.name', read_only=True)
    profit_margin = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'category', 'category_name', 'outlet_name', 'name',
            'description', 'price', 'cost', 'profit_margin', 'is_available',
            'is_taxable', 'image'
        ]
        read_only_fields = ['id']
    
    def get_profit_margin(self, obj):
        """Calculate profit margin percentage."""
        if obj.price > 0:
            margin = ((obj.price - obj.cost) / obj.price) * 100
            return round(margin, 2)
        return 0
    
    def validate_price(self, value):
        """Validate price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_cost(self, value):
        """Validate cost is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value


class POSOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for POS order items."""
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    
    class Meta:
        model = POSOrderItem
        fields = [
            'id', 'order', 'menu_item', 'menu_item_name', 'quantity',
            'unit_price', 'amount', 'notes', 'is_voided'
        ]
        read_only_fields = ['id', 'amount']
    
    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class POSOrderSerializer(serializers.ModelSerializer):
    """Serializer for POS orders."""
    outlet_name = serializers.CharField(source='outlet.name', read_only=True)
    server_name = serializers.CharField(source='server.get_full_name', read_only=True)
    items = POSOrderItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = POSOrder
        fields = [
            'id', 'order_number', 'outlet', 'outlet_name', 'check_in',
            'room_number', 'guest_name', 'table_number', 'covers',
            'subtotal', 'tax_amount', 'discount', 'total', 'status',
            'is_posted_to_room', 'posted_at', 'notes', 'server',
            'server_name', 'created_at', 'updated_at', 'items', 'items_count'
        ]
        read_only_fields = ['id', 'order_number', 'posted_at', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate POS order data."""
        # If posting to room, check_in or room_number is required
        if data.get('is_posted_to_room'):
            if not data.get('check_in') and not data.get('room_number'):
                raise serializers.ValidationError(
                    "check_in or room_number is required when posting to room"
                )
        
        # Validate covers
        covers = data.get('covers', 1)
        if covers < 1:
            raise serializers.ValidationError("Covers must be at least 1")
        
        return data


class POSOrderCreateSerializer(serializers.Serializer):
    """Serializer for creating POS order with items."""
    outlet = serializers.IntegerField()
    check_in = serializers.IntegerField(required=False, allow_null=True)
    room_number = serializers.CharField(required=False, allow_blank=True)
    guest_name = serializers.CharField(required=False, allow_blank=True)
    table_number = serializers.CharField(required=False, allow_blank=True)
    covers = serializers.IntegerField(default=1)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_items(self, value):
        """Validate order items."""
        for item in value:
            if 'menu_item' not in item:
                raise serializers.ValidationError("Each item must have menu_item")
            if 'quantity' not in item:
                raise serializers.ValidationError("Each item must have quantity")
            if item['quantity'] <= 0:
                raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class POSOrderUpdateSerializer(serializers.Serializer):
    """Serializer for updating order amounts."""
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)


class POSDashboardSerializer(serializers.Serializer):
    """Serializer for POS dashboard statistics."""
    open_orders = serializers.IntegerField()
    orders_today = serializers.IntegerField()
    revenue_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    covers_today = serializers.IntegerField()
    avg_check_size = serializers.DecimalField(max_digits=10, decimal_places=2)
    top_selling_items = serializers.ListField()
