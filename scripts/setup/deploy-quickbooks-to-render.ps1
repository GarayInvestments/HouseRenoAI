# Deploy QuickBooks Environment Variables to Render
# Run this script to add QB config to your Render service

Write-Host "🚀 Deploying QuickBooks to Render..." -ForegroundColor Cyan
Write-Host ""

# Get service name
$serviceName = "house-renovators-ai-portal"

# QuickBooks environment variables
$envVars = @{
    "QB_CLIENT_ID" = "ABqSaOOjjMosXSBWJCrvrLWgpH1KjiIDjzOMerAOw4yZp7Gcmm"
    "QB_CLIENT_SECRET" = "idSQXTLLqCpg91iw69FkWlSssVgILNBSToTuJaEX"
    "QB_REDIRECT_URI" = "https://houserenoai.onrender.com/v1/quickbooks/callback"
    "QB_ENVIRONMENT" = "sandbox"
}

Write-Host "📋 Environment Variables to Add:" -ForegroundColor Yellow
foreach ($key in $envVars.Keys) {
    $displayValue = $envVars[$key]
    if ($key -eq "QB_CLIENT_SECRET") {
        $displayValue = $displayValue.Substring(0, 10) + "..." # Hide secret
    }
    Write-Host "   $key = $displayValue" -ForegroundColor Gray
}
Write-Host ""

# Check if logged in
Write-Host "🔐 Checking Render authentication..." -ForegroundColor Cyan
$whoami = render whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Not logged in to Render CLI" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run: render login" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Authenticated as: $whoami" -ForegroundColor Green
Write-Host ""

# List services to confirm service name
Write-Host "📋 Listing your Render services..." -ForegroundColor Cyan
render services list
Write-Host ""

# Prompt for confirmation
Write-Host "⚠️  This will add 4 QuickBooks environment variables to service: $serviceName" -ForegroundColor Yellow
Write-Host "   and trigger a new deployment." -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Continue? (y/n)"

if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🔧 Adding environment variables..." -ForegroundColor Cyan

# Add each environment variable
$successCount = 0
foreach ($key in $envVars.Keys) {
    Write-Host "   Adding $key..." -ForegroundColor Gray
    
    $value = $envVars[$key]
    $result = render env set $key=$value --service $serviceName 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $key added" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "   ❌ Failed to add $key" -ForegroundColor Red
        Write-Host "   Error: $result" -ForegroundColor Red
    }
}

Write-Host ""

if ($successCount -eq $envVars.Count) {
    Write-Host "🎉 All $successCount environment variables added successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 Render is now deploying your service..." -ForegroundColor Cyan
    Write-Host "   This will take 2-3 minutes" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔍 Monitor deployment:" -ForegroundColor Yellow
    Write-Host "   Dashboard: https://dashboard.render.com" -ForegroundColor Cyan
    Write-Host "   Or run: render services logs $serviceName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ After deployment completes, test OAuth:" -ForegroundColor Yellow
    Write-Host "   https://houserenoai.onrender.com/v1/quickbooks/auth" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Only $successCount/$($envVars.Count) variables added" -ForegroundColor Yellow
    Write-Host "   Check errors above and try again" -ForegroundColor Yellow
}

Write-Host ""
