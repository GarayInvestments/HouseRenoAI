# House Renovators AI Portal - AI Agent Instructions

**Version**: 1.0.0  
**Last Updated**: November 3, 2025  
**Schema Version**: GC_Permit_Compliance_Schema.json (12-sheet structure)  
**Production Status**: Live at https://houserenoai.onrender.com

## 🏗️ Project Overview
FastAPI-based AI portal for construction permit management with Google Sheets integration and OpenAI-powered chat. Production deployment at https://houserenoai.onrender.com serves permit data from live Google Sheets to construction teams in North Carolina.

## 📚 Related Documentation
- **[API_DOCUMENTATION.md](../API_DOCUMENTATION.md)** - Complete endpoint reference with examples
- **[TROUBLESHOOTING.md](../TROUBLESHOOTING.md)** - Debug procedures and solutions
- **[GC_Permit_Compliance_Schema.json](../../../GC_Permit_Compliance_Schema.json)** - 12-sheet Google Sheets data model
- **[DEPLOYMENT.md](../DEPLOYMENT.md)** - Production deployment and monitoring
- **[README.md](../README.md)** - Project overview and quick start guide

## 🧠 Core Architecture

### Service Layer Pattern
- **`app/services/google_service.py`**: Singleton Google Sheets/Drive API client with Base64 credential handling
- **`app/services/openai_service.py`**: GPT-4o chat service with construction domain prompts
- **`app/routes/`**: FastAPI routers that bridge services with REST endpoints

### Critical Initialization Flow
```python
# Startup sequence (app/main.py):
1. Decode GOOGLE_SERVICE_ACCOUNT_BASE64 → service-account.json file
2. Initialize GoogleService singleton with proper error handling
3. Mount chat/permits routers with service dependency injection
```

### Data Schema (GC_Permit_Compliance_Schema.json)
12-sheet Google Sheets structure with relational IDs:
- **Permits** (Project ID → Projects.Project ID)
- **Projects** (Client ID → Clients.Client ID) 
- **Site Visits, Subcontractors, Documents** (Project ID relations)

## 🔧 Development Workflow

### Environment Setup
```bash
# Required environment variables
GOOGLE_SERVICE_ACCOUNT_BASE64=<base64-encoded-service-account-json>
SHEET_ID=1BvDHl8XS9p7eKl4Q8F2wJ3mR5nT6uY9vI0pA7sS8dF1gH
OPENAI_API_KEY=sk-proj-...
PORT=10000  # Render requirement
```

### Local Development
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Testing Key Endpoints
```bash
curl localhost:8000/health                    # Service status
curl localhost:8000/debug/                   # Google service diagnostics  
curl localhost:8000/v1/permits/              # Live permit data
curl -X POST localhost:8000/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How many permits are approved?"}'
```

## 🎯 Project-Specific Patterns

### Google Service Error Handling
```python
# Never fail fast on Google init - allow service to start
try:
    self.credentials = service_account.Credentials.from_service_account_file(...)
    self.sheets_service = build("sheets", "v4", credentials=self.credentials)
    logger.info("Google services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize: {e}")
    # Don't raise - log and continue, implement lazy re-initialization
    self._initialized = False

# Lazy re-initialization pattern for resilience
def _ensure_initialized(self):
    if not self._initialized or not self.sheets_service:
        logger.info("Re-initializing Google services...")
        self._initialize_services()
```

### Base64 Credential Management (Render deployment)
```python
# app/main.py startup_event - handles credential corruption
if service_account_base64:
    decoded_json = base64.b64decode(service_account_base64).decode('utf-8')
    credentials_data = json.loads(decoded_json)
    # Fix private key newlines if double-escaped
    if '\\n' in credentials_data['private_key']:
        credentials_data['private_key'] = credentials_data['private_key'].replace('\\n', '\n')
```

**🔒 Security Note**: Base64 credentials MUST be injected via environment variables only. Never commit encoded credentials to source control, even if Base64 encoded. Use `GOOGLE_SERVICE_ACCOUNT_BASE64` environment variable in production.

### AI Context Injection Pattern
```python
# app/routes/chat.py - dynamic context loading
if any(keyword in message.lower() for keyword in ['permit', 'project', 'client']):
    permits = await google_service.get_permits_data()
    projects = await google_service.get_projects_data()
    clients = await google_service.get_clients_data()
    
    context.update({
        'permits_count': len(permits),
        'projects_count': len(projects), 
        'clients_count': len(clients),
        'recent_permits': permits[:5] if permits else [],
        'recent_projects': projects[:5] if projects else []
    })
```

### Construction Domain Prompts (openai_service.py)
```python
# System prompt template for maintaining construction terminology consistency
system_prompt = """
You are the AI assistant for House Renovators LLC, a North Carolina licensed General Contractor.

Your role is to help with:
- Permit management and tracking
- Project status updates
- Inspection scheduling and results  
- Compliance with NC building codes
- Team communication and coordination

Always provide accurate, professional responses related to construction, permits, and project management.
When you need to update data or perform actions, clearly indicate what function calls are needed.

Use construction industry terminology:
- "Permit approval" not "permit acceptance"
- "Inspection scheduled" not "meeting planned"
- "Code compliance" not "rule following"
- "Subcontractor" not "vendor"
- "Site visit" not "location check"
"""

# Context message format for permit data
if context:
    context_message = f"""Current permit context:
    - Total permits: {context.get('permits_count', 0)}
    - Recent permits: {context.get('recent_permits', [])}
    - Project status: {context.get('project_summary', 'Not available')}
    - Last updated: {context.get('last_sync', 'Unknown')}"""
```

## 📊 Data Flow Architecture

### Request → Service → Sheets → AI Response
1. **FastAPI Router** receives request (`/v1/chat/` or `/v1/permits/`)
2. **Google Service** queries live Google Sheets via API
3. **OpenAI Service** processes data with construction-specific prompts
4. **Structured Response** returns permit insights to frontend

### Permit Data Pipeline
```python
# Sheets range → Python dict conversion (google_service.py)
data = await self.read_sheet_data('Permits!A1:Z1000')
headers = data[0]  # First row contains column names
permits = [dict(zip(headers, row)) for row in data[1:]]
```

## 🚀 Deployment Architecture

### Render.com Production
- **Auto-deploy**: Git push to main → Render build
- **Health monitoring**: `/health` and `/debug/` endpoints
- **Environment**: Python 3.11, 512MB RAM, Oregon region
- **Build command**: `pip install -r requirements.txt`
- **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`

### Critical Dependencies
```python
# requirements.txt - pinned versions for stability
fastapi==0.103.0      # API framework
openai==1.51.0        # GPT-4o integration
google-api-python-client==2.108.0  # Sheets/Drive APIs
uvicorn[standard]==0.23.0  # ASGI server
```

## ⚡ Performance Considerations

### Google API Quotas
- **100 requests/100 seconds/user** limit
- Use data caching for repeated permit queries
- Batch sheet operations when possible

### Memory Management
- Limit permit data samples in AI context (`permits[:5]`)
- Stream large responses for permit listings
- Monitor Render memory usage (512MB limit)

### Error Recovery Patterns
```python
# Service availability checks in routes
def get_google_service():
    if not google_service_module.google_service:
        raise HTTPException(status_code=503, detail="Google service not initialized")
    return google_service_module.google_service
```

## 🔍 Debugging Workflows

### Service Initialization Issues
1. Check `/debug/` endpoint for credential status
2. Verify Base64 decoding in Render logs
3. Test with local `service-account.json` file

### Google Sheets Connection
```python
# Test sheet access manually
from app.services.google_service import google_service
data = await google_service.read_sheet_data('A1:A1')
```

### AI Response Quality
- Monitor OpenAI token usage with permit context
- Test construction-specific prompts in `/v1/chat/`
- Validate response JSON structure for analysis endpoints

## 📝 Code Conventions

### Async/Await Usage
All service methods are async for FastAPI compatibility, even when not doing I/O

### Logging Strategy
```python
logger.info(f"Retrieved {len(permits)} permits")  # Success states
logger.error(f"Failed to initialize: {e}")        # Error conditions
logger.warning("Chat webhook URL not configured") # Missing config
```

### Error Propagation
- Services log errors but don't raise on initialization failures
- Routes catch service exceptions and convert to HTTP errors
- Global exception handler for unhandled errors

## 🎯 When Contributing

1. **Test with live data**: Use production `/debug/` endpoint to verify Google Sheets connectivity
2. **Validate AI responses**: Construction terminology and NC building code references
3. **Check documentation**: Update API_DOCUMENTATION.md for new endpoints
4. **Monitor performance**: Render dashboard for memory/CPU usage after changes