# Render Logs Access Guide

**Created**: November 9, 2025  
**Purpose**: Quick reference for viewing production logs  
**Service ID**: `srv-d44ak76uk2gs73a3psig`  
**Service Name**: HouseRenoAI

---

## 🚀 Quick Commands

### View Recent Logs (Last 200 lines)
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 200 --confirm -o text
```

### Stream Live Logs
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --tail --confirm
```

### Search for Errors
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --text "error,ERROR,exception" --limit 500 --confirm -o text
```

### Search for Performance Metrics
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --text "[METRICS]" --limit 100 --confirm -o text
```

### Search for Specific Session
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --text "session_abc123" --limit 200 --confirm -o text
```

---

## 📋 All Available Flags

```
--direction       'forward' or 'backward' (default: backward)
--end             End time for log query
--start           Start time for log query
--limit           Maximum number of logs (default: 100)
--text            Comma-separated strings to search for
--level           Log level: info, warning, error, debug
--type            Log type filter
--host            Filter by host
--instance        Filter by instance ID
--method          HTTP method filter (GET, POST, etc.)
--path            Filter by request path
--status-code     Filter by HTTP status code
--tail            Stream new logs in real-time
-r, --resources   Service ID (REQUIRED in non-interactive mode)
--confirm         Skip confirmation prompts
-o, --output      Output format: text, json, yaml, interactive
```

---

## 🎯 Common Use Cases

### 1. Debug Failed Request
```powershell
# Find 500 errors
render logs -r srv-d44ak76uk2gs73a3psig --status-code 500 --limit 50 --confirm -o text

# See full context around error
render logs -r srv-d44ak76uk2gs73a3psig --text "ERROR,exception" --limit 100 --confirm -o text
```

### 2. Monitor Deployment
```powershell
# Watch logs during deploy
render logs -r srv-d44ak76uk2gs73a3psig --tail --confirm

# Check for startup errors after deploy
render logs -r srv-d44ak76uk2gs73a3psig --text "startup,initialized" --limit 50 --confirm -o text
```

### 3. Performance Analysis
```powershell
# View all timing metrics
render logs -r srv-d44ak76uk2gs73a3psig --text "[METRICS],[TIMING]" --limit 200 --confirm -o text

# Check slow requests (>5 seconds)
render logs -r srv-d44ak76uk2gs73a3psig --text "took" --limit 100 --confirm -o text
```

### 4. QuickBooks Integration Issues
```powershell
# Check QB authentication status
render logs -r srv-d44ak76uk2gs73a3psig --text "QuickBooks,QB_" --limit 100 --confirm -o text

# View token refresh attempts
render logs -r srv-d44ak76uk2gs73a3psig --text "token refresh,expired" --limit 50 --confirm -o text
```

### 5. Google Sheets Issues
```powershell
# Check cache behavior
render logs -r srv-d44ak76uk2gs73a3psig --text "cache HIT,cache MISS,cache EXPIRED" --limit 100 --confirm -o text

# View Sheets API calls
render logs -r srv-d44ak76uk2gs73a3psig --text "Sheets API,google_service" --limit 100 --confirm -o text
```

### 6. Chat/AI Issues
```powershell
# View chat requests
render logs -r srv-d44ak76uk2gs73a3psig --path "/v1/chat" --limit 100 --confirm -o text

# Check context loading
render logs -r srv-d44ak76uk2gs73a3psig --text "Smart context loading" --limit 50 --confirm -o text

# View OpenAI API calls
render logs -r srv-d44ak76uk2gs73a3psig --text "openai.com" --limit 100 --confirm -o text
```

---

## 🔍 Log Analysis Patterns

### Finding Session-Specific Issues
```powershell
# 1. Get session ID from error report or frontend
$sessionId = "session_abc123"

# 2. View all logs for that session
render logs -r srv-d44ak76uk2gs73a3psig --text $sessionId --limit 500 --confirm -o text
```

### Monitoring API Response Times
```powershell
# Look for slow endpoints
render logs -r srv-d44ak76uk2gs73a3psig --text "completed in" --limit 100 --confirm -o text | Select-String -Pattern "completed in \d{4,}ms"
```

### Checking Authentication Issues
```powershell
# View auth failures
render logs -r srv-d44ak76uk2gs73a3psig --status-code 401,403 --limit 50 --confirm -o text

# Check JWT token issues
render logs -r srv-d44ak76uk2gs73a3psig --text "Invalid token,expired token,Unauthorized" --limit 50 --confirm -o text
```

---

## 🛑 Common Mistakes

### ❌ WRONG: Using `-s` flag (old syntax)
```powershell
render logs -s house-renovators-ai-portal  # This FAILS
```

### ✅ CORRECT: Using `-r` flag with service ID
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --confirm -o text
```

### ❌ WRONG: Forgetting output format
```powershell
render logs -r srv-d44ak76uk2gs73a3psig  # Opens interactive mode (not scriptable)
```

### ✅ CORRECT: Specify output format for scripts
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --confirm -o text
```

---

## 📊 Log Output Formats

### Text Format (Human-Readable)
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 10 --confirm -o text
```
**Output**:
```
2025-11-09 11:34:34  INFO:app.routes.chat:[session_abc] Processing message
2025-11-09 11:34:35  INFO:app.utils.timing:[session_abc] [TIMING] context_build took 0.221s
```

### JSON Format (Machine-Parseable)
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 10 --confirm -o json | ConvertFrom-Json
```
**Use case**: Parsing logs programmatically, importing to log aggregators

### YAML Format
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 10 --confirm -o yaml
```
**Use case**: Easy to read structured data, copy to config files

---

## 🔐 Security: Checking for Exposed Secrets

### What to Look For
```powershell
# Search for potentially exposed secrets
render logs -r srv-d44ak76uk2gs73a3psig --text "token,password,secret,key,Bearer,JWT" --limit 500 --confirm -o text
```

### Safe Patterns (Should See)
- `INFO:app.routes.auth:User logged in` ✅
- `INFO:app.services.google_service:Sheets cache HIT` ✅
- `INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions` ✅

### Dangerous Patterns (Should NOT See)
- `Bearer eyJhbGciOi...` ❌ (JWT token exposed)
- `password: admin123` ❌ (Password in plaintext)
- `OPENAI_API_KEY=sk-proj-...` ❌ (API key exposed)
- `access_token: "ABC123..."` ❌ (OAuth token exposed)

---

## 💡 Tips & Best Practices

### 1. Use Wide Output in PowerShell
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 100 --confirm -o text | Out-String -Width 500
```
Prevents log lines from being truncated.

### 2. Save Logs to File
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 1000 --confirm -o text > logs_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt
```

### 3. Grep Specific Patterns
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 500 --confirm -o text | Select-String -Pattern "ERROR|exception" -Context 3
```

### 4. Count Occurrences
```powershell
# How many cache hits vs misses?
render logs -r srv-d44ak76uk2gs73a3psig --text "cache" --limit 500 --confirm -o text | Select-String -Pattern "cache HIT|cache MISS" | Group-Object
```

### 5. Export to CSV for Analysis
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 1000 --confirm -o json | ConvertFrom-Json | Export-Csv logs.csv -NoTypeInformation
```

---

## 🚨 Emergency Scenarios

### Service Down / 503 Errors
```powershell
# 1. Check last 50 logs
render logs -r srv-d44ak76uk2gs73a3psig --limit 50 --confirm -o text

# 2. Look for startup failures
render logs -r srv-d44ak76uk2gs73a3psig --text "Failed,error,exception,startup" --limit 100 --confirm -o text

# 3. Check if service is running
render services --confirm -o json | ConvertFrom-Json | Where-Object { $_.service.id -eq "srv-d44ak76uk2gs73a3psig" }
```

### Memory/CPU Issues
```powershell
# Look for OOM (Out of Memory) errors
render logs -r srv-d44ak76uk2gs73a3psig --text "memory,killed,OOM" --limit 100 --confirm -o text
```

### Database Connection Issues
```powershell
# Check Google Sheets connectivity
render logs -r srv-d44ak76uk2gs73a3psig --text "Google service not initialized,credentials,Sheets API" --limit 100 --confirm -o text
```

---

## 📚 Additional Resources

- **Render CLI Docs**: https://render.com/docs/cli
- **Service Dashboard**: https://dashboard.render.com/web/srv-d44ak76uk2gs73a3psig
- **API Logs**: `/v1` routes logged with status codes and timing
- **GitHub Issues**: Check repo for known issues

---

## 🔄 Quick Reference Card

| Task | Command |
|------|---------|
| **View last 200 logs** | `render logs -r srv-d44ak76uk2gs73a3psig --limit 200 --confirm -o text` |
| **Stream live** | `render logs -r srv-d44ak76uk2gs73a3psig --tail --confirm` |
| **Search errors** | `render logs -r srv-d44ak76uk2gs73a3psig --text "error" --limit 100 --confirm -o text` |
| **Check metrics** | `render logs -r srv-d44ak76uk2gs73a3psig --text "[METRICS]" --limit 50 --confirm -o text` |
| **Save to file** | `render logs -r srv-d44ak76uk2gs73a3psig --limit 500 --confirm -o text > logs.txt` |
| **View 401/403 errors** | `render logs -r srv-d44ak76uk2gs73a3psig --status-code 401,403 --limit 50 --confirm -o text` |
| **Find session logs** | `render logs -r srv-d44ak76uk2gs73a3psig --text "session_ID" --limit 200 --confirm -o text` |

---

**Last Updated**: November 9, 2025  
**Service ID**: `srv-d44ak76uk2gs73a3psig`  
**Verified Working**: ✅ Render CLI v2.5.0
