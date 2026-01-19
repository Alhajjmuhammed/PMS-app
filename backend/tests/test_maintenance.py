"""
Tests for Maintenance Module
"""

import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta

from apps.maintenance.models import MaintenanceRequest, Asset, MaintenanceLog
from apps.properties.models import Property
from apps.rooms.models import Room, RoomType
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestMaintenanceModels:
    """Test maintenance functionality."""
    
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
        
        # Create room type
        room_type = RoomType.objects.create(
            hotel=property_obj,
            name='Deluxe',
            code='DLX',
            max_occupancy=3,
            base_rate=Decimal('150.00')
        )
        
        # Create room
        room = Room.objects.create(
            hotel=property_obj,
            room_number='201',
            room_type=room_type,
            status='CLEAN'
        )
        
        # Create users
        technician = User.objects.create_user(
            email='tech@example.com',
            password='test123',
            first_name='Tech',
            last_name='Smith',
            role='STAFF'
        )
        
        reporter = User.objects.create_user(
            email='reporter@example.com',
            password='test123',
            first_name='Reporter',
            last_name='Jones',
            role='STAFF'
        )
        
        return {
            'property': property_obj,
            'room': room,
            'technician': technician,
            'reporter': reporter
        }
    
    def test_create_maintenance_request(self, setup_data):
        """Test creating a maintenance request."""
        request = MaintenanceRequest.objects.create(
            request_number='MNT001',
            property=setup_data['property'],
            room=setup_data['room'],
            request_type='PLUMBING',
            priority='HIGH',
            title='Leaking faucet',
            description='Bathroom sink faucet is leaking',
            reported_by=setup_data['reporter']
        )
        
        assert request.id is not None
        assert request.status == 'PENDING'
        assert request.priority == 'HIGH'
        assert request.request_type == 'PLUMBING'
    
    def test_assign_maintenance_request(self, setup_data):
        """Test assigning a request to a technician."""
        request = MaintenanceRequest.objects.create(
            request_number='MNT002',
            property=setup_data['property'],
            room=setup_data['room'],
            request_type='ELECTRICAL',
            priority='MEDIUM',
            title='Broken light',
            description='Light fixture not working',
            reported_by=setup_data['reporter']
        )
        
        # Assign to technician
        request.assigned_to = setup_data['technician']
        request.assigned_at = timezone.now()
        request.status = 'ASSIGNED'
        request.save()
        
        assert request.assigned_to == setup_data['technician']
        assert request.status == 'ASSIGNED'
        assert request.assigned_at is not None
    
    def test_complete_maintenance_request(self, setup_data):
        """Test completing a maintenance request."""
        request = MaintenanceRequest.objects.create(
            request_number='MNT003',
            property=setup_data['property'],
            room=setup_data['room'],
            request_type='HVAC',
            priority='HIGH',
            title='AC not working',
            description='Air conditioning unit not cooling',
            reported_by=setup_data['reporter'],
            assigned_to=setup_data['technician']
        )
        
        # Start work
        request.status = 'IN_PROGRESS'
        request.started_at = timezone.now()
        request.save()
        
        # Complete work
        request.status = 'COMPLETED'
        request.completed_at = timezone.now()
        request.resolution_notes = 'Replaced compressor'
        request.parts_cost = Decimal('250.00')
        request.labor_hours = Decimal('2.5')
        request.save()
        
        assert request.status == 'COMPLETED'
        assert request.completed_at is not None
        assert request.parts_cost == Decimal('250.00')
        assert request.labor_hours == Decimal('2.5')
    
    def test_emergency_priority(self, setup_data):
        """Test emergency priority request."""
        request = MaintenanceRequest.objects.create(
            request_number='MNT004',
            property=setup_data['property'],
            request_type='PLUMBING',
            priority='EMERGENCY',
            title='Flooding in lobby',
            description='Burst pipe causing flooding',
            reported_by=setup_data['reporter']
        )
        
        assert request.priority == 'EMERGENCY'
        assert request.status == 'PENDING'
    
    def test_create_asset(self, setup_data):
        """Test creating an asset."""
        asset = Asset.objects.create(
            code='AST001',
            property=setup_data['property'],
            room=setup_data['room'],
            name='HVAC Unit A1',
            category='HVAC',
            brand='Carrier',
            model='XYZ-123',
            purchase_date=timezone.now().date() - timedelta(days=365),
            warranty_expiry=timezone.now().date() + timedelta(days=365),
            is_active=True
        )
        
        assert asset.id is not None
        assert asset.category == 'HVAC'
        assert asset.is_active is True
    
    def test_create_maintenance_log(self, setup_data):
        """Test creating a maintenance log entry."""
        request = MaintenanceRequest.objects.create(
            request_number='MNT005',
            property=setup_data['property'],
            room=setup_data['room'],
            request_type='PREVENTIVE',
            priority='LOW',
            title='Monthly HVAC check',
            description='Regular maintenance check',
            reported_by=setup_data['reporter'],
            assigned_to=setup_data['technician']
        )
        
        log = MaintenanceLog.objects.create(
            request=request,
            action='Cleaned filters and checked refrigerant levels',
            notes='Air filters x2 replaced',
            user=setup_data['technician']
        )
        
        assert log.id is not None
        assert log.user == setup_data['technician']
        assert 'filters' in log.action
    
    def test_preventive_maintenance(self, setup_data):
        """Test preventive maintenance workflow."""
        # Create recurring preventive maintenance
        request = MaintenanceRequest.objects.create(
            request_number='MNT006',
            property=setup_data['property'],
            request_type='PREVENTIVE',
            priority='LOW',
            title='Quarterly elevator inspection',
            description='Required quarterly safety inspection',
            location='Elevator A',
            reported_by=setup_data['reporter'],
            assigned_to=setup_data['technician']
        )
        
        request.status = 'COMPLETED'
        request.completed_at = timezone.now()
        request.resolution_notes = 'All systems operational'
        request.save()
        
        assert request.request_type == 'PREVENTIVE'
        assert request.status == 'COMPLETED'
