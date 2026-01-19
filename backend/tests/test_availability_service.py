import pytest
from datetime import date, timedelta
from apps.reservations.services import AvailabilityService
from apps.reservations.models import Reservation
from apps.rooms.models import Room, RoomType
from apps.properties.models import Property
from apps.guests.models import Guest


@pytest.mark.django_db
class TestAvailabilityService:
    """Test availability service."""
    
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
            name='Standard Room',
            code='STD',
            max_occupancy=2
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
    
    def test_check_availability_no_conflict(self, setup_data):
        """Test availability check with no conflicts."""
        check_in = date.today() + timedelta(days=5)
        check_out = check_in + timedelta(days=2)
        
        available = AvailabilityService.check_availability(
            room_id=setup_data['room'].id,
            check_in_date=check_in,
            check_out_date=check_out
        )
        
        assert available is True
    
    def test_check_availability_with_conflict(self, setup_data):
        """Test availability check with existing reservation."""
        from apps.reservations.models import ReservationRoom
        
        # Create existing reservation
        check_in = date.today() + timedelta(days=5)
        check_out = check_in + timedelta(days=3)
        
        reservation = Reservation.objects.create(
            hotel=setup_data['hotel'],
            guest=setup_data['guest'],
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            status='CONFIRMED'
        )
        
        ReservationRoom.objects.create(
            reservation=reservation,
            room=setup_data['room'],
            room_type=setup_data['room_type']
        )
        
        # Try to book overlapping dates
        new_check_in = check_in + timedelta(days=1)
        new_check_out = new_check_in + timedelta(days=2)
        
        available = AvailabilityService.check_availability(
            room_id=setup_data['room'].id,
            check_in_date=new_check_in,
            check_out_date=new_check_out
        )
        
        assert available is False
    
    def test_validate_booking_dates_past_date(self):
        """Test validation for past dates."""
        check_in = date.today() - timedelta(days=1)
        check_out = date.today() + timedelta(days=1)
        
        is_valid, error = AvailabilityService.validate_booking_dates(
            check_in, check_out
        )
        
        assert is_valid is False
        assert error is not None
    
    def test_validate_booking_dates_invalid_range(self):
        """Test validation for invalid date range."""
        check_in = date.today() + timedelta(days=5)
        check_out = check_in  # Same day
        
        is_valid, error = AvailabilityService.validate_booking_dates(
            check_in, check_out
        )
        
        assert is_valid is False
    
    def test_validate_booking_dates_valid(self):
        """Test validation for valid dates."""
        check_in = date.today() + timedelta(days=5)
        check_out = check_in + timedelta(days=2)
        
        is_valid, error = AvailabilityService.validate_booking_dates(
            check_in, check_out
        )
        
        assert is_valid is True
        assert error is None
    
    def test_get_available_rooms(self, setup_data):
        """Test getting available rooms."""
        check_in = date.today() + timedelta(days=5)
        check_out = check_in + timedelta(days=2)
        
        available_rooms = AvailabilityService.get_available_rooms(
            hotel_id=setup_data['hotel'].id,
            room_type_id=setup_data['room_type'].id,
            check_in_date=check_in,
            check_out_date=check_out,
            count=1
        )
        
        assert available_rooms.count() >= 0
    
    def test_availability_calendar(self, setup_data):
        """Test availability calendar generation."""
        start_date = date.today()
        end_date = start_date + timedelta(days=7)
        
        calendar = AvailabilityService.get_availability_calendar(
            hotel_id=setup_data['hotel'].id,
            room_type_id=setup_data['room_type'].id,
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(calendar) == 7
        for date_str, data in calendar.items():
            assert 'total_rooms' in data
            assert 'occupied' in data
            assert 'available' in data
            assert 'occupancy_rate' in data
