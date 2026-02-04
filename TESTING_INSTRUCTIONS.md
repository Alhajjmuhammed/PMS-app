# 🧪 COMPLETE SYSTEM TESTING GUIDE

**Date:** February 3, 2026  
**Status:** Both servers running and ready for testing

---

## 🚀 SERVERS RUNNING

✅ **Backend API:** http://localhost:8000  
✅ **Web Frontend:** http://localhost:3000

---

## 🔐 TEST CREDENTIALS

### Working Test User:
- **Email:** `testadmin@hotel.com`
- **Password:** `Test123456`
- **Role:** Admin (full access)

### Alternative Test Users (from database):
- `manager@hotel.com` / `password123` (Manager)
- `frontdesk@test.com` / `password123` (Front Desk)
- `housekeeping@test.com` / `password123` (Housekeeping)

---

## 📋 STEP-BY-STEP TESTING CHECKLIST

### Phase 1: Login & Authentication (5 minutes)

**Steps:**
1. ✅ Open browser: http://localhost:3000
2. ✅ Should redirect to: http://localhost:3000/login
3. ✅ Enter credentials:
   - Email: `testadmin@hotel.com`
   - Password: `Test123456`
4. ✅ Click "Sign In"
5. ✅ Should redirect to: http://localhost:3000/dashboard

**What to Check:**
- [ ] Login form displays correctly
- [ ] No console errors
- [ ] Form submission works
- [ ] Redirect happens after login
- [ ] Dashboard loads

**Expected Result:** You should see the dashboard with statistics

---

### Phase 2: Dashboard Testing (3 minutes)

**What to Check:**
- [ ] Dashboard shows statistics (occupancy, guests, revenue)
- [ ] Cards display data
- [ ] No "loading" state stuck
- [ ] Charts/graphs render (if any)
- [ ] Navigation menu visible

**Expected Data:**
- Properties: 5
- Rooms: 50
- Guests: 30+
- Reservations: 21

---

### Phase 3: Guests Module (5 minutes)

**Steps:**
1. ✅ Click "Guests" in navigation
2. ✅ URL: http://localhost:3000/guests
3. ✅ Should see list of guests (30+ guests)
4. ✅ Click "+ New Guest" button
5. ✅ Fill out form:
   - First Name: Test
   - Last Name: User
   - Email: testuser@example.com
   - Phone: +1-555-0123
   - Country: USA
6. ✅ Click "Save"
7. ✅ Guest should appear in list

**What to Check:**
- [ ] Guest list displays
- [ ] Search works
- [ ] New guest form opens
- [ ] Form submission works
- [ ] New guest appears in list
- [ ] Can click on guest to view details

---

### Phase 4: Reservations Module (5 minutes)

**Steps:**
1. ✅ Click "Reservations" in navigation
2. ✅ URL: http://localhost:3000/reservations
3. ✅ Should see list of reservations (21 reservations)
4. ✅ Try creating new reservation
5. ✅ Check different statuses (Confirmed, Checked-In, etc.)

**What to Check:**
- [ ] Reservation list displays
- [ ] Can filter by status
- [ ] Can create new reservation
- [ ] Reservation details show

---

### Phase 5: Rooms Module (3 minutes)

**Steps:**
1. ✅ Click "Rooms" in navigation
2. ✅ URL: http://localhost:3000/rooms
3. ✅ Should see list of rooms (50 rooms)

**What to Check:**
- [ ] Room list displays
- [ ] Room status visible (Available, Occupied, etc.)
- [ ] Room types shown
- [ ] Can view room details

---

### Phase 6: Properties Module (3 minutes)

**Steps:**
1. ✅ Click "Properties" in navigation
2. ✅ URL: http://localhost:3000/properties
3. ✅ Should see properties (5 properties)

**What to Check:**
- [ ] Property list displays
- [ ] Property details show
- [ ] Images display (if any)

---

### Phase 7: Other Modules (10 minutes)

**Test Each Module:**
- [ ] **Housekeeping:** http://localhost:3000/housekeeping (21 tasks)
- [ ] **Maintenance:** http://localhost:3000/maintenance (15 requests)
- [ ] **Billing:** http://localhost:3000/billing (16 folios)
- [ ] **Reports:** http://localhost:3000/reports (daily statistics)
- [ ] **POS:** http://localhost:3000/pos (2 outlets, 2 menu items)

**For Each Module Check:**
- [ ] Page loads without errors
- [ ] Data displays from backend
- [ ] Lists show records
- [ ] Forms work (if applicable)

---

## 🐛 COMMON ISSUES & SOLUTIONS

### Issue: "Cannot connect" or "Network Error"
**Solution:** 
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/properties/

# Check if web is running
curl http://localhost:3000
```

### Issue: Login fails
**Solution:**
- Make sure you're using: `testadmin@hotel.com` / `Test123456`
- Check browser console for errors (F12)
- Verify backend is running

### Issue: Data not showing
**Solution:**
- Check browser console (F12) for API errors
- Check Network tab for failed requests
- Verify 249 records exist in database

### Issue: 403 Forbidden errors
**Solution:** 
- This is normal for some role-based endpoints
- Try with different user roles
- Admin user has most permissions

---

## 📊 SUCCESS CRITERIA

### ✅ PASS = System Working
- Login works
- Dashboard displays
- At least 3 modules show data correctly
- Can create a new record (guest/reservation)
- No critical console errors

### ⚠️ PARTIAL = Needs Work
- Login works but some pages don't load
- Data displays but forms don't work
- Some modules work, others don't

### ❌ FAIL = Not Working
- Cannot log in
- Dashboard doesn't load
- No data displays
- Many console errors

---

## 🔍 DEBUGGING TIPS

### Check Backend Logs:
```bash
tail -f /tmp/backend.log
```

### Check Web Logs:
```bash
tail -f /tmp/web.log
```

### Check Browser Console:
1. Open browser
2. Press F12
3. Go to Console tab
4. Look for errors (red text)

### Check Network Requests:
1. Press F12
2. Go to Network tab
3. Try an action
4. Look for failed requests (red)

---

## 📝 TEST REPORT TEMPLATE

After testing, note:

```
✅ LOGIN: Working / Not Working
✅ DASHBOARD: Shows data / Empty / Error
✅ GUESTS: Working / Not Working / Partial
✅ RESERVATIONS: Working / Not Working / Partial
✅ ROOMS: Working / Not Working / Partial
✅ OTHER MODULES: List which work/don't work

OVERALL VERDICT:
- Backend API: ___% working
- Web Frontend: ___% working
- Overall: ___% complete

ISSUES FOUND:
1. 
2. 
3. 

WHAT WORKS WELL:
1. 
2. 
3. 
```

---

## 🎯 EXPECTED OUTCOME

**If Everything Works:**
- You can log in
- Dashboard shows: ~68% occupancy, 30+ guests, 21 reservations
- All pages load
- Data displays in lists
- Forms work for creating records
- **System is 95%+ complete** ✅

**If Some Issues:**
- Note what doesn't work
- Check console for errors
- This helps identify remaining 5-10% work

---

## 🆘 NEED HELP?

**Quick Health Check:**
```bash
cd /home/easyfix/Documents/PMS/backend
source venv/bin/activate
python -c "
import requests
# Test backend
r1 = requests.get('http://localhost:8000/api/v1/properties/')
print(f'Backend: HTTP {r1.status_code}')

# Test web
r2 = requests.get('http://localhost:3000')
print(f'Web: HTTP {r2.status_code}')

# Test login
r3 = requests.post(
    'http://localhost:8000/api/v1/auth/login/',
    json={'email': 'testadmin@hotel.com', 'password': 'Test123456'}
)
print(f'Login: HTTP {r3.status_code}')
if r3.status_code == 200:
    print(f'Token: {r3.json().get(\"token\")[:30]}...')
"
```

---

**Good luck testing! 🚀**

The moment of truth - let's see if this system really works! 💪
