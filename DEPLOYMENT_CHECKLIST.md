# Production Deployment Checklist

## ✅ Completed Security Fixes

### 1. SECRET_KEY
- ✅ Generated secure 50+ character random key
- ✅ Stored in .env file
- ⚠️ **ACTION REQUIRED**: Generate new SECRET_KEY for production server

### 2. ALLOWED_HOSTS
- ✅ Restricted to localhost,127.0.0.1 in development
- ⚠️ **ACTION REQUIRED**: Update ALLOWED_HOSTS in production .env with actual domain names

### 3. Production Security Settings (config/settings/production.py)
- ✅ DEBUG=False enforced
- ✅ SECURE_BROWSER_XSS_FILTER=True
- ✅ SECURE_CONTENT_TYPE_NOSNIFF=True
- ✅ X_FRAME_OPTIONS='DENY'
- ✅ CSRF_COOKIE_SECURE=True
- ✅ SESSION_COOKIE_SECURE=True
- ✅ SECURE_HSTS_SECONDS=31536000 (1 year)
- ✅ SECURE_HSTS_INCLUDE_SUBDOMAINS=True
- ✅ SECURE_HSTS_PRELOAD=True
- ✅ SECURE_SSL_REDIRECT=True
- ✅ SESSION_COOKIE_HTTPONLY=True
- ✅ CSRF_COOKIE_HTTPONLY=True
- ✅ SECURE_REFERRER_POLICY='same-origin'
- ✅ SECURE_PROXY_SSL_HEADER configured for HTTPS behind proxy

### 4. API Rate Limiting
- ✅ DRF throttling enabled
- ✅ Anonymous users: 100 requests/hour
- ✅ Authenticated users: 1000 requests/hour
- ℹ️ Adjust rates in base.py if needed

### 5. Error Monitoring & Logging
- ✅ Comprehensive logging configuration
- ✅ Rotating file handlers (10MB max, 5 backups)
- ✅ Separate error log file
- ✅ Console and file logging
- ✅ Sentry integration ready (requires SENTRY_DSN env var)

## 📋 Pre-Production Steps

### Environment Variables (.env for production)
```bash
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-new-secure-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=hotel_pms_prod
DATABASE_USER=pms_user
DATABASE_PASSWORD=<secure-password>
DATABASE_HOST=localhost
DATABASE_PORT=5432

# CORS
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password>

# Sentry (optional but recommended)
SENTRY_DSN=https://your-sentry-dsn
ENVIRONMENT=production
```

### Database Migration
```bash
# Backup existing database
python manage.py dumpdata > backup.json

# Switch to PostgreSQL
# Update .env with PostgreSQL credentials
python manage.py migrate

# Load data if needed
python manage.py loaddata backup.json
```

### Static Files
```bash
python manage.py collectstatic --noinput
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### SSL Certificate
- Configure HTTPS/SSL certificate (Let's Encrypt recommended)
- Update nginx/apache configuration

### Server Configuration
- Configure gunicorn/uwsgi for WSGI
- Setup nginx/apache as reverse proxy
- Configure systemd service for auto-start
- Setup backup cron jobs

## 🔐 Security Checklist

- [ ] Generate new SECRET_KEY for production
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS with actual domains
- [ ] Setup HTTPS/SSL certificate
- [ ] Configure firewall rules
- [ ] Setup database backups
- [ ] Configure email backend
- [ ] Setup Sentry or error monitoring
- [ ] Review user permissions
- [ ] Enable CORS only for trusted origins
- [ ] Test rate limiting
- [ ] Review log retention policies
- [ ] Setup monitoring/alerting
- [ ] Document admin credentials securely
- [ ] Setup regular security audits

## 📊 Monitoring

### Logs Location
- Django logs: `backend/logs/django.log`
- Error logs: `backend/logs/errors.log`

### Monitoring Endpoints
- Health check: `/api/v1/health/` (if implemented)
- Admin panel: `/admin/`
- API docs: `/swagger/` or `/redoc/`

## 🚀 Deployment Commands

### Development Server
```bash
python manage.py runserver
```

### Production Server (Gunicorn)
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## 📝 Notes

- Development mode warnings (5) are expected and normal
- Production mode has all security warnings resolved
- Rate limiting is configured and active
- Logging system captures all errors and warnings
- Sentry integration ready (optional, requires DSN)
