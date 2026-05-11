#!/usr/bin/env python3
"""Fix assigned_property for all users and check room types."""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, '/home/easyfix/Documents/PMS-app/backend')
django.setup()

from apps.accounts.models import User
from apps.properties.models import Property
from apps.rooms.models import RoomType

props = list(Property.objects.all())
print(f"Properties in DB: {len(props)}")
for p in props:
    print(f"  [{p.id}] {p.name}")

users = list(User.objects.all())
print(f"\nUsers in DB: {len(users)}")
for u in users:
    print(f"  [{u.id}] {u.email} ({u.role}) assigned_property={u.assigned_property_id}")

if props:
    # Find the property that has room types
    prop_with_types = Property.objects.filter(room_types__isnull=False).first()
    if prop_with_types:
        print(f"\nProperty with room types: [{prop_with_types.id}] {prop_with_types.name}")
        # Move admin@hotel.com to the property that has room types
        try:
            admin = User.objects.get(email='admin@hotel.com')
            if admin.assigned_property_id != prop_with_types.id:
                admin.assigned_property = prop_with_types
                admin.save(update_fields=['assigned_property'])
                print(f"  FIXED: admin@hotel.com moved to property [{prop_with_types.id}] {prop_with_types.name}")
            else:
                print(f"  admin@hotel.com already on property [{prop_with_types.id}]")
        except User.DoesNotExist:
            print("  admin@hotel.com not found")
    else:
        print("\nNo room types in DB yet - create some first")
else:
    print("\nERROR: No properties found!")

room_types = list(RoomType.objects.all())
print(f"\nRoom Types in DB: {len(room_types)}")
for rt in room_types:
    print(f"  [{rt.id}] {rt.name} (code={rt.code}, hotel_id={rt.hotel_id})")

print("\nDone.")
