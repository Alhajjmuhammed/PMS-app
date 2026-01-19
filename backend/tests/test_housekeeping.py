"""Tests for Housekeeping module."""
import pytest
from datetime import date, timedelta
from django.utils import timezone
from apps.housekeeping.models import HousekeepingTask
from apps.properties.models import Property
from apps.rooms.models import Room, RoomType
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestHousekeepingModels:
    """Test housekeeping models."""
    
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
            name='Standard Room',
            code='STD',
            max_occupancy=2,
            base_rate=100
        )
        
        # Create room
        room = Room.objects.create(
            hotel=property_obj,
            room_type=room_type,
            room_number='101',
            status='VD',  # Vacant Dirty
            is_active=True
        )
        
        # Create user
        user = User.objects.create_user(
            email='housekeeper@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Housekeeper'
        )
        
        return {
            'property': property_obj,
            'room_type': room_type,
            'room': room,
            'user': user
        }
    
    def test_create_housekeeping_task(self, setup_data):
        """Test creating a housekeeping task."""
        task = HousekeepingTask.objects.create(
            room=setup_data['room'],
            task_type='CLEANING',
            priority='NORMAL',
            status='PENDING',
            scheduled_date=date.today(),
            created_by=setup_data['user']
        )
        
        assert task.id is not None
        assert task.room == setup_data['room']
        assert task.task_type == 'CLEANING'
        assert task.status == 'PENDING'
    
    def test_task_assignment(self, setup_data):
        """Test assigning a task to a housekeeper."""
        task = HousekeepingTask.objects.create(
            room=setup_data['room'],
            task_type='CLEANING',
            status='PENDING',
            scheduled_date=date.today()
        )
        
        # Assign task
        task.assigned_to = setup_data['user']
        task.assigned_at = timezone.now()
        task.save()
        
        assert task.assigned_to == setup_data['user']
        assert task.assigned_at is not None
    
    def test_task_completion(self, setup_data):
        """Test completing a task."""
        task = HousekeepingTask.objects.create(
            room=setup_data['room'],
            task_type='CLEANING',
            status='IN_PROGRESS',
            scheduled_date=date.today(),
            assigned_to=setup_data['user'],
            started_at=timezone.now()
        )
        
        # Complete task
        task.status = 'COMPLETED'
        task.completed_at = timezone.now()
        task.save()
        
        assert task.status == 'COMPLETED'
        assert task.completed_at is not None
    
    def test_task_inspection(self, setup_data):
        """Test inspecting a completed task."""
        task = HousekeepingTask.objects.create(
            room=setup_data['room'],
            task_type='CLEANING',
            status='COMPLETED',
            scheduled_date=date.today(),
            completed_at=timezone.now()
        )
        
        # Inspect task
        task.inspected_by = setup_data['user']
        task.inspected_at = timezone.now()
        task.inspection_passed = True
        task.inspection_notes = 'Room cleaned to standard'
        task.status = 'INSPECTED'
        task.save()
        
        assert task.status == 'INSPECTED'
        assert task.inspection_passed is True
        assert task.inspected_by == setup_data['user']
    
    def test_urgent_task_priority(self, setup_data):
        """Test creating urgent priority task."""
        task = HousekeepingTask.objects.create(
            room=setup_data['room'],
            task_type='SPECIAL_REQUEST',
            priority='URGENT',
            status='PENDING',
            scheduled_date=date.today(),
            special_instructions='Guest allergic to feather pillows'
        )
        
        assert task.priority == 'URGENT'
        assert task.special_instructions != ''
