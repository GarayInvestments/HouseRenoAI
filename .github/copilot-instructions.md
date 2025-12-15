# House Renovators AI Portal - Copilot Instructions

## 🏁 SESSION-END CHECKPOINT (CHECK BEFORE EVERY RESPONSE)

**BEFORE saying "done", "complete", "that should work", or ending your turn:**

### Mandatory Documentation Check

```
✅ Did I complete 3+ file edits? → Suggest IMPLEMENTATION_TRACKER.md update
✅ Did I fix a blocking bug? → Suggest IMPLEMENTATION_TRACKER.md update  
✅ Did I finish a migration? → Suggest IMPLEMENTATION_TRACKER.md update
✅ Did I create new API endpoints? → Suggest API_DOCUMENTATION.md update
✅ Did testing pass after failures? → Suggest IMPLEMENTATION_TRACKER.md update
✅ Did user say "works", "good", "testing passes"? → Offer documentation NOW
```

### Required Response Pattern

**When ANY checkbox above is ✅:**

```
✅ Completed [specific feature/fix] (Dec 15 11:45 PM EST).
Should I update IMPLEMENTATION_TRACKER.md?
```

**NEVER say work is "complete" without offering documentation.**

---

## ⚡ CODE QUALITY STANDARD (READ THIS FIRST)

**CRITICAL**: Accuracy > Speed

When writing scripts or creating files:

### 1. Verify Before Writing
- ✅ Check existing patterns in codebase
- ✅ Review similar files for conventions
- ✅ Validate logic mentally before coding
- ✅ Search for existing implementations

### 2. Common Mistake Areas (Extra Caution Required)
- **File paths**: Use absolute paths, verify directories exist
- **Shell syntax**: PowerShell (not bash) - use `;` not `&&`, use `-eq` not `==`
- **Import statements**: Verify module paths resolve
- **Database schema**: Check actual columns with `psql` before assuming
- **Pydantic models**: Match database types exactly (JSONB = `List[dict]` not `dict`)
- **Environment variables**: Verify exact names from `.env` or Fly secrets
- **Route protection**: Use `Depends(get_current_user)` from `auth_supabase.py`

### 3. Before Creating a File
- ✅ Search for existing similar files
- ✅ Check naming conventions in that directory
- ✅ Verify imports will resolve
- ✅ Confirm directory structure exists
- ✅ Review error-prone patterns in similar files

### 4. Take Time To
- ✅ Read error messages completely
- ✅ Check documentation when unsure
- ✅ Ask clarifying questions
- ✅ Verify assumptions with user
- ✅ Test logic mentally before writing

**Never rush. Get it right the first time.**

---

## 🚨 CRITICAL: Frontend API Patterns (MANDATORY)

**ALWAYS use the centralized API service. NEVER use direct `fetch()` calls.**

### ❌ FORBIDDEN Pattern (Causes Bugs)
```javascript
// DON'T DO THIS - Direct fetch with manual token handling
const response = await fetch('/v1/quickbooks/sync/cache/payments', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
  }
});
```

**Problems with this approach:**
1. **Relative URLs** resolve to Vite dev server (`localhost:5173`) not backend API (`localhost:8000`)
2. **Token storage** - `localStorage.getItem('supabase_token')` doesn't exist (tokens in Supabase session)
3. **Code duplication** - repeats auth logic that already exists in `api.js`
4. **No error handling** - missing retry logic, 401 refresh, etc.

### ✅ CORRECT Pattern (Use Existing API Service)

**Option 1: Use existing api.js methods**
```javascript
import api from '../lib/api';

// Use existing methods
const clients = await api.getClients();
const projects = await api.getProjects();
```

**Option 2: Extend api.js for new endpoints**
```javascript
// In api.js - Add new methods
async getPaymentsCache() {
  return this.request('/quickbooks/sync/cache/payments');
}

async syncPayments() {
  return this.request('/quickbooks/sync/payments', { method: 'POST' });
}

// In store - Use new methods
import api from '../lib/api';
const payments = await api.getPaymentsCache();
```

**Option 3: Use api.request() directly**
```javascript
import api from '../lib/api';

// Generic request method handles everything
const data = await api.request('/quickbooks/sync/cache/payments');
```

### Why api.js is Mandatory

**What it handles automatically:**
1. ✅ **Absolute URLs** - Uses `VITE_API_URL` environment variable
2. ✅ **Token retrieval** - Gets fresh token from `supabase.auth.getSession()`
3. ✅ **Token refresh** - Auto-retries on 401 with session refresh
4. ✅ **Error handling** - Consistent error formatting
5. ✅ **Logging** - Request/response tracking for debugging

**api.js token pattern (reference):**
```javascript
async getAuthToken() {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token; // ✅ Correct - from Supabase session
}
```

### Code Review Checklist (Before Committing)

When adding new API calls, verify:
- ✅ Using `api.js` service (not direct `fetch()`)
- ✅ No `localStorage.getItem('supabase_token')` anywhere
- ✅ No relative URLs like `/v1/...` (api.js handles this)
- ✅ Import exists: `import api from '../lib/api'`

### ESLint Rule (Recommended)

Add to `.eslintrc.js` to prevent direct fetch:
```javascript
rules: {
  'no-restricted-globals': ['error', {
    name: 'fetch',
    message: 'Use api.js service instead of direct fetch(). See copilot-instructions.md'
  }]
}
```

### Common Migration Pattern

If you find direct `fetch()` calls in stores:

**Before:**
```javascript
const response = await fetch('/v1/endpoint', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('supabase_token')}` }
});
const data = await response.json();
```

**After:**
```javascript
const data = await api.request('/endpoint');
```

**That's it.** 80% less code, 100% more reliable.

---

## 🎯 SYSTEM ARCHITECTURE TRUTH

**Deployment Platform**:
- Backend is deployed on **Fly.io** (`houserenovators-api.fly.dev`)
- Any Render references in this document exist only for **historical context** and must **not be used for new work**

**Authentication System**:
- Authentication is handled by **Supabase Auth** (hosted service)
- Backend validates Supabase-issued JWTs via `supabase_auth_service.py`
- Routes use `get_current_user` dependency from `app/routes/auth_supabase.py`
- **No auth middleware active** - protection happens at route level via `Depends(get_current_user)`
- Legacy custom JWT system exists in codebase but is **DISABLED** (auth.py commented out in main.py)

**Database**:
- PostgreSQL (Supabase) is the **primary and only** data store
- Google Sheets are **no longer used** for core application data
- Any Google Sheets references below are **historical unless explicitly stated**

**Required Tooling Prerequisites** (Verify Before Debugging):
1. **Fly CLI must be installed and functional**:
   ```powershell
   fly version
   ```
   If this fails: User must install Fly CLI or fix permissions before proceeding. No backend debugging should continue until resolved.

2. **Supabase Auth token must be present** for protected endpoints
3. **Backend health must be verified** before debugging endpoints:
   ```powershell
   fly status --app houserenovators-api
   ```

**Workflow Order** (Non-Negotiable):
1. Verify Fly CLI → 2. Verify Supabase Auth token → 3. Verify backend health → 4. Proceed with debugging

---

## 📘 CRITICAL: Documentation Governance (MUST READ FIRST)

**READ FIRST**: `docs/README.md` - Canonical documentation governance policy

**Enforcement Rules (Non-Negotiable)**:

When you want to add documentation:

1. **STOP** - Read `docs/README.md` first
2. **ASK**: Which folder does this belong in?
   - Current priorities → `roadmap/`
   - Active work & blockers → `operations/`
   - System design → `architecture/`
   - Business rules → `business/`
   - Debugging rationale → `audits/`
   - How-to guides → `guides/`
   - Setup instructions → `setup/`
   - Completed work → `history/`
3. **ASK**: Is there already a canonical document for this topic?
   - Check folder first
   - Prefer updating existing docs over creating new ones
4. **IF UNSURE**: Stop and ask the user

**Prohibited Actions**:
- ❌ Creating new status files (use `operations/IMPLEMENTATION_TRACKER.md`)
- ❌ Creating phase notes outside `operations/`
- ❌ Creating one-off debugging docs without approval
- ❌ Creating docs without checking governance policy first

**Required Actions**:
- ✅ Check `docs/README.md` before any documentation work
- ✅ Ask which folder if creating new doc
- ✅ Ask if canonical doc exists before creating
- ✅ Update existing docs instead of creating duplicates

**Why This Matters**: Documentation clarity > Documentation volume. A smaller, trusted docs set is always preferred.

---

## 📝 CRITICAL: Progress Tracking & Documentation Updates

**REQUIRED BEHAVIOR**: Proactively update `docs/operations/IMPLEMENTATION_TRACKER.md` after completing ANY work.

### Tracker Update Pattern with Timestamps

**Use EST timestamps** in format: `MMM DD h:mm AM/PM EST`

**Examples**:
```markdown
- [x] Implemented QuickBooks sync (Completed: Dec 13 3:45 PM EST)
- [ ] Add payment reconciliation (Started: Dec 13 2:30 PM EST)
- [x] Fixed CORS issue (Completed: Dec 12 11:20 PM EST)
```

**Tracker structure**:
```markdown
# Implementation Tracker

**Last Updated**: December 13, 2025 3:45 PM EST

## 🔴 Active Blockers
- [Blocker with discovery timestamp]

## 🟡 In Progress Now
- [ ] Task (Started: [timestamp])

## 🟢 Up Next
- [ ] Upcoming priorities

## ✅ Recently Completed (Last 48 Hours)
- [x] Task (Completed: [timestamp])
(Archive when 10+ items or major milestone completes)
```

### After Completing Work (NON-NEGOTIABLE)

**Immediately suggest**:
```
"✅ Completed [specific task] (Dec 13 3:45 PM EST). 
Should I update IMPLEMENTATION_TRACKER.md?"
```

### When to Update IMPLEMENTATION_TRACKER.md

✅ **ALWAYS update after**:
- Completing a task or subtask (add timestamp)
- Hitting a blocker (add discovery timestamp)
- Starting new work (add start timestamp)
- Major milestone completes (suggest archiving old items)

❌ **NEVER create separate status files**:
- No `PROGRESS_REPORT.md`
- No `STATUS_UPDATE.md`
- No `COMPLETION_SUMMARY.md`
- All progress goes in ONE place: `docs/operations/IMPLEMENTATION_TRACKER.md`

### Archive Triggers (Volume-Based, Not Time-Based)

**Suggest archiving when**:
- ✅ Major milestone/phase completes
- ✅ "Recently Completed" has 10+ items
- ✅ Tracker feels cluttered with old completions
- ✅ User requests cleanup

### Phase Completion File Standard (Strict)

**📁 Canonical Location**: `docs/history/PHASE_COMPLETIONS/` only

**🧱 Naming Format (Mandatory)**:
```
PHASE_<PHASE_CODE>_<SHORT_DESCRIPTION>_<YYYY_MM_DD>.md
```

**Examples**:
```
PHASE_D_INSPECTIONS_API_2025_12_13.md
PHASE_D_AUTH_MIGRATION_2025_12_10.md
PHASE_E_PAYMENTS_FEATURE_2025_11_10.md
```

**🔑 Rules (Non-Negotiable)**:

1. **Phase code is mandatory**
   - Must match roadmap phase exactly (PHASE_C, PHASE_D, PHASE_E, etc.)
   - ❌ `INSPECTIONS_COMPLETE.md`
   - ✅ `PHASE_D_INSPECTIONS_API_2025_12_13.md`

2. **Description is short, functional, uppercase**
   - 2-4 words max
   - What shipped, not how
   - ✅ `INSPECTIONS_API`, `AUTH_MIGRATION`, `QUICKBOOKS_SYNC`
   - ❌ `INSPECTIONS_FEATURE_FINAL_VERSION`

3. **Date = completion date**
   - Format: `YYYY_MM_DD`
   - Use date milestone was functionally complete
   - No timestamps in filenames (timestamps go inside file)

4. **One file = one milestone**
   - Not per commit, not per day, not per task list
   - Multiple milestones same day = multiple files

**📄 Internal File Structure (Required)**:
```markdown
# Phase D – Inspections API

**Completion Date**: December 13, 2025 (EST)  
**Phase**: D  
**Status**: ✅ Complete

---

## What Was Delivered
- /v1/inspections CRUD endpoints
- JSONB photos and deficiencies support
- Supabase-auth protected routes

---

## Key Decisions
- JSONB arrays used instead of relational tables
- Route-level auth enforcement only

---

## Files Touched (High-Level)
- app/routes/inspections.py
- app/db/models.py

---

## Follow-Ups (If Any)
- None
```

**🚦 Create Phase Completion File Only When**:
- Roadmap phase item is fully shipped
- Major subsystem is complete
- Migration is finished
- Feature crosses from "in progress" → "done forever"

**Never for**:
- Bug fixes
- Partial work
- Refactors without functional change

**After creating phase completion file**:
1. Remove completed items from `IMPLEMENTATION_TRACKER.md`
2. Tracker becomes forward-looking immediately

### Proactive Documentation Suggestions

**After major milestones (not every task), suggest**:

1. **New API endpoints** → "Update `docs/guides/API_DOCUMENTATION.md` with new routes?"
2. **Bug fixes** → "Add solution to `docs/guides/TROUBLESHOOTING.md`?"
3. **Architecture changes** → "Update `docs/architecture/[relevant].md`?"
4. **Setup changes** → "Update `docs/setup/SETUP_GUIDE.md` with new dependency/env var?"
5. **Completed features** → "Move design docs to `docs/history/archive/`?"
6. **Debugging discoveries** → "Document in `docs/audits/` as canonical reference?"

### Key Principle

**Always ask, never auto-create**. Make specific suggestions with exact file paths, but get approval before creating/updating docs.

---

## ⚠️ CRITICAL: Server Terminal Management
**READ FIRST**: `docs/guides/TERMINAL_MANAGEMENT.md` - Complete guide to preventing server shutdowns

**Quick Rules**:
- **Use `isBackground: true`** for ALL commands when servers are running - forces new terminal creation
- **Save terminal IDs** when starting servers - needed for `get_terminal_output()`
- **Pattern**: Terminal 1 = Backend (start once, never touch), Terminal 2 = Frontend (start once), Terminal 3+ = All other commands
- **Check server health**: `get_terminal_output(BACKEND_TERMINAL_ID)` before running tests
- **Root cause**: `run_in_terminal` without `isBackground: true` reuses terminals, killing background processes

---

## ⚡ Quick Reference: Common Tasks

### When Asked to "Test Chat"
1. **Read test procedures**: `docs/guides/CHAT_TESTING_SOP.md` (6 standard tests, log patterns, troubleshooting)
2. **Use test scripts**: `scripts/testing/chat-tests/test_sync_production.py` or similar
3. **Check Fly logs**: `fly logs --app houserenovators-api --follow`
4. **Look for patterns**: `[METRICS]`, `Smart context loading:`, error traces
5. **Verify in database**: Check if data actually updated (QB sync, client data, etc.)

### When Adding New AI Function
1. **Add function handler**: `app/handlers/ai_functions.py` (handle_* pattern)
2. **Register in FUNCTION_HANDLERS**: Same file, dictionary at bottom
3. **Add OpenAI definition**: `app/services/openai_service.py` in `tools` array
4. **Update context loading**: `app/utils/context_builder.py` if needs new data source
5. **Test via chat**: Use test script from `scripts/testing/chat-tests/`
6. **Deploy and verify logs**: Check Fly.io logs for execution traces

### When Deploying Changes
1. **Commit with clear message**: `git commit -m "Feature: ..." or "Fix: ..."`
2. **Push to main**: `git push origin main` (auto-deploys to Fly.io + Cloudflare)
3. **Monitor deployment**: `fly status --app houserenovators-api`
4. **Watch logs**: `fly logs --app houserenovators-api --follow`
5. **Test endpoint**: Run relevant test from `scripts/testing/chat-tests/`

### When Investigating Bugs
1. **Check recent logs**: `fly logs --app houserenovators-api | Select-Object -Last 200`
2. **Search for errors**: `fly logs --app houserenovators-api | Select-String "ERROR|CRITICAL|Exception"`
3. **Review context loading**: Look for `Smart context loading:` to verify data sources
4. **Check function execution**: Search for function name in logs
5. **Verify data in database**: Use `psql` to check PostgreSQL data/schema
6. **Reference docs**: `docs/guides/TROUBLESHOOTING.md` and `docs/audits/PYDANTIC_VALIDATION_DEBUGGING.md`

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
1. **Read governance policy**: `docs/README.md` (MANDATORY - check which folder, check for existing docs)
2. **Ask before creating**: Which folder? Is there a canonical doc already?
3. **Prefer updates**: Update existing docs instead of creating new ones
4. **If unsure**: Stop and ask the user

---

## 🏗️ Architecture Overview

**Multi-Cloud Full-Stack App**: FastAPI backend (Fly.io) + React PWA frontend (Cloudflare Pages) + PostgreSQL database (Supabase)

### Key Components
- **Backend** (`app/`): FastAPI with async routes in `routes/`, services in `services/`
- **Frontend** (`frontend/src/`): React 19 + Vite, Zustand for state, pages in `pages/`
- **Database**: PostgreSQL (Supabase) - all data operations via SQLAlchemy ORM with async
- **Auth**: Supabase Auth service (hosted authentication with JWT tokens)
- **Deployments**: Backend auto-deploys to Fly.io, frontend to Cloudflare Pages on `main` push

### Data Migration Status (Dec 13, 2025)
- ✅ **All Data Migrated to PostgreSQL**: Clients, Projects, Permits, Payments, Inspections, QuickBooks tokens
- ✅ **AI Chat Context**: Uses `db_service` via `context_builder.py`
- 🗑️ **Google Sheets**: Fully deprecated (removed from operational use)

## 🔑 Critical Patterns

### Authentication Pattern (Supabase Auth)
```python
# Protected routes use get_current_user dependency
from app.routes.auth_supabase import get_current_user
from app.db.models import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    # current_user is User model from database
    return {"message": f"Hello {current_user.full_name}"}

# Frontend must send: Authorization: Bearer <supabase_access_token>
# Backend validates Supabase-issued JWT via supabase_auth_service.verify_jwt()
# User identity comes from Supabase 'sub' claim mapped to app users table
# No middleware - protection via route dependencies
```
**Why**: Supabase Auth handles token issuance, refresh, and rotation. Backend validates JWTs using Supabase JWT secret and maps to app users. Users stored in PostgreSQL `users` table.

**Legacy Auth Note**: `app/routes/auth.py` and `app/services/auth_service.py` exist but are disabled (custom JWT with refresh tokens, blacklist). Only Supabase Auth is active.

**Auth System Documentation**:
- **Complete Reference**: `docs/architecture/AUTHENTICATION_MODEL.md` (endpoints, flows, security, troubleshooting)

### QuickBooks Integration Pattern
```python
# QuickBooks OAuth2 flow (production approved)
from app.services.quickbooks_service import quickbooks_service

# 1. Check authentication status
if not quickbooks_service.is_authenticated():
    # Redirect to /v1/quickbooks/connect for OAuth flow
    
# 2. Tokens stored in PostgreSQL (encrypted)
# 3. Auto-refresh when expired (60-day refresh token)
# 4. Supports sandbox + production environments

# Common operations:
customers = await quickbooks_service.get_customers()
invoices = await quickbooks_service.get_invoices()
invoice = await quickbooks_service.create_invoice(customer_id, line_items)
```
**Why**: OAuth tokens persist across deployments in PostgreSQL. Service auto-refreshes expired access tokens.

### Smart Context Loading (Performance Critical)
```python
# context_builder.py intelligently loads ONLY needed data
from app.utils.context_builder import build_context

context = await build_context(
    message=user_message,
    db_service=db_service,
    qb_service=quickbooks_service,
    session_memory=memory_manager.get_all(session_id)
)

# Examples:
# "Show me Temple project" → Loads PostgreSQL only (no QB API calls)
# "Create invoice for Temple" → Loads PostgreSQL + QB
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

# Frontend uses environment-based config (see frontend/.env)
# By default, local dev points to PRODUCTION backend on Fly.io
# Override in frontend/.env.local to point to local backend:
VITE_API_URL=https://houserenovators-api.fly.dev  # Production Fly.io backend (default)
# VITE_API_URL=http://localhost:8000  # Uncomment for local backend testing
VITE_ENV=development
```

### PostgreSQL Access (REQUIRED for Database Work)

**Setup pgpass.conf (one-time setup):**
```powershell
# Run setup script to enable password-less psql access
.\scripts\setup-pgpass.ps1

# Verify it works (no password prompt should appear)
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres" -c "\dt"
```

**What pgpass.conf does:**
- Stores PostgreSQL credentials locally in `%APPDATA%\postgresql\pgpass.conf`
- Eliminates interactive password prompts for all psql commands
- Required for: database introspection, migrations, testing, debugging
- File permissions automatically restricted to current user only

**Daily database workflow:**
```powershell
# Inspect table structures
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres" -c "\d permits"

# Run queries
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres" -c "SELECT business_id, status FROM permits LIMIT 5"

# Check column defaults
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres" -c "SELECT column_name, column_default FROM information_schema.columns WHERE table_name = 'permits'"

# Interactive mode
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres"
```

**When to use psql:**
- Before creating migrations (inspect current schema)
- After applying migrations (verify changes applied)
- Debugging SQLAlchemy issues (check actual vs expected schema)
- Testing business ID triggers
- Verifying data after service operations

**Note**: venv is at root level, not in a backend/ subdirectory. Most API endpoints require JWT authentication (send `Authorization: Bearer <token>` header).

### Environment Files
- **Backend** (`.env` at root): Database connection, `OPENAI_API_KEY`, Supabase credentials
- **Frontend** (`frontend/.env`): `VITE_API_URL` (defaults to production Fly.io backend)

### Deployment
- **Push to `main`** → Auto-deploys backend (Fly.io) + frontend (Cloudflare Pages)
- **No manual build steps** - CI/CD handles everything via GitHub Actions
- **Backend secrets**: Set via `fly secrets set` or Fly.io dashboard

## 🐛 Common Issues & Solutions

### Database Connection Issues
→ Check PostgreSQL connection string in `.env`
→ Verify Supabase credentials are correct
→ In production, Fly.io uses secrets set via `fly secrets set`

### CORS errors from frontend
→ Backend `app/config.py` has explicit CORS origins. Add new domains there + in `app/main.py` CORSMiddleware.

### Pydantic ValidationError with JSONB fields
→ Database stores JSONB as arrays: `[{...}, {...}]`
→ Pydantic model must match structure: `Optional[List[dict]]` not `Optional[dict]`
→ SQLAlchemy type hints don't enforce JSONB shape - always verify actual data structure
→ See `docs/audits/PYDANTIC_VALIDATION_DEBUGGING.md` for complete debugging guide

### Objects rendering in React
→ Use `typeof value === 'object' ? JSON.stringify(value) : value` before rendering unknown data

## 📁 Key Files to Reference

### Backend
- **API structure**: `app/main.py` (startup logic), `app/routes/` (all endpoints)
- **Authentication**: `app/routes/auth_supabase.py` (Supabase Auth integration), `app/services/supabase_auth_service.py` (JWT validation)
- **Services**: `app/services/db_service.py` (PostgreSQL), `app/services/quickbooks_service.py` (QB OAuth)
- **Smart loading**: `app/utils/context_builder.py` (reduces API calls by 90%, token usage by 40-50%)
- **Session memory**: `app/memory/memory_manager.py` (TTL-based context storage)
- **Config**: `app/config.py` (all env vars + CORS origins)
- **Legacy (disabled)**: `app/routes/auth.py`, `app/services/auth_service.py`, `app/middleware/auth_middleware.py`

### Frontend
- **State management**: `frontend/src/stores/appStore.js` (navigation + global state)
- **Component patterns**: `frontend/src/pages/ClientDetails.jsx` (shows field fallbacks + data handling)

### Available Routes
- `/v1/auth/supabase/*` - Supabase Auth integration (user management, /me endpoint)
- `/v1/chat` - AI chat with smart context loading
- `/v1/clients` - Client data from PostgreSQL
- `/v1/projects` - Project management
- `/v1/permits` - Permit tracking
- `/v1/inspections` - Inspection management with photos/deficiencies (JSONB arrays)
- `/v1/documents` - Document upload/management
- `/v1/quickbooks/*` - OAuth flow, customers, invoices, estimates, bills
- `/v1/payments` - Payment tracking and QB sync
- `/v1/invoices` - Invoice management
- `/v1/site-visits` - Site visit tracking
- `/v1/jurisdictions` - Jurisdiction data
- `/v1/users` - User management

**Note**: Legacy `/v1/auth/legacy/*` exists in codebase but is disabled in production

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
4. **PostgreSQL as primary database**: All CRUD operations use SQLAlchemy ORM with async. Google Sheets fully deprecated (Phase D.3, Dec 2025).
5. **Module singleton pattern**: Services are module-level instances, not class instantiation per request
6. **API versioning**: All routes prefixed with `/v1/` (see `settings.API_VERSION`)
7. **Supabase Auth**: Routes protected via `Depends(get_current_user)` from `auth_supabase.py` (no middleware)
8. **Smart context loading**: ALWAYS use `context_builder.py` for chat - 90% fewer API calls, 40-50% less tokens
9. **Session-based memory**: Use `memory_manager` for conversational context (10-min TTL)
10. **Structured logging**: Use `logger.info("[METRICS] ...")` for performance tracking in Fly.io logs

## 📊 Logging & Monitoring

### Backend Logging Pattern
```python
import logging
logger = logging.getLogger(__name__)

# Performance metrics (visible in Fly.io logs)
logger.info(f"[METRICS] API call took {duration}ms, tokens: {token_count}")

# Context loading
logger.info(f"Smart context loading: {contexts} for message: '{message[:50]}...'")

# Errors with context
logger.error(f"Database error: {e}", exc_info=True)
```

### Viewing Logs
```powershell
# Fly CLI - View recent logs
fly logs --app houserenovators-api

# Stream live logs
fly logs --app houserenovators-api --follow

# Search for specific text (use grep/Select-String)
fly logs --app houserenovators-api | Select-String "error|warning"

# View logs from specific instance
fly logs --app houserenovators-api --instance <instance-id>

# See docs/deployment/DEPLOYMENT.md for complete Fly.io guide
# See docs/technical/LOGGING_SECURITY.md for security monitoring patterns
```

**What to look for**:
- `[METRICS]` prefix = Performance data
- `Smart context loading:` = Which data sources were used
- `Google service not initialized` = Missing env vars
- `Invalid or expired token` = JWT auth issues
- `QuickBooks not authenticated` = Need to run OAuth flow

## 🚀 When Adding Features

- **New backend route**: Create in `app/routes/`, add auth with `Depends(get_current_user)` if protected, register in `app/main.py`
- **New frontend page**: Add to `pages/`, update `App.jsx` switch statement, add navigation in `appStore.js`
- **New database model**: Create in `app/db/models.py`, generate migration with Alembic, apply to Supabase
- **New data source for chat**: Add keywords to `context_builder.py` → add loading function → update `build_context()`
- **New QuickBooks operation**: Add method to `quickbooks_service.py`, ensure `is_authenticated()` check, handle token refresh
- **Environment variable**: Add to `app/config.py`, document in README, set via `fly secrets set`
- **Performance logging**: Add `logger.info("[METRICS] ...")` for operations > 100ms or using external APIs

## 🧪 Testing Patterns

### Testing Protected Endpoints

**Note**: The example below uses the legacy `/v1/auth/login` endpoint for **local testing only**. This endpoint exists in the codebase but is **disabled in production** (commented out in `app/main.py` line 123). Production applications should use the **Supabase Auth SDK** directly (see `frontend/src/lib/supabase.js`).

```powershell
# LEGACY AUTH (Local Testing Only) - Not available in production
# 1. Login to get token
$response = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"email":"admin@example.com","password":"admin123"}'

$token = $response.access_token

# 2. Call protected endpoint
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/v1/clients" -Headers $headers

# PRODUCTION AUTH - Use Supabase SDK
# See frontend/src/lib/supabase.js for reference implementation
# Frontend obtains token from Supabase Auth service, sends as: Authorization: Bearer <supabase_access_token>
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

## 🎯 TASK TRACKING WITH MANDATORY DOCUMENTATION

When using `manage_todo_list` for multi-step work:

**ALWAYS include final task:**
```markdown
- [ ] Update IMPLEMENTATION_TRACKER.md with completion timestamp
```

**Never mark work "complete" without documentation step in task list.**

**After completing ALL tasks:**
1. Mark last technical task as completed
2. Suggest documentation update before marking documentation task complete
3. Wait for user approval before updating docs

---

## 📚 Documentation Reference

### Essential Guides (Read These First)
- **`docs/guides/TERMINAL_MANAGEMENT.md`** - **CRITICAL**: How to prevent server shutdowns, terminal isolation patterns
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
- **`docs/deployment/DEPLOYMENT.md`** - Fly.io and Cloudflare deployment process
- **`docs/deployment/FLY_IO_DEPLOYMENT.md`** - Detailed Fly.io deployment guide

### Reference & Troubleshooting
- **`docs/guides/TROUBLESHOOTING.md`** - Common issues and solutions
- **`docs/audits/PYDANTIC_VALIDATION_DEBUGGING.md`** - Debugging Pydantic + JSONB validation issues
- **`docs/technical/LOGGING_SECURITY.md`** - Security logging patterns
- **`docs/technical/DATABASE_SCHEMA.md`** - PostgreSQL schema reference

### Scripts Organization
- **`scripts/testing/chat-tests/`** - All chat and integration tests
- **`scripts/docs-management/`** - Documentation maintenance tools
- **`scripts/setup/`** - Environment setup automation


