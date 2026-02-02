#!/usr/bin/env python
"""
Test script for Channel Manager API endpoints.
Run after starting the server with: python manage.py runserver
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.urls import reverse

# Define all new channel endpoints
channel_endpoints = [
    # Rate Plan Mappings
    ('rate_mapping_list', 'api_v1:channels:rate_mapping_list'),
    ('rate_mapping_detail', 'api_v1:channels:rate_mapping_detail'),
    
    # Availability Updates
    ('availability_update_list', 'api_v1:channels:availability_update_list'),
    ('availability_update_detail', 'api_v1:channels:availability_update_detail'),
    ('availability_update_resend', 'api_v1:channels:availability_update_resend'),
    
    # Rate Updates
    ('rate_update_list', 'api_v1:channels:rate_update_list'),
    ('rate_update_detail', 'api_v1:channels:rate_update_detail'),
    ('rate_update_resend', 'api_v1:channels:rate_update_resend'),
    
    # Channel Reservations
    ('reservation_list', 'api_v1:channels:reservation_list'),
    ('reservation_detail', 'api_v1:channels:reservation_detail'),
    ('reservation_process', 'api_v1:channels:reservation_process'),
    ('reservation_cancel', 'api_v1:channels:reservation_cancel'),
]

print("=" * 70)
print("CHANNEL MANAGER API ENDPOINTS - VERIFICATION")
print("=" * 70)
print()

success_count = 0
error_count = 0

for name, url_name in channel_endpoints:
    try:
        if 'detail' in name or 'resend' in name or 'process' in name or 'cancel' in name:
            # These require a pk parameter
            url = reverse(url_name, kwargs={'pk': 1})
        else:
            url = reverse(url_name)
        
        print(f"✅ {name:35} -> {url}")
        success_count += 1
    except Exception as e:
        print(f"❌ {name:35} -> ERROR: {str(e)}")
        error_count += 1

print()
print("=" * 70)
print(f"RESULTS: {success_count} successful, {error_count} errors")
print("=" * 70)

if error_count == 0:
    print()
    print("🎉 All Channel Manager endpoints are registered correctly!")
    print()
    print("IMPLEMENTED ENDPOINTS:")
    print("  - Rate Plan Mappings (CRUD)")
    print("  - Availability Updates (CRUD + Resend)")
    print("  - Rate Updates (CRUD + Resend)")
    print("  - Channel Reservations (CRUD + Process/Cancel)")
    print()
    print("Total: 12 new endpoints")
    sys.exit(0)
else:
    print()
    print("⚠️  Some endpoints failed to register. Check the errors above.")
    sys.exit(1)
