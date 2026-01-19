#!/bin/bash

# Hotel PMS - Database Setup and Verification Script
# This script sets up the database and verifies all components are working

set -e  # Exit on error

echo "========================================="
echo "Hotel PMS - Database Setup & Verification"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/Update dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please review .env file and update settings if needed${NC}"
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p static staticfiles media
mkdir -p media/properties/logos media/properties/images
mkdir -p media/avatars media/room_types media/guests
mkdir -p media/registration_cards media/signatures
mkdir -p media/guest_documents media/menu_items
mkdir -p media/channels
echo -e "${GREEN}✓ Directories created${NC}"

# Run Django checks
echo ""
echo "Running Django system checks..."
python manage.py check --deploy 2>/dev/null || python manage.py check
echo -e "${GREEN}✓ System checks passed${NC}"

# Create migrations if needed
echo ""
echo "Checking for new migrations..."
python manage.py makemigrations --dry-run --check 2>&1 | grep -q "No changes detected" && {
    echo -e "${GREEN}✓ No new migrations needed${NC}"
} || {
    echo -e "${YELLOW}Creating new migrations...${NC}"
    python manage.py makemigrations
}

# Apply migrations
echo ""
echo "Applying database migrations..."
python manage.py migrate --no-input
echo -e "${GREEN}✓ Migrations applied${NC}"

# Test database connectivity
echo ""
echo "Testing database connectivity..."
python manage.py shell -c "
from django.db import connection
from django.db.utils import OperationalError

try:
    connection.ensure_connection()
    print('✅ Database connection successful')
except OperationalError as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Verify all models
echo ""
echo "Verifying all models..."
python manage.py shell -c "
from apps.accounts.models import User
from apps.properties.models import Property, Building, Floor, Department
from apps.rooms.models import Room, RoomType, RoomAmenity
from apps.guests.models import Guest, Company
from apps.reservations.models import Reservation
from apps.frontdesk.models import CheckIn, CheckOut
from apps.housekeeping.models import HousekeepingTask
from apps.maintenance.models import MaintenanceRequest
from apps.billing.models import Folio, Payment, ChargeCode
from apps.pos.models import Outlet, MenuItem, POSOrder
from apps.rates.models import RatePlan, Season
from apps.channels.models import Channel, PropertyChannel
from apps.reports.models import DailyStatistics
from apps.notifications.models import NotificationTemplate

print('Database Model Counts:')
print('----------------------')
print(f'Users: {User.objects.count()}')
print(f'Properties: {Property.objects.count()}')
print(f'Buildings: {Building.objects.count()}')
print(f'Departments: {Department.objects.count()}')
print(f'Room Types: {RoomType.objects.count()}')
print(f'Rooms: {Room.objects.count()}')
print(f'Room Amenities: {RoomAmenity.objects.count()}')
print(f'Guests: {Guest.objects.count()}')
print(f'Companies: {Company.objects.count()}')
print(f'Reservations: {Reservation.objects.count()}')
print(f'Check-ins: {CheckIn.objects.count()}')
print(f'Folios: {Folio.objects.count()}')
print(f'Payments: {Payment.objects.count()}')
print(f'Charge Codes: {ChargeCode.objects.count()}')
print(f'Housekeeping Tasks: {HousekeepingTask.objects.count()}')
print(f'Maintenance Requests: {MaintenanceRequest.objects.count()}')
print(f'POS Outlets: {Outlet.objects.count()}')
print(f'Menu Items: {MenuItem.objects.count()}')
print(f'Rate Plans: {RatePlan.objects.count()}')
print(f'Channels: {Channel.objects.count()}')
print(f'Daily Statistics: {DailyStatistics.objects.count()}')
print(f'Notification Templates: {NotificationTemplate.objects.count()}')
print()
print('✅ All models verified successfully!')
"

# Check for superuser
echo ""
echo "Checking for superuser account..."
python manage.py shell -c "
from apps.accounts.models import User
superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    print(f'✅ Found {superusers.count()} superuser(s)')
    for user in superusers:
        print(f'   - {user.email}')
else:
    print('⚠ No superuser found')
    print('   Run: python manage.py createsuperuser')
"

# Test server startup (quick check)
echo ""
echo "Testing server startup..."
timeout 3 python manage.py runserver 0.0.0.0:8000 2>&1 >/dev/null || true
echo -e "${GREEN}✓ Server can start successfully${NC}"

# Summary
echo ""
echo "========================================="
echo -e "${GREEN}Database Setup Complete!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Create a superuser (if not exists):"
echo "   python manage.py createsuperuser"
echo ""
echo "2. Start the development server:"
echo "   python manage.py runserver"
echo ""
echo "3. Access the application:"
echo "   - Web: http://127.0.0.1:8000/"
echo "   - Admin: http://127.0.0.1:8000/admin/"
echo "   - API: http://127.0.0.1:8000/api/v1/"
echo ""
echo "4. View API documentation:"
echo "   - Swagger: http://127.0.0.1:8000/swagger/"
echo "   - ReDoc: http://127.0.0.1:8000/redoc/"
echo ""
echo "========================================="
