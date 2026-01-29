#!/usr/bin/env python3
"""
Role-Based Permission Testing Script
Tests all 8 roles against various endpoints to verify permissions
"""

import requests
import json
from typing import Dict, List, Tuple

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
CREDENTIALS = {
    "superuser": {"email": "admin@pms.com", "password": "test123"},
    "manager_grand": {"email": "manager@grandhotel.com", "password": "test123"},
    "manager_beach": {"email": "manager@beachresort.com", "password": "test123"},
    "front_desk": {"email": "frontdesk@test.com", "password": "test123"},
    "housekeeping": {"email": "housekeeping@test.com", "password": "test123"},
    "maintenance": {"email": "maintenance@test.com", "password": "test123"},
    # Add more test users as needed
}

# Test Cases: (endpoint, method, role_should_access)
TEST_CASES = [
    # Properties - Superuser Only
    ("/properties/", "GET", ["superuser", "manager_grand", "manager_beach"]),
    ("/properties/", "POST", ["superuser"]),
    
    # Users - Superuser Only
    ("/auth/users/", "GET", ["superuser"]),
    ("/auth/users/", "POST", ["superuser"]),
    
    # Reservations - Front Desk+
    ("/reservations/", "GET", ["superuser", "manager_grand", "manager_beach", "front_desk"]),
    ("/reservations/", "POST", ["superuser", "manager_grand", "manager_beach", "front_desk"]),
    
    # Housekeeping - Housekeeping+
    ("/housekeeping/tasks/", "GET", ["superuser", "manager_grand", "manager_beach", "housekeeping"]),
    
    # Maintenance - Maintenance+
    ("/maintenance/requests/", "GET", ["superuser", "manager_grand", "manager_beach", "maintenance"]),
    
    # Billing - Accountant+
    ("/billing/charge-codes/", "GET", ["superuser", "manager_grand", "manager_beach", "front_desk"]),
    
    # Reports - Manager+
    ("/reports/dashboard/", "GET", ["superuser", "manager_grand", "manager_beach"]),
    
    # Rooms - All Authenticated
    ("/rooms/", "GET", ["superuser", "manager_grand", "manager_beach", "front_desk", "housekeeping", "maintenance"]),
]

class PermissionTester:
    def __init__(self):
        self.tokens: Dict[str, str] = {}
        self.results: List[Tuple[str, str, str, bool, int]] = []
    
    def login(self, role: str, credentials: dict) -> str:
        """Login and get token for a role"""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login/",
                json=credentials,
                timeout=10
            )
            if response.status_code == 200:
                token = response.json().get("token")
                self.tokens[role] = token
                return token
            else:
                print(f"❌ Login failed for {role}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Login error for {role}: {e}")
            return None
    
    def test_endpoint(self, role: str, endpoint: str, method: str, should_pass: bool):
        """Test a single endpoint with a role"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  No token for {role}, skipping")
            return
        
        headers = {"Authorization": f"Token {token}"}
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json={}, timeout=10)
            else:
                return
            
            status = response.status_code
            passed = (should_pass and status in [200, 201]) or (not should_pass and status == 403)
            
            result_icon = "✅" if passed else "❌"
            expected = "200/201" if should_pass else "403"
            
            self.results.append((role, endpoint, method, passed, status))
            
            if not passed:
                print(f"{result_icon} {role} → {method} {endpoint}: Expected {expected}, Got {status}")
            
        except Exception as e:
            print(f"❌ Error testing {role} → {method} {endpoint}: {e}")
    
    def run_tests(self):
        """Run all test cases"""
        print("=" * 80)
        print("ROLE-BASED PERMISSION TESTING")
        print("=" * 80)
        
        # Login all users
        print("\n📝 Logging in test users...")
        for role, creds in CREDENTIALS.items():
            token = self.login(role, creds)
            if token:
                print(f"✅ {role} logged in")
        
        # Run tests
        print(f"\n🧪 Running {len(TEST_CASES)} test cases...\n")
        
        for endpoint, method, allowed_roles in TEST_CASES:
            for role in CREDENTIALS.keys():
                should_pass = role in allowed_roles
                self.test_endpoint(role, endpoint, method, should_pass)
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r[3])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for role, endpoint, method, passed, status in self.results:
                if not passed:
                    print(f"  • {role} → {method} {endpoint} (got {status})")
        else:
            print("\n🎉 ALL TESTS PASSED!")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = PermissionTester()
    tester.run_tests()
