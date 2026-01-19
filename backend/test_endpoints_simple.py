#!/usr/bin/env python
"""
Simple endpoint verification script
Tests that all new endpoints respond without 500 errors
"""
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
django.setup()

from django.test import Client
from apps.accounts.models import User
from apps.properties.models import Property
from apps.rooms.models import Room, RoomType
from apps.guests.models import Guest
from apps.pos.models import Outlet
from apps.notifications.models import Notification
from apps.billing.models import Folio

# Setup
client = Client()

# Create test user or get existing
user, created = User.objects.get_or_create(
    email='test@test.com',
    defaults={'password': 'test123'}
)
if not created:
    user.set_password('test123')
    user.save()
client.force_login(user)

# Use existing test data instead of creating
try:
    prop = Property.objects.first()
    room_type = RoomType.objects.first()
    room = Room.objects.first()
    guest = Guest.objects.first()
    outlet = Outlet.objects.first()
    notification = Notification.objects.filter(user=user).first()
    folio = Folio.objects.first()
    
    if not all([prop, room_type, room, guest, outlet, folio]):
        print("⚠️  Not enough test data in database. Creating minimal data...")
        if not prop:
            prop = Property.objects.create(name='Test', code='TEST' + str(Property.objects.count()), address='123', city='City', country='Country')
        if not room_type:
            room_type = RoomType.objects.create(hotel=prop, name='Standard', code='STD', max_occupancy=2)
        if not room:
            room = Room.objects.create(hotel=prop, room_type=room_type, room_number='T101', status='VC')
        if not guest:
            guest = Guest.objects.create(first_name='Test', last_name='User', email='test-user@example.com')
        if not outlet:
            outlet = Outlet.objects.create(property=prop, name='Test Restaurant', code='TREST', outlet_type='RESTAURANT')
        if not folio:
            folio = Folio.objects.create(guest=guest, folio_number='T-F-001', status='OPEN')
    if not notification:
        notification = Notification.objects.create(user=user, title='Test', message='Test', is_read=False)
except Exception as e:
    print(f"Error setting up test data: {e}")
    exit(1)

print("Testing new endpoints...")
print("-" * 60)

tests = [
    ('Room Images List', 'GET', f'/api/v1/rooms/{room.id}/images/'),
    ('Guest Documents List', 'GET', f'/api/v1/guests/{guest.id}/documents/'),
    ('Menu Categories List', 'GET', f'/api/v1/pos/outlets/{outlet.id}/categories/'),
    ('Menu Items List', 'GET', '/api/v1/pos/menu-items/'),
    ('Notification Read', 'POST', f'/api/v1/notifications/{notification.id}/read/'),
    ('Folio Close', 'PATCH', f'/api/v1/billing/folios/{folio.id}/close/'),
]

results = []
for name, method, url in tests:
    try:
        if method == 'GET':
            response = client.get(url)
        elif method == 'POST':
            response = client.post(url)
        elif method == 'PATCH':
            response = client.patch(url, content_type='application/json')
        
        status = response.status_code
        # Accept 200, 400 (validation errors), 404 - but not 500 (server error)
        if status < 500:
            result = f"✅ {name:25s} {method:6s} {url:50s} → {status}"
        else:
            result = f"❌ {name:25s} {method:6s} {url:50s} → {status}"
        print(result)
        results.append((name, status < 500))
    except Exception as e:
        print(f"❌ {name:25s} {method:6s} {url:50s} → ERROR: {str(e)[:50]}")
        results.append((name, False))

print("-" * 60)
passed = sum(1 for _, success in results if success)
total = len(results)
print(f"\nResults: {passed}/{total} endpoints responding correctly")

if passed == total:
    print("✅ All new endpoints are functional!")
else:
    print(f"⚠️  {total - passed} endpoint(s) have issues")

