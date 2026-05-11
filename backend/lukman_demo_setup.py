"""
Complete demo setup for Lukman hotel night audit test.
This script:
1. Resets passwords for Lukman users
2. Creates a fresh CHECKED_IN reservation for today
3. Adds room charges (3 nights x $99) to the folio
4. Creates one CONFIRMED reservation that will become a NO_SHOW during audit
5. Cleans old night audit records for Lukman
6. Gets fresh login tokens
Run: DJANGO_SETTINGS_MODULE=config.settings.development venv/bin/python lukman_demo_setup.py
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token

from apps.reservations.models import Reservation
from apps.rooms.models import Room, RoomType
from apps.guests.models import Guest
from apps.billing.models import Folio, FolioCharge, ChargeCode, Payment
from apps.properties.models import Property
from apps.reports.models import NightAudit, AuditLog

today = timezone.now().date()
User = get_user_model()

prop = Property.objects.get(id=2)   # Lukman hotel
print(f"\n{'='*60}")
print(f"  LUKMAN HOTEL DEMO SETUP")
print(f"  Property: {prop.name} (id={prop.id})")
print(f"  Today: {today}")
print(f"{'='*60}\n")

# ── 1. Reset passwords & create tokens for Lukman users ──────────────────────
NEW_PASSWORD = "Lukman@2026"
lukman_users = User.objects.filter(assigned_property=prop)
print("STEP 1 ─ Reset passwords for all Lukman users")
for u in lukman_users:
    u.set_password(NEW_PASSWORD)
    u.save()
    tok, _ = Token.objects.get_or_create(user=u)
    print(f"  ✓ {u.get_full_name():<20}  role={u.role:<15}  email={u.email:<35}  token={tok.key}")

# Get the admin/manager token for use below
admin_user = User.objects.get(email='mn@gmail.com')
admin_token = Token.objects.get(user=admin_user).key

manager_user = User.objects.get(email='alhajjmuhammed@gmail.com')
manager_token = Token.objects.get(user=manager_user).key

frontdesk_user = User.objects.get(email='fr@gmail.com')
frontdesk_token = Token.objects.get(user=frontdesk_user).key

# ── 2. Clean up old night audits for Lukman ──────────────────────────────────
print("\nSTEP 2 ─ Clean old night audits for Lukman")
old_audits = NightAudit.objects.filter(property=prop)
count = old_audits.count()
AuditLog.objects.filter(night_audit__in=old_audits).delete()
old_audits.delete()
print(f"  ✓ Deleted {count} old audit record(s)")

# ── 3. Get guest ─────────────────────────────────────────────────────────────
guest = Guest.objects.get(id=43)  # Moh'd Juma
print(f"\nSTEP 3 ─ Guest: {guest.first_name} {guest.last_name} (id={guest.id})")

# ── 4. Get room 1 (Delux King at Lukman, $99/night) ──────────────────────────
room = Room.objects.get(hotel=prop, room_number='1')
print(f"STEP 4 ─ Room: {room.room_number} ({room.room_type}) — rate: $99/night")

# ── 5. Get or create charge code ─────────────────────────────────────────────
cc_room, _ = ChargeCode.objects.get_or_create(
    code='ROOM', defaults={'name':'Room Charge','category':'ROOM','default_amount':Decimal('99.00'),'is_active':True}
)
cc_fb, _ = ChargeCode.objects.get_or_create(
    code='FOOD', defaults={'name':'Food & Beverage','category':'FOOD','default_amount':Decimal('30.00'),'is_active':True}
)
print(f"\nSTEP 5 ─ Charge codes ready: ROOM ($99), FOOD ($30)")

# ── 6. Delete existing seed reservation if any ───────────────────────────────
Reservation.objects.filter(confirmation_number__startswith='LKY_DEMO_').delete()

# ── 7. Create a CHECKED_IN reservation for today (guest checked in) ──────────
print(f"\nSTEP 6 ─ Creating CHECKED_IN reservation for today ({today})")
res_checkin = Reservation.objects.create(
    hotel=prop,
    guest=guest,
    check_in_date=today,
    check_out_date=today,   # checking out today
    status='CHECKED_IN',
    adults=2,
    created_by=admin_user,
    total_amount=Decimal('297.00'),  # 3 nights x $99
)
# Override the auto-generated confirmation number
res_checkin.confirmation_number = 'LKY_DEMO_CHECKIN_TODAY'
res_checkin.save()
print(f"  ✓ Reservation #{res_checkin.id}  conf={res_checkin.confirmation_number}")
print(f"    Guest: {guest.first_name} {guest.last_name}")
print(f"    Check-in: {today}  Check-out: {today}")
print(f"    Status: {res_checkin.status}")

# Create folio for this reservation
folio = Folio.objects.create(
    reservation=res_checkin,
    guest=guest,
    folio_number=f"LKY-DEMO-{today.strftime('%Y%m%d')}",
    status='OPEN',
)
print(f"  ✓ Folio created: {folio.folio_number}")

# Add 3 nights of room charges
from datetime import timedelta
for night, offset in enumerate([2, 1, 0], start=1):
    charge_date = today - timedelta(days=offset)
    FolioCharge.objects.create(
        folio=folio, charge_code=cc_room,
        description=f'Room Rate Night {night} — Room {room.room_number}',
        unit_price=Decimal('99.00'), quantity=1, charge_date=charge_date,
    )
    print(f"  ✓ Room charge night {night}: $99 on {charge_date}")

# Add food charge
FolioCharge.objects.create(
    folio=folio, charge_code=cc_fb,
    description='Breakfast × 2 guests',
    unit_price=Decimal('30.00'), quantity=2, charge_date=today,
)
print(f"  ✓ F&B charge: $30 × 2 = $60 (breakfast for 2)")

# Add a partial payment (guest paid a deposit upfront)
pay = Payment.objects.create(
    folio=folio,
    payment_method='CASH',
    amount=Decimal('150.00'),
    received_by=frontdesk_user,
    reference='Advance deposit at check-in',
)
print(f"  ✓ Payment received: ${pay.amount} CASH (deposit)")

folio.recalculate_totals()
folio.refresh_from_db()
print(f"\n  ═══════════════════════════════════")
print(f"  FOLIO SUMMARY — {folio.folio_number}")
print(f"  Room charges (3 nights × $99): $297.00")
print(f"  F&B charges  (breakfast × 2):  $60.00")
print(f"  ─────────────────────────────────")
print(f"  Total charges:  ${folio.total_charges}")
print(f"  Payments made:  ${folio.total_payments}")
print(f"  BALANCE DUE:    ${folio.balance}")
print(f"  ═══════════════════════════════════")

# ── 8. Create a CONFIRMED reservation that will be a NO_SHOW ─────────────────
print(f"\nSTEP 7 ─ Creating a CONFIRMED reservation (will become NO_SHOW during audit)")
res_noshow = Reservation.objects.create(
    hotel=prop,
    guest=guest,
    check_in_date=today,
    check_out_date=today,
    status='CONFIRMED',   # confirmed but never checked in — night audit will catch this
    adults=1,
    created_by=admin_user,
    total_amount=Decimal('99.00'),
)
res_noshow.confirmation_number = 'LKY_DEMO_NOSHOW'
res_noshow.save()
print(f"  ✓ Reservation #{res_noshow.id}  conf={res_noshow.confirmation_number}")
print(f"    Status: CONFIRMED — did not check in — audit will mark as NO_SHOW")

# ── 9. Print summary ──────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"  SETUP COMPLETE!")
print(f"{'='*60}")
print(f"\n  LUKMAN HOTEL LOGIN DETAILS:")
print(f"  Password for ALL users: {NEW_PASSWORD}")
print(f"")
print(f"  Admin  (mn@gmail.com):             token = {admin_token}")
print(f"  Manager (alhajjmuhammed@gmail.com): token = {manager_token}")
print(f"  FrontDesk (fr@gmail.com):           token = {frontdesk_token}")
print(f"\n  WHAT EXISTS NOW IN LUKMAN:")
print(f"  • 1 guest checked in today — Moh'd Juma — Room 1")
print(f"  • Folio with $357 charges (3 nights room + breakfast)")
print(f"  • $150 deposit already paid — $207 still owed")
print(f"  • 1 no-show reservation (confirmed but never arrived)")
print(f"\n  WHAT NIGHT AUDIT WILL DO:")
print(f"  Step 1: Mark the CONFIRMED reservation → NO_SHOW")
print(f"  Step 2: Post tonight's room rate ($99) for Moh'd Juma")
print(f"  Step 3: Check departures — warn if balance > $0")
print(f"  Step 4: Verify all folios")
print(f"  Step 5: Calculate total revenue")
print(f"")
print(f"  API Base: http://localhost:8000")
print(f"  UI:       http://localhost:3000/night-audit")
print(f"")
