"""
Simplified Test Data Population Script
Populates all models with realistic data for testing
"""
import os
import sys
import django
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

# Setup Django
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

# Import all models
from apps.properties.models import Property, Building, Floor, Department, PropertyAmenity, TaxConfiguration
from apps.rooms.models import Room, RoomType, RoomAmenity, RoomTypeAmenity, RoomBlock, RoomStatusLog
from apps.guests.models import Guest, Company, GuestDocument, GuestPreference, LoyaltyProgram, LoyaltyTier, LoyaltyTransaction
from apps.reservations.models import Reservation, ReservationRoom, GroupBooking, ReservationLog, ReservationRateDetail
from apps.frontdesk.models import CheckIn, CheckOut, GuestMessage, RoomMove, WalkIn
from apps.billing.models import Folio, FolioCharge, Invoice, Payment, ChargeCode, CashierShift
from apps.housekeeping.models import HousekeepingTask, HousekeepingSchedule, RoomInspection, AmenityInventory, LinenInventory, StockMovement
from apps.maintenance.models import MaintenanceRequest, MaintenanceLog, Asset
from apps.pos.models import Outlet, MenuCategory, MenuItem, POSOrder, POSOrderItem
from apps.rates.models import RatePlan, RoomRate, DateRate, Season, Discount, Package, YieldRule
from apps.channels.models import Channel, PropertyChannel, RoomTypeMapping, RatePlanMapping, ChannelReservation, AvailabilityUpdate, RateUpdate
from apps.reports.models import NightAudit, DailyStatistics, MonthlyStatistics, AuditLog, ReportTemplate
from apps.notifications.models import Notification, NotificationTemplate, Alert, EmailLog, SMSLog, PushDeviceToken
from apps.accounts.models import User, StaffProfile, ActivityLog

print("\n" + "="*80)
print("COMPREHENSIVE TEST DATA GENERATION".center(80))
print("="*80 + "\n")

User = get_user_model()
stats = {}

# Get existing data
properties = list(Property.objects.all()[:2])
users = list(User.objects.all())

if not properties:
    print("❌ ERROR: No properties found. Please run basic setup first.")
    sys.exit(1)

property1 = properties[0]
property2 = properties[1] if len(properties) > 1 else properties[0]

print(f"✓ Using properties: {property1.name}, {property2.name}\n")

with transaction.atomic():
    
    # 1. PROPERTIES SETUP
    print("1. PROPERTIES MODULE")
    print("-" * 80)
    
    # Buildings
    buildings = list(Building.objects.all())
    if not buildings:
        buildings = [
            Building.objects.create(property=property1, name="Main Building", code="MB1", description="Primary building"),
            Building.objects.create(property=property2, name="East Wing", code="EW1", description="East wing building")
        ]
    print(f"   ✓ Buildings: {len(buildings)}")
    
    # Floors
    floors = list(Floor.objects.all())
    if Floor.objects.count() < 5:
        for building in buildings[:1]:
            for i in range(1, 6):
                Floor.objects.get_or_create(building=building, number=i, defaults={'name': f"Floor {i}"})
        floors = list(Floor.objects.all())
    print(f"   ✓ Floors: {len(floors)}")
    
    # Departments
    if Department.objects.count() < 3:
        for prop in properties[:1]:
            for name, code in [('Front Office', 'FO'), ('Housekeeping', 'HK'), ('Maintenance', 'MN')]:
                Department.objects.get_or_create(property=prop, code=code, defaults={'name': name})
    print(f"   ✓ Departments: {Department.objects.count()}")
    
    # Property Amenities (no is_available field)
    if PropertyAmenity.objects.count() < 3:
        for prop in properties[:1]:
            for name in ['Swimming Pool', 'Gym', 'Restaurant']:
                PropertyAmenity.objects.get_or_create(
                    property=prop, name=name,
                    defaults={'description': f"{name} facility"}
                )
    print(f"   ✓ Property Amenities: {PropertyAmenity.objects.count()}")
    
    # Tax Configuration
    if TaxConfiguration.objects.count() < 1:
        TaxConfiguration.objects.get_or_create(
            property=property1, code='VAT',
            defaults={'name': 'VAT', 'rate': Decimal('15.00')}
        )
    print(f"   ✓ Tax Configurations: {TaxConfiguration.objects.count()}\n")
    
    # 2. ROOMS SETUP
    print("2. ROOMS MODULE")
    print("-" * 80)
    
    room_types = list(RoomType.objects.all())
    rooms = list(Room.objects.all())
    
    # More rooms
    if len(rooms) < 30:
        statuses = ['VACANT', 'OCCUPIED', 'DIRTY', 'CLEAN']
        for i in range(30 - len(rooms)):
            room_num = f"{100 + i}"
            if not Room.objects.filter(number=room_num, hotel=property1).exists():
                Room.objects.create(
                    hotel=property1,
                    number=room_num,
                    room_type=random.choice(room_types) if room_types else None,
                    floor=random.choice(floors) if floors else None,
                    status=random.choice(statuses),
                    housekeeping_status='CLEAN'
                )
        rooms = list(Room.objects.all())
    print(f"   ✓ Rooms: {len(rooms)}\n")
    
    # 3. GUESTS SETUP
    print("3. GUESTS MODULE")
    print("-" * 80)
    
    # Companies
    companies = list(Company.objects.all())
    if not companies:
        for name in ['Tech Corp', 'Global Inc', 'Innovations Ltd']:
            companies.append(Company.objects.create(
                name=name,
                email=f"contact@{name.lower().replace(' ', '')}.com",
                phone="+1-555-1234",
                country="USA"
            ))
    print(f"   ✓ Companies: {len(companies)}")
    
    # More guests
    guests = list(Guest.objects.all())
    if len(guests) < 20:
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones']
        
        for i in range(20 - len(guests)):
            first = random.choice(first_names)
            last = random.choice(last_names)
            Guest.objects.create(
                first_name=first,
                last_name=last,
                email=f"{first.lower()}.{last.lower()}{i}@email.com",
                phone=f"+1-555-{1000+i}",
                country="USA"
            )
        guests = list(Guest.objects.all())
    print(f"   ✓ Guests: {len(guests)}")
    
    # Loyalty Program
    if not LoyaltyProgram.objects.exists():
        program = LoyaltyProgram.objects.create(name="Rewards Plus", description="Premier loyalty program")
        for name, points in [('Silver', 0), ('Gold', 500), ('Platinum', 2000)]:
            LoyaltyTier.objects.create(
                program=program, name=name, min_points=points,
                discount_percentage=Decimal('5.0')
            )
    print(f"   ✓ Loyalty Program: {LoyaltyProgram.objects.count()}")
    print(f"   ✓ Loyalty Tiers: {LoyaltyTier.objects.count()}\n")
    
    # 4. RATES SETUP
    print("4. RATES MODULE")
    print("-" * 80)
    
    # Rate Plans
    rate_plans = list(RatePlan.objects.all())
    if len(rate_plans) < 3:
        for code, name, rate in [('BAR', 'Best Available Rate', '150'), ('CORP', 'Corporate Rate', '120')]:
            rp, _ = RatePlan.objects.get_or_create(
                property=property1, code=code,
                defaults={'name': name, 'base_rate': Decimal(rate)}
            )
            rate_plans.append(rp)
    print(f"   ✓ Rate Plans: {len(rate_plans)}")
    
    # Room Rates
    if RoomRate.objects.count() < 3 and rate_plans and room_types:
        for rp in rate_plans:
            for rt in room_types:
                RoomRate.objects.get_or_create(
                    rate_plan=rp, room_type=rt,
                    defaults={'rate': rp.base_rate + Decimal('20')}
                )
    print(f"   ✓ Room Rates: {RoomRate.objects.count()}\n")
    
    # 5. RESERVATIONS
    print("5. RESERVATIONS MODULE")
    print("-" * 80)
    
    if Reservation.objects.count() < 15:
        today = date.today()
        
        # Past reservations
        for i in range(5):
            check_in = today - timedelta(days=random.randint(10, 30))
            Reservation.objects.create(
                property=property1,
                guest=random.choice(guests),
                check_in_date=check_in,
                check_out_date=check_in + timedelta(days=random.randint(2, 4)),
                adults=random.randint(1, 2),
                status='CHECKED_OUT',
                total_amount=Decimal(str(random.randint(300, 800)))
            )
        
        # Current reservations
        for i in range(5):
            check_in = today - timedelta(days=random.randint(0, 2))
            Reservation.objects.create(
                property=property1,
                guest=random.choice(guests),
                check_in_date=check_in,
                check_out_date=today + timedelta(days=random.randint(2, 4)),
                adults=random.randint(1, 2),
                status='CHECKED_IN',
                total_amount=Decimal(str(random.randint(300, 800)))
            )
        
        # Future reservations
        for i in range(5):
            check_in = today + timedelta(days=random.randint(5, 30))
            Reservation.objects.create(
                property=property1,
                guest=random.choice(guests),
                check_in_date=check_in,
                check_out_date=check_in + timedelta(days=random.randint(2, 5)),
                adults=random.randint(1, 3),
                status='CONFIRMED',
                total_amount=Decimal(str(random.randint(400, 1000)))
            )
    
    reservations = list(Reservation.objects.all())
    print(f"   ✓ Reservations: {len(reservations)}\n")
    
    # 6. FRONTDESK OPERATIONS
    print("6. FRONTDESK MODULE")
    print("-" * 80)
    
    checked_in_reservations = [r for r in reservations if r.status == 'CHECKED_IN']
    
    # Check-Ins
    if CheckIn.objects.count() < 5 and checked_in_reservations and rooms:
        for reservation in checked_in_reservations[:5]:
            if not hasattr(reservation, 'check_in'):
                CheckIn.objects.create(
                    reservation=reservation,
                    room=random.choice(rooms),
                    guest=reservation.guest,
                    expected_check_out=reservation.check_out_date,
                    registration_number=f"REG{random.randint(10000, 99999)}",
                    checked_in_by=users[0] if users else None
                )
    print(f"   ✓ Check-Ins: {CheckIn.objects.count()}")
    
    # Check-Outs
    checkins = list(CheckIn.objects.all())
    if CheckOut.objects.count() < 3 and len(checkins) > 0:
        for checkin in checkins[:3]:
            if not hasattr(checkin, 'check_out'):
                CheckOut.objects.create(
                    check_in=checkin,
                    total_charges=Decimal('500'),
                    total_payments=Decimal('500'),
                    balance=Decimal('0'),
                    checked_out_by=users[0] if users else None
                )
    print(f"   ✓ Check-Outs: {CheckOut.objects.count()}\n")
    
    # 7. BILLING
    print("7. BILLING MODULE")
    print("-" * 80)
    
    # Charge Codes
    if ChargeCode.objects.count() < 3:
        for code, name, category in [('ROOM', 'Room Charge', 'ROOM'), ('TAX', 'Tax', 'OTHER'), ('FOOD', 'Food & Beverage', 'FOOD')]:
            ChargeCode.objects.get_or_create(code=code, defaults={'name': name, 'category': category})
    charge_codes = list(ChargeCode.objects.all())
    print(f"   ✓ Charge Codes: {len(charge_codes)}")
    
    # Folios
    if Folio.objects.count() < 10 and reservations:
        for reservation in reservations[:10]:
            if not hasattr(reservation, 'folio'):
                Folio.objects.create(
                    reservation=reservation,
                    guest=reservation.guest,
                    folio_number=f"F{random.randint(1000, 9999)}",
                    status='OPEN'
                )
    folios = list(Folio.objects.all())
    print(f"   ✓ Folios: {len(folios)}")
    
    # Folio Charges
    if FolioCharge.objects.count() < 10 and folios and charge_codes:
        for folio in folios[:5]:
            FolioCharge.objects.create(
                folio=folio,
                charge_code=charge_codes[0],
                amount=Decimal('200'),
                description="Room charge"
            )
    print(f"   ✓ Folio Charges: {FolioCharge.objects.count()}")
    
    # Payments
    if Payment.objects.count() < 5 and folios:
        for folio in folios[:5]:
            Payment.objects.create(
                folio=folio,
                amount=Decimal('200'),
                payment_method='CREDIT_CARD',
                reference_number=f"PAY{random.randint(10000, 99999)}"
            )
    print(f"   ✓ Payments: {Payment.objects.count()}\n")
    
    # 8. HOUSEKEEPING
    print("8. HOUSEKEEPING MODULE")
    print("-" * 80)
    
    if HousekeepingTask.objects.count() < 15:
        for room in rooms[:15]:
            HousekeepingTask.objects.create(
                property=property1,
                room=room,
                task_type='CLEANING',
                status=random.choice(['PENDING', 'COMPLETED']),
                assigned_to=users[0] if users else None
            )
    print(f"   ✓ Housekeeping Tasks: {HousekeepingTask.objects.count()}")
    
    if AmenityInventory.objects.count() < 3:
        for item in ['Shampoo', 'Soap', 'Towels']:
            AmenityInventory.objects.get_or_create(
                property=property1, item_name=item,
                defaults={'quantity': 100, 'reorder_level': 20}
            )
    print(f"   ✓ Amenity Inventory: {AmenityInventory.objects.count()}\n")
    
    # 9. MAINTENANCE
    print("9. MAINTENANCE MODULE")
    print("-" * 80)
    
    if MaintenanceRequest.objects.count() < 5:
        for room in rooms[:5]:
            MaintenanceRequest.objects.create(
                property=property1,
                room=room,
                reported_by=users[0] if users else None,
                issue_type='ELECTRICAL',
                description='Light not working',
                priority='MEDIUM',
                status='OPEN'
            )
    print(f"   ✓ Maintenance Requests: {MaintenanceRequest.objects.count()}\n")
    
    # 10. POS
    print("10. POS MODULE")
    print("-" * 80)
    
    outlets = list(Outlet.objects.all())
    if not outlets:
        outlets = [Outlet.objects.create(property=property1, name="Main Restaurant", outlet_type='RESTAURANT')]
    print(f"   ✓ Outlets: {len(outlets)}")
    
    if MenuCategory.objects.count() < 2 and outlets:
        for name in ['Main Course', 'Beverages']:
            MenuCategory.objects.get_or_create(outlet=outlets[0], name=name)
    menu_categories = list(MenuCategory.objects.all())
    print(f"   ✓ Menu Categories: {len(menu_categories)}")
    
    if MenuItem.objects.count() < 3 and menu_categories:
        for name, price in [('Grilled Chicken', '25'), ('Coffee', '5')]:
            MenuItem.objects.get_or_create(
                category=menu_categories[0], name=name,
                defaults={'price': Decimal(price)}
            )
    print(f"   ✓ Menu Items: {MenuItem.objects.count()}\n")
    
    # 11. CHANNELS
    print("11. CHANNELS MODULE")
    print("-" * 80)
    
    channels = list(Channel.objects.all())
    if not channels:
        channels = [Channel.objects.create(name="Booking.com", code="BKG", api_url="https://api.booking.com")]
    print(f"   ✓ Channels: {len(channels)}")
    
    if PropertyChannel.objects.count() < 1 and channels:
        PropertyChannel.objects.get_or_create(property=property1, channel=channels[0])
    print(f"   ✓ Property Channels: {PropertyChannel.objects.count()}\n")
    
    # 12. REPORTS
    print("12. REPORTS MODULE")
    print("-" * 80)
    
    if DailyStatistics.objects.count() < 3:
        for i in range(3):
            date_val = date.today() - timedelta(days=i)
            rooms_sold = random.randint(10, 40)
            DailyStatistics.objects.get_or_create(
                property=property1, date=date_val,
                defaults={
                    'total_rooms': len(rooms),
                    'rooms_sold': rooms_sold,
                    'available_rooms': len(rooms) - rooms_sold,
                    'room_revenue': Decimal(str(random.randint(2000, 8000))),
                    'total_revenue': Decimal(str(random.randint(3000, 10000))),
                    'occupancy_percent': Decimal(str(round(rooms_sold / len(rooms) * 100, 2) if rooms else 0))
                }
            )
    print(f"   ✓ Daily Statistics: {DailyStatistics.objects.count()}\n")
    
    # 13. NOTIFICATIONS
    print("13. NOTIFICATIONS MODULE")
    print("-" * 80)
    
    if Notification.objects.count() < 5:
        for user in users[:3]:
            Notification.objects.create(
                user=user,
                title="Test Notification",
                message="System is working correctly",
                priority='NORMAL'
            )
    print(f"   ✓ Notifications: {Notification.objects.count()}")
    
    if NotificationTemplate.objects.count() < 2:
        for name, trigger in [('Check-in Confirmation', 'CHECK_IN'), ('Check-out Reminder', 'CHECK_OUT')]:
            NotificationTemplate.objects.get_or_create(
                name=name,
                defaults={'body': f'Template for {name}', 'template_type': 'EMAIL', 'trigger_event': trigger}
            )
    print(f"   ✓ Notification Templates: {NotificationTemplate.objects.count()}\n")
    
    # 14. ACCOUNTS
    print("14. ACCOUNTS MODULE")
    print("-" * 80)
    
    if ActivityLog.objects.count() < 5:
        for user in users[:3]:
            ActivityLog.objects.create(
                user=user,
                action='Test login',
                ip_address='127.0.0.1'
            )
    print(f"   ✓ Activity Logs: {ActivityLog.objects.count()}\n")

print("="*80)
print("GENERATION COMPLETE".center(80))
print("="*80 + "\n")

# Final counts
print("FINAL SUMMARY:")
print(f"   Properties: {Property.objects.count()}")
print(f"   Rooms: {Room.objects.count()}")
print(f"   Guests: {Guest.objects.count()}")
print(f"   Reservations: {Reservation.objects.count()}")
print(f"   Check-Ins: {CheckIn.objects.count()}")
print(f"   Check-Outs: {CheckOut.objects.count()}")
print(f"   Folios: {Folio.objects.count()}")
print(f"   Payments: {Payment.objects.count()}")
print(f"   Housekeeping Tasks: {HousekeepingTask.objects.count()}")
print(f"   Maintenance Requests: {MaintenanceRequest.objects.count()}")
print(f"   Rate Plans: {RatePlan.objects.count()}")
print(f"   Loyalty Programs: {LoyaltyProgram.objects.count()}")
print(f"   Channels: {Channel.objects.count()}")
print(f"   Daily Statistics: {DailyStatistics.objects.count()}")
print(f"   Notifications: {Notification.objects.count()}")

print("\n✅ Database populated with comprehensive test data!")
print("✅ Ready for end-to-end workflow testing\n")
