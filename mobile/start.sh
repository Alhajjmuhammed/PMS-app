#!/bin/bash

# Hotel PMS - Mobile App Quick Start Script

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}  Hotel PMS Mobile - Quick Start${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Get local IP
LOCAL_IP=$(ip route get 1 2>/dev/null | awk '{print $7; exit}' || hostname -I 2>/dev/null | awk '{print $1}')

echo ""
echo -e "${GREEN}Mobile App Configuration:${NC}"
echo -e "  API URL: http://${LOCAL_IP}:8000/api/v1"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC} Make sure backend is running on:"
echo -e "  ${GREEN}python manage.py runserver 0.0.0.0:8000${NC}"
echo ""
echo -e "${BLUE}Starting Expo development server...${NC}"
echo ""
echo -e "Instructions:"
echo -e "  1. Install 'Expo Go' app on your phone"
echo -e "  2. Scan the QR code that appears"
echo -e "  3. App will load on your device"
echo ""
echo -e "  Login credentials:"
echo -e "  - Email: admin@hotel.com"
echo -e "  - Password: (your admin password)"
echo ""
echo -e "${BLUE}=======================================${NC}"
echo ""

# Start Expo
npm start
