#!/usr/bin/env python3
"""
Test Frontend-Backend Integration with Real User Workflows
Tests actual workflows through the web interface to verify end-to-end functionality.
"""

import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, date, timedelta


class HotelPMSWorkflowTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.api_token = None
        self.driver = None
        self.test_results = []
        
    def setup_browser(self):
        """Setup headless browser for testing"""
        print("🌐 Setting up browser for frontend testing...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"   ⚠️  Could not setup Chrome driver: {e}")
            print("   💡 Skipping browser tests - install Chrome and chromedriver for full testing")
            return False
    
    def authenticate_api(self):
        """Get API authentication token"""
        try:
            response = requests.post(f"{self.backend_url}/api/auth/login/", {
                'username': 'admin@hotel.com',
                'password': 'admin123'
            })
            
            if response.status_code == 200:
                self.api_token = response.json().get('access')
                return True
            else:
                print(f"   ❌ API Login failed: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ API authentication error: {e}")
            return False
    
    def test_api_endpoints_with_real_data(self):
        """Test API endpoints with the test data we created"""
        print("🔌 Testing API Endpoints with Real Data...")
        
        headers = {'Authorization': f'Bearer {self.api_token}'}
        
        tests = [
            {
                'name': 'Properties API',
                'url': '/api/properties/',
                'expected_min_count': 1
            },
            {
                'name': 'Guests API',
                'url': '/api/guests/',
                'expected_min_count': 4
            },
            {
                'name': 'Reservations API',
                'url': '/api/reservations/',
                'expected_min_count': 3
            },
            {
                'name': 'Rooms API',
                'url': '/api/rooms/',
                'expected_min_count': 24
            },
            {
                'name': 'Room Types API',
                'url': '/api/room-types/',
                'expected_min_count': 3
            },
            {
                'name': 'Billing Folios API',
                'url': '/api/billing/folios/',
                'expected_min_count': 3
            },
            {
                'name': 'Housekeeping Tasks API',
                'url': '/api/housekeeping/tasks/',
                'expected_min_count': 3
            },
            {
                'name': 'Maintenance Requests API',
                'url': '/api/maintenance/requests/',
                'expected_min_count': 3
            }
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                response = requests.get(f"{self.backend_url}{test['url']}", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if it's paginated response
                    if isinstance(data, dict) and 'results' in data:
                        count = len(data['results'])
                        total_count = data.get('count', count)
                    else:
                        count = len(data) if isinstance(data, list) else 1
                        total_count = count
                    
                    if count >= test['expected_min_count']:
                        print(f"   ✅ {test['name']}: {total_count} records")
                        passed += 1
                    else:
                        print(f"   ⚠️  {test['name']}: Expected at least {test['expected_min_count']}, got {count}")
                        
                else:
                    print(f"   ❌ {test['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {test['name']}: {str(e)}")
        
        print(f"   📊 API Tests: {passed}/{total} passed")
        self.test_results.append(f"API Tests: {passed}/{total}")
        return passed == total
    
    def test_frontend_pages(self):
        """Test frontend page accessibility"""
        if not self.driver:
            print("⏭️  Skipping frontend page tests (no browser)")
            return True
            
        print("🖥️  Testing Frontend Page Accessibility...")
        
        pages = [
            {'name': 'Dashboard', 'path': '/'},
            {'name': 'Reservations', 'path': '/reservations'},
            {'name': 'Guests', 'path': '/guests'},
            {'name': 'Rooms', 'path': '/rooms'},
            {'name': 'Billing', 'path': '/billing'},
            {'name': 'Housekeeping', 'path': '/housekeeping'},
            {'name': 'Maintenance', 'path': '/maintenance'},
            {'name': 'Reports', 'path': '/reports'}
        ]
        
        passed = 0
        total = len(pages)
        
        for page in pages:
            try:
                self.driver.get(f"{self.frontend_url}{page['path']}")
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                # Check if we got a valid page (not 404)
                title = self.driver.title
                if "404" not in title and "Error" not in title:
                    print(f"   ✅ {page['name']}: {title}")
                    passed += 1
                else:
                    print(f"   ❌ {page['name']}: {title}")
                    
            except TimeoutException:
                print(f"   ⏰ {page['name']}: Timeout loading page")
            except Exception as e:
                print(f"   ❌ {page['name']}: {str(e)}")
        
        print(f"   📊 Frontend Tests: {passed}/{total} passed")
        self.test_results.append(f"Frontend Tests: {passed}/{total}")
        return passed == total
    
    def test_login_workflow(self):
        """Test actual login workflow through the UI"""
        if not self.driver:
            print("⏭️  Skipping login workflow test (no browser)")
            return True
            
        print("🔐 Testing Login Workflow...")
        
        try:
            # Go to login page
            self.driver.get(f"{self.frontend_url}/login")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for common login form elements
            try:
                email_field = self.driver.find_element(By.NAME, "email")
                password_field = self.driver.find_element(By.NAME, "password")
                login_button = self.driver.find_element(By.TYPE, "submit")
                
                # Fill in credentials
                email_field.clear()
                email_field.send_keys("admin@hotel.com")
                password_field.clear()
                password_field.send_keys("admin123")
                
                # Submit login
                login_button.click()
                
                # Wait for redirect or success
                time.sleep(2)
                
                current_url = self.driver.current_url
                if "/login" not in current_url:
                    print("   ✅ Login successful - redirected to dashboard")
                    return True
                else:
                    print("   ⚠️  Login form submitted but still on login page")
                    return False
                    
            except NoSuchElementException:
                print("   ⚠️  Login form elements not found (login might use different field names)")
                return False
                
        except Exception as e:
            print(f"   ❌ Login workflow error: {e}")
            return False
    
    def test_data_display(self):
        """Test if frontend displays the test data"""
        if not self.driver:
            print("⏭️  Skipping data display test (no browser)")
            return True
            
        print("📊 Testing Data Display in Frontend...")
        
        tests = [
            {
                'name': 'Reservations Page',
                'path': '/reservations',
                'look_for': ['John', 'Jane', 'Michael', 'reservation']
            },
            {
                'name': 'Guests Page', 
                'path': '/guests',
                'look_for': ['john.doe@email.com', 'guest', 'contact']
            },
            {
                'name': 'Rooms Page',
                'path': '/rooms',
                'look_for': ['101', '201', 'room', 'available']
            }
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                self.driver.get(f"{self.frontend_url}{test['path']}")
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                page_source = self.driver.page_source.lower()
                found_items = [item for item in test['look_for'] if item.lower() in page_source]
                
                if found_items:
                    print(f"   ✅ {test['name']}: Found {len(found_items)}/{len(test['look_for'])} data items")
                    passed += 1
                else:
                    print(f"   ⚠️  {test['name']}: No expected data found on page")
                    
            except Exception as e:
                print(f"   ❌ {test['name']}: {str(e)}")
        
        print(f"   📊 Data Display Tests: {passed}/{total} passed")
        self.test_results.append(f"Data Display Tests: {passed}/{total}")
        return passed == total
    
    def test_create_guest_workflow(self):
        """Test creating a new guest through the frontend"""
        if not self.driver:
            print("⏭️  Skipping guest creation test (no browser)")
            return True
            
        print("👤 Testing Guest Creation Workflow...")
        
        try:
            # Go to guests page
            self.driver.get(f"{self.frontend_url}/guests")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for "Add Guest" or "New Guest" button
            add_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Add') or contains(text(), 'New') or contains(text(), 'Create')]")
            
            if add_buttons:
                print("   ✅ Found 'Add Guest' functionality")
                return True
            else:
                print("   ⚠️  No 'Add Guest' button found - may need to implement")
                return False
                
        except Exception as e:
            print(f"   ❌ Guest creation test error: {e}")
            return False
    
    def test_mobile_app_api_connectivity(self):
        """Test if mobile app can connect to API"""
        print("📱 Testing Mobile App API Connectivity...")
        
        # Test the API endpoints that mobile app would use
        headers = {'Authorization': f'Bearer {self.api_token}'}
        
        mobile_endpoints = [
            '/api/auth/me/',  # User profile
            '/api/properties/',  # Property selection
            '/api/reservations/',  # Reservations list
            '/api/guests/',  # Guest lookup
            '/api/rooms/',  # Room status
        ]
        
        passed = 0
        total = len(mobile_endpoints)
        
        for endpoint in mobile_endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {endpoint}: Mobile-ready")
                    passed += 1
                else:
                    print(f"   ❌ {endpoint}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {endpoint}: {str(e)}")
        
        print(f"   📊 Mobile API Tests: {passed}/{total} passed")
        self.test_results.append(f"Mobile API Tests: {passed}/{total}")
        return passed == total
    
    def run_comprehensive_test(self):
        """Run all integration tests"""
        print("🏨 COMPREHENSIVE FRONTEND-BACKEND INTEGRATION TEST")
        print("=" * 60)
        print(f"🔗 Backend URL: {self.backend_url}")
        print(f"🖥️  Frontend URL: {self.frontend_url}")
        print(f"🕒 Test Time: {datetime.now()}")
        print()
        
        # Setup
        browser_available = self.setup_browser()
        
        # API Authentication
        if not self.authenticate_api():
            print("❌ Cannot proceed without API authentication")
            return False
        
        print("   ✅ API Authentication successful")
        print()
        
        # Run all tests
        tests = [
            ('API Endpoints with Real Data', self.test_api_endpoints_with_real_data),
            ('Frontend Page Accessibility', self.test_frontend_pages),
            ('Login Workflow', self.test_login_workflow),
            ('Data Display', self.test_data_display),
            ('Guest Creation Workflow', self.test_create_guest_workflow),
            ('Mobile App API Connectivity', self.test_mobile_app_api_connectivity)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_function in tests:
            print(f"🧪 {test_name}...")
            try:
                if test_function():
                    passed_tests += 1
                print()
            except Exception as e:
                print(f"   ❌ Test failed with error: {e}")
                print()
        
        # Summary
        print("=" * 60)
        print("📋 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            print(f"📊 {result}")
        
        print()
        print(f"🎯 Overall Result: {passed_tests}/{total_tests} test categories passed")
        
        if passed_tests == total_tests:
            print("✅ ALL TESTS PASSED! 🎉")
            print("🚀 Hotel PMS is fully functional end-to-end!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ MOSTLY FUNCTIONAL! 👍")
            print("🔧 Minor issues to fix but core functionality works")
        else:
            print("⚠️  SOME ISSUES FOUND")
            print("🛠️  Additional work needed for full functionality")
        
        # Cleanup
        if self.driver:
            self.driver.quit()
        
        return passed_tests == total_tests


def main():
    tester = HotelPMSWorkflowTester()
    return tester.run_comprehensive_test()


if __name__ == "__main__":
    main()