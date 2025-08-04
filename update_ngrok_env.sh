#!/bin/bash

# Auto-update .env files with current ngrok URL
# This script detects the running ngrok tunnel and updates your .env files

echo "🔍 Detecting current ngrok tunnel..."

# Check if ngrok is running
if ! curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
    echo "❌ ngrok is not running!"
    echo "   Start ngrok first: ngrok http 8000"
    exit 1
fi

# Get the current ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    for tunnel in tunnels:
        if tunnel.get('proto') == 'https' and '8000' in tunnel.get('config', {}).get('addr', ''):
            print(tunnel['public_url'])
            break
except:
    pass
")

if [ -z "$NGROK_URL" ]; then
    echo "❌ No ngrok tunnel found for port 8000"
    exit 1
fi

echo "✅ Found ngrok URL: $NGROK_URL"

# Update frontend/.env
if [ -f "frontend/.env" ]; then
    echo "📝 Updating frontend/.env..."
    
    # Create backup
    cp frontend/.env frontend/.env.backup
    
    # Update the URLs
    sed -i.tmp "s|VITE_NGROK_URL=.*|VITE_NGROK_URL=$NGROK_URL|g" frontend/.env
    sed -i.tmp "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=$NGROK_URL/api/v1|g" frontend/.env
    rm frontend/.env.tmp
    
    echo "✅ Updated frontend/.env"
else
    echo "📝 Creating frontend/.env..."
    cat > frontend/.env << EOF
VITE_NGROK_URL=$NGROK_URL
VITE_API_BASE_URL=$NGROK_URL/api/v1
EOF
    echo "✅ Created frontend/.env"
fi

# Update backend/.env if it exists
if [ -f "backend/.env" ]; then
    echo "📝 Updating backend/.env..."
    cp backend/.env backend/.env.backup
    sed -i.tmp "s|WEBHOOK_URL=.*|WEBHOOK_URL=$NGROK_URL/api/v1/retellai/agent-level-webhook|g" backend/.env
    rm backend/.env.tmp
    echo "✅ Updated backend/.env"
fi

echo ""
echo "🎉 Environment updated successfully!"
echo "   Frontend URL: $NGROK_URL"
echo "   API URL: $NGROK_URL/api/v1" 
echo "   Webhook URL: $NGROK_URL/api/v1/retellai/agent-level-webhook"
echo ""
echo "💡 Next steps:"
echo "   1. Refresh your E2E Tuning page"
echo "   2. Click 'Auto-Update' button in Service Manager to update all RetellAI agents automatically! ✨"
echo "   3. Start testing!" 