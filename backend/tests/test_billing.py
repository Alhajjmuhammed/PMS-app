"""Tests for Billing module."""
import pytest
from decimal import Decimal
from datetime import date
from django.utils import timezone
from apps.billing.models import Folio, ChargeCode, FolioCharge, Payment
from apps.properties.models import Property
from apps.guests.models import Guest
from apps.reservations.models import Reservation


@pytest.mark.django_db
class TestBillingModels:
    """Test billing models."""
    
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
        
        # Create guest
        guest = Guest.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890'
        )
        
        # Create reservation
        reservation = Reservation.objects.create(
            hotel=property_obj,
            guest=guest,
            check_in_date=date.today(),
            check_out_date=date.today() + timezone.timedelta(days=3),
            status='CHECKED_IN',
            adults=2
        )
        
        # Create charge code
        charge_code = ChargeCode.objects.create(

            category='ROOM',
            is_taxable=True
        )
        
        return {
            'property': property_obj,
            'guest': guest,
            'reservation': reservation,
            'charge_code': charge_code
        }
    
    def test_create_folio(self, setup_data):
        """Test creating a folio."""
        folio = Folio.objects.create(
            folio_number='F001',
            guest=setup_data['guest'],
            reservation=setup_data['reservation'],
            folio_type='GUEST',
            status='OPEN'
        )
        
        assert folio.id is not None
        assert folio.guest == setup_data['guest']
        assert folio.status == 'OPEN'
        assert folio.balance == 0
    
    def test_add_charge_to_folio(self, setup_data):
        """Test adding charges to folio."""
        folio = Folio.objects.create(
            folio_number='F002',
            guest=setup_data['guest'],
            status='OPEN'
        )
        
        # Add charge
        charge = FolioCharge.objects.create(
            folio=folio,
            charge_code=setup_data['charge_code'],
            description='Room charge for 101',
            quantity=1,
            unit_price=Decimal('150.00'),
            tax_amount=Decimal('15.00')
        )
        
        folio.refresh_from_db()
        
        assert charge.amount == Decimal('150.00')
        assert folio.total_charges == Decimal('150.00')
        assert folio.balance == Decimal('165.00')
    
    def test_add_payment_to_folio(self, setup_data):
        """Test adding payment to folio."""
        folio = Folio.objects.create(
            folio_number='F003',
            guest=setup_data['guest'],
            status='OPEN'
        )
        
        # Add charge
        FolioCharge.objects.create(
            folio=folio,
            charge_code=setup_data['charge_code'],
            description='Room charge',
            quantity=1,
            unit_price=Decimal('200.00'),
            tax_amount=Decimal('20.00')
        )
        
        # Add payment
        payment = Payment.objects.create(
            folio=folio,
            payment_method='CREDIT_CARD',
            amount=Decimal('220.00'),
            reference='CC123456'
        )
        
        folio.recalculate_totals()
        
        assert folio.total_payments == Decimal('220.00')
        assert folio.balance == Decimal('0.00')
    
    def test_folio_settlement(self, setup_data):
        """Test settling a folio."""
        folio = Folio.objects.create(
            folio_number='F004',
            guest=setup_data['guest'],
            status='OPEN'
        )
        
        # Add charges and payment
        FolioCharge.objects.create(
            folio=folio,
            charge_code=setup_data['charge_code'],
            description='Charge',
            quantity=1,
            unit_price=Decimal('100.00'),
            tax_amount=Decimal('10.00')
        )
        
        Payment.objects.create(
            folio=folio,
            payment_method='CASH',
            amount=Decimal('110.00')
        )
        
        folio.recalculate_totals()
        
        # Settle folio
        if folio.balance == 0:
            folio.status = 'SETTLED'
            folio.close_date = date.today()
            folio.save()
        
        assert folio.status == 'SETTLED'
        assert folio.close_date is not None
    
    def test_multiple_charges(self, setup_data):
        """Test multiple charges on folio."""
        folio = Folio.objects.create(
            folio_number='F005',
            guest=setup_data['guest'],
            status='OPEN'
        )
        
        # Room charge
        FolioCharge.objects.create(
            folio=folio,
            charge_code=setup_data['charge_code'],
            description='Room Night 1',
            quantity=1,
            unit_price=Decimal('100.00'),
            tax_amount=Decimal('10.00')
        )
        
        # Minibar charge
        minibar_code = ChargeCode.objects.create(
            code='MINIBAR',
            name='Minibar',
            category='MINIBAR'
        )
        
        FolioCharge.objects.create(
            folio=folio,
            charge_code=minibar_code,
            description='Minibar items',
            quantity=1,
            unit_price=Decimal('25.00'),
            tax_amount=Decimal('2.50')
        )
        
        folio.refresh_from_db()
        
        assert folio.total_charges == Decimal('125.00')
        assert folio.total_taxes == Decimal('12.50')
        assert folio.balance == Decimal('137.50')
