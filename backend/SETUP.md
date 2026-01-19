# Hotel PMS - Setup Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Quick Start

### 1. Clone/Navigate to the project
```bash
cd /home/easyfix/Documents/PMS/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Configuration
Copy the example environment file and configure:
```bash
cp .env.example .env
```

Edit `.env` file with your settings (SECRET_KEY, database credentials, etc.)

### 6. Database Setup
```bash
# Create migrations (if needed)
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

### 8. Create Static Files Directory
```bash
mkdir -p static staticfiles media
```

### 9. Run Development Server
```bash
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

Admin panel: http://127.0.0.1:8000/admin/

## Database Configuration

### SQLite (Default - Development)
Already configured in `.env`:
```
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

### PostgreSQL (Production)
Update `.env`:
```
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=hotel_pms
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

Then update `config/settings/base.py` to use these variables:
```python
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DATABASE_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DATABASE_USER', ''),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', ''),
        'PORT': os.getenv('DATABASE_PORT', ''),
    }
}
```

## Verify Installation

Run the test script:
```bash
python manage.py check
```

Check database connectivity:
```bash
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('✅ Database connected!')"
```

## Common Commands

### Database
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (CAUTION: Deletes all data)
rm db.sqlite3
python manage.py migrate

# Create database backup (SQLite)
cp db.sqlite3 db.sqlite3.backup
```

### Development
```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080

# Run on all interfaces
python manage.py runserver 0.0.0.0:8000

# Open Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser
```

### Code Quality
```bash
# Format code with black
black .

# Check code style
flake8

# Sort imports
isort .
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=apps

# Run specific test file
pytest apps/properties/tests.py
```

## Project Structure
```
backend/
├── apps/                    # Django applications
│   ├── accounts/           # User management
│   ├── properties/         # Property management
│   ├── rooms/              # Room management
│   ├── reservations/       # Reservation system
│   ├── frontdesk/          # Check-in/out operations
│   ├── guests/             # Guest profiles
│   ├── housekeeping/       # Housekeeping tasks
│   ├── maintenance/        # Maintenance requests
│   ├── billing/            # Billing & payments
│   ├── pos/                # Point of sale
│   ├── rates/              # Rate management
│   ├── channels/           # Channel manager
│   ├── reports/            # Reports & analytics
│   └── notifications/      # Notifications
├── api/                    # REST API
│   └── v1/                 # API version 1
├── config/                 # Django configuration
│   ├── settings/           # Settings modules
│   │   ├── base.py        # Base settings
│   │   ├── development.py # Development settings
│   │   └── production.py  # Production settings
│   ├── urls.py            # URL configuration
│   └── wsgi.py            # WSGI configuration
├── static/                 # Static files (CSS, JS)
├── staticfiles/           # Collected static files
├── media/                 # User uploads
├── templates/             # HTML templates
├── venv/                  # Virtual environment
├── .env                   # Environment variables
├── .env.example           # Environment template
├── .gitignore            # Git ignore file
├── db.sqlite3            # SQLite database
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/v1/`

### Authentication
- POST `/api/v1/auth/login/` - Login
- POST `/api/v1/auth/logout/` - Logout
- POST `/api/v1/auth/register/` - Register

### Properties
- GET `/api/v1/properties/` - List properties
- POST `/api/v1/properties/` - Create property
- GET `/api/v1/properties/{id}/` - Get property
- PUT `/api/v1/properties/{id}/` - Update property

### Rooms
- GET `/api/v1/rooms/` - List rooms
- POST `/api/v1/rooms/` - Create room
- GET `/api/v1/rooms/{id}/` - Get room
- PUT `/api/v1/rooms/{id}/` - Update room

### Reservations
- GET `/api/v1/reservations/` - List reservations
- POST `/api/v1/reservations/` - Create reservation
- GET `/api/v1/reservations/{id}/` - Get reservation
- PUT `/api/v1/reservations/{id}/` - Update reservation

### More endpoints...
See API documentation at: http://127.0.0.1:8000/swagger/

## Troubleshooting

### "No module named 'django'"
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "DATABASES setting not configured"
- Check that `config/settings/base.py` has DATABASES configuration
- Verify `.env` file exists and has correct values

### "Can't connect to database"
- For SQLite: Check file permissions on `db.sqlite3`
- For PostgreSQL: Verify PostgreSQL is running and credentials are correct

### Port already in use
```bash
# Use different port
python manage.py runserver 8080

# Or kill process using port 8000 (Linux)
lsof -ti:8000 | xargs kill -9
```

## Security Notes

### For Production:
1. Generate a new SECRET_KEY:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

2. Update `.env`:
```
SECRET_KEY=your-new-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOW_ALL_ORIGINS=False
```

3. Use PostgreSQL instead of SQLite
4. Configure proper CORS settings
5. Set up HTTPS
6. Use environment-specific settings

## Support

For issues or questions, please check:
- Project documentation
- Django documentation: https://docs.djangoproject.com/
- DRF documentation: https://www.django-rest-framework.org/

## Next Steps

1. ✅ Database configured and working
2. Create sample data (properties, rooms, etc.)
3. Set up API documentation
4. Configure production settings
5. Deploy to server
