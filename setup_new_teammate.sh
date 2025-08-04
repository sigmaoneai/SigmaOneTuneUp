#!/bin/bash

# SigmaOne TuneUp - New Team Member Setup
# This script automates the entire setup process

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🚀 SigmaOne TuneUp - New Team Member Setup${NC}"
echo ""

# Get team member info
read -p "What's your name/identifier? (e.g., alice, bob): " TEAM_MEMBER_NAME
TEAM_MEMBER_NAME=$(echo "$TEAM_MEMBER_NAME" | tr '[:upper:]' '[:lower:]' | tr -d ' ')

if [ -z "$TEAM_MEMBER_NAME" ]; then
    echo -e "${RED}❌ Name is required${NC}"
    exit 1
fi

echo -e "${BLUE}👋 Hi $TEAM_MEMBER_NAME! Setting up your development environment...${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

MISSING_DEPS=()

if ! command -v python3 &> /dev/null; then
    MISSING_DEPS+=("python3")
fi

if ! command -v node &> /dev/null; then
    MISSING_DEPS+=("node/npm")
fi

if ! command -v ngrok &> /dev/null; then
    MISSING_DEPS+=("ngrok")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo ""
    echo "Please install:"
    for dep in "${MISSING_DEPS[@]}"; do
        case $dep in
            "python3")
                echo "  • Python 3: https://python.org/downloads"
                ;;
            "node/npm")
                echo "  • Node.js: https://nodejs.org/downloads"
                ;;
            "ngrok")
                echo "  • ngrok: https://ngrok.com/download"
                ;;
        esac
    done
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"
echo ""

# Generate URLs
NGROK_URL="https://${TEAM_MEMBER_NAME}-sigmaonetune.ngrok.io"
WEBHOOK_URL="${NGROK_URL}/api/v1/retellai/agent-level-webhook"

echo -e "${BLUE}🔗 Your URLs will be:${NC}"
echo -e "   Backend: $NGROK_URL"
echo -e "   Frontend: http://localhost:3000"
echo -e "   Webhook: $WEBHOOK_URL"
echo ""

# Setup backend .env
echo -e "${YELLOW}🔧 Setting up backend configuration...${NC}"

cd backend

if [ ! -f ".env" ]; then
    echo "# SigmaOne TuneUp Backend Configuration" > .env
    echo "" >> .env
    echo "# Database" >> .env
    echo "DATABASE_URL=postgresql://username:password@localhost:5432/sigmaonetune" >> .env
    echo "" >> .env
    echo "# RetellAI Configuration" >> .env
    echo "RETELLAI_API_KEY=your_retellai_api_key_here" >> .env
    echo "RETELLAI_AGENT_WEBHOOK_URL=${WEBHOOK_URL}" >> .env
    echo "" >> .env
    echo "# SyncroMSP Configuration" >> .env
    echo "SYNCROMSP_API_KEY=your_syncromsp_api_key_here" >> .env
    echo "SYNCROMSP_BASE_URL=https://your-subdomain.syncromsp.com" >> .env
    
    echo -e "${GREEN}✅ Created backend/.env${NC}"
else
    echo -e "${YELLOW}ℹ️  backend/.env already exists${NC}"
fi

# Install backend dependencies
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
source venv/bin/activate
pip install -q -r requirements.txt

echo -e "${GREEN}✅ Backend setup complete${NC}"

# Setup frontend .env
echo -e "${YELLOW}🔧 Setting up frontend configuration...${NC}"

cd ../frontend

if [ ! -f ".env" ]; then
    echo "# SigmaOne TuneUp Frontend Configuration" > .env
    echo "" >> .env
    echo "# Your personal ngrok URL" >> .env
    echo "VITE_NGROK_URL=${NGROK_URL}" >> .env
    echo "VITE_API_BASE_URL=${NGROK_URL}/api/v1" >> .env
    
    echo -e "${GREEN}✅ Created frontend/.env${NC}"
else
    echo -e "${YELLOW}ℹ️  frontend/.env already exists${NC}"
fi

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install --silent
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}ℹ️  Frontend dependencies already installed${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}🎉 Setup complete! Here's what to do next:${NC}"
echo ""

echo -e "${BLUE}📋 Required Manual Steps:${NC}"
echo -e "1. ${YELLOW}Add your API keys to backend/.env:${NC}"
echo -e "   • RETELLAI_API_KEY=your_actual_key"
echo -e "   • SYNCROMSP_API_KEY=your_actual_key (if using SyncroMSP)"
echo ""

echo -e "${BLUE}🚀 Start Development (run in separate terminals):${NC}"
echo ""
echo -e "${GREEN}Terminal 1 - Backend:${NC}"
echo -e "   cd backend && source venv/bin/activate && python run.py"
echo ""
echo -e "${GREEN}Terminal 2 - Ngrok:${NC}"  
echo -e "   ngrok http 8000 --subdomain=${TEAM_MEMBER_NAME}-sigmaonetune"
echo ""
echo -e "${GREEN}Terminal 3 - Frontend:${NC}"
echo -e "   cd frontend && npm run dev"
echo ""

echo -e "${BLUE}🎯 After services start:${NC}"
echo -e "1. Visit: ${YELLOW}http://localhost:3000${NC}"
echo -e "2. Go to: ${YELLOW}E2E Agent Tuning${NC}"
echo -e "3. Check: ${YELLOW}Service Manager${NC} shows all green"
echo -e "4. Configure RetellAI agents with webhook URL:"
echo -e "   ${YELLOW}${WEBHOOK_URL}${NC}"
echo ""

echo -e "${PURPLE}💡 Pro Tips:${NC}"
echo -e "• Service Manager shows real-time status of all services"
echo -e "• Green = running, Red = stopped, Yellow = starting"  
echo -e "• Use 'Copy URL' button to get webhook URL for RetellAI"
echo -e "• Live transcript streaming works automatically once configured"
echo ""

echo -e "${GREEN}✨ Happy coding, ${TEAM_MEMBER_NAME}! ✨${NC}" 