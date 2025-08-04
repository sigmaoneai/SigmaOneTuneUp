# SigmaOne TuneUp Backend

A comprehensive backend API for managing RetellAI agents and SyncroMSP integration with enhanced observability.

## Features

- **RetellAI Integration**: Complete CRUD operations for agents and phone number management
- **SyncroMSP Integration**: Access tickets, customers, and create new tickets
- **Call Management**: Track, monitor, and analyze voice AI calls
- **Real-time Observability**: Comprehensive logging, metrics, and dashboard
- **Webhook Support**: Handle RetellAI webhooks for real-time call updates
- **Database Management**: PostgreSQL with async SQLAlchemy
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL database (configured in .env)
- RetellAI API key
- SyncroMSP API credentials

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

3. Run the server:
```bash
python run.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Agents (`/api/v1/agents`)
- `GET /` - List all agents
- `POST /` - Create new agent
- `GET /{agent_id}` - Get specific agent
- `PUT /{agent_id}` - Update agent
- `DELETE /{agent_id}` - Delete agent
- `POST /{agent_id}/test-call` - Make test call
- `GET /{agent_id}/sync-retell` - Sync with RetellAI

### Phone Numbers (`/api/v1/phone-numbers`)
- `GET /` - List phone numbers
- `GET /sync-from-retell` - Sync from RetellAI
- `POST /assign` - Assign number to agent
- `POST /{phone_id}/unassign` - Unassign number

### Calls (`/api/v1/calls`)
- `GET /` - List calls
- `POST /` - Make outbound call
- `GET /{call_id}` - Get call details
- `GET /sync-all/retell` - Sync all calls
- `POST /webhook/retell` - RetellAI webhook
- `GET /stats/today` - Today's call statistics

### SyncroMSP (`/api/v1/syncro`)
- `GET /tickets` - List tickets
- `GET /tickets/sync-from-syncro` - Sync tickets
- `POST /tickets` - Create ticket
- `GET /customers` - List customers
- `GET /customers/search/{term}` - Search customers

### Dashboard (`/api/v1/dashboard`)
- `GET /stats` - Dashboard statistics
- `GET /health-check` - System health
- `GET /call-activity` - Call activity metrics
- `GET /agent-performance` - Agent performance
- `GET /system-overview` - Complete overview

## Configuration

Key environment variables:

### RetellAI
- `RETELLAI_API_KEY` - Your RetellAI API key
- `RETELLAI_AGENT_WEBHOOK_URL` - Webhook URL for agent events

### SyncroMSP
- `SYNCROMSP_API_KEY` - SyncroMSP API key
- `SYNCROMSP_API_URL` - SyncroMSP base URL

### Database
- `POSTGRES_DB_HOST_DEV` - Development database host
- `POSTGRES_DB_NAME_DEV` - Development database name
- `POSTGRES_DB_USER_DEV` - Development database user
- `POSTGRES_DB_PASSWORD_DEV` - Development database password

## Usage Examples

### Create an Agent
```bash
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Support Agent",
    "prompt": "You are a helpful customer support agent...",
    "voice_id": "11labs-Adrian"
  }'
```

### Sync Phone Numbers
```bash
curl -X GET "http://localhost:8000/api/v1/phone-numbers/sync-from-retell"
```

### Make a Test Call
```bash
curl -X POST "http://localhost:8000/api/v1/agents/1/test-call" \
  -H "Content-Type: application/json" \
  -d '{
    "test_phone_number": "+1234567890"
  }'
```

### Dashboard Stats
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/stats"
```

## Architecture

```
backend/
├── main.py                 # FastAPI application
├── run.py                  # Server startup script
├── api/
│   ├── database.py         # Database models & config
│   ├── schemas.py          # Pydantic models
│   ├── services/           # External service integrations
│   │   ├── retell_service.py
│   │   └── syncro_service.py
│   ├── routes/             # API route handlers
│   │   ├── agents.py
│   │   ├── phone_numbers.py
│   │   ├── calls.py
│   │   ├── syncro.py
│   │   └── dashboard.py
│   └── middleware/         # Custom middleware
│       └── logging.py
└── requirements.txt
```

## Observability Features

- **Request/Response Logging**: All API calls are logged with request IDs
- **Call Tracking**: Complete call lifecycle tracking
- **Health Checks**: Multi-system health monitoring
- **Performance Metrics**: Agent and system performance analytics
- **Real-time Events**: WebSocket-ready event streaming
- **Error Handling**: Comprehensive error logging and reporting

## Development

The API automatically generates OpenAPI documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

For development, set `DEBUG=true` in your `.env` file to enable:
- Auto-reload on code changes
- Detailed error messages
- SQL query logging

## Integration with RetellAI Tools

The backend provides tool endpoints that RetellAI agents can call:
- `/api/v1/syncro/retell-tools/{agent_id}/lookup-customer`
- `/api/v1/syncro/retell-tools/{agent_id}/create-ticket`

These are configured in your RetellAI agent tool definitions.

## SyncroMSP Integration Setup

To connect to your SyncroMSP API, set the following environment variables:

```bash
# Required - Your SyncroMSP API credentials
SYNCROMSP_API_KEY=your_syncromsp_api_key_here
SYNCROMSP_BASE_URL=https://your-subdomain.syncromsp.com

# Optional - Custom API paths (defaults shown)
SYNCROMSP_TICKETS_PATH=/api/v1/tickets
SYNCROMSP_CUSTOMERS_PATH=/api/v1/customers
SYNCROMSP_TICKET_COMMENTS_PATH=/comment
```

### Getting Your SyncroMSP API Credentials

1. Log into your SyncroMSP account
2. Go to Admin → Global Settings → API
3. Generate a new API key
4. Set the `SYNCROMSP_API_KEY` environment variable to this key
5. Set the `SYNCROMSP_BASE_URL` to your SyncroMSP subdomain URL

### Read-Only Mode

The integration runs in **read-only mode** by default, which means:
- ✅ Fetch tickets, customers, and other data from SyncroMSP
- ✅ Real-time sync of data from your SyncroMSP system
- ❌ No modifications are made to your SyncroMSP data
- ❌ Cannot create tickets or update data through the integration

This ensures safe integration without risk of modifying your production SyncroMSP data.

## Monitoring

Monitor your deployment using the dashboard endpoints:
- System health: `/api/v1/dashboard/health-check`
- Call activity: `/api/v1/dashboard/call-activity`
- Agent performance: `/api/v1/dashboard/agent-performance`

## Security

- Environment-based configuration
- Request ID tracking for audit trails
- Comprehensive error handling without data leakage
- CORS configuration for frontend integration 