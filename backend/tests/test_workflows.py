"""
End-to-End Workflow Tests
Complete business process testing from reservation to checkout
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

from apps.reservations.models import Reservation
from apps.guests.models import Guest
from apps.properties.models import Property
from apps.rooms.models import Room, RoomType
from apps.rates.models import RatePlan, RoomRate
from apps.frontdesk.models import CheckIn, CheckOut
from apps.billing.models import Folio, FolioCharge, Payment, ChargeCode
from apps.housekeeping.models import HousekeepingTask
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestEndToEndWorkflows:
    """Test complete guest journey workflows."""
    
    @pytest.fixture
    def setup_property(self):
        """Create property with rooms and rates."""
        # Property
        property_obj = Property.objects.create(
            name='Grand Hotel',
            code='GRAND',
            total_rooms=50,
            address='456 Main St',
            city='New York',
            country='USA'
        )
        
        # Room type
        room_type = RoomType.objects.create(
            hotel=property_obj,
            name='Deluxe King',
            code='DLX-K',
            max_occupancy=2,
            base_rate=Decimal('250.00')
        )
        
        # Room
        room = Room.objects.create(
            hotel=property_obj,
            room_number='301',
            room_type=room_type,
            status='CLEAN',
            is_active=True
        )
        
        # Rate plan
        rate_plan = RatePlan.objects.create(
            property=property_obj,
            name='Best Available Rate',
            code='BAR',
            rate_type='BAR',
            min_nights=1,
            is_active=True
        )
        
        # Room rate
        room_rate = RoomRate.objects.create(
            rate_plan=rate_plan,
            room_type=room_type,
            single_rate=Decimal('200.00'),
            double_rate=Decimal('250.00'),
            extra_adult=Decimal('50.00'),
            extra_child=Decimal('25.00')
        )
        
        # Charge codes
        room_charge = ChargeCode.objects.create(
            code='ROOM',
            name='Room Charge',
            category='ROOM',
            is_taxable=True
        )
        
        fb_charge = ChargeCode.objects.create(
            code='FB',
            name='Food & Beverage',
            category='FOOD',
            is_taxable=True
        )
        
        # Users
        front_desk = User.objects.create_user(
            email='frontdesk@grandhotel.com',
            password='test123',
            first_name='Front',
            last_name='Desk',
            role='STAFF'
        )
        
        housekeeper = User.objects.create_user(
            email='housekeeper@grandhotel.com',
            password='test123',
            first_name='House',
            last_name='Keeper',
            role='STAFF'
        )
        
        return {
            'property': property_obj,
            'room_type': room_type,
            'room': room,
            'rate_plan': rate_plan,
            'room_rate': room_rate,
            'room_charge': room_charge,
            'fb_charge': fb_charge,
            'front_desk': front_desk,
            'housekeeper': housekeeper
        }
    
    def test_complete_reservation_to_checkout_workflow(self, setup_property):
        """
        Test complete workflow:
        1. Create guest
        2. Make reservation
        3. Check-in
        4. Post charges
        5. Housekeeping service
        6. Payment
        7. Check-out
        """
        # Step 1: Create guest
        guest = Guest.objects.create(
            first_name='John',
            last_name='Traveler',
            email='john.traveler@example.com',
            phone='+1234567890',
            nationality='USA'
        )
        assert guest.id is not None
        
        # Step 2: Create reservation
        check_in_date = date.today()
        check_out_date = check_in_date + timedelta(days=3)
        
        reservation = Reservation.objects.create(
            hotel=setup_property['property'],
            guest=guest,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=2,
            children=0,
            status='CONFIRMED',
            total_amount=Decimal('750.00')  # 250 * 3 nights
        )
        assert reservation.status == 'CONFIRMED'
        
        # Step 3: Check-in
        check_in = CheckIn.objects.create(
            reservation=reservation,
            room=setup_property['room'],
            guest=guest,
            expected_check_out=check_out_date,
            registration_number='REG-20260109-001',
            key_card_number='KEY-301-001',
            keys_issued=2,
            deposit_amount=Decimal('100.00'),
            deposit_method='CREDIT_CARD',
            checked_in_by=setup_property['front_desk']
        )
        
        # Update reservation and room status
        reservation.status = 'CHECKED_IN'
        reservation.save()
        
        setup_property['room'].status = 'OCC'
        setup_property['room'].save()
        
        assert check_in.id is not None
        assert reservation.status == 'CHECKED_IN'
        assert setup_property['room'].status == 'OCC'
        
        # Step 4: Create folio and post charges
        folio = Folio.objects.create(
            folio_number='FOL-001',
            reservation=reservation,
            guest=guest,
            status='OPEN'
        )
        
        # Post room charges for each night
        for night in range(3):
            charge_date = check_in_date + timedelta(days=night)
            FolioCharge.objects.create(
                folio=folio,
                charge_code=setup_property['room_charge'],
                description=f'Room 301 - Night {night + 1}',
                quantity=1,
                unit_price=Decimal('250.00'),
                tax_amount=Decimal('25.00'),
                charge_date=charge_date
            )
        
        # Post F&B charge
        FolioCharge.objects.create(
            folio=folio,
            charge_code=setup_property['fb_charge'],
            description='Restaurant - Dinner',
            quantity=1,
            unit_price=Decimal('85.00'),
            tax_amount=Decimal('8.50')
        )
        
        folio.refresh_from_db()
        assert folio.charges.count() == 4
        assert folio.total_charges == Decimal('835.00')  # 750 + 85
        
        # Step 5: Housekeeping service
        housekeeping_task = HousekeepingTask.objects.create(
            room=setup_property['room'],
            task_type='CLEANING',
            priority='NORMAL',
            status='PENDING',
            scheduled_date=check_in_date,
            created_by=setup_property['front_desk']
        )
        
        # Assign and complete task
        housekeeping_task.assigned_to = setup_property['housekeeper']
        housekeeping_task.status = 'IN_PROGRESS'
        housekeeping_task.save()
        
        housekeeping_task.status = 'COMPLETED'
        housekeeping_task.completed_at = timezone.now()
        housekeeping_task.save()
        
        assert housekeeping_task.status == 'COMPLETED'
        
        # Step 6: Process payment
        payment = Payment.objects.create(
            folio=folio,
            amount=Decimal('935.00'),  # Including taxes
            payment_method='CREDIT_CARD',
            reference='CC-AUTH-12345',
            notes='Visa ending 4242'
        )
        
        folio.refresh_from_db()
        assert payment.amount == Decimal('935.00')
        
        # Step 7: Check-out
        check_out = CheckOut.objects.create(
            check_in=check_in,
            total_charges=Decimal('835.00'),
            total_payments=Decimal('935.00'),
            balance=Decimal('-100.00'),  # Refund deposit
            keys_returned=2,
            rating=5,
            feedback='Excellent stay!',
            checked_out_by=setup_property['front_desk']
        )
        
        # Update statuses
        reservation.status = 'CHECKED_OUT'
        reservation.save()
        
        folio.status = 'CLOSED'
        folio.save()
        
        setup_property['room'].status = 'VD'  # Vacant Dirty
        setup_property['room'].save()
        
        assert check_out.id is not None
        assert reservation.status == 'CHECKED_OUT'
        assert folio.status == 'CLOSED'
        assert setup_property['room'].status == 'VD'
        assert check_out.balance == Decimal('-100.00')
    
    def test_walk_in_guest_workflow(self, setup_property):
        """Test walk-in guest without prior reservation."""
        # Create walk-in guest
        guest = Guest.objects.create(
            first_name='Jane',
            last_name='Walker',
            email='jane.walker@example.com',
            phone='+9876543210'
        )
        
        # Create reservation on the spot
        check_in_date = date.today()
        check_out_date = date.today() + timedelta(days=1)
        
        reservation = Reservation.objects.create(
            hotel=setup_property['property'],
            guest=guest,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=1,
            children=0,
            status='CONFIRMED',
            total_amount=Decimal('200.00')
        )
        
        # Immediate check-in
        check_in = CheckIn.objects.create(
            reservation=reservation,
            room=setup_property['room'],
            guest=guest,
            expected_check_out=check_out_date,
            registration_number=f'WALKIN-{timezone.now().strftime("%Y%m%d%H%M%S")}',
            key_card_number='KEY-301-002',
            deposit_amount=Decimal('50.00'),
            deposit_method='CASH',
            checked_in_by=setup_property['front_desk']
        )
        
        reservation.status = 'CHECKED_IN'
        reservation.save()
        
        assert check_in.id is not None
    
    def test_early_checkout_workflow(self, setup_property):
        """Test early checkout with adjusted charges."""
        guest = Guest.objects.create(
            first_name='Early',
            last_name='Bird',
            email='early@example.com',
            phone='+1111111111'
        )
        
        # 5-night reservation
        reservation = Reservation.objects.create(
            hotel=setup_property['property'],
            guest=guest,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=5),
            adults=2,
            status='CONFIRMED',
            total_amount=Decimal('1250.00')  # 250 * 5
        )
            
        
        check_in = CheckIn.objects.create(
            reservation=reservation,
            room=setup_property['room'],
            guest=guest,
            expected_check_out=date.today() + timedelta(days=5),
            registration_number='REG-EARLY-001',
            checked_in_by=setup_property['front_desk']
        )
        
        reservation.status = 'CHECKED_IN'
        reservation.save()
        
        # Guest checks out after only 2 nights
        folio = Folio.objects.create(
            folio_number='FOL-EARLY',
            reservation=reservation,
            guest=guest,
            status='OPEN'
        )
        
        # Only charge for 2 nights
        for night in range(2):
            FolioCharge.objects.create(
                folio=folio,
                charge_code=setup_property['room_charge'],
                description=f'Room charge - Night {night + 1}',
                quantity=1,
                unit_price=Decimal('250.00'),
                tax_amount=Decimal('25.00')
            )
        
        folio.refresh_from_db()
        assert folio.total_charges == Decimal('500.00')  # Only 2 nights
        
        # Process payment
        Payment.objects.create(
            folio=folio,
            amount=Decimal('550.00'),  # Including taxes
            payment_method='CREDIT_CARD'
        )
        
        # Early checkout
        check_out = CheckOut.objects.create(
            check_in=check_in,
            total_charges=Decimal('500.00'),
            total_payments=Decimal('550.00'),
            balance=Decimal('0.00'),
            notes='Early departure - guest request',
            checked_out_by=setup_property['front_desk']
        )
        
        reservation.status = 'CHECKED_OUT'
        reservation.save()
        
        assert check_out.id is not None
        assert reservation.status == 'CHECKED_OUT'
    
    def test_split_billing_workflow(self, setup_property):
        """Test split billing with multiple payment methods."""
        guest = Guest.objects.create(
            first_name='Business',
            last_name='Traveler',
            email='business@example.com',
            phone='+2222222222'
        )
        
        reservation = Reservation.objects.create(
            hotel=setup_property['property'],
            guest=guest,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=2),
            adults=1,
            status='CONFIRMED',
            total_amount=Decimal('500.00')
        )
        
        check_in = CheckIn.objects.create(
            reservation=reservation,
            room=setup_property['room'],
            guest=guest,
            expected_check_out=date.today() + timedelta(days=2),
            registration_number='REG-SPLIT-001',
            checked_in_by=setup_property['front_desk']
        )
        
        reservation.status = 'CHECKED_IN'
        reservation.save()
        
        # Single folio with all charges
        folio = Folio.objects.create(
            folio_number='FOL-SPLIT',
            reservation=reservation,
            guest=guest,
            status='OPEN'
        )
        
        # Post room charges
        for night in range(2):
            FolioCharge.objects.create(
                folio=folio,
                charge_code=setup_property['room_charge'],
                description=f'Room charge - Night {night + 1}',
                quantity=1,
                unit_price=Decimal('250.00'),
                tax_amount=Decimal('25.00')
            )
        
        # Post F&B charge
        FolioCharge.objects.create(
            folio=folio,
            charge_code=setup_property['fb_charge'],
            description='Restaurant',
            quantity=1,
            unit_price=Decimal('50.00'),
            tax_amount=Decimal('5.00')
        )
        
        folio.refresh_from_db()
        
        # Split payment: company pays room, guest pays incidentals
        payment1 = Payment.objects.create(
            folio=folio,
            amount=Decimal('550.00'),
            payment_method='COMPANY_ACCOUNT',
            reference='COMP-001'
        )
        
        payment2 = Payment.objects.create(
            folio=folio,
            amount=Decimal('55.00'),
            payment_method='CREDIT_CARD',
            reference='CC-456'
        )
        
        # Verify split payments exist
        assert Payment.objects.filter(folio=folio).count() == 2
        assert payment1.payment_method == 'COMPANY_ACCOUNT'
        assert payment2.payment_method == 'CREDIT_CARD'
