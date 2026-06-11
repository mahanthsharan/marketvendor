#!/bin/bash
# Setup script to initialize the marketplace system
# Run: bash setup.sh

set -e

echo "=================================="
echo "Marketplace System Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found${NC}"
    exit 1
fi
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js not found${NC}"
    exit 1
fi
echo -e "${GREEN}Prerequisites OK${NC}"
echo ""

# Backend setup
echo -e "${BLUE}Setting up backend...${NC}"
cd marketplace-backend

if [ ! -f .env ]; then
    echo "Creating .env from .env.example"
    cp .env.example .env
    echo -e "${BLUE}⚠ Edit .env with your database & Stripe credentials${NC}"
fi

if [ ! -d venv ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Initializing database..."
python init_db.py

echo -e "${GREEN}Backend setup complete!${NC}"
echo ""

# Seller Portal setup
echo -e "${BLUE}Setting up seller portal...${NC}"
cd ../seller-portal

if [ ! -f .env.local ]; then
    echo "Creating .env.local from .env.example"
    cp .env.example .env.local
fi

if [ ! -d node_modules ]; then
    echo "Installing dependencies..."
    npm install
fi

echo -e "${GREEN}Seller portal setup complete!${NC}"
echo ""

# Storefront setup
echo -e "${BLUE}Setting up customer storefront...${NC}"
cd ../customer-storefront

if [ ! -f .env.local ]; then
    echo "Creating .env.local from .env.example"
    cp .env.example .env.local
    echo -e "${BLUE}⚠ Edit .env.local with your Stripe public key${NC}"
fi

if [ ! -d node_modules ]; then
    echo "Installing dependencies..."
    npm install
fi

echo -e "${GREEN}Storefront setup complete!${NC}"
echo ""

echo -e "${GREEN}=================================="
echo "Setup Complete!"
echo "==================================${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env files with your configuration"
echo "2. Start PostgreSQL & Redis"
echo "3. Run: cd marketplace-backend && source venv/bin/activate && python -m uvicorn main:app --reload"
echo "4. In new terminal: cd seller-portal && npm run dev"
echo "5. In new terminal: cd customer-storefront && npm run dev"
echo ""
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Seller Portal: http://localhost:5173"
echo "Storefront: http://localhost:5174"
echo ""
