import pytest
from datetime import date, timedelta
from decimal import Decimal
from apps.rates.services import PricingService
from apps.rates.models import RatePlan, Season, RoomRate, Discount
from apps.rooms.models import RoomType
from apps.properties.models import Property


@pytest.mark.django_db
class TestPricingService:
    """Test pricing service calculations."""
    
    @pytest.fixture
    def setup_data(self):
        """Create test data."""
        # Create property
        property_obj = Property.objects.create(
            name='Test Hotel',
            code='TEST001',
            total_rooms=50
        )
        
        # Create room type
        room_type = RoomType.objects.create(
            hotel=property_obj,
            name='Deluxe Room',
            code='DLX',
            max_occupancy=3,
            base_rate=Decimal('100.00')
        )
        
        # Create rate plan
        rate_plan = RatePlan.objects.create(
            property=property_obj,
            name='Standard Rate',
            code='STD',
            rate_type='RACK',
            is_active=True
        )
        
        # Create season
        season = Season.objects.create(
            property=property_obj,
            name='High Season',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            priority=1,
            is_active=True
        )
        
        # Create room rate
        room_rate = RoomRate.objects.create(
            rate_plan=rate_plan,
            room_type=room_type,
            season=season,
            single_rate=Decimal('100.00'),
            double_rate=Decimal('150.00'),
            extra_adult=Decimal('30.00'),
            extra_child=Decimal('20.00'),
            is_active=True
        )
        
        return {
            'property': property_obj,
            'room_type': room_type,
            'rate_plan': rate_plan,
            'season': season,
            'room_rate': room_rate
        }
    
    def test_calculate_basic_rate(self, setup_data):
        """Test basic rate calculation."""
        check_in = date.today()
        check_out = check_in + timedelta(days=2)
        
        result = PricingService.calculate_room_rate(
            room_type_id=setup_data['room_type'].id,
            rate_plan_id=setup_data['rate_plan'].id,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=2,
            children=0
        )
        
        assert 'error' not in result
        assert result['nights'] == 2
        assert result['adults'] == 2
        assert float(result['base_amount']) == 300.00  # 150 * 2 nights
    
    def test_calculate_with_extra_guests(self, setup_data):
        """Test rate with extra guests."""
        check_in = date.today()
        check_out = check_in + timedelta(days=1)
        
        result = PricingService.calculate_room_rate(
            room_type_id=setup_data['room_type'].id,
            rate_plan_id=setup_data['rate_plan'].id,
            check_in_date=check_in,
            check_out_date=check_out,
            adults=3,
            children=1
        )
        
        assert 'error' not in result
        # Base (150) + Extra adult (30) + Extra child (20) = 200 per night
        assert float(result['base_amount']) == 200.00
    
    def test_invalid_date_range(self, setup_data):
        """Test with invalid date range."""
        check_in = date.today()
        check_out = check_in  # Same day
        
        result = PricingService.calculate_room_rate(
            room_type_id=setup_data['room_type'].id,
            rate_plan_id=setup_data['rate_plan'].id,
            check_in_date=check_in,
            check_out_date=check_out
        )
        
        assert 'error' in result
    
    def test_discount_application(self, setup_data):
        """Test discount calculation."""
        # Create a discount
        discount = Discount.objects.create(
            property=setup_data['property'],
            name='10% Off',
            code='SAVE10',
            discount_type='PERCENTAGE',
            value=Decimal('10.00'),
            valid_from=date.today() - timedelta(days=1),
            valid_to=date.today() + timedelta(days=30),
            is_active=True
        )
        # Note: Discount model doesn't have rate_plans field, so discount applies to all
        
        check_in = date.today()
        check_out = check_in + timedelta(days=2)
        
        result = PricingService.calculate_room_rate(
            room_type_id=setup_data['room_type'].id,
            rate_plan_id=setup_data['rate_plan'].id,
            check_in_date=check_in,
            check_out_date=check_out
        )
        
        assert 'error' not in result
        # Discount should be applied
        assert result['discount_amount'] > 0
        assert len(result['discount_details']) > 0
