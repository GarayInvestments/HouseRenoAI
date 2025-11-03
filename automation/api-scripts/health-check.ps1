# 🏥 House Renovators AI Portal - Automated Health Check & Monitoring
# Comprehensive health verification for the complete stack

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$Google,
    [switch]$AI,
    [switch]$All,
    [switch]$Json,
    [switch]$Continuous,
    [int]$Interval = 300,  # 5 minutes
    [switch]$Notify,
    [switch]$Verbose
)

# Default to all checks if no specific component specified
if (-not ($Backend -or $Frontend -or $Google -or $AI)) {
    $All = $true
}

$HealthResults = @{
    timestamp = Get-Date
    overall = "unknown"
    components = @{}
    issues = @()
    recommendations = @()
}

function Write-Output($message, $color = "White") {
    if ($Json) { return }
    Write-Host $message -ForegroundColor $color
}

function Test-HealthEndpoint($url, $timeout = 30, $componentName = "Service") {
    try {
        if ($Verbose) { Write-Output "Testing $componentName`: $url" "Gray" }
        
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri $url -TimeoutSec $timeout -ErrorAction Stop
        $responseTime = [math]::Round(((Get-Date) - $startTime).TotalMilliseconds, 0)
        
        return @{
            status = "healthy"
            responseTime = $responseTime
            response = $response
            url = $url
        }
    } catch {
        return @{
            status = "error"
            error = $_.Exception.Message
            url = $url
        }
    }
}

function Test-APIEndpoint($url, $method = "GET", $body = $null, $componentName = "API") {
    try {
        if ($Verbose) { Write-Output "Testing $componentName API: $method $url" "Gray" }
        
        $startTime = Get-Date
        $params = @{
            Uri = $url
            Method = $method
            TimeoutSec = 45
            ErrorAction = "Stop"
        }
        
        if ($body) {
            $params.Body = $body | ConvertTo-Json
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        $responseTime = [math]::Round(((Get-Date) - $startTime).TotalMilliseconds, 0)
        
        return @{
            status = "healthy"
            responseTime = $responseTime
            response = $response
            url = $url
        }
    } catch {
        return @{
            status = "error"
            error = $_.Exception.Message
            url = $url
        }
    }
}

function Send-HealthNotification($overallStatus, $issues) {
    if (-not $Notify -or -not $env:CHAT_WEBHOOK_URL) { return }
    
    try {
        $emoji = if ($overallStatus -eq "healthy") { "✅" } else { "❌" }
        $message = "$emoji House Renovators AI Portal Health Check`n"
        $message += "Status: $overallStatus`n"
        $message += "Time: $(Get-Date -Format 'HH:mm:ss')"
        
        if ($issues.Count -gt 0) {
            $message += "`n`nIssues:"
            foreach ($issue in $issues) {
                $message += "`n• $issue"
            }
        }
        
        $payload = @{ text = $message } | ConvertTo-Json
        Invoke-RestMethod -Uri $env:CHAT_WEBHOOK_URL -Method POST -Body $payload -ContentType "application/json" | Out-Null
        
        if ($Verbose) { Write-Output "Health notification sent" "Green" }
    } catch {
        if ($Verbose) { Write-Output "Failed to send notification: $_" "Red" }
    }
}

function Test-BackendHealth {
    Write-Output "`n🟢 Backend Health Checks" "Green"
    Write-Output ("-" * 30)
    
    $backendResults = @{}
    
    # Main health endpoint
    $healthCheck = Test-HealthEndpoint "https://houserenoai.onrender.com/health" 30 "Backend Health"
    $backendResults.health = $healthCheck
    
    if ($healthCheck.status -eq "healthy") {
        Write-Output "✅ Backend API: Healthy ($($healthCheck.responseTime)ms)" "Green"
    } else {
        Write-Output "❌ Backend API: $($healthCheck.error)" "Red"
        $HealthResults.issues += "Backend API health check failed"
    }
    
    # Debug endpoint (Google service status)
    $debugCheck = Test-HealthEndpoint "https://houserenoai.onrender.com/debug/" 30 "Debug Info"
    $backendResults.debug = $debugCheck
    
    if ($debugCheck.status -eq "healthy") {
        Write-Output "✅ Debug endpoint: Accessible ($($debugCheck.responseTime)ms)" "Green"
        
        # Check Google service initialization
        $googleInit = $debugCheck.response.google_service_initialized
        if ($googleInit.credentials -and $googleInit.sheets_service -and $googleInit.drive_service) {
            Write-Output "✅ Google Services: All initialized" "Green"
        } else {
            Write-Output "⚠️  Google Services: Some services not initialized" "Yellow"
            $HealthResults.issues += "Google services partially initialized"
            $HealthResults.recommendations += "Check Google service account credentials"
        }
    } else {
        Write-Output "❌ Debug endpoint: $($debugCheck.error)" "Red"
        $HealthResults.issues += "Debug endpoint inaccessible"
    }
    
    # API Documentation
    $docsCheck = Test-HealthEndpoint "https://houserenoai.onrender.com/docs" 15 "API Docs"
    $backendResults.docs = $docsCheck
    
    if ($docsCheck.status -eq "healthy") {
        Write-Output "✅ API Documentation: Available" "Green"
    } else {
        Write-Output "⚠️  API Documentation: $($docsCheck.error)" "Yellow"
    }
    
    return $backendResults
}

function Test-GoogleIntegration {
    Write-Output "`n🔵 Google Integration Checks" "Blue"
    Write-Output ("-" * 35)
    
    $googleResults = @{}
    
    # Permit data endpoint
    $permitsCheck = Test-APIEndpoint "https://houserenoai.onrender.com/v1/permits/" "GET" $null "Permits API"
    $googleResults.permits = $permitsCheck
    
    if ($permitsCheck.status -eq "healthy") {
        $permitCount = if ($permitsCheck.response) { $permitsCheck.response.Count } else { 0 }
        Write-Output "✅ Permit Data: $permitCount permits loaded ($($permitsCheck.responseTime)ms)" "Green"
        
        if ($permitCount -eq 0) {
            $HealthResults.issues += "No permit data found"
            $HealthResults.recommendations += "Check Google Sheets connection and data"
        }
    } else {
        Write-Output "❌ Permit Data: $($permitsCheck.error)" "Red"
        $HealthResults.issues += "Failed to load permit data"
    }
    
    # Permit analysis endpoint
    $analysisCheck = Test-APIEndpoint "https://houserenoai.onrender.com/v1/permits/analyze" "POST" $null "Analysis API"
    $googleResults.analysis = $analysisCheck
    
    if ($analysisCheck.status -eq "healthy") {
        Write-Output "✅ Permit Analysis: Working ($($analysisCheck.responseTime)ms)" "Green"
    } else {
        Write-Output "❌ Permit Analysis: $($analysisCheck.error)" "Red"
        $HealthResults.issues += "Permit analysis endpoint failed"
    }
    
    return $googleResults
}

function Test-AIIntegration {
    Write-Output "`n🧠 AI Integration Checks" "Magenta"
    Write-Output ("-" * 30)
    
    $aiResults = @{}
    
    # Chat status endpoint
    $chatStatusCheck = Test-APIEndpoint "https://houserenoai.onrender.com/v1/chat/status" "GET" $null "Chat Status"
    $aiResults.status = $chatStatusCheck
    
    if ($chatStatusCheck.status -eq "healthy") {
        Write-Output "✅ Chat Status: Available ($($chatStatusCheck.responseTime)ms)" "Green"
        
        $response = $chatStatusCheck.response
        if ($response.openai_status -eq "connected") {
            Write-Output "✅ OpenAI Integration: Connected" "Green"
        } else {
            Write-Output "❌ OpenAI Integration: $($response.openai_status)" "Red"
            $HealthResults.issues += "OpenAI integration not connected"
        }
        
        if ($response.sheets_status -eq "connected") {
            Write-Output "✅ Sheets Integration: Connected" "Green"
        } else {
            Write-Output "❌ Sheets Integration: $($response.sheets_status)" "Red"
            $HealthResults.issues += "Sheets integration not connected"
        }
    } else {
        Write-Output "❌ Chat Status: $($chatStatusCheck.error)" "Red"
        $HealthResults.issues += "Chat status endpoint failed"
    }
    
    # Test chat endpoint with simple query
    $testMessage = @{ message = "Health check test - how many permits are there?" }
    $chatCheck = Test-APIEndpoint "https://houserenoai.onrender.com/v1/chat/" "POST" $testMessage "Chat API"
    $aiResults.chat = $chatCheck
    
    if ($chatCheck.status -eq "healthy") {
        Write-Output "✅ AI Chat: Responding ($($chatCheck.responseTime)ms)" "Green"
        
        $response = $chatCheck.response.response
        if ($response -and $response.Length -gt 10) {
            Write-Output "✅ AI Response Quality: Good ($(($response.Length)) chars)" "Green"
        } else {
            Write-Output "⚠️  AI Response Quality: Short or empty response" "Yellow"
            $HealthResults.recommendations += "Check AI response quality and context"
        }
    } else {
        Write-Output "❌ AI Chat: $($chatCheck.error)" "Red"
        $HealthResults.issues += "AI chat endpoint failed"
    }
    
    return $aiResults
}

function Test-FrontendHealth {
    Write-Output "`n🟠 Frontend Health Checks" "DarkYellow"
    Write-Output ("-" * 30)
    
    $frontendResults = @{}
    
    # This would check Cloudflare Pages deployment
    # For now, we'll simulate frontend checks
    Write-Output "ℹ️  Frontend health checks would test Cloudflare Pages deployment" "Cyan"
    Write-Output "   - PWA accessibility" "Gray"
    Write-Output "   - API connectivity from frontend" "Gray"
    Write-Output "   - Static asset loading" "Gray"
    
    $frontendResults.status = @{
        status = "info"
        message = "Frontend health checks not implemented yet"
    }
    
    return $frontendResults
}

# Main health check execution
do {
    if (-not $Json) {
        Write-Host "🏥 House Renovators AI Portal - Health Check" -ForegroundColor Cyan
        Write-Host ("=" * 55)
        Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
    }
    
    # Reset results for each iteration
    $HealthResults.issues = @()
    $HealthResults.recommendations = @()
    $HealthResults.components = @{}
    
    # Run component checks
    if ($All -or $Backend) {
        $HealthResults.components.backend = Test-BackendHealth
    }
    
    if ($All -or $Google) {
        $HealthResults.components.google = Test-GoogleIntegration
    }
    
    if ($All -or $AI) {
        $HealthResults.components.ai = Test-AIIntegration
    }
    
    if ($All -or $Frontend) {
        $HealthResults.components.frontend = Test-FrontendHealth
    }
    
    # Determine overall health
    $totalErrors = $HealthResults.issues.Count
    $HealthResults.overall = if ($totalErrors -eq 0) { "healthy" } elseif ($totalErrors -lt 3) { "warning" } else { "critical" }
    
    # Summary
    if ($Json) {
        $HealthResults | ConvertTo-Json -Depth 10
    } else {
        Write-Host "`n📊 Health Summary" -ForegroundColor Cyan
        Write-Host ("=" * 20)
        
        $overallColor = switch ($HealthResults.overall) {
            "healthy" { "Green" }
            "warning" { "Yellow" }
            "critical" { "Red" }
            default { "White" }
        }
        
        Write-Host "Overall Status: $($HealthResults.overall.ToUpper())" -ForegroundColor $overallColor
        Write-Host "Issues Found: $($HealthResults.issues.Count)" -ForegroundColor $(if ($HealthResults.issues.Count -eq 0) { "Green" } else { "Red" })
        Write-Host "Recommendations: $($HealthResults.recommendations.Count)" -ForegroundColor $(if ($HealthResults.recommendations.Count -eq 0) { "Green" } else { "Yellow" })
        
        if ($HealthResults.issues.Count -gt 0) {
            Write-Host "`n❌ Issues:" -ForegroundColor Red
            foreach ($issue in $HealthResults.issues) {
                Write-Host "  • $issue" -ForegroundColor Red
            }
        }
        
        if ($HealthResults.recommendations.Count -gt 0) {
            Write-Host "`n💡 Recommendations:" -ForegroundColor Yellow
            foreach ($rec in $HealthResults.recommendations) {
                Write-Host "  • $rec" -ForegroundColor Yellow
            }
        }
        
        Write-Host "`n✅ Health check completed at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
    }
    
    # Send notification if requested
    Send-HealthNotification $HealthResults.overall $HealthResults.issues
    
    # Wait for next iteration if continuous monitoring
    if ($Continuous) {
        if (-not $Json) {
            Write-Host "`n⏱️  Waiting $Interval seconds for next check..." -ForegroundColor Gray
            Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Gray
        }
        Start-Sleep $Interval
    }
    
} while ($Continuous)