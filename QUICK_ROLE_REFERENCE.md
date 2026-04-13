# 🎭 Quick Role Reference Card

## 👤 User Roles at a Glance

### 🏆 SUPERUSER
**Platform:** Web only  
**Can:**
- ✅ Manage ALL properties
- ✅ Create/delete properties  
- ✅ Manage all users
- ✅ System configuration

**Cannot:**
- ❌ (Has full access)

**Login Example:**
```
Email: owner@pms.com
Dashboard → See all 3 properties → Switch between them
```

---

### 👔 ADMIN
**Platform:** Web + Mobile  
**Can:**
- ✅ Full property management
- ✅ Manage staff (edit only)
- ✅ All operations
- ✅ Financial reports
- ✅ Run night audit

**Cannot:**
- ❌ Create/delete users
- ❌ Access other properties
- ❌ Delete property

**Typical Day:**
```
9:00 AM  → Check dashboard (occupancy, revenue)
10:00 AM → Review staff schedules
12:00 PM → Handle VIP arrival
3:00 PM  → Review maintenance issues
5:00 PM  → Check reports
```

---

### 📊 MANAGER
**Platform:** Web + Mobile  
**Can:**
- ✅ View all operations
- ✅ Manage reservations
- ✅ Assign tasks
- ✅ View reports
- ✅ Handle guest issues

**Cannot:**
- ❌ Modify rates
- ❌ Full billing access
- ❌ Manage users
- ❌ Night audit execution

**Typical Day:**
```
7:00 AM  → Review night audit
8:00 AM  → Check arrivals/departures
10:00 AM → Assign housekeeping
2:00 PM  → Monitor operations
6:00 PM  → Daily report review
```

---

### 🎯 FRONT DESK
**Platform:** Web + Mobile  
**Can:**
- ✅ Check-in/Check-out
- ✅ Create reservations
- ✅ Manage guests
- ✅ View bills
- ✅ Process payments

**Cannot:**
- ❌ Modify rates
- ❌ Access financial reports
- ❌ Manage staff
- ❌ Delete reservations

**Quick Actions:**
```
Check-In:
1. Find reservation → Verify ID → Assign room → Check-in ✓

Check-Out:
1. Open folio → Review charges → Process payment → Check-out ✓

New Booking:
1. Search availability → Create guest → Book room → Confirm ✓
```

---

### 🧹 HOUSEKEEPING
**Platform:** Mobile primary  
**Can:**
- ✅ View assigned tasks
- ✅ Update room status
- ✅ Report issues
- ✅ Track time/progress

**Cannot:**
- ❌ View guest info
- ❌ Access reservations
- ❌ See billing
- ❌ Assign own tasks

**Daily Workflow:**
```
8:00 AM  → Login → See 15 rooms assigned
9:00 AM  → Start Room 205 → Clean → Mark Clean
11:00 AM → Complete 5 rooms
1:00 PM  → Lunch break
2:00 PM  → Complete remaining 10 rooms
3:00 PM  → All done ✓
```

---

### 🔧 MAINTENANCE
**Platform:** Mobile primary  
**Can:**
- ✅ View work orders
- ✅ Update task status
- ✅ Report parts used
- ✅ Create new requests

**Cannot:**
- ❌ View guest info
- ❌ Access reservations
- ❌ Delete requests
- ❌ See financials

**Request Handling:**
```
URGENT Request: "Room 405 AC broken"
1. Receive alert
2. Go to room
3. Start work
4. Fix issue
5. Add notes + photo
6. Mark complete
7. Guest notified ✓
```

---

### 💰 ACCOUNTANT
**Platform:** Web only  
**Can:**
- ✅ All financial reports
- ✅ Billing/invoices (full)
- ✅ Process payments
- ✅ Night audit review
- ✅ Export data

**Cannot:**
- ❌ Modify reservations
- ❌ Check-in guests
- ❌ Manage staff
- ❌ Modify rates

**Monthly Tasks:**
```
Week 1: Daily reconciliation
Week 2: Invoice processing
Week 3: Report generation
Week 4: Month-end closing
```

---

### 🍽️ POS STAFF
**Platform:** Web + Mobile  
**Can:**
- ✅ Process orders
- ✅ Post room charges
- ✅ Cash/card payments
- ✅ Manage menu
- ✅ Shift reports

**Cannot:**
- ❌ View full guest data
- ❌ Access reservations
- ❌ See other departments
- ❌ Manage staff

**Order Flow:**
```
1. Take order → Table 5 → $45
2. Choose: Room charge or Cash/Card
3. If room: Enter room 305 → Post to folio
4. Send to kitchen
5. Serve → Close bill ✓
```

---

### 🏨 GUEST
**Platform:** Web + Mobile  
**Can:**
- ✅ Book rooms
- ✅ View own reservations
- ✅ View own bills
- ✅ Request services
- ✅ Leave reviews

**Cannot:**
- ❌ See other guests
- ❌ Access operations
- ❌ View reports
- ❌ Modify rates

**Guest Journey:**
```
1. Download app
2. Register
3. Search & book
4. Receive confirmation
5. Check-in (app/desk)
6. Use during stay
7. Check-out
8. Leave review
```

---

## 🔐 Permission Quick Reference

| Action | Super | Admin | Manager | Front | House | Maint | Acct | POS | Guest |
|--------|-------|-------|---------|-------|-------|-------|------|-----|-------|
| Create Property | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Check-In/Out | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Update Rooms | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| View Reports | ✅ | ✅ | ✅ | ⚠️ | ❌ | ❌ | ✅ | ⚠️ | ❌ |
| Modify Rates | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Process Billing | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ | ✅ | ⚠️ | ❌ |
| Night Audit | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ⚠️ | ❌ | ❌ |

**Legend:** ✅ Full Access | ⚠️ Limited | ❌ No Access

---

## 📱 Platform Matrix

| Role | Web | Mobile | Primary |
|------|-----|--------|---------|
| Superuser | ✅ | ❌ | Web |
| Admin | ✅ | ✅ | Both |
| Manager | ✅ | ✅ | Both |
| Front Desk | ✅ | ✅ | Both |
| Housekeeping | ⚠️ | ✅ | **Mobile** |
| Maintenance | ⚠️ | ✅ | **Mobile** |
| Accountant | ✅ | ❌ | **Web** |
| POS Staff | ✅ | ✅ | Both |
| Guest | ✅ | ✅ | Both |

---

## 🎯 Common Scenarios

### Scenario 1: Guest Complaint - AC Not Working
```
Guest (Room 405) → Calls Front Desk
   ↓
Front Desk → Creates Maintenance Request (URGENT)
   ↓
Manager → Reviews & Assigns to Technician
   ↓
Maintenance → Receives Alert → Goes to Room
   ↓
Maintenance → Fixes AC → Marks Complete
   ↓
Front Desk → Notified → Calls Guest
   ↓
Guest → Confirms AC Working ✓
```

### Scenario 2: Check-Out with Restaurant Charge
```
Guest → Arrives at Front Desk for Checkout
   ↓
Front Desk → Opens Folio → Reviews Charges
   - Room: $300 (2 nights)
   - Restaurant: $45 (posted by POS Staff)
   - Tax: $34.50
   - Total: $379.50
   ↓
Guest → Pays by Credit Card
   ↓
Front Desk → Process Payment → Print Receipt
   ↓
Housekeeping → Receives Alert: Room 405 Dirty
   ↓
Housekeeping → Cleans Room → Marks Clean
   ↓
Front Desk → Room Available for Next Guest ✓
```

### Scenario 3: VIP Arrival
```
Week Before:
Admin → Reviews reservation → Notes: VIP Guest
   ↓
Manager → Assigns best room (Suite 801)
   ↓
Front Desk → Prepares welcome amenities

Day of Arrival:
Front Desk → Fast-track check-in
   ↓
Housekeeping → Extra attention to room
   ↓
Manager → Personal greeting
   ↓
POS Staff → Complimentary welcome drink
   ↓
VIP Guest → Happy Experience ✓
```

---

## 🔄 Data Flow Example

### New Reservation → Check-Out Flow
```
1. BOOKING
   Guest Portal → Creates reservation
   → Database: Reservation created (status: Reserved)

2. PRE-ARRIVAL
   Front Desk → Views arrivals
   → Assigns Room 305

3. CHECK-IN
   Front Desk → Guest arrives
   → Database: Status = Checked In
   → Folio created

4. DURING STAY
   POS Staff → Guest orders dinner ($45)
   → Database: Charge added to Folio
   Housekeeping → Daily cleaning
   → Database: Room cleaned logs

5. CHECK-OUT
   Front Desk → Guest checks out
   → Database: 
     - Status = Checked Out
     - Payment recorded
     - Room status = Dirty
   
6. CLEANUP
   Housekeeping → Cleans room
   → Database: Room status = Clean
   → Available for next guest
```

---

## 📊 Key Metrics by Role

### Admin/Manager View:
- Occupancy Rate: 92%
- Revenue Today: $13,200
- ADR: $165
- RevPAR: $151.80
- Pending Tasks: 5
- Guest Satisfaction: 4.5/5

### Front Desk View:
- Arrivals Today: 10
- Departures Today: 8
- In-House: 46
- Available Rooms: 4
- Pending Folios: 3

### Housekeeping View:
- Rooms Assigned: 15
- Completed: 10
- In Progress: 2
- Pending: 3
- Avg Time: 28 min/room

### Maintenance View:
- Open Requests: 8
- Urgent: 2
- Completed Today: 5
- Parts Used: $345

### Accountant View:
- Revenue (Month): $385,000
- Outstanding Invoices: 5
- Collections: 95%
- Pending Payments: $12,450

---

## 🎓 Training Time Estimates

| Role | Training Time | Certification |
|------|---------------|---------------|
| Superuser | 4 hours | Not required |
| Admin | 8 hours | Recommended |
| Manager | 6 hours | Recommended |
| Front Desk | 4 hours | **Required** |
| Housekeeping | 2 hours | Basic |
| Maintenance | 2 hours | Basic |
| Accountant | 6 hours | Recommended |
| POS Staff | 3 hours | Required |
| Guest | Self-serve | No |

---

## 🆘 Quick Help

**Forgot Password?**
- Login page → "Forgot Password"
- Enter email → Reset link sent

**Can't See Expected Data?**
- Check: Are you assigned to correct property?
- Contact: Your Admin

**Permission Denied Error?**
- Your role doesn't have access
- Contact: Manager or Admin

**Mobile App Issues?**
- Clear cache and restart
- Update to latest version
- Check internet connection

---

## 📞 Support Contacts

**Technical Issues:**
- System Admin: admin@pms.com

**Account Issues:**
- Property Admin: your-admin@property.com

**Training:**
- Training Team: training@pms.com

---

## ✅ Quick Checklist

### For Admins:
- [ ] Create property
- [ ] Add staff users
- [ ] Configure rooms
- [ ] Set up rates
- [ ] Test check-in/out
- [ ] Train staff

### For Front Desk:
- [ ] Login credentials
- [ ] Practice check-in
- [ ] Practice check-out
- [ ] Know emergency procedures
- [ ] Understand payment processing

### For Housekeeping:
- [ ] Download mobile app
- [ ] Login and test
- [ ] Understand task system
- [ ] Know how to report issues

### For Maintenance:
- [ ] Download mobile app
- [ ] Login and test
- [ ] Understand priority system
- [ ] Know inventory system

---

**For detailed workflows, see:** [ROLE_BASED_WORKFLOW_GUIDE.md](ROLE_BASED_WORKFLOW_GUIDE.md)
