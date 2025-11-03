# 🔔 House Renovators AI Portal - Continuous Monitoring & Alerting
# Automated health monitoring with intelligent notifications

param(
    [int]$HealthCheckInterval = 300,    # 5 minutes
    [int]$MetricsInterval = 900,        # 15 minutes
    [int]$AlertThreshold = 3,           # Alert after 3 consecutive failures
    [string]$WebhookUrl = $env:CHAT_WEBHOOK_URL,
    [string]$SlackWebhook = $env:SLACK_WEBHOOK_URL,
    [string]$TeamsWebhook = $env:TEAMS_WEBHOOK_URL,
    [string]$LogFile = "monitoring.log",
    [switch]$EnableMetrics,
    [switch]$EnableAlerts,
    [switch]$EnableDashboard,
    [switch]$Verbose,
    [switch]$Json
)

# Global state tracking
$Script:MonitoringState = @{
    StartTime = Get-Date
    HealthChecks = @()
    Metrics = @()
    Alerts = @()
    ConsecutiveFailures = 0
    LastNotification = $null
    IsRunning = $true
}

$Script:HealthHistory = @{}
$Script:MetricsHistory = @{}

function Write-Log($message, $level = "INFO", $color = "White") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$level] $message"
    
    # Write to console if not JSON mode
    if (-not $Json) {
        Write-Host $logEntry -ForegroundColor $color
    }
    
    # Write to log file
    if ($LogFile) {
        Add-Content -Path $LogFile -Value $logEntry
    }
    
    # Add to monitoring state
    $Script:MonitoringState.HealthChecks += @{
        timestamp = Get-Date
        level = $level
        message = $message
    }
}

function Test-ComponentHealth($component, $url, $timeout = 30) {
    try {
        Write-Log "Testing $component health: $url" "DEBUG" "Gray"
        
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri $url -TimeoutSec $timeout -ErrorAction Stop
        $responseTime = [math]::Round(((Get-Date) - $startTime).TotalMilliseconds, 0)
        
        $result = @{
            component = $component
            status = "healthy"
            responseTime = $responseTime
            timestamp = Get-Date
            url = $url
            details = $response
        }
        
        Write-Log "✅ $component: Healthy ($($responseTime)ms)" "INFO" "Green"
        return $result
        
    } catch {
        $result = @{
            component = $component
            status = "error"
            error = $_.Exception.Message
            timestamp = Get-Date
            url = $url
        }
        
        Write-Log "❌ $component: $($_.Exception.Message)" "ERROR" "Red"
        return $result
    }
}

function Perform-ComprehensiveHealthCheck {
    Write-Log "🏥 Starting comprehensive health check" "INFO" "Cyan"
    
    $healthResults = @{
        timestamp = Get-Date
        overall = "unknown"
        components = @{}
        issues = @()
        metrics = @{}
    }
    
    # Backend API Health
    $backendHealth = Test-ComponentHealth "Backend API" "https://houserenoai.onrender.com/health"
    $healthResults.components.backend = $backendHealth
    
    # Backend Debug Endpoint
    $debugHealth = Test-ComponentHealth "Debug Endpoint" "https://houserenoai.onrender.com/debug/"
    $healthResults.components.debug = $debugHealth
    
    # Permit Data API
    $permitsHealth = Test-ComponentHealth "Permits API" "https://houserenoai.onrender.com/v1/permits/"
    $healthResults.components.permits = $permitsHealth
    
    # Chat Status API
    $chatHealth = Test-ComponentHealth "Chat Status" "https://houserenoai.onrender.com/v1/chat/status"
    $healthResults.components.chat = $chatHealth
    
    # Collect issues
    foreach ($component in $healthResults.components.Values) {
        if ($component.status -eq "error") {
            $healthResults.issues += "$($component.component): $($component.error)"
        }
    }
    
    # Determine overall health
    $errorCount = $healthResults.issues.Count
    $healthResults.overall = switch ($errorCount) {
        0 { "healthy" }
        { $_ -le 1 } { "warning" }
        default { "critical" }
    }
    
    # Calculate performance metrics
    $healthyComponents = $healthResults.components.Values | Where-Object { $_.status -eq "healthy" }
    if ($healthyComponents.Count -gt 0) {
        $avgResponseTime = ($healthyComponents | Measure-Object responseTime -Average).Average
        $maxResponseTime = ($healthyComponents | Measure-Object responseTime -Maximum).Maximum
        
        $healthResults.metrics = @{
            averageResponseTime = [math]::Round($avgResponseTime, 0)
            maxResponseTime = $maxResponseTime
            healthyComponents = $healthyComponents.Count
            totalComponents = $healthResults.components.Count
            uptime = [math]::Round(((Get-Date) - $Script:MonitoringState.StartTime).TotalMinutes, 1)
        }
    }
    
    # Update failure tracking
    if ($healthResults.overall -eq "critical") {
        $Script:MonitoringState.ConsecutiveFailures++
    } else {
        $Script:MonitoringState.ConsecutiveFailures = 0
    }
    
    # Store health history
    $componentKey = $healthResults.timestamp.ToString("yyyy-MM-dd HH:mm")
    $Script:HealthHistory[$componentKey] = $healthResults
    
    # Cleanup old history (keep last 24 hours)
    $cutoffTime = (Get-Date).AddHours(-24)
    $keysToRemove = $Script:HealthHistory.Keys | Where-Object { 
        [DateTime]::ParseExact($_, "yyyy-MM-dd HH:mm", $null) -lt $cutoffTime 
    }
    foreach ($key in $keysToRemove) {
        $Script:HealthHistory.Remove($key)
    }
    
    return $healthResults
}

function Collect-SystemMetrics {
    Write-Log "📊 Collecting system metrics" "INFO" "Blue"
    
    try {
        $metrics = @{
            timestamp = Get-Date
            system = @{
                cpuUsage = (Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 1).CounterSamples.CookedValue
                memoryUsage = [math]::Round((Get-WmiObject Win32_OperatingSystem).TotalVisibleMemorySize / 1MB, 2)
                diskSpace = Get-WmiObject Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 } | ForEach-Object {
                    @{
                        drive = $_.DeviceID
                        freeSpace = [math]::Round($_.FreeSpace / 1GB, 2)
                        totalSpace = [math]::Round($_.Size / 1GB, 2)
                        percentFree = [math]::Round(($_.FreeSpace / $_.Size) * 100, 1)
                    }
                }
            }
            network = @{
                timestamp = Get-Date
                # Network metrics would be collected here
                # This is a placeholder for network monitoring
            }
            performance = @{
                healthCheckCount = $Script:MonitoringState.HealthChecks.Count
                alertCount = $Script:MonitoringState.Alerts.Count
                uptime = [math]::Round(((Get-Date) - $Script:MonitoringState.StartTime).TotalMinutes, 1)
            }
        }
        
        # Store metrics history
        $metricsKey = $metrics.timestamp.ToString("yyyy-MM-dd HH:mm")
        $Script:MetricsHistory[$metricsKey] = $metrics
        
        # Cleanup old metrics (keep last 24 hours)
        $cutoffTime = (Get-Date).AddHours(-24)
        $keysToRemove = $Script:MetricsHistory.Keys | Where-Object { 
            [DateTime]::ParseExact($_, "yyyy-MM-dd HH:mm", $null) -lt $cutoffTime 
        }
        foreach ($key in $keysToRemove) {
            $Script:MetricsHistory.Remove($key)
        }
        
        Write-Log "📈 Metrics collected: CPU $([math]::Round($metrics.system.cpuUsage, 1))%, Memory $($metrics.system.memoryUsage)GB" "INFO" "Blue"
        return $metrics
        
    } catch {
        Write-Log "❌ Failed to collect metrics: $_" "ERROR" "Red"
        return $null
    }
}

function Send-Alert($severity, $message, $details = $null) {
    if (-not $EnableAlerts) { return }
    
    $alert = @{
        timestamp = Get-Date
        severity = $severity
        message = $message
        details = $details
        consecutiveFailures = $Script:MonitoringState.ConsecutiveFailures
    }
    
    $Script:MonitoringState.Alerts += $alert
    
    # Rate limiting - don't send alerts more than once every 10 minutes for the same issue
    $now = Get-Date
    if ($Script:MonitoringState.LastNotification -and 
        ($now - $Script:MonitoringState.LastNotification).TotalMinutes -lt 10) {
        Write-Log "⏰ Alert rate limited: $message" "WARN" "Yellow"
        return
    }
    
    $emoji = switch ($severity) {
        "critical" { "🚨" }
        "warning" { "⚠️" }
        "info" { "ℹ️" }
        default { "📢" }
    }
    
    $alertMessage = "$emoji House Renovators AI Portal Alert`n"
    $alertMessage += "Severity: $severity`n"
    $alertMessage += "Message: $message`n"
    $alertMessage += "Time: $($now.ToString('yyyy-MM-dd HH:mm:ss'))`n"
    $alertMessage += "Consecutive Failures: $($Script:MonitoringState.ConsecutiveFailures)"
    
    if ($details) {
        $alertMessage += "`n`nDetails:`n$($details -join "`n")"
    }
    
    # Send to configured webhooks
    $sent = $false
    
    if ($WebhookUrl) {
        try {
            $payload = @{ text = $alertMessage } | ConvertTo-Json
            Invoke-RestMethod -Uri $WebhookUrl -Method POST -Body $payload -ContentType "application/json" | Out-Null
            $sent = $true
            Write-Log "📤 Alert sent to primary webhook" "INFO" "Green"
        } catch {
            Write-Log "❌ Failed to send alert to primary webhook: $_" "ERROR" "Red"
        }
    }
    
    if ($SlackWebhook) {
        try {
            $slackPayload = @{ 
                text = $alertMessage
                username = "House Renovators Monitor"
                icon_emoji = ":house:"
            } | ConvertTo-Json
            Invoke-RestMethod -Uri $SlackWebhook -Method POST -Body $slackPayload -ContentType "application/json" | Out-Null
            $sent = $true
            Write-Log "📤 Alert sent to Slack" "INFO" "Green"
        } catch {
            Write-Log "❌ Failed to send alert to Slack: $_" "ERROR" "Red"
        }
    }
    
    if ($TeamsWebhook) {
        try {
            $teamsPayload = @{
                "@type" = "MessageCard"
                "@context" = "http://schema.org/extensions"
                "themeColor" = if ($severity -eq "critical") { "FF0000" } elseif ($severity -eq "warning") { "FFFF00" } else { "0078D4" }
                "summary" = "House Renovators AI Portal Alert"
                "sections" = @(@{
                    "activityTitle" = "🏠 House Renovators AI Portal"
                    "activitySubtitle" = "System Monitoring Alert"
                    "facts" = @(
                        @{ "name" = "Severity"; "value" = $severity },
                        @{ "name" = "Message"; "value" = $message },
                        @{ "name" = "Time"; "value" = $now.ToString('yyyy-MM-dd HH:mm:ss') },
                        @{ "name" = "Consecutive Failures"; "value" = $Script:MonitoringState.ConsecutiveFailures }
                    )
                })
            } | ConvertTo-Json -Depth 10
            Invoke-RestMethod -Uri $TeamsWebhook -Method POST -Body $teamsPayload -ContentType "application/json" | Out-Null
            $sent = $true
            Write-Log "📤 Alert sent to Teams" "INFO" "Green"
        } catch {
            Write-Log "❌ Failed to send alert to Teams: $_" "ERROR" "Red"
        }
    }
    
    if ($sent) {
        $Script:MonitoringState.LastNotification = $now
    } else {
        Write-Log "⚠️ No notification webhooks configured" "WARN" "Yellow"
    }
}

function Generate-Dashboard {
    if (-not $EnableDashboard) { return }
    
    $dashboard = @{
        title = "🏠 House Renovators AI Portal - Monitoring Dashboard"
        generatedAt = Get-Date
        status = $Script:MonitoringState
        recentHealth = $Script:HealthHistory.Values | Sort-Object timestamp -Descending | Select-Object -First 10
        recentMetrics = $Script:MetricsHistory.Values | Sort-Object timestamp -Descending | Select-Object -First 10
        summary = @{
            uptime = [math]::Round(((Get-Date) - $Script:MonitoringState.StartTime).TotalHours, 1)
            totalChecks = $Script:MonitoringState.HealthChecks.Count
            totalAlerts = $Script:MonitoringState.Alerts.Count
            currentStatus = if ($Script:MonitoringState.ConsecutiveFailures -gt 0) { "degraded" } else { "healthy" }
        }
    }
    
    # Save dashboard to file
    $dashboardFile = "monitoring-dashboard.json"
    $dashboard | ConvertTo-Json -Depth 10 | Out-File -FilePath $dashboardFile -Encoding UTF8
    
    Write-Log "📊 Dashboard updated: $dashboardFile" "INFO" "Cyan"
}

function Show-MonitoringStatus {
    if ($Json) {
        $status = @{
            monitoring = $Script:MonitoringState
            recentHealth = $Script:HealthHistory.Values | Sort-Object timestamp -Descending | Select-Object -First 5
            recentMetrics = $Script:MetricsHistory.Values | Sort-Object timestamp -Descending | Select-Object -First 5
        }
        return $status | ConvertTo-Json -Depth 10
    }
    
    Write-Host "`n🔔 Continuous Monitoring Status" -ForegroundColor Cyan
    Write-Host "=" * 40
    Write-Host "Started: $($Script:MonitoringState.StartTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
    Write-Host "Uptime: $([math]::Round(((Get-Date) - $Script:MonitoringState.StartTime).TotalHours, 1)) hours" -ForegroundColor White
    Write-Host "Health Checks: $($Script:MonitoringState.HealthChecks.Count)" -ForegroundColor White
    Write-Host "Alerts Sent: $($Script:MonitoringState.Alerts.Count)" -ForegroundColor White
    Write-Host "Consecutive Failures: $($Script:MonitoringState.ConsecutiveFailures)" -ForegroundColor $(if ($Script:MonitoringState.ConsecutiveFailures -gt 0) { "Red" } else { "Green" })
    
    if ($Script:MonitoringState.LastNotification) {
        Write-Host "Last Alert: $($Script:MonitoringState.LastNotification.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Yellow
    }
    
    Write-Host "`nRecent Health Checks:" -ForegroundColor Cyan
    $Script:HealthHistory.Values | Sort-Object timestamp -Descending | Select-Object -First 5 | ForEach-Object {
        $status = switch ($_.overall) {
            "healthy" { "✅" }
            "warning" { "⚠️" }
            "critical" { "❌" }
            default { "❓" }
        }
        Write-Host "  $status $($_.timestamp.ToString('HH:mm:ss')) - $($_.overall) ($($_.issues.Count) issues)" -ForegroundColor White
    }
}

# Signal handlers for graceful shutdown
$Script:MonitoringState.IsRunning = $true

Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    Write-Host "`n🛑 Monitoring stopped gracefully" -ForegroundColor Yellow
    $Script:MonitoringState.IsRunning = $false
}

# Main monitoring loop
try {
    Write-Log "🚀 Starting House Renovators AI Portal monitoring" "INFO" "Green"
    Write-Log "Health Check Interval: $HealthCheckInterval seconds" "INFO" "White"
    Write-Log "Metrics Interval: $MetricsInterval seconds" "INFO" "White"
    Write-Log "Alert Threshold: $AlertThreshold consecutive failures" "INFO" "White"
    
    if ($EnableAlerts -and -not ($WebhookUrl -or $SlackWebhook -or $TeamsWebhook)) {
        Write-Log "⚠️ Alerts enabled but no webhook URLs configured" "WARN" "Yellow"
    }
    
    $lastHealthCheck = Get-Date
    $lastMetricsCollection = Get-Date
    
    while ($Script:MonitoringState.IsRunning) {
        $now = Get-Date
        
        # Perform health checks
        if (($now - $lastHealthCheck).TotalSeconds -ge $HealthCheckInterval) {
            $healthResults = Perform-ComprehensiveHealthCheck
            $lastHealthCheck = $now
            
            # Check for alerts
            if ($EnableAlerts -and $Script:MonitoringState.ConsecutiveFailures -ge $AlertThreshold) {
                $alertMessage = "System health critical - $($Script:MonitoringState.ConsecutiveFailures) consecutive failures"
                Send-Alert "critical" $alertMessage $healthResults.issues
            } elseif ($EnableAlerts -and $healthResults.overall -eq "warning") {
                Send-Alert "warning" "System health degraded" $healthResults.issues
            }
        }
        
        # Collect metrics
        if ($EnableMetrics -and ($now - $lastMetricsCollection).TotalSeconds -ge $MetricsInterval) {
            Collect-SystemMetrics
            $lastMetricsCollection = $now
        }
        
        # Update dashboard
        if ($EnableDashboard) {
            Generate-Dashboard
        }
        
        # Sleep for a short interval
        Start-Sleep 10
        
        # Check if we should continue (for interactive monitoring)
        if (-not $Script:MonitoringState.IsRunning) {
            break
        }
    }
    
} catch {
    Write-Log "💥 Monitoring error: $_" "ERROR" "Red"
    if ($EnableAlerts) {
        Send-Alert "critical" "Monitoring system error: $_"
    }
} finally {
    Write-Log "🏁 Monitoring session ended" "INFO" "Yellow"
    
    # Show final status
    if (-not $Json) {
        Show-MonitoringStatus
    }
    
    Write-Log "📊 Total runtime: $([math]::Round(((Get-Date) - $Script:MonitoringState.StartTime).TotalMinutes, 1)) minutes" "INFO" "White"
}