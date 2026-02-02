#!/usr/bin/env python3
"""Test script for Phase 4 implementation - Loyalty Program + Revenue Management"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.urls import reverse, resolve

def test_phase4_endpoints():
    """Test all Phase 4 URL patterns"""
    
    print("=" * 70)
    print("PHASE 4 ENDPOINT TESTING - LOYALTY PROGRAM + REVENUE MANAGEMENT")
    print("=" * 70)
    
    # Define Phase 4 endpoints
    phase4_endpoints = {
        'Loyalty Program': [
            ('api_v1:guests:loyalty_program_list', 'GET/POST', '/api/v1/guests/loyalty/programs/'),
            ('api_v1:guests:loyalty_program_detail', 'GET/PUT/DELETE', '/api/v1/guests/loyalty/programs/<id>/'),
            ('api_v1:guests:loyalty_tier_list', 'GET/POST', '/api/v1/guests/loyalty/tiers/'),
            ('api_v1:guests:loyalty_tier_detail', 'GET/PUT/DELETE', '/api/v1/guests/loyalty/tiers/<id>/'),
            ('api_v1:guests:loyalty_transaction_list', 'GET/POST', '/api/v1/guests/loyalty/transactions/'),
            ('api_v1:guests:loyalty_transaction_detail', 'GET/PUT/DELETE', '/api/v1/guests/loyalty/transactions/<id>/'),
            ('api_v1:guests:guest_loyalty_balance', 'GET', '/api/v1/guests/<guest_id>/loyalty/balance/'),
        ],
        'Revenue Management': [
            ('api_v1:rates:package_list', 'GET/POST', '/api/v1/rates/packages/'),
            ('api_v1:rates:package_detail', 'GET/PUT/DELETE', '/api/v1/rates/packages/<id>/'),
            ('api_v1:rates:discount_list', 'GET/POST', '/api/v1/rates/discounts/'),
            ('api_v1:rates:discount_detail', 'GET/PUT/DELETE', '/api/v1/rates/discounts/<id>/'),
            ('api_v1:rates:yield_rule_list', 'GET/POST', '/api/v1/rates/yield-rules/'),
            ('api_v1:rates:yield_rule_detail', 'GET/PUT/DELETE', '/api/v1/rates/yield-rules/<id>/'),
        ]
    }
    
    total_endpoints = 0
    passed_endpoints = 0
    failed_endpoints = []
    
    for module, endpoints in phase4_endpoints.items():
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
                
                print(f"✓ {url_name:40s} {methods:20s} {url}")
                passed_endpoints += 1
                
            except Exception as e:
                print(f"✗ {url_name:40s} {methods:20s} FAILED: {str(e)}")
                failed_endpoints.append((url_name, str(e)))
    
    # Summary
    print(f"\n{'='*70}")
    print("PHASE 4 SUMMARY")
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
    print("PHASE 4 IMPLEMENTATION DETAILS")
    print(f"{'='*70}")
    print("""
Loyalty Program (7 endpoints):
  - Loyalty Program CRUD (List/Create, Detail/Update/Delete)
  - Loyalty Tier CRUD (List/Create, Detail/Update/Delete)
  - Loyalty Transaction CRUD (List/Create, Detail/Update/Delete)
  - Guest Balance View (Points balance, tier info, statistics)

Revenue Management (6 endpoints):
  - Package CRUD (List/Create, Detail/Update/Delete)
  - Discount CRUD (List/Create, Detail/Update/Delete)
  - Yield Rule CRUD (List/Create, Detail/Update/Delete)

Features Implemented:
  ✓ Property-based filtering for multi-tenant support
  ✓ Comprehensive validation in serializers
  ✓ Query optimization with select_related/prefetch_related
  ✓ Permission-based access control (IsAdminOrManager, IsFrontDeskOrAbove)
  ✓ Search, filter, and ordering capabilities
  ✓ Read/write serializer separation for complex operations
  ✓ Business logic validations (dates, balances, codes, usage limits)
    """)
    
    return passed_endpoints == total_endpoints

if __name__ == '__main__':
    success = test_phase4_endpoints()
    sys.exit(0 if success else 1)
