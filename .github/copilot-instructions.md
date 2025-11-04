# House Renovators AI Portal - AI Agent Instructions

**Version**: 1.0.0  
**Last Updated**: November 3, 2025  
**Schema Version**: GC_Permit_Compliance_Schema.json (12-sheet structure)  
**Production Status**: Live at https://houserenoai.onrender.com

## 🏗️ Project Overview
FastAPI-based AI portal for construction permit management with Google Sheets integration and OpenAI-powered chat. Production deployment at https://houserenoai.onrender.com serves permit data from live Google Sheets to construction teams in North Carolina.

## 📚 Related Documentation
- **[WORKFLOW_GUIDE.md](../../../WORKFLOW_GUIDE.md)** - Daily development workflow and deployment procedures
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

### AI Context Injection Pattern (UPDATED Nov 3, 2025)
```python
# app/routes/chat.py - ALWAYS loads comprehensive context
# Changed from keyword-based conditional to full data loading
permits = await google_service.get_permits_data()
projects = await google_service.get_projects_data()
clients = await google_service.get_clients_data()

# Extract ID lists for quick validation
client_ids = [c.get('Client ID') for c in clients if c.get('Client ID')]
project_ids = [p.get('Project ID') for p in projects if p.get('Project ID')]
permit_ids = [p.get('Permit ID') for p in permits if p.get('Permit ID')]

context.update({
    # Counts
    'permits_count': len(permits),
    'projects_count': len(projects),
    'clients_count': len(clients),
    
    # ID Lists for validation
    'client_ids': client_ids,
    'project_ids': project_ids,
    'permit_ids': permit_ids,
    
    # Full data arrays (AI has access to EVERYTHING)
    'all_permits': permits,
    'all_projects': projects,
    'all_clients': clients,
    
    # Grouped by status for quick filtering
    'permits_by_status': _group_by_field(permits, 'Permit Status'),
    'projects_by_status': _group_by_field(projects, 'Status'),
    'clients_by_status': _group_by_field(clients, 'Status'),
    
    # Client summary for easy lookup
    'clients_summary': [
        {
            'Client ID': c.get('Client ID'),
            'Name': c.get('Name'),
            'Status': c.get('Status'),
            'Address': c.get('Address'),
            'Phone': c.get('Phone Number'),
            'Email': c.get('Email')
        } for c in clients
    ]
})
```

**Key Changes (Nov 3, 2025):**
- ✅ Removed keyword-based conditional loading
- ✅ ALWAYS fetches comprehensive data
- ✅ Added explicit ID lists for AI validation
- ✅ Added client summaries for quick lookup
- ✅ Added status groupings for filtering
- ✅ AI now has access to ALL 12 sheets worth of data

### Construction Domain Prompts (openai_service.py) - ENHANCED Nov 3, 2025
```python
# System prompt - comprehensive with formatting rules
system_prompt = """
You are an advanced AI assistant for House Renovators LLC, a North Carolina licensed General Contractor.

You have FULL ACCESS to comprehensive project data including:
- All client information (names, addresses, status, roles, contacts)
- All project details (addresses, costs, timelines, scope of work)
- All permit records (numbers, statuses, submission dates, approvals)
- Site visits, subcontractors, documents, tasks, and payments
- Jurisdiction information and inspector contacts
- Construction phase tracking with images

YOUR CAPABILITIES:
✅ Answer ANY question about clients, projects, or permits
✅ Search and filter data by any field (status, date, location, etc.)
✅ Calculate totals, averages, and statistics
✅ Track timelines and identify delays
✅ Identify missing data or incomplete records
✅ Cross-reference data between sheets (clients → projects → permits)
✅ Provide detailed analysis and recommendations
✅ Generate reports and summaries

CRITICAL FORMATTING RULES:
🎯 ALWAYS format responses in clean, readable markdown
🎯 Use proper lists with line breaks between items
🎯 Use headers (##, ###) to organize sections
🎯 Use tables for comparisons or multiple data points
🎯 Use bold (**text**) for important fields like names, addresses, statuses
🎯 NEVER dump raw data or concatenate fields without formatting
🎯 Group related information under clear headings
🎯 Add blank lines between sections for readability

RESPONSE GUIDELINES:
- Be comprehensive and data-driven in your answers
- If asked about specific data, search through ALL available records
- Provide exact counts, dates, and values when available
- Cross-reference related information (e.g., client → their projects → permit status)
- Highlight issues or incomplete data proactively
- Use professional construction industry terminology
- ALWAYS format lists with proper line breaks and structure

DATA ACCESS:
You receive the complete dataset in the context. Search through it thoroughly to answer questions.
Don't say "I don't have access" - the data is provided to you in the context.
"""

# Context message format - structured with clear sections
if context:
    context_parts = []
    
    # Add counts summary
    if 'clients_count' in context:
        context_parts.append(f"Total Clients: {context['clients_count']}")
    if 'projects_count' in context:
        context_parts.append(f"Total Projects: {context['projects_count']}")
    if 'permits_count' in context:
        context_parts.append(f"Total Permits: {context['permits_count']}")
    
    # Add available IDs
    if 'client_ids' in context and context['client_ids']:
        context_parts.append(f"\nAvailable Client IDs: {', '.join(context['client_ids'][:20])}")
    
    # Add clients summary
    if 'clients_summary' in context:
        context_parts.append("\n\n=== CLIENTS DATA ===")
        for client in context['clients_summary'][:50]:
            context_parts.append(
                f"\nClient ID: {client.get('Client ID')}"
                f"\n  Name: {client.get('Name')}"
                f"\n  Status: {client.get('Status')}"
                f"\n  Address: {client.get('Address')}"
            )
    
    # Add full data arrays for detailed queries
    if 'all_clients' in context:
        context_parts.append(f"\n\n=== FULL CLIENT RECORDS ===")
        context_parts.append(str(context['all_clients']))
    
    context_message = "\n".join(context_parts)
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