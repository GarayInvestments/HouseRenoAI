# 🚀 Render CLI Setup and Authentication
# Configure Render CLI for House Renovators AI Portal backend management

param(
    [string]$ApiToken,
    [string]$ServiceName = "house-renovators-ai",
    [switch]$Verbose
)

Write-Host "🟢 Setting up Render CLI for House Renovators AI Portal..." -ForegroundColor Green
Write-Host "=" * 60

# Check if Render CLI is installed
if (-not (Get-Command "render" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Render CLI not found. Please run install-all-clis.ps1 first" -ForegroundColor Red
    exit 1
}

# Check current authentication status
Write-Host "`n🔍 Checking current Render CLI status..." -ForegroundColor Cyan
try {
    $currentAuth = render auth status 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Already authenticated with Render CLI" -ForegroundColor Green
        Write-Host $currentAuth
    }
} catch {
    Write-Host "❌ Not currently authenticated with Render CLI" -ForegroundColor Yellow
}

# Authenticate with Render
if (-not $ApiToken) {
    Write-Host "`n🔑 Render API Token required for authentication" -ForegroundColor Cyan
    Write-Host "Get your token from: https://dashboard.render.com/account/settings" -ForegroundColor Yellow
    $ApiToken = Read-Host "Enter your Render API Token (or press Enter to use interactive login)"
}

if ($ApiToken) {
    Write-Host "`n🔐 Authenticating with provided API token..." -ForegroundColor Cyan
    $env:RENDER_API_KEY = $ApiToken
    
    # Test authentication
    try {
        $services = render services list --output json 2>$null | ConvertFrom-Json
        if ($services) {
            Write-Host "✅ Successfully authenticated with Render CLI" -ForegroundColor Green
            Write-Host "Found $($services.Count) services in your account" -ForegroundColor White
        }
    } catch {
        Write-Host "❌ Authentication failed. Please check your API token." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n🔐 Starting interactive authentication..." -ForegroundColor Cyan
    try {
        render auth login
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully authenticated with Render CLI" -ForegroundColor Green
        } else {
            Write-Host "❌ Authentication failed" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Interactive authentication failed: $_" -ForegroundColor Red
        exit 1
    }
}

# List available services
Write-Host "`n📋 Available Render Services:" -ForegroundColor Cyan
try {
    $services = render services list --output json | ConvertFrom-Json
    
    $houseRenovatorsService = $null
    foreach ($service in $services) {
        $status = if ($service.suspended -eq "Yes") { "🔴 Suspended" } else { "🟢 Active" }
        Write-Host "  - $($service.name) ($($service.type)) - $status" -ForegroundColor White
        
        if ($service.name -like "*house-renovators*" -or $service.name -like "*houserenoai*") {
            $houseRenovatorsService = $service
        }
    }
    
    if ($houseRenovatorsService) {
        Write-Host "`n🎯 Found House Renovators service:" -ForegroundColor Green
        Write-Host "  Name: $($houseRenovatorsService.name)" -ForegroundColor White
        Write-Host "  ID: $($houseRenovatorsService.id)" -ForegroundColor White
        Write-Host "  Type: $($houseRenovatorsService.type)" -ForegroundColor White
        Write-Host "  URL: $($houseRenovatorsService.serviceDetails.url)" -ForegroundColor White
        
        # Save service ID for automation scripts
        $configPath = ".\automation\config\cli-config.json"
        if (-not (Test-Path ".\automation\config")) {
            New-Item -ItemType Directory -Path ".\automation\config" -Force | Out-Null
        }
        
        $config = @{
            render = @{
                serviceId = $houseRenovatorsService.id
                serviceName = $houseRenovatorsService.name
                serviceUrl = $houseRenovatorsService.serviceDetails.url
            }
        }
        
        $config | ConvertTo-Json -Depth 3 | Set-Content $configPath
        Write-Host "✅ Saved service configuration to $configPath" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ Failed to list services: $_" -ForegroundColor Red
}

# Test deployment capabilities
Write-Host "`n🧪 Testing Render CLI deployment capabilities..." -ForegroundColor Cyan
if ($houseRenovatorsService) {
    try {
        # Get recent deployments
        $deploys = render deploys list --service $houseRenovatorsService.id --limit 3 --output json | ConvertFrom-Json
        Write-Host "✅ Recent deployments:" -ForegroundColor Green
        foreach ($deploy in $deploys) {
            $status = switch ($deploy.status) {
                "live" { "🟢 Live" }
                "build_in_progress" { "🟡 Building" }
                "update_in_progress" { "🟡 Updating" }
                "failed" { "🔴 Failed" }
                default { "⚪ $($deploy.status)" }
            }
            Write-Host "  - $($deploy.id) - $status - $($deploy.createdAt)" -ForegroundColor White
        }
        
        # Get service logs (last 10 lines)
        Write-Host "`n📋 Recent service logs:" -ForegroundColor Cyan
        render logs --service $houseRenovatorsService.id --num 10
        
    } catch {
        Write-Host "⚠️  Could not fetch deployment info: $_" -ForegroundColor Yellow
    }
}

# Environment variable management test
Write-Host "`n🔧 Testing environment variable access..." -ForegroundColor Cyan
if ($houseRenovatorsService) {
    try {
        $envVars = render env list --service $houseRenovatorsService.id --output json | ConvertFrom-Json
        Write-Host "✅ Found $($envVars.Count) environment variables configured" -ForegroundColor Green
        
        # Check for key variables (without showing values)
        $keyVars = @("OPENAI_API_KEY", "SHEET_ID", "GOOGLE_CREDENTIALS_B64", "CHAT_WEBHOOK_URL")
        foreach ($keyVar in $keyVars) {
            $found = $envVars | Where-Object { $_.name -eq $keyVar }
            if ($found) {
                Write-Host "  ✅ $keyVar - Configured" -ForegroundColor Green
            } else {
                Write-Host "  ❌ $keyVar - Missing" -ForegroundColor Red
            }
        }
    } catch {
        Write-Host "⚠️  Could not access environment variables: $_" -ForegroundColor Yellow
    }
}

Write-Host "`n🚀 Render CLI Commands Reference:" -ForegroundColor Cyan
Write-Host "=" * 40
Write-Host "List services:     render services list" -ForegroundColor White
Write-Host "Deploy service:    render deploys create --service <service-id>" -ForegroundColor White
Write-Host "View logs:         render logs --service <service-id> --tail 100" -ForegroundColor White
Write-Host "List deployments:  render deploys list --service <service-id>" -ForegroundColor White
Write-Host "Environment vars:  render env list --service <service-id>" -ForegroundColor White
Write-Host "Service status:    render services get <service-id>" -ForegroundColor White

Write-Host "`n💡 Automation Usage:" -ForegroundColor Cyan
Write-Host "Service ID saved to: .\automation\config\cli-config.json" -ForegroundColor White
Write-Host "Use in scripts: `$config = Get-Content .\automation\config\cli-config.json | ConvertFrom-Json" -ForegroundColor White

Write-Host "`n✅ Render CLI setup complete!" -ForegroundColor Green
Write-Host "Next: Run .\automation\cli-tools\setup-wrangler-cli.ps1" -ForegroundColor Cyan