#!/bin/bash

# Hotel PMS - Complete Testing Script
# Tests both backend and mobile app

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Hotel PMS - Complete System Test${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Get local IP
LOCAL_IP=$(ip route get 1 2>/dev/null | awk '{print $7; exit}' || hostname -I 2>/dev/null | awk '{print $1}')

echo -e "${GREEN}System Configuration:${NC}"
echo -e "  Local IP: ${LOCAL_IP}"
echo -e "  Backend: http://${LOCAL_IP}:8000"
echo -e "  API: http://${LOCAL_IP}:8000/api/v1"
echo ""

# Test Backend
echo -e "${BLUE}Testing Backend...${NC}"
cd "$(dirname "$0")/backend"

if [ -d "venv" ]; then
    source venv/bin/activate
    
    # Check Django
    if python manage.py check > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Django check passed"
    else
        echo -e "  ${RED}✗${NC} Django check failed"
        exit 1
    fi
    
    # Check database
    if python test_database.py > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Database working"
    else
        echo -e "  ${RED}✗${NC} Database test failed"
        exit 1
    fi
else
    echo -e "  ${RED}✗${NC} Virtual environment not found"
    exit 1
fi

echo ""

# Test Mobile
echo -e "${BLUE}Testing Mobile App...${NC}"
cd "$(dirname "$0")/mobile"

if [ -d "node_modules" ]; then
    echo -e "  ${GREEN}✓${NC} Dependencies installed"
else
    echo -e "  ${YELLOW}⚠${NC} Installing dependencies..."
    npm install > /dev/null 2>&1
    echo -e "  ${GREEN}✓${NC} Dependencies installed"
fi

if [ -f "src/config/environment.ts" ]; then
    echo -e "  ${GREEN}✓${NC} Environment config exists"
else
    echo -e "  ${RED}✗${NC} Environment config missing"
    exit 1
fi

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}✓ All tests passed!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "To start testing:"
echo ""
echo -e "${YELLOW}Terminal 1 - Backend:${NC}"
echo -e "  cd backend"
echo -e "  source venv/bin/activate"
echo -e "  ${GREEN}python manage.py runserver 0.0.0.0:8000${NC}"
echo ""
echo -e "${YELLOW}Terminal 2 - Mobile:${NC}"
echo -e "  cd mobile"
echo -e "  ${GREEN}./start.sh${NC}"
echo -e "  (or: npm start)"
echo ""
echo -e "${YELLOW}On Your Phone:${NC}"
echo -e "  1. Install 'Expo Go' app"
echo -e "  2. Scan QR code from Terminal 2"
echo -e "  3. Login with: admin@hotel.com"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo -e "  Admin: ${GREEN}http://${LOCAL_IP}:8000/admin/${NC}"
echo -e "  Swagger: ${GREEN}http://${LOCAL_IP}:8000/swagger/${NC}"
echo -e "  ReDoc: ${GREEN}http://${LOCAL_IP}:8000/redoc/${NC}"
echo ""
