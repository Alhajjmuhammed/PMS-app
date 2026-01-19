import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from apps.properties.models import Property
from apps.rooms.models import Room, RoomType
from apps.guests.models import Guest
from apps.reservations.models import Reservation

User = get_user_model()


@pytest.mark.django_db
class TestReservationAPI:
    """Test reservation API endpoints."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client with authenticated user."""
        client = APIClient()
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        client.force_authenticate(user=user)
        return client, user
    
    @pytest.fixture
    def setup_data(self):
        """Create test data."""
        property_obj = Property.objects.create(
            name='Test Hotel',
            code='TEST001',
            total_rooms=10
        )
        
        room_type = RoomType.objects.create(
            hotel=property_obj,
            name='Standard',
            code='STD',
            max_occupancy=2,
            base_rate=100
        )
        
        room = Room.objects.create(
            hotel=property_obj,
            room_type=room_type,
            room_number='101',
            status='VC',
            is_active=True
        )
        
        guest = Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890'
        )
        
        return {
            'hotel': property_obj,
            'room_type': room_type,
            'room': room,
            'guest': guest
        }
    
    def test_list_reservations(self, api_client, setup_data):
        """Test listing reservations."""
        client, user = api_client
        
        # Create a reservation
        Reservation.objects.create(
            hotel=setup_data['hotel'],
            guest=setup_data['guest'],
            check_in_date=date.today() + timedelta(days=1),
            check_out_date=date.today() + timedelta(days=3),
            adults=2,
            status='CONFIRMED'
        )
        
        response = client.get('/api/v1/reservations/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_check_availability(self, api_client, setup_data):
        """Test availability check endpoint."""
        client, user = api_client
        
        data = {
            'hotel_id': setup_data['hotel'].id,
            'room_type_id': setup_data['room_type'].id,
            'check_in_date': (date.today() + timedelta(days=5)).isoformat(),
            'check_out_date': (date.today() + timedelta(days=7)).isoformat(),
            'count': 1
        }
        
        response = client.post('/api/v1/reservations/check-availability/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'available' in response.data
        assert response.data['available'] is True
    
    def test_calculate_price(self, api_client, setup_data):
        """Test price calculation endpoint."""
        from apps.rates.models import RatePlan, Season, RoomRate
        from decimal import Decimal
        
        client, user = api_client
        
        # Create rate plan
        rate_plan = RatePlan.objects.create(
            property=setup_data['hotel'],
            name='Standard',
            code='STD',
            rate_type='RACK',
            is_active=True
        )
        
        # Create season
        season = Season.objects.create(
            property=setup_data['hotel'],
            name='Regular',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            priority=1,
            is_active=True
        )
        
        # Create room rate
        RoomRate.objects.create(
            rate_plan=rate_plan,
            room_type=setup_data['room_type'],
            season=season,
            single_rate=Decimal('100.00'),
            double_rate=Decimal('150.00'),
            extra_adult=Decimal('30.00'),
            extra_child=Decimal('20.00'),
            is_active=True
        )
        
        data = {
            'room_type_id': setup_data['room_type'].id,
            'rate_plan_id': rate_plan.id,
            'check_in_date': (date.today() + timedelta(days=1)).isoformat(),
            'check_out_date': (date.today() + timedelta(days=3)).isoformat(),
            'adults': 2,
            'children': 0
        }
        
        response = client.post('/api/v1/reservations/calculate-price/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_amount' in response.data
        assert 'nights' in response.data
        assert response.data['nights'] == 2
    
    def test_filter_reservations_by_status(self, api_client, setup_data):
        """Test filtering reservations by status."""
        client, user = api_client
        
        # Create reservations with different statuses
        Reservation.objects.create(
            hotel=setup_data['hotel'],
            guest=setup_data['guest'],
            check_in_date=date.today() + timedelta(days=1),
            check_out_date=date.today() + timedelta(days=2),
            adults=2,
            status='CONFIRMED'
        )
        
        Reservation.objects.create(
            hotel=setup_data['hotel'],
            guest=setup_data['guest'],
            check_in_date=date.today() + timedelta(days=3),
            check_out_date=date.today() + timedelta(days=4),
            adults=2,
            status='CANCELLED'
        )
        
        response = client.get('/api/v1/reservations/?status=CONFIRMED')
        
        assert response.status_code == status.HTTP_200_OK
        assert all(r['status'] == 'CONFIRMED' for r in response.data['results'])
    
    def test_search_reservations(self, api_client, setup_data):
        """Test searching reservations."""
        client, user = api_client
        
        # Create a reservation
        Reservation.objects.create(
            hotel=setup_data['hotel'],
            guest=setup_data['guest'],
            check_in_date=date.today() + timedelta(days=1),
            check_out_date=date.today() + timedelta(days=2),
            adults=2,
            status='CONFIRMED',
            confirmation_number='TEST123'
        )
        
        response = client.get('/api/v1/reservations/?search=TEST123')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0


@pytest.mark.django_db
class TestGuestAPI:
    """Test guest API endpoints."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client."""
        client = APIClient()
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        client.force_authenticate(user=user)
        return client
    
    def test_create_guest_valid(self, api_client):
        """Test creating a guest with valid data."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone': '+1234567890',
            'date_of_birth': '1990-01-01'
        }
        
        response = api_client.post('/api/v1/guests/create/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'jane@example.com'
    
    def test_create_guest_invalid_email(self, api_client):
        """Test creating guest with duplicate email."""
        Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='duplicate@example.com',
            phone='+1234567890'
        )
        
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'duplicate@example.com',
            'phone': '+0987654321'
        }
        
        response = api_client.post('/api/v1/guests/create/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_search_guests(self, api_client):
        """Test searching guests."""
        Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890'
        )
        
        response = api_client.get('/api/v1/guests/?search=John')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
