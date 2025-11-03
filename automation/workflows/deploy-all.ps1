# 🚀 House Renovators AI Portal - Complete Stack Deployment
# Orchestrates backend + frontend + notifications across all platforms

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$SkipTests,
    [switch]$SkipNotifications,
    [string]$Environment = "production",
    [switch]$Verbose,
    [switch]$Force
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host "🚀 House Renovators AI Portal - Full Stack Deployment" -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host "Environment: $Environment" -ForegroundColor White
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
Write-Host ""

# Load configuration
$configPath = ".\config\cli-config.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
    Write-Host "✅ Loaded configuration from $configPath" -ForegroundColor Green
} else {
    Write-Host "⚠️  Configuration file not found. Run CLI setup scripts first." -ForegroundColor Yellow
    $config = @{
        render = @{ serviceId = ""; serviceName = "house-renovators-ai" }
        cloudflare = @{ projectName = "house-renovators-pwa" }
    }
}

# Deployment tracking
$deploymentLog = @{
    startTime = Get-Date
    steps = @()
    errors = @()
    success = $false
}

function Add-DeploymentStep($step, $status, $details = "", $duration = 0) {
    $deploymentLog.steps += @{
        step = $step
        status = $status
        details = $details
        timestamp = Get-Date
        duration = $duration
    }
    
    $icon = switch ($status) {
        "success" { "✅" }
        "error" { "❌" }
        "warning" { "⚠️ " }
        "info" { "ℹ️ " }
        default { "🔄" }
    }
    
    Write-Host "$icon $step" -ForegroundColor $(if ($status -eq "error") { "Red" } elseif ($status -eq "warning") { "Yellow" } elseif ($status -eq "success") { "Green" } else { "White" })
    if ($details) {
        Write-Host "   $details" -ForegroundColor Gray
    }
}

function Test-CommandExists($command) {
    return [bool](Get-Command -Name $command -ErrorAction SilentlyContinue)
}

function Send-TeamNotification($message, $success = $true) {
    if ($SkipNotifications) { return }
    
    try {
        $webhookUrl = $env:CHAT_WEBHOOK_URL
        if (-not $webhookUrl) {
            Add-DeploymentStep "Team Notification" "warning" "CHAT_WEBHOOK_URL not configured"
            return
        }
        
        $emoji = if ($success) { "✅" } else { "❌" }
        $payload = @{
            text = "$emoji $message`n🕐 $(Get-Date -Format 'HH:mm:ss')"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri $webhookUrl -Method POST -Body $payload -ContentType "application/json"
        Add-DeploymentStep "Team Notification" "success" "Sent to Google Chat"
    } catch {
        Add-DeploymentStep "Team Notification" "error" "Failed: $_"
    }
}

# Pre-deployment checks
Write-Host "🔍 Pre-Deployment Checks" -ForegroundColor Cyan
Write-Host "-" * 30

# Check CLI tools
$requiredTools = @("render", "wrangler", "curl", "jq")
$missingTools = @()

foreach ($tool in $requiredTools) {
    if (Test-CommandExists $tool) {
        Add-DeploymentStep "CLI Check: $tool" "success"
    } else {
        Add-DeploymentStep "CLI Check: $tool" "error" "Not found"
        $missingTools += $tool
    }
}

if ($missingTools.Count -gt 0 -and -not $Force) {
    Write-Host "`n❌ Missing required tools: $($missingTools -join ', ')" -ForegroundColor Red
    Write-Host "Run .\automation\cli-tools\install-all-clis.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Environment check
$requiredEnvVars = @("OPENAI_API_KEY", "SHEET_ID")
foreach ($envVar in $requiredEnvVars) {
    if ([Environment]::GetEnvironmentVariable($envVar)) {
        Add-DeploymentStep "Environment: $envVar" "success"
    } else {
        Add-DeploymentStep "Environment: $envVar" "warning" "Not set locally"
    }
}

# Backend Deployment
if (-not $FrontendOnly) {
    Write-Host "`n🟢 Backend Deployment (Render)" -ForegroundColor Green
    Write-Host "-" * 40
    
    try {
        $startTime = Get-Date
        
        # Verify Render authentication
        $renderStatus = render auth status 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Render CLI not authenticated"
        }
        Add-DeploymentStep "Render Authentication" "success"
        
        # Get service information
        if ($config.render.serviceId) {
            $serviceId = $config.render.serviceId
        } else {
            # Try to find service by name
            $services = render services list --output json | ConvertFrom-Json
            $service = $services | Where-Object { $_.name -like "*house-renovators*" -or $_.name -like "*houserenoai*" }
            if ($service) {
                $serviceId = $service.id
                Add-DeploymentStep "Service Discovery" "success" "Found service: $($service.name)"
            } else {
                throw "Could not find House Renovators service"
            }
        }
        
        # Trigger deployment
        Add-DeploymentStep "Backend Deployment" "info" "Triggering deployment..."
        $deployResult = render deploys create --service $serviceId --confirm 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
            Add-DeploymentStep "Backend Deployment" "success" "Deployment triggered successfully" $duration
            
            # Wait for deployment to complete (optional)
            if (-not $SkipTests) {
                Add-DeploymentStep "Deployment Status" "info" "Waiting for deployment to complete..."
                Start-Sleep 30  # Give it time to start
                
                # Check deployment status
                $attempts = 0
                $maxAttempts = 20  # 10 minutes max
                do {
                    Start-Sleep 30
                    $attempts++
                    try {
                        $deploys = render deploys list --service $serviceId --limit 1 --output json | ConvertFrom-Json
                        $latestDeploy = $deploys[0]
                        $status = $latestDeploy.status
                        
                        Add-DeploymentStep "Deployment Status" "info" "Status: $status (attempt $attempts/$maxAttempts)"
                        
                        if ($status -eq "live") {
                            Add-DeploymentStep "Backend Deployment" "success" "Deployment completed successfully"
                            break
                        } elseif ($status -eq "failed") {
                            throw "Deployment failed"
                        }
                    } catch {
                        Add-DeploymentStep "Deployment Status" "warning" "Could not check status: $_"
                    }
                } while ($attempts -lt $maxAttempts)
                
                if ($attempts -ge $maxAttempts) {
                    Add-DeploymentStep "Deployment Status" "warning" "Timeout waiting for deployment"
                }
            }
        } else {
            throw "Deployment command failed: $deployResult"
        }
        
    } catch {
        Add-DeploymentStep "Backend Deployment" "error" $_
        $deploymentLog.errors += "Backend: $_"
    }
}

# Frontend Deployment
if (-not $BackendOnly) {
    Write-Host "`n🟠 Frontend Deployment (Cloudflare Pages)" -ForegroundColor DarkYellow
    Write-Host "-" * 50
    
    try {
        $startTime = Get-Date
        
        # Check if we're in the frontend directory or need to navigate
        $frontendPath = ".\house-renovators-pwa"
        if (-not (Test-Path $frontendPath)) {
            $frontendPath = "..\house-renovators-pwa"
        }
        
        if (Test-Path $frontendPath) {
            Push-Location $frontendPath
            Add-DeploymentStep "Frontend Directory" "success" "Found frontend at $frontendPath"
            
            # Check for build artifacts
            if (Test-Path ".\dist") {
                Add-DeploymentStep "Build Artifacts" "success" "Found existing build"
            } else {
                Add-DeploymentStep "Frontend Build" "info" "Building frontend..."
                npm run build
                if ($LASTEXITCODE -eq 0) {
                    Add-DeploymentStep "Frontend Build" "success" "Build completed"
                } else {
                    throw "Frontend build failed"
                }
            }
            
            # Deploy to Cloudflare Pages
            Add-DeploymentStep "Frontend Deployment" "info" "Deploying to Cloudflare Pages..."
            $projectName = if ($config.cloudflare.projectName) { $config.cloudflare.projectName } else { "house-renovators-pwa" }
            
            wrangler pages deploy dist --project-name=$projectName
            if ($LASTEXITCODE -eq 0) {
                $duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
                Add-DeploymentStep "Frontend Deployment" "success" "Deployed successfully" $duration
            } else {
                throw "Wrangler deployment failed"
            }
            
            Pop-Location
        } else {
            throw "Frontend directory not found"
        }
        
    } catch {
        if (Get-Location | Where-Object { $_.Path -ne $PWD.Path }) {
            Pop-Location
        }
        Add-DeploymentStep "Frontend Deployment" "error" $_
        $deploymentLog.errors += "Frontend: $_"
    }
}

# Post-Deployment Testing
if (-not $SkipTests) {
    Write-Host "`n🧪 Post-Deployment Testing" -ForegroundColor Magenta
    Write-Host "-" * 35
    
    # Test backend health
    if (-not $FrontendOnly) {
        try {
            $healthUrl = "https://houserenoai.onrender.com/health"
            Add-DeploymentStep "Backend Health Check" "info" "Testing $healthUrl"
            
            $healthResponse = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 30
            if ($healthResponse.status -eq "healthy") {
                Add-DeploymentStep "Backend Health Check" "success" "API is healthy"
            } else {
                Add-DeploymentStep "Backend Health Check" "warning" "Unexpected health status: $($healthResponse.status)"
            }
            
            # Test Google service
            $debugUrl = "https://houserenoai.onrender.com/debug/"
            $debugResponse = Invoke-RestMethod -Uri $debugUrl -TimeoutSec 30
            if ($debugResponse.google_service_initialized.credentials) {
                Add-DeploymentStep "Google Services Check" "success" "Google integration working"
            } else {
                Add-DeploymentStep "Google Services Check" "warning" "Google service issues detected"
            }
            
            # Test permit data
            $permitsUrl = "https://houserenoai.onrender.com/v1/permits/"
            $permitsResponse = Invoke-RestMethod -Uri $permitsUrl -TimeoutSec 30
            if ($permitsResponse -and $permitsResponse.Count -gt 0) {
                Add-DeploymentStep "Permit Data Check" "success" "Found $($permitsResponse.Count) permits"
            } else {
                Add-DeploymentStep "Permit Data Check" "warning" "No permit data found"
            }
            
        } catch {
            Add-DeploymentStep "Backend Testing" "error" "Health check failed: $_"
        }
    }
    
    # Test AI chat endpoint
    if (-not $FrontendOnly) {
        try {
            $chatUrl = "https://houserenoai.onrender.com/v1/chat/"
            $chatPayload = @{
                message = "Test deployment - how many permits are there?"
            } | ConvertTo-Json
            
            Add-DeploymentStep "AI Chat Test" "info" "Testing chat endpoint"
            $chatResponse = Invoke-RestMethod -Uri $chatUrl -Method POST -Body $chatPayload -ContentType "application/json" -TimeoutSec 45
            
            if ($chatResponse.response) {
                Add-DeploymentStep "AI Chat Test" "success" "AI responding correctly"
            } else {
                Add-DeploymentStep "AI Chat Test" "warning" "Unexpected chat response format"
            }
        } catch {
            Add-DeploymentStep "AI Chat Test" "error" "Chat test failed: $_"
        }
    }
}

# Deployment Summary
$deploymentLog.endTime = Get-Date
$deploymentLog.totalDuration = [math]::Round(($deploymentLog.endTime - $deploymentLog.startTime).TotalMinutes, 1)
$deploymentLog.success = $deploymentLog.errors.Count -eq 0

Write-Host "`n📊 Deployment Summary" -ForegroundColor Cyan
Write-Host "=" * 30
Write-Host "Started: $($deploymentLog.startTime.ToString('HH:mm:ss'))" -ForegroundColor White
Write-Host "Completed: $($deploymentLog.endTime.ToString('HH:mm:ss'))" -ForegroundColor White
Write-Host "Duration: $($deploymentLog.totalDuration) minutes" -ForegroundColor White
Write-Host "Steps completed: $($deploymentLog.steps.Count)" -ForegroundColor White

$successSteps = ($deploymentLog.steps | Where-Object { $_.status -eq "success" }).Count
$errorSteps = ($deploymentLog.steps | Where-Object { $_.status -eq "error" }).Count
$warningSteps = ($deploymentLog.steps | Where-Object { $_.status -eq "warning" }).Count

Write-Host "✅ Successful: $successSteps" -ForegroundColor Green
if ($warningSteps -gt 0) { Write-Host "⚠️  Warnings: $warningSteps" -ForegroundColor Yellow }
if ($errorSteps -gt 0) { Write-Host "❌ Errors: $errorSteps" -ForegroundColor Red }

# Final notifications
if ($deploymentLog.success) {
    Write-Host "`n🎉 Deployment completed successfully!" -ForegroundColor Green
    Send-TeamNotification "🚀 House Renovators AI Portal deployment completed successfully in $($deploymentLog.totalDuration) minutes" $true
    
    Write-Host "`n🔗 Live URLs:" -ForegroundColor Cyan
    Write-Host "Backend API: https://houserenoai.onrender.com" -ForegroundColor White
    Write-Host "API Docs: https://houserenoai.onrender.com/docs" -ForegroundColor White
    Write-Host "Health Check: https://houserenoai.onrender.com/health" -ForegroundColor White
    
} else {
    Write-Host "`n❌ Deployment completed with errors" -ForegroundColor Red
    Write-Host "Errors encountered:" -ForegroundColor Yellow
    foreach ($deployError in $deploymentLog.errors) {
        Write-Host "  - $deployError" -ForegroundColor Red
    }
    
    Send-TeamNotification "❌ House Renovators AI Portal deployment failed. Check logs for details." $false
    exit 1
}

Write-Host "`n✅ Deployment process complete!" -ForegroundColor Green