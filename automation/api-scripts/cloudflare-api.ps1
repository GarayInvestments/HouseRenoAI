# 🌤️ House Renovators AI Portal - Cloudflare API Utilities
# Comprehensive Cloudflare Pages management and operations

param(
    [Parameter(Position=0)]
    [ValidateSet("status", "deploy", "logs", "env", "purge", "analytics", "domains", "help")]
    [string]$Action = "status",
    
    [string]$ProjectId = $env:CF_PROJECT_ID,
    [string]$Token = $env:CF_API_TOKEN,
    [string]$AccountId = $env:CF_ACCOUNT_ID,
    [string]$Branch = "main",
    [string]$Environment,
    [string]$Domain,
    [hashtable]$Variables,
    [string]$OutputFile,
    [switch]$Json,
    [switch]$Watch,
    [int]$WatchInterval = 30,
    [switch]$Verbose
)

# Configuration
$BaseUrl = "https://api.cloudflare.com/client/v4"
$DefaultProject = "house-renovators-ai-portal"

# Validation
if (-not $Token) {
    Write-Error "Cloudflare API token required. Set CF_API_TOKEN environment variable or use -Token parameter."
    exit 1
}

if (-not $AccountId) {
    Write-Error "Cloudflare Account ID required. Set CF_ACCOUNT_ID environment variable or use -AccountId parameter."
    exit 1
}

if (-not $ProjectId) {
    $ProjectId = $DefaultProject
    if ($Verbose) { Write-Host "Using default project: $ProjectId" -ForegroundColor Yellow }
}

function Write-Output($message, $color = "White") {
    if ($Json -and $Action -ne "help") { return }
    Write-Host $message -ForegroundColor $color
}

function Invoke-CloudflareAPI($endpoint, $method = "GET", $body = $null) {
    try {
        $headers = @{
            "Authorization" = "Bearer $Token"
            "Content-Type" = "application/json"
        }
        
        $uri = "$BaseUrl$endpoint"
        if ($Verbose) { Write-Output "API Call: $method $uri" "Gray" }
        
        $params = @{
            Uri = $uri
            Method = $method
            Headers = $headers
            TimeoutSec = 60
        }
        
        if ($body) {
            $params.Body = $body | ConvertTo-Json -Depth 10
        }
        
        $response = Invoke-RestMethod @params
        return $response
    } catch {
        $errorDetails = $_.Exception.Message
        if ($_.Exception.Response) {
            try {
                $errorStream = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($errorStream)
                $errorBody = $reader.ReadToEnd()
                $errorDetails += " - $errorBody"
            } catch {
                # Ignore stream reading errors
            }
        }
        throw "Cloudflare API error: $errorDetails"
    }
}

function Get-ProjectStatus {
    Write-Output "`n🌤️ Cloudflare Pages Project Status" "Cyan"
    Write-Output "=" * 40
    
    try {
        # Get project details
        $project = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId"
        
        if ($Json) {
            return $project | ConvertTo-Json -Depth 10
        }
        
        $projectData = $project.result
        
        Write-Output "Project Name: $($projectData.name)" "White"
        Write-Output "ID: $($projectData.id)" "Gray"
        Write-Output "Created: $(([DateTime]$projectData.created_on).ToString('yyyy-MM-dd HH:mm:ss'))" "Gray"
        Write-Output "Status: $($projectData.deployment_configs.production.compatibility_date)" "Green"
        
        # Production URL
        if ($projectData.domains -and $projectData.domains.Count -gt 0) {
            Write-Output "`nDomains:" "Cyan"
            foreach ($domain in $projectData.domains) {
                $status = if ($domain.status -eq "active") { "✅" } else { "⚠️" }
                Write-Output "  $status $($domain.name)" "White"
            }
        }
        
        # Get recent deployments
        Write-Output "`nRecent Deployments:" "Cyan"
        $deployments = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId/deployments?per_page=5"
        
        foreach ($deployment in $deployments.result) {
            $status = switch ($deployment.stage) {
                "success" { "✅" }
                "failure" { "❌" }
                "active" { "🔄" }
                default { "⏳" }
            }
            
            $env = if ($deployment.environment -eq "production") { "PROD" } else { "DEV" }
            $time = ([DateTime]$deployment.created_on).ToString('MM-dd HH:mm')
            
            Write-Output "  $status [$env] $($deployment.short_id) - $time" "White"
            if ($deployment.stage -eq "failure" -and $deployment.stage_message) {
                Write-Output "    Error: $($deployment.stage_message)" "Red"
            }
        }
        
        # Build configuration
        Write-Output "`nBuild Configuration:" "Cyan"
        $config = $projectData.deployment_configs.production
        Write-Output "  Build Command: $($config.build_command)" "Gray"
        Write-Output "  Output Directory: $($config.destination_dir)" "Gray"
        Write-Output "  Node Version: $($config.build_config.web_analytics_tag)" "Gray"
        
    } catch {
        Write-Error "Failed to get project status: $_"
        return $false
    }
}

function Start-Deployment {
    Write-Output "`n🚀 Triggering Cloudflare Pages Deployment" "Green"
    Write-Output "=" * 45
    
    try {
        # Cloudflare Pages deployments are typically triggered by Git pushes
        # For manual deployment, we can trigger a retry of the latest deployment
        
        $deployments = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId/deployments?per_page=1"
        $latestDeployment = $deployments.result[0]
        
        if (-not $latestDeployment) {
            Write-Error "No deployments found for project $ProjectId"
            return $false
        }
        
        Write-Output "Latest deployment: $($latestDeployment.short_id)" "White"
        Write-Output "Status: $($latestDeployment.stage)" "White"
        
        if ($latestDeployment.stage -in @("success", "active")) {
            Write-Output "Deployment already successful or in progress" "Yellow"
            return $true
        }
        
        # Retry deployment
        $retryResponse = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId/deployments/$($latestDeployment.id)/retry" "POST"
        
        if ($Json) {
            return $retryResponse | ConvertTo-Json -Depth 10
        }
        
        Write-Output "✅ Deployment retry triggered successfully" "Green"
        Write-Output "Deployment ID: $($retryResponse.result.id)" "White"
        
        if ($Watch) {
            Write-Output "`n👀 Watching deployment progress..." "Cyan"
            Watch-Deployment $retryResponse.result.id
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to start deployment: $_"
        return $false
    }
}

function Watch-Deployment($deploymentId) {
    do {
        Start-Sleep $WatchInterval
        
        try {
            $deployment = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId/deployments/$deploymentId"
            $stage = $deployment.result.stage
            $progress = [math]::Round($deployment.result.build_progress * 100, 1)
            
            $status = switch ($stage) {
                "queued" { "⏳ Queued" }
                "initialize" { "🔧 Initializing" }
                "clone_repo" { "📥 Cloning repository" }
                "build" { "🔨 Building ($progress%)" }
                "deploy" { "🚀 Deploying" }
                "success" { "✅ Success" }
                "failure" { "❌ Failed" }
                default { "📊 $stage" }
            }
            
            Write-Output "Status: $status" "White"
            
            if ($stage -in @("success", "failure")) {
                if ($stage -eq "success") {
                    Write-Output "🎉 Deployment completed successfully!" "Green"
                    Write-Output "URL: $($deployment.result.url)" "Cyan"
                } else {
                    Write-Output "💥 Deployment failed" "Red"
                    if ($deployment.result.stage_message) {
                        Write-Output "Error: $($deployment.result.stage_message)" "Red"
                    }
                }
                break
            }
            
        } catch {
            Write-Output "Error checking deployment status: $_" "Red"
            break
        }
        
    } while ($true)
}

function Get-DeploymentLogs {
    Write-Output "`n📋 Cloudflare Pages Deployment Logs" "Cyan"
    Write-Output "=" * 40
    
    try {
        $deployments = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId/deployments?per_page=5"
        
        if ($Json) {
            return $deployments | ConvertTo-Json -Depth 10
        }
        
        foreach ($deployment in $deployments.result) {
            $status = switch ($deployment.stage) {
                "success" { "✅" }
                "failure" { "❌" }
                "active" { "🔄" }
                default { "⏳" }
            }
            
            $time = ([DateTime]$deployment.created_on).ToString('yyyy-MM-dd HH:mm:ss')
            Write-Output "$status $($deployment.short_id) - $time [$($deployment.environment)]" "White"
            
            if ($deployment.stage_message) {
                Write-Output "  Message: $($deployment.stage_message)" "Gray"
            }
            
            if ($deployment.stage -eq "failure") {
                # Get detailed logs for failed deployments
                try {
                    $logs = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId/deployments/$($deployment.id)/history/logs"
                    if ($logs.result -and $logs.result.data) {
                        Write-Output "  Logs:" "Red"
                        foreach ($logEntry in $logs.result.data) {
                            Write-Output "    $($logEntry.message)" "Red"
                        }
                    }
                } catch {
                    Write-Output "  Could not retrieve detailed logs" "Yellow"
                }
            }
            
            Write-Output ""
        }
        
    } catch {
        Write-Error "Failed to get deployment logs: $_"
        return $false
    }
}

function Set-Environment {
    Write-Output "`n🔧 Cloudflare Pages Environment Variables" "Blue"
    Write-Output "=" * 45
    
    try {
        if ($Variables) {
            # Set environment variables
            Write-Output "Setting environment variables..." "White"
            
            $targetEnv = if ($Environment) { $Environment } else { "production" }
            Write-Output "Target environment: $targetEnv" "Gray"
            
            foreach ($key in $Variables.Keys) {
                $value = $Variables[$key]
                
                $body = @{
                    name = $key
                    value = $value
                    type = "plain_text"
                }
                
                try {
                    $null = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId/env_vars" "POST" $body
                    Write-Output "✅ Set $key" "Green"
                } catch {
                    Write-Output "❌ Failed to set $key`: $_" "Red"
                }
            }
        } else {
            # List environment variables
            $envVars = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId/env_vars"
            
            if ($Json) {
                return $envVars | ConvertTo-Json -Depth 10
            }
            
            if ($envVars.result -and $envVars.result.Count -gt 0) {
                Write-Output "Environment Variables:" "Cyan"
                foreach ($var in $envVars.result) {
                    $value = if ($var.value.Length -gt 20) { 
                        "$($var.value.Substring(0, 20))..." 
                    } else { 
                        $var.value 
                    }
                    Write-Output "  $($var.name) = $value" "White"
                }
            } else {
                Write-Output "No environment variables configured" "Yellow"
            }
        }
        
    } catch {
        Write-Error "Failed to manage environment variables: $_"
        return $false
    }
}

function Clear-Cache {
    Write-Output "`n🧹 Purging Cloudflare Cache" "Magenta"
    Write-Output "=" * 30
    
    try {
        # Get zones for the account to find the appropriate zone
        $zones = Invoke-CloudflareAPI "/zones?account.id=$AccountId"
        
        if (-not $zones.result -or $zones.result.Count -eq 0) {
            Write-Output "No zones found for account" "Yellow"
            return $false
        }
        
        foreach ($zone in $zones.result) {
            Write-Output "Purging cache for zone: $($zone.name)" "White"
            
            $purgeBody = @{
                purge_everything = $true
            }
            
            try {
                $null = Invoke-CloudflareAPI "/zones/$($zone.id)/purge_cache" "POST" $purgeBody
                Write-Output "✅ Cache purged for $($zone.name)" "Green"
            } catch {
                Write-Output "❌ Failed to purge cache for $($zone.name): $_" "Red"
            }
        }
        
        if ($Json) {
            return @{ status = "completed"; zones_purged = $zones.result.Count } | ConvertTo-Json
        }
        
    } catch {
        Write-Error "Failed to purge cache: $_"
        return $false
    }
}

function Get-Analytics {
    Write-Output "`n📊 Cloudflare Pages Analytics" "DarkYellow"
    Write-Output "=" * 35
    
    try {
        # Get project analytics
        $endDate = Get-Date
        $startDate = $endDate.AddDays(-7)
        
        $analytics = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId/analytics?since=$($startDate.ToString('yyyy-MM-ddTHH:mm:ssZ'))&until=$($endDate.ToString('yyyy-MM-ddTHH:mm:ssZ'))"
        
        if ($Json) {
            return $analytics | ConvertTo-Json -Depth 10
        }
        
        if ($analytics.result) {
            Write-Output "Analytics (Last 7 days):" "Cyan"
            Write-Output "Requests: $($analytics.result.requests || 'N/A')" "White"
            Write-Output "Bandwidth: $($analytics.result.bandwidth || 'N/A')" "White"
            Write-Output "Page Views: $($analytics.result.page_views || 'N/A')" "White"
        } else {
            Write-Output "Analytics data not available" "Yellow"
        }
        
    } catch {
        Write-Output "Analytics not available or error occurred: $_" "Yellow"
        return $false
    }
}

function Get-DomainStatus {
    Write-Output "`n🌐 Domain Configuration" "DarkCyan"
    Write-Output "=" * 25
    
    try {
        $project = Invoke-CloudflareAPI "/accounts/$AccountId/pages/projects/$ProjectId"
        
        if ($Json) {
            return $project.result.domains | ConvertTo-Json -Depth 10
        }
        
        if ($project.result.domains -and $project.result.domains.Count -gt 0) {
            foreach ($domain in $project.result.domains) {
                $status = switch ($domain.status) {
                    "active" { "✅ Active" }
                    "pending" { "⏳ Pending" }
                    "error" { "❌ Error" }
                    default { "📊 $($domain.status)" }
                }
                
                Write-Output "Domain: $($domain.name)" "White"
                Write-Output "Status: $status" "White"
                if ($domain.verification_data) {
                    Write-Output "Verification: Required" "Yellow"
                }
                Write-Output ""
            }
        } else {
            Write-Output "No custom domains configured" "Yellow"
            Write-Output "Default URL: https://$ProjectId.pages.dev" "Cyan"
        }
        
    } catch {
        Write-Error "Failed to get domain status: $_"
        return $false
    }
}

function Show-Help {
    Write-Host @"
🌤️ House Renovators AI Portal - Cloudflare API Utilities

USAGE:
    .\cloudflare-api.ps1 [ACTION] [OPTIONS]

ACTIONS:
    status      Show project status and recent deployments
    deploy      Trigger deployment (retry latest)
    logs        Show deployment logs and history
    env         Manage environment variables
    purge       Purge cache for all zones
    analytics   Show project analytics
    domains     Show domain configuration
    help        Show this help message

OPTIONS:
    -ProjectId      Project identifier (default: house-renovators-ai-portal)
    -Token          Cloudflare API token (or CF_API_TOKEN env var)
    -AccountId      Cloudflare Account ID (or CF_ACCOUNT_ID env var)
    -Branch         Branch for operations (default: main)
    -Environment    Environment (production/preview)
    -Variables      Hashtable of environment variables to set
    -Json           Output in JSON format
    -Watch          Watch deployment progress
    -WatchInterval  Watch interval in seconds (default: 30)
    -Verbose        Enable verbose output

EXAMPLES:
    # Check project status
    .\cloudflare-api.ps1 status

    # Trigger deployment and watch progress
    .\cloudflare-api.ps1 deploy -Watch

    # Set environment variables
    .\cloudflare-api.ps1 env -Variables @{API_URL="https://api.example.com"; DEBUG="true"}

    # View analytics in JSON format
    .\cloudflare-api.ps1 analytics -Json

    # Purge cache for all zones
    .\cloudflare-api.ps1 purge

ENVIRONMENT VARIABLES:
    CF_API_TOKEN    Cloudflare API token
    CF_ACCOUNT_ID   Cloudflare Account ID
    CF_PROJECT_ID   Project identifier (optional)

For more information, visit: https://developers.cloudflare.com/pages/
"@ -ForegroundColor Cyan
}

# Main execution
try {
    switch ($Action.ToLower()) {
        "status" { 
            Get-ProjectStatus 
        }
        "deploy" { 
            Start-Deployment 
        }
        "logs" { 
            Get-DeploymentLogs 
        }
        "env" { 
            Set-Environment 
        }
        "purge" { 
            Clear-Cache 
        }
        "analytics" { 
            Get-Analytics 
        }
        "domains" { 
            Get-DomainStatus 
        }
        "help" { 
            Show-Help 
        }
        default { 
            Write-Error "Unknown action: $Action. Use 'help' for usage information."
            exit 1
        }
    }
    
    if ($OutputFile -and -not $Json) {
        Write-Output "`n💾 Results saved to: $OutputFile" "Green"
    }
    
} catch {
    Write-Error "Script execution failed: $_"
    exit 1
}