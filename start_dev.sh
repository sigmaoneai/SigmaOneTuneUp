#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 Starting SigmaOne TuneUp Development Environment${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/run.py" ] || [ ! -f "frontend/package.json" ]; then
    echo -e "${RED}❌ Please run this script from the SigmaOneTuneUp root directory${NC}"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed${NC}"
    exit 1
fi

if ! command_exists ngrok; then
    echo -e "${RED}❌ ngrok is required but not installed${NC}"
    echo -e "${YELLOW}💡 Install from: https://ngrok.com/download${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"
echo ""

# Backend setup
echo -e "${BLUE}🔧 Setting up backend...${NC}"
cd backend

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}📝 Creating .env from .env.example${NC}"
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit backend/.env with your API keys before continuing${NC}"
        read -p "Press Enter when you've updated the .env file..."
    else
        echo -e "${RED}❌ No .env file found. Please create one with your API keys.${NC}"
        exit 1
    fi
fi

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
source venv/bin/activate
pip install -r requirements.txt

echo -e "${GREEN}✅ Backend setup complete${NC}"
cd ..

# Frontend setup
echo -e "${BLUE}🌐 Setting up frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    npm install
fi

echo -e "${GREEN}✅ Frontend setup complete${NC}"
cd ..

echo ""
echo -e "${PURPLE}🚀 Starting services...${NC}"

# Start backend in background
echo -e "${BLUE}🔄 Starting backend server...${NC}"
cd backend
source venv/bin/activate
python run.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start ngrok in background  
echo -e "${BLUE}🌐 Starting ngrok tunnel...${NC}"
echo -e "${YELLOW}💡 For stable URL, use: ngrok http 8000 --subdomain=your-name-sigmaonetune${NC}"
ngrok http 8000 --log=stdout &
NGROK_PID=$!

# Wait for ngrok to start
sleep 5

# Get ngrok URL
echo -e "${YELLOW}🔍 Getting ngrok URL...${NC}"
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    for tunnel in tunnels:
        if tunnel.get('proto') == 'https':
            print(tunnel['public_url'])
            break
except:
    pass
" 2>/dev/null)

if [ -n "$NGROK_URL" ]; then
    echo -e "${GREEN}✅ Backend available at: $NGROK_URL${NC}"
    echo -e "${BLUE}📖 API Docs: $NGROK_URL/docs${NC}"
    echo -e "${BLUE}🔗 Webhook URL: $NGROK_URL/api/v1/retellai/agent-level-webhook${NC}"
else
    echo -e "${YELLOW}⚠️  Could not get ngrok URL automatically${NC}"
fi

# Start frontend
echo -e "${BLUE}⚡ Starting frontend development server...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}🎉 Development environment started!${NC}"
echo ""
echo -e "${BLUE}📍 Services running:${NC}"
echo -e "   Backend:  http://localhost:8000"
echo -e "   Frontend: http://localhost:3000"
if [ -n "$NGROK_URL" ]; then
    echo -e "   Public:   $NGROK_URL"
fi
echo ""
echo -e "${PURPLE}🔧 Next steps:${NC}"
echo -e "1. Visit http://localhost:3000 to access the frontend"
echo -e "2. Go to E2E Agent Tuning to test live transcripts"
if [ -n "$NGROK_URL" ]; then
    echo -e "3. Update your RetellAI agents with webhook URL:"
    echo -e "   ${NGROK_URL}/api/v1/retellai/agent-level-webhook"
fi
echo ""
echo -e "${YELLOW}💡 To stop all services, press Ctrl+C${NC}"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null  
    kill $FRONTEND_PID 2>/dev/null
    pkill -f ngrok 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Setup signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait 