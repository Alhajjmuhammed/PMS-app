#!/usr/bin/env python
"""
Seed demo billing data for H1 (Grand Hotel Demo, property=1) so the night audit
shows non-zero revenue in the UI.
Run: DJANGO_SETTINGS_MODULE=config.settings.development venv/bin/python seed_demo_data.py
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.reservations.models import Reservation
from apps.rooms.models import Room
from apps.guests.models import Guest
from apps.billing.models import Folio, FolioCharge, ChargeCode, Payment
from apps.properties.models import Property

today = timezone.now().date()
User = get_user_model()

manager = User.objects.get(email='manager@hotel.com')
prop = Property.objects.get(id=1)
print(f"Property: {prop.name}")

# Print field names for debugging
print("ChargeCode fields:", [f.name for f in ChargeCode._meta.concrete_fields])
print("FolioCharge fields:", [f.name for f in FolioCharge._meta.concrete_fields])
print("Payment fields:", [f.name for f in Payment._meta.concrete_fields])

# Get any guest
guest = Guest.objects.first()
if not guest:
    guest = Guest.objects.create(
        first_name='John', last_name='Demo', email='john@demo.com', phone='+1000000001'
    )
print(f"Guest: {guest} (id={guest.id})")

# Get or create a charge code – ChargeCode is global (no hotel/property FK)
cc, _ = ChargeCode.objects.get_or_create(
    code='ROOM',
    defaults={'name': 'Room Rate', 'category': 'ROOM', 'default_amount': Decimal('150.00'), 'is_active': True}
)
print(f"ChargeCode: {cc}")

# Create a CHECKED_IN reservation
res = Reservation.objects.create(
    hotel=prop,
    guest=guest,
    check_in_date=today,
    check_out_date=today,
    status='CHECKED_IN',
    adults=1,
    created_by=manager,
)
print(f"Reservation #{res.id}  conf={res.confirmation_number}")

# Create folio  
folio = Folio.objects.create(
    reservation=res,
    guest=guest,
    folio_number=f"F-SEED{today.strftime('%Y%m%d')}",
    status='OPEN',
)
print(f"Folio: {folio.folio_number}")

# Create 2 room charges – try different field combos
try:
    fc1 = FolioCharge.objects.create(
        folio=folio, charge_code=cc,
        description='Room Rate Night 1',
        unit_price=Decimal('150.00'), quantity=1, charge_date=today,
    )
    fc2 = FolioCharge.objects.create(
        folio=folio, charge_code=cc,
        description='Room Rate Night 2',
        unit_price=Decimal('150.00'), quantity=1, charge_date=today,
    )
    print(f"Charges: ${fc1.unit_price} + ${fc2.unit_price}")
except Exception as e:
    print(f"FolioCharge create failed: {e}")

# Create payment
try:
    pay = Payment.objects.create(
        folio=folio,
        payment_method='CREDIT_CARD',
        amount=Decimal('300.00'),
        payment_date=timezone.now(),
        received_by=manager,
    )
    print(f"Payment: ${pay.amount}  #{pay.payment_number}")
except Exception as e:
    print(f"Payment create failed: {e}")

folio.recalculate_totals()
folio.refresh_from_db()
print(f"\nFolio summary: charges={folio.total_charges}  payments={folio.total_payments}  balance={folio.balance}")
print("DONE")
