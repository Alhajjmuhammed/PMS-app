#!/bin/bash

# ============================================
# PMS Deployment Verification Script
# ============================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_ok() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

echo "================================"
echo "PMS Deployment Verification"
echo "================================"
echo ""

# Check required files
echo "Checking required files..."

required_files=(
    "docker-compose.yml"
    "backend/Dockerfile"
    "backend/requirements.txt"
    "backend/manage.py"
    "nginx/nginx.conf"
    "scripts/deploy.sh"
    "scripts/backup.sh"
    "scripts/health-check.sh"
    ".env.production.example"
    "Makefile"
)

missing_files=0
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        log_ok "Found: $file"
    else
        log_error "Missing: $file"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    log_error "$missing_files required files are missing!"
    exit 1
fi

echo ""
echo "Checking directory structure..."

required_dirs=(
    "backend"
    "web"
    "mobile"
    "nginx"
    "scripts"
    "systemd"
    ".github/workflows"
)

missing_dirs=0
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        log_ok "Found: $dir/"
    else
        log_warn "Missing: $dir/"
        missing_dirs=$((missing_dirs + 1))
    fi
done

echo ""
echo "Checking script permissions..."

scripts=(
    "scripts/deploy.sh"
    "scripts/backup.sh"
    "scripts/health-check.sh"
    "scripts/monitor.sh"
)

for script in "${scripts[@]}"; do
    if [ -x "$script" ]; then
        log_ok "Executable: $script"
    else
        log_warn "Not executable: $script (run: chmod +x $script)"
    fi
done

echo ""
echo "Checking configuration..."

if [ -f ".env" ]; then
    log_ok ".env file exists"
    
    # Check critical env vars
    if grep -q "SECRET_KEY=your_secret_key" .env; then
        log_warn "SECRET_KEY not configured (still default value)"
    else
        log_ok "SECRET_KEY appears to be configured"
    fi
    
    if grep -q "DEBUG=False" .env; then
        log_ok "DEBUG=False (production mode)"
    else
        log_warn "DEBUG is not False"
    fi
else
    log_warn ".env file not found (copy from .env.production.example)"
fi

echo ""
echo "Checking dependencies..."

# Check Docker
if command -v docker &> /dev/null; then
    log_ok "Docker is installed ($(docker --version | cut -d' ' -f3))"
    
    if docker ps &> /dev/null; then
        log_ok "Docker daemon is running"
    else
        log_warn "Docker daemon is not running"
    fi
else
    log_warn "Docker is not installed"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    log_ok "Docker Compose is installed ($(docker-compose --version | cut -d' ' -f4))"
else
    log_warn "Docker Compose is not installed"
fi

# Check Python
if command -v python3 &> /dev/null; then
    log_ok "Python is installed ($(python3 --version | cut -d' ' -f2))"
else
    log_warn "Python 3 is not installed"
fi

# Check Node.js
if command -v node &> /dev/null; then
    log_ok "Node.js is installed ($(node --version))"
else
    log_warn "Node.js is not installed"
fi

echo ""
echo "Deployment Infrastructure Status:"
echo "================================"

deployment_files=(
    "Docker:docker-compose.yml"
    "Backend Image:backend/Dockerfile"
    "Nginx Config:nginx/nginx.conf"
    "Deploy Script:scripts/deploy.sh"
    "Backup Script:scripts/backup.sh"
    "Health Check:scripts/health-check.sh"
    "CI/CD:.github/workflows/ci-cd.yml"
    "Systemd Service:systemd/pms-backend.service"
    "Makefile:Makefile"
    "Documentation:PRODUCTION_DEPLOYMENT.md"
)

for item in "${deployment_files[@]}"; do
    name="${item%%:*}"
    file="${item##*:}"
    if [ -f "$file" ]; then
        log_ok "$name"
    else
        log_error "$name - Missing: $file"
    fi
done

echo ""
echo "================================"
echo "Verification Summary"
echo "================================"

if [ $missing_files -eq 0 ]; then
    log_ok "All required files present"
else
    log_error "$missing_files required files missing"
fi

if [ -f ".env" ]; then
    log_ok "Environment configuration ready"
else
    log_warn "Environment needs configuration"
fi

if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    log_ok "Docker deployment ready"
else
    log_warn "Docker not available (manual deployment required)"
fi

echo ""
echo "Next steps:"
echo "1. Configure .env file (copy from .env.production.example)"
echo "2. Generate SECRET_KEY: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
echo "3. Update ALLOWED_HOSTS with your domain"
echo "4. Run deployment: ./scripts/deploy.sh or make deploy"
echo "5. Create superuser: docker-compose exec backend python manage.py createsuperuser"
echo "6. Access admin: http://your-domain/admin"
echo ""
echo "For full instructions, see: PRODUCTION_DEPLOYMENT.md"
echo ""
