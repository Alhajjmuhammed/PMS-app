import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from apps.guests.models import Guest
from apps.reservations.models import Reservation
from apps.billing.models import Folio, FolioCharge, Payment
from apps.properties.models import Property

User = get_user_model()

print("=" * 60)
print("ALL USERS")
print("=" * 60)
for u in User.objects.all().order_by('id'):
    prop = getattr(u.assigned_property, 'name', 'None') if u.assigned_property else 'None'
    print(f"  id={u.id:<3}  email={u.email:<35}  name={u.get_full_name():<20}  role={u.role:<15}  property={prop}")

print()
print("=" * 60)
print("ALL PROPERTIES")
print("=" * 60)
for p in Property.objects.all():
    print(f"  id={p.id}  name={p.name}")

print()
print("=" * 60)
print("ALL GUESTS")
print("=" * 60)
for g in Guest.objects.all().order_by('id'):
    print(f"  id={g.id:<3}  name={g.first_name} {g.last_name:<20}  email={g.email}")

print()
print("=" * 60)
print("ALL RESERVATIONS")
print("=" * 60)
for r in Reservation.objects.all().order_by('id'):
    prop = r.hotel.name if r.hotel else '?'
    print(f"  id={r.id:<3}  conf={r.confirmation_number:<25}  guest={r.guest.first_name} {r.guest.last_name:<15}  status={r.status:<12}  in={r.check_in_date}  out={r.check_out_date}  hotel={prop}")

print()
print("=" * 60)
print("ALL FOLIOS")
print("=" * 60)
for f in Folio.objects.all().order_by('id'):
    print(f"  id={f.id:<3}  {f.folio_number:<20}  status={f.status:<8}  charges={f.total_charges}  payments={f.total_payments}  balance={f.balance}")

print()
print("=" * 60)
print("ALL PAYMENTS")
print("=" * 60)
for p in Payment.objects.all().order_by('id'):
    print(f"  id={p.id:<3}  {p.payment_number:<15}  amount=${p.amount}  method={p.payment_method}  folio={p.folio.folio_number}  date={p.payment_date.date()}")
