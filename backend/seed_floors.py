#!/usr/bin/env python3
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.properties.models import Property, Building, Floor

prop = Property.objects.first()
print(f"Property: {prop.id} - {prop.name}")

building, created = Building.objects.get_or_create(
    property=prop,
    name='Main Building',
    defaults={'code': 'MAIN', 'floors': 15}
)
print(f"Building: {building.id} - {building.name} (created={created})")

# Remove ALL existing floors to avoid duplicates
deleted, _ = Floor.objects.filter(building=building).delete()
print(f"Deleted {deleted} existing floors")

floor_names = [
    'Ground Floor', 'First Floor', 'Second Floor', 'Third Floor', 'Fourth Floor',
    'Fifth Floor', 'Sixth Floor', 'Seventh Floor', 'Eighth Floor', 'Ninth Floor',
    'Tenth Floor', 'Eleventh Floor', 'Twelfth Floor', 'Thirteenth Floor', 'Fourteenth Floor',
]
for i, name in enumerate(floor_names):
    Floor.objects.create(building=building, number=i, name=name)

print(f"\nCreated {Floor.objects.filter(building=building).count()} floors:")
for f in Floor.objects.filter(building=building).order_by('number'):
    print(f"  id={f.id}  Floor {f.number} — {f.name}")
