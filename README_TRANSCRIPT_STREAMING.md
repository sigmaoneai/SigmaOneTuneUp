# 🎙️ Real-Time Transcript Streaming Setup

This guide explains how to set up real-time transcript streaming from RetellAI directly to your application without using ngrok.

## ✅ Your Existing Configuration

You already have `RETELLAI_AGENT_WEBHOOK_URL` configured! Your webhook endpoint is ready at:
```
https://classic-husky-steady.ngrok-free.app/api/v1/retellai/agent-level-webhook
```

**No changes needed** - your existing RetellAI agents should already be configured to use this webhook URL.

## 🔧 Backend Configuration

### 1. Webhook Endpoints Available
Your backend has **two** webhook endpoints:

**Your existing endpoint:**
```
POST /api/v1/retellai/agent-level-webhook
```

**Alternative endpoint:**
```
POST /api/v1/calls/webhook/retell
```

Both endpoints handle the same events with real-time streaming:
- `call_started` - Call initiation
- `call_ended` - Call completion  
- `agent_response` - Real-time AI agent responses
- `user_speech` - Real-time human speech
- `tool_call` - Function calls (ticket creation, customer lookup)
- `speech_detected` - Speech detection events

### 2. WebSocket Streaming
Real-time transcript data is broadcast via WebSocket at:
```
ws://localhost:8000/api/v1/calls/ws/transcript/{call_id}
```

## 🌐 RetellAI Configuration

### Option 1: Public Server (Recommended)
Deploy your backend to a public server and configure RetellAI webhooks to point to:
```
https://your-domain.com/api/v1/calls/webhook/retell
```

### Option 2: Local Development with Public Tunnel

#### A. Using Cloudflare Tunnel (Free)
```bash
# Install cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Create tunnel to your local backend
cloudflared tunnel --url localhost:8000
```

#### B. Using LocalTunnel (Alternative)
```bash
npm install -g localtunnel
lt --port 8000 --subdomain your-app-name
```

#### C. Using Serveo (SSH-based)
```bash
ssh -R 80:localhost:8000 serveo.net
```

### 3. RetellAI Webhook Setup

In your RetellAI agent configuration, set the webhook URL to:
```json
{
  "webhook_url": "https://your-public-url.com/api/v1/calls/webhook/retell",
  "webhook_events": [
    "call_started",
    "call_ended", 
    "agent_response",
    "user_speech",
    "tool_call",
    "speech_detected"
  ]
}
```

## 🚀 Testing the Setup

### 1. Start Your Backend
```bash
cd backend
python run.py
```

### 2. Start Your Frontend  
```bash
cd frontend
npm run dev
```

### 3. Open E2E Tuning Page
Navigate to: `http://localhost:3000/e2e-tuning`

### 4. Test Real-Time Streaming

1. **Select an Agent** - Choose an agent with webhook configured
2. **Enter Phone Number** - Your test phone number
3. **Start Call** - Click "Start Call" button
4. **Make the Call** - The system will initiate the call via RetellAI
5. **Watch Live Transcript** - See real-time transcript streaming in the interface

## 🎯 What You'll See

### Real-Time Features
- **Live Transcript** - Speech appears as it's spoken
- **Interim Transcripts** - Partial speech with dashed borders (yellow "Interim" badge)  
- **Speech Detection** - "Speaking..." indicators with animated dots
- **Tool Calls** - Function calls with parameters and results
- **Ticket Creation** - Tickets appear automatically when created by agent

### Visual Indicators
- 🔵 **Live Badge** - Final transcript messages from webhook
- 🟡 **Interim Badge** - Partial/in-progress transcripts
- 🟠 **Speaking Badge** - Active speech detection
- 🔧 **Tool Call Icon** - Function executions
- 🎫 **Tickets** - Auto-created tickets from calls

## 🔍 Troubleshooting

### Webhook Not Receiving Data
1. **Check RetellAI Configuration**
   ```bash
   curl -X GET "https://api.retellai.com/v2/agent/{agent_id}" \
   -H "Authorization: Bearer YOUR_API_KEY"
   ```

2. **Verify Webhook URL is Accessible**
   ```bash
   curl -X POST "https://your-public-url.com/api/v1/calls/webhook/retell" \
   -H "Content-Type: application/json" \
   -d '{"event":"test","data":{"call_id":"test"}}'
   ```

3. **Check Backend Logs**
   Look for webhook processing messages in your backend logs

### WebSocket Connection Issues
1. **Check Browser Console** - Look for WebSocket connection errors
2. **Verify Call ID** - WebSocket connects using the RetellAI call ID
3. **Check CORS** - Ensure WebSocket CORS is properly configured

### No Transcript Streaming
1. **Verify Webhook Events** - Ensure `agent_response` and `user_speech` events are enabled
2. **Check Call Status** - Call must be in "ongoing" status
3. **Agent Configuration** - Verify agent has webhook_url set

## 📊 Development vs Production

### Development
- Use tunnel services for local testing
- Backend runs on `localhost:8000`
- Frontend runs on `localhost:3000`

### Production  
- Deploy backend to cloud service (AWS, GCP, Azure, etc.)
- Configure domain with SSL certificate
- Update RetellAI webhook URLs to production endpoints
- Consider rate limiting and authentication

## 🔐 Security Considerations

### Webhook Authentication (Recommended)
Add webhook signature verification:
```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(), 
        payload, 
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### Rate Limiting
Implement rate limiting for webhook endpoints to prevent abuse.

### HTTPS Only
Always use HTTPS for webhook URLs in production.

## 🎉 Success!

Once configured, you'll see real-time transcript streaming just like you experienced with ngrok, but integrated directly into your E2E tuning interface with additional features like:

- Visual transcript styling
- Ticket creation tracking  
- Tool call monitoring
- Speech detection indicators
- Call session management

No more terminal streaming - everything is now beautifully integrated into your web interface! 🚀 