# 📱 Mobile App Testing Guide

## 🚀 How to Run Mobile App

### Step 1: Start the Mobile App
```bash
cd /home/easyfix/Documents/PMS/mobile
npm install  # If not already installed
npm start    # Starts Expo development server
```

### Step 2: Open on Your Device

#### Option A: Physical Device (Recommended)
1. Install **Expo Go** app from:
   - **iOS**: App Store
   - **Android**: Google Play Store

2. **Connect to same WiFi** as your computer (192.168.100.116)

3. **Scan QR Code**:
   - iOS: Use Camera app to scan QR code in terminal
   - Android: Use Expo Go app to scan QR code

4. Wait for app to load

#### Option B: Android Emulator
```bash
cd /home/easyfix/Documents/PMS/mobile
npm run android
```

#### Option C: iOS Simulator (Mac only)
```bash
cd /home/easyfix/Documents/PMS/mobile
npm run ios
```

## 🔐 Mobile App Login Credentials

**IMPORTANT**: Mobile app connects to: `http://192.168.100.116:8000/api/v1`

### 🌍 System Administrators (Can See ALL Properties)

| Email | Password | Role | Access |
|-------|----------|------|--------|
| admin@test.com | test123 | Admin | ⭐ ALL Properties |
| admin@hotel.com | test123 | Admin | ⭐ ALL Properties |

### 🏨 Property Managers (See ONLY Their Hotel)

| Email | Password | Property | Access |
|-------|----------|----------|--------|
| manager.downtown@hotel.com | test123 | Manager | 🏢 Grand Hotel Downtown ONLY |
| manager.beach@resort.com | test123 | Manager | 🏖️ Beach Resort Paradise ONLY |
| manager.test@hotel.com | test123 | Manager | 🧪 Test Property ONLY |

### 👥 Staff Accounts (See ALL Properties - Not Yet Assigned)

| Email | Password | Role | Access |
|-------|----------|------|--------|
| frontdesk@hotel.com | test123 | Front Desk | 🌍 ALL Properties |
| maintenance@hotel.com | test123 | Maintenance | 🌍 ALL Properties |
| housekeeper@hotel.com | test123 | Housekeeping | 🌍 ALL Properties |

## 📋 Testing Checklist

### Test 1: System Admin Login
- [ ] Login with: admin@test.com / test123
- [ ] Should see dashboard with ALL properties
- [ ] Can view all reservations across all hotels
- [ ] Can access all modules

### Test 2: Hotel Manager Login (Property Restricted)
- [ ] Login with: manager.downtown@hotel.com / test123
- [ ] Should see "Grand Hotel Downtown" in header
- [ ] Dashboard shows ONLY Grand Hotel Downtown data
- [ ] Cannot see Beach Resort or Test property data

### Test 3: Different Hotel Manager
- [ ] Logout from previous manager
- [ ] Login with: manager.beach@resort.com / test123
- [ ] Should see "Beach Resort Paradise" in header
- [ ] Dashboard shows ONLY Beach Resort data
- [ ] Cannot see Grand Hotel or Test property data

## 🔧 Troubleshooting

### Issue: Cannot Connect to Backend
**Problem**: "Network Error" or "Unable to connect"

**Solutions**:
1. Check your computer's IP address:
   ```bash
   hostname -I  # On Linux
   ipconfig     # On Windows
   ifconfig     # On Mac
   ```

2. Update mobile API URL if IP changed:
   - Edit: `/home/easyfix/Documents/PMS/mobile/src/config/env.ts`
   - Change line 4: `API_URL: 'http://YOUR_NEW_IP:8000/api/v1'`

3. Make sure backend is running:
   ```bash
   cd /home/easyfix/Documents/PMS/backend
   source venv/bin/activate
   python manage.py runserver 0.0.0.0:8000
   ```

4. Check firewall allows port 8000

### Issue: QR Code Not Working
- Make sure phone and computer are on **same WiFi network**
- Try typing the URL manually in Expo Go app
- Use tunnel mode: `expo start --tunnel`

### Issue: App Crashes on Login
- Clear Expo cache: `expo start -c`
- Check backend logs for errors
- Verify credentials are correct

## 📱 Mobile App Features

The mobile app includes:
- ✅ Login / Logout
- ✅ Dashboard with stats
- ✅ Reservations management
- ✅ Guest management
- ✅ Room management
- ✅ Front desk operations
- ✅ Housekeeping tasks
- ✅ Maintenance requests
- ✅ POS / Billing
- ✅ Reports
- ✅ Notifications
- ✅ Profile management

## 🔐 Security Notes

- Mobile app uses **Token-based authentication**
- Tokens are stored securely in device storage
- All API requests include `Authorization: Token <token>` header
- Property filtering happens automatically on backend
- Managers can ONLY see data from their assigned property

## 📞 Support

If you encounter issues:
1. Check backend is running: http://192.168.100.116:8000
2. Check API docs: http://192.168.100.116:8000/swagger/
3. View backend logs for errors
4. Test login with curl first to verify backend works

---
**Last Updated**: January 22, 2026
**Backend**: http://192.168.100.116:8000
**Mobile Network**: 192.168.100.116:8081 (Expo)
