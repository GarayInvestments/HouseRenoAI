# House Renovators AI Portal - Copilot Instructions

## ⚠️ CRITICAL: Server Terminal Management
**Backend and Frontend servers MUST run in DEDICATED terminals that are BLOCKED from other commands**
- **NEVER run commands in a terminal that's running a server** - it will kill the server process
- **Always open a NEW terminal** for git, testing, logs, or any other commands
- **Pattern**: Terminal 1 = Backend (blocked), Terminal 2 = Frontend (blocked), Terminal 3+ = Commands
- If you only have server terminals available, open Terminal 3 before running any command

---

## ⚡ Quick Reference: Common Tasks

### When Asked to "Test Chat"
1. **Read test procedures**: `docs/guides/CHAT_TESTING_SOP.md` (6 standard tests, log patterns, troubleshooting)
2. **Use test scripts**: `scripts/testing/chat-tests/test_sync_production.py` or similar
3. **Check Render logs**: `render logs -r srv-d44ak76uk2gs73a3psig --limit 50 --confirm -o text`
4. **Look for patterns**: `[METRICS]`, `Smart context loading:`, error traces
5. **Verify in Sheets**: Check if data actually updated (QB sync, client data, etc.)

### When Adding New AI Function
1. **Add function handler**: `app/handlers/ai_functions.py` (handle_* pattern)
2. **Register in FUNCTION_HANDLERS**: Same file, dictionary at bottom
3. **Add OpenAI definition**: `app/services/openai_service.py` in `tools` array
4. **Update context loading**: `app/utils/context_builder.py` if needs new data source
5. **Test via chat**: Use test script from `scripts/testing/chat-tests/`
6. **Deploy and verify logs**: Check Render for execution traces

### When Deploying Changes
1. **Commit with clear message**: `git commit -m "Feature: ..." or "Fix: ..."`
2. **Push to main**: `git push origin main` (auto-deploys to Render + Cloudflare)
3. **Monitor deployment**: `render services list` then check service status
4. **Watch logs**: `render logs -r srv-d44ak76uk2gs73a3psig --tail --confirm`
5. **Test endpoint**: Run relevant test from `scripts/testing/chat-tests/`

### When Investigating Bugs
1. **Check recent logs**: `render logs -r srv-d44ak76uk2gs73a3psig --limit 200 --confirm -o text`
2. **Search for errors**: Pipe through `Select-String -Pattern "ERROR|CRITICAL|Exception"`
3. **Review context loading**: Look for `Smart context loading:` to verify data sources
4. **Check function execution**: Search for function name in logs
5. **Verify data in Sheets**: Ensure Google Sheets has expected data/columns
6. **Reference docs**: `docs/guides/TROUBLESHOOTING.md` for common issues

### When Setting Up New Machine
1. **Follow setup guide**: `docs/setup/SETUP_GUIDE.md` (comprehensive, covers all steps)
2. **Quick start**: `docs/setup/SETUP_NEW_MACHINE.md` (streamlined version)
3. **Environment vars**: `docs/setup/SETUP_QUICK_REFERENCE.md` (all required vars)
4. **Secrets setup**: `docs/setup/GIT_SECRET_SETUP.md` (GPG-based encryption)

### When Working with QuickBooks
1. **Complete reference**: `docs/guides/QUICKBOOKS_GUIDE.md` (OAuth2, API, sync, troubleshooting)
2. **Check auth status**: GET `/v1/quickbooks/status`
3. **Connect if needed**: Navigate to `/v1/quickbooks/connect`
4. **Test operations**: `scripts/testing/chat-tests/test_quickbooks_comprehensive.py`

### When Updating Documentation
1. **Check category**: Essential guides vs reference vs config
2. **Update copilot instructions**: If affects common workflows or patterns
3. **Update README.md**: If changing doc structure or adding new guides
4. **Run reorganization script**: `scripts/docs-management/reorganize-docs.ps1` if merging/archiving

---

## 🏗️ Architecture Overview

**Multi-Cloud Full-Stack App**: FastAPI backend (Render) + React PWA frontend (Cloudflare Pages) + Google Sheets data layer

### Key Components
- **Backend** (`app/`): FastAPI with async routes in `routes/`, services in `services/`
- **Frontend** (`frontend/src/`): React 19 + Vite, Zustand for state, pages in `pages/`
- **Data Source**: Google Sheets API (not a database) - all data operations are async API calls
- **Deployments**: Backend auto-deploys to Render, frontend to Cloudflare Pages on `main` push

## 🔑 Critical Patterns

### Backend Service Initialization (app/main.py)
```python
# Services initialize on startup from env vars or files
# GOOGLE_SERVICE_ACCOUNT_BASE64 → decoded → service-account.json
# google_service is a module-level singleton in services/google_service.py
```
**Why**: Render doesn't persist files, so credentials load from env vars on every cold start.

### Authentication Pattern (JWT)
```python
# Protected routes use get_current_user dependency
from app.routes.auth import get_current_user

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    # current_user contains: {"email": "...", "name": "...", "role": "..."}
    return {"message": f"Hello {current_user['name']}"}

# Frontend must send: Authorization: Bearer <token>
# Tokens expire after 7 days
# JWTAuthMiddleware automatically protects all routes except PUBLIC_ROUTES
```
**Why**: Centralized auth via middleware + dependency injection. Users stored in Google Sheets `Users` tab.

### API Route Structure
```python
# All routes follow this pattern:
from app.services import google_service_module

def get_google_service():
    """Helper with proper error handling"""
    if not google_service_module.google_service or google_service_module.google_service is None:
        raise HTTPException(status_code=503, detail="Google service not initialized")
    return google_service_module.google_service

@router.get("/")
async def get_data():
    google_service = get_google_service()
    data = await google_service.get_sheet_data()
    return data
```
**Why**: Ensures service is initialized before use; consistent error handling across routes.

### QuickBooks Integration Pattern
```python
# QuickBooks OAuth2 flow (production approved)
from app.services.quickbooks_service import quickbooks_service

# 1. Check authentication status
if not quickbooks_service.is_authenticated():
    # Redirect to /v1/quickbooks/connect for OAuth flow
    
# 2. Tokens stored in Google Sheets (QB_Tokens tab)
# 3. Auto-refresh when expired (60-day refresh token)
# 4. Supports sandbox + production environments

# Common operations:
customers = await quickbooks_service.get_customers()
invoices = await quickbooks_service.get_invoices()
invoice = await quickbooks_service.create_invoice(customer_id, line_items)
```
**Why**: OAuth tokens persist across deployments via Google Sheets. Service auto-refreshes expired access tokens.

### Smart Context Loading (Performance Critical)
```python
# context_builder.py intelligently loads ONLY needed data
from app.utils.context_builder import build_context

context = await build_context(
    message=user_message,
    google_service=google_service,
    qb_service=quickbooks_service,
    session_memory=memory_manager.get_all(session_id)
)

# Examples:
# "Show me Temple project" → Loads Sheets only (no QB API calls)
# "Create invoice for Temple" → Loads Sheets + QB
# "Hello" → Loads nothing (returns {'none'})

# Performance: 80% fewer API calls, 60% less tokens
```
**Why**: Keyword analysis determines required data sources before making API calls. Dramatically reduces latency and costs.

### Session Memory Pattern
```python
# memory_manager.py provides TTL-based session storage
from app.memory.memory_manager import memory_manager

# Store context during conversation
memory_manager.set(session_id, "last_client_id", "123", ttl_minutes=10)

# Retrieve in subsequent messages
last_client = memory_manager.get(session_id, "last_client_id")

# Automatic cleanup after TTL expires (default: 10 minutes)
```
**Why**: Maintains conversational context without database. User says "show me their invoices" after viewing a client - memory remembers which client.

### Frontend State Management (Zustand)
```javascript
// State lives in stores/appStore.js - single global store
// Navigation pattern: useAppStore((state) => state.navigateToClient(id))
// Sets currentView + currentClientId, App.jsx renders based on these
```
**Why**: Simple, no routing library - view changes via state, enabling browser back/forward support.

### Field Name Handling (CRITICAL)
```javascript
// Google Sheets columns vary: 'Full Name' vs 'Client Name', 'Client ID' vs 'ID'
// ALWAYS check multiple field variations:
const name = client['Full Name'] || client['Client Name'] || 'Unnamed Client';
const id = client['Client ID'] || client['ID'] || index;
```
**Why**: Sheet structure evolved; multiple fallbacks prevent "Unnamed" or blank data.

## 🛠️ Development Workflow

### Running Locally
```powershell
# Backend (Terminal 1) - MUST activate venv first
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Runs on http://localhost:8000

# Frontend (Terminal 2) - separate terminal
cd frontend
npm run dev
# Runs on http://localhost:5173

# Frontend connects to PRODUCTION backend by default (see frontend/.env)
VITE_API_URL=https://houserenoai.onrender.com
```

**⚠️ CRITICAL: Server Terminal Management**
- **Backend and Frontend servers MUST run in DEDICATED terminals**
- **NEVER run other commands in a terminal that's running a server**
- Running commands in server terminals will kill the server process
- **Always open a NEW terminal** for git commands, testing, log checks, etc.
- If you need to run a command and only have server terminals, open Terminal 3+
- Pattern: Terminal 1 = Backend (blocked), Terminal 2 = Frontend (blocked), Terminal 3+ = Commands

**Note**: venv is at root level, not in a backend/ subdirectory. Most API endpoints require JWT authentication (send `Authorization: Bearer <token>` header).

### Environment Files
- **Backend** (`.env` at root): `SHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_FILE`, `OPENAI_API_KEY`
- **Frontend** (`frontend/.env`): `VITE_API_URL` (defaults to production Render URL)

### Deployment
- **Push to `main`** → Auto-deploys backend (Render) + frontend (Cloudflare Pages)
- **No manual build steps** - CI/CD handles everything
- **Backend credentials**: Set in Render dashboard as `GOOGLE_SERVICE_ACCOUNT_BASE64`

## 🐛 Common Issues & Solutions

### "Unnamed Client" / Missing Data
→ Check field name variations (see Field Name Handling above). Add console.log to see actual keys from API.

### "Google service not initialized"
→ Backend needs `.env` with `GOOGLE_SERVICE_ACCOUNT_FILE=config/house-renovators-credentials.json` and `SHEET_ID=...`
→ In production, Render uses `GOOGLE_SERVICE_ACCOUNT_BASE64` env var

### CORS errors from frontend
→ Backend `app/config.py` has explicit CORS origins. Add new domains there + in `app/main.py` CORSMiddleware.

### Objects rendering in React
→ Use `typeof value === 'object' ? JSON.stringify(value) : value` before rendering unknown data

## 📁 Key Files to Reference

### Backend
- **API structure**: `app/main.py` (startup logic), `app/routes/` (all endpoints)
- **Authentication**: `app/routes/auth.py` (JWT endpoints), `app/middleware/auth_middleware.py` (protection)
- **Services**: `app/services/google_service.py` (Sheets), `app/services/quickbooks_service.py` (QB OAuth), `app/services/auth_service.py` (JWT + bcrypt)
- **Smart loading**: `app/utils/context_builder.py` (80% API reduction logic)
- **Session memory**: `app/memory/memory_manager.py` (TTL-based context storage)
- **Config**: `app/config.py` (all env vars + CORS origins)

### Frontend
- **State management**: `frontend/src/stores/appStore.js` (navigation + global state)
- **Component patterns**: `frontend/src/pages/ClientDetails.jsx` (shows field fallbacks + data handling)

### Google Sheets API Access
- **Backend Service** (`google_service`): Use in API routes, chat functions (requires FastAPI context)
- **Direct API Access**: Use in standalone scripts (`scripts/setup_*.py`, migrations, admin tools)
- **Complete Guide**: `docs/GOOGLE_SHEETS_API_ACCESS.md` (when to use each approach, patterns, troubleshooting)
### Available Routes
- `/v1/auth/*` - Login, register, token refresh, user info
- `/v1/chat` - AI chat with smart context loading
- `/v1/clients` - Client data from Google Sheets
- `/v1/projects` - Project management
- `/v1/permits` - Permit tracking
- `/v1/documents` - Document upload/management
- `/v1/quickbooks/*` - OAuth flow, customers, invoices, estimates, bills
- `/v1/payments` - Payment tracking and QB sync (NEW: Nov 10, 2025)

## 🔐 Secrets Management

### Git-Secret (Primary Method)
Secrets are encrypted using GPG and committed to Git as `*.secret` files.

**Daily Workflow:**
```powershell
# After modifying .env or credentials
.\scripts\git-secret-wrapper.ps1 -Action hide

# Commit encrypted files
git add .env.secret config/*.secret
git commit -m "Update secrets"
git push

# On new machine or after git pull
.\scripts\git-secret-wrapper.ps1 -Action reveal
```

**Adding Team Members:**
```powershell
# Team member shares their GPG public key fingerprint
.\scripts\git-secret-wrapper.ps1 -Action tell -Email "teammate@example.com"

# Re-encrypt files
.\scripts\git-secret-wrapper.ps1 -Action hide
git add *.secret
git commit -m "Add teammate to secrets"
```

**Files Tracked:**
- `.env` → `.env.secret` (encrypted)
- `config/house-renovators-credentials.json` → `.json.secret` (encrypted)

**Alternative (No GPG):**
```powershell
# PowerShell encryption (password-based)
.\scripts\encrypt-secrets.ps1 -Action encrypt  # Create .encrypted files
.\scripts\encrypt-secrets.ps1 -Action decrypt  # Restore originals
```

## 🎯 Project-Specific Conventions

1. **No TypeScript**: Stick to JavaScript for frontend (existing codebase decision)
2. **Inline styles over CSS**: Many components use React inline styles for specific layouts
3. **PowerShell scripts**: DevOps uses `.ps1` files (Windows-first environment)
4. **Google Sheets as database**: All CRUD operations go through Google Sheets API, no SQL
5. **Module singleton pattern**: Services like `google_service` are module-level instances, not class instantiation per request
6. **API versioning**: All routes prefixed with `/v1/` (see `settings.API_VERSION`)
7. **JWT everywhere**: All routes protected by default except PUBLIC_ROUTES in `JWTAuthMiddleware`
8. **Smart context loading**: ALWAYS use `context_builder.py` for chat - never load all data blindly
9. **Session-based memory**: Use `memory_manager` for conversational context (10-min TTL)
10. **Structured logging**: Use `logger.info("[METRICS] ...")` for performance tracking in Render logs

## 📊 Logging & Monitoring

### Backend Logging Pattern
```python
import logging
logger = logging.getLogger(__name__)

# Performance metrics (visible in Render logs)
logger.info(f"[METRICS] API call took {duration}ms, tokens: {token_count}")

# Context loading
logger.info(f"Smart context loading: {contexts} for message: '{message[:50]}...'")

# Errors with context
logger.error(f"Google Sheets error: {e}", exc_info=True)
```

### Viewing Logs
```powershell
# Render CLI (CORRECT SYNTAX)
# Service ID: srv-d44ak76uk2gs73a3psig
render logs -r srv-d44ak76uk2gs73a3psig --limit 200 --confirm -o text

# Stream live logs
render logs -r srv-d44ak76uk2gs73a3psig --tail --confirm

# Search for specific text
render logs -r srv-d44ak76uk2gs73a3psig --text "error,warning" --limit 100 --confirm -o text

# Programmatic access via Render API
# See docs/RENDER_API_DEPLOYMENT_GUIDE.md and docs/RENDER_LOGS_GUIDE.md
# See docs/LOGGING_SECURITY.md for security monitoring patterns
```
**Note**: Use `-r` (resources) flag with service ID, NOT `-s` (service name). Old CLI syntax (`-s`) no longer works.

**What to look for**:
- `[METRICS]` prefix = Performance data
- `Smart context loading:` = Which data sources were used
- `Google service not initialized` = Missing env vars
- `Invalid or expired token` = JWT auth issues
- `QuickBooks not authenticated` = Need to run OAuth flow

## 🚀 When Adding Features

- **New backend route**: Create in `app/routes/`, add auth with `Depends(get_current_user)` if protected, register in `app/main.py`
- **New frontend page**: Add to `pages/`, update `App.jsx` switch statement, add navigation in `appStore.js`
- **New Google Sheets column**: Update field fallbacks in frontend components to handle old/new column names
- **New data source for chat**: Add keywords to `context_builder.py` → add loading function → update `build_context()`
- **New QuickBooks operation**: Add method to `quickbooks_service.py`, ensure `is_authenticated()` check, handle token refresh
- **Environment variable**: Add to `app/config.py`, document in README, set in Render/Cloudflare dashboard
- **Performance logging**: Add `logger.info("[METRICS] ...")` for operations > 100ms or using external APIs

## 🧪 Testing Patterns

### Testing Protected Endpoints
```powershell
# 1. Login to get token
$response = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"email":"admin@example.com","password":"admin123"}'

$token = $response.access_token

# 2. Call protected endpoint
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/v1/clients" -Headers $headers
```

### Testing QuickBooks Integration
```powershell
# 1. Check auth status
curl http://localhost:8000/v1/quickbooks/status

# 2. If not authenticated, connect (opens browser)
# Navigate to: http://localhost:8000/v1/quickbooks/connect

# 3. Test operations
curl http://localhost:8000/v1/quickbooks/customers -H "Authorization: Bearer $token"
```

### Testing Smart Context Loading
```python
# Look for these log messages in terminal:
# "Smart context loading: {'sheets'} for message: 'Show Temple project'..."
# "Smart context loading: {'sheets', 'quickbooks'} for message: 'Invoice for Temple'..."
# "Smart context loading: {'none'} for message: 'Hello'..."
```

**For comprehensive testing workflows, see:**
- `docs/guides/CHAT_TESTING_SOP.md` - Standard testing procedures for chat functionality
- `scripts/testing/chat-tests/` - Test scripts for various features

## 📚 Documentation Reference

### Essential Guides (Read These First)
- **`docs/guides/QUICKBOOKS_GUIDE.md`** - Complete QuickBooks OAuth2, API usage, sync features
- **`docs/setup/SETUP_GUIDE.md`** - Dev environment setup, GitHub Actions, secrets management
- **`docs/guides/CHAT_TESTING_SOP.md`** - Testing chat features, log monitoring, troubleshooting
- **`docs/guides/API_DOCUMENTATION.md`** - Complete API reference with examples
- **`docs/guides/WORKFLOW_GUIDE.md`** - Daily development workflow and git patterns

### Configuration & Setup
- **`docs/setup/GIT_SECRET_SETUP.md`** - GPG-based secrets encryption
- **`docs/setup/SETUP_NEW_MACHINE.md`** - Quick setup for new developers
- **`docs/setup/SETUP_QUICK_REFERENCE.md`** - Environment variables and quick commands

### Deployment & Operations
- **`docs/deployment/DEPLOYMENT.md`** - Render and Cloudflare deployment process
- **`docs/deployment/RENDER_API_DEPLOYMENT_GUIDE.md`** - Programmatic deployments via Render API
- **`docs/deployment/RENDER_LOGS_GUIDE.md`** - Log access and monitoring
- **`docs/technical/LOGGING_SECURITY.md`** - Security logging patterns and monitoring

### Reference & Troubleshooting
- **`docs/guides/TROUBLESHOOTING.md`** - Common issues and solutions
- **`docs/guides/FIELD_MAPPING.md`** - Google Sheets column mappings
- **`docs/technical/GOOGLE_SHEETS_STRUCTURE.md`** - Sheets structure and field definitions
- **`docs/technical/GOOGLE_SHEETS_API_ACCESS.md`** - API access patterns and best practices
- **`docs/technical/BASELINE_METRICS.md`** - Performance benchmarks

### Scripts Organization
- **`scripts/testing/chat-tests/`** - All chat and integration tests
- **`scripts/docs-management/`** - Documentation maintenance tools
- **`scripts/setup/`** - Environment setup automation


