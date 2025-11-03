#!/bin/bash
# AutoWebIQ Production Build & Deploy Script
# Domain: autowebiq.com

set -e

echo "🚀 AutoWebIQ Production Build Started"
echo "========================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0;0m' # No Color

# Step 1: Environment Check
echo -e "${YELLOW}Step 1: Checking environment...${NC}"
if [ ! -f "/app/.env.production" ]; then
    echo -e "${RED}Error: .env.production not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Environment files found${NC}"

# Step 2: Copy production environment files
echo -e "${YELLOW}Step 2: Copying production environment files...${NC}"
cp /app/.env.production /app/backend/.env
cp /app/frontend/.env.production /app/frontend/.env
echo -e "${GREEN}✓ Environment files copied${NC}"

# Step 3: Install backend dependencies
echo -e "${YELLOW}Step 3: Installing backend dependencies...${NC}"
cd /app/backend
pip install --upgrade pip
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Step 4: Install frontend dependencies
echo -e "${YELLOW}Step 4: Installing frontend dependencies...${NC}"
cd /app/frontend
yarn install --silent
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Step 5: Build frontend for production
echo -e "${YELLOW}Step 5: Building frontend (this may take a few minutes)...${NC}"
REACT_APP_BACKEND_URL=https://api.autowebiq.com yarn build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend build successful${NC}"
else
    echo -e "${RED}✗ Frontend build failed${NC}"
    exit 1
fi

# Step 6: Test backend health
echo -e "${YELLOW}Step 6: Testing backend configuration...${NC}"
cd /app/backend
python -c "import server; print('Backend imports OK')"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend configuration valid${NC}"
else
    echo -e "${RED}✗ Backend configuration error${NC}"
    exit 1
fi

# Step 7: Database connectivity check
echo -e "${YELLOW}Step 7: Checking database connectivity...${NC}"
python -c "from database import db; import asyncio; asyncio.run(db.command('ping')); print('MongoDB OK')"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database connection OK${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Could not verify database connection${NC}"
fi

# Step 8: Restart services
echo -e "${YELLOW}Step 8: Restarting services...${NC}"
sudo supervisorctl restart all
sleep 5

# Step 9: Health check
echo -e "${YELLOW}Step 9: Performing health checks...${NC}"
sleep 3

# Check backend
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health 2>/dev/null || echo "000")
if [ "$BACKEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${YELLOW}⚠ Backend health check returned: $BACKEND_STATUS${NC}"
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Frontend health check passed${NC}"
else
    echo -e "${YELLOW}⚠ Frontend health check returned: $FRONTEND_STATUS${NC}"
fi

# Summary
echo ""
echo "========================================"
echo -e "${GREEN}🎉 Production Build Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Configure your domain (autowebiq.com) to point to this server"
echo "2. Set up Nginx reverse proxy (see PRODUCTION_DEPLOYMENT_GUIDE.md)"
echo "3. Configure SSL certificates with Let's Encrypt"
echo "4. Test the live site at https://autowebiq.com"
echo ""
echo "Documentation: /app/PRODUCTION_DEPLOYMENT_GUIDE.md"
echo ""
