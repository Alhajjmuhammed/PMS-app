#!/usr/bin/env python
"""
Test script for Night Audit & Monthly Stats API endpoints.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.urls import reverse

# Define all new night audit endpoints
audit_endpoints = [
    # Monthly Statistics
    ('monthly_stats_list', 'api_v1:reports:monthly_stats_list'),
    ('monthly_stats_detail', 'api_v1:reports:monthly_stats_detail'),
    
    # Night Audit
    ('night_audit_list', 'api_v1:reports:night_audit_list'),
    ('night_audit_detail', 'api_v1:reports:night_audit_detail'),
    ('night_audit_start', 'api_v1:reports:night_audit_start'),
    ('night_audit_complete', 'api_v1:reports:night_audit_complete'),
    ('night_audit_rollback', 'api_v1:reports:night_audit_rollback'),
    ('audit_logs', 'api_v1:reports:audit_logs'),
]

print("=" * 70)
print("NIGHT AUDIT SYSTEM API ENDPOINTS - VERIFICATION")
print("=" * 70)
print()

success_count = 0
error_count = 0

for name, url_name in audit_endpoints:
    try:
        if 'detail' in name or 'start' in name or 'complete' in name or 'rollback' in name:
            url = reverse(url_name, kwargs={'pk': 1})
        elif 'logs' in name:
            url = reverse(url_name, kwargs={'night_audit_id': 1})
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
    print("🎉 All Night Audit endpoints are registered correctly!")
    print()
    print("IMPLEMENTED ENDPOINTS:")
    print("  - Monthly Statistics (CRUD)")
    print("  - Night Audit (CRUD + Start/Complete/Rollback)")
    print("  - Audit Logs (Read)")
    print()
    print("Total: 8 new endpoints")
else:
    print()
    print("⚠️  Some endpoints failed to register. Check the errors above.")
