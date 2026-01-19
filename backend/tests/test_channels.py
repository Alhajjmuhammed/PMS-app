"""
Tests for Channels Module - OTA Integration
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

from apps.channels.models import (
    Channel, PropertyChannel, RoomTypeMapping, RatePlanMapping,
    AvailabilityUpdate, RateUpdate, ChannelReservation
)
from apps.properties.models import Property
from apps.rooms.models import RoomType
from apps.rates.models import Season, RatePlan, RoomRate


@pytest.fixture
def setup_channel_data(db):
    """Setup test data for channel tests."""
    # Create property
    property = Property.objects.create(
        name='Beach Resort',
        code='BEACH',
        address='123 Beach St',
        city='Miami',
        country='USA',
        email='info@beachresort.com',
        phone='+1234567890'
    )
    
    # Create room type
    room_type = RoomType.objects.create(
        hotel=property,
        name='Double Room',
        code='DBL',
        max_occupancy=2,
        base_rate=Decimal('180.00')
    )
    
    # Create season and rate plan
    season = Season.objects.create(
        property=property,
        name='High Season',
        start_date=date.today(),
        end_date=date.today() + timedelta(days=90),
        priority=1
    )
    
    rate_plan = RatePlan.objects.create(
        property=property,
        name='Best Available Rate',
        code='BAR',
        rate_type='STANDARD',
        min_nights=1,
        valid_from=date.today(),
        valid_to=date.today() + timedelta(days=365)
    )
    
    RoomRate.objects.create(
        rate_plan=rate_plan,
        room_type=room_type,
        season=season,
        single_rate=Decimal('150.00'),
        double_rate=Decimal('180.00')
    )
    
    return {
        'property': property,
        'room_type': room_type,
        'season': season,
        'rate_plan': rate_plan
    }


@pytest.mark.django_db
class TestChannelsModels:
    """Test Channels module models."""
    
    def test_create_channel(self):
        """Test creating a distribution channel."""
        channel = Channel.objects.create(
            name='Booking.com',
            code='BOOKINGCOM',
            channel_type='OTA',
            commission_percent=Decimal('15.00'),
            api_url='https://api.booking.com',
            api_key='test_key_123',
            api_secret='test_secret_456'
        )
        
        assert channel.id is not None
        assert channel.name == 'Booking.com'
        assert channel.commission_percent == Decimal('15.00')
        assert channel.is_active is True
    
    def test_channel_types(self):
        """Test different channel types."""
        ota = Channel.objects.create(name='Expedia', code='EXPEDIA', channel_type='OTA')
        gds = Channel.objects.create(name='Amadeus', code='AMADEUS', channel_type='GDS')
        direct = Channel.objects.create(name='Website', code='WEBSITE', channel_type='DIRECT')
        
        assert ota.channel_type == 'OTA'
        assert gds.channel_type == 'GDS'
        assert direct.channel_type == 'DIRECT'
    
    def test_create_property_channel(self, setup_channel_data):
        """Test connecting a property to a channel."""
        channel = Channel.objects.create(
            name='Booking.com',
            code='BOOKINGCOM',
            channel_type='OTA',
            commission_percent=Decimal('15.00')
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-12345',
            rate_plan=setup_channel_data['rate_plan'],
            rate_markup=Decimal('10.00'),
            min_availability=2,
            max_availability=10,
            sync_rates=True,
            sync_availability=True
        )
        
        assert property_channel.id is not None
        assert property_channel.property_code == 'BEACH-12345'
        assert property_channel.rate_markup == Decimal('10.00')
        assert property_channel.is_active is True
    
    def test_property_channel_unique_constraint(self, setup_channel_data):
        """Test property-channel uniqueness."""
        channel = Channel.objects.create(
            name='Booking.com',
            code='BOOKINGCOM',
            channel_type='OTA'
        )
        
        PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-001'
        )
        
        # Try to create duplicate
        with pytest.raises(Exception):
            PropertyChannel.objects.create(
                property=setup_channel_data['property'],
                channel=channel,
                property_code='BEACH-002'  # Different code but same property+channel
            )
    
    def test_room_type_mapping(self, setup_channel_data):
        """Test mapping room types to channel codes."""
        channel = Channel.objects.create(
            name='Expedia',
            code='EXPEDIA',
            channel_type='OTA'
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-EXP'
        )
        
        mapping = RoomTypeMapping.objects.create(
            property_channel=property_channel,
            room_type=setup_channel_data['room_type'],
            channel_room_code='DBL-STD-001',
            channel_room_name='Standard Double Room'
        )
        
        assert mapping.id is not None
        assert mapping.channel_room_code == 'DBL-STD-001'
        assert mapping.is_active is True
        assert str(mapping) == 'DBL -> DBL-STD-001'
    
    def test_rate_plan_mapping(self, setup_channel_data):
        """Test mapping rate plans to channel rates."""
        channel = Channel.objects.create(
            name='Booking.com',
            code='BOOKINGCOM',
            channel_type='OTA'
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-BDC'
        )
        
        mapping = RatePlanMapping.objects.create(
            property_channel=property_channel,
            rate_plan=setup_channel_data['rate_plan'],
            channel_rate_code='BAR-NR',
            channel_rate_name='Best Available - Non-Refundable'
        )
        
        assert mapping.id is not None
        assert mapping.channel_rate_code == 'BAR-NR'
        assert str(mapping) == 'BAR -> BAR-NR'
    
    def test_availability_update_lifecycle(self, setup_channel_data):
        """Test availability update from pending to confirmed."""
        channel = Channel.objects.create(
            name='Booking.com',
            code='BOOKINGCOM',
            channel_type='OTA'
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-BDC'
        )
        
        # Create pending update
        update = AvailabilityUpdate.objects.create(
            property_channel=property_channel,
            room_type=setup_channel_data['room_type'],
            date=date.today() + timedelta(days=1),
            availability=5,
            status='PENDING'
        )
        
        assert update.status == 'PENDING'
        assert update.sent_at is None
        
        # Simulate sending
        update.status = 'SENT'
        update.sent_at = timezone.now()
        update.save()
        
        assert update.status == 'SENT'
        assert update.sent_at is not None
        
        # Confirm
        update.status = 'CONFIRMED'
        update.save()
        
        assert update.status == 'CONFIRMED'
    
    def test_availability_update_failure(self, setup_channel_data):
        """Test failed availability update with error message."""
        channel = Channel.objects.create(
            name='Expedia',
            code='EXPEDIA',
            channel_type='OTA'
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-EXP'
        )
        
        update = AvailabilityUpdate.objects.create(
            property_channel=property_channel,
            room_type=setup_channel_data['room_type'],
            date=date.today() + timedelta(days=7),
            availability=3,
            status='FAILED',
            error_message='API timeout - connection refused'
        )
        
        assert update.status == 'FAILED'
        assert 'timeout' in update.error_message
    
    def test_rate_update_lifecycle(self, setup_channel_data):
        """Test rate update from pending to confirmed."""
        channel = Channel.objects.create(
            name='Booking.com',
            code='BOOKINGCOM',
            channel_type='OTA'
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-BDC'
        )
        
        # Create rate update
        update = RateUpdate.objects.create(
            property_channel=property_channel,
            room_type=setup_channel_data['room_type'],
            rate_plan=setup_channel_data['rate_plan'],
            date=date.today() + timedelta(days=5),
            rate=Decimal('199.00'),
            status='PENDING'
        )
        
        assert update.id is not None
        assert update.rate == Decimal('199.00')
        assert update.status == 'PENDING'
        
        # Send and confirm
        update.status = 'SENT'
        update.sent_at = timezone.now()
        update.save()
        
        update.status = 'CONFIRMED'
        update.save()
        
        assert update.status == 'CONFIRMED'
    
    def test_channel_reservation_received(self, setup_channel_data):
        """Test receiving a reservation from OTA."""
        channel = Channel.objects.create(
            name='Expedia',
            code='EXPEDIA',
            channel_type='OTA',
            commission_percent=Decimal('18.00')
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-EXP'
        )
        
        channel_reservation = ChannelReservation.objects.create(
            property_channel=property_channel,
            channel_booking_id='EXP-2026-123456',
            guest_name='John Smith',
            check_in_date=date.today() + timedelta(days=10),
            check_out_date=date.today() + timedelta(days=13),
            room_type_code='DBL-STD',
            rate_amount=Decimal('180.00'),
            total_amount=Decimal('540.00'),  # 3 nights
            status='RECEIVED',
            raw_data={
                'booking_id': 'EXP-2026-123456',
                'guest_email': 'john@example.com',
                'payment_method': 'credit_card'
            }
        )
        
        assert channel_reservation.id is not None
        assert channel_reservation.status == 'RECEIVED'
        assert channel_reservation.total_amount == Decimal('540.00')
        assert 'booking_id' in channel_reservation.raw_data
    
    def test_channel_reservation_processed(self, setup_channel_data):
        """Test processing OTA reservation into system reservation."""
        channel = Channel.objects.create(
            name='Booking.com',
            code='BOOKINGCOM',
            channel_type='OTA'
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-BDC'
        )
        
        channel_reservation = ChannelReservation.objects.create(
            property_channel=property_channel,
            channel_booking_id='BDC-789456123',
            guest_name='Jane Doe',
            check_in_date=date.today() + timedelta(days=15),
            check_out_date=date.today() + timedelta(days=18),
            room_type_code='DBL',
            rate_amount=Decimal('200.00'),
            total_amount=Decimal('600.00'),
            status='RECEIVED'
        )
        
        # Simulate processing
        channel_reservation.status = 'PROCESSED'
        channel_reservation.processed_at = timezone.now()
        channel_reservation.save()
        
        assert channel_reservation.status == 'PROCESSED'
        assert channel_reservation.processed_at is not None
    
    def test_channel_reservation_unique_booking_id(self, setup_channel_data):
        """Test that channel booking IDs are unique per property channel."""
        channel = Channel.objects.create(
            name='Booking.com',
            code='BOOKINGCOM',
            channel_type='OTA'
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-BDC'
        )
        
        ChannelReservation.objects.create(
            property_channel=property_channel,
            channel_booking_id='BDC-UNIQUE-001',
            guest_name='Guest 1',
            check_in_date=date.today() + timedelta(days=20),
            check_out_date=date.today() + timedelta(days=22),
            room_type_code='DBL',
            rate_amount=Decimal('180.00'),
            total_amount=Decimal('360.00')
        )
        
        # Try duplicate booking ID
        with pytest.raises(Exception):
            ChannelReservation.objects.create(
                property_channel=property_channel,
                channel_booking_id='BDC-UNIQUE-001',  # Same ID
                guest_name='Guest 2',
                check_in_date=date.today() + timedelta(days=25),
                check_out_date=date.today() + timedelta(days=27),
                room_type_code='DBL',
                rate_amount=Decimal('180.00'),
                total_amount=Decimal('360.00')
            )
    
    def test_multiple_channels_for_property(self, setup_channel_data):
        """Test property connected to multiple channels."""
        booking = Channel.objects.create(
            name='Booking.com',
            code='BOOKINGCOM',
            channel_type='OTA',
            commission_percent=Decimal('15.00')
        )
        
        expedia = Channel.objects.create(
            name='Expedia',
            code='EXPEDIA',
            channel_type='OTA',
            commission_percent=Decimal('18.00')
        )
        
        booking_pc = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=booking,
            property_code='BEACH-BDC'
        )
        
        expedia_pc = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=expedia,
            property_code='BEACH-EXP'
        )
        
        assert setup_channel_data['property'].channels.count() == 2
        assert booking_pc.channel.commission_percent == Decimal('15.00')
        assert expedia_pc.channel.commission_percent == Decimal('18.00')
    
    def test_sync_settings(self, setup_channel_data):
        """Test channel sync settings."""
        channel = Channel.objects.create(
            name='Agoda',
            code='AGODA',
            channel_type='OTA'
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-AGODA',
            sync_rates=True,
            sync_availability=True,
            sync_restrictions=False  # Don't sync min stay restrictions
        )
        
        assert property_channel.sync_rates is True
        assert property_channel.sync_availability is True
        assert property_channel.sync_restrictions is False
    
    def test_last_sync_tracking(self, setup_channel_data):
        """Test tracking last sync time."""
        channel = Channel.objects.create(
            name='HRS',
            code='HRS',
            channel_type='OTA'
        )
        
        property_channel = PropertyChannel.objects.create(
            property=setup_channel_data['property'],
            channel=channel,
            property_code='BEACH-HRS'
        )
        
        assert property_channel.last_sync is None
        
        # Simulate sync
        property_channel.last_sync = timezone.now()
        property_channel.save()
        
        assert property_channel.last_sync is not None
