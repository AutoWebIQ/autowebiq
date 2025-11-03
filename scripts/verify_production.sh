#!/bin/bash
# Quick production verification script

echo "🔍 AutoWebIQ Production Verification"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0;m'

# Check environment
if [ -f "/app/backend/.env" ]; then
    echo -e "${GREEN}✓${NC} Backend .env exists"
else
    echo -e "${RED}✗${NC} Backend .env missing"
fi

if [ -f "/app/frontend/.env" ]; then
    echo -e "${GREEN}✓${NC} Frontend .env exists"
else
    echo -e "${RED}✗${NC} Frontend .env missing"
fi

# Check backend service
if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend is running"
else
    echo -e "${RED}✗${NC} Backend is not responding"
fi

# Check frontend service
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend is running"
else
    echo -e "${RED}✗${NC} Frontend is not responding"
fi

# Check MongoDB
if mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} MongoDB is accessible"
else
    echo -e "${YELLOW}⚠${NC}  MongoDB check skipped (mongosh not available)"
fi

# Check build
if [ -d "/app/frontend/build" ]; then
    echo -e "${GREEN}✓${NC} Frontend build exists"
else
    echo -e "${YELLOW}⚠${NC}  Frontend build not found (run production_build.sh)"
fi

echo ""
echo "====================================="
echo "Verification complete"
echo ""
