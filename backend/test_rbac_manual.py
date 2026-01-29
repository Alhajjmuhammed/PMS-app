"""
Manual RBAC Testing Script
Tests permissions for all 8 roles against key endpoints
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000/api/v1"

# Test credentials
USERS = {
    'ADMIN': {'email': 'admin@test.com', 'password': 'test123'},
    'MANAGER': {'email': 'manager@test.com', 'password': 'manager123'},
    'FRONT_DESK': {'email': 'frontdesk@test.com', 'password': 'frontdesk123'},
    'HOUSEKEEPING': {'email': 'housekeeping@test.com', 'password': 'housekeeping123'},
    'MAINTENANCE': {'email': 'maintenance@test.com', 'password': 'maintenance123'},
    'ACCOUNTANT': {'email': 'accountant@test.com', 'password': 'accountant123'},
    'POS_STAFF': {'email': 'pos@test.com', 'password': 'pos123'},
    'GUEST': {'email': 'guest@test.com', 'password': 'guest123'},
}

# Test endpoints with expected permissions
TEST_CASES = [
    {
        'name': 'Properties List',
        'endpoint': '/properties/',
        'method': 'GET',
        'allowed': ['ADMIN', 'MANAGER'],
        'denied': ['FRONT_DESK', 'HOUSEKEEPING', 'MAINTENANCE', 'ACCOUNTANT', 'POS_STAFF', 'GUEST']
    },
    {
        'name': 'Reservations List',
        'endpoint': '/reservations/',
        'method': 'GET',
        'allowed': ['ADMIN', 'MANAGER', 'FRONT_DESK'],
        'denied': ['HOUSEKEEPING', 'MAINTENANCE', 'POS_STAFF', 'GUEST']
    },
    {
        'name': 'Guests List',
        'endpoint': '/guests/',
        'method': 'GET',
        'allowed': ['ADMIN', 'MANAGER', 'FRONT_DESK'],
        'denied': ['HOUSEKEEPING', 'MAINTENANCE', 'POS_STAFF', 'GUEST']
    },
    {
        'name': 'Housekeeping Tasks',
        'endpoint': '/housekeeping/tasks/',
        'method': 'GET',
        'allowed': ['ADMIN', 'MANAGER', 'HOUSEKEEPING'],
        'denied': ['FRONT_DESK', 'MAINTENANCE', 'ACCOUNTANT', 'POS_STAFF', 'GUEST']
    },
    {
        'name': 'Maintenance Requests',
        'endpoint': '/maintenance/requests/',
        'method': 'GET',
        'allowed': ['ADMIN', 'MANAGER', 'MAINTENANCE'],
        'denied': ['FRONT_DESK', 'HOUSEKEEPING', 'ACCOUNTANT', 'POS_STAFF', 'GUEST']
    },
    {
        'name': 'Billing Invoices',
        'endpoint': '/billing/invoices/',
        'method': 'GET',
        'allowed': ['ADMIN', 'MANAGER', 'ACCOUNTANT'],
        'denied': ['FRONT_DESK', 'HOUSEKEEPING', 'MAINTENANCE', 'POS_STAFF', 'GUEST']
    },
    {
        'name': 'POS Orders',
        'endpoint': '/pos/orders/',
        'method': 'GET',
        'allowed': ['ADMIN', 'MANAGER', 'POS_STAFF'],
        'denied': ['FRONT_DESK', 'HOUSEKEEPING', 'MAINTENANCE', 'ACCOUNTANT', 'GUEST']
    },
    {
        'name': 'Reports Dashboard',
        'endpoint': '/reports/dashboard/',
        'method': 'GET',
        'allowed': ['ADMIN', 'MANAGER'],
        'denied': ['FRONT_DESK', 'HOUSEKEEPING', 'MAINTENANCE', 'ACCOUNTANT', 'POS_STAFF', 'GUEST']
    },
    {
        'name': 'Rooms List',
        'endpoint': '/rooms/',
        'method': 'GET',
        'allowed': ['ADMIN', 'MANAGER', 'FRONT_DESK'],
        'denied': ['HOUSEKEEPING', 'MAINTENANCE', 'ACCOUNTANT', 'POS_STAFF', 'GUEST']
    },
    {
        'name': 'Rate Plans',
        'endpoint': '/rates/plans/',
        'method': 'GET',
        'allowed': ['ADMIN', 'MANAGER'],
        'denied': ['FRONT_DESK', 'HOUSEKEEPING', 'MAINTENANCE', 'ACCOUNTANT', 'POS_STAFF', 'GUEST']
    },
]


def login(email, password):
    """Login and get token"""
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={'email': email, 'password': password}
    )
    if response.status_code == 200:
        return response.json().get('token')
    return None


def test_endpoint(token, endpoint, method='GET'):
    """Test endpoint with token"""
    headers = {'Authorization': f'Token {token}'}
    
    if method == 'GET':
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    elif method == 'POST':
        response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json={})
    
    return response.status_code


def main():
    print("\n" + "="*80)
    print("RBAC PERMISSION TESTING - ALL ROLES")
    print("="*80 + "\n")
    
    # Get tokens for all users
    tokens = {}
    print("Logging in users...")
    for role, creds in USERS.items():
        token = login(creds['email'], creds['password'])
        if token:
            tokens[role] = token
            print(f"✅ {role}: Logged in")
        else:
            print(f"❌ {role}: Login failed")
    
    print("\n" + "-"*80 + "\n")
    
    # Run tests
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test in TEST_CASES:
        print(f"\nTest: {test['name']} ({test['endpoint']})")
        print("-" * 60)
        
        for role in USERS.keys():
            if role not in tokens:
                continue
            
            total_tests += 1
            status_code = test_endpoint(tokens[role], test['endpoint'], test['method'])
            
            # Check if result matches expectation
            if role in test['allowed']:
                expected = 200
                result_text = "ALLOW"
            else:
                expected = 403
                result_text = "DENY"
            
            if status_code == expected:
                status_icon = "✅"
                passed_tests += 1
            else:
                status_icon = "❌"
                failed_tests += 1
            
            print(f"  {status_icon} {role:<15} Expected: {expected} | Got: {status_code} | {result_text}")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
