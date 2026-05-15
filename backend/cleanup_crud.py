#!/usr/bin/env python
"""Clean up CRUD test data from previous failed runs"""
import django, os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, '/home/easyfix/Documents/PMS-app/backend')
django.setup()

from apps.guests.models import Guest
from apps.reservations.models import Reservation
from apps.billing.models import Folio
from apps.frontdesk.models import CheckIn, CheckOut
from apps.rooms.models import Room

# Delete in dependency order
test_guests = Guest.objects.filter(email__icontains='crud')
test_res = Reservation.objects.filter(guest__in=test_guests)
test_check_ins = CheckIn.objects.filter(reservation__in=test_res)
test_folios = Folio.objects.filter(guest__in=test_guests)
test_rooms = Room.objects.filter(room_number__icontains='CRUD')

r_co = CheckOut.objects.filter(check_in__in=test_check_ins).delete()
print("Deleted test check-outs:", r_co)
r_ci = test_check_ins.delete()
print("Deleted test check-ins:", r_ci)
r_f = test_folios.delete()
print("Deleted test folios:", r_f)
r_r = test_res.delete()
print("Deleted test reservations:", r_r)
r_g = test_guests.delete()
print("Deleted test guests:", r_g)
r_rm = test_rooms.delete()
print("Deleted test rooms:", r_rm)

# Check state
print("Guests for Lukman:", Guest.objects.filter(home_property_id=2).count())
print("Reservations for Lukman:", Reservation.objects.filter(hotel_id=2).count())
print("Folios:", Folio.objects.count())
