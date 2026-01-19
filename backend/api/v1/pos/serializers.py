from rest_framework import serializers
from apps.pos.models import Outlet, MenuCategory, MenuItem, POSOrder, POSOrderItem


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'cost', 'category', 'category_name', 'is_available', 'is_taxable', 'image']


class MenuCategorySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)
    outlet_name = serializers.CharField(source='outlet.name', read_only=True)
    
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'description', 'outlet', 'outlet_name', 'sort_order', 'is_active', 'items']


class OutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = ['id', 'name', 'code', 'outlet_type', 'location', 'opening_time', 'closing_time']


class POSOrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='menu_item.name', read_only=True)
    
    class Meta:
        model = POSOrderItem
        fields = ['id', 'menu_item', 'item_name', 'quantity', 'unit_price', 'amount', 'notes']


class POSOrderSerializer(serializers.ModelSerializer):
    items = POSOrderItemSerializer(many=True, read_only=True)
    outlet_name = serializers.CharField(source='outlet.name', read_only=True)
    
    class Meta:
        model = POSOrder
        fields = [
            'id', 'order_number', 'outlet', 'outlet_name',
            'room_number', 'guest_name', 'table_number', 'covers',
            'subtotal', 'tax_amount', 'discount', 'total',
            'status', 'is_posted_to_room', 'items', 'created_at'
        ]


class OrderCreateSerializer(serializers.Serializer):
    outlet_id = serializers.IntegerField()
    room_number = serializers.CharField(required=False, allow_blank=True)
    guest_name = serializers.CharField(required=False, allow_blank=True)
    table_number = serializers.CharField(required=False, allow_blank=True)
    covers = serializers.IntegerField(default=1)


class AddOrderItemSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
    notes = serializers.CharField(required=False, allow_blank=True)
