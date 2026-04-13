# Production Deployment Guide

## Overview
This guide covers deploying the PMS system to a production environment with PostgreSQL, proper security, and scalability.

## Prerequisites
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+
- Nginx
- SSL certificate (Let's Encrypt recommended)
- Domain name

## 1. Database Setup

### Install PostgreSQL
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### Create Database and User
```bash
sudo -u postgres psql

CREATE DATABASE pms_production;
CREATE USER pms_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE pms_user SET client_encoding TO 'utf8';
ALTER ROLE pms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pms_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pms_production TO pms_user;
\q
```

### Backup Existing Data (if migrating from SQLite)
```bash
cd /path/to/PMS/backend

# Export data from SQLite
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 \
  -e contenttypes -e auth.Permission -e sessions -e admin.logentry \
  > data_export.json

# Load into PostgreSQL (after configuring DATABASE_URL)
python manage.py migrate
python manage.py loaddata data_export.json
```

## 2. Backend Deployment

### Clone Repository
```bash
cd /var/www
sudo git clone <your-repo-url> pms
sudo chown -R $USER:$USER pms
cd pms/backend
```

### Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Configure Environment Variables
```bash
sudo nano /var/www/pms/backend/.env.production
```

Add the following:
```env
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your_very_long_secret_key_here_generate_with_django
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://pms_user:your_secure_password_here@localhost:5432/pms_production

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (SMTP)
EMAIL_ENABLED=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Or SendGrid
# EMAIL_HOST=smtp.sendgrid.net
# EMAIL_HOST_USER=apikey
# EMAIL_HOST_PASSWORD=your_sendgrid_api_key

# Push Notifications (Firebase)
FCM_ENABLED=True
FCM_SERVER_KEY=your_firebase_server_key

# SMS (Twilio - Optional)
SMS_ENABLED=False
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Run Migrations
```bash
source venv/bin/activate
export $(cat .env.production | xargs)
python manage.py migrate
python manage.py collectstatic --noinput
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Test Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
# Press Ctrl+C after verifying it works
```

### Create Systemd Service
```bash
sudo nano /etc/systemd/system/pms-backend.service
```

Add:
```ini
[Unit]
Description=PMS Backend (Gunicorn)
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/pms/backend
Environment="PATH=/var/www/pms/backend/venv/bin"
EnvironmentFile=/var/www/pms/backend/.env.production
ExecStart=/var/www/pms/backend/venv/bin/gunicorn \
          --workers 4 \
          --bind unix:/var/www/pms/backend/gunicorn.sock \
          --access-logfile /var/log/pms/access.log \
          --error-logfile /var/log/pms/error.log \
          --log-level info \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Create log directory:
```bash
sudo mkdir -p /var/log/pms
sudo chown www-data:www-data /var/log/pms
sudo chown -R www-data:www-data /var/www/pms
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pms-backend
sudo systemctl start pms-backend
sudo systemctl status pms-backend
```

## 3. Frontend Deployment

### Build Next.js Application
```bash
cd /var/www/pms/web
npm install
npm run build
```

### Configure Environment
```bash
nano .env.production
```

Add:
```env
NEXT_PUBLIC_API_URL=https://yourdomain.com/api/v1
NODE_ENV=production
```

### Create Systemd Service
```bash
sudo nano /etc/systemd/system/pms-frontend.service
```

Add:
```ini
[Unit]
Description=PMS Frontend (Next.js)
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/pms/web
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable pms-frontend
sudo systemctl start pms-frontend
sudo systemctl status pms-frontend
```

## 4. Nginx Configuration

### Install Nginx
```bash
sudo apt install nginx
```

### Configure Site
```bash
sudo nano /etc/nginx/sites-available/pms
```

Add:
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://unix:/var/www/pms/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (Django admin, DRF)
    location /static/ {
        alias /var/www/pms/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/pms/backend/media/;
        expires 30d;
    }

    # Max upload size
    client_max_body_size 20M;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/pms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Setup SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 5. Monitoring & Maintenance

### Setup Log Rotation
```bash
sudo nano /etc/logrotate.d/pms
```

Add:
```
/var/log/pms/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload pms-backend > /dev/null
    endscript
}
```

### Database Backups
```bash
sudo nano /usr/local/bin/backup-pms-db.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/pms"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U pms_user pms_production | gzip > $BACKUP_DIR/pms_backup_$DATE.sql.gz
# Keep last 30 days
find $BACKUP_DIR -name "pms_backup_*.sql.gz" -mtime +30 -delete
```

Make executable and add to crontab:
```bash
sudo chmod +x /usr/local/bin/backup-pms-db.sh
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-pms-db.sh
```

### Monitoring Commands
```bash
# Check service status
sudo systemctl status pms-backend
sudo systemctl status pms-frontend
sudo systemctl status nginx

# View logs
sudo journalctl -u pms-backend -f
sudo journalctl -u pms-frontend -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/pms/error.log

# Database status
sudo -u postgres psql -c "\l"
sudo -u postgres psql -d pms_production -c "SELECT count(*) FROM reservations_reservation;"
```

## 6. Performance Optimization

### Redis for Caching (Optional)
```bash
sudo apt install redis-server
pip install redis django-redis
```

Add to settings:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### Celery for Background Tasks (Optional)
```bash
pip install celery
```

Create celery service for async tasks (night audit, email sending, etc.)

## 7. Security Checklist

- [ ] Change all default passwords
- [ ] Enable firewall (ufw)
- [ ] Configure fail2ban
- [ ] Regular security updates
- [ ] Backup verification
- [ ] SSL certificate auto-renewal
- [ ] Monitor access logs
- [ ] Implement rate limiting
- [ ] Setup intrusion detection

## 8. Troubleshooting

### Backend not starting
```bash
sudo systemctl status pms-backend
sudo journalctl -u pms-backend -n 50
# Check database connection
sudo -u postgres psql -d pms_production -c "SELECT 1;"
```

### Frontend build errors
```bash
cd /var/www/pms/web
npm run build
# Check environment variables
```

### 502 Bad Gateway
```bash
# Check gunicorn socket
ls -l /var/www/pms/backend/gunicorn.sock
# Check nginx error log
sudo tail -f /var/log/nginx/error.log
```

## Support
For issues, consult the logs and check the deployment checklist in DEPLOYMENT_CHECKLIST.md
