# 🔐 Roles and Permissions - Hotel PMS System

## 📋 System Roles

The system has **8 distinct roles** defined:

| Role | Code | Primary Responsibility |
|------|------|------------------------|
| 1. Administrator | `ADMIN` | Full system control, manages all properties |
| 2. Manager | `MANAGER` | Property-level management |
| 3. Front Desk | `FRONT_DESK` | Guest check-in/out, reservations |
| 4. Housekeeping | `HOUSEKEEPING` | Room cleaning, maintenance scheduling |
| 5. Maintenance | `MAINTENANCE` | Property repairs, maintenance requests |
| 6. Accountant | `ACCOUNTANT` | Financial operations, billing, reports |
| 7. POS Staff | `POS_STAFF` | Restaurant/bar operations, sales |
| 8. Guest | `GUEST` | Limited access (typically for guest portal) |

---

## 🔑 Role-Based Access Control

### 1. 👑 ADMINISTRATOR / SUPERUSER
**Access Level**: SYSTEM-WIDE (All Properties)

**Permissions**:
- ✅ **Full Access** to all modules across all properties
- ✅ View and manage ALL properties
- ✅ Create, edit, delete users
- ✅ Assign staff to properties
- ✅ View all financial reports
- ✅ System configuration
- ✅ Access Django admin panel

**Can Access**:
- All dashboard views
- All properties
- All reservations (any hotel)
- All rooms (any hotel)
- All guests
- All staff management
- All billing and financial data
- All reports and analytics
- System settings

**Current Users**:
- admin@test.com (Superuser)
- admin@hotel.com (Superuser)

---

### 2. 🏨 MANAGER
**Access Level**: PROPERTY-SPECIFIC (Only Assigned Property)

**Permissions**:
- ✅ View and manage their assigned property
- ✅ Create/edit reservations for their property
- ✅ Manage rooms in their property
- ✅ View guests for their property
- ✅ Manage staff assignments within their property
- ✅ View property-specific reports
- ✅ POS operations for their property
- ✅ Housekeeping & maintenance for their property
- ❌ CANNOT see other properties
- ❌ CANNOT create new properties
- ❌ CANNOT manage system-wide settings

**Can Access**:
- Dashboard (property-specific data)
- Reservations (their property only)
- Rooms (their property only)
- Guests (their property only)
- Front Desk operations
- Housekeeping tasks
- Maintenance requests
- POS/Billing (their property)
- Reports (their property only)

**Current Users**:
- manager.downtown@hotel.com → Grand Hotel Downtown
- manager.beach@resort.com → Beach Resort Paradise
- manager.test@hotel.com → Test Property

---

### 3. 🎫 FRONT DESK
**Access Level**: PROPERTY-SPECIFIC (If assigned) or ALL (If not assigned)

**Permissions**:
- ✅ Check-in / Check-out guests
- ✅ Create and manage reservations
- ✅ Guest management (add, edit, search)
- ✅ View room availability
- ✅ Process payments
- ✅ View daily reports
- ✅ Handle guest requests
- ⚠️ Limited financial access (no full reports)
- ❌ Cannot manage users
- ❌ Cannot edit property settings

**Can Access**:
- Dashboard
- Reservations (create, view, edit)
- Front Desk operations
- Guest management
- Room availability
- Basic billing
- Check-in/out operations
- Daily reports

**Current Users**:
- frontdesk@hotel.com (Not assigned - sees all)
- admin@test.com (Also has this role)

---

### 4. 🧹 HOUSEKEEPING
**Access Level**: PROPERTY-SPECIFIC (If assigned) or ALL (If not assigned)

**Permissions**:
- ✅ View assigned cleaning tasks
- ✅ Update room status (clean, dirty, inspected)
- ✅ Create maintenance requests
- ✅ View room assignments
- ✅ Track cleaning progress
- ❌ Cannot access reservations
- ❌ Cannot access billing
- ❌ Cannot view financial reports

**Can Access**:
- Housekeeping dashboard
- Task list (assigned rooms)
- Room status updates
- Maintenance request creation
- Housekeeping reports

**Current Users**:
- housekeeper@hotel.com (Not assigned - sees all)

---

### 5. 🔧 MAINTENANCE
**Access Level**: PROPERTY-SPECIFIC (If assigned) or ALL (If not assigned)

**Permissions**:
- ✅ View maintenance requests
- ✅ Update request status (pending, in progress, completed)
- ✅ Create new maintenance tickets
- ✅ Assign maintenance to rooms
- ✅ Track repair history
- ❌ Cannot access guest data
- ❌ Cannot access reservations
- ❌ Cannot access financial data

**Can Access**:
- Maintenance dashboard
- Request list
- Work order management
- Equipment tracking
- Maintenance reports

**Current Users**:
- maintenance@hotel.com (Not assigned - sees all)

---

### 6. 💰 ACCOUNTANT
**Access Level**: PROPERTY-SPECIFIC (If assigned) or ALL (If not assigned)

**Permissions**:
- ✅ View all financial reports
- ✅ Process invoices
- ✅ Manage billing
- ✅ Revenue reports
- ✅ Tax calculations
- ✅ Payment processing
- ⚠️ Limited reservation editing (read-only)
- ❌ Cannot manage users
- ❌ Cannot edit properties

**Can Access**:
- Financial dashboard
- Billing module
- Revenue reports
- Payment history
- Invoices
- Tax reports
- Profit/loss statements

**Current Users**:
- None yet (can be created)

---

### 7. 🍽️ POS STAFF
**Access Level**: PROPERTY-SPECIFIC (If assigned) or ALL (If not assigned)

**Permissions**:
- ✅ Process POS sales (restaurant, bar, room service)
- ✅ Manage menu items
- ✅ Create orders
- ✅ Process payments
- ✅ View sales reports
- ❌ Cannot access reservations
- ❌ Cannot view all financial data
- ❌ Cannot manage users

**Can Access**:
- POS dashboard
- Menu management
- Order creation
- Payment processing
- Daily sales reports
- Inventory (limited)

**Current Users**:
- None yet (can be created)

---

### 8. 👤 GUEST
**Access Level**: RESTRICTED (Own data only)

**Permissions**:
- ✅ View own reservations
- ✅ Update own profile
- ✅ View invoices
- ✅ Make service requests
- ❌ Cannot see other guests
- ❌ Cannot access staff modules
- ❌ Cannot view property data

**Can Access**:
- Guest portal (if implemented)
- Personal reservation details
- Personal billing
- Service requests

**Current Users**:
- None (guests would be created via registration)

---

## 🔒 Permission Implementation

### Current System Security:
- **Authentication**: All API endpoints require `IsAuthenticated` permission
- **Property Filtering**: Automatically filters data based on `assigned_property`
- **Token-based Auth**: Uses DRF Token Authentication
- **Role-based Access**: Role is stored in User model but not strictly enforced yet

### How Property Filtering Works:
```python
def get_queryset(self):
    queryset = Model.objects.all()
    
    # If user has assigned_property, filter to that property only
    if self.request.user.assigned_property:
        queryset = queryset.filter(property=self.request.user.assigned_property)
    
    # Superusers see everything (no filter)
    return queryset
```

---

## 📊 Permission Matrix

| Module | Admin | Manager | Front Desk | Housekeeping | Maintenance | Accountant | POS Staff | Guest |
|--------|-------|---------|------------|--------------|-------------|------------|-----------|-------|
| **Dashboard** | ✅ All | ✅ Property | ✅ Property | ✅ Limited | ✅ Limited | ✅ Financial | ✅ POS | ❌ |
| **Properties** | ✅ All | ✅ View Own | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Reservations** | ✅ | ✅ | ✅ | ❌ | ❌ | 👁️ View | ❌ | 👁️ Own |
| **Guests** | ✅ | ✅ | ✅ | ❌ | ❌ | 👁️ View | ❌ | 👁️ Own |
| **Rooms** | ✅ | ✅ | ✅ View | ✅ Status | ✅ View | 👁️ View | ❌ | ❌ |
| **Front Desk** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Housekeeping** | ✅ | ✅ | 👁️ View | ✅ | ✅ Report | ❌ | ❌ | ❌ |
| **Maintenance** | ✅ | ✅ | ✅ Create | 👁️ View | ✅ | ❌ | ❌ | ✅ Request |
| **Billing** | ✅ | ✅ | ✅ Limited | ❌ | ❌ | ✅ | ✅ POS | 👁️ Own |
| **POS** | ✅ | ✅ | ✅ View | ❌ | ❌ | 👁️ Reports | ✅ | ❌ |
| **Reports** | ✅ All | ✅ Property | ✅ Daily | ✅ Tasks | ✅ Work | ✅ Financial | ✅ Sales | ❌ |
| **Users** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Settings** | ✅ | ⚠️ Limited | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Legend**:
- ✅ = Full Access
- 👁️ = View Only
- ⚠️ = Limited Access
- ❌ = No Access

---

## 🎯 How to Assign Roles

### Via Django Admin:
1. Go to http://localhost:8000/admin/
2. Login as superuser
3. Navigate to Users
4. Edit user
5. Set Role and assigned_property

### Via Django Shell:
```python
from apps.accounts.models import User
from apps.properties.models import Property

# Get property
property = Property.objects.get(name='Grand Hotel Downtown')

# Create user with specific role
user = User.objects.create_user(
    email='staff@hotel.com',
    password='test123',
    first_name='John',
    last_name='Doe',
    role='FRONT_DESK',  # or MANAGER, HOUSEKEEPING, etc.
    assigned_property=property  # Assign to specific property
)
```

---

## 🔐 Security Best Practices

1. **Superusers**: Only create for system administrators
2. **Property Assignment**: Always assign staff to specific properties
3. **Role Selection**: Choose the minimum necessary role
4. **Password Policy**: Enforce strong passwords in production
5. **Token Expiry**: Consider implementing token expiration
6. **Audit Logging**: Track user actions (future enhancement)
7. **Two-Factor Auth**: Consider for sensitive roles (future enhancement)

---

**Last Updated**: January 22, 2026  
**System Version**: 1.0  
**Total Roles**: 8  
**Total Users**: 9 (6 staff + 3 managers)
