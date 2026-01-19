"""
Tests for new API endpoints created in Session 10
"""

import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.models import User
from apps.properties.models import Property
from apps.rooms.models import Room, RoomType, RoomImage
from apps.guests.models import Guest, GuestDocument
from apps.pos.models import Outlet, MenuCategory, MenuItem
from apps.notifications.models import Notification
from apps.billing.models import Folio
from apps.reservations.models import Reservation


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def setup_test_data(db):
    """Setup test data for API endpoint tests."""
    # Create user (email is username in this system)
    user = User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    
    # Create property
    property_obj = Property.objects.create(
        name='Test Hotel',
        code='TEST',
        address='123 Test St',
        city='Test City',
        country='Test Country'
    )
    
    # Create room type and room
    room_type = RoomType.objects.create(
        hotel=property_obj,
        name='Deluxe',
        code='DLX',
        max_occupancy=2
    )
    
    room = Room.objects.create(
        hotel=property_obj,
        room_type=room_type,
        room_number='101',
        status='VC'
    )
    
    # Create guest
    guest = Guest.objects.create(
        first_name='John',
        last_name='Doe',
        email='john@example.com'
    )
    
    # Create POS outlet
    outlet = Outlet.objects.create(
        property=property_obj,
        name='Restaurant',
        code='REST',
        outlet_type='RESTAURANT'
    )
    
    # Create notification
    notification = Notification.objects.create(
        user=user,
        title='Test Notification',
        message='Test message',
        is_read=False
    )
    
    # Create folio directly (without complex reservation)
    folio = Folio.objects.create(
        hotel=property_obj,
        guest=guest,
        folio_number='F-001',
        status='OPEN'
    )
    # Balance is calculated from charges, so it's zero by default
    
    return {
        'user': user,
        'property': property_obj,
        'room': room,
        'guest': guest,
        'outlet': outlet,
        'notification': notification,
        'folio': folio
    }


@pytest.mark.django_db
class TestRoomImagesAPI:
    """Test Room Images API endpoints."""
    
    def test_list_room_images(self, api_client, setup_test_data):
        """Test listing room images."""
        data = setup_test_data
        api_client.force_authenticate(user=data['user'])
        
        # Create a room image
        RoomImage.objects.create(
            room=data['room'],
            caption='Test image',
            is_primary=True,
            uploaded_by=data['user']
        )
        
        response = api_client.get(f'/api/v1/rooms/{data["room"].id}/images/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
    
    def test_create_room_image_requires_auth(self, api_client, setup_test_data):
        """Test creating room image requires authentication."""
        data = setup_test_data
        
        response = api_client.post(
            f'/api/v1/rooms/{data["room"].id}/images/',
            {'caption': 'Test'}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGuestDocumentsAPI:
    """Test Guest Documents API endpoints."""
    
    def test_list_guest_documents(self, api_client, setup_test_data):
        """Test listing guest documents."""
        data = setup_test_data
        api_client.force_authenticate(user=data['user'])
        
        response = api_client.get(f'/api/v1/guests/{data["guest"].id}/documents/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
    
    def test_create_guest_document_requires_auth(self, api_client, setup_test_data):
        """Test creating guest document requires authentication."""
        data = setup_test_data
        
        response = api_client.post(
            f'/api/v1/guests/{data["guest"].id}/documents/',
            {'document_type': 'PASSPORT'}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPOSMenuManagementAPI:
    """Test POS Menu Management API endpoints."""
    
    def test_list_menu_categories(self, api_client, setup_test_data):
        """Test listing menu categories."""
        data = setup_test_data
        api_client.force_authenticate(user=data['user'])
        
        response = api_client.get(f'/api/v1/pos/outlets/{data["outlet"].id}/categories/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
    
    def test_create_menu_category(self, api_client, setup_test_data):
        """Test creating menu category."""
        data = setup_test_data
        api_client.force_authenticate(user=data['user'])
        
        response = api_client.post(
            f'/api/v1/pos/outlets/{data["outlet"].id}/categories/',
            {
                'name': 'Beverages',
                'sort_order': 1,
                'is_active': True
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Beverages'
    
    def test_list_menu_items(self, api_client, setup_test_data):
        """Test listing menu items."""
        data = setup_test_data
        api_client.force_authenticate(user=data['user'])
        
        response = api_client.get('/api/v1/pos/menu-items/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)


@pytest.mark.django_db
class TestNotificationReadAPI:
    """Test Notification Read API endpoint."""
    
    def test_mark_notification_as_read(self, api_client, setup_test_data):
        """Test marking notification as read."""
        data = setup_test_data
        api_client.force_authenticate(user=data['user'])
        
        assert data['notification'].is_read is False
        
        response = api_client.post(f'/api/v1/notifications/{data["notification"].id}/read/')
        assert response.status_code == status.HTTP_200_OK
        
        # Verify notification was marked as read
        data['notification'].refresh_from_db()
        assert data['notification'].is_read is True
        assert data['notification'].read_at is not None
    
    def test_mark_notification_read_requires_ownership(self, api_client, setup_test_data):
        """Test users can only mark their own notifications as read."""
        data = setup_test_data
        
        # Create another user (email is username)
        other_user = User.objects.create_user(
            email='other@example.com',
            password='pass123'
        )
        api_client.force_authenticate(user=other_user)
        
        response = api_client.post(f'/api/v1/notifications/{data["notification"].id}/read/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestFolioCloseAPI:
    """Test Folio Close API endpoint."""
    
    def test_close_folio_with_zero_balance(self, api_client, setup_test_data):
        """Test closing folio with zero balance."""
        data = setup_test_data
        api_client.force_authenticate(user=data['user'])
        
        assert data['folio'].status == 'OPEN'
        
        response = api_client.patch(f'/api/v1/billing/folios/{data["folio"].id}/close/')
        assert response.status_code == status.HTTP_200_OK
        
        # Verify folio was closed
        data['folio'].refresh_from_db()
        assert data['folio'].status == 'CLOSED'
        assert data['folio'].closed_at is not None
        assert data['folio'].closed_by == data['user']
    
    def test_cannot_close_folio_with_balance(self, api_client, setup_test_data):
        """Test cannot close folio with outstanding balance."""
        data = setup_test_data
        api_client.force_authenticate(user=data['user'])
        
        # Add a charge to create non-zero balance
        from apps.billing.models import ChargeCode, FolioCharge
        charge_code = ChargeCode.objects.create(
            hotel=data['property'],
            code='ROOM',
            description='Room Charge',
            amount=100.00
        )
        FolioCharge.objects.create(
            folio=data['folio'],
            charge_code=charge_code,
            amount=100.00,
            description='Test charge'
        )
        data['folio'].recalculate_totals()
        
        response = api_client.patch(f'/api/v1/billing/folios/{data["folio"].id}/close/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'outstanding balance' in response.data['error'].lower()
        
        # Verify folio was not closed
        data['folio'].refresh_from_db()
        assert data['folio'].status == 'OPEN'
