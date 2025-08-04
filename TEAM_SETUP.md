# 🚀 Team Setup Guide - E2E Testing

## Super Quick Setup (3 Commands)

```bash
# 1. Start backend
cd backend && source venv/bin/activate && python run.py

# 2. Start ngrok (gets random URL each time)  
ngrok http 8000

# 3. Auto-update .env files with current ngrok URL
./update_ngrok_env.sh
```

**Then refresh your frontend page - all services should be green!** ✅

## 🔄 Daily Workflow (Each Time You Restart)

**The Reality with ngrok Free:** Each time you restart ngrok, you get a new random URL like `abc123.ngrok-free.app`

**Solution:** Just run the auto-update script:
```bash
./update_ngrok_env.sh
```

This script:
- ✅ Detects your current ngrok URL
- ✅ Updates `frontend/.env` and `backend/.env` automatically  
- ✅ Shows you the webhook URL to update in RetellAI
- ✅ Creates backups of your old .env files

## 🎯 For Production Teams

**Recommendation:** Upgrade to ngrok Pro ($8/month) for:
- 🔗 **Stable custom subdomains** (no more random URLs!)
- 🚀 **No session limits** (multiple teammates simultaneously)
- ⚡ **Better performance** and reliability

**Alternative:** Use Railway/Heroku for a stable staging environment.

## 📋 Full Setup (First Time Only)

If you need to install everything:

```bash
# 1. Clone and install dependencies
git clone <repo>
cd SigmaOneTuneUp

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Frontend setup  
cd ../frontend
npm install

# 4. Start services (3 terminals)
# Terminal 1: Backend
cd backend && source venv/bin/activate && python run.py

# Terminal 2: Frontend  
cd frontend && npm run dev

# Terminal 3: Ngrok
ngrok http 8000

# Terminal 4: Auto-update .env
./update_ngrok_env.sh
```

## 🔧 Troubleshooting

**"Update Needed" in Service Manager?**
```bash
./update_ngrok_env.sh
```

**ngrok session limit error?**
- Only 1 ngrok session per free account
- Kill existing sessions: `pkill ngrok`
- Or upgrade to Pro plan

**Need to update RetellAI webhook?**
- ✨ **NEW**: Click "Auto-Update" button in E2E Service Manager - updates all agents automatically via API!
- Or get URL from `./update_ngrok_env.sh` output and paste manually into RetellAI agent settings 