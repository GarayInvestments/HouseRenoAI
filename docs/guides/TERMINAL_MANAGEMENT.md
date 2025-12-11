# Terminal Management Guide - HouseRenovators-api

**Version**: 1.0  
**Date**: December 11, 2025  
**Critical**: Read this before running backend/frontend servers or tests

---

## 🚨 THE PROBLEM WE'RE SOLVING

### What Keeps Happening
1. Backend starts successfully with `uvicorn app.main:app --reload`
2. Agent needs to run another command (git, test, migration)
3. Agent uses `run_in_terminal` → **uses the SAME terminal**
4. Backend shuts down with `INFO: Shutting down`
5. Test/command fails because backend is dead

**Root Cause**: `run_in_terminal` with `isBackground: true` doesn't guarantee terminal isolation in VS Code. Each subsequent call can reuse the terminal, killing the background process.

---

## ✅ SOLUTION: Terminal Dedication Pattern

### The Rule
**One server = One dedicated terminal that is NEVER reused**

```
Terminal 1: Backend (uvicorn)     → BLOCKED, never touch
Terminal 2: Frontend (npm dev)    → BLOCKED, never touch  
Terminal 3+: Commands (git/test)  → Free to use
```

---

## 🔧 CORRECT WORKFLOW

### Step 1: Start Backend Server (ONE TIME)

```typescript
run_in_terminal({
  command: "& 'C:/Users/Steve Garay/Desktop/HouseRenovators-api/.venv/Scripts/Activate.ps1'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
  explanation: "Starting FastAPI backend server in DEDICATED terminal",
  isBackground: true
})
```

**Returns**: `Terminal ID=abc-123-def-456` → **SAVE THIS ID**

**Expected Output**:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Started server process [12345]
Google services initialized successfully
QuickBooks token valid until 2025-12-11 14:27:49
INFO: Application startup complete
```

### Step 2: Check Server Status (Anytime)

```typescript
get_terminal_output({
  id: "abc-123-def-456"  // The ID from Step 1
})
```

**When to check**:
- After startup (verify no errors)
- Before running tests (confirm server still alive)
- After API calls fail (check for crash logs)
- When debugging endpoint issues

### Step 3: Run Commands in NEW Terminals

**❌ WRONG** (kills server):
```typescript
// Backend is running in terminal X
run_in_terminal({
  command: "python scripts/test_permit_api.py",
  isBackground: false  // ← Will reuse terminal X, kills uvicorn
})
```

**✅ CORRECT** (server stays alive):
```typescript
// Option A: Use isBackground=true to FORCE new terminal
run_in_terminal({
  command: "python scripts/test_permit_api.py",
  isBackground: true  // ← Creates NEW terminal, server safe
})

// Option B: Manual execution
// Tell user: "Please run in a new terminal: python scripts/test_permit_api.py"
```

---

## 📋 PRACTICAL EXAMPLES

### Example 1: Backend Testing Workflow

```typescript
// === START OF CHAT SESSION ===

// 1. Start backend (ONCE)
run_in_terminal({
  command: "& 'C:/Users/Steve Garay/Desktop/HouseRenovators-api/.venv/Scripts/Activate.ps1'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
  explanation: "Starting backend in dedicated terminal",
  isBackground: true
})
// Save ID: BACKEND_TERMINAL_ID = "abc-123..."

// 2. Wait 3-5 seconds for startup
// (Tool doesn't wait automatically)

// 3. Verify server is up
get_terminal_output({ id: BACKEND_TERMINAL_ID })
// Look for: "Application startup complete"

// 4. Run tests in SEPARATE terminal
run_in_terminal({
  command: "python scripts/test_permit_api.py",
  explanation: "Running permit API tests",
  isBackground: true  // ← NEW TERMINAL
})

// 5. Check test results
// (Separate terminal output will show test results)

// 6. Check backend logs for API activity
get_terminal_output({ id: BACKEND_TERMINAL_ID })
// Look for: POST /v1/permits, status codes, errors

// 7. Run git commands in SEPARATE terminal
run_in_terminal({
  command: "git add -A; git commit -m 'Test Phase B.1'; git push origin main",
  explanation: "Committing changes",
  isBackground: false  // ← Will create/use non-server terminal
})

// 8. Backend STILL RUNNING (check anytime)
get_terminal_output({ id: BACKEND_TERMINAL_ID })
```

### Example 2: Frontend + Backend

```typescript
// 1. Start backend
run_in_terminal({
  command: "& '.venv/Scripts/Activate.ps1'; uvicorn app.main:app --reload",
  explanation: "Backend server (Terminal 1)",
  isBackground: true
})
// Save: BACKEND_ID

// 2. Start frontend
run_in_terminal({
  command: "cd frontend; npm run dev",
  explanation: "Frontend server (Terminal 2)",
  isBackground: true
})
// Save: FRONTEND_ID

// 3. Run database migration (Terminal 3)
run_in_terminal({
  command: "alembic upgrade head",
  explanation: "Applying database migrations",
  isBackground: true  // NEW TERMINAL
})

// 4. Both servers STILL RUNNING
get_terminal_output({ id: BACKEND_ID })   // Check backend
get_terminal_output({ id: FRONTEND_ID })  // Check frontend
```

### Example 3: Monitoring Server Errors

```typescript
// Backend running in Terminal 1

// User reports: "API returning 500 errors"

// Check backend logs for stack traces
get_terminal_output({ id: BACKEND_TERMINAL_ID })

// Look for:
// - "ERROR: ..." lines
// - "Traceback (most recent call last):"
// - "sqlalchemy.exc..." (database errors)
// - "ModuleNotFoundError" (import issues)
// - HTTP status codes (POST /v1/permits - 500)

// Typical errors you might see:
// 1. "ModuleNotFoundError: No module named 'app.db.database'"
//    → Fix: Correct import path
// 
// 2. "Google service not initialized"
//    → Fix: Check .env has GOOGLE_SERVICE_ACCOUNT_FILE
//
// 3. "Invalid or expired token"
//    → Fix: User needs to re-login (/v1/auth/login)
```

---

## 🎯 PROJECT-SPECIFIC COMMANDS

### Backend Commands (Always in Dedicated Terminal)

```powershell
# Full backend startup (with venv)
& "C:/Users/Steve Garay/Desktop/HouseRenovators-api/.venv/Scripts/Activate.ps1"; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend with specific port
uvicorn app.main:app --reload --port 8001

# Backend without reload (production-like)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Commands (Always in Dedicated Terminal)

```powershell
# Frontend dev server
cd frontend; npm run dev

# Frontend with specific port
cd frontend; npm run dev -- --port 5174
```

### Database Commands (Always in NEW Terminal)

```powershell
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Check current revision
alembic current

# PostgreSQL access (requires pgpass.conf)
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres" -c "\dt"
```

### Testing Commands (Always in NEW Terminal)

```powershell
# Run API tests
python scripts/test_permit_api.py

# Run pytest
pytest tests/

# Run specific test
pytest tests/test_current_chat_handlers.py::test_create_client
```

### Git Commands (Always in NEW Terminal)

```powershell
# Standard commit + push
git add -A; git commit -m "Message"; git push origin main

# Check status
git status

# View logs
git log --oneline -10
```

---

## 🐛 TROUBLESHOOTING

### Problem: Backend Shuts Down After Test

**Symptoms**:
```
INFO: Application startup complete
INFO: Shutting down               ← Backend died
INFO: Finished server process
```

**Cause**: Test command ran in same terminal as backend

**Solution**:
1. Check if backend terminal ID was saved
2. If not, restart backend with `isBackground: true`
3. Run tests with `isBackground: true` to force new terminal
4. Verify with `get_terminal_output(BACKEND_ID)` that server still running

### Problem: "Connection Refused" When Testing

**Symptoms**:
```
HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded
[WinError 10061] No connection could be made
```

**Cause**: Backend not running

**Solution**:
1. Check backend terminal: `get_terminal_output(BACKEND_ID)`
2. If shut down, restart:
   ```typescript
   run_in_terminal({
     command: "& '.venv/Scripts/Activate.ps1'; uvicorn app.main:app --reload",
     isBackground: true
   })
   ```
3. Wait 5 seconds for startup
4. Verify with `get_terminal_output(new_id)`

### Problem: ModuleNotFoundError on Backend Start

**Symptoms**:
```
ModuleNotFoundError: No module named 'sqlalchemy'
```

**Cause**: Virtual environment not activated

**Solution**:
Always prefix backend commands with venv activation:
```powershell
& "C:/Users/Steve Garay/Desktop/HouseRenovators-api/.venv/Scripts/Activate.ps1"; python -m uvicorn ...
```

### Problem: Can't Track Multiple Terminals

**Solution**: Store terminal IDs in chat context
```typescript
// At start of session, declare:
let BACKEND_TERMINAL = null;
let FRONTEND_TERMINAL = null;
let COMMAND_TERMINAL = null;

// When starting backend:
run_in_terminal({ ... isBackground: true })
// Returns: ID=abc123
BACKEND_TERMINAL = "abc123";

// Later, check backend:
get_terminal_output({ id: BACKEND_TERMINAL })
```

---

## 📊 TERMINAL STATE REFERENCE

### Healthy Backend Terminal Output

```
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO: Started reloader process [12345] using WatchFiles
INFO: Started server process [12346]
INFO: Waiting for application startup.
INFO: Service account file already exists: config/house-renovators-credentials.json
INFO: Google services initialized successfully
INFO: Users sheet ready
INFO: QuickBooks token valid until 2025-12-11 14:27:49.603841
INFO: Application startup complete.
```

### Backend with Errors (Still Running)

```
INFO: Application startup complete.
INFO: 127.0.0.1:54321 - "POST /v1/permits HTTP/1.1" 500 Internal Server Error
ERROR: Exception in ASGI application
Traceback (most recent call last):
  File "app/routes/permits.py", line 123
    result = await service.create_permit(...)
sqlalchemy.exc.IntegrityError: (psycopg2.errors.NotNullViolation) null value...
```
**Action**: Server running but endpoint has bug. Fix code, auto-reload will restart.

### Backend Dead (Needs Restart)

```
INFO: Application startup complete.
INFO: Shutting down
INFO: Waiting for application shutdown.
INFO: Application shutdown complete.
INFO: Finished server process [12346]
INFO: Stopping reloader process [12345]
```
**Action**: Backend shut down. Must restart with `isBackground: true` in new terminal.

---

## 🎓 BEST PRACTICES

### 1. Start Servers First, Save IDs

```typescript
// RIGHT: Start all servers FIRST, save all IDs
const BACKEND_ID = await startBackend();
const FRONTEND_ID = await startFrontend();

// THEN run commands
await runTests();
await commitChanges();
```

### 2. Always Verify Server Status

```typescript
// Before running tests:
get_terminal_output({ id: BACKEND_ID });
// Look for: "Application startup complete" (not "Shutting down")

// Then run test:
run_in_terminal({ command: "python test.py", isBackground: true });
```

### 3. Use isBackground for Everything During Active Session

```typescript
// If backend is running, ALWAYS use isBackground: true for new commands
run_in_terminal({
  command: "git push",
  isBackground: true  // ← Prevents terminal reuse
})
```

### 4. Communicate Terminal State to User

```typescript
// After starting backend:
// "✅ Backend started in Terminal 1 (ID: abc123)"
// "Server will remain running. All other commands use separate terminals."

// When running tests:
// "Running tests in Terminal 3 (backend still running in Terminal 1)"

// After completion:
// "✅ Tests passed. Backend still running. Check logs with get_terminal_output."
```

### 5. Keep-Alive for Long Sessions

If you need a terminal to stay open but command finishes quickly:

```powershell
# Add sleep to keep terminal alive
python script.py; Write-Host "Complete. Terminal stays open."; Start-Sleep 3600
```

---

## 🚀 RECOMMENDED WORKFLOW FOR THIS PROJECT

### Initial Setup (Once Per Chat Session)

```typescript
// 1. Start backend
run_in_terminal({
  command: "& 'C:/Users/Steve Garay/Desktop/HouseRenovators-api/.venv/Scripts/Activate.ps1'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
  explanation: "Starting FastAPI backend (Terminal 1 - DEDICATED)",
  isBackground: true
})
// Save: BACKEND_TERMINAL_ID = response.id

// 2. Wait 5 seconds (backend startup)

// 3. Verify startup
get_terminal_output({ id: BACKEND_TERMINAL_ID })
// Confirm: "Application startup complete"

// 4. Optionally start frontend
run_in_terminal({
  command: "cd frontend; npm run dev",
  explanation: "Starting React frontend (Terminal 2 - DEDICATED)",
  isBackground: true
})
// Save: FRONTEND_TERMINAL_ID = response.id
```

### During Development

```typescript
// All commands use NEW terminals (isBackground: true)

// Run tests
run_in_terminal({
  command: "python scripts/test_permit_api.py",
  isBackground: true
})

// Check backend logs
get_terminal_output({ id: BACKEND_TERMINAL_ID })

// Run migrations
run_in_terminal({
  command: "alembic upgrade head",
  isBackground: true
})

// Git operations
run_in_terminal({
  command: "git add -A; git commit -m 'Fix'; git push",
  isBackground: true
})

// Backend NEVER touched after initial start
```

### End of Session

```typescript
// Optional: Gracefully stop servers
// (Usually not needed - closing VS Code stops all terminals)

// But if you want to stop manually:
// Navigate to Terminal 1 in VS Code → Ctrl+C
// Navigate to Terminal 2 in VS Code → Ctrl+C
```

---

## 📚 QUICK REFERENCE

| Task | Command Pattern | Terminal Type |
|------|----------------|---------------|
| Start backend | `uvicorn app.main:app --reload` | `isBackground: true` (ONCE) |
| Start frontend | `cd frontend; npm run dev` | `isBackground: true` (ONCE) |
| Run tests | `python scripts/test_*.py` | `isBackground: true` (new) |
| Git operations | `git add/commit/push` | `isBackground: true` (new) |
| Database migrations | `alembic upgrade head` | `isBackground: true` (new) |
| Check backend logs | `get_terminal_output(BACKEND_ID)` | N/A (read only) |
| Check frontend logs | `get_terminal_output(FRONTEND_ID)` | N/A (read only) |

---

## ⚡ KEY TAKEAWAYS

1. **`isBackground: true` creates NEW terminals** - use for all commands when servers running
2. **Save terminal IDs** - you need them to read logs with `get_terminal_output`
3. **Start servers ONCE** - they run for entire chat session
4. **Never run commands in server terminals** - always create new terminal
5. **Check logs proactively** - use `get_terminal_output` to verify server health
6. **This prevents the shutdown problem** - backend/frontend stay alive throughout development

---

## 📖 SEE ALSO

- **Deployment Logs**: `docs/deployment/RENDER_LOGS_GUIDE.md` (production server logs)
- **Testing Guide**: `docs/guides/CHAT_TESTING_SOP.md` (test procedures)
- **Setup Guide**: `docs/setup/SETUP_GUIDE.md` (initial project setup)
- **PostgreSQL Access**: Setup guide section on pgpass.conf

---

**Last Updated**: December 11, 2025  
**Tested On**: Phase B.1 permit API endpoint testing workflow  
**Status**: Verified solution for terminal isolation issues
