#!/usr/bin/env python
"""
Hotel PMS - Database Test Script

This script tests database connectivity and performs basic CRUD operations
to ensure the database configuration is working correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from apps.accounts.models import User
from apps.properties.models import Property, Building, Department
from apps.rooms.models import RoomType, Room
from apps.guests.models import Guest, Company


def test_database_connection():
    """Test basic database connectivity."""
    print("\n" + "="*50)
    print("Testing Database Connection")
    print("="*50)
    
    try:
        connection.ensure_connection()
        print("✅ Database connection successful")
        print(f"   Database: {connection.settings_dict['NAME']}")
        print(f"   Engine: {connection.settings_dict['ENGINE']}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_model_queries():
    """Test basic model queries."""
    print("\n" + "="*50)
    print("Testing Model Queries")
    print("="*50)
    
    try:
        # Test User model
        user_count = User.objects.count()
        print(f"✅ User.objects.count() = {user_count}")
        
        # Test Property model
        property_count = Property.objects.count()
        print(f"✅ Property.objects.count() = {property_count}")
        
        # Test Room model
        room_count = Room.objects.count()
        print(f"✅ Room.objects.count() = {room_count}")
        
        # Test Guest model
        guest_count = Guest.objects.count()
        print(f"✅ Guest.objects.count() = {guest_count}")
        
        return True
    except Exception as e:
        print(f"❌ Model query failed: {e}")
        return False


def test_model_creation():
    """Test creating model instances."""
    print("\n" + "="*50)
    print("Testing Model Creation (Dry Run)")
    print("="*50)
    
    try:
        # Test creating a property (without saving)
        property_obj = Property(
            name="Test Hotel",
            code="TEST001",
            address="123 Test St",
            city="Test City",
            country="Test Country"
        )
        print(f"✅ Can create Property instance: {property_obj}")
        
        # Test creating a guest (without saving)
        guest = Guest(
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            email="john@example.com"
        )
        print(f"✅ Can create Guest instance: {guest}")
        
        print("\n⚠️  Note: No data was saved to database (dry run)")
        return True
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False


def test_relationships():
    """Test model relationships."""
    print("\n" + "="*50)
    print("Testing Model Relationships")
    print("="*50)
    
    try:
        # Check if we have any properties to test relationships
        if Property.objects.exists():
            property_obj = Property.objects.first()
            print(f"✅ Found property: {property_obj.name}")
            
            # Test reverse relationship
            buildings = property_obj.buildings.count()
            print(f"✅ Property has {buildings} building(s)")
            
            rooms = property_obj.rooms.count()
            print(f"✅ Property has {rooms} room(s)")
        else:
            print("ℹ️  No properties found (create some to test relationships)")
        
        return True
    except Exception as e:
        print(f"❌ Relationship test failed: {e}")
        return False


def show_database_stats():
    """Display comprehensive database statistics."""
    print("\n" + "="*50)
    print("Database Statistics")
    print("="*50)
    
    stats = {
        'Users': User.objects.count(),
        'Properties': Property.objects.count(),
        'Buildings': Building.objects.count(),
        'Departments': Department.objects.count(),
        'Room Types': RoomType.objects.count(),
        'Rooms': Room.objects.count(),
        'Guests': Guest.objects.count(),
        'Companies': Company.objects.count(),
    }
    
    for model_name, count in stats.items():
        print(f"  {model_name:.<30} {count:>5}")
    
    print()


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("Hotel PMS - Database Test Suite")
    print("="*50)
    
    results = []
    
    # Run tests
    results.append(("Database Connection", test_database_connection()))
    results.append(("Model Queries", test_model_queries()))
    results.append(("Model Creation", test_model_creation()))
    results.append(("Model Relationships", test_relationships()))
    
    # Show statistics
    show_database_stats()
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:.<30} {status}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Database is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
