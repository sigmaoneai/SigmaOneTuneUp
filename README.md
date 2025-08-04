# SigmaOne TuneUp

A comprehensive Vue.js frontend and FastAPI backend application for managing AI-powered customer service interactions, integrating with RetellAI and SyncroMSP.

## 🎯 **Live E2E Testing & Transcript Streaming**

**Perfect for testing RetellAI voice agents with real-time visibility:**
- 🎙️ **Live transcript streaming** from RetellAI calls
- 📊 **Real-time service monitoring** (backend, ngrok, frontend status)
- 🔧 **One-click setup** for new team members  
- 🌐 **WebSocket integration** for instant updates
- 🎛️ **Service management UI** with start/stop controls
- 🔗 **Automatic webhook configuration** for RetellAI agents

## Features

### Frontend (Vue.js)
- **🎯 E2E Agent Tuning**: Live transcript streaming, service monitoring, and real-time testing
- **📊 Service Manager**: Real-time status of backend, ngrok, and frontend services  
- **🎙️ Live Transcript**: WebSocket-powered real-time call transcription from RetellAI
- **Dashboard**: Real-time system overview with health monitoring and statistics
- **Agents Management**: RetellAI agent configuration and monitoring
- **Phone Numbers**: Phone number management and call routing
- **Call History**: Detailed call logs and analytics with filtering and search
- **Prompts Management**: AI prompt configuration and testing
- **SyncroMSP Integration**: Ticket and customer management (currently in mock mode)
- **Settings**: System configuration and API status monitoring

### Backend (FastAPI)
- **🎙️ Live Transcript Streaming**: WebSocket endpoints for real-time RetellAI call transcription
- **🔗 RetellAI Webhook Handler**: Processes live call events (speech, tool calls, call status)
- **📊 Service Health API**: Real-time monitoring of backend, database, and external services
- **RESTful API**: Comprehensive endpoints for all frontend features
- **RetellAI Integration**: Agent management and call handling
- **SyncroMSP Integration**: Mock ticket and customer management
- **Real-time WebSocket**: Live updates for call status and system health
- **Async Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based user authentication
- **Health Monitoring**: System status and service health checks

## Technology Stack

### Frontend
- Vue 3 with Composition API
- Pinia for state management
- Vue Router for SPA navigation
- Tailwind CSS for styling
- Axios for HTTP client
- Chart.js for data visualization
- Heroicons for UI icons
- Date-fns for date formatting
- Vue Toastification for notifications

### Backend
- FastAPI with async/await support
- Pydantic for data validation
- SQLAlchemy with asyncpg for PostgreSQL
- Alembic for database migrations
- Redis for caching (optional)
- Loguru for logging
- WebSockets for real-time updates
- HTTPx for external API calls

## Setup Instructions

### 🚀 **Super Quick Setup (Recommended for New Team Members)**

**One command setup:**
```bash
git clone <this-repo>
cd SigmaOneTuneUp
./setup_new_teammate.sh
```

The script will:
- ✅ Check prerequisites (Python, Node.js, ngrok)
- ✅ Create personalized `.env` files with your ngrok URL
- ✅ Install all dependencies (backend + frontend)  
- ✅ Generate your webhook URLs for RetellAI
- ✅ Show you exactly what commands to run next

**Then start development (3 terminals):**
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && python run.py

# Terminal 2: Your ngrok tunnel
ngrok http 8000 --subdomain=YOUR-NAME-sigmaonetune

# Terminal 3: Frontend
cd frontend && npm run dev
```

**Access your E2E testing:**
- 🎯 **Frontend**: http://localhost:3000 → E2E Agent Tuning
- 📊 **Service Manager**: Real-time status monitoring
- 🔗 **Your Backend**: https://YOUR-NAME-sigmaonetune.ngrok.io
- 📖 **API Docs**: https://YOUR-NAME-sigmaonetune.ngrok.io/docs

---

### 📋 **Manual Setup (If You Prefer)**

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- PostgreSQL (optional, can use SQLite for development)
- Redis (optional)
- **ngrok** (for webhook tunneling)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration values
   ```

5. **Start the backend server:**
   ```bash
   # Development mode
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

## Development

### Backend Development
- The backend runs on `http://localhost:8000`
- API documentation available at `http://localhost:8000/docs` (Swagger UI)
- Alternative docs at `http://localhost:8000/redoc`

### Frontend Development
- The frontend runs on `http://localhost:5173` (Vite dev server)
- Hot module replacement enabled for development
- Proxy configuration routes API calls to backend

### Mock Mode
- SyncroMSP integration currently runs in mock mode for testing
- Mock data includes sample tickets, customers, and operations
- Real SyncroMSP operations are commented out in the backend routes
- To enable real SyncroMSP integration, set `SYNCRO_MOCK_MODE=false` and configure API credentials

## API Endpoints

### Core Endpoints
- `GET /health` - System health check
- `GET /api/system/health` - Detailed system status
- `GET /api/system/stats` - System statistics

### RetellAI Integration
- `GET /api/retell/agents` - List agents
- `POST /api/retell/agents` - Create agent
- `GET /api/retell/phone-numbers` - List phone numbers
- `GET /api/retell/calls` - List calls with filtering

### SyncroMSP Integration (Mock Mode)
- `GET /api/syncro/tickets` - List tickets
- `POST /api/syncro/tickets` - Create ticket (mock)
- `GET /api/syncro/tickets/{id}` - Get ticket details
- `GET /api/syncro/customers` - List customers
- `GET /api/syncro/customers/{id}` - Get customer details

### Prompts Management
- `GET /api/prompts` - List prompts
- `POST /api/prompts` - Create prompt
- `PUT /api/prompts/{id}` - Update prompt
- `DELETE /api/prompts/{id}` - Delete prompt

## Configuration

### Environment Variables
See `.env.example` for all available configuration options including:
- Database connection settings
- API keys for external services
- CORS configuration
- Logging levels
- Mock mode settings

### Frontend Configuration
- API base URL configured in `src/services/api.js`
- Tailwind configuration in `tailwind.config.js`
- Vite configuration in `vite.config.js`

## Production Deployment

### Backend
1. Set `ENVIRONMENT=production` in `.env`
2. Configure production database
3. Set secure `SECRET_KEY`
4. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend
1. Build the production version:
   ```bash
   npm run build
   ```
2. Serve the `dist` folder with a web server like Nginx
3. Configure reverse proxy to backend API

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary software. All rights reserved. 