"""Tests for POS module."""
import pytest
from decimal import Decimal
from datetime import datetime
from apps.pos.models import Outlet, MenuCategory, MenuItem, POSOrder, POSOrderItem
from apps.properties.models import Property
from apps.guests.models import Guest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestPOSModels:
    """Test POS models."""
    
    @pytest.fixture
    def setup_data(self):
        """Create test data."""
        # Create property
        property_obj = Property.objects.create(
            name='Test Hotel',
            code='TEST001',
            total_rooms=10,
            address='123 Test St',
            city='Test City',
            country='Test Country'
        )
        
        # Create outlet
        outlet = Outlet.objects.create(
            property=property_obj,
            name='Main Restaurant',
            code='REST01',
            outlet_type='RESTAURANT',
            capacity=50,
            is_active=True
        )
        
        # Create menu category
        category = MenuCategory.objects.create(
            outlet=outlet,
            name='Appetizers',
            sort_order=1,
            is_active=True
        )
        
        # Create menu items
        item1 = MenuItem.objects.create(
            category=category,
            name='Caesar Salad',
            description='Classic Caesar with parmesan',
            price=Decimal('12.50'),
            cost=Decimal('4.00'),
            is_available=True,
            is_taxable=True
        )
        
        item2 = MenuItem.objects.create(
            category=category,
            name='Soup of the Day',
            price=Decimal('8.00'),
            cost=Decimal('2.50'),
            is_available=True
        )
        
        # Create guest
        guest = Guest.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            phone='+9876543210'
        )
        
        # Create user
        user = User.objects.create_user(
            email='server@test.com',
            password='testpass123',
            first_name='Server',
            last_name='One'
        )
        
        return {
            'property': property_obj,
            'outlet': outlet,
            'category': category,
            'item1': item1,
            'item2': item2,
            'guest': guest,
            'user': user
        }
    
    def test_create_outlet(self, setup_data):
        """Test creating an outlet."""
        outlet = setup_data['outlet']
        
        assert outlet.id is not None
        assert outlet.name == 'Main Restaurant'
        assert outlet.outlet_type == 'RESTAURANT'
        assert outlet.is_active is True
    
    def test_create_menu_structure(self, setup_data):
        """Test menu category and items."""
        category = setup_data['category']
        item1 = setup_data['item1']
        
        assert category.outlet == setup_data['outlet']
        assert item1.category == category
        assert item1.price == Decimal('12.50')
    
    def test_create_order(self, setup_data):
        """Test creating a POS order."""
        order = POSOrder.objects.create(
            outlet=setup_data['outlet'],
            order_number='ORD001',
            status='OPEN',
            table_number='T5',
            server=setup_data['user']
        )
        
        assert order.id is not None
        assert order.status == 'OPEN'
        assert order.total == Decimal('0.00')
    
    def test_add_items_to_order(self, setup_data):
        """Test adding items to order."""
        order = POSOrder.objects.create(
            outlet=setup_data['outlet'],
            order_number='ORD002',
            status='OPEN',
            server=setup_data['user']
        )
        
        # Add items
        POSOrderItem.objects.create(
            order=order,
            menu_item=setup_data['item1'],
            quantity=2,
            unit_price=setup_data['item1'].price
        )
        
        POSOrderItem.objects.create(
            order=order,
            menu_item=setup_data['item2'],
            quantity=1,
            unit_price=setup_data['item2'].price
        )
        
        # Calculate total
        total = sum(item.amount for item in order.items.all())
        order.total = total
        order.save()
        
        assert order.items.count() == 2
        assert order.total == Decimal('33.00')  # (12.50 * 2) + 8.00
    
    def test_order_with_guest(self, setup_data):
        """Test order linked to guest."""
        order = POSOrder.objects.create(
            outlet=setup_data['outlet'],
            order_number='ORD003',
            status='OPEN',
            guest_name=f"{setup_data['guest'].first_name} {setup_data['guest'].last_name}",
            room_number='201',
            server=setup_data['user']
        )
        
        assert order.guest_name == 'Jane Smith'
        assert order.room_number == '201'
    
    def test_close_order(self, setup_data):
        """Test closing an order."""
        order = POSOrder.objects.create(
            outlet=setup_data['outlet'],
            order_number='ORD004',
            status='OPEN',
            server=setup_data['user']
        )
        
        # Add item
        POSOrderItem.objects.create(
            order=order,
            menu_item=setup_data['item1'],
            quantity=1,
            unit_price=setup_data['item1'].price
        )
        
        # Close order
        order.subtotal = setup_data['item1'].price
        order.tax_amount = order.subtotal * Decimal('0.10')
        order.total = order.subtotal + order.tax_amount
        order.status = 'CLOSED'
        order.save()
        
        assert order.status == 'CLOSED'
        assert order.total == Decimal('13.75')  # 12.50 + 1.25 tax
    
    def test_menu_item_availability(self, setup_data):
        """Test menu item availability."""
        item = setup_data['item1']
        
        # Mark as unavailable
        item.is_available = False
        item.save()
        
        assert item.is_available is False
