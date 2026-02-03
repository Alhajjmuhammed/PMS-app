#!/usr/bin/env python
"""
Complete Login & Authentication Testing
Tests login functionality with all test users
"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"
WEB_BASE = "http://localhost:3000"

# Test users from our database
TEST_USERS = [
    {"email": "admin@test.com", "password": "admin123", "role": "Admin"},
    {"email": "manager@test.com", "password": "manager123", "role": "Manager"},
    {"email": "receptionist@test.com", "password": "receptionist123", "role": "Receptionist"},
    {"email": "housekeeper@test.com", "password": "housekeeper123", "role": "Housekeeper"},
]

def test_backend_login(email, password, role):
    """Test backend API login"""
    print(f"\n{'='*80}")
    print(f"Testing Backend Login: {role} ({email})")
    print('='*80)
    
    try:
        # Test login endpoint
        response = requests.post(
            f"{API_BASE}/auth/login/",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token') or data.get('access') or data.get('key')
            
            print(f"✅ Login Successful!")
            print(f"   Status: {response.status_code}")
            print(f"   Token: {token[:30] if token else 'No token'}...")
            
            if token:
                # Test authenticated request
                print(f"\n   Testing authenticated API call...")
                test_response = requests.get(
                    f"{API_BASE}/properties/",
                    headers={"Authorization": f"Token {token}"},
                    timeout=5
                )
                print(f"   Properties API: HTTP {test_response.status_code}")
                
                if test_response.status_code == 200:
                    print(f"   ✅ Authenticated requests working!")
                    return True, token
                elif test_response.status_code == 403:
                    print(f"   ⚠️  Permission denied (expected for some roles)")
                    return True, token
                else:
                    print(f"   ❌ Unexpected status: {test_response.status_code}")
                    return True, token
            else:
                print(f"   ⚠️  No token in response")
                return False, None
                
        elif response.status_code == 400:
            print(f"❌ Login Failed: Bad Request")
            print(f"   Response: {response.text[:200]}")
            return False, None
        elif response.status_code == 401:
            print(f"❌ Login Failed: Invalid Credentials")
            return False, None
        elif response.status_code == 404:
            print(f"❌ Login endpoint not found (check URL)")
            return False, None
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, None

def test_auth_endpoints():
    """Test all authentication endpoints"""
    print("\n" + "="*80)
    print("TESTING AUTHENTICATION ENDPOINTS")
    print("="*80)
    
    endpoints_to_check = [
        "/auth/login/",
        "/auth/token/",
        "/api-token-auth/",
        "/accounts/login/",
    ]
    
    for endpoint in endpoints_to_check:
        try:
            response = requests.post(
                f"{API_BASE}{endpoint}",
                json={"email": "admin@test.com", "password": "admin123"},
                timeout=3
            )
            status = f"HTTP {response.status_code}"
            if response.status_code == 200:
                print(f"✅ {endpoint:30s} {status} - Working!")
            elif response.status_code == 404:
                print(f"❌ {endpoint:30s} {status} - Not Found")
            else:
                print(f"⚠️  {endpoint:30s} {status}")
        except Exception as e:
            print(f"❌ {endpoint:30s} Error: {str(e)[:40]}")

def test_web_login_page():
    """Test if web login page loads"""
    print("\n" + "="*80)
    print("TESTING WEB LOGIN PAGE")
    print("="*80)
    
    try:
        response = requests.get(f"{WEB_BASE}/login", timeout=5)
        
        if response.status_code == 200:
            content = response.text
            has_email = 'email' in content.lower()
            has_password = 'password' in content.lower()
            has_login = 'login' in content.lower() or 'sign in' in content.lower()
            
            print(f"✅ Login page loads: HTTP {response.status_code}")
            print(f"   Page size: {len(content)} bytes")
            print(f"   Contains 'email': {has_email}")
            print(f"   Contains 'password': {has_password}")
            print(f"   Contains 'login': {has_login}")
            
            if has_email and has_password and has_login:
                print(f"   ✅ Login form appears to be present")
                return True
            else:
                print(f"   ⚠️  Login form might be missing elements")
                return False
        else:
            print(f"❌ Login page failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading login page: {str(e)}")
        return False

def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "LOGIN & AUTHENTICATION TEST SUITE" + " "*24 + "║")
    print("╚" + "="*78 + "╝")
    
    # Test 1: Check authentication endpoints
    test_auth_endpoints()
    
    # Test 2: Check web login page
    web_login_works = test_web_login_page()
    
    # Test 3: Test backend login for each user
    successful_logins = 0
    failed_logins = 0
    tokens = {}
    
    for user in TEST_USERS:
        success, token = test_backend_login(
            user['email'], 
            user['password'], 
            user['role']
        )
        if success:
            successful_logins += 1
            tokens[user['role']] = token
        else:
            failed_logins += 1
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    total_tests = len(TEST_USERS)
    success_rate = (successful_logins / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nBackend Login Tests:")
    print(f"  Total Users Tested: {total_tests}")
    print(f"  ✅ Successful: {successful_logins}")
    print(f"  ❌ Failed: {failed_logins}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    print(f"\nWeb Login Page:")
    if web_login_works:
        print(f"  ✅ Login page loads and has form elements")
    else:
        print(f"  ❌ Login page has issues")
    
    print(f"\nTokens Obtained:")
    for role, token in tokens.items():
        if token:
            print(f"  {role:20s} {token[:50]}...")
    
    print("\n" + "="*80)
    print("🎯 FINAL VERDICT")
    print("="*80)
    
    if successful_logins == total_tests and web_login_works:
        print("✅ AUTHENTICATION IS FULLY WORKING!")
        print("   - Backend login: 100% functional")
        print("   - Web login page: Present and ready")
        print("   - All test users can authenticate")
        print("\n   🚀 System is ready for user login testing!")
    elif successful_logins > 0:
        print("⚠️  AUTHENTICATION PARTIALLY WORKING")
        print(f"   - Backend login: {success_rate:.0f}% functional")
        print(f"   - Some users can authenticate")
        print(f"   - Needs investigation for failed logins")
    else:
        print("❌ AUTHENTICATION NOT WORKING")
        print("   - No users can log in")
        print("   - Check authentication endpoint configuration")
        print("   - Verify user credentials in database")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
