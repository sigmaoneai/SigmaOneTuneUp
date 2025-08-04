#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Restarting ngrok tunnel...${NC}"

# Kill existing ngrok processes
pkill -f ngrok
sleep 2

# Start new ngrok tunnel
echo -e "${YELLOW}📡 Starting ngrok tunnel on port 8000...${NC}"
if [ -n "$1" ]; then
    echo -e "${BLUE}🎯 Using custom subdomain: $1${NC}"
    ngrok http 8000 --subdomain="$1" &
else
    echo -e "${YELLOW}💡 For stable URL, run: ./restart_ngrok.sh your-subdomain-name${NC}"
    ngrok http 8000 &
fi

# Wait for ngrok to start
sleep 5

# Get the new ngrok URL
echo -e "${YELLOW}🔍 Getting new ngrok URL...${NC}"
NEW_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
data = json.load(sys.stdin)
tunnels = data.get('tunnels', [])
for tunnel in tunnels:
    if tunnel.get('proto') == 'https':
        print(tunnel['public_url'])
        break
")

if [ -z "$NEW_URL" ]; then
    echo -e "${RED}❌ Failed to get ngrok URL. Make sure ngrok is running.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ New ngrok URL: $NEW_URL${NC}"

# Update RetellAI webhook URLs
echo -e "${YELLOW}🔄 Updating RetellAI webhook URLs...${NC}"
python3 update_webhook_url.py "$NEW_URL"

echo -e "${GREEN}🎉 Setup complete!${NC}"
echo -e "${BLUE}Backend URL: $NEW_URL${NC}"
echo -e "${BLUE}Webhook URL: $NEW_URL/api/v1/retellai/agent-level-webhook${NC}"
echo -e "${BLUE}API Docs: $NEW_URL/docs${NC}" 