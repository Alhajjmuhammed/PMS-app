#!/usr/bin/env python
"""Create comprehensive test data for PMS system"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.properties.models import Property
from apps.rooms.models import RoomType, Room
from apps.guests.models import Guest
from apps.reservations.models import Reservation, ReservationRoom
from apps.housekeeping.models import HousekeepingTask
from apps.maintenance.models import MaintenanceRequest
from apps.billing.models import ChargeCode
from apps.pos.models import MenuCategory, MenuItem, Outlet
from apps.channels.models import PropertyChannel
from apps.rates.models import RatePlan, RoomRate
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

print("=" * 80)
print("🗄️  CREATING COMPREHENSIVE TEST DATA")
print("=" * 80)
print()

# 1. Create test users
print("👤 Creating test users...")
users_data = [
    {'email': 'admin@hotel.com', 'password': 'admin123', 'role': 'ADMIN', 'first_name': 'Admin', 'last_name': 'User'},
    {'email': 'manager@hotel.com', 'password': 'manager123', 'role': 'MANAGER', 'first_name': 'John', 'last_name': 'Manager'},
    {'email': 'frontdesk@hotel.com', 'password': 'front123', 'role': 'FRONT_DESK', 'first_name': 'Sarah', 'last_name': 'Smith'},
    {'email': 'housekeeper@hotel.com', 'password': 'house123', 'role': 'HOUSEKEEPING', 'first_name': 'Maria', 'last_name': 'Garcia'},
]

users = []
for user_info in users_data:
    user, created = User.objects.get_or_create(
        email=user_info['email'],
        defaults={
            'first_name': user_info['first_name'],
            'last_name': user_info['last_name'],
            'role': user_info['role'],
            'is_staff': True,
            'is_active': True,
        }
    )
    if created:
        user.set_password(user_info['password'])
        user.save()
        print(f"   ✅ Created {user.role}: {user.email}")
    else:
        print(f"   ℹ️  Exists: {user.email}")
    users.append(user)

admin_user = users[0]
print()

# 2. Create property
print("🏨 Creating property...")
property, created = Property.objects.get_or_create(
    code='HTL001',
    defaults={
        'name': 'Grand Plaza Hotel',
        'property_type': 'HOTEL',
        'address': '123 Main Street',
        'city': 'New York',
        'state': 'NY',
        'country': 'USA',
        'postal_code': '10001',
        'phone': '+1-555-0100',
        'email': 'info@grandplaza.com',
        'website': 'http://www.grandplaza.com',
        'total_rooms': 50,
        'is_active': True,
        'created_by': admin_user,
    }
)
print(f"   {'✅ Created' if created else 'ℹ️  Exists'}: {property.name}")
print()

# 3. Create room types
print("🛏️  Creating room types...")
room_types_data = [
    {'name': 'Standard Room', 'code': 'STD', 'base_price': '150.00', 'capacity': 2},
    {'name': 'Deluxe Room', 'code': 'DLX', 'base_price': '250.00', 'capacity': 2},
    {'name': 'Suite', 'code': 'STE', 'base_price': '450.00', 'capacity': 4},
]

room_types = []
for rt_data in room_types_data:
    rt, created = RoomType.objects.get_or_create(
        hotel=property,
        code=rt_data['code'],
        defaults={
            'name': rt_data['name'],
            'base_price': Decimal(rt_data['base_price']),
            'max_occupancy': rt_data['capacity'],
            'description': f'{rt_data["name"]} with modern amenities',
        }
    )
    room_types.append(rt)
    if created:
        print(f"   ✅ {rt.name} - ${rt.base_price}/night")
print()

# 4. Create rooms
print("🚪 Creating rooms...")
rooms = []
for room_num in range(101, 125):
    room_type = room_types[room_num % 3]
    room, created = Room.objects.get_or_create(
        hotel=property,
        number=str(room_num),
        defaults={
            'room_type': room_type,
            'floor_number': ((room_num - 100) // 10) or 1,
            'status': 'CLEAN' if room_num % 3 == 0 else 'VACANT',
            'is_active': True,
        }
    )
    rooms.append(room)
    if created:
        print(f"   ✅ Room {room.number} ({room_type.name})")
print(f"   Total: {len(rooms)} rooms")
print()

# 5. Create guests
print("👥 Creating guests...")
guests_data = [
    {'first_name': 'James', 'last_name': 'Wilson', 'email': 'james.wilson@email.com', 'phone': '+1-555-1001'},
    {'first_name': 'Emily', 'last_name': 'Brown', 'email': 'emily.brown@email.com', 'phone': '+1-555-1002'},
    {'first_name': 'Michael', 'last_name': 'Davis', 'email': 'michael.davis@email.com', 'phone': '+1-555-1003'},
    {'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah.johnson@email.com', 'phone': '+1-555-1004'},
    {'first_name': 'David', 'last_name': 'Martinez', 'email': 'david.martinez@email.com', 'phone': '+1-555-1005'},
]

guests = []
for guest_data in guests_data:
    guest, created = Guest.objects.get_or_create(
        email=guest_data['email'],
        defaults={
            'first_name': guest_data['first_name'],
            'last_name': guest_data['last_name'],
            'phone': guest_data['phone'],
            'nationality': 'USA',
            'guest_type': 'INDIVIDUAL',
            'created_by': admin_user,
        }
    )
    guests.append(guest)
    if created:
        print(f"   ✅ {guest.first_name} {guest.last_name}")
print()

# 6. Create rate plan
print("💰 Creating rate plans...")
rate_plan, created = RatePlan.objects.get_or_create(
    property=property,
    code='BAR',
    defaults={
        'name': 'Best Available Rate',
        'description': 'Standard rate plan',
        'rate_type': 'STANDARD',
        'is_active': True,
    }
)
if created:
    print(f"   ✅ {rate_plan.name}")
    for room_type in room_types:
        RoomRate.objects.get_or_create(
            rate_plan=rate_plan,
            room_type=room_type,
            defaults={
                'rate': room_type.base_price,
            }
        )
else:
    print(f"   ℹ️  Exists: {rate_plan.name}")
print()

# 7. Create reservations
print("📅 Creating reservations...")
today = timezone.now().date()
reservations_data = [
    {'guest': 0, 'checkin': today - timedelta(days=2), 'checkout': today + timedelta(days=2), 'status': 'CHECKED_IN', 'room': 0},
    {'guest': 1, 'checkin': today, 'checkout': today + timedelta(days=3), 'status': 'CONFIRMED', 'room': 1},
    {'guest': 2, 'checkin': today + timedelta(days=1), 'checkout': today + timedelta(days=5), 'status': 'CONFIRMED', 'room': 2},
    {'guest': 3, 'checkin': today - timedelta(days=5), 'checkout': today - timedelta(days=1), 'status': 'CHECKED_OUT', 'room': 3},
    {'guest': 4, 'checkin': today + timedelta(days=7), 'checkout': today + timedelta(days=10), 'status': 'CONFIRMED', 'room': 4},
]

for idx, res_data in enumerate(reservations_data, 1):
    guest = guests[res_data['guest']]
    room = rooms[res_data['room']]
    nights = (res_data['checkout'] - res_data['checkin']).days
    total = room.room_type.base_price * nights
    
    res, created = Reservation.objects.get_or_create(
        confirmation_number=f'RES{today.year}{idx:04d}',
        defaults={
            'property': property,
            'guest': guest,
            'checkin_date': res_data['checkin'],
            'checkout_date': res_data['checkout'],
            'adults': 2,
            'children': 0,
            'status': res_data['status'],
            'total_amount': total,
            'created_by': admin_user,
        }
    )
    
    if created:
        ReservationRoom.objects.create(
            reservation=res,
            room=room,
            room_type=room.room_type,
            rate_plan=rate_plan,
            rate=room.room_type.base_price,
            checkin_date=res_data['checkin'],
            checkout_date=res_data['checkout'],
        )
        print(f"   ✅ {res.confirmation_number} - {guest.full_name} (Room {room.number}) - {res.status}")
print()

# 8. Create charge codes
print("💵 Creating charge codes...")
charge_codes_data = [
    {'code': 'ROOM', 'name': 'Room Charge', 'category': 'ACCOMMODATION'},
    {'code': 'FB', 'name': 'Food & Beverage', 'category': 'FOOD_BEVERAGE'},
    {'code': 'LAUNDRY', 'name': 'Laundry Service', 'category': 'SERVICE'},
]

for cc_data in charge_codes_data:
    cc, created = ChargeCode.objects.get_or_create(
        property=property,
        code=cc_data['code'],
        defaults={
            'name': cc_data['name'],
            'category': cc_data['category'],
            'price': Decimal('0.00'),
            'is_active': True,
        }
    )
    if created:
        print(f"   ✅ {cc.name}")
print()

# 9. Create housekeeping tasks
print("🧹 Creating housekeeping tasks...")
for idx, room in enumerate(rooms[:8]):
    task, created = HousekeepingTask.objects.get_or_create(
        property=property,
        room=room,
        date=today,
        defaults={
            'task_type': 'CLEANING',
            'priority': 'MEDIUM' if idx % 2 == 0 else 'HIGH',
            'status': 'PENDING' if idx < 4 else 'IN_PROGRESS',
            'assigned_to': users[3] if idx < 4 else None,
            'created_by': admin_user,
        }
    )
    if created:
        print(f"   ✅ Clean Room {room.number} - {task.status}")
print()

# 10. Create maintenance requests
print("🔧 Creating maintenance requests...")
maintenance_data = [
    {'room': 0, 'issue': 'AC not cooling properly', 'priority': 'HIGH', 'status': 'PENDING'},
    {'room': 5, 'issue': 'Leaky faucet in bathroom', 'priority': 'MEDIUM', 'status': 'IN_PROGRESS'},
    {'room': 10, 'issue': 'Light bulb replacement', 'priority': 'LOW', 'status': 'COMPLETED'},
]

for maint_data in maintenance_data:
    room = rooms[maint_data['room']]
    maint, created = MaintenanceRequest.objects.get_or_create(
        property=property,
        room=room,
        description=maint_data['issue'],
        defaults={
            'request_type': 'REPAIR',
            'priority': maint_data['priority'],
            'status': maint_data['status'],
            'reported_by': admin_user,
        }
    )
    if created:
        print(f"   ✅ Room {room.number} - {maint_data['issue']}")
print()

# 11. Create POS data
print("🍽️  Creating POS data...")
outlet, created = Outlet.objects.get_or_create(
    property=property,
    name='Main Restaurant',
    defaults={'code': 'REST01', 'is_active': True}
)

categories_data = [
    {'name': 'Beverages', 'code': 'BEV'},
    {'name': 'Main Course', 'code': 'MAIN'},
    {'name': 'Desserts', 'code': 'DES'},
]

for cat_data in categories_data:
    cat, created = MenuCategory.objects.get_or_create(
        property=property,
        code=cat_data['code'],
        defaults={'name': cat_data['name'], 'is_active': True}
    )
    if created:
        print(f"   ✅ Category: {cat.name}")

items_data = [
    {'category': 'BEV', 'name': 'Coffee', 'price': '5.00'},
    {'category': 'MAIN', 'name': 'Grilled Chicken', 'price': '25.00'},
    {'category': 'DES', 'name': 'Chocolate Cake', 'price': '8.00'},
]

for item_data in items_data:
    category = MenuCategory.objects.get(property=property, code=item_data['category'])
    item, created = MenuItem.objects.get_or_create(
        property=property,
        name=item_data['name'],
        defaults={
            'category': category,
            'price': Decimal(item_data['price']),
            'is_available': True,
        }
    )
    if created:
        print(f"   ✅ {item.name} - ${item.price}")
print()

# 12. Create channel
print("🌐 Creating channel connection...")
channel, created = PropertyChannel.objects.get_or_create(
    property=property,
    channel='BOOKING_COM',
    defaults={'is_active': True, 'hotel_id': 'HTL001'}
)
if created:
    print(f"   ✅ Booking.com channel")
print()

print("=" * 80)
print("✅ TEST DATA CREATION COMPLETE")
print("=" * 80)
print()
print("📊 Summary:")
print(f"   • Users: {User.objects.count()}")
print(f"   • Properties: 1 (Grand Plaza Hotel)")
print(f"   • Room Types: {RoomType.objects.filter(hotel=property).count()}")
print(f"   • Rooms: {Room.objects.filter(hotel=property).count()}")
print(f"   • Guests: {Guest.objects.count()}")
print(f"   • Reservations: {Reservation.objects.filter(property=property).count()}")
print(f"   • Housekeeping Tasks: {HousekeepingTask.objects.filter(property=property).count()}")
print(f"   • Maintenance Requests: {MaintenanceRequest.objects.filter(property=property).count()}")
print(f"   • Menu Items: {MenuItem.objects.filter(property=property).count()}")
print()
print("🔐 Test Credentials:")
print("   Admin:       admin@hotel.com / admin123")
print("   Manager:     manager@hotel.com / manager123")
print("   Front Desk:  frontdesk@hotel.com / front123")
print("   Housekeeper: housekeeper@hotel.com / house123")
print()
print("🚀 Next Steps:")
print("   1. Start backend:  cd backend && source venv/bin/activate && python manage.py runserver")
print("   2. Start web:      cd web && npm run dev")
print("   3. Start mobile:   cd mobile && npm start")
print()
