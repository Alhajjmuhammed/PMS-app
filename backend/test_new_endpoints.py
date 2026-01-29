#!/usr/bin/env python
"""
Test script for newly implemented API endpoints.
Tests: Company, Building, Floor, Room Amenity, and Room Type CRUD operations.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
CREDENTIALS = {
    "username": "admin@pms.com",
    "password": "admin123"
}

class TestRunner:
    def __init__(self):
        self.token = None
        self.property_id = None
        self.test_results = []
    
    def login(self):
        """Authenticate and get token."""
        print("\n=== Authentication ===")
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login/",
                json=CREDENTIALS
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access')
                self.property_id = data.get('user', {}).get('assigned_property')
                print("✓ Login successful")
                return True
            else:
                print(f"✗ Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False
    
    def headers(self):
        """Return auth headers."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_endpoint(self, method, endpoint, data=None, expected_status=None):
        """Generic endpoint test."""
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers())
            elif method == "POST":
                response = requests.post(url, headers=self.headers(), json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers(), json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers(), json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers())
            else:
                return None, "Invalid method"
            
            success = (expected_status is None and 200 <= response.status_code < 300) or \
                     (expected_status == response.status_code)
            
            return response, None
        except Exception as e:
            return None, str(e)
    
    def test_company_api(self):
        """Test Company Management API."""
        print("\n=== Testing Company API ===")
        
        # 1. List companies
        print("1. GET /guests/companies/")
        response, error = self.test_endpoint("GET", "/guests/companies/")
        if response and response.status_code == 200:
            print(f"   ✓ Status: {response.status_code}")
        else:
            print(f"   ✗ Failed: {error or response.status_code}")
        
        # 2. Create company
        print("2. POST /guests/companies/")
        company_data = {
            "name": "Test Corporation Ltd",
            "code": "TESTCORP",
            "company_type": "CORPORATE",
            "contact_person": "John Doe",
            "email": "john@testcorp.com",
            "phone": "+1234567890",
            "credit_limit": "50000.00",
            "discount_percentage": "10.00"
        }
        response, error = self.test_endpoint("POST", "/guests/companies/", company_data, 201)
        if response and response.status_code == 201:
            company_id = response.json().get('id')
            print(f"   ✓ Status: {response.status_code}, ID: {company_id}")
            
            # 3. Get company detail
            print(f"3. GET /guests/companies/{company_id}/")
            response, _ = self.test_endpoint("GET", f"/guests/companies/{company_id}/")
            if response and response.status_code == 200:
                print(f"   ✓ Status: {response.status_code}")
            
            # 4. Update company
            print(f"4. PATCH /guests/companies/{company_id}/")
            update_data = {"discount_percentage": "15.00"}
            response, _ = self.test_endpoint("PATCH", f"/guests/companies/{company_id}/", update_data)
            if response and response.status_code == 200:
                print(f"   ✓ Status: {response.status_code}")
            
            # 5. Delete company
            print(f"5. DELETE /guests/companies/{company_id}/")
            response, _ = self.test_endpoint("DELETE", f"/guests/companies/{company_id}/")
            if response and response.status_code == 204:
                print(f"   ✓ Status: {response.status_code}")
        else:
            print(f"   ✗ Failed: {error or response.status_code}")
    
    def test_building_floor_api(self):
        """Test Building and Floor Management API."""
        print("\n=== Testing Building & Floor API ===")
        
        # 1. List buildings
        print("1. GET /properties/buildings/")
        response, error = self.test_endpoint("GET", "/properties/buildings/")
        if response and response.status_code == 200:
            print(f"   ✓ Status: {response.status_code}")
        
        # 2. Create building
        if self.property_id:
            print("2. POST /properties/buildings/")
            building_data = {
                "property": self.property_id,
                "name": "Test Building A",
                "code": "BLDG-A",
                "floors": 5,
                "description": "Test building for API testing"
            }
            response, error = self.test_endpoint("POST", "/properties/buildings/", building_data, 201)
            if response and response.status_code == 201:
                building_id = response.json().get('id')
                print(f"   ✓ Status: {response.status_code}, ID: {building_id}")
                
                # 3. Create floor
                print("3. POST /properties/floors/")
                floor_data = {
                    "building": building_id,
                    "number": 1,
                    "name": "First Floor",
                    "description": "Ground floor"
                }
                response, _ = self.test_endpoint("POST", "/properties/floors/", floor_data, 201)
                if response and response.status_code == 201:
                    floor_id = response.json().get('id')
                    print(f"   ✓ Status: {response.status_code}, ID: {floor_id}")
                    
                    # 4. Get floor detail
                    print(f"4. GET /properties/floors/{floor_id}/")
                    response, _ = self.test_endpoint("GET", f"/properties/floors/{floor_id}/")
                    if response and response.status_code == 200:
                        print(f"   ✓ Status: {response.status_code}")
                    
                    # 5. Delete floor
                    print(f"5. DELETE /properties/floors/{floor_id}/")
                    response, _ = self.test_endpoint("DELETE", f"/properties/floors/{floor_id}/")
                    if response and response.status_code == 204:
                        print(f"   ✓ Status: {response.status_code}")
                
                # 6. Delete building
                print(f"6. DELETE /properties/buildings/{building_id}/")
                response, _ = self.test_endpoint("DELETE", f"/properties/buildings/{building_id}/")
                if response and response.status_code == 204:
                    print(f"   ✓ Status: {response.status_code}")
            else:
                print(f"   ✗ Failed: {error or response.status_code}")
        else:
            print("   ! Skipped - No property assigned to user")
    
    def test_amenity_api(self):
        """Test Room Amenity Management API."""
        print("\n=== Testing Room Amenity API ===")
        
        # 1. List amenities
        print("1. GET /rooms/amenities/")
        response, error = self.test_endpoint("GET", "/rooms/amenities/")
        if response and response.status_code == 200:
            print(f"   ✓ Status: {response.status_code}")
        
        # 2. Create amenity
        print("2. POST /rooms/amenities/")
        amenity_data = {
            "name": "Smart TV",
            "code": "SMART_TV",
            "category": "ENTERTAINMENT",
            "description": "55-inch 4K Smart TV",
            "icon": "tv"
        }
        response, error = self.test_endpoint("POST", "/rooms/amenities/", amenity_data, 201)
        if response and response.status_code == 201:
            amenity_id = response.json().get('id')
            print(f"   ✓ Status: {response.status_code}, ID: {amenity_id}")
            
            # 3. Get amenity detail
            print(f"3. GET /rooms/amenities/{amenity_id}/")
            response, _ = self.test_endpoint("GET", f"/rooms/amenities/{amenity_id}/")
            if response and response.status_code == 200:
                print(f"   ✓ Status: {response.status_code}")
            
            # 4. Update amenity
            print(f"4. PATCH /rooms/amenities/{amenity_id}/")
            update_data = {"description": "65-inch 4K Smart TV with streaming"}
            response, _ = self.test_endpoint("PATCH", f"/rooms/amenities/{amenity_id}/", update_data)
            if response and response.status_code == 200:
                print(f"   ✓ Status: {response.status_code}")
            
            # 5. Delete amenity
            print(f"5. DELETE /rooms/amenities/{amenity_id}/")
            response, _ = self.test_endpoint("DELETE", f"/rooms/amenities/{amenity_id}/")
            if response and response.status_code == 204:
                print(f"   ✓ Status: {response.status_code}")
        else:
            print(f"   ✗ Failed: {error or response.status_code}")
    
    def test_room_type_api(self):
        """Test Room Type CRUD operations."""
        print("\n=== Testing Room Type API ===")
        
        # 1. List room types
        print("1. GET /rooms/types/")
        response, error = self.test_endpoint("GET", "/rooms/types/")
        if response and response.status_code == 200:
            print(f"   ✓ Status: {response.status_code}")
        
        # 2. Create room type
        if self.property_id:
            print("2. POST /rooms/types/")
            room_type_data = {
                "property": self.property_id,
                "name": "Test Suite",
                "code": "TST-STE",
                "description": "Test suite room type",
                "base_rate": "250.00",
                "max_occupancy": 4,
                "max_adults": 2,
                "max_children": 2,
                "bed_type": "King"
            }
            response, error = self.test_endpoint("POST", "/rooms/types/", room_type_data, 201)
            if response and response.status_code == 201:
                room_type_id = response.json().get('id')
                print(f"   ✓ Status: {response.status_code}, ID: {room_type_id}")
                
                # 3. Get room type detail
                print(f"3. GET /rooms/types/{room_type_id}/")
                response, _ = self.test_endpoint("GET", f"/rooms/types/{room_type_id}/")
                if response and response.status_code == 200:
                    print(f"   ✓ Status: {response.status_code}")
                
                # 4. Update room type
                print(f"4. PATCH /rooms/types/{room_type_id}/")
                update_data = {"base_rate": "275.00"}
                response, _ = self.test_endpoint("PATCH", f"/rooms/types/{room_type_id}/", update_data)
                if response and response.status_code == 200:
                    print(f"   ✓ Status: {response.status_code}")
                
                # 5. Delete room type
                print(f"5. DELETE /rooms/types/{room_type_id}/")
                response, _ = self.test_endpoint("DELETE", f"/rooms/types/{room_type_id}/")
                if response and response.status_code == 204:
                    print(f"   ✓ Status: {response.status_code}")
            else:
                print(f"   ✗ Failed: {error or response.status_code}")
        else:
            print("   ! Skipped - No property assigned to user")
    
    def run_all_tests(self):
        """Run all tests."""
        print("\n" + "="*60)
        print("  PMS API - New Endpoints Test Suite")
        print("  Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*60)
        
        if not self.login():
            print("\n✗ Tests aborted - Authentication failed")
            return False
        
        self.test_company_api()
        self.test_building_floor_api()
        self.test_amenity_api()
        self.test_room_type_api()
        
        print("\n" + "="*60)
        print("  Test Suite Completed")
        print("="*60)
        return True


if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all_tests()
