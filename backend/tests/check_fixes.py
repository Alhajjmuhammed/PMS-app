"""Quick sanity check for isolation fixes (no pytest overhead)."""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

# Check WalkIn model fields
from apps.frontdesk.models import WalkIn
fields = [f.name for f in WalkIn._meta.get_fields() if not f.is_relation or f.many_to_one or f.one_to_one]
print("WalkIn fields:", sorted(fields))

# Check WalkIn has 'property' not 'room'
assert hasattr(WalkIn, 'property_id') or 'property' in [f.name for f in WalkIn._meta.fields], "WalkIn missing 'property' field!"
print("✓ WalkIn has 'property' FK")

has_room = any(f.name == 'room' for f in WalkIn._meta.fields)
print(f"  WalkIn has 'room' field: {has_room} (should be False)")

# Check AmenityInventoryDetailView permission
from api.v1.housekeeping.views import AmenityInventoryDetailView, LinenInventoryDetailView
from api.permissions import IsHousekeepingStaff

amenity_detail_perms = [p.__name__ if hasattr(p, '__name__') else str(p) for p in AmenityInventoryDetailView.permission_classes]
linen_detail_perms = [p.__name__ if hasattr(p, '__name__') else str(p) for p in LinenInventoryDetailView.permission_classes]

print(f"\nAmenityInventoryDetailView permissions: {amenity_detail_perms}")
print(f"LinenInventoryDetailView permissions: {linen_detail_perms}")

assert 'IsHousekeepingStaff' in str(amenity_detail_perms), f"AmenityInventoryDetailView should use IsHousekeepingStaff, got: {amenity_detail_perms}"
assert 'IsHousekeepingStaff' in str(linen_detail_perms), f"LinenInventoryDetailView should use IsHousekeepingStaff, got: {linen_detail_perms}"
print("✓ Inventory detail views use IsHousekeepingStaff")

# Check WalkIn view get_queryset uses 'property' not 'room__hotel'
from api.v1.frontdesk.checkin_views import WalkInListCreateView, WalkInDetailView
import inspect
list_qs_src = inspect.getsource(WalkInListCreateView.get_queryset)
detail_qs_src = inspect.getsource(WalkInDetailView.get_queryset)
print(f"\nWalkInListCreateView.get_queryset source:")
print(list_qs_src)
print(f"\nWalkInDetailView.get_queryset source:")
print(detail_qs_src)

assert 'property=prop' in list_qs_src, "WalkInListCreateView still uses wrong filter!"
assert 'property=prop' in detail_qs_src, "WalkInDetailView still uses wrong filter!"
assert 'room__hotel' not in list_qs_src, "WalkInListCreateView still uses room__hotel!"
print("✓ WalkIn views use correct property filter")

# Check WalkIn perform_create forces property
list_create_src = inspect.getsource(WalkInListCreateView.perform_create)
print(f"\nWalkInListCreateView.perform_create source:")
print(list_create_src)
assert 'property=prop' in list_create_src, "WalkInListCreateView.perform_create doesn't force property!"
print("✓ WalkIn CREATE injection fix applied")

print("\n=== ALL CHECKS PASSED ===")
