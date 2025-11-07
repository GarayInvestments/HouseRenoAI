# Render API Deployment Guide

**Created**: November 6, 2025  
**Last Updated**: November 6, 2025  
**Use Case**: Deploying environment variables to Render via API when CLI doesn't support it

---

## 🎯 **Problem Statement**

**Challenge**: Need to programmatically add environment variables to Render service, but Render CLI v2.5.0 does not support environment variable management.

**Attempted Solutions**:
1. ❌ `render env set` - Command doesn't exist
2. ❌ `render env-vars set` - Unknown command
3. ❌ Interactive PowerShell script - Requires manual dashboard input
4. ✅ **Render REST API** - Direct API calls work

**Why This Matters**: When deploying integrations (like QuickBooks) that require multiple environment variables, manual dashboard entry is slow and error-prone. API automation is faster and repeatable.

---

## ✅ **Solution: Render REST API**

### **Prerequisites**

1. **Render API Key**:
   - Go to: https://dashboard.render.com/u/settings/api-keys
   - Click "Create API Key"
   - Copy the key (starts with `rnd_`)

2. **Set API Key in PowerShell**:
   ```powershell
   $env:RENDER_API_KEY = "rnd_your_key_here"
   ```

3. **Know Your Service Details**:
   - Service ID (e.g., `srv-d44ak76uk2gs73a3psig`)
   - Service name (e.g., `HouseRenoAI`)

---

## 📋 **Step-by-Step Process**

### **Step 1: Find Your Service ID**

```powershell
# Set up headers
$headers = @{
    "Authorization" = "Bearer $env:RENDER_API_KEY"
    "Accept" = "application/json"
}

# List all services
$services = Invoke-RestMethod -Uri "https://api.render.com/v1/services" -Headers $headers -Method Get

# Display services
$services | ForEach-Object {
    Write-Host "$($_.service.name) - ID: $($_.service.id)"
}

# Get specific service ID
$serviceId = $services[0].service.id
```

**Output Example**:
```
HouseRenoAI - ID: srv-d44ak76uk2gs73a3psig
```

---

### **Step 2: Get Current Environment Variables**

**Important**: Render requires you to send ALL environment variables when updating (PUT operation replaces entire list).

```powershell
$serviceId = "srv-d44ak76uk2gs73a3psig"
$envVarsUrl = "https://api.render.com/v1/services/$serviceId/env-vars"

# Get current variables
$currentVars = Invoke-RestMethod -Uri $envVarsUrl -Headers $headers -Method Get

# Display current variables
Write-Host "Current Environment Variables:"
$currentVars | ForEach-Object {
    Write-Host "  - $($_.envVar.key)"
}
```

**Output Example**:
```
Current Environment Variables:
  - GOOGLE_SERVICE_ACCOUNT_BASE64
  - OPENAI_API_KEY
  - SHEET_ID
  - PORT
  - DEBUG
```

---

### **Step 3: Add New Variables to Existing List**

```powershell
# Create array with all variables (existing + new)
$allVars = @()

# Add existing variables
foreach ($var in $currentVars) {
    $allVars += @{
        key = $var.envVar.key
        value = $var.envVar.value
    }
}

# Add new variables (QuickBooks example)
$allVars += @{ key = "QB_CLIENT_ID"; value = "ABqSaOOjjMosXSBWJCrvrLWgpH1KjiIDjzOMerAOw4yZp7Gcmm" }
$allVars += @{ key = "QB_CLIENT_SECRET"; value = "idSQXTLLqCpg91iw69FkWlSssVgILNBSToTuJaEX" }
$allVars += @{ key = "QB_REDIRECT_URI"; value = "https://houserenoai.onrender.com/v1/quickbooks/callback" }
$allVars += @{ key = "QB_ENVIRONMENT"; value = "sandbox" }

Write-Host "Total variables: $($allVars.Count) ($(($currentVars.Count)) existing + $(($allVars.Count - $currentVars.Count)) new)"
```

---

### **Step 4: Update Environment Variables**

```powershell
# Add Content-Type header
$headers["Content-Type"] = "application/json"

# Convert to JSON
$body = @($allVars) | ConvertTo-Json -Depth 5

# Update variables (PUT replaces all)
Write-Host "Updating environment variables..." -ForegroundColor Cyan

try {
    $result = Invoke-RestMethod -Uri $envVarsUrl -Headers $headers -Method Put -Body $body
    Write-Host "✅ Environment variables updated successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
```

---

### **Step 5: Trigger Deployment**

**Note**: Adding environment variables does NOT automatically trigger a deployment. You must manually trigger one.

```powershell
$deployUrl = "https://api.render.com/v1/services/$serviceId/deploys"

$body = '{"clearCache":"do_not_clear"}'

Write-Host "🚀 Triggering deployment..." -ForegroundColor Cyan

try {
    $deploy = Invoke-RestMethod -Uri $deployUrl -Headers $headers -Method Post -Body $body
    
    Write-Host "✅ Deployment triggered!" -ForegroundColor Green
    Write-Host "   Deploy ID: $($deploy.id)" -ForegroundColor Gray
    Write-Host "   Status: $($deploy.status)" -ForegroundColor Gray
    
    # Save deploy ID for monitoring
    $deployId = $deploy.id
} catch {
    Write-Host "❌ Failed to trigger deployment: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
```

---

### **Step 6: Monitor Deployment Status**

```powershell
$deployUrl = "https://api.render.com/v1/services/$serviceId/deploys/$deployId"

# Check status
Write-Host "`n📦 Checking deployment status..." -ForegroundColor Cyan

$deploy = Invoke-RestMethod -Uri $deployUrl -Headers $headers -Method Get

Write-Host "   Status: $($deploy.status)" -ForegroundColor $(
    if ($deploy.status -eq 'live') { 'Green' } 
    elseif ($deploy.status -eq 'build_failed') { 'Red' }
    else { 'Yellow' }
)
Write-Host "   Created: $($deploy.createdAt)" -ForegroundColor Gray
Write-Host "   Updated: $($deploy.updatedAt)" -ForegroundColor Gray

# Deployment statuses:
# - build_in_progress
# - build_failed
# - live
```

---

### **Step 7: Verify Variables Were Added**

```powershell
# Get updated environment variables
$vars = Invoke-RestMethod -Uri $envVarsUrl -Headers $headers -Method Get

Write-Host "`n✅ Current Environment Variables:" -ForegroundColor Green

$vars | ForEach-Object {
    $key = $_.envVar.key
    $isNew = $key -like "QB_*"  # Adjust pattern for your new vars
    
    if ($isNew) {
        Write-Host "  ✅ $key (NEW)" -ForegroundColor Cyan
    } else {
        Write-Host "  - $key" -ForegroundColor Gray
    }
}

# Count new variables
$newCount = ($vars | Where-Object { $_.envVar.key -like "QB_*" }).Count
Write-Host "`n📊 New variables added: $newCount/4" -ForegroundColor Yellow
```

---

## 🚀 **Quick Reference Script**

**Complete script for future deployments**:

```powershell
# === CONFIGURATION ===
$serviceId = "srv-d44ak76uk2gs73a3psig"  # Your service ID
$newVars = @(
    @{ key = "NEW_VAR_1"; value = "value1" }
    @{ key = "NEW_VAR_2"; value = "value2" }
)

# === SETUP ===
if (-not $env:RENDER_API_KEY) {
    Write-Host "❌ Set RENDER_API_KEY first: `$env:RENDER_API_KEY = 'rnd_your_key'" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $env:RENDER_API_KEY"
    "Accept" = "application/json"
    "Content-Type" = "application/json"
}

$envVarsUrl = "https://api.render.com/v1/services/$serviceId/env-vars"
$deployUrl = "https://api.render.com/v1/services/$serviceId/deploys"

# === GET CURRENT VARS ===
Write-Host "📋 Fetching current variables..." -ForegroundColor Cyan
$currentVars = Invoke-RestMethod -Uri $envVarsUrl -Headers $headers -Method Get

# === MERGE VARS ===
$allVars = @()
foreach ($var in $currentVars) {
    $allVars += @{ key = $var.envVar.key; value = $var.envVar.value }
}
foreach ($var in $newVars) {
    $allVars += $var
}

Write-Host "   Total: $($allVars.Count) ($($currentVars.Count) existing + $($newVars.Count) new)" -ForegroundColor Gray

# === UPDATE VARS ===
Write-Host "🔧 Updating environment variables..." -ForegroundColor Cyan
$body = @($allVars) | ConvertTo-Json -Depth 5
$result = Invoke-RestMethod -Uri $envVarsUrl -Headers $headers -Method Put -Body $body
Write-Host "✅ Variables updated" -ForegroundColor Green

# === DEPLOY ===
Write-Host "🚀 Triggering deployment..." -ForegroundColor Cyan
$body = '{"clearCache":"do_not_clear"}'
$deploy = Invoke-RestMethod -Uri $deployUrl -Headers $headers -Method Post -Body $body
Write-Host "✅ Deploy started: $($deploy.id)" -ForegroundColor Green

# === MONITOR ===
Write-Host "`n📦 Deployment in progress..." -ForegroundColor Yellow
Write-Host "   Monitor at: https://dashboard.render.com" -ForegroundColor Cyan
Write-Host "   ETA: 2-3 minutes" -ForegroundColor Gray
```

---

## 🔍 **Troubleshooting**

### **Issue 1: 405 Method Not Allowed**

**Problem**: Trying to POST individual env vars
```powershell
# ❌ WRONG - Returns 405
Invoke-RestMethod -Uri $envVarsUrl -Method Post -Body $singleVar
```

**Solution**: Use PUT with ALL variables (existing + new)
```powershell
# ✅ CORRECT
Invoke-RestMethod -Uri $envVarsUrl -Method Put -Body $allVars
```

---

### **Issue 2: Variables Not Taking Effect**

**Problem**: Updated vars but service still uses old values

**Solution**: Must trigger deployment after updating vars
```powershell
# Variables updated but NOT deployed yet
Invoke-RestMethod -Uri $envVarsUrl -Method Put -Body $allVars

# MUST trigger deploy
Invoke-RestMethod -Uri $deployUrl -Method Post -Body '{"clearCache":"do_not_clear"}'
```

---

### **Issue 3: 401 Unauthorized**

**Problem**: API key not set or invalid

**Solution**: 
1. Check API key is set: `$env:RENDER_API_KEY`
2. Regenerate key if expired: https://dashboard.render.com/u/settings/api-keys
3. Ensure key starts with `rnd_`

---

### **Issue 4: Service Name vs Service ID**

**Problem**: Using service name instead of service ID

**Solution**: Always use service ID (starts with `srv-`)
```powershell
# ❌ WRONG
$serviceId = "HouseRenoAI"

# ✅ CORRECT
$serviceId = "srv-d44ak76uk2gs73a3psig"
```

---

### **Issue 5: Lost Existing Variables**

**Problem**: PUT replaces entire list - if you only send new vars, old ones are deleted

**Solution**: Always fetch existing vars first, then merge
```powershell
# Get existing
$currentVars = Invoke-RestMethod -Uri $envVarsUrl -Method Get

# Merge with new
$allVars = @()
foreach ($var in $currentVars) { $allVars += @{key=$var.envVar.key; value=$var.envVar.value} }
foreach ($newVar in $newVars) { $allVars += $newVar }

# Update with complete list
Invoke-RestMethod -Uri $envVarsUrl -Method Put -Body ($allVars | ConvertTo-Json)
```

---

## 📊 **API Endpoints Reference**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/services` | GET | List all services |
| `/v1/services/{id}` | GET | Get service details |
| `/v1/services/{id}/env-vars` | GET | List environment variables |
| `/v1/services/{id}/env-vars` | PUT | Update all environment variables |
| `/v1/services/{id}/deploys` | GET | List deployments |
| `/v1/services/{id}/deploys` | POST | Trigger new deployment |
| `/v1/services/{id}/deploys/{id}` | GET | Get deployment status |

---

## 🎯 **Real-World Example: QuickBooks Integration**

**Context**: Adding 4 QuickBooks OAuth environment variables to production backend

**Variables to Add**:
- `QB_CLIENT_ID` - OAuth client ID
- `QB_CLIENT_SECRET` - OAuth client secret
- `QB_REDIRECT_URI` - Callback URL
- `QB_ENVIRONMENT` - `sandbox` or `production`

**Commands Used**:
```powershell
# 1. Setup
$env:RENDER_API_KEY = "rnd_Neuz9MlvtsseujgY73iN4OZhlpEU"
$serviceId = "srv-d44ak76uk2gs73a3psig"
$headers = @{
    "Authorization" = "Bearer $env:RENDER_API_KEY"
    "Content-Type" = "application/json"
}

# 2. Get existing vars
$envVarsUrl = "https://api.render.com/v1/services/$serviceId/env-vars"
$currentVars = Invoke-RestMethod -Uri $envVarsUrl -Headers $headers -Method Get

# 3. Merge with new vars
$allVars = @()
foreach ($var in $currentVars) {
    $allVars += @{ key = $var.envVar.key; value = $var.envVar.value }
}
$allVars += @{ key = "QB_CLIENT_ID"; value = "ABqSaOOjjMosXSBWJCrvrLWgpH1KjiIDjzOMerAOw4yZp7Gcmm" }
$allVars += @{ key = "QB_CLIENT_SECRET"; value = "idSQXTLLqCpg91iw69FkWlSssVgILNBSToTuJaEX" }
$allVars += @{ key = "QB_REDIRECT_URI"; value = "https://houserenoai.onrender.com/v1/quickbooks/callback" }
$allVars += @{ key = "QB_ENVIRONMENT"; value = "sandbox" }

# 4. Update vars
$body = @($allVars) | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri $envVarsUrl -Headers $headers -Method Put -Body $body

# 5. Deploy
$deployUrl = "https://api.render.com/v1/services/$serviceId/deploys"
$deploy = Invoke-RestMethod -Uri $deployUrl -Headers $headers -Method Post -Body '{"clearCache":"do_not_clear"}'

# 6. Monitor
$deployId = $deploy.id
$statusUrl = "https://api.render.com/v1/services/$serviceId/deploys/$deployId"
Invoke-RestMethod -Uri $statusUrl -Headers $headers -Method Get | Select-Object -ExpandProperty status
```

**Result**: ✅ All 4 variables added, deployment triggered (ID: `dep-d46kvimuk2gs7388e0pg`)

---

## 🔐 **Security Best Practices**

1. **Never commit API keys to Git**:
   ```powershell
   # Store in environment variable
   $env:RENDER_API_KEY = "rnd_your_key"
   
   # Or use .env file (excluded from Git)
   Get-Content .env | ForEach-Object {
       if ($_ -match "^RENDER_API_KEY=(.+)$") {
           $env:RENDER_API_KEY = $matches[1]
       }
   }
   ```

2. **Rotate API keys regularly**:
   - Delete old keys after creating new ones
   - Use separate keys for different projects/environments

3. **Mask secrets in logs**:
   ```powershell
   # Display masked value
   $value = "idSQXTLLqCpg91iw69FkWlSssVgILNBSToTuJaEX"
   $masked = $value.Substring(0, 10) + "..."
   Write-Host "QB_CLIENT_SECRET = $masked"
   ```

4. **Use least privilege**:
   - Create API keys with minimal required permissions
   - Use separate keys for read-only vs. write operations

---

## 📚 **Additional Resources**

- **Render API Documentation**: https://api-docs.render.com/
- **Render Dashboard**: https://dashboard.render.com
- **API Keys Management**: https://dashboard.render.com/u/settings/api-keys
- **Service Logs**: `render logs -s <service-name>`

---

## ✅ **Success Criteria**

After running the deployment:
- [ ] All new variables appear in Render dashboard
- [ ] Deployment triggered and shows "live" status
- [ ] Service restarts with new environment variables
- [ ] Application can access new variables (test via API endpoint)
- [ ] No existing variables were lost

**Verification**:
```powershell
# Check variables
curl https://your-app.onrender.com/health

# Test new feature (QuickBooks example)
curl https://houserenoai.onrender.com/v1/quickbooks/status
```

---

**Last Successful Deployment**: November 6, 2025 @ 8:47 PM PST  
**Deploy ID**: dep-d46kvimuk2gs7388e0pg  
**Variables Added**: 4 (QB_CLIENT_ID, QB_CLIENT_SECRET, QB_REDIRECT_URI, QB_ENVIRONMENT)
