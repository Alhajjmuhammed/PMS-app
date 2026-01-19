# 🧪 Testing Guide - Hotel PMS System

## Quick Start Testing

### 1. Backend API Testing

#### Start the Server
```bash
cd /home/easyfix/Documents/PMS/backend
python3 manage.py runserver
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
```

#### Test API Documentation
Open in browser:
- **Swagger UI:** http://localhost:8000/swagger/
- **ReDoc:** http://localhost:8000/redoc/

#### Test Specific Endpoints

**Authentication:**
```bash
# Login (get token)
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your_password"}'

# Response: {"token": "abc123...", "user": {...}}
```

**Properties (requires token):**
```bash
curl -X GET http://localhost:8000/api/v1/properties/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Rooms:**
```bash
curl -X GET http://localhost:8000/api/v1/rooms/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Rates (NEW):**
```bash
curl -X GET http://localhost:8000/api/v1/rates/plans/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Channels (NEW):**
```bash
curl -X GET http://localhost:8000/api/v1/channels/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Notifications (NEW):**
```bash
curl -X GET http://localhost:8000/api/v1/notifications/unread/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Reports (NEW):**
```bash
curl -X GET http://localhost:8000/api/v1/reports/dashboard/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

---

### 2. Mobile App Testing

#### Install Dependencies
```bash
cd /home/easyfix/Documents/PMS/mobile
npm install
```

#### Start Development Server
```bash
npm start
# or
npx expo start
```

#### Test on Device
1. Install Expo Go app on your phone
2. Scan QR code from terminal
3. App should load

#### Test Features
- ✅ Login screen should appear
- ✅ Error messages should display properly
- ✅ Loading states should show during API calls
- ✅ Navigation should work
- ✅ API calls should connect to localhost:8000

#### Change API URL (for testing)
Edit `/mobile/src/config/env.ts`:
```typescript
development: {
  API_URL: 'http://YOUR_IP:8000/api/v1',  // Use your machine's IP, not localhost
  API_BASE_URL: 'http://YOUR_IP:8000',
}
```

To find your IP:
```bash
hostname -I | awk '{print $1}'
```

---

### 3. Database Testing

#### Check Database Status
```bash
cd /home/easyfix/Documents/PMS/backend
python3 test_database.py
```

**Expected:** All 4 tests should pass ✅

#### View Database
```bash
python3 manage.py dbshell
```

SQLite commands:
```sql
.tables                    -- List all tables
.schema rooms_room         -- View table structure
SELECT * FROM rooms_room;  -- Query data
.quit                      -- Exit
```

---

### 4. Create Test Data

#### Create Superuser
```bash
cd /home/easyfix/Documents/PMS/backend
python3 manage.py createsuperuser
```

Enter:
- Email: `admin@test.com`
- Password: `admin123` (dev only!)

#### Access Admin Panel
http://localhost:8000/admin/

Login with superuser credentials and create:
1. **Property** - Add your hotel
2. **Room Types** - Add room categories (Single, Double, Suite)
3. **Rooms** - Add individual rooms
4. **Rate Plans** - Add pricing plans
5. **Seasons** - Add seasonal periods

---

### 5. End-to-End Testing Flow

#### Scenario: Book a Room

1. **Mobile: Login**
   - Open app
   - Enter credentials
   - Should navigate to dashboard

2. **Mobile: View Rooms**
   - Navigate to Rooms screen
   - Should see list of rooms
   - Should show availability status

3. **Mobile: Create Reservation**
   - Navigate to Reservations
   - Tap "New Reservation"
   - Fill in guest details
   - Select dates
   - Select room
   - Confirm booking

4. **Verify in Backend:**
   ```bash
   curl -X GET http://localhost:8000/api/v1/reservations/ \
     -H "Authorization: Token YOUR_TOKEN"
   ```

5. **Check in Admin:**
   - http://localhost:8000/admin/
   - Go to Reservations
   - Should see new booking

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** `ImproperlyConfigured: Database settings not found`
```bash
cd /home/easyfix/Documents/PMS/backend
# Check .env file exists
ls -la .env
# If missing, copy example
cp .env.example .env
```

**Problem:** `No module named 'rest_framework'`
```bash
cd /home/easyfix/Documents/PMS/backend
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** `Table doesn't exist`
```bash
python3 manage.py migrate
```

### Mobile Issues

**Problem:** `Unable to connect to server`
- Check backend is running: `curl http://localhost:8000/api/v1/properties/`
- Use IP address, not localhost in mobile config
- Check firewall allows port 8000

**Problem:** `Module not found`
```bash
cd /home/easyfix/Documents/PMS/mobile
rm -rf node_modules package-lock.json
npm install
```

**Problem:** `Expo error`
```bash
npm install -g expo-cli
expo doctor
```

---

## ✅ Test Checklist

### Backend Tests
- [ ] Server starts without errors
- [ ] Swagger UI loads at /swagger/
- [ ] Can create superuser
- [ ] Admin panel accessible
- [ ] All migrations applied
- [ ] Database test script passes
- [ ] API endpoints return 200/401
- [ ] Authentication works (login/logout)
- [ ] CRUD operations work for each module

### Mobile Tests
- [ ] App builds without errors
- [ ] TypeScript compiles successfully
- [ ] App loads on device/emulator
- [ ] Login screen appears
- [ ] Can navigate between screens
- [ ] Loading states display
- [ ] Error messages display
- [ ] API calls reach backend
- [ ] Authentication persists
- [ ] Can logout successfully

### Integration Tests
- [ ] Mobile can login via backend
- [ ] Mobile can fetch data from backend
- [ ] Mobile can create records in backend
- [ ] Changes reflect in admin panel
- [ ] Real-time updates work (if implemented)

---

## 📊 Test Results Template

```markdown
## Test Session: [Date]

### Environment
- Backend: Running on http://localhost:8000
- Mobile: Running on [Device/Simulator]
- Database: SQLite

### Backend Results
- [ ] System Check: PASS/FAIL
- [ ] Migrations: PASS/FAIL
- [ ] API Endpoints: X/83 working
- [ ] Authentication: PASS/FAIL
- Issues Found: [List any issues]

### Mobile Results
- [ ] Build: PASS/FAIL
- [ ] UI Load: PASS/FAIL
- [ ] Navigation: PASS/FAIL
- [ ] API Connection: PASS/FAIL
- Issues Found: [List any issues]

### Integration Results
- [ ] Login Flow: PASS/FAIL
- [ ] Data Sync: PASS/FAIL
- [ ] CRUD Operations: PASS/FAIL
- Issues Found: [List any issues]

### Summary
Overall Status: [READY/NEEDS WORK]
Next Actions: [List next steps]
```

---

## 🎯 Performance Benchmarks

### Expected Response Times
- Authentication: < 500ms
- List endpoints: < 1s
- Detail endpoints: < 500ms
- Create/Update: < 1s

### Mobile App
- Screen load: < 2s
- Navigation: < 200ms
- API call feedback: Immediate (loading state)

---

## 📝 Notes
- Use development server for testing only
- Don't use `DEBUG=True` in production
- Change `SECRET_KEY` before deploying
- Update API URLs in mobile config for production
- Add proper error logging for production
