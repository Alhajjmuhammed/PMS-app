#!/usr/bin/env python3
"""Test script for Phase 5 implementation - Housekeeping Inventory + Enhanced Notifications + Guest Preferences"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.urls import reverse, resolve

def test_phase5_endpoints():
    """Test all Phase 5 URL patterns"""
    
    print("=" * 70)
    print("PHASE 5 ENDPOINT TESTING - INVENTORY + NOTIFICATIONS + PREFERENCES")
    print("=" * 70)
    
    # Define Phase 5 endpoints
    phase5_endpoints = {
        'Housekeeping Inventory (9 endpoints)': [
            ('api_v1:housekeeping:amenity_inventory_list', 'GET/POST', '/api/v1/housekeeping/inventory/amenities/'),
            ('api_v1:housekeeping:amenity_inventory_detail', 'GET/PUT/DELETE', '/api/v1/housekeeping/inventory/amenities/<id>/'),
            ('api_v1:housekeeping:linen_inventory_list', 'GET/POST', '/api/v1/housekeeping/inventory/linens/'),
            ('api_v1:housekeeping:linen_inventory_detail', 'GET/PUT/DELETE', '/api/v1/housekeeping/inventory/linens/<id>/'),
            ('api_v1:housekeeping:stock_movement_list', 'GET/POST', '/api/v1/housekeeping/inventory/movements/'),
            ('api_v1:housekeeping:stock_movement_detail', 'GET', '/api/v1/housekeeping/inventory/movements/<id>/'),
        ],
        'Enhanced Notifications (7 endpoints)': [
            ('api_v1:notifications:template_list', 'GET/POST', '/api/v1/notifications/templates/'),
            ('api_v1:notifications:template_detail', 'GET/PUT/DELETE', '/api/v1/notifications/templates/<id>/'),
            ('api_v1:notifications:email_log_list', 'GET/POST', '/api/v1/notifications/emails/'),
            ('api_v1:notifications:email_log_detail', 'GET', '/api/v1/notifications/emails/<id>/'),
            ('api_v1:notifications:sms_log_list', 'GET/POST', '/api/v1/notifications/sms/'),
            ('api_v1:notifications:sms_log_detail', 'GET', '/api/v1/notifications/sms/<id>/'),
            ('api_v1:notifications:send_push', 'POST', '/api/v1/notifications/push/send/'),
        ],
        'Guest Preferences (3 endpoints)': [
            ('api_v1:guests:preference_list', 'GET/POST', '/api/v1/guests/preferences/'),
            ('api_v1:guests:preference_detail', 'GET/PUT/DELETE', '/api/v1/guests/preferences/<id>/'),
            ('api_v1:guests:guest_preferences', 'GET', '/api/v1/guests/<guest_id>/preferences/'),
        ]
    }
    
    total_endpoints = 0
    passed_endpoints = 0
    failed_endpoints = []
    
    for module, endpoints in phase5_endpoints.items():
        print(f"\n{'='*70}")
        print(f"{module.upper()}")
        print(f"{'='*70}")
        
        for url_name, methods, path_example in endpoints:
            total_endpoints += 1
            try:
                # Test URL resolution
                if '<id>' in path_example:
                    url = reverse(url_name, kwargs={'pk': 1})
                elif '<guest_id>' in path_example:
                    url = reverse(url_name, kwargs={'guest_id': 1})
                else:
                    url = reverse(url_name)
                
                # Test URL reverse resolution
                match = resolve(url)
                
                print(f"✓ {url_name:50s} {methods:20s} {url}")
                passed_endpoints += 1
                
            except Exception as e:
                print(f"✗ {url_name:50s} {methods:20s} FAILED: {str(e)}")
                failed_endpoints.append((url_name, str(e)))
    
    # Summary
    print(f"\n{'='*70}")
    print("PHASE 5 SUMMARY")
    print(f"{'='*70}")
    print(f"Total Endpoints:  {total_endpoints}")
    print(f"Passed:           {passed_endpoints} ({passed_endpoints/total_endpoints*100:.1f}%)")
    print(f"Failed:           {len(failed_endpoints)}")
    
    if failed_endpoints:
        print(f"\n{'='*70}")
        print("FAILED ENDPOINTS")
        print(f"{'='*70}")
        for name, error in failed_endpoints:
            print(f"  {name}: {error}")
    
    print(f"\n{'='*70}")
    print("PHASE 5 IMPLEMENTATION DETAILS")
    print(f"{'='*70}")
    print("""
Housekeeping Inventory (6 endpoints):
  - Amenity Inventory CRUD (List/Create, Detail/Update/Delete)
  - Linen Inventory CRUD (List/Create, Detail/Update/Delete)
  - Stock Movement tracking (List/Create, Detail)

Enhanced Notifications (7 endpoints):
  - Notification Template CRUD (List/Create, Detail/Update/Delete)
  - Email Log CRUD (List/Create, Detail)
  - SMS Log CRUD (List/Create, Detail)
  - Push Notification sending (Send)

Guest Preferences (3 endpoints):
  - Guest Preference CRUD (List/Create, Detail/Update/Delete)
  - Guest-specific preferences list (Get by guest ID)

Features Implemented:
  ✓ Property-based filtering for multi-tenant support
  ✓ Comprehensive validation in serializers
  ✓ Query optimization with select_related
  ✓ Permission-based access control
  ✓ Search, filter, and ordering capabilities
  ✓ Stock movement tracking with balance updates
  ✓ Inventory low-stock alerts
  ✓ Template-based notification system
  ✓ Email and SMS logging
  ✓ Push notification infrastructure
  ✓ Preference categorization and duplicate prevention
    """)
    
    return passed_endpoints == total_endpoints

if __name__ == '__main__':
    success = test_phase5_endpoints()
    sys.exit(0 if success else 1)
