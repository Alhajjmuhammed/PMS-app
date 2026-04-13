#!/bin/bash

# ============================================
# PMS Deployment Script
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    log_error ".env file not found!"
    log_info "Copy .env.production.example to .env and configure it"
    exit 1
fi

log_info "Starting deployment..."

# Pull latest changes (if using git)
if [ -d ".git" ]; then
    log_info "Pulling latest changes from git..."
    git pull origin main || log_warn "Git pull failed or not configured"
fi

# Build and start services
log_info "Building Docker images..."
docker-compose build --no-cache

log_info "Starting services..."
docker-compose up -d

# Wait for database
log_info "Waiting for database to be ready..."
sleep 10

# Run migrations
log_info "Running database migrations..."
docker-compose exec -T backend python manage.py migrate --noinput

# Collect static files
log_info "Collecting static files..."
docker-compose exec -T backend python manage.py collectstatic --noinput --clear

# Create superuser (only if needed)
log_info "Checking for superuser..."
docker-compose exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one manually with: docker-compose exec backend python manage.py createsuperuser')
" || true

# Check deployment
log_info "Running Django deployment checks..."
docker-compose exec -T backend python manage.py check --deploy || log_warn "Deployment checks have warnings"

# Show running services
log_info "Deployment complete! Services status:"
docker-compose ps

log_info "
Deployment successful! 🎉

Access points:
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- API Docs: http://localhost:8000/swagger
- Web App: http://localhost

Next steps:
1. Create a superuser: docker-compose exec backend python manage.py createsuperuser
2. Configure your domain in .env (ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS)
3. Set up SSL certificate for HTTPS
4. Configure monitoring and backups
"
