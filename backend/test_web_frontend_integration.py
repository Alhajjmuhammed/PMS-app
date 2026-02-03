#!/usr/bin/env python
"""
Comprehensive Web Frontend Integration Test
Tests actual Next.js pages loading data from Django backend
"""
import requests
import json
import time

BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000/api/v1"

def log_test(name, passed, message=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if message:
        print(f"     {message}")
    return passed

def test_web_homepage():
    """Test if Next.js web frontend homepage loads"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        return log_test(
            "Web Homepage Loading",
            response.status_code == 200,
            f"HTTP {response.status_code}, Size: {len(response.content)} bytes"
        )
    except Exception as e:
        return log_test("Web Homepage Loading", False, str(e))

def test_web_dashboard():
    """Test if dashboard page loads"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=5)
        passed = response.status_code == 200
        return log_test(
            "Dashboard Page",
            passed,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        return log_test("Dashboard Page", False, str(e))

def test_web_properties_page():
    """Test if properties page loads"""
    try:
        response = requests.get(f"{BASE_URL}/properties", timeout=5)
        passed = response.status_code == 200
        return log_test(
            "Properties Page",
            passed,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        return log_test("Properties Page", False, str(e))

def test_web_guests_page():
    """Test if guests page loads"""
    try:
        response = requests.get(f"{BASE_URL}/guests", timeout=5)
        passed = response.status_code == 200
        return log_test(
            "Guests Page",
            passed,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        return log_test("Guests Page", False, str(e))

def test_web_reservations_page():
    """Test if reservations page loads"""
    try:
        response = requests.get(f"{BASE_URL}/reservations", timeout=5)
        passed = response.status_code == 200
        return log_test(
            "Reservations Page",
            passed,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        return log_test("Reservations Page", False, str(e))

def test_web_rooms_page():
    """Test if rooms page loads"""
    try:
        response = requests.get(f"{BASE_URL}/rooms", timeout=5)
        passed = response.status_code == 200
        return log_test(
            "Rooms Page",
            passed,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        return log_test("Rooms Page", False, str(e))

def test_web_housekeeping_page():
    """Test if housekeeping page loads"""
    try:
        response = requests.get(f"{BASE_URL}/housekeeping", timeout=5)
        passed = response.status_code == 200
        return log_test(
            "Housekeeping Page",
            passed,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        return log_test("Housekeeping Page", False, str(e))

def test_web_maintenance_page():
    """Test if maintenance page loads"""
    try:
        response = requests.get(f"{BASE_URL}/maintenance", timeout=5)
        passed = response.status_code == 200
        return log_test(
            "Maintenance Page",
            passed,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        return log_test("Maintenance Page", False, str(e))

def test_web_billing_page():
    """Test if billing page loads"""
    try:
        response = requests.get(f"{BASE_URL}/billing", timeout=5)
        passed = response.status_code == 200
        return log_test(
            "Billing Page",
            passed,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        return log_test("Billing Page", False, str(e))

def test_web_reports_page():
    """Test if reports page loads"""
    try:
        response = requests.get(f"{BASE_URL}/reports", timeout=5)
        passed = response.status_code == 200
        return log_test(
            "Reports Page",
            passed,
            f"HTTP {response.status_code}"
        )
    except Exception as e:
        return log_test("Reports Page", False, str(e))

def test_api_endpoint_for_frontend(endpoint, name):
    """Test if API endpoint is accessible (for frontend data fetching)"""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=5)
        # Accept both 200 (success) and 401 (needs auth)
        passed = response.status_code in [200, 401, 403]
        return log_test(
            f"API {name}",
            passed,
            f"HTTP {response.status_code} (Backend responding)"
        )
    except Exception as e:
        return log_test(f"API {name}", False, str(e))

def main():
    print("=" * 80)
    print("🌐 WEB FRONTEND INTEGRATION TEST")
    print("=" * 80)
    print()
    
    results = []
    
    print("📄 Testing Web Pages:")
    print("-" * 80)
    results.append(test_web_homepage())
    time.sleep(0.2)
    results.append(test_web_dashboard())
    time.sleep(0.2)
    results.append(test_web_properties_page())
    time.sleep(0.2)
    results.append(test_web_guests_page())
    time.sleep(0.2)
    results.append(test_web_reservations_page())
    time.sleep(0.2)
    results.append(test_web_rooms_page())
    time.sleep(0.2)
    results.append(test_web_housekeeping_page())
    time.sleep(0.2)
    results.append(test_web_maintenance_page())
    time.sleep(0.2)
    results.append(test_web_billing_page())
    time.sleep(0.2)
    results.append(test_web_reports_page())
    
    print()
    print("🔌 Testing Backend API Endpoints (for frontend):")
    print("-" * 80)
    results.append(test_api_endpoint_for_frontend("/properties/", "Properties"))
    results.append(test_api_endpoint_for_frontend("/rooms/", "Rooms"))
    results.append(test_api_endpoint_for_frontend("/guests/", "Guests"))
    results.append(test_api_endpoint_for_frontend("/reservations/", "Reservations"))
    results.append(test_api_endpoint_for_frontend("/housekeeping/tasks/", "Housekeeping"))
    results.append(test_api_endpoint_for_frontend("/maintenance/requests/", "Maintenance"))
    results.append(test_api_endpoint_for_frontend("/billing/folios/", "Billing"))
    results.append(test_api_endpoint_for_frontend("/reports/daily-stats/", "Reports"))
    
    print()
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    if success_rate >= 90:
        print("🎉 EXCELLENT: Web frontend is loading correctly!")
    elif success_rate >= 70:
        print("✅ GOOD: Most web pages are loading")
    elif success_rate >= 50:
        print("⚠️  WARNING: Some pages are not loading")
    else:
        print("❌ CRITICAL: Many pages failing to load")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
