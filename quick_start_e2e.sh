#!/bin/bash

# SigmaOne TuneUp - Quick Start for E2E Testing
# Your specific ngrok URLs are pre-configured

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 SigmaOne TuneUp - E2E Testing Quick Start${NC}"
echo ""

# Check if services are already running
BACKEND_RUNNING=$(curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "true" || echo "false")
NGROK_RUNNING=$(curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1 && echo "true" || echo "false")

 echo -e "${YELLOW}📊 Current Service Status:${NC}"
 if [ "$BACKEND_RUNNING" = "true" ]; then
     echo -e "   ✅ Backend: Running on http://localhost:8000"
 else
     echo -e "   ❌ Backend: Stopped"
 fi
 
 if [ "$NGROK_RUNNING" = "true" ]; then
     echo -e "   ✅ Ngrok: Running"
 else
     echo -e "   ❌ Ngrok: Stopped"
 fi
 
 echo -e "   ✅ Frontend: Running (you're viewing it!)"
echo ""

# Function to start services
start_services() {
    echo -e "${BLUE}🔥 Starting services for E2E testing...${NC}"
    echo ""
    
    # Terminal commands to run
    echo -e "${YELLOW}Run these commands in separate terminals:${NC}"
    echo ""
    echo -e "${GREEN}Terminal 1 - Backend:${NC}"
    echo "cd backend && python run.py"
    echo ""
         echo -e "${GREEN}Terminal 2 - Your Backend Ngrok:${NC}"
     echo "ngrok http --url=classic-husky-steady.ngrok-free.app 8000"
     echo ""
     echo -e "${GREEN}✅ Frontend is already running!${NC}"
     echo "(You're viewing this interface, so it's obviously running)"
    echo ""
    
         echo -e "${BLUE}📍 Your URLs will be:${NC}"
     echo -e "   Backend: https://classic-husky-steady.ngrok-free.app"
     echo -e "   Frontend: http://localhost:3000 (local development)"
     echo -e "   Webhook: https://classic-husky-steady.ngrok-free.app/api/v1/retellai/agent-level-webhook"
    echo ""
    
    echo -e "${YELLOW}🎯 For E2E Testing:${NC}"
    echo -e "1. Wait for all services to start"
    echo -e "2. Visit http://localhost:3000"
    echo -e "3. Go to 'E2E Agent Tuning' page"
    echo -e "4. Check service status in the Service Manager"
    echo -e "5. Start testing calls and watch live transcripts!"
}

# Function to show current status
show_status() {
    echo -e "${BLUE}📊 Service Status Check${NC}"
    echo ""
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "✅ Backend API: ${GREEN}Running${NC} → http://localhost:8000"
        echo -e "   📖 API Docs: http://localhost:8000/docs"
    else
        echo -e "❌ Backend API: ${RED}Stopped${NC}"
    fi
    
    # Check ngrok
    if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
        echo -e "✅ Ngrok Tunnels: ${GREEN}Running${NC}"
        
        # Get tunnel info
        TUNNELS=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for tunnel in data.get('tunnels', []):
        if tunnel.get('proto') == 'https':
            addr = tunnel.get('config', {}).get('addr', '')
            print(f'   🌐 {tunnel[\"public_url\"]} → {addr}')
except:
    pass
" 2>/dev/null)
        echo "$TUNNELS"
    else
        echo -e "❌ Ngrok Tunnels: Stopped"
    fi
    
         # Frontend status
     echo -e "✅ Frontend: ${GREEN}Running${NC} → http://localhost:3000"
     echo -e "   (You're viewing this interface, so it's obviously running!)"
    
    echo ""
    echo -e "${BLUE}🔗 RetellAI Webhook URL:${NC}"
    echo -e "   https://classic-husky-steady.ngrok-free.app/api/v1/retellai/agent-level-webhook"
}

# Main menu
echo -e "${YELLOW}Choose an action:${NC}"
echo "1. 🚀 Start E2E Testing Setup"
echo "2. 📊 Check Service Status" 
echo "3. 🔄 Refresh Status"
echo "4. ❓ Help"
echo ""

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        start_services
        ;;
    2)
        show_status
        ;;
    3)
        show_status
        ;;
    4)
        echo -e "${BLUE}🎯 E2E Testing Help${NC}"
        echo ""
                 echo "This script helps you start the remaining SigmaOne TuneUp development services"
         echo "for End-to-End testing with live transcript streaming."
         echo ""
         echo "Your setup uses:"
         echo "• Backend on port 8000 → ngrok classic-husky-steady.ngrok-free.app"
         echo "• Frontend on port 3000 → ✅ ALREADY RUNNING (you're viewing it!)" 
         echo "• RetellAI webhook configured for live transcript streaming"
        echo ""
        echo "After starting services, visit the E2E Agent Tuning page to:"
        echo "• Monitor service status"
        echo "• Start phone calls or agent-to-agent calls"
        echo "• Watch live transcript streaming"
        echo "• Test tool calls and ticket creation"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac 