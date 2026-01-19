#!/bin/bash

# Hotel PMS - Development Helper Script
# Quick commands for common development tasks

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Virtual environment not found!${NC}"
    echo "Run: ./setup_database.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Show menu
show_menu() {
    echo ""
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}   Hotel PMS - Development Helper${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo ""
    echo "1) Start server"
    echo "2) Run migrations"
    echo "3) Create superuser"
    echo "4) Open Django shell"
    echo "5) Test database"
    echo "6) Check for errors"
    echo "7) Show database stats"
    echo "8) Create migrations"
    echo "9) Reset database (DANGER!)"
    echo "10) Run tests"
    echo "11) Format code (black)"
    echo "12) Check code style (flake8)"
    echo "13) Create backup"
    echo "14) Show URLs"
    echo "15) Collect static files"
    echo "0) Exit"
    echo ""
    echo -n "Select option: "
}

# Main loop
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1)
            echo -e "${GREEN}Starting development server...${NC}"
            python manage.py runserver
            ;;
        2)
            echo -e "${GREEN}Running migrations...${NC}"
            python manage.py migrate
            echo -e "${GREEN}✓ Done${NC}"
            ;;
        3)
            echo -e "${GREEN}Creating superuser...${NC}"
            python manage.py createsuperuser
            ;;
        4)
            echo -e "${GREEN}Opening Django shell...${NC}"
            python manage.py shell
            ;;
        5)
            echo -e "${GREEN}Testing database...${NC}"
            python test_database.py
            ;;
        6)
            echo -e "${GREEN}Checking for errors...${NC}"
            python manage.py check
            echo -e "${GREEN}✓ No errors found${NC}"
            ;;
        7)
            echo -e "${GREEN}Database statistics:${NC}"
            python manage.py shell -c "
from apps.accounts.models import User
from apps.properties.models import Property
from apps.rooms.models import Room, RoomType
from apps.guests.models import Guest
from apps.reservations.models import Reservation

print('Users:', User.objects.count())
print('Properties:', Property.objects.count())
print('Room Types:', RoomType.objects.count())
print('Rooms:', Room.objects.count())
print('Guests:', Guest.objects.count())
print('Reservations:', Reservation.objects.count())
"
            ;;
        8)
            echo -e "${GREEN}Creating migrations...${NC}"
            python manage.py makemigrations
            echo -e "${GREEN}✓ Done${NC}"
            ;;
        9)
            echo -e "${RED}WARNING: This will delete ALL data!${NC}"
            echo -n "Are you sure? (type 'yes' to confirm): "
            read -r confirm
            if [ "$confirm" = "yes" ]; then
                echo -e "${YELLOW}Backing up database...${NC}"
                cp db.sqlite3 "db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)"
                echo -e "${YELLOW}Resetting database...${NC}"
                rm db.sqlite3
                python manage.py migrate
                echo -e "${GREEN}✓ Database reset complete${NC}"
                echo -e "${YELLOW}Remember to create a new superuser!${NC}"
            else
                echo "Cancelled"
            fi
            ;;
        10)
            echo -e "${GREEN}Running tests...${NC}"
            pytest
            ;;
        11)
            echo -e "${GREEN}Formatting code with black...${NC}"
            black .
            echo -e "${GREEN}✓ Done${NC}"
            ;;
        12)
            echo -e "${GREEN}Checking code style...${NC}"
            flake8
            echo -e "${GREEN}✓ Done${NC}"
            ;;
        13)
            backup_file="db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)"
            echo -e "${GREEN}Creating backup: $backup_file${NC}"
            cp db.sqlite3 "$backup_file"
            echo -e "${GREEN}✓ Backup created${NC}"
            ;;
        14)
            echo -e "${GREEN}Application URLs:${NC}"
            echo "- Admin: http://127.0.0.1:8000/admin/"
            echo "- API: http://127.0.0.1:8000/api/v1/"
            echo "- Swagger: http://127.0.0.1:8000/swagger/"
            echo "- ReDoc: http://127.0.0.1:8000/redoc/"
            ;;
        15)
            echo -e "${GREEN}Collecting static files...${NC}"
            python manage.py collectstatic --no-input
            echo -e "${GREEN}✓ Done${NC}"
            ;;
        0)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    
    echo ""
    echo -n "Press Enter to continue..."
    read -r
done
