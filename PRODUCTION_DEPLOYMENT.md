# ============================================
# PMS Production Deployment - Complete Guide
# ============================================

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Docker)](#quick-start-docker)
3. [Manual Deployment](#manual-deployment)
4. [Configuration](#configuration)
5. [Security](#security)
6. [Monitoring](#monitoring)
7. [Backup & Restore](#backup--restore)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Docker & Docker Compose (recommended) OR
- Python 3.11+, PostgreSQL 16+, Redis 7+, Nginx
- Git (optional, for updates)

### Required Services
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)
- Email service (Gmail, SendGrid, etc.)
- Server with minimum specs:
  - 2 CPU cores
  - 4GB RAM
  - 20GB disk space

---

## Quick Start (Docker)

### 1. Clone Repository
```bash
cd /opt
git clone <repository-url> pms
cd pms
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.production.example .env

# Edit configuration (see Configuration section)
nano .env
```

### 3. Deploy
```bash
# Using deployment script
./scripts/deploy.sh

# OR using Makefile
make deploy

# OR manually
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --noinput
```

### 4. Access Application
- Backend API: `http://your-domain/api/`
- Admin Panel: `http://your-domain/admin/`
- API Docs: `http://your-domain/swagger/`
- Web App: `http://your-domain/`

---

## Manual Deployment

### 1. System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql-16 postgresql-contrib \
    redis-server nginx git

# Create user
sudo useradd -m -s /bin/bash pmsuser
sudo usermod -aG www-data pmsuser
```

### 2. Database Setup
```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE pms_production;
CREATE USER pms_user WITH PASSWORD 'your_secure_password';
ALTER ROLE pms_user SET client_encoding TO 'utf8';
ALTER ROLE pms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pms_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pms_production TO pms_user;
\q
```

### 3. Application Setup
```bash
# Clone repository
sudo mkdir -p /opt/pms
sudo chown pmsuser:www-data /opt/pms
sudo -u pmsuser git clone <repository-url> /opt/pms
cd /opt/pms/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.production.txt

# Configure environment
cp ../.env.production.example .env
nano .env  # Edit configuration

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Create directories
mkdir -p logs media staticfiles
sudo chown -R pmsuser:www-data logs media staticfiles
```

### 4. Configure Nginx
```bash
# Copy nginx configuration
sudo cp /opt/pms/nginx/conf.d/pms.conf /etc/nginx/sites-available/pms
sudo ln -s /etc/nginx/sites-available/pms /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 5. Configure Systemd Services
```bash
# Copy service files
sudo cp /opt/pms/systemd/*.service /etc/systemd/system/

# Create runtime directory
sudo mkdir -p /run/pms
sudo chown pmsuser:www-data /run/pms

# Create log directory
sudo mkdir -p /var/log/pms
sudo chown pmsuser:www-data /var/log/pms

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable pms-backend pms-celery pms-celery-beat
sudo systemctl start pms-backend pms-celery pms-celery-beat

# Check status
sudo systemctl status pms-backend
```

---

## Configuration

### Environment Variables (.env)

**Critical Settings:**
```env
# Django
SECRET_KEY=<generate-50-char-random-string>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=pms_production
DB_USER=pms_user
DB_PASSWORD=<your-secure-password>
DB_HOST=db  # For Docker, or localhost for manual
DB_PORT=5432

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Generate SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Security

### SSL/HTTPS Setup (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal:
sudo certbot renew --dry-run
```

### Firewall Setup
```bash
# Using UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Check status
sudo ufw status
```

### Security Checklist
- [ ] Change all default passwords
- [ ] Configure SECRET_KEY (unique per instance)
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Set up firewall
- [ ] Regular security updates
- [ ] Configure fail2ban (optional)

---

## Monitoring

### Health Checks
```bash
# Run manual health check
./scripts/health-check.sh

# Set up cron job for automated checks
crontab -e
# Add: */5 * * * * /opt/pms/scripts/health-check.sh
```

### Metrics Collection
```bash
# Run monitoring script
./scripts/monitor.sh

# Set up cron for continuous monitoring
# Add to crontab: * * * * * /opt/pms/scripts/monitor.sh
```

### Log Management
```bash
# View logs (Docker)
make logs-backend
make logs-db

# View logs (Manual)
sudo tail -f /var/log/pms/*.log
sudo journalctl -u pms-backend -f

# Rotate logs
sudo nano /etc/logrotate.d/pms
```

**Log rotation config:**
```
/var/log/pms/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 pmsuser www-data
    sharedscripts
    postrotate
        systemctl reload pms-backend
    endscript
}
```

---

## Backup & Restore

### Automated Backups
```bash
# Run backup
./scripts/backup.sh

# Set up automated daily backups (2 AM)
crontab -e
# Add: 0 2 * * * /opt/pms/scripts/backup.sh
```

### Manual Backup
```bash
# Database (Docker)
docker-compose exec db pg_dump -U pms_user pms_production | gzip > backup.sql.gz

# Database (Manual)
pg_dump -U pms_user -h localhost pms_production | gzip > backup.sql.gz

# Media files
tar -czf media_backup.tar.gz backend/media/
```

### Restore
```bash
# Database (Docker)
gunzip -c backup.sql.gz | docker-compose exec -T db psql -U pms_user pms_production

# Database (Manual)
gunzip -c backup.sql.gz | psql -U pms_user -h localhost pms_production

# Media files
tar -xzf media_backup.tar.gz -C backend/
```

---

## Troubleshooting

### Common Issues

**1. Services won't start**
```bash
# Check logs
docker-compose logs backend
sudo journalctl -u pms-backend -n 50

# Check configuration
python manage.py check --deploy
```

**2. Database connection errors**
```bash
# Verify database is running
docker-compose ps db
systemctl status postgresql

# Test connection
psql -U pms_user -h localhost -d pms_production
```

**3. Static files not loading**
```bash
# Recollect static files
python manage.py collectstatic --noinput --clear

# Check nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

**4. Permission errors**
```bash
# Fix ownership
sudo chown -R pmsuser:www-data /opt/pms/backend/media
sudo chown -R pmsuser:www-data /opt/pms/backend/logs
sudo chmod -R 755 /opt/pms/backend/media
```

### Performance Issues

**High CPU usage:**
- Increase number of workers
- Enable Redis caching
- Optimize database queries
- Check for slow queries in logs

**High memory usage:**
- Reduce number of workers
- Enable swap if needed
- Check for memory leaks

**Slow response times:**
- Enable Redis caching
- Optimize database indexes
- Enable CDN for static files
- Check network latency

---

## Useful Commands

### Docker Commands
```bash
make build          # Build images
make up             # Start services
make down           # Stop services
make restart        # Restart services
make logs           # View logs
make shell          # Django shell
make migrate        # Run migrations
make backup         # Backup database
make ps             # Show status
```

### Manual Deployment Commands
```bash
# Restart services
sudo systemctl restart pms-backend pms-celery

# View logs
sudo journalctl -u pms-backend -f

# Run management commands
cd /opt/pms/backend
source venv/bin/activate
python manage.py <command>
```

---

## Support

### Getting Help
- Check logs first: `make logs` or `/var/log/pms/`
- Run health checks: `./scripts/health-check.sh`
- Check system status: `make ps` or `systemctl status pms-*`
- Review documentation: `/opt/pms/backend/SETUP.md`

### Maintenance Windows
- Recommended: Sunday 2-4 AM
- Backup before updates
- Test in staging first
- Monitor for 30 minutes after updates

---

## License

[Your License Here]

## Version

1.0.0 - February 2026
