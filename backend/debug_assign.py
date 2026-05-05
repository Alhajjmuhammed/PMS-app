#!/usr/bin/env python
"""Debug script: test maintenance assign isolation."""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.properties.models import Property
from apps.maintenance.models import MaintenanceRequest
from apps.accounts.models import User
from apps.rooms.models import Room, RoomType
from rest_framework.test import APIClient
import uuid

ha = Property.objects.create(name='HA_DBG', code='HAD-'+uuid.uuid4().hex[:6], address='1st', phone='111', city='X', country='US')
hb = Property.objects.create(name='HB_DBG', code='HBD-'+uuid.uuid4().hex[:6], address='2nd', phone='222', city='Y', country='US')

wa = User.objects.create_user(
    email='maint_a_'+uuid.uuid4().hex[:6]+'@x.com', password='pass',
    role='MAINTENANCE', assigned_property=ha, is_active=True
)

rt = RoomType.objects.create(hotel=hb, name='STD', code='SDX'+uuid.uuid4().hex[:4], base_rate=100)
room = Room.objects.create(hotel=hb, room_type=rt, room_number='R'+uuid.uuid4().hex[:4], status='VC', fo_status='VACANT')
maint = MaintenanceRequest.objects.create(
    property=hb, room=room, request_number='MNT-'+uuid.uuid4().hex[:8].upper(),
    title='Test', description='Desc', priority='HIGH', status='PENDING'
)

client = APIClient()
client.force_authenticate(user=wa)
r = client.post(f'/api/v1/maintenance/{maint.id}/assign/', {'assigned_to': wa.id}, format='json')
print(f'URL: /api/v1/maintenance/{maint.id}/assign/')
print(f'Status: {r.status_code}')
print(f'Data: {r.data}')
