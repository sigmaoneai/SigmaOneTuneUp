# 👥 SigmaOne TuneUp - Team Development Workflow

## 🏗️ Environment Setup

### **Individual Development (Fast Iteration)**
Each teammate runs their own ngrok tunnel with custom subdomain for rapid testing:

```bash
# Terminal 1: Start backend with auto-reload
cd backend
python run.py

# Terminal 2: Start personal ngrok tunnel with custom subdomain
ngrok http 8000 --subdomain=your-name-sigmaonetune
# Gets stable URL like: https://your-name-sigmaonetune.ngrok.io

# Terminal 3: Configure frontend environment
cd frontend
# Edit .env and set: VITE_NGROK_URL=https://your-name-sigmaonetune.ngrok.io
npm run dev
```

**Example URLs for team members:**
- You: `https://classic-husky-steady.ngrok-free.app` ✅ (already set up)
- Alice: `https://alice-sigmaonetune.ngrok.io`  
- Bob: `https://bob-sigmaonetune.ngrok.io`

**Frontend .env Configuration:**
```bash
# frontend/.env
VITE_NGROK_URL=https://your-name-sigmaonetune.ngrok.io
VITE_API_BASE_URL=https://your-name-sigmaonetune.ngrok.io/api/v1
```

**Benefits:**
- ✅ **Instant code changes** (0-second iteration)
- ✅ **Personal testing** without conflicts
- ✅ **Full debugging** access

### **Shared Staging (Team Collaboration)**
Deployed on Railway for team testing and demos:

```bash
# Deploy to shared staging
cd backend
railway up
# URL: https://sigmaonetune-staging.railway.app
```

**Benefits:**
- ✅ **Stable URL** for team testing
- ✅ **Client demos** and presentations
- ✅ **Integration testing** between team features

### **Production (AWS)**
Final production deployment on AWS infrastructure:
- ECS/Fargate for containerized deployment
- RDS for managed PostgreSQL 
- ALB for load balancing
- Route53 for custom domain

## 🔄 Development Flow

### **Daily Development (Individual)**
```bash
# 1. Start your services
cd backend && python run.py          # Terminal 1
ngrok http 8000                      # Terminal 2  
cd ../frontend && npm run dev        # Terminal 3

# 2. Get your ngrok URL and update RetellAI (if changed)
python update_webhook_url.py https://your-new-url.ngrok.io

# 3. Test and iterate rapidly
# - Code changes auto-reload
# - Test immediately with RetellAI
```

### **Team Testing (Staging)**
```bash
# 1. Push to staging when feature is ready
git push origin feature-branch

# 2. Deploy to shared staging
railway up

# 3. Team tests on stable URL:
# https://sigmaonetune-staging.railway.app
```

### **Production Deployment (AWS)**
```bash
# 1. Merge to main branch
git checkout main && git merge feature-branch

# 2. Deploy to AWS (automated via CI/CD)
# - GitHub Actions → AWS ECS deployment
# - Update production webhook URLs
```

## 🛠️ Team Setup Instructions

### **New Team Member Onboarding (Super Simple!)**

**Option 1: Automated Setup (Recommended)**
```bash
git clone <repo>
cd SigmaOneTuneUp
chmod +x setup_new_teammate.sh
./setup_new_teammate.sh
```
That's it! The script will:
- ✅ Check prerequisites 
- ✅ Create your personalized .env files
- ✅ Install all dependencies
- ✅ Generate your ngrok URLs
- ✅ Show you exactly what commands to run

**Option 2: Manual Setup**
If you prefer to set up manually:

1. **Clone and configure:**
```bash
git clone <repo>
cd SigmaOneTuneUp

# Backend setup
cd backend
# Create .env with your RetellAI API key

# Frontend setup  
cd ../frontend
# Create .env with: VITE_NGROK_URL=https://your-name-sigmaonetune.ngrok.io
```

2. **Install dependencies:**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd ../frontend && npm install
```

3. **Start development (3 terminals):**
```bash
# Terminal 1: Backend
cd backend && python run.py

# Terminal 2: Ngrok
ngrok http 8000 --subdomain=your-name-sigmaonetune

# Terminal 3: Frontend  
cd frontend && npm run dev
```

4. **Verify setup:**
- Visit `http://localhost:3000` → "E2E Agent Tuning"
- Service Manager shows all services as green ✅
- Update RetellAI agents with your webhook URL

### **RetellAI Agent Management**

**Individual Development:**
- Each teammate updates their agents to use their ngrok URL
- Use the `update_webhook_url.py` script when ngrok URL changes

**Staging/Production:**
- Dedicated agents for staging and production environments
- Stable webhook URLs that don't change

## 📋 Environment Variables

### **Individual Dev (.env)**
```bash
ENVIRONMENT=dev
RETELLAI_AGENT_WEBHOOK_URL=https://your-ngrok-url.ngrok.io/api/v1/retellai/agent-level-webhook
```

### **Staging (Railway)**
```bash
ENVIRONMENT=staging  
RETELLAI_AGENT_WEBHOOK_URL=https://sigmaonetune-staging.railway.app/api/v1/retellai/agent-level-webhook
```

### **Production (AWS)**
```bash
ENVIRONMENT=production
RETELLAI_AGENT_WEBHOOK_URL=https://api.sigmaonetune.com/api/v1/retellai/agent-level-webhook
```

## 🚨 Best Practices

### **For Fast Iteration:**
- Use ngrok for daily development
- Keep backend running with `--reload` flag
- Use `restart_ngrok.sh` when tunnel breaks

### **For Team Collaboration:**
- Test on staging before requesting reviews
- Use staging for client demos
- Coordinate major changes on staging

### **For Production:**
- Only deploy thoroughly tested features
- Use proper CI/CD pipeline
- Monitor AWS infrastructure

## 🔧 Quick Commands

```bash
# Start personal dev environment
./restart_ngrok.sh

# Deploy to staging
railway up

# Update webhook URLs
python update_webhook_url.py <new-url>

# Check all services health
curl https://your-url/health
``` 