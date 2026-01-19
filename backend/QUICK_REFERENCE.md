# Hotel PMS - Quick Reference

## 🚀 Quick Start Commands

```bash
# Setup (First Time)
cd /home/easyfix/Documents/PMS/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# Daily Development
source venv/bin/activate
python manage.py runserver

# Run Setup Script (All-in-One)
./setup_database.sh
```

## 📊 Database Commands

```bash
# Activate virtual environment first
source venv/bin/activate

# Check database status
python manage.py check
python test_database.py

# Migrations
python manage.py makemigrations          # Create new migrations
python manage.py migrate                 # Apply migrations
python manage.py showmigrations          # Show migration status
python manage.py migrate app_name zero   # Rollback app migrations

# Database Shell
python manage.py dbshell                 # SQL shell
python manage.py shell                   # Python shell

# Create superuser
python manage.py createsuperuser
```

## 🔧 Development Commands

```bash
# Server
python manage.py runserver               # Start on 8000
python manage.py runserver 8080          # Start on 8080
python manage.py runserver 0.0.0.0:8000  # Listen on all interfaces

# Static Files
python manage.py collectstatic           # Collect static files
python manage.py findstatic filename     # Find static file location

# Cache
python manage.py createcachetable        # Create cache table
python manage.py clear_cache             # Clear cache (if installed)
```

## 🧪 Testing & Quality

```bash
# Testing
pytest                                   # Run all tests
pytest apps/properties/                  # Test specific app
pytest --cov                            # With coverage
pytest -v                               # Verbose output

# Code Quality
black .                                  # Format code
flake8                                   # Check style
isort .                                  # Sort imports
python manage.py check --deploy          # Deployment checks
```

## 📦 Package Management

```bash
# Install packages
pip install package-name
pip install -r requirements.txt

# Update requirements
pip freeze > requirements.txt

# Update packages
pip install --upgrade package-name
pip list --outdated                      # Check outdated packages
```

## 🔍 Inspection Commands

```bash
# Models
python manage.py inspectdb               # Generate models from database
python manage.py sqlmigrate app 0001     # Show SQL for migration

# Shell Commands
python manage.py shell -c "from apps.accounts.models import User; print(User.objects.count())"

# Show URLs
python manage.py show_urls               # Requires django-extensions
```

## 🐛 Debugging

```bash
# Check for problems
python manage.py check
python manage.py check --deploy
python manage.py validate

# Show settings
python manage.py diffsettings            # Show non-default settings

# Database check
python test_database.py
```

## 📁 Project Structure

```
backend/
├── apps/               # Django apps (models, views, etc.)
├── api/v1/            # REST API endpoints
├── config/            # Django settings
├── static/            # Static files (CSS, JS)
├── media/             # User uploads
├── venv/              # Virtual environment
├── db.sqlite3         # Database
├── manage.py          # Django CLI
└── requirements.txt   # Dependencies
```

## 🌐 Important URLs (when server running)

```
http://127.0.0.1:8000/              # Home
http://127.0.0.1:8000/admin/        # Admin panel
http://127.0.0.1:8000/api/v1/       # API base
http://127.0.0.1:8000/swagger/      # API documentation (Swagger)
http://127.0.0.1:8000/redoc/        # API documentation (ReDoc)
```

## 🔐 Environment Variables (.env)

```bash
# Essential variables
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# For PostgreSQL
# DATABASE_ENGINE=django.db.backends.postgresql
# DATABASE_NAME=hotel_pms
# DATABASE_USER=postgres
# DATABASE_PASSWORD=password
# DATABASE_HOST=localhost
# DATABASE_PORT=5432
```

## 🆘 Common Issues & Solutions

### Virtual environment not activated
```bash
# You'll see (venv) in prompt when activated
source venv/bin/activate
```

### Module not found
```bash
pip install -r requirements.txt
```

### Database locked (SQLite)
```bash
# Close all connections and restart server
# Or use PostgreSQL for production
```

### Port already in use
```bash
python manage.py runserver 8080  # Use different port
# Or kill process: lsof -ti:8000 | xargs kill -9
```

### Migrations conflict
```bash
python manage.py migrate --fake app_name zero
python manage.py migrate app_name
```

## 📝 Useful Django Shell Commands

```python
# In Django shell (python manage.py shell)

# Import models
from apps.accounts.models import User
from apps.properties.models import Property

# Query data
User.objects.all()
User.objects.count()
User.objects.filter(is_active=True)
User.objects.get(email='admin@hotel.com')

# Create data
property = Property.objects.create(
    name="Test Hotel",
    code="TEST01",
    address="123 Test St",
    city="Test City",
    country="USA"
)

# Update data
property.name = "New Name"
property.save()

# Delete data
property.delete()
```

## 🔄 Database Backup & Restore

```bash
# SQLite Backup
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# SQLite Restore
cp db.sqlite3.backup.20260107 db.sqlite3

# Export data
python manage.py dumpdata > backup.json
python manage.py dumpdata app_name > app_backup.json

# Import data
python manage.py loaddata backup.json
```

## 🎯 Production Checklist

- [ ] Set DEBUG=False in .env
- [ ] Generate new SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Use PostgreSQL database
- [ ] Configure CORS properly
- [ ] Set up HTTPS/SSL
- [ ] Configure static files serving
- [ ] Set up logging
- [ ] Configure email backend
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Run security checks: `python manage.py check --deploy`

## 📚 Documentation Links

- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- Project Setup: See SETUP.md
