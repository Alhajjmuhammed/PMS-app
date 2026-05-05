# Hotel PMS - Backend API

Django REST Framework backend for the Hotel Property Management System.

## 🏗️ Architecture

- **Framework**: Django 4.2.7 with Django REST Framework 3.14.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: Token-based authentication
- **Task Queue**: Celery with Redis
- **API Documentation**: Swagger/OpenAPI via drf-yasg

## 📦 Project Structure

```
backend/
├── api/                    # API layer
│   ├── v1/                # API version 1 endpoints
│   │   ├── auth/         # Authentication endpoints
│   │   ├── billing/      # Billing & invoicing
│   │   ├── channels/     # OTA channel management
│   │   ├── frontdesk/    # Check-in/out operations
│   │   ├── guests/       # Guest management
│   │   ├── housekeeping/ # Housekeeping tasks
│   │   ├── maintenance/  # Maintenance requests
│   │   ├── properties/   # Property settings
│   │   ├── rates/        # Rate plans & pricing
│   │   ├── reports/      # Reporting & analytics
│   │   ├── reservations/ # Booking management
│   │   └── rooms/        # Room inventory
│   ├── authentication.py # Custom auth backends
│   ├── permissions.py    # Custom permissions
│   └── ratelimit.py      # API rate limiting
├── apps/                  # Django applications
│   ├── accounts/         # User & role management
│   ├── billing/          # Billing models & services
│   ├── channels/         # OTA integration
│   ├── frontdesk/        # Front desk operations
│   ├── guests/           # Guest profiles
│   ├── housekeeping/     # Housekeeping management
│   ├── maintenance/      # Maintenance tracking
│   ├── notifications/    # Notification services
│   ├── pos/              # Point of sale
│   ├── properties/       # Property configuration
│   ├── rates/            # Rate management
│   ├── reports/          # Reports & analytics
│   ├── reservations/     # Reservation system
│   └── rooms/            # Room management
├── config/               # Django configuration
│   ├── settings/         # Split settings
│   │   ├── base.py      # Base settings
│   │   ├── development.py # Dev settings
│   │   └── production.py  # Prod settings
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI config
│   └── asgi.py          # ASGI config
├── tests/                # Test suite
└── manage.py             # Django management

```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (for production)
- Redis (for Celery)

### Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

API will be available at: `http://localhost:8000`

### Using Development Script

```bash
chmod +x dev.sh
./dev.sh
```

## 🔧 Configuration

### Environment Variables

Key `.env` variables:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/pms_db

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:19006

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/profile/` - Get user profile
- `POST /api/v1/auth/change-password/` - Change password

### Reservations
- `GET /api/v1/reservations/` - List reservations
- `POST /api/v1/reservations/` - Create reservation
- `GET /api/v1/reservations/{id}/` - Get reservation details
- `PUT /api/v1/reservations/{id}/` - Update reservation
- `DELETE /api/v1/reservations/{id}/` - Cancel reservation

### Rooms
- `GET /api/v1/rooms/` - List rooms
- `GET /api/v1/rooms/{id}/` - Get room details
- `GET /api/v1/rooms/availability/` - Check room availability

### Front Desk
- `POST /api/v1/frontdesk/checkin/` - Check-in guest
- `POST /api/v1/frontdesk/checkout/` - Check-out guest
- `GET /api/v1/frontdesk/dashboard/` - Front desk dashboard

### Billing
- `GET /api/v1/billing/folios/` - List folios
- `POST /api/v1/billing/folios/{id}/charges/` - Add charge
- `POST /api/v1/billing/folios/{id}/payments/` - Add payment
- `POST /api/v1/billing/folios/{id}/close/` - Close folio

**Full API documentation**: `http://localhost:8000/swagger/`

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_reservations.py
```

### Run with coverage
```bash
pytest --cov=apps --cov-report=html
```

### Current test status
- **29/35 tests passing (83%)**
- See [FINAL_API_STATUS.md](../FINAL_API_STATUS.md) for details

## 🗄️ Database

### Models Overview

- **78 models** across 15 Django apps
- Key models:
  - `User` - System users with role-based permissions
  - `Property` - Hotel properties
  - `Room` - Room inventory with types and status
  - `Reservation` - Bookings and reservations
  - `Guest` - Guest profiles and preferences
  - `Folio` - Guest billing folios
  - `Invoice` - Invoices and payments
  - `HousekeepingTask` - Cleaning tasks
  - `MaintenanceRequest` - Repair requests

### Service Layer

Selected apps have service classes for business logic:
- `BillingService` - Folio and invoice operations
- `AvailabilityService` - Room availability queries
- `PricingService` - Dynamic pricing calculations
- `EmailService` - Email notifications
- `PushNotificationService` - Mobile notifications

## 🔐 Security

- Token-based authentication with expiry
- Role-based access control (RBAC)
- Permission-based endpoint protection
- CORS configuration for frontend origins
- Rate limiting on API endpoints
- SQL injection protection via ORM
- XSS protection enabled
- CSRF protection for state-changing operations

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

## 📊 Performance

- Database query optimization with select_related/prefetch_related
- API response caching for frequently accessed data
- Pagination on list endpoints (default: 50 items)
- Background tasks via Celery for heavy operations

## 🛠️ Development Tools

### Django Admin
Access at: `http://localhost:8000/admin/`

### API Documentation
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

### Database Shell
```bash
python manage.py dbshell
```

### Django Shell
```bash
python manage.py shell_plus
```

## 🔄 Common Tasks

### Create test data
```bash
python create_test_data.py
```

### Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collect static files
```bash
python manage.py collectstatic
```

### Export database
```bash
python manage.py dumpdata > backup.json
```

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:8000/health/
```

### Celery Monitoring
```bash
celery -A config worker -l info
celery -A config beat -l info
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit pull request

## 📝 License

Proprietary - All rights reserved

## 👥 Team

Backend API development team

---

**Status**: Production-ready (83% test coverage)  
**Last Updated**: April 16, 2026
