# Copilot Instructions Validation Commands

**Purpose**: Regression checks to verify copilot-instructions.md accuracy  
**Date**: December 13, 2025

---

## 1. Backend Routes Validation

### Check All Registered Routes
```powershell
cd "C:\Users\Steve Garay\Desktop\HouseRenovators-api"
.\.venv\Scripts\Activate.ps1

python -c "from app.main import app; routes = [(r.path, list(r.methods)) for r in app.routes if r.path.startswith('/v1')]; [print(f'{path:50} {methods}') for path, methods in sorted(routes)]"
```

**Expected Output**: 14 routes starting with `/v1/`

### Verify Supabase Auth Routes Active
```powershell
python -c "from app.main import app; supabase_routes = [r.path for r in app.routes if 'supabase' in r.path]; print('\n'.join(supabase_routes) if supabase_routes else 'NO SUPABASE ROUTES FOUND')"
```

**Expected**: Routes like `/v1/auth/supabase/me`, `/v1/auth/supabase/users`, etc.

### Verify Legacy Auth Routes Disabled
```powershell
python -c "from app.main import app; legacy_routes = [r.path for r in app.routes if 'legacy' in r.path]; print('✅ Legacy auth disabled (correct)' if not legacy_routes else f'⚠️ ISSUE: Legacy routes found: {legacy_routes}')"
```

**Expected**: `✅ Legacy auth disabled (correct)`

---

## 2. Auth System Validation

### Verify Supabase Auth Service Exists
```powershell
python -c "from app.services.supabase_auth_service import supabase_auth_service; print(f'✅ Supabase Auth Service loaded: {type(supabase_auth_service).__name__}')"
```

**Expected**: `✅ Supabase Auth Service loaded: SupabaseAuthService`

### Verify get_current_user Dependency
```powershell
python -c "from app.routes.auth_supabase import get_current_user; import inspect; print('✅ get_current_user signature:', inspect.signature(get_current_user))"
```

**Expected**: Signature showing `HTTPAuthorizationCredentials` and `AsyncSession` dependencies

### Check No Auth Middleware Active
```powershell
python -c "from app.main import app; middleware_classes = [type(m).__name__ for m in app.user_middleware]; auth_middleware = [m for m in middleware_classes if 'Auth' in m or 'JWT' in m]; print('✅ No auth middleware (correct)' if not auth_middleware else f'⚠️ ISSUE: Auth middleware found: {auth_middleware}')"
```

**Expected**: `✅ No auth middleware (correct)`

---

## 3. Database Validation

### Verify PostgreSQL Connection
```powershell
python -c "from app.config import settings; print('✅ DATABASE_URL configured:', bool(settings.DATABASE_URL))"
```

**Expected**: `✅ DATABASE_URL configured: True`

### Check SQLAlchemy Models Exist
```powershell
python -c "from app.db.models import Client, Project, Permit, Payment, Inspection, User; models = [Client, Project, Permit, Payment, Inspection, User]; print('✅ Models loaded:', ', '.join([m.__name__ for m in models]))"
```

**Expected**: `✅ Models loaded: Client, Project, Permit, Payment, Inspection, User`

### Verify Google Sheets Deprecation
```powershell
python -c "import sys; sys.path.insert(0, 'app'); from services import quickbooks_service; import inspect; source = inspect.getsource(quickbooks_service.QuickBooksService.sync_payments_to_sheets); assert 'DEPRECATED' in source or 'retired' in source, 'Google Sheets not deprecated'; print('✅ Google Sheets methods deprecated')"
```

**Expected**: `✅ Google Sheets methods deprecated`

---

## 4. Documentation Validation

### Check Key Documentation Files Exist
```powershell
$docs = @(
    "docs\README.md",
    "docs\architecture\AUTHENTICATION_MODEL.md",
    "docs\audits\PYDANTIC_VALIDATION_DEBUGGING.md",
    "docs\deployment\DEPLOYMENT.md",
    "docs\deployment\FLY_IO_DEPLOYMENT.md",
    "docs\guides\QUICKBOOKS_GUIDE.md",
    "docs\guides\TROUBLESHOOTING.md",
    ".github\copilot-instructions.md"
)

foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Write-Host "✅ $doc"
    } else {
        Write-Host "❌ $doc - NOT FOUND"
    }
}
```

**Expected**: All files show ✅

### Verify Governance Compliance
```powershell
# Check canonical folders exist
$folders = @(
    "docs\roadmap",
    "docs\operations",
    "docs\architecture",
    "docs\business",
    "docs\audits",
    "docs\guides",
    "docs\setup",
    "docs\deployment",
    "docs\technical",
    "docs\history"
)

foreach ($folder in $folders) {
    if (Test-Path $folder) {
        Write-Host "✅ $folder"
    } else {
        Write-Host "⚠️ $folder - NOT FOUND (may not exist yet)"
    }
}
```

---

## 5. Context Builder Validation

### Verify No Google Service Usage
```powershell
python -c "from app.utils import context_builder; import inspect; source = inspect.getsource(context_builder.build_context); has_google = 'google_service' in source; print('⚠️ ISSUE: google_service still referenced' if has_google else '✅ context_builder clean (no google_service)')"
```

**Expected**: `✅ context_builder clean (no google_service)`

### Check Context Loading Performance Claims
```powershell
python -c "from app.utils.context_builder import get_required_contexts; test_cases = [('Show me Temple project', {'sheets'}), ('Create invoice', {'sheets', 'quickbooks'}), ('Hello', {'none'})]; results = [(msg, get_required_contexts(msg)) for msg, _ in test_cases]; [print(f'Message: {msg:30} → Contexts: {ctx}') for msg, ctx in results]"
```

**Expected**: Shows smart context selection (different contexts for different messages)

---

## 6. Fly.io Integration Validation

### Verify Fly.io Configuration
```powershell
if (Test-Path "fly.toml") {
    $config = Get-Content "fly.toml" | Select-String "app =|primary_region =|internal_port ="
    Write-Host "✅ fly.toml exists"
    $config
} else {
    Write-Host "❌ fly.toml NOT FOUND"
}
```

**Expected**: Shows `app = 'houserenovators-api'`

### Check Fly CLI Installation
```powershell
try {
    $version = fly version
    Write-Host "✅ Fly CLI installed: $version"
} catch {
    Write-Host "❌ Fly CLI not installed or not in PATH"
    Write-Host "   Install: iwr https://fly.io/install.ps1 -useb | iex"
}
```

**Expected**: Shows Fly CLI version

### Test Fly.io Backend Health (if connected)
```powershell
try {
    $status = fly status --app houserenovators-api 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Fly.io backend reachable"
        $status | Select-String "Status|Instances"
    } else {
        Write-Host "⚠️ Not authenticated to Fly.io (run: fly auth login)"
    }
} catch {
    Write-Host "⚠️ Cannot check Fly.io status (CLI not installed or not authenticated)"
}
```

---

## 7. Frontend Integration Validation

### Check Frontend Supabase Integration
```powershell
if (Test-Path "frontend\src\lib\supabase.js") {
    $supabase_code = Get-Content "frontend\src\lib\supabase.js" | Select-String "@supabase/supabase-js|createClient"
    if ($supabase_code) {
        Write-Host "✅ Frontend uses @supabase/supabase-js"
        $supabase_code | ForEach-Object { Write-Host "   $_" }
    } else {
        Write-Host "❌ Frontend Supabase integration not found"
    }
} else {
    Write-Host "❌ frontend\src\lib\supabase.js NOT FOUND"
}
```

**Expected**: Shows `import { createClient } from '@supabase/supabase-js'`

### Check Frontend API URL Configuration
```powershell
if (Test-Path "frontend\.env") {
    $api_url = Get-Content "frontend\.env" | Select-String "VITE_API_URL"
    Write-Host "✅ Frontend .env exists"
    $api_url
} else {
    Write-Host "⚠️ frontend\.env NOT FOUND (may use defaults)"
}
```

**Expected**: Shows `VITE_API_URL=https://houserenovators-api.fly.dev`

---

## 8. Complete System Check (All-in-One)

```powershell
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "COPILOT INSTRUCTIONS VALIDATION REPORT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

cd "C:\Users\Steve Garay\Desktop\HouseRenovators-api"
.\.venv\Scripts\Activate.ps1

# 1. Platform
Write-Host "1. DEPLOYMENT PLATFORM" -ForegroundColor Yellow
$has_fly = Test-Path "fly.toml"
$has_render = Test-Path "render.yaml"
Write-Host "   Fly.io config: $(if ($has_fly) {'✅ Present'} else {'❌ Missing'})"
Write-Host "   Render config: $(if ($has_render) {'⚠️ Present (should be historical)'} else {'✅ Not present (correct)'})"

# 2. Auth
Write-Host "`n2. AUTHENTICATION SYSTEM" -ForegroundColor Yellow
try {
    python -c "from app.routes.auth_supabase import get_current_user; print('   Supabase Auth: ✅ Active')"
} catch {
    Write-Host "   Supabase Auth: ❌ ERROR" -ForegroundColor Red
}

try {
    python -c "from app.main import app; legacy = [r for r in app.routes if 'legacy' in r.path]; print('   Legacy auth: ✅ Disabled' if not legacy else '   Legacy auth: ⚠️ Still active')"
} catch {
    Write-Host "   Legacy auth check: ❌ ERROR" -ForegroundColor Red
}

# 3. Database
Write-Host "`n3. DATABASE" -ForegroundColor Yellow
try {
    python -c "from app.db.models import Client, Project, Permit; print('   PostgreSQL models: ✅ Loaded')"
} catch {
    Write-Host "   PostgreSQL models: ❌ ERROR" -ForegroundColor Red
}

# 4. Routes
Write-Host "`n4. API ROUTES" -ForegroundColor Yellow
try {
    $route_count = python -c "from app.main import app; print(len([r for r in app.routes if r.path.startswith('/v1')]))"
    Write-Host "   Registered routes: $route_count (expected: 14+)"
} catch {
    Write-Host "   Route check: ❌ ERROR" -ForegroundColor Red
}

# 5. Documentation
Write-Host "`n5. DOCUMENTATION" -ForegroundColor Yellow
$doc_count = (Get-ChildItem -Path "docs" -Recurse -Filter "*.md" | Measure-Object).Count
Write-Host "   Total docs: $doc_count files"
Write-Host "   Governance: $(if (Test-Path 'docs\README.md') {'✅ docs\README.md exists'} else {'❌ Missing'})"
Write-Host "   Copilot instructions: $(if (Test-Path '.github\copilot-instructions.md') {'✅ Present'} else {'❌ Missing'})"

Write-Host "`n========================================`n" -ForegroundColor Cyan
```

---

## Expected Results Summary

| Check | Expected Result |
|-------|----------------|
| **Routes** | 14+ routes starting with `/v1/` |
| **Auth** | Supabase Auth active, legacy disabled |
| **Middleware** | No auth middleware active |
| **Database** | PostgreSQL models loaded, Sheets deprecated |
| **Platform** | fly.toml present, render.yaml absent |
| **Documentation** | All key docs present in correct folders |
| **Context Builder** | No google_service references |
| **Frontend** | Uses @supabase/supabase-js SDK |

---

## Troubleshooting

### If Routes Don't Match
```powershell
# List all routes with details
python -c "from app.main import app; import json; routes = [{'path': r.path, 'name': r.name, 'methods': list(r.methods)} for r in app.routes if r.path.startswith('/v1')]; print(json.dumps(routes, indent=2))"
```

### If Auth Check Fails
```powershell
# Check which auth modules are imported
python -c "from app.main import app; import sys; auth_modules = [m for m in sys.modules.keys() if 'auth' in m.lower()]; print('\n'.join(sorted(auth_modules)))"
```

### If Database Check Fails
```powershell
# Verify database connection string
python -c "from app.config import settings; print('DATABASE_URL configured:', bool(settings.DATABASE_URL)); print('SUPABASE_URL configured:', bool(settings.SUPABASE_URL))"
```

---

**Last Updated**: December 13, 2025  
**Purpose**: Validate copilot-instructions.md accuracy against live codebase
