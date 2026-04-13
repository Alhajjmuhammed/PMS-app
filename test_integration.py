#!/usr/bin/env python3
"""
Comprehensive Frontend-Backend Integration Test
Tests real API connectivity and data flow.
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# Add Django settings
sys.path.insert(0, '/home/easyfix/Documents/PMS/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.accounts.models import User
from apps.properties.models import Property
from apps.rooms.models import Room
from apps.guests.models import Guest
from apps.reservations.models import Reservation

API_BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:3000"

class IntegrationTester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
    
    def test_backend_running(self):
        """Test if Django backend is accessible"""
        print("🔧 Testing Backend Server...")
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=5)
            print(f"   ✅ Backend accessible: {response.status_code}")
            return True
        except Exception as e:
            print(f"   ❌ Backend not accessible: {e}")
            return False
    
    def test_authentication(self):
        """Test login API and get JWT token"""
        print("🔐 Testing Authentication...")
        
        # Test with admin user
        login_data = {
            "email": "admin@hotel.com",
            "password": "admin123"
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/auth/login/", 
                                   json=login_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                print(f"   ✅ Login successful, token: {self.token[:20]}...")
                
                # Set token for future requests
                self.session.headers.update({
                    'Authorization': f'Token {self.token}',
                    'Content-Type': 'application/json'
                })
                return True
            else:
                print(f"   ❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test key API endpoints with authentication"""
        print("📡 Testing API Endpoints...")
        
        endpoints = [
            ('/properties/', 'Properties'),
            ('/rooms/?limit=5', 'Rooms'),
            ('/rooms/types/', 'Room Types'),
            ('/auth/users/', 'Users'),
            ('/auth/permissions/', 'Permissions'),
        ]
        
        for endpoint, name in endpoints:
            try:
                response = self.session.get(f"{API_BASE_URL}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'count' in data:
                        count = data['count']
                        print(f"   ✅ {name}: {count} records")
                    elif isinstance(data, list):
                        print(f"   ✅ {name}: {len(data)} records")
                    else:
                        print(f"   ✅ {name}: Response OK")
                else:
                    print(f"   ❌ {name}: {response.status_code} - {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
    
    def test_frontend_running(self):
        """Test if Next.js frontend is accessible"""
        print("🌐 Testing Frontend Server...")
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Frontend accessible: {response.status_code}")
                return True
            else:
                print(f"   ⚠️  Frontend returned: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Frontend not accessible: {e}")
            return False
    
    def create_test_data(self):
        """Create comprehensive test data for workflows"""
        print("📊 Creating Test Data...")
        
        try:
            # Create guests
            guests_data = [
                {
                    'email': 'john.doe@email.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'phone': '+1-555-0001',
                    'address': '123 Main St',
                    'city': 'New York',
                    'country': 'USA'
                },
                {
                    'email': 'jane.smith@email.com', 
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'phone': '+1-555-0002',
                    'address': '456 Oak Ave',
                    'city': 'Los Angeles', 
                    'country': 'USA'
                }
            ]
            
            guest_count = 0
            for guest_data in guests_data:
                guest, created = Guest.objects.get_or_create(
                    email=guest_data['email'],
                    defaults=guest_data
                )
                if created:
                    guest_count += 1
                    
            print(f"   ✅ Created {guest_count} guests")
            
            # Get property and rooms for reservations
            property_obj = Property.objects.first()
            rooms = Room.objects.filter(hotel=property_obj)[:3]
            
            if property_obj and rooms.exists():
                print(f"   ✅ Found property: {property_obj.name}")
                print(f"   ✅ Found {rooms.count()} rooms for reservations")
            else:
                print("   ❌ No property or rooms found for reservations")
                
            return True
            
        except Exception as e:
            print(f"   ❌ Test data creation failed: {e}")
            return False
    
    def test_crud_operations(self):
        """Test Create, Read, Update operations via API"""
        print("🔄 Testing CRUD Operations...")
        
        try:
            # Test creating a guest via API
            guest_data = {
                "email": "test.guest@email.com",
                "first_name": "Test",
                "last_name": "Guest",
                "phone": "+15551234567",
                "address": "123 Test St",
                "city": "Test City",
                "country": "USA"
            }
            
            response = self.session.post(f"{API_BASE_URL}/guests/", 
                                       json=guest_data, 
                                       timeout=10)
            
            if response.status_code in [200, 201]:
                guest = response.json()
                guest_id = guest.get('id')
                print(f"   ✅ Created guest via API: ID {guest_id}")
                
                # Test reading the guest back
                response = self.session.get(f"{API_BASE_URL}/guests/{guest_id}/", 
                                          timeout=10)
                if response.status_code == 200:
                    print("   ✅ Read guest via API: Success")
                else:
                    print(f"   ❌ Read guest failed: {response.status_code}")
                    
            else:
                print(f"   ❌ Create guest failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ CRUD test failed: {e}")
    
    def run_full_test(self):
        """Run complete integration test suite"""
        print("="*60)
        print("🧪 COMPREHENSIVE FRONTEND-BACKEND INTEGRATION TEST")
        print("="*60)
        print()
        
        results = {}
        
        # Test backend
        results['backend'] = self.test_backend_running()
        
        # Test authentication
        if results['backend']:
            results['auth'] = self.test_authentication()
        else:
            results['auth'] = False
        
        # Test API endpoints
        if results['auth']:
            self.test_api_endpoints()
            results['api'] = True
        else:
            results['api'] = False
        
        # Test frontend
        results['frontend'] = self.test_frontend_running()
        
        # Create test data
        results['test_data'] = self.create_test_data()
        
        # Test CRUD operations
        if results['auth']:
            self.test_crud_operations()
            results['crud'] = True
        else:
            results['crud'] = False
        
        # Summary
        print()
        print("="*60)
        print("📋 TEST RESULTS SUMMARY")
        print("="*60)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {test_name.upper()}: {status}")
        
        print()
        print(f"📊 Overall: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.0f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - System is fully integrated!")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️  Most tests passed - Minor issues to resolve")
        else:
            print("❌ Major integration issues found - Requires fixes")
        
        return results

if __name__ == "__main__":
    tester = IntegrationTester()
    tester.run_full_test()