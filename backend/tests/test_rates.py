"""
Tests for Rates Module
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

from apps.rates.models import Season, RatePlan, RoomRate, DateRate, Package, Discount, YieldRule
from apps.properties.models import Property
from apps.rooms.models import RoomType


@pytest.mark.django_db
class TestRatesModels:
    """Test rates and revenue management functionality."""
    
    @pytest.fixture
    def setup_data(self):
        """Create test data."""
        # Create property
        property_obj = Property.objects.create(
            name='Test Hotel',
            code='TEST001',
            total_rooms=100,
            address='123 Test St',
            city='Test City',
            country='Test Country'
        )
        
        # Create room type
        room_type = RoomType.objects.create(
            hotel=property_obj,
            name='Deluxe Room',
            code='DLX',
            max_occupancy=2,
            base_rate=Decimal('200.00')
        )
        
        # Create season
        season = Season.objects.create(
            property=property_obj,
            name='High Season',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            priority=10,
            is_active=True
        )
        
        # Create rate plan
        rate_plan = RatePlan.objects.create(
            property=property_obj,
            name='Best Available Rate',
            code='BAR',
            rate_type='BAR',
            min_nights=1,
            cancellation_hours=24,
            is_refundable=True,
            is_active=True
        )
        
        return {
            'property': property_obj,
            'room_type': room_type,
            'season': season,
            'rate_plan': rate_plan
        }
    
    def test_create_season(self, setup_data):
        """Test creating a pricing season."""
        season = Season.objects.create(
            property=setup_data['property'],
            name='Summer Season',
            start_date=date(2026, 6, 1),
            end_date=date(2026, 8, 31),
            priority=5
        )
        
        assert season.id is not None
        assert season.name == 'Summer Season'
        assert season.is_active is True
        assert season.priority == 5
    
    def test_season_priority(self, setup_data):
        """Test season priority ordering."""
        low_season = Season.objects.create(
            property=setup_data['property'],
            name='Low Season',
            start_date=date(2026, 11, 1),
            end_date=date(2027, 2, 28),
            priority=1
        )
        
        high_season = setup_data['season']
        
        assert high_season.priority > low_season.priority
    
    def test_create_rate_plan(self, setup_data):
        """Test creating a rate plan."""
        rate_plan = RatePlan.objects.create(
            property=setup_data['property'],
            name='Corporate Rate',
            code='CORP',
            rate_type='CORPORATE',
            min_nights=2,
            max_nights=14,
            min_advance_booking=0,
            cancellation_hours=48,
            is_refundable=False
        )
        
        assert rate_plan.id is not None
        assert rate_plan.code == 'CORP'
        assert rate_plan.min_nights == 2
        assert rate_plan.is_refundable is False
    
    def test_rate_plan_restrictions(self, setup_data):
        """Test rate plan booking restrictions."""
        rate_plan = RatePlan.objects.create(
            property=setup_data['property'],
            name='Early Bird Special',
            code='EARLY',
            rate_type='PROMOTIONAL',
            min_nights=3,
            min_advance_booking=30,
            max_advance_booking=90,
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=180)
        )
        
        assert rate_plan.min_nights == 3
        assert rate_plan.min_advance_booking == 30
        assert rate_plan.max_advance_booking == 90
        assert rate_plan.valid_from is not None
    
    def test_create_room_rate(self, setup_data):
        """Test creating room rate with occupancy pricing."""
        room_rate = RoomRate.objects.create(
            rate_plan=setup_data['rate_plan'],
            room_type=setup_data['room_type'],
            season=setup_data['season'],
            single_rate=Decimal('150.00'),
            double_rate=Decimal('200.00'),
            extra_adult=Decimal('50.00'),
            extra_child=Decimal('25.00')
        )
        
        assert room_rate.id is not None
        assert room_rate.single_rate == Decimal('150.00')
        assert room_rate.double_rate == Decimal('200.00')
        assert room_rate.extra_adult == Decimal('50.00')
        assert room_rate.extra_child == Decimal('25.00')
    
    def test_room_rate_day_of_week_pricing(self, setup_data):
        """Test day-of-week specific pricing."""
        room_rate = RoomRate.objects.create(
            rate_plan=setup_data['rate_plan'],
            room_type=setup_data['room_type'],
            single_rate=Decimal('150.00'),
            double_rate=Decimal('200.00'),
            extra_adult=Decimal('50.00'),
            extra_child=Decimal('25.00'),
            friday_rate=Decimal('250.00'),
            saturday_rate=Decimal('300.00')
        )
        
        assert room_rate.friday_rate == Decimal('250.00')
        assert room_rate.saturday_rate == Decimal('300.00')
    
    def test_create_date_rate_override(self, setup_data):
        """Test creating date-specific rate override."""
        special_date = date.today() + timedelta(days=30)
        
        date_rate = DateRate.objects.create(
            room_type=setup_data['room_type'],
            rate_plan=setup_data['rate_plan'],
            date=special_date,
            rate=Decimal('350.00'),
            min_stay=2
        )
        
        assert date_rate.id is not None
        assert date_rate.date == special_date
        assert date_rate.rate == Decimal('350.00')
        assert date_rate.min_stay == 2
        assert date_rate.is_closed is False
    
    def test_date_rate_closed_for_sale(self, setup_data):
        """Test marking date as closed for sale."""
        date_rate = DateRate.objects.create(
            room_type=setup_data['room_type'],
            rate_plan=setup_data['rate_plan'],
            date=date.today() + timedelta(days=15),
            rate=Decimal('0.00'),
            is_closed=True
        )
        
        assert date_rate.is_closed is True
    
    def test_create_package(self, setup_data):
        """Test creating a package with inclusions."""
        package = Package.objects.create(
            property=setup_data['property'],
            name='Romantic Getaway',
            code='ROMANCE',
            description='2 nights with breakfast and spa',
            rate_plan=setup_data['rate_plan'],
            includes_breakfast=True,
            includes_spa=True,
            package_price=Decimal('500.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=90),
            min_nights=2
        )
        
        assert package.id is not None
        assert package.code == 'ROMANCE'
        assert package.includes_breakfast is True
        assert package.includes_spa is True
        assert package.package_price == Decimal('500.00')
        assert package.min_nights == 2
    
    def test_package_with_discount_percent(self, setup_data):
        """Test package with percentage discount."""
        package = Package.objects.create(
            property=setup_data['property'],
            name='Weekend Special',
            code='WEEKEND',
            description='Save 20% on weekends',
            rate_plan=setup_data['rate_plan'],
            discount_percent=Decimal('20.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            min_nights=1
        )
        
        assert package.discount_percent == Decimal('20.00')
        assert package.package_price is None
    
    def test_create_discount_code(self, setup_data):
        """Test creating a discount code."""
        discount = Discount.objects.create(
            property=setup_data['property'],
            name='Spring Sale',
            code='SPRING2026',
            discount_type='PERCENTAGE',
            value=Decimal('15.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=60),
            max_uses=100
        )
        
        assert discount.id is not None
        assert discount.code == 'SPRING2026'
        assert discount.discount_type == 'PERCENTAGE'
        assert discount.value == Decimal('15.00')
        assert discount.max_uses == 100
        assert discount.times_used == 0
    
    def test_discount_fixed_amount(self, setup_data):
        """Test fixed amount discount."""
        discount = Discount.objects.create(
            property=setup_data['property'],
            name='$50 Off',
            code='SAVE50',
            discount_type='FIXED',
            value=Decimal('50.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            min_amount=Decimal('200.00')
        )
        
        assert discount.discount_type == 'FIXED'
        assert discount.value == Decimal('50.00')
        assert discount.min_amount == Decimal('200.00')
    
    def test_discount_usage_tracking(self, setup_data):
        """Test discount usage tracking."""
        discount = Discount.objects.create(
            property=setup_data['property'],
            name='Limited Offer',
            code='LIMITED10',
            discount_type='PERCENTAGE',
            value=Decimal('10.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=7),
            max_uses=5
        )
        
        # Simulate usage
        discount.times_used = 3
        discount.save()
        
        assert discount.times_used == 3
        assert discount.times_used < discount.max_uses
    
    def test_discount_with_restrictions(self, setup_data):
        """Test discount with booking restrictions."""
        discount = Discount.objects.create(
            property=setup_data['property'],
            name='Long Stay Discount',
            code='LONGSTAY',
            discount_type='PERCENTAGE',
            value=Decimal('25.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=180),
            min_nights=7,
            min_amount=Decimal('1000.00')
        )
        
        assert discount.min_nights == 7
        assert discount.min_amount == Decimal('1000.00')
    
    def test_create_yield_rule_occupancy(self, setup_data):
        """Test creating occupancy-based yield rule."""
        yield_rule = YieldRule.objects.create(
            property=setup_data['property'],
            name='High Occupancy Boost',
            trigger_type='OCCUPANCY',
            min_threshold=80,
            max_threshold=100,
            adjustment_percent=Decimal('25.00'),
            priority=10
        )
        
        assert yield_rule.id is not None
        assert yield_rule.trigger_type == 'OCCUPANCY'
        assert yield_rule.min_threshold == 80
        assert yield_rule.adjustment_percent == Decimal('25.00')
    
    def test_yield_rule_days_ahead(self, setup_data):
        """Test days-ahead yield rule."""
        yield_rule = YieldRule.objects.create(
            property=setup_data['property'],
            name='Last Minute Discount',
            trigger_type='DAY_AHEAD',
            min_threshold=0,
            max_threshold=3,
            adjustment_percent=Decimal('-15.00'),
            priority=5
        )
        
        assert yield_rule.trigger_type == 'DAY_AHEAD'
        assert yield_rule.max_threshold == 3
        assert yield_rule.adjustment_percent == Decimal('-15.00')
    
    def test_yield_rule_priority(self, setup_data):
        """Test yield rule priority ordering."""
        high_priority = YieldRule.objects.create(
            property=setup_data['property'],
            name='Critical Rule',
            trigger_type='DEMAND',
            min_threshold=90,
            adjustment_percent=Decimal('50.00'),
            priority=100
        )
        
        low_priority = YieldRule.objects.create(
            property=setup_data['property'],
            name='Standard Rule',
            trigger_type='OCCUPANCY',
            min_threshold=50,
            adjustment_percent=Decimal('10.00'),
            priority=10
        )
        
        assert high_priority.priority > low_priority.priority
    
    def test_multiple_rate_plans_same_property(self, setup_data):
        """Test multiple rate plans for same property."""
        bar_plan = setup_data['rate_plan']
        
        corp_plan = RatePlan.objects.create(
            property=setup_data['property'],
            name='Corporate Rate',
            code='CORP',
            rate_type='CORPORATE',
            min_nights=1
        )
        
        gov_plan = RatePlan.objects.create(
            property=setup_data['property'],
            name='Government Rate',
            code='GOV',
            rate_type='GOVERNMENT',
            min_nights=1
        )
        
        all_plans = RatePlan.objects.filter(property=setup_data['property'])
        assert all_plans.count() == 3
    
    def test_seasonal_room_rates(self, setup_data):
        """Test different rates for different seasons."""
        # High season rate
        high_rate = RoomRate.objects.create(
            rate_plan=setup_data['rate_plan'],
            room_type=setup_data['room_type'],
            season=setup_data['season'],
            single_rate=Decimal('200.00'),
            double_rate=Decimal('250.00'),
            extra_adult=Decimal('60.00'),
            extra_child=Decimal('30.00')
        )
        
        # Create low season
        low_season = Season.objects.create(
            property=setup_data['property'],
            name='Low Season',
            start_date=date(2026, 11, 1),
            end_date=date(2027, 3, 31),
            priority=1
        )
        
        # Low season rate
        low_rate = RoomRate.objects.create(
            rate_plan=setup_data['rate_plan'],
            room_type=setup_data['room_type'],
            season=low_season,
            single_rate=Decimal('120.00'),
            double_rate=Decimal('150.00'),
            extra_adult=Decimal('40.00'),
            extra_child=Decimal('20.00')
        )
        
        assert high_rate.double_rate > low_rate.double_rate
        assert high_rate.season.priority > low_rate.season.priority
