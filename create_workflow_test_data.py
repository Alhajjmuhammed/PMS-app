#!/usr/bin/env python3
"""
Create comprehensive test data for hotel workflows
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Add Django settings
sys.path.insert(0, '/home/easyfix/Documents/PMS/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User
from apps.properties.models import Property
from apps.rooms.models import Room, RoomType
from apps.guests.models import Guest
from apps.reservations.models import Reservation, ReservationRoom
from apps.billing.models import Folio, FolioCharge, Invoice, ChargeCode
from apps.housekeeping.models import HousekeepingTask
from apps.maintenance.models import MaintenanceRequest

def create_comprehensive_test_data():
    print("🏨 Creating Comprehensive Test Data for Hotel Workflows")
    print("="*60)
    
    try:
        # Get existing data
        property_obj = Property.objects.first()
        if not property_obj:
            print("❌ No property found. Run basic setup first.")
            return False
            
        rooms = Room.objects.filter(hotel=property_obj)
        room_types = RoomType.objects.filter(hotel=property_obj)
        
        print(f"📍 Using Property: {property_obj.name}")
        print(f"🏠 Available Rooms: {rooms.count()}")
        print(f"🛏️  Room Types: {room_types.count()}")
        print()
        
        # 0. Create Charge Codes if they don't exist
        print("💳 Creating Charge Codes...")
        
        charge_codes_data = [
            {'code': 'ROOM', 'name': 'Room Charge', 'category': 'ROOM', 'default_amount': Decimal('150.00')},
            {'code': 'RESTAURANT', 'name': 'Restaurant', 'category': 'FOOD', 'default_amount': Decimal('50.00')},
            {'code': 'MINIBAR', 'name': 'Minibar', 'category': 'MINIBAR', 'default_amount': Decimal('25.00')},
            {'code': 'LAUNDRY', 'name': 'Laundry Service', 'category': 'LAUNDRY', 'default_amount': Decimal('15.00')},
            {'code': 'PARKING', 'name': 'Parking', 'category': 'PARKING', 'default_amount': Decimal('20.00')},
        ]
        
        created_codes = 0
        for code_data in charge_codes_data:
            charge_code, created = ChargeCode.objects.get_or_create(
                code=code_data['code'],
                defaults=code_data
            )
            if created:
                created_codes += 1
                
        print(f"   ✅ Created {created_codes} new charge codes")
        total_codes = ChargeCode.objects.count()
        print(f"   📊 Total charge codes: {total_codes}")
        print()
        
        # 1. Create Guests
        print("👥 Creating Guest Profiles...")
        guests_data = [
            {
                'email': 'john.doe@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+15551234001',
                'address': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'postal_code': '10001',
                'date_of_birth': date(1985, 5, 15),
                'nationality': 'American',
                'id_type': 'PASSPORT',
                'id_number': 'US123456789'
            },
            {
                'email': 'jane.smith@email.com',
                'first_name': 'Jane',
                'last_name': 'Smith', 
                'phone': '+15551234002',
                'address': '456 Oak Avenue',
                'city': 'Los Angeles',
                'state': 'CA',
                'country': 'USA',
                'postal_code': '90210',
                'date_of_birth': date(1990, 8, 22),
                'nationality': 'American',
                'id_type': 'DRIVERS_LICENSE',
                'id_number': 'CA987654321'
            },
            {
                'email': 'mike.johnson@email.com',
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'phone': '+15551234003',
                'address': '789 Pine Road',
                'city': 'Chicago',
                'state': 'IL',
                'country': 'USA',
                'postal_code': '60601',
                'date_of_birth': date(1982, 12, 3),
                'nationality': 'American',
                'id_type': 'PASSPORT',
                'id_number': 'US987654321'
            },
            {
                'email': 'sarah.wilson@email.com',
                'first_name': 'Sarah',
                'last_name': 'Wilson',
                'phone': '+15551234004', 
                'address': '321 Elm Street',
                'city': 'Miami',
                'state': 'FL',
                'country': 'USA',
                'postal_code': '33101',
                'date_of_birth': date(1988, 3, 18),
                'nationality': 'American',
                'id_type': 'DRIVERS_LICENSE',
                'id_number': 'FL456789123'
            }
        ]
        
        created_guests = 0
        for guest_data in guests_data:
            guest, created = Guest.objects.get_or_create(
                email=guest_data['email'],
                defaults=guest_data
            )
            if created:
                created_guests += 1
                
        print(f"   ✅ Created {created_guests} new guests")
        total_guests = Guest.objects.count()
        print(f"   📊 Total guests in system: {total_guests}")
        print()
        
        # 2. Create Reservations
        print("📅 Creating Reservations...")
        
        guests = Guest.objects.all()
        available_rooms = list(rooms)
        
        # Create reservations for different scenarios
        reservations_data = [
            # Current guest (checked in)
            {
                'guest': guests[0],
                'room': available_rooms[0],
                'check_in_date': date.today() - timedelta(days=2),
                'check_out_date': date.today() + timedelta(days=3),
                'status': 'CONFIRMED',
                'adults': 2,
                'children': 0,
                'rate_per_night': Decimal('150.00'),
                'source': 'DIRECT',
                'special_requests': 'Late check-out requested'
            },
            # Future reservation
            {
                'guest': guests[1],
                'room': available_rooms[1],
                'check_in_date': date.today() + timedelta(days=5),
                'check_out_date': date.today() + timedelta(days=8),
                'status': 'CONFIRMED',
                'adults': 1,
                'children': 1,
                'rate_per_night': Decimal('250.00'),
                'source': 'WEBSITE',
                'special_requests': 'Ground floor room preferred'
            },
            # Past reservation (checked out)
            {
                'guest': guests[2],
                'room': available_rooms[2],
                'check_in_date': date.today() - timedelta(days=10),
                'check_out_date': date.today() - timedelta(days=7),
                'status': 'CHECKED_OUT',
                'adults': 2,
                'children': 2,
                'rate_per_night': Decimal('450.00'),
                'source': 'PHONE',
                'special_requests': 'Extra towels, baby crib'
            }
        ]
        
        created_reservations = 0
        for res_data in reservations_data:
            room = res_data.pop('room')
            rate_per_night = res_data.pop('rate_per_night')
            
            nights = (res_data['check_out_date'] - res_data['check_in_date']).days
            total_amount = rate_per_night * nights
            res_data['total_amount'] = total_amount
            res_data['hotel'] = property_obj
            
            reservation, created = Reservation.objects.get_or_create(
                guest=res_data['guest'],
                check_in_date=res_data['check_in_date'],
                check_out_date=res_data['check_out_date'],
                defaults=res_data
            )
            
            if created:
                created_reservations += 1
                
                # Create ReservationRoom
                reservation_room = ReservationRoom.objects.create(
                    reservation=reservation,
                    room=room,
                    room_type=room.room_type,
                    rate_per_night=rate_per_night,
                    total_rate=total_amount,
                    adults=reservation.adults,
                    children=reservation.children
                )
                
        print(f"   ✅ Created {created_reservations} new reservations")
        total_reservations = Reservation.objects.count()
        print(f"   📊 Total reservations: {total_reservations}")
        print()
        
        # 3. Create Billing Data (Folios and Charges)
        print("💰 Creating Billing Data...")
        
        reservations = Reservation.objects.all()
        created_folios = 0
        created_charges = 0
        
        for reservation in reservations:
            # Create folio for each reservation
            folio, created = Folio.objects.get_or_create(
                reservation=reservation,
                defaults={
                    'folio_number': f'F{reservation.id:06d}',
                    'guest': reservation.guest,
                    'status': 'OPEN' if reservation.status == 'CONFIRMED' else 'CLOSED',
                    'total_charges': reservation.total_amount,
                    'total_taxes': reservation.total_amount * Decimal('0.10'),  # 10% tax
                    'total_payments': reservation.total_amount * Decimal('1.10') if reservation.status == 'COMPLETED' else Decimal('0.00')
                }
            )
            
            if created:
                created_folios += 1
                
                # Get charge codes
                room_code = ChargeCode.objects.get(code='ROOM')
                restaurant_code = ChargeCode.objects.get(code='RESTAURANT')
                minibar_code = ChargeCode.objects.get(code='MINIBAR')
                
                # Get the reservation room for rate info
                reservation_room = reservation.rooms.first()
                
                # Room charges
                room_charge = FolioCharge.objects.create(
                    folio=folio,
                    charge_code=room_code,
                    charge_date=reservation.check_in_date,
                    description=f'Room {reservation_room.room.room_number} - {nights} nights',
                    quantity=nights,
                    unit_price=reservation_room.rate_per_night,
                    amount=reservation_room.total_rate
                )
                created_charges += 1
                
                # Additional charges based on reservation
                if reservation.guest.first_name == 'John':  # Current guest
                    # Restaurant charge
                    restaurant_charge = FolioCharge.objects.create(
                        folio=folio,
                        charge_code=restaurant_code,
                        charge_date=reservation.check_in_date + timedelta(days=1),
                        description='Restaurant - Dinner for 2',
                        quantity=1,
                        unit_price=Decimal('85.50'),
                        amount=Decimal('85.50')
                    )
                    created_charges += 1
                    
                    # Mini bar charge
                    minibar_charge = FolioCharge.objects.create(
                        folio=folio,
                        charge_code=minibar_code,
                        charge_date=reservation.check_in_date + timedelta(days=2),
                        description='Mini Bar - Beverages',
                        quantity=1,
                        unit_price=Decimal('24.75'),
                        amount=Decimal('24.75')
                    )
                    created_charges += 1
                
        print(f"   ✅ Created {created_folios} new folios")
        print(f"   ✅ Created {created_charges} new charges")
        total_folios = Folio.objects.count()
        print(f"   📊 Total folios: {total_folios}")
        print()
        
        # 4. Create Housekeeping Tasks
        print("🧹 Creating Housekeeping Tasks...")
        
        hk_tasks_data = [
            {
                'room': available_rooms[0],
                'task_type': 'DEEP_CLEAN',
                'priority': 'HIGH',
                'notes': 'Deep clean after checkout - extra attention to bathroom',
                'status': 'IN_PROGRESS',
                'special_instructions': 'Use eco-friendly cleaning products'
            },
            {
                'room': available_rooms[1], 
                'task_type': 'CLEANING',
                'priority': 'NORMAL',
                'notes': 'Regular maintenance cleaning',
                'status': 'IN_PROGRESS',
                'special_instructions': 'Standard cleaning protocol'
            },
            {
                'room': available_rooms[2],
                'task_type': 'INSPECTION',
                'priority': 'LOW',
                'notes': 'Quality inspection after cleaning',
                'status': 'COMPLETED',
                'inspection_notes': 'All items checked and approved'
            }
        ]
        
        # Get housekeeping user
        hk_user = User.objects.filter(role='HOUSEKEEPING').first()
        
        created_hk_tasks = 0
        for task_data in hk_tasks_data:
            if hk_user:
                task_data['assigned_to'] = hk_user
            
            task, created = HousekeepingTask.objects.get_or_create(
                room=task_data['room'],
                task_type=task_data['task_type'],
                defaults=task_data
            )
            if created:
                created_hk_tasks += 1
                
        print(f"   ✅ Created {created_hk_tasks} new housekeeping tasks")
        total_hk_tasks = HousekeepingTask.objects.count()
        print(f"   📊 Total housekeeping tasks: {total_hk_tasks}")
        print()
        
        # 5. Create Maintenance Requests
        print("🔧 Creating Maintenance Requests...")
        
        maint_requests_data = [
            {
                'room': available_rooms[3],
                'request_type': 'PLUMBING',
                'priority': 'HIGH',
                'title': 'Leaky Faucet',
                'description': 'Leaky faucet in bathroom sink needs repair',
                'status': 'PENDING',
                'property': property_obj
            },
            {
                'room': available_rooms[4],
                'request_type': 'ELECTRICAL',
                'priority': 'MEDIUM',
                'title': 'Light Fixture Issue',
                'description': 'Light fixture not working properly in bedroom',
                'status': 'IN_PROGRESS',
                'property': property_obj
            },
            {
                'room': available_rooms[5],
                'request_type': 'HVAC',
                'priority': 'LOW',
                'title': 'AC Unit Noise',
                'description': 'AC unit making unusual noise - needs inspection',
                'status': 'COMPLETED',
                'resolution_notes': 'Cleaned and serviced AC unit, noise resolved',
                'property': property_obj
            }
        ]
        
        # Get maintenance user
        maint_user = User.objects.filter(role='MAINTENANCE').first()
        
        created_maint_requests = 0
        for i, req_data in enumerate(maint_requests_data):
            req_data['request_number'] = f'MR{i+1:06d}'
            if maint_user:
                req_data['assigned_to'] = maint_user
                
            request, created = MaintenanceRequest.objects.get_or_create(
                room=req_data['room'],
                request_type=req_data['request_type'],
                defaults=req_data
            )
            if created:
                created_maint_requests += 1
                
        print(f"   ✅ Created {created_maint_requests} new maintenance requests")
        total_maint_requests = MaintenanceRequest.objects.count()
        print(f"   📊 Total maintenance requests: {total_maint_requests}")
        print()
        
        # 6. Summary
        print("="*60)
        print("📊 COMPREHENSIVE TEST DATA SUMMARY")
        print("="*60)
        print(f"👥 Guests: {Guest.objects.count()} records")
        print(f"📅 Reservations: {Reservation.objects.count()} records")
        print(f"💰 Folios: {Folio.objects.count()} records")
        print(f"📋 Charges: {FolioCharge.objects.count()} records")
        print(f"🧹 Housekeeping Tasks: {HousekeepingTask.objects.count()} records")
        print(f"🔧 Maintenance Requests: {MaintenanceRequest.objects.count()} records")
        print()
        print("✅ COMPREHENSIVE TEST DATA CREATION COMPLETE!")
        print("🎯 System now has realistic data for all major workflows.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_comprehensive_test_data()