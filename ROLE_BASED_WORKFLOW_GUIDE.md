# 🎭 Complete Role-Based Workflow Guide

## 📋 Table of Contents
1. [System Roles Overview](#system-roles-overview)
2. [Role Hierarchy](#role-hierarchy)
3. [Detailed Role Workflows](#detailed-role-workflows)
4. [Common Workflows](#common-workflows)
5. [Permission Matrix](#permission-matrix)
6. [Multi-Property Setup](#multi-property-setup)

---

## 🎯 System Roles Overview

The PMS system has **8 distinct roles** with specific permissions:

| Role | Code | Purpose | Platform Access |
|------|------|---------|-----------------|
| **Superuser** | - | System owner, full control | Web only |
| **Administrator** | `ADMIN` | Property admin, manages everything | Web + Mobile |
| **Manager** | `MANAGER` | Operations manager, reports, oversight | Web + Mobile |
| **Front Desk** | `FRONT_DESK` | Check-in/out, reservations, guests | Web + Mobile |
| **Housekeeping** | `HOUSEKEEPING` | Room cleaning, status updates | Mobile primarily |
| **Maintenance** | `MAINTENANCE` | Repairs, work orders | Mobile primarily |
| **Accountant** | `ACCOUNTANT` | Billing, invoices, financial reports | Web only |
| **POS Staff** | `POS_STAFF` | Restaurant/bar operations | Web + Mobile |
| **Guest** | `GUEST` | View own bookings, bills | Web + Mobile |

---

## 📊 Role Hierarchy

```
┌─────────────────────────────────────────┐
│           SUPERUSER (Owner)             │
│  ✓ Multi-property management            │
│  ✓ Create/delete properties             │
│  ✓ Manage all users                     │
│  ✓ System configuration                 │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
┌───────▼───────┐  ┌──▼────────────┐
│  ADMIN        │  │  MANAGER      │
│  Full Access  │  │  Most Access  │
└───────┬───────┘  └──┬────────────┘
        │             │
        └──────┬──────┘
               │
    ┌──────────┼──────────┬──────────┬──────────┐
    │          │          │          │          │
┌───▼────┐ ┌──▼──────┐ ┌─▼──────┐ ┌─▼──────┐ ┌─▼──────┐
│ FRONT  │ │ HOUSE   │ │ MAINT  │ │ ACCT   │ │ POS    │
│ DESK   │ │ KEEPING │ │ ENANCE │ │ OUNTANT│ │ STAFF  │
└────────┘ └─────────┘ └────────┘ └────────┘ └────────┘
```

---

## 👥 Detailed Role Workflows

### 1️⃣ **SUPERUSER** (System Owner)

**Who**: Business owner, IT administrator  
**Access Level**: COMPLETE SYSTEM ACCESS  
**Login**: Web only

#### Daily Tasks:
1. **Multi-Property Management**
   ```
   Login → Properties → View all properties
   → Add new property
   → Configure property settings
   → Assign managers to properties
   ```

2. **User Management**
   ```
   Users → Create staff accounts
   → Assign roles (Admin, Manager, Front Desk, etc.)
   → Assign users to properties
   → Deactivate/delete users
   ```

3. **System Configuration**
   ```
   Settings → Configure channels (Booking.com, Expedia)
   → Setup payment gateways
   → Configure email/SMS notifications
   → System-wide settings
   ```

#### Can Access:
- ✅ All properties
- ✅ All modules
- ✅ All data across properties
- ✅ User management
- ✅ Property creation/deletion
- ✅ System configuration

---

### 2️⃣ **ADMINISTRATOR** (Property Admin)

**Who**: General Manager, Property Owner  
**Access Level**: FULL ACCESS to assigned property  
**Login**: Web + Mobile

#### Daily Workflow:
**Morning (9:00 AM)**
```
1. Login → Dashboard
2. Check occupancy status (50 rooms, 45 occupied)
3. Review overnight activity
4. Check pending check-ins (10 arrivals today)
5. Review housekeeping status
```

**Key Responsibilities:**

1. **Staff Management**
   ```
   Users → View staff
   → Edit staff profiles
   → Assign shifts/departments
   → View staff activity logs
   ```

2. **Property Operations**
   ```
   Dashboard → View all metrics
   Rooms → Manage room inventory
   Rates → Update pricing
   Reports → Access all reports
   ```

3. **Financial Overview**
   ```
   Billing → View all folios
   Reports → Revenue reports
   → Occupancy reports
   → Night audit review
   ```

4. **Reservation Management**
   ```
   Reservations → View all bookings
   → Create group reservations
   → Modify/cancel bookings
   → Handle complaints
   ```

#### Can Access:
- ✅ All modules in assigned property
- ✅ Staff management (can't create/delete users)
- ✅ Financial reports
- ✅ Night audit execution
- ✅ Channel manager configuration
- ❌ Can't create new properties
- ❌ Can't delete users

---

### 3️⃣ **MANAGER** (Operations Manager)

**Who**: Shift Manager, Operations Manager  
**Access Level**: HIGH ACCESS (read/execute operations)  
**Login**: Web + Mobile

#### Daily Workflow:

**Morning Shift (7:00 AM - 3:00 PM)**
```
1. Login → Dashboard
2. Review night audit report
3. Check today's arrivals (10 guests)
4. Check today's departures (8 guests)
5. Assign housekeeping tasks
6. Review maintenance requests (3 pending)
7. Monitor front desk operations
```

**Key Tasks:**

1. **Operations Monitoring**
   ```
   Dashboard → Real-time occupancy
   → Staff on duty
   → Tasks pending
   → Revenue today
   ```

2. **Guest Relations**
   ```
   Guests → View all guests
   → Handle VIP requests
   → Resolve complaints
   Reservations → Approve modifications
   ```

3. **Task Coordination**
   ```
   Housekeeping → Assign rooms to staff
   → Monitor cleaning progress
   Maintenance → Review requests
   → Prioritize urgent issues
   ```

4. **Reports Review**
   ```
   Reports → Daily reports
   → Occupancy forecast
   → Revenue analysis
   → Staff performance
   ```

#### Can Access:
- ✅ All operational modules
- ✅ View financial reports
- ✅ Manage reservations
- ✅ Assign tasks
- ✅ Run reports
- ⚠️ Limited billing access (view only)
- ❌ Can't modify rates
- ❌ Can't manage staff accounts

---

### 4️⃣ **FRONT DESK** (Receptionist)

**Who**: Receptionist, Front Desk Agent  
**Access Level**: GUEST-FACING OPERATIONS  
**Login**: Web + Mobile

#### Daily Workflow:

**Check-In Process (2:00 PM)**
```
1. Mobile App → Reservations → Arrivals Today
2. Guest arrives: "John Smith"
3. Tap on reservation → Verify details
4. Check ID → Upload document
5. Assign room: Room 205
6. Generate key card
7. Tap "Check In" → Guest checked in
8. Print welcome letter
```

**Check-Out Process (11:00 AM)**
```
1. Mobile/Web → Reservations → In-House
2. Guest: "Room 205 checking out"
3. Open folio → Review charges
   - Room: $150 x 2 nights = $300
   - Restaurant: $45
   - Minibar: $15
   - Tax: $36
   Total: $396
4. Process payment (Card/Cash/Invoice)
5. Tap "Check Out"
6. Print receipt
7. Request housekeeping (Room 205 dirty)
```

**Creating New Reservation**
```
1. Reservations → New Reservation
2. Search guest or create new
3. Fill details:
   - Check-in: Feb 25, 2026
   - Check-out: Feb 27, 2026
   - Room type: Deluxe King
   - Guests: 2 adults
   - Rate: $150/night
4. Add special requests: "Late check-out"
5. Payment method: Credit Card
6. Create → Confirmation email sent
```

**Walk-In Guest**
```
1. Front Desk → Walk-In
2. Check availability (Today)
3. Show available rooms
4. Create guest profile
5. Assign room
6. Process payment/deposit
7. Immediate check-in
```

#### Can Access:
- ✅ Reservations (create, modify, cancel)
- ✅ Guest management (full access)
- ✅ Check-in/Check-out
- ✅ View folios/bills
- ✅ Request housekeeping
- ✅ Create maintenance requests
- ⚠️ Limited billing (view only, can process checkout)
- ❌ Can't modify rates
- ❌ Can't access financial reports
- ❌ Can't manage staff

---

### 5️⃣ **HOUSEKEEPING** (Room Attendant)

**Who**: Housekeeper, Room Attendant, Housekeeping Supervisor  
**Access Level**: ROOM STATUS & CLEANING TASKS  
**Login**: Mobile App only

#### Daily Workflow:

**Morning (8:00 AM)**
```
1. Mobile App Login
2. Dashboard shows: "15 rooms assigned to you"
3. Tasks view:
   ✓ Priority: 3 checkouts (clean by 2 PM)
   ✓ Stay-overs: 10 rooms
   ✓ Vacant dirty: 2 rooms
```

**Cleaning a Room (Room 305)**
```
1. Tasks → Tap "Room 305 - Checkout"
2. Status: "Dirty" → Tap "Start Cleaning"
3. Timer starts (tracks cleaning time)
4. Clean room (linens, bathroom, vacuum, etc.)
5. Issues found?
   → Yes: Report maintenance (broken lamp)
   → No: Continue
6. Tap "Mark as Clean"
7. Photos: Take 2-3 photos of cleaned room
8. Status changes: Dirty → Clean
9. Front desk notified → Room available
```

**Handling Special Requests**
```
Tasks → Special Requests
→ "Room 401: Extra towels"
→ "Room 215: Hypoallergenic pillows"
→ Complete each request
→ Mark as done
```

**Daily Progress Tracking**
```
Dashboard shows:
✅ Completed: 12 rooms
🔄 In Progress: 1 room (Room 308)
⏳ Pending: 2 rooms
⏱️ Average time: 28 minutes/room
```

**End of Shift (3:00 PM)**
```
1. Review completed tasks: 15/15 rooms ✓
2. Report any maintenance issues found
3. Inventory check:
   - Towels used: 30
   - Toiletries used: 45 items
4. Clock out
```

#### Can Access:
- ✅ Assigned cleaning tasks
- ✅ Room status updates (Dirty → Clean)
- ✅ Maintenance requests (create only)
- ✅ Lost & found reporting
- ✅ Inventory tracking
- ❌ Can't view guest information
- ❌ Can't access reservations
- ❌ Can't see billing

---

### 6️⃣ **MAINTENANCE** (Maintenance Staff)

**Who**: Technician, Electrician, Plumber  
**Access Level**: MAINTENANCE WORK ORDERS  
**Login**: Mobile App only

#### Daily Workflow:

**Morning (7:00 AM)**
```
1. Mobile App Login
2. Dashboard: "8 open requests"
   🔴 Urgent: 2 (AC not working, Water leak)
   🟡 High: 3
   🟢 Normal: 3
```

**Handling Urgent Request**
```
1. Requests → Urgent → "Room 405: AC not working"
2. Details:
   - Reported by: Front Desk (Guest complaint)
   - Time: 11:30 PM (last night)
   - Priority: URGENT
   - Room status: Occupied
3. Tap "Start Work"
4. Go to Room 405
5. Diagnose issue: Thermostat broken
6. Repair/Replace thermostat
7. Test AC: Working ✓
8. Add notes: "Replaced thermostat, tested OK"
9. Parts used:
   - Thermostat: 1 unit ($85)
   - Labor: 1.5 hours
10. Upload photo of working AC
11. Tap "Complete" → Status: Closed
12. Guest notified: "AC repaired"
```

**Preventive Maintenance**
```
Schedule → This Week
→ "Pool pump inspection"
→ "Fire extinguisher check"
→ "HVAC filter replacement"
Complete each task with checklist
```

**Creating Maintenance Request**
```
While cleaning pool area:
1. Notice broken pool light
2. Requests → Create New
3. Details:
   - Location: Pool Area
   - Issue: Underwater light not working
   - Priority: Normal
   - Photos: Upload 2 photos
4. Submit
5. Supervisor gets notification
```

#### Can Access:
- ✅ Maintenance requests
- ✅ Work order management
- ✅ Asset/equipment list
- ✅ Inventory (parts/supplies)
- ✅ Schedule preventive maintenance
- ❌ Can't view guest info
- ❌ Can't access reservations
- ❌ Can't see financial data

---

### 7️⃣ **ACCOUNTANT** (Accountant/Bookkeeper)

**Who**: Accountant, Financial Controller  
**Access Level**: FINANCIAL DATA & REPORTS  
**Login**: Web only

#### Daily Workflow:

**Morning (9:00 AM)**
```
1. Login → Dashboard
2. Review yesterday's revenue: $12,450
3. Check night audit report
4. Review pending invoices: 5
5. Check payment status
```

**Monthly Closing Tasks:**

1. **Review Revenue**
   ```
   Reports → Revenue Report
   → Select: February 2026
   → Total Revenue: $385,000
   → Breakdown:
     - Room Revenue: $280,000 (73%)
     - F&B Revenue: $65,000 (17%)
     - Other: $40,000 (10%)
   ```

2. **Reconcile Payments**
   ```
   Billing → Folios → Filter: Closed
   → Total collected: $385,000
   → Payment methods:
     - Credit Card: $290,000
     - Cash: $45,000
     - Invoice: $50,000
   → Bank reconciliation
   ```

3. **Generate Invoices**
   ```
   Billing → Invoices → Create
   → Corporate client: "ABC Corp"
   → Group booking charges
   → Add tax, discounts
   → Generate PDF
   → Email to: accounts@abccorp.com
   ```

4. **Financial Reports**
   ```
   Reports → Financial
   → Profit & Loss Statement
   → Balance Sheet
   → Tax reports
   → Export to Excel/PDF
   ```

5. **Night Audit Review**
   ```
   Reports → Night Audit History
   → Review each day's closing
   → Check discrepancies
   → Verify all charges posted
   ```

#### Can Access:
- ✅ All financial reports
- ✅ Billing & invoices (full access)
- ✅ Payment processing
- ✅ Night audit reports
- ✅ Revenue management
- ⚠️ View-only for reservations
- ❌ Can't modify room rates
- ❌ Can't manage staff
- ❌ Can't check-in guests

---

### 8️⃣ **POS STAFF** (Restaurant/Bar Staff)

**Who**: Waiter, Bartender, Restaurant Cashier  
**Access Level**: RESTAURANT/BAR OPERATIONS  
**Login**: Web + Mobile

#### Daily Workflow:

**Taking an Order (Restaurant)**
```
1. Mobile App → POS → Tables
2. Guest arrives → Assign to Table 7
3. Take order:
   → Menu → Breakfast → Continental
   → Coffee x2
   → Orange Juice x1
   → Total: $45
4. Options:
   a) Room Charge: Enter room 305
      → Posts to guest folio
   b) Cash/Card: Process payment
5. Send to kitchen → Order printed
6. Kitchen prepares → Mark "Ready"
7. Serve guest
8. Close bill
```

**Bar Service**
```
1. POS → Bar → New Order
2. Take order:
   → 2x Beer ($8 each)
   → 1x Cocktail ($15)
   → Total: $31
3. Guest: "Charge to Room 412"
4. Verify room 412 occupied ✓
5. Post charge → Guest signs bill
6. Prepare drinks
```

**End of Shift Closing**
```
1. POS → Reports → Today's Sales
2. Cash register:
   - Starting: $200
   - Cash sales: $350
   - Expected: $550
   - Actual: $550 ✓
3. Credit card reconciliation
4. Transfer room charges: 15 bills → $675
5. Print shift report
6. Submit to manager
```

#### Can Access:
- ✅ POS system (full access)
- ✅ Menu management
- ✅ Order processing
- ✅ Room charge posting
- ✅ Shift reports
- ⚠️ Limited guest info (room verification only)
- ❌ Can't access reservations
- ❌ Can't view financial reports
- ❌ Can't manage staff

---

### 9️⃣ **GUEST** (Hotel Guest)

**Who**: Current or past hotel guests  
**Access Level**: OWN DATA ONLY  
**Login**: Web + Mobile

#### Guest Portal Features:

**Booking a Room (Mobile App)**
```
1. Download app → Register
2. Search:
   - Destination: Beach Resort
   - Check-in: March 1
   - Check-out: March 5
   - Guests: 2
3. View available rooms:
   → Standard: $100/night
   → Deluxe: $150/night
   → Suite: $250/night
4. Select Deluxe → Book Now
5. Enter payment details
6. Confirmation received
```

**During Stay**
```
1. Mobile App → My Reservations
2. Current stay: Room 305
3. Features:
   → Digital key (if supported)
   → Request services:
     - Housekeeping
     - Room service
     - Wake-up call
   → View charges
   → Extend stay
   → Early checkout
```

**Viewing Bills**
```
My Account → Bills
→ Current stay charges:
  - Room (4 nights): $600
  - Restaurant: $145
  - Spa: $80
  - Total: $825
```

**Past Reservations**
```
My Reservations → History
→ Feb 2025: Beach Resort (5 nights)
→ Jan 2026: City Hotel (2 nights)
→ Download invoices
→ Leave reviews
```

#### Can Access:
- ✅ Own reservations only
- ✅ Own bills/folios
- ✅ Request services
- ✅ View property information
- ✅ Make new bookings
- ❌ Can't see other guests
- ❌ Can't see property operations
- ❌ Can't access reports

---

## 🔄 Common Workflows

### Workflow 1: Complete Reservation Cycle

```
┌──────────────────────────────────────────────────────────┐
│ 1. BOOKING (Guest Portal or Front Desk)                 │
│    - Guest searches availability                         │
│    - Selects room type                                   │
│    - Books online or calls front desk                    │
│    - Confirmation email sent                             │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ 2. PRE-ARRIVAL (Front Desk / Manager)                   │
│    - Review arrivals for tomorrow                        │
│    - Prepare room assignments                            │
│    - Note special requests (early check-in, etc.)        │
│    - Update housekeeping schedule                        │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ 3. CHECK-IN (Front Desk - 2:00 PM)                      │
│    - Guest arrives at reception                          │
│    - Verify reservation & ID                             │
│    - Collect payment/deposit                             │
│    - Assign room key                                     │
│    - Status: Reserved → Checked In                       │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ 4. DURING STAY (Multiple Roles)                         │
│    - Housekeeping: Daily room cleaning                   │
│    - Front Desk: Handle requests                         │
│    - POS Staff: Process restaurant charges               │
│    - Maintenance: Fix any issues                         │
│    - All charges posted to folio                         │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ 5. CHECK-OUT (Front Desk - 11:00 AM)                    │
│    - Guest requests checkout                             │
│    - Review folio with guest                             │
│    - Process payment                                     │
│    - Generate invoice                                    │
│    - Status: Checked In → Checked Out                    │
│    - Room status: Clean → Dirty                          │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ 6. POST-CHECKOUT (Housekeeping)                         │
│    - Receives notification: Room 305 dirty               │
│    - Cleans room                                         │
│    - Marks as clean                                      │
│    - Room available for next guest                       │
└──────────────────────────────────────────────────────────┘
```

### Workflow 2: Maintenance Request Flow

```
┌──────────────────────────────────────────────────────────┐
│ STEP 1: Request Creation                                 │
│ Who: Guest, Front Desk, Housekeeping                     │
│ Action: Create maintenance request                       │
│ Example: "Room 501 - AC not cooling"                     │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ STEP 2: Manager Review                                   │
│ Who: Manager                                             │
│ Action: Review request, set priority                     │
│ Priority: URGENT (guest complaint)                       │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ STEP 3: Assignment                                       │
│ Who: Manager/Admin                                       │
│ Action: Assign to maintenance technician                 │
│ Notification sent to technician's mobile                 │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ STEP 4: Work Execution                                   │
│ Who: Maintenance Staff                                   │
│ Action: Fix the issue                                    │
│ - Start work                                             │
│ - Diagnose problem                                       │
│ - Repair/replace parts                                   │
│ - Test solution                                          │
│ - Document: parts used, labor hours                      │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ STEP 5: Completion                                       │
│ Who: Maintenance Staff                                   │
│ Action: Mark as complete                                 │
│ Notifications sent to:                                   │
│ - Manager (for review)                                   │
│ - Front Desk (inform guest)                              │
│ - Guest (if applicable)                                  │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ STEP 6: Verification                                     │
│ Who: Manager/Admin                                       │
│ Action: Verify work completed satisfactorily             │
│ Close work order                                         │
└──────────────────────────────────────────────────────────┘
```

### Workflow 3: Night Audit Process

```
┌──────────────────────────────────────────────────────────┐
│ TIME: 12:00 AM (Midnight)                                │
│ WHO: System (automated) OR Manager (manual)              │
│                                                          │
│ STEP 1: Day Closure                                     │
│ - Close business day                                     │
│ - No more transactions for previous day                  │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ STEP 2: Post Room Charges                               │
│ - All occupied rooms: post room rate                     │
│ - Room 305: $150 posted to folio                        │
│ - Room 401: $200 posted to folio                        │
│ - Total: 45 rooms x average $165 = $7,425              │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ STEP 3: Update Room Statuses                            │
│ - Check-ins become "In-House"                           │
│ - Expected check-outs flagged                           │
│ - No-shows identified and handled                       │
│ - Stayovers confirmed                                   │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ STEP 4: Financial Reconciliation                        │
│ - Calculate daily revenue                               │
│   Room Revenue: $7,425                                  │
│   F&B Revenue: $1,850                                   │
│   Other: $325                                           │
│   Total: $9,600                                         │
│ - Reconcile payments                                    │
│ - Generate reports                                      │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ STEP 5: Generate Statistics                             │
│ - Occupancy: 90% (45/50 rooms)                         │
│ - ADR (Average Daily Rate): $165                        │
│ - RevPAR: $148.50                                       │
│ - Create daily statistics record                        │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ STEP 6: Manager Review (Morning)                        │
│ - Manager reviews night audit report                    │
│ - Check for discrepancies                               │
│ - Approve and proceed with new day                      │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Permission Matrix

| Module | Superuser | Admin | Manager | Front Desk | Housekeeping | Maintenance | Accountant | POS Staff | Guest |
|--------|-----------|-------|---------|------------|--------------|-------------|------------|-----------|-------|
| **Dashboard** | Full | Full | Full | Limited | Limited | Limited | Full | Limited | Own |
| **Properties** | CRUD | R | R | - | - | - | R | - | R |
| **Rooms** | CRUD | CRUD | RU | R | RU | R | R | - | R |
| **Reservations** | CRUD | CRUD | CRUD | CRUD | - | - | R | R | Own |
| **Guests** | CRUD | CRUD | CRUD | CRUD | - | - | R | R | Own |
| **Check-In/Out** | ✓ | ✓ | ✓ | ✓ | - | - | - | - | - |
| **Housekeeping** | CRUD | CRUD | CRUD | R | CRUD | - | - | - | - |
| **Maintenance** | CRUD | CRUD | CRUD | CR | CR | CRUD | R | - | - |
| **Billing** | CRUD | CRUD | R | R | - | - | CRUD | R | Own |
| **Invoices** | CRUD | CRUD | R | R | - | - | CRUD | - | Own |
| **POS** | CRUD | CRUD | R | - | - | - | R | CRUD | - |
| **Reports** | Full | Full | Full | Limited | - | - | Financial | Sales | - |
| **Night Audit** | ✓ | ✓ | ✓ | - | - | - | Review | - | - |
| **Users** | CRUD | RU | R | - | - | - | - | - | - |
| **Rates** | CRUD | CRUD | R | R | - | - | R | - | R |
| **Channels** | CRUD | CRUD | RU | R | - | - | - | - | - |
| **Notifications** | CRUD | CRUD | R | R | R | R | R | R | Own |
| **Settings** | CRUD | RU | R | - | - | - | - | - | - |

**Legend:**
- CRUD = Create, Read, Update, Delete
- R = Read only
- RU = Read & Update
- CR = Create & Read
- Own = Only their own data
- ✓ = Can perform action
- \- = No access

---

## 🏢 Multi-Property Setup

### How Properties Work:

**Scenario**: You own 3 hotels:
1. **Beach Resort** (50 rooms)
2. **City Hotel** (30 rooms)
3. **Mountain Lodge** (20 rooms)

**Setup Process:**

```
1. SUPERUSER creates properties:
   ├─ Create "Beach Resort"
   ├─ Create "City Hotel"
   └─ Create "Mountain Lodge"

2. SUPERUSER creates Admin for each:
   ├─ john@beach.com → Admin → Assign to Beach Resort
   ├─ mary@city.com → Admin → Assign to City Hotel
   └─ bob@mountain.com → Admin → Assign to Mountain Lodge

3. Each Admin manages their property:
   ├─ Beach Resort Admin (john@beach.com)
   │   ├─ Creates staff accounts
   │   ├─ Manages rooms
   │   └─ Can only see Beach Resort data
   │
   ├─ City Hotel Admin (mary@city.com)
   │   ├─ Creates staff accounts
   │   ├─ Manages rooms
   │   └─ Can only see City Hotel data
   │
   └─ Mountain Lodge Admin (bob@mountain.com)
       ├─ Creates staff accounts
       ├─ Manages rooms
       └─ Can only see Mountain Lodge data

4. Staff assigned to properties:
   ├─ Front Desk → Beach Resort → Can only check-in Beach Resort guests
   ├─ Housekeeping → City Hotel → Only sees City Hotel rooms
   └─ Maintenance → Mountain Lodge → Only Mountain Lodge work orders
```

**Data Isolation:**
- ✅ Each property's data is completely isolated
- ✅ Staff at Beach Resort cannot see City Hotel data
- ✅ Only Superuser sees all properties
- ✅ Each property has own:
  - Rooms
  - Reservations
  - Guests (property-specific)
  - Staff
  - Reports
  - Billing

---

## 🎯 Real-World Example: A Day at Beach Resort

**6:00 AM** - System runs night audit (automated)

**7:00 AM** - **Manager** logs in (Mobile)
- Reviews night audit report
- Checks today: 10 arrivals, 8 departures
- Assigns housekeeping tasks

**8:00 AM** - **Housekeeping** starts (Mobile)
- Opens app: 15 rooms assigned
- 8 checkouts (priority)
- 7 stayovers
- Starts cleaning Room 205

**9:00 AM** - **Accountant** logs in (Web)
- Reviews yesterday's revenue: $12,450
- Processes 3 corporate invoices
- Bank reconciliation

**10:00 AM** - **Maintenance** receives urgent request (Mobile)
- Room 405: AC not working
- Guest complaint (priority: URGENT)
- Goes to room, fixes thermostat
- Marks complete

**11:00 AM** - **Front Desk** handles checkout (Web/Mobile)
- Guest in Room 305 checking out
- Reviews folio: $396 total
- Processes payment
- Prints receipt
- Updates room status: Dirty

**12:00 PM** - **Housekeeping** cleans Room 305
- Marks room as clean
- Front desk notified
- Room available for 2 PM check-in

**2:00 PM** - **Front Desk** handles check-in (Web/Mobile)
- New guest arrives for Room 305
- Verify reservation
- Assign room key
- Status: Reserved → Checked In

**6:00 PM** - **POS Staff** takes restaurant order (Mobile)
- Guest from Room 401 dines
- Order: Dinner for 2 = $85
- Posts charge to Room 401 folio

**9:00 PM** - **Manager** reviews day (Web)
- Occupancy: 92% (46/50 rooms)
- Revenue today: $13,200
- All tasks completed
- No pending issues

**11:59 PM** - System prepares for night audit
- Day ends
- Ready for tomorrow

---

## 📱 Platform Access Summary

| Role | Web Access | Mobile Access | Primary Platform |
|------|------------|---------------|------------------|
| Superuser | ✅ | ❌ | Web only |
| Admin | ✅ | ✅ | Both equally |
| Manager | ✅ | ✅ | Both equally |
| Front Desk | ✅ | ✅ | Both equally |
| Housekeeping | ⚠️ Limited | ✅ | **Mobile primary** |
| Maintenance | ⚠️ Limited | ✅ | **Mobile primary** |
| Accountant | ✅ | ❌ | **Web only** |
| POS Staff | ✅ | ✅ | Both equally |
| Guest | ✅ | ✅ | Both equally |

---

## 🔐 Security Features

1. **Token-Based Authentication**: Secure login with tokens
2. **Role-Based Access**: Automatic permission enforcement
3. **Property Isolation**: Multi-tenant data separation
4. **Audit Logs**: All actions tracked
5. **Password Security**: Encrypted, secure storage
6. **Session Management**: Automatic timeout
7. **API Security**: Protected endpoints

---

## 📞 Getting Started

**For Property Owners (Superuser):**
1. Get credentials from system admin
2. Login to web interface
3. Create your first property
4. Add admin user for that property
5. Admin creates staff accounts

**For Staff:**
1. Receive credentials from Admin
2. Download mobile app (if applicable)
3. Login with your email/password
4. Complete profile
5. Start using based on your role

**For Guests:**
1. Download mobile app
2. Register account
3. Book a room
4. Use app during stay

---

## 🎓 Training Resources

Each role has specific training materials:
- **Admin/Manager**: Full system training
- **Front Desk**: Check-in/out procedures
- **Housekeeping**: Task management
- **Maintenance**: Work order system
- **Accountant**: Financial reports
- **POS Staff**: Order processing

---

## ❓ FAQ

**Q: Can a user have multiple roles?**
A: No, each user has one primary role. Contact admin to change roles.

**Q: Can staff access multiple properties?**
A: No, staff are assigned to one property only. Superuser sees all.

**Q: How do I change my role?**
A: Only Admin or Superuser can change roles.

**Q: Can Front Desk modify rates?**
A: No, only Admin and Manager can modify rates.

**Q: How do guests get login credentials?**
A: Guests register themselves or Front Desk creates account.

---

## 📊 System Summary

✅ **8 distinct roles** with specific permissions  
✅ **Multi-property support** with data isolation  
✅ **Web + Mobile** platforms  
✅ **Complete workflows** for all operations  
✅ **Security** built-in with RBAC  
✅ **Scalable** from 1 property to hundreds  

**The system is designed so each role sees only what they need to do their job efficiently!** 🎯
