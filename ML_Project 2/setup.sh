#!/bin/bash

# Agentic AI Art Generator - Automated Setup Script
# This script sets up both backend and frontend

set -e  # Exit on error

echo "=€ Setting up Agentic AI Art Generator..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "=æ Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN} Found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED} Python 3 is not installed${NC}"
    echo "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

# Check Node.js
echo "=æ Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN} Found Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED} Node.js is not installed${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo ""
echo "==================================="
echo "  BACKEND SETUP"
echo "==================================="

# Backend setup
cd backend

echo "=' Creating Python virtual environment..."
python3 -m venv venv

echo " Activating virtual environment..."
source venv/bin/activate

echo "=å Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo "™  Checking .env file..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}   No .env file found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}   IMPORTANT: Edit backend/.env and add your OPENAI_API_KEY${NC}"
else
    echo -e "${GREEN} .env file exists${NC}"
fi

cd ..

echo ""
echo "==================================="
echo "  FRONTEND SETUP"
echo "==================================="

# Frontend setup
cd frontend

echo "=å Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "==================================="
echo "   SETUP COMPLETE!"
echo "==================================="
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo ""
echo "1. Add your OpenAI API key:"
echo "   ${YELLOW}nano backend/.env${NC}"
echo "   (Add: OPENAI_API_KEY=your_key_here)"
echo ""
echo "2. Start the backend (Terminal 1):"
echo "   ${YELLOW}cd backend${NC}"
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo "   ${YELLOW}python3 main.py${NC}"
echo ""
echo "3. Start the frontend (Terminal 2):"
echo "   ${YELLOW}cd frontend${NC}"
echo "   ${YELLOW}npm run dev${NC}"
echo ""
echo "4. Open your browser:"
echo "   ${YELLOW}http://localhost:5173${NC}"
echo ""
echo -e "${GREEN}<¨ Happy creating!${NC}"
