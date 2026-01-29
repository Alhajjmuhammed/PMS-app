# PMS System - Login Credentials

## 🔐 All User Accounts

All users now have the password: **test123**

### 🌍 System Administrators (Full Access to ALL Properties)

| Email | Password | Role | Access Level |
|-------|----------|------|--------------|
| admin@test.com | test123 | FRONT_DESK | ⭐ Superuser - ALL Properties |
| admin@hotel.com | test123 | FRONT_DESK | ⭐ Superuser - ALL Properties |
| frontdesk@hotel.com | test123 | FRONT_DESK | ALL Properties |
| maintenance@hotel.com | test123 | MAINTENANCE | ALL Properties |
| housekeeper@hotel.com | test123 | HOUSEKEEPING | ALL Properties |
| test@test.com | test123 | FRONT_DESK | ALL Properties |

### 🏨 Property Managers (Access to ONLY Their Assigned Property)

| Email | Password | Role | Assigned Property |
|-------|----------|------|-------------------|
| manager.downtown@hotel.com | test123 | MANAGER | 🏢 Grand Hotel Downtown |
| manager.beach@resort.com | test123 | MANAGER | 🏖️ Beach Resort Paradise |
| manager.test@hotel.com | test123 | MANAGER | 🧪 Test Property |

## � Properties in System

| Property Name | Code | Type | Rooms | Location |
|---------------|------|------|-------|----------|
| Grand Hotel Downtown | GHD001 | Hotel | 50 | New York, USA ⭐⭐⭐⭐⭐ |
| Beach Resort Paradise | BRP002 | Resort | 100 | Miami, USA ⭐⭐⭐⭐ |
| Test | TST | Hotel | 0 | Test Location ⭐⭐⭐ |

## 🔐 How Multi-Property Access Works

### System Administrator (Superuser)
- **Who**: admin@test.com, admin@hotel.com
- **Can See**: ALL 3 properties
- **Can Do**: Create/edit/delete any data across all properties

### Property Manager
- **Who**: manager.downtown@hotel.com, manager.beach@resort.com, manager.test@hotel.com
- **Can See**: ONLY their assigned property
- **Can Do**: Manage only their property's rooms, reservations, staff, etc.

### 🧪 Test It Yourself

1. **Login as System Admin** (admin@test.com)
   - Go to Properties page → You'll see all 3 hotels
   - Go to Dashboard → You'll see combined data from all properties

2. **Login as Hotel Manager** (manager.downtown@hotel.com)
   - Go to Properties page → You'll only see "Grand Hotel Downtown"
   - Go to Dashboard → You'll only see data from Grand Hotel Downtown
   - All reservations, rooms, reports filtered to your hotel only

3. **Login as Beach Resort Manager** (manager.beach@resort.com)
   - You'll only see "Beach Resort Paradise" data
   - Cannot see or access Grand Hotel Downtown data

## �🌐 API Endpoints

### Backend Server
- **Base URL**: http://localhost:8000
- **API URL**: http://localhost:8000/api/v1
- **Network URL**: http://192.168.100.116:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/swagger/

### Frontend Apps
- **Web App**: http://localhost:3000
- **Mobile App**: http://192.168.100.116:8081 (Expo)

## 📱 Login Instructions

### Web App (http://localhost:3000/login)
1. Open browser to http://localhost:3000/login
2. Enter email and password
3. Click "Sign In"

### Mobile App (Expo)
1. Scan QR code with Expo Go app
2. Wait for app to load
3. Enter email and password on login screen
4. Tap "Login"

### API Direct (for testing)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"test123"}'
```

## ✅ Verified Working
- ✅ Backend API: Running on port 8000
- ✅ Login endpoint: /api/v1/auth/login/ (tested successfully)
- ✅ Web App: Running on port 3000
- ✅ Mobile App: Running on Expo

## 🔧 Quick Test Commands

### Test Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"test123"}'
```

### Test Authenticated Request
```bash
# Get the token from login response, then:
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## 📝 Notes
- All passwords have been set to "test123" for easy testing
- Mobile app uses network IP (192.168.100.116) to connect from physical devices
- Web app uses localhost as it runs on the same machine
- CORS is enabled for all origins in development mode

---
Last Updated: January 22, 2026
