# 🏨 Hotel Property Management System (PMS)

[![Backend Tests](https://img.shields.io/badge/backend%20tests-118%2F118%20passing-brightgreen)]()
[![Frontend](https://img.shields.io/badge/web%20frontend-43%20pages-blue)]()
[![Mobile](https://img.shields.io/badge/mobile%20app-31%20screens-blue)]()
[![Completion](https://img.shields.io/badge/completion-96%25-success)]()

A comprehensive Hotel PMS built with **Django REST Framework** (Backend), **Next.js** (Web Frontend), and **React Native Expo** (Mobile App).

## 🎯 Project Status: 96% Complete

- ✅ **Backend:** 100% (118 tests passing)
- ✅ **Web Frontend:** 98% (43 pages)
- ✅ **Mobile App:** 92% (31 screens)

**Ready for production deployment!**

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Backend runs on: http://localhost:8000

### 2. Start Web Frontend
```bash
cd web
npm install
npm run dev
```
Web runs on: http://localhost:3000

### 3. Start Mobile App
```bash
cd mobile
npm install
npm start
```
Scan QR code with Expo Go app

### Default Login
```
Email: admin@example.com
Password: admin123
```

---

## 🚀 Features

### 1. Front Desk Operations ✅
- Check-in/Check-out processing
- Walk-in reservations
- Room assignment and moves
- Daily arrivals/departures dashboard
- Guest messages and requests

### 2. Reservation Management ✅
- Individual and group reservations
- Multi-room bookings
- Date range selection with calendar
- Confirmation number generation
- Status workflow (Pending → Confirmed → Checked-In → Checked-Out)
- Cancellation and no-show handling
- Edit reservations (web and mobile)

### 3. Room Management ✅
- Room types with pricing
- Room inventory and availability
- Room status tracking
- Amenities management
- **Room image gallery** (upload, view, delete)
- Floor plans and room numbers

### 4. Guest Management ✅
- Guest profiles and database
- Personal information and preferences
- VIP status tracking
- Guest notes and history
- **Document management** (ID, passport, visa uploads)
- Loyalty programs
- Corporate accounts

### 5. Billing & Payments ✅
- Guest folios with detailed transactions
- **Complete charge posting** (ROOM, F&B, LAUNDRY, MINIBAR, etc.)
- **Payment recording** (CASH, CARD, BANK_TRANSFER, CHECK)
- Real-time balance calculation
- Invoice generation and printing
- **PDF/Excel export**
- Folio closure when fully paid

### 6. Point of Sale (POS) ✅
- Multiple outlet management
- **Complete menu management** (categories, items, images)
- Order processing and cart
- Post charges to guest folios
- Payment methods
- Sales history and reporting

### 7. Housekeeping Management ✅
- Task assignment and tracking
- Room status management (CLEAN, DIRTY, INSPECTED, etc.)
- Room inspections
- Linen and amenity inventory
- Mobile app for housekeeping staff

### 8. Maintenance ✅
- Maintenance request tracking
- Priority levels (LOW, MEDIUM, HIGH, URGENT)
- Assignment to technicians
- Status tracking
- Notes and updates

### 9. Rate & Revenue Management ✅
- Rate plans and packages
- Seasonal pricing
- Dynamic pricing rules
- Discounts and promotions

### 10. Reports & Analytics ✅
- Daily statistics and KPIs
- Occupancy reports
- Revenue reports
- **Advanced analytics dashboard** (NEW)
  - Revenue trends (area chart)
  - Occupancy forecasting (line chart)
  - Top room types (bar chart)
  - Revenue by channel (pie chart)
  - RevPAR and ADR calculations
  - Guest satisfaction metrics

### 11. Multi-property Management ✅
- **Property switcher** in header (NEW)
- Multiple properties support
- Property-specific filtering
- Cross-property reporting
- Centralized management

### 12. Notifications ✅
- **Real-time notification bell** (NEW)
- Unread count badge
- Mark as read functionality
- Auto-refresh every 30 seconds
- Notification types (info, success, warning, danger)

### 13. User Management ✅
- User profiles and settings
- Password change
- **User administration** (create, edit, delete)
- **Role-based access control**
- Permissions management

### 14. File Management ✅ (NEW)
- Drag-and-drop file upload
- Image preview and lightbox
- Document management
- File type and size validation
- Download and delete functionality

---

## Project Structure

```
PMS/
├── backend/                 # Django Backend
│   ├── apps/
│   │   ├── accounts/       # User management & authentication
│   │   ├── properties/     # Property & building management
│   │   ├── rooms/          # Room types & inventory
│   │   ├── reservations/   # Reservation management
│   │   ├── frontdesk/      # Front desk operations
│   │   ├── guests/         # Guest profiles & loyalty
│   │   ├── housekeeping/   # Housekeeping tasks
│   │   ├── maintenance/    # Maintenance requests
│   │   ├── billing/        # Folios & payments
│   │   ├── pos/            # Point of sale
│   │   ├── rates/          # Rate management
│   │   ├── channels/       # Channel manager
│   │   ├── reports/        # Reports & analytics
│   │   └── notifications/  # Alerts & notifications
│   ├── api/
│   │   └── v1/             # REST API endpoints
│   ├── config/             # Django settings
│   └── templates/          # HTML templates
│
├── mobile/                  # React Native Mobile App
│   ├── src/
│   │   ├── contexts/       # Auth context
│   │   ├── navigation/     # App navigation
│   │   ├── screens/        # App screens
│   │   └── services/       # API services
│   └── App.tsx
│
└── README.md
```

## Setup Instructions

### Backend Setup (Quick Start)

**Automated Setup (Recommended):**
```bash
cd backend
./setup_database.sh
```

This will:
- Create virtual environment
- Install dependencies
- Configure database
- Run migrations
- Verify all models
- Create necessary directories

**Manual Setup:**

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Create superuser:**
```bash
python manage.py createsuperuser
```

6. **Run development server:**
```bash
python manage.py runserver
```

**Access Points:**
- Admin Panel: http://localhost:8000/admin/
- API: http://localhost:8000/api/v1/
- Swagger API Docs: http://localhost:8000/swagger/
- ReDoc API Docs: http://localhost:8000/redoc/

**Test Database:**
```bash
python test_database.py
```

See [Backend Setup Guide](backend/SETUP.md) for detailed instructions and [Quick Reference](backend/QUICK_REFERENCE.md) for common commands.

### Mobile App Setup

1. **Install dependencies:**
```bash
cd mobile
npm install
```

2. **Update API URL:**
Edit `src/services/api.ts` and set your backend URL:
```typescript
const BASE_URL = 'http://your-ip:8000/api/v1';
```

3. **Start Expo:**
```bash
npm start
```

4. **Run on device/emulator:**
- Press `a` for Android
- Press `i` for iOS
- Scan QR code with Expo Go app

## User Roles

| Role | Access |
|------|--------|
| ADMIN | Full system access |
| MANAGER | Property management |
| FRONT_DESK | Check-in/out, reservations |
| HOUSEKEEPING | Room status, tasks |
| MAINTENANCE | Work orders |
| ACCOUNTANT | Billing, reports |
| POS_STAFF | POS operations |

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `GET /api/v1/auth/profile/` - Get profile

### Rooms
- `GET /api/v1/rooms/` - List rooms
- `GET /api/v1/rooms/{id}/` - Room details
- `POST /api/v1/rooms/{id}/status/` - Update status
- `GET /api/v1/rooms/availability/` - Check availability

### Reservations
- `GET /api/v1/reservations/` - List reservations
- `POST /api/v1/reservations/create/` - Create reservation
- `GET /api/v1/reservations/{id}/` - Reservation details
- `POST /api/v1/reservations/{id}/cancel/` - Cancel reservation

### Front Desk
- `GET /api/v1/frontdesk/dashboard/` - Dashboard stats
- `POST /api/v1/frontdesk/check-in/` - Process check-in
- `POST /api/v1/frontdesk/check-out/` - Process check-out

### Housekeeping
- `GET /api/v1/housekeeping/tasks/` - List tasks
- `GET /api/v1/housekeeping/my-tasks/` - My assigned tasks
- `POST /api/v1/housekeeping/tasks/{id}/start/` - Start task
- `POST /api/v1/housekeeping/tasks/{id}/complete/` - Complete task

### Maintenance
- `GET /api/v1/maintenance/requests/` - List requests
- `POST /api/v1/maintenance/requests/create/` - Create request
- `POST /api/v1/maintenance/requests/{id}/start/` - Start work
- `POST /api/v1/maintenance/requests/{id}/complete/` - Complete request

### Billing
- `GET /api/v1/billing/folios/{id}/` - Folio details
- `POST /api/v1/billing/folios/{id}/charges/` - Add charge
- `POST /api/v1/billing/folios/{id}/payments/` - Add payment

### Reports
- `GET /api/v1/reports/dashboard/` - Dashboard statistics
- `GET /api/v1/reports/occupancy/` - Occupancy report
- `GET /api/v1/reports/revenue/` - Revenue report

## Room Status Codes

| Code | Description |
|------|-------------|
| VC | Vacant Clean |
| VD | Vacant Dirty |
| OC | Occupied Clean |
| OD | Occupied Dirty |
| OOO | Out of Order |
| OOS | Out of Service |

## Technology Stack

### Backend
- Django 4.2+
- Django REST Framework
- SQLite (development) / PostgreSQL (production)
- Token Authentication

### Mobile
- React Native (Expo)
- React Navigation
- React Query
- React Native Paper (UI)
- Zustand (State)

## Development Notes

1. **Database**: SQLite is used for development. For production, configure PostgreSQL in `config/settings/production.py`.

2. **CORS**: CORS is enabled for all origins in development. Configure properly for production.

3. **Media Files**: User uploads are stored in `media/` directory.

4. **Static Files**: Run `python manage.py collectstatic` for production.

## License

This project is proprietary software.

## Support

For support, contact the development team.
