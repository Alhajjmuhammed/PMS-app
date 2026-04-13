#!/usr/bin/env python3
"""
Test script to verify the specific API fixes we implemented
"""

import requests
import json

# Use the valid token we obtained
TOKEN = "fc0d416cdf17522aba6642f8465fc0ad141b06e8"
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Authorization": f"Token {TOKEN}"}

def test_endpoint(name, url, expected_status=200):
    """Test an API endpoint"""
    print(f"\n🧪 Testing {name}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                if 'count' in data:
                    print(f"   Count: {data['count']}")
                if 'results' in data:
                    print(f"   Results: {len(data['results'])} items")
                if 'username' in data or 'email' in data:
                    print(f"   User: {data.get('email', data.get('username', 'N/A'))}")
            print(f"   ✅ {name} PASSED")
            return True
        else:
            print(f"   ❌ {name} FAILED - Status {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ {name} FAILED - Connection Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ {name} FAILED - Error: {e}")
        return False

def main():
    print("================================================================================")
    print("                           API FIXES VERIFICATION TEST")
    print("================================================================================")
    
    tests = [
        # Test the fixes we implemented
        ("Room Types API", f"{BASE_URL}/rooms/types/"),
        ("User Profile /me/", f"{BASE_URL}/auth/me/"),
        ("Folio Charges API", f"{BASE_URL}/billing/folio-charges/"),
        
        # Test related endpoints that should still work
        ("Rooms API", f"{BASE_URL}/rooms/"),
        ("Housekeeping Tasks", f"{BASE_URL}/housekeeping/tasks/"),
        ("Maintenance Requests", f"{BASE_URL}/maintenance/requests/"),
        
        # Test other important endpoints
        ("Properties API", f"{BASE_URL}/properties/"),
        ("Guests API", f"{BASE_URL}/guests/"),
        ("Reservations API", f"{BASE_URL}/reservations/"),
        ("Billing Folios", f"{BASE_URL}/billing/folios/"),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, url in tests:
        if test_endpoint(name, url):
            passed += 1
    
    print("\n================================================================================")
    print("                                 TEST SUMMARY")
    print("================================================================================")
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! API fixes are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Some issues may remain.")

if __name__ == "__main__":
    main()