# House Renovators AI Portal - Copilot Instructions

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
```bash
# Backend (Terminal 1) - MUST activate venv first
cd backend && .\venv\Scripts\Activate.ps1
cd .. && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend && npm run dev  # http://localhost:5173

# Frontend connects to PRODUCTION backend by default (see frontend/.env)
VITE_API_URL=https://houserenoai.onrender.com
```

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

- **API structure**: `app/main.py` (startup logic), `app/routes/` (endpoints)
- **Google Sheets ops**: `app/services/google_service.py` (all read operations are async)
- **State management**: `frontend/src/stores/appStore.js` (navigation + global state)
- **Component patterns**: `frontend/src/pages/ClientDetails.jsx` (shows field fallbacks + data handling)
- **Config**: `app/config.py` (all env vars + CORS origins)

## 🎯 Project-Specific Conventions

1. **No TypeScript**: Stick to JavaScript for frontend (existing codebase decision)
2. **Inline styles over CSS**: Many components use React inline styles for specific layouts
3. **PowerShell scripts**: DevOps uses `.ps1` files (Windows-first environment)
4. **Google Sheets as database**: All CRUD operations go through Google Sheets API, no SQL
5. **Module singleton pattern**: Services like `google_service` are module-level instances, not class instantiation per request
6. **API versioning**: All routes prefixed with `/v1/` (see `settings.API_VERSION`)

## 🚀 When Adding Features

- **New backend route**: Create in `app/routes/`, use `get_google_service()` helper, add to `app/main.py`
- **New frontend page**: Add to `pages/`, update `App.jsx` switch statement, add navigation in `appStore.js`
- **New Google Sheets column**: Update field fallbacks in frontend components to handle old/new column names
- **Environment variable**: Add to `app/config.py`, document in README, set in Render/Cloudflare dashboard
