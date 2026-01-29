"""
Script to create test users for all roles in the system.
Run with: python manage.py shell < create_test_users.py
"""

from django.contrib.auth import get_user_model
from apps.properties.models import Property

User = get_user_model()

# Get or create test property
property_obj, created = Property.objects.get_or_create(
    name="Test Hotel",
    defaults={
        'address': '123 Test Street',
        'phone': '555-0000',
        'email': 'hotel@test.com'
    }
)

print(f"Using property: {property_obj.name} (ID: {property_obj.id})")

# Define test users
test_users = [
    {
        'email': 'admin@test.com',
        'password': 'admin123',
        'role': 'ADMIN',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_superuser': True,
        'is_staff': True
    },
    {
        'email': 'manager@test.com',
        'password': 'manager123',
        'role': 'MANAGER',
        'first_name': 'Manager',
        'last_name': 'User'
    },
    {
        'email': 'frontdesk@test.com',
        'password': 'frontdesk123',
        'role': 'FRONT_DESK',
        'first_name': 'Front',
        'last_name': 'Desk'
    },
    {
        'email': 'housekeeping@test.com',
        'password': 'housekeeping123',
        'role': 'HOUSEKEEPING',
        'first_name': 'House',
        'last_name': 'Keeper'
    },
    {
        'email': 'maintenance@test.com',
        'password': 'maintenance123',
        'role': 'MAINTENANCE',
        'first_name': 'Maintenance',
        'last_name': 'Staff'
    },
    {
        'email': 'accountant@test.com',
        'password': 'accountant123',
        'role': 'ACCOUNTANT',
        'first_name': 'Account',
        'last_name': 'Ant'
    },
    {
        'email': 'pos@test.com',
        'password': 'pos123',
        'role': 'POS_STAFF',
        'first_name': 'POS',
        'last_name': 'Staff'
    },
    {
        'email': 'guest@test.com',
        'password': 'guest123',
        'role': 'GUEST',
        'first_name': 'Test',
        'last_name': 'Guest'
    }
]

print("\n" + "="*60)
print("Creating Test Users")
print("="*60 + "\n")

for user_data in test_users:
    email = user_data.pop('email')
    password = user_data.pop('password')
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        print(f"⚠️  User {email} already exists - skipping")
        continue
    
    # Create user
    is_superuser = user_data.pop('is_superuser', False)
    is_staff = user_data.pop('is_staff', False)
    
    if is_superuser:
        user = User.objects.create_superuser(
            email=email,
            password=password,
            assigned_property=property_obj,
            **user_data
        )
    else:
        user = User.objects.create_user(
            email=email,
            password=password,
            assigned_property=property_obj,
            is_staff=is_staff,
            **user_data
        )
    
    print(f"✅ Created {user.role}: {user.email} (password: {password})")

print("\n" + "="*60)
print("Test Users Summary")
print("="*60)
print(f"\n{'Role':<15} {'Email':<25} {'Password':<15}")
print("-"*60)

for user_data in test_users:
    print(f"{user_data['role']:<15} {user_data['email']:<25} {user_data.get('password', 'N/A'):<15}")

print("\n" + "="*60)
print("✅ All test users created successfully!")
print("="*60)
