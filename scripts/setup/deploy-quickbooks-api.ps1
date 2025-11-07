# Deploy QuickBooks to Render using Render API
# This script uses curl to interact with Render's REST API

Write-Host "🚀 Deploying QuickBooks to Render via API" -ForegroundColor Cyan
Write-Host ""

# Check for API key
$apiKey = $env:RENDER_API_KEY

if (-not $apiKey) {
    Write-Host "❌ RENDER_API_KEY not found in environment variables" -ForegroundColor Red
    Write-Host ""
    Write-Host "📝 To get your API key:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://dashboard.render.com/u/settings/api-keys" -ForegroundColor Cyan
    Write-Host "   2. Click 'Create API Key'" -ForegroundColor Cyan
    Write-Host "   3. Copy the key" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then set it:" -ForegroundColor Yellow
    Write-Host '   $env:RENDER_API_KEY = "rnd_your_key_here"' -ForegroundColor Cyan
    Write-Host ""
    
    $input = Read-Host "Or paste your API key now (or press Enter to exit)"
    if ($input) {
        $apiKey = $input
        $env:RENDER_API_KEY = $apiKey
        Write-Host "✅ API key set for this session" -ForegroundColor Green
        Write-Host ""
    } else {
        exit 1
    }
}

# Step 1: Get service ID
Write-Host "🔍 Finding your service..." -ForegroundColor Cyan

$headers = @{
    "Authorization" = "Bearer $apiKey"
    "Accept" = "application/json"
}

$servicesUrl = "https://api.render.com/v1/services?name=house-renovators-ai-portal"

try {
    $response = Invoke-RestMethod -Uri $servicesUrl -Headers $headers -Method Get
    
    if ($response.PSObject.Properties['services'] -and $response.services.Count -gt 0) {
        $service = $response.services[0]
        $serviceId = $service.service.id
        $serviceName = $service.service.name
        
        Write-Host "✅ Found service: $serviceName" -ForegroundColor Green
        Write-Host "   Service ID: $serviceId" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "❌ Service 'house-renovators-ai-portal' not found" -ForegroundColor Red
        Write-Host ""
        Write-Host "Available services:" -ForegroundColor Yellow
        
        $allServicesUrl = "https://api.render.com/v1/services"
        $allResponse = Invoke-RestMethod -Uri $allServicesUrl -Headers $headers -Method Get
        
        foreach ($svc in $allResponse.services) {
            Write-Host "   - $($svc.service.name) (ID: $($svc.service.id))" -ForegroundColor Gray
        }
        exit 1
    }
} catch {
    Write-Host "❌ Failed to fetch services" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Check your API key is valid" -ForegroundColor Yellow
    exit 1
}

# Step 2: Get current environment variables
Write-Host "📋 Fetching current environment variables..." -ForegroundColor Cyan

$envVarsUrl = "https://api.render.com/v1/services/$serviceId/env-vars"

try {
    $currentEnvVars = Invoke-RestMethod -Uri $envVarsUrl -Headers $headers -Method Get
    Write-Host "✅ Found $($currentEnvVars.Count) existing environment variables" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "⚠️  Could not fetch current env vars, proceeding anyway..." -ForegroundColor Yellow
    Write-Host ""
}

# Step 3: Add QuickBooks environment variables
Write-Host "🔧 Adding QuickBooks environment variables..." -ForegroundColor Cyan
Write-Host ""

$qbEnvVars = @(
    @{
        key = "QB_CLIENT_ID"
        value = "ABqSaOOjjMosXSBWJCrvrLWgpH1KjiIDjzOMerAOw4yZp7Gcmm"
    },
    @{
        key = "QB_CLIENT_SECRET"
        value = "idSQXTLLqCpg91iw69FkWlSssVgILNBSToTuJaEX"
    },
    @{
        key = "QB_REDIRECT_URI"
        value = "https://houserenoai.onrender.com/v1/quickbooks/callback"
    },
    @{
        key = "QB_ENVIRONMENT"
        value = "sandbox"
    }
)

$successCount = 0
$headers["Content-Type"] = "application/json"

foreach ($envVar in $qbEnvVars) {
    $key = $envVar.key
    $value = $envVar.value
    
    # Display masked value for secrets
    $displayValue = $value
    if ($key -like "*SECRET*") {
        $displayValue = $value.Substring(0, 10) + "..."
    }
    
    Write-Host "   Adding $key = $displayValue" -ForegroundColor Gray
    
    $body = @{
        key = $key
        value = $value
    } | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Uri $envVarsUrl -Headers $headers -Method Post -Body $body
        Write-Host "   ✅ $key added successfully" -ForegroundColor Green
        $successCount++
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        
        if ($statusCode -eq 409) {
            # Variable already exists, try to update it
            Write-Host "   ⚠️  $key already exists, updating..." -ForegroundColor Yellow
            
            # Find the env var ID
            try {
                $existingVars = Invoke-RestMethod -Uri $envVarsUrl -Headers $headers -Method Get
                $existingVar = $existingVars | Where-Object { $_.envVar.key -eq $key } | Select-Object -First 1
                
                if ($existingVar) {
                    $envVarId = $existingVar.envVar.id
                    $updateUrl = "https://api.render.com/v1/services/$serviceId/env-vars/$envVarId"
                    
                    $updateResult = Invoke-RestMethod -Uri $updateUrl -Headers $headers -Method Put -Body $body
                    Write-Host "   ✅ $key updated successfully" -ForegroundColor Green
                    $successCount++
                }
            } catch {
                Write-Host "   ❌ Failed to update $key" -ForegroundColor Red
            }
        } else {
            Write-Host "   ❌ Failed to add $key (HTTP $statusCode)" -ForegroundColor Red
            Write-Host "      $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""

if ($successCount -eq $qbEnvVars.Count) {
    Write-Host "🎉 All $successCount environment variables added successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Added/updated $successCount of $($qbEnvVars.Count) variables" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📦 Triggering deployment..." -ForegroundColor Cyan

# Trigger a deploy
$deployUrl = "https://api.render.com/v1/services/$serviceId/deploys"

try {
    $deployBody = @{
        clearCache = "do_not_clear"
    } | ConvertTo-Json
    
    $deploy = Invoke-RestMethod -Uri $deployUrl -Headers $headers -Method Post -Body $deployBody
    
    Write-Host "✅ Deployment triggered!" -ForegroundColor Green
    Write-Host "   Deploy ID: $($deploy.id)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔍 Monitor deployment:" -ForegroundColor Yellow
    Write-Host "   Dashboard: https://dashboard.render.com" -ForegroundColor Cyan
    Write-Host "   Or run: render logs -s house-renovators-ai-portal" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ After deployment completes (2-3 min), test OAuth:" -ForegroundColor Yellow
    Write-Host "   https://houserenoai.onrender.com/v1/quickbooks/auth" -ForegroundColor Cyan
    
} catch {
    Write-Host "⚠️  Could not trigger deployment automatically" -ForegroundColor Yellow
    Write-Host "   The env vars are added, but you may need to manually deploy" -ForegroundColor Yellow
    Write-Host "   Go to: https://dashboard.render.com" -ForegroundColor Cyan
}

Write-Host ""
