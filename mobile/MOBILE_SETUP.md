# Hotel PMS Mobile App - Setup & Testing Guide

## Prerequisites
- Node.js 16+ installed
- Expo CLI installed (`npm install -g expo-cli`)
- Expo Go app on your phone (iOS/Android)
- Backend server running

## Quick Start

### 1. Install Dependencies
```bash
cd /home/easyfix/Documents/PMS/mobile
npm install
```

### 2. Configure API URL

The API URL is configured in `src/config/environment.ts`. 

**Current configuration:**
```typescript
apiUrl: 'http://192.168.100.114:8000/api/v1'
```

**Update based on your setup:**

- **Physical Device (Recommended):** Use your computer's IP
  ```typescript
  apiUrl: 'http://192.168.100.114:8000/api/v1'
  ```

- **Android Emulator:** Use special IP
  ```typescript
  apiUrl: 'http://10.0.2.2:8000/api/v1'
  ```

- **iOS Simulator:** Use localhost
  ```typescript
  apiUrl: 'http://localhost:8000/api/v1'
  ```

### 3. Start Backend Server

**Important:** Backend must be accessible from your network!

```bash
cd /home/easyfix/Documents/PMS/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

> Note: `0.0.0.0:8000` allows network access (not just localhost)

### 4. Start Mobile App

```bash
cd /home/easyfix/Documents/PMS/mobile
npm start
```

This will:
- Start Expo development server
- Display QR code in terminal
- Open Metro bundler in browser

### 5. Run on Device

**Option A: Physical Device (Recommended)**
1. Install "Expo Go" app from App Store/Play Store
2. Scan the QR code from terminal
3. App will load on your device

**Option B: Emulator**
- Press `a` for Android emulator
- Press `i` for iOS simulator (Mac only)

## Testing the Connection

### 1. Check Backend Accessibility

From your mobile device's network, test if backend is reachable:

```bash
# From another computer or phone browser, visit:
http://192.168.100.114:8000/swagger/
```

If it doesn't load, check:
- Backend is running with `0.0.0.0:8000`
- Firewall allows port 8000
- Both devices on same network

### 2. Test Login

Use existing superuser credentials:
- Email: `admin@hotel.com`
- Password: (your admin password)

Or create a new user:
```bash
cd backend
source venv/bin/activate
python manage.py createsuperuser
```

## Mobile App Features

The mobile app includes:

### ✅ Implemented Screens:
1. **Authentication**
   - Login screen
   - Auth context with token management

2. **Dashboard**
   - Overview stats
   - Quick actions

3. **Housekeeping**
   - Task list
   - Task details
   - Room status updates

4. **Maintenance**
   - Request list
   - Create new request
   - Request details

5. **Profile**
   - User profile
   - Settings

### 📱 Navigation:
- Stack navigation for auth flow
- Bottom tabs for main app
- Drawer/Stack for nested screens

## API Endpoints Used

The mobile app connects to these backend endpoints:

```typescript
// Authentication
POST   /api/v1/auth/login/          - Login
POST   /api/v1/auth/logout/         - Logout  
GET    /api/v1/auth/profile/        - Get user profile

// Housekeeping
GET    /api/v1/housekeeping/tasks/  - List tasks
GET    /api/v1/housekeeping/tasks/:id/ - Task detail
PATCH  /api/v1/housekeeping/tasks/:id/ - Update task

// Maintenance
GET    /api/v1/maintenance/         - List requests
POST   /api/v1/maintenance/         - Create request
GET    /api/v1/maintenance/:id/     - Request detail

// More endpoints available in Swagger docs
```

## Troubleshooting

### Issue: "Network Error" or "Cannot connect"

**Solutions:**
1. Check backend is running: `http://192.168.100.114:8000/`
2. Verify backend is accessible: Visit swagger on phone browser
3. Check API URL in `src/config/environment.ts`
4. Ensure both devices on same WiFi
5. Check firewall allows port 8000

### Issue: "401 Unauthorized"

**Solutions:**
1. Check credentials are correct
2. Verify user exists in database
3. Check token is being sent (inspect network tab)
4. Backend auth endpoint working: Test in Swagger

### Issue: Expo Go won't load

**Solutions:**
1. Clear Expo cache: `expo start -c`
2. Reinstall Expo Go app
3. Check node_modules: `rm -rf node_modules && npm install`
4. Update Expo: `npm update`

### Issue: "Couldn't connect to Metro"

**Solutions:**
1. Check firewall/antivirus
2. Restart Expo: `expo start -c`
3. Use tunnel mode: `expo start --tunnel`

## Development Commands

```bash
# Start development server
npm start

# Start with cache clear
expo start -c

# Start in tunnel mode (if network issues)
expo start --tunnel

# Run on Android
npm run android

# Run on iOS (Mac only)
npm run ios

# Check for updates
expo upgrade

# Install new package
npm install package-name

# Type checking
npx tsc --noEmit
```

## Project Structure

```
mobile/
├── src/
│   ├── config/
│   │   └── environment.ts      # API configuration ⚙️
│   ├── contexts/
│   │   └── AuthContext.tsx     # Auth state management
│   ├── navigation/
│   │   ├── RootNavigator.tsx   # Auth flow navigation
│   │   └── MainNavigator.tsx   # Main app navigation
│   ├── screens/
│   │   ├── auth/               # Login screen
│   │   ├── dashboard/          # Dashboard
│   │   ├── housekeeping/       # Housekeeping screens
│   │   ├── maintenance/        # Maintenance screens
│   │   └── profile/            # Profile screen
│   └── services/
│       └── api.ts              # API client with interceptors
├── App.tsx                     # App entry point
├── app.json                    # Expo configuration
└── package.json                # Dependencies
```

## Configuration Files

### environment.ts
```typescript
// Change environment here
dev: {
  apiUrl: 'http://192.168.100.114:8000/api/v1',
}
```

### app.json
```json
{
  "expo": {
    "name": "hotel-pms-mobile",
    "slug": "hotel-pms-mobile",
    "version": "1.0.0",
    "orientation": "portrait"
  }
}
```

## Network Configuration

### Backend Server (Required)

The backend MUST be started with network access:

```bash
# ❌ Wrong - Only localhost
python manage.py runserver

# ✅ Correct - Network accessible
python manage.py runserver 0.0.0.0:8000
```

### Firewall Configuration

Allow port 8000:
```bash
# Ubuntu/Debian
sudo ufw allow 8000

# Fedora/RHEL
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload

# Check if port is open
netstat -tuln | grep 8000
```

## Testing Checklist

- [ ] Backend running on `0.0.0.0:8000`
- [ ] Swagger accessible from mobile device browser
- [ ] API URL configured in environment.ts
- [ ] Mobile dependencies installed (`npm install`)
- [ ] Expo app started (`npm start`)
- [ ] Can scan QR code in Expo Go
- [ ] App loads without errors
- [ ] Login screen appears
- [ ] Can login with valid credentials
- [ ] Dashboard displays after login
- [ ] Can navigate between tabs
- [ ] API calls work (check network tab)

## Security Notes

### Development:
- Backend allows CORS from all origins ✅
- Token stored in SecureStore (encrypted) ✅
- HTTP acceptable for local development ✅

### Production:
- [ ] Use HTTPS for API
- [ ] Configure specific CORS origins
- [ ] Use environment variables for API URL
- [ ] Enable SSL pinning
- [ ] Implement refresh tokens
- [ ] Add biometric authentication

## Next Steps

After successful setup:

1. **Test all features:**
   - Login/Logout
   - View housekeeping tasks
   - Update task status
   - Create maintenance request
   - View profile

2. **Add more features:**
   - Check-in/Check-out
   - Guest management
   - Room assignment
   - Reservations view
   - Reports

3. **Improve UX:**
   - Add loading states
   - Error handling
   - Offline support
   - Push notifications
   - Image upload

## Support

### Get Your IP Address:
```bash
# Linux/Mac
ip a | grep "inet " | grep -v 127.0.0.1
# or
hostname -I

# Windows
ipconfig | findstr IPv4
```

### Test Backend Connectivity:
```bash
# From mobile device browser, visit:
http://YOUR_IP:8000/swagger/
```

### Expo Documentation:
- https://docs.expo.dev/
- https://reactnavigation.org/

### Backend API Docs:
- http://192.168.100.114:8000/swagger/

---

## Quick Test Command

Run this to verify everything:

```bash
# Terminal 1: Start Backend
cd /home/easyfix/Documents/PMS/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Start Mobile
cd /home/easyfix/Documents/PMS/mobile
npm start
```

Then open Expo Go on your phone and scan the QR code!

✅ **Mobile app is configured and ready to test!**
