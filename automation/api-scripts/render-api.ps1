# 🟢 Render API Integration Utilities
# Programmatic access to Render services for House Renovators AI Portal

param(
    [string]$Action = "status",
    [string]$ServiceId = "",
    [string]$ApiToken = $env:RENDER_API_KEY,
    [int]$LogLines = 50,
    [switch]$Json,
    [switch]$Verbose
)

# API Configuration
$BaseUrl = "https://api.render.com/v1"
$Headers = @{
    "Authorization" = "Bearer $ApiToken"
    "Content-Type" = "application/json"
}

function Write-Output($message, $color = "White") {
    if ($Json) { return }
    Write-Host $message -ForegroundColor $color
}

function Invoke-RenderAPI($endpoint, $method = "GET", $body = $null) {
    try {
        $uri = "$BaseUrl$endpoint"
        if ($Verbose) { Write-Output "API Call: $method $uri" "Gray" }
        
        $params = @{
            Uri = $uri
            Method = $method
            Headers = $Headers
        }
        
        if ($body) {
            $params.Body = $body | ConvertTo-Json -Depth 10
        }
        
        $response = Invoke-RestMethod @params
        return $response
    } catch {
        if ($Json) {
            return @{ error = $_.Exception.Message }
        } else {
            Write-Host "❌ API Error: $($_.Exception.Message)" -ForegroundColor Red
            return $null
        }
    }
}

function Get-ServiceInfo($serviceId) {
    if (-not $serviceId) {
        # Try to find House Renovators service
        $services = Invoke-RenderAPI "/services"
        if ($services) {
            $houseService = $services | Where-Object { 
                $_.name -like "*house-renovators*" -or 
                $_.name -like "*houserenoai*" -or
                $_.name -like "*house-reno*"
            }
            if ($houseService) {
                return $houseService[0]
            }
        }
        return $null
    } else {
        return Invoke-RenderAPI "/services/$serviceId"
    }
}

function Get-ServiceStatus($serviceId) {
    $service = Get-ServiceInfo $serviceId
    if (-not $service) {
        return @{ error = "Service not found" }
    }
    
    $deploys = Invoke-RenderAPI "/services/$($service.id)/deploys?limit=1"
    $latestDeploy = if ($deploys) { $deploys[0] } else { $null }
    
    return @{
        id = $service.id
        name = $service.name
        type = $service.type
        url = $service.serviceDetails.url
        region = $service.serviceDetails.region
        suspended = $service.suspended
        autoUpgrade = $service.serviceDetails.autoupgrade
        latestDeploy = if ($latestDeploy) {
            @{
                id = $latestDeploy.id
                status = $latestDeploy.status
                createdAt = $latestDeploy.createdAt
                finishedAt = $latestDeploy.finishedAt
            }
        } else { $null }
    }
}

function Get-ServiceLogs($serviceId, $lines = 50) {
    $service = Get-ServiceInfo $serviceId
    if (-not $service) {
        return @{ error = "Service not found" }
    }
    
    try {
        # Note: Render API doesn't directly support logs via REST API
        # This would typically use the Render CLI or WebSocket connections
        Write-Output "📋 Recent logs for $($service.name):" "Cyan"
        Write-Output "Use 'render logs --service $($service.id) --num $lines' for live logs" "Yellow"
        
        return @{
            message = "Use Render CLI for log access"
            command = "render logs --service $($service.id) --num $lines"
        }
    } catch {
        return @{ error = $_.Exception.Message }
    }
}

function Start-Deployment($serviceId) {
    $service = Get-ServiceInfo $serviceId
    if (-not $service) {
        return @{ error = "Service not found" }
    }
    
    $deployData = @{
        clearCache = $false
    }
    
    $result = Invoke-RenderAPI "/services/$($service.id)/deploys" "POST" $deployData
    return $result
}

function Get-EnvironmentVariables($serviceId) {
    $service = Get-ServiceInfo $serviceId
    if (-not $service) {
        return @{ error = "Service not found" }
    }
    
    $envVars = Invoke-RenderAPI "/services/$($service.id)/env-vars"
    return $envVars
}

function Get-ServiceMetrics($serviceId) {
    $service = Get-ServiceInfo $serviceId
    if (-not $service) {
        return @{ error = "Service not found" }
    }
    
    # Get recent deployments for metrics
    $deploys = Invoke-RenderAPI "/services/$($service.id)/deploys?limit=10"
    
    $metrics = @{
        serviceName = $service.name
        serviceId = $service.id
        serviceUrl = $service.serviceDetails.url
        totalDeploys = $deploys.Count
        recentDeploys = $deploys | ForEach-Object {
            @{
                id = $_.id
                status = $_.status
                createdAt = $_.createdAt
                finishedAt = $_.finishedAt
                buildDuration = if ($_.finishedAt -and $_.createdAt) {
                    try {
                        $start = [DateTime]::Parse($_.createdAt)
                        $end = [DateTime]::Parse($_.finishedAt)
                        [math]::Round(($end - $start).TotalMinutes, 1)
                    } catch { $null }
                } else { $null }
            }
        }
        healthStatus = "unknown"  # Would need to call health endpoint
    }
    
    return $metrics
}

# Main execution based on action
switch ($Action.ToLower()) {
    "status" {
        $result = Get-ServiceStatus $ServiceId
        if ($Json) {
            $result | ConvertTo-Json -Depth 10
        } else {
            if ($result.error) {
                Write-Output "❌ $($result.error)" "Red"
            } else {
                Write-Output "🟢 Render Service Status" "Green"
                Write-Output "=" * 30
                Write-Output "Name: $($result.name)" "White"
                Write-Output "ID: $($result.id)" "Gray"
                Write-Output "Type: $($result.type)" "White"
                Write-Output "URL: $($result.url)" "Cyan"
                Write-Output "Region: $($result.region)" "White"
                Write-Output "Suspended: $($result.suspended)" "White"
                
                if ($result.latestDeploy) {
                    Write-Output "`nLatest Deployment:" "Yellow"
                    Write-Output "  Status: $($result.latestDeploy.status)" "White"
                    Write-Output "  Created: $($result.latestDeploy.createdAt)" "Gray"
                    if ($result.latestDeploy.finishedAt) {
                        Write-Output "  Finished: $($result.latestDeploy.finishedAt)" "Gray"
                    }
                }
            }
        }
    }
    
    "deploy" {
        if (-not $ApiToken) {
            Write-Output "❌ RENDER_API_KEY environment variable required for deployments" "Red"
            exit 1
        }
        
        $result = Start-Deployment $ServiceId
        if ($Json) {
            $result | ConvertTo-Json -Depth 10
        } else {
            if ($result.error) {
                Write-Output "❌ Deployment failed: $($result.error)" "Red"
            } else {
                Write-Output "🚀 Deployment started successfully" "Green"
                Write-Output "Deploy ID: $($result.id)" "White"
                Write-Output "Status: $($result.status)" "White"
                Write-Output "Monitor with: render logs --service $ServiceId" "Cyan"
            }
        }
    }
    
    "logs" {
        $result = Get-ServiceLogs $ServiceId $LogLines
        if ($Json) {
            $result | ConvertTo-Json -Depth 10
        } else {
            Write-Output $result.message "Yellow"
            Write-Output "Command: $($result.command)" "Cyan"
        }
    }
    
    "env" {
        $result = Get-EnvironmentVariables $ServiceId
        if ($Json) {
            $result | ConvertTo-Json -Depth 10
        } else {
            if ($result.error) {
                Write-Output "❌ $($result.error)" "Red"
            } else {
                Write-Output "🔧 Environment Variables" "Cyan"
                Write-Output "=" * 25
                foreach ($envVar in $result) {
                    $value = if ($envVar.value.Length -gt 20) { 
                        "$($envVar.value.Substring(0, 20))..." 
                    } else { 
                        $envVar.value 
                    }
                    Write-Output "$($envVar.name): $value" "White"
                }
            }
        }
    }
    
    "metrics" {
        $result = Get-ServiceMetrics $ServiceId
        if ($Json) {
            $result | ConvertTo-Json -Depth 10
        } else {
            Write-Output "📊 Service Metrics" "Cyan"
            Write-Output "=" * 20
            Write-Output "Service: $($result.serviceName)" "White"
            Write-Output "Total Deployments: $($result.totalDeploys)" "White"
            Write-Output "Service URL: $($result.serviceUrl)" "Cyan"
            
            Write-Output "`nRecent Deployments:" "Yellow"
            foreach ($deploy in $result.recentDeploys | Select-Object -First 5) {
                $status = switch ($deploy.status) {
                    "live" { "🟢 Live" }
                    "failed" { "🔴 Failed" }
                    "build_in_progress" { "🟡 Building" }
                    default { "⚪ $($deploy.status)" }
                }
                $duration = if ($deploy.buildDuration) { " ($($deploy.buildDuration)m)" } else { "" }
                Write-Output "  $status - $($deploy.createdAt)$duration" "White"
            }
        }
    }
    
    "health" {
        $service = Get-ServiceInfo $ServiceId
        if ($service) {
            try {
                $healthUrl = "$($service.serviceDetails.url)/health"
                $healthResponse = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 15
                
                if ($Json) {
                    @{
                        url = $healthUrl
                        status = $healthResponse.status
                        response = $healthResponse
                    } | ConvertTo-Json -Depth 10
                } else {
                    Write-Output "🏥 Health Check" "Cyan"
                    Write-Output "=" * 15
                    Write-Output "URL: $healthUrl" "Gray"
                    Write-Output "Status: $($healthResponse.status)" "Green"
                    if ($healthResponse.api_version) {
                        Write-Output "API Version: $($healthResponse.api_version)" "White"
                    }
                }
            } catch {
                if ($Json) {
                    @{ error = "Health check failed: $($_.Exception.Message)" } | ConvertTo-Json
                } else {
                    Write-Output "❌ Health check failed: $($_.Exception.Message)" "Red"
                }
            }
        }
    }
    
    default {
        Write-Output "🟢 Render API Utilities" "Green"
        Write-Output "=" * 25
        Write-Output "Available actions:" "White"
        Write-Output "  status   - Get service status and latest deployment" "Gray"
        Write-Output "  deploy   - Trigger new deployment" "Gray"
        Write-Output "  logs     - Access service logs (requires CLI)" "Gray"
        Write-Output "  env      - List environment variables" "Gray"
        Write-Output "  metrics  - Get service metrics and deployment history" "Gray"
        Write-Output "  health   - Check service health endpoint" "Gray"
        Write-Output "`nUsage: .\render-api.ps1 -Action <action> [-ServiceId <id>] [-Json]" "Cyan"
        Write-Output "Example: .\render-api.ps1 -Action status -Json" "Yellow"
    }
}