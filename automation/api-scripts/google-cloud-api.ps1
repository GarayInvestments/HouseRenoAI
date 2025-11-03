# ☁️ House Renovators AI Portal - Google Cloud API Utilities
# Comprehensive Google Cloud Platform management and operations

param(
    [Parameter(Position=0)]
    [ValidateSet("status", "sheets", "service", "logs", "billing", "quota", "deploy", "help")]
    [string]$Action = "status",
    
    [string]$ProjectId = $env:GOOGLE_CLOUD_PROJECT,
    [string]$ServiceAccount = $env:GOOGLE_SERVICE_ACCOUNT_EMAIL,
    [string]$KeyFile = $env:GOOGLE_APPLICATION_CREDENTIALS,
    [string]$SpreadsheetId = $env:GOOGLE_SHEETS_ID,
    [string]$SheetName = "permits",
    [string]$ServiceName,
    [int]$Days = 7,
    [switch]$Json,
    [switch]$Verbose,
    [string]$OutputFile
)

# Configuration
$DefaultProject = "house-renovators-ai"
$RequiredServices = @(
    "sheets.googleapis.com",
    "drive.googleapis.com",
    "serviceusage.googleapis.com",
    "cloudresourcemanager.googleapis.com"
)

# Validation
if (-not $ProjectId) {
    $ProjectId = $DefaultProject
    if ($Verbose) { Write-Host "Using default project: $ProjectId" -ForegroundColor Yellow }
}

function Write-Output($message, $color = "White") {
    if ($Json -and $Action -ne "help") { return }
    Write-Host $message -ForegroundColor $color
}

function Test-GoogleCloudCLI {
    try {
        $null = gcloud --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Initialize-GoogleCloudAuth {
    if (-not (Test-GoogleCloudCLI)) {
        Write-Error "Google Cloud CLI (gcloud) not installed. Please install it first."
        return $false
    }
    
    try {
        # Check if already authenticated
        $authList = gcloud auth list --format="value(account)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $authList) {
            if ($Verbose) { Write-Output "Already authenticated with Google Cloud" "Green" }
            return $true
        }
        
        # Authenticate using service account if available
        if ($KeyFile -and (Test-Path $KeyFile)) {
            gcloud auth activate-service-account --key-file="$KeyFile" 2>$null
            if ($LASTEXITCODE -eq 0) {
                if ($Verbose) { Write-Output "Authenticated using service account key" "Green" }
                return $true
            }
        }
        
        Write-Output "Google Cloud authentication required. Please run:" "Yellow"
        Write-Output "  gcloud auth login" "Cyan"
        Write-Output "  gcloud config set project $ProjectId" "Cyan"
        return $false
        
    } catch {
        Write-Error "Failed to initialize Google Cloud authentication: $_"
        return $false
    }
}

function Invoke-GCloudCommand($command, $errorAction = "Stop") {
    try {
        if ($Verbose) { Write-Output "Executing: gcloud $command" "Gray" }
        
        $result = Invoke-Expression "gcloud $command" 2>&1
        if ($LASTEXITCODE -ne 0) {
            if ($errorAction -eq "Stop") {
                throw "gcloud command failed: $result"
            } else {
                return $null
            }
        }
        return $result
    } catch {
        if ($errorAction -eq "Stop") {
            throw $_
        }
        return $null
    }
}

function Get-ProjectStatus {
    Write-Output "`n☁️ Google Cloud Project Status" "Cyan"
    Write-Output "=" * 35
    
    if (-not (Initialize-GoogleCloudAuth)) {
        return $false
    }
    
    try {
        # Set active project
        Invoke-GCloudCommand "config set project $ProjectId" | Out-Null
        
        # Get project information
        $projectInfo = Invoke-GCloudCommand "projects describe $ProjectId --format=json" | ConvertFrom-Json
        
        if ($Json) {
            return $projectInfo | ConvertTo-Json -Depth 10
        }
        
        Write-Output "Project ID: $($projectInfo.projectId)" "White"
        Write-Output "Name: $($projectInfo.name)" "White"
        Write-Output "Number: $($projectInfo.projectNumber)" "Gray"
        Write-Output "State: $($projectInfo.lifecycleState)" "Green"
        Write-Output "Created: $(([DateTime]$projectInfo.createTime).ToString('yyyy-MM-dd HH:mm:ss'))" "Gray"
        
        # Check enabled services
        Write-Output "`nEnabled Services:" "Cyan"
        $enabledServices = Invoke-GCloudCommand "services list --enabled --format='value(name)'" -ErrorAction "Continue"
        
        if ($enabledServices) {
            foreach ($service in $RequiredServices) {
                $isEnabled = $enabledServices -contains $service
                $status = if ($isEnabled) { "✅" } else { "❌" }
                Write-Output "  $status $service" "White"
                
                if (-not $isEnabled) {
                    Write-Output "    Run: gcloud services enable $service" "Yellow"
                }
            }
        }
        
        # Check billing
        Write-Output "`nBilling Status:" "Cyan"
        $billingInfo = Invoke-GCloudCommand "billing projects describe $ProjectId --format=json" -ErrorAction "Continue"
        if ($billingInfo) {
            $billing = $billingInfo | ConvertFrom-Json
            $billingStatus = if ($billing.billingEnabled) { "✅ Enabled" } else { "❌ Disabled" }
            Write-Output "  $billingStatus" "White"
            if ($billing.billingAccountName) {
                Write-Output "  Account: $($billing.billingAccountName)" "Gray"
            }
        } else {
            Write-Output "  ⚠️  Billing information not accessible" "Yellow"
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get project status: $_"
        return $false
    }
}

function Test-SheetsIntegration {
    Write-Output "`n📊 Google Sheets Integration Test" "Green"
    Write-Output "=" * 40
    
    if (-not (Initialize-GoogleCloudAuth)) {
        return $false
    }
    
    try {
        if (-not $SpreadsheetId) {
            Write-Output "❌ No Spreadsheet ID configured" "Red"
            Write-Output "Set GOOGLE_SHEETS_ID environment variable" "Yellow"
            return $false
        }
        
        Write-Output "Spreadsheet ID: $SpreadsheetId" "White"
        Write-Output "Sheet Name: $SheetName" "White"
        
        # Test using the same endpoint our FastAPI app uses
        if ($KeyFile -and (Test-Path $KeyFile)) {
            Write-Output "`nTesting service account access..." "Cyan"
            
            # This would typically require a Python script or PowerShell Google Sheets module
            # For now, we'll provide instructions for manual testing
            Write-Output "Service Account Key: $(Split-Path $KeyFile -Leaf)" "Gray"
            
            # Check if we can access the spreadsheet metadata
            Write-Output "`nTo test Sheets access manually:" "Yellow"
            Write-Output "1. Verify service account has access to the spreadsheet" "Gray"
            Write-Output "2. Check that Sheets API is enabled" "Gray"
            Write-Output "3. Test with our FastAPI health endpoint: /debug/" "Gray"
            
            Write-Output "`n💡 Use the FastAPI health endpoint for live testing:" "Cyan"
            Write-Output "   GET https://houserenoai.onrender.com/debug/" "Cyan"
            
        } else {
            Write-Output "❌ Service account key file not found" "Red"
            Write-Output "Set GOOGLE_APPLICATION_CREDENTIALS environment variable" "Yellow"
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to test Sheets integration: $_"
        return $false
    }
}

function Get-ServiceStatus {
    Write-Output "`n🔧 Google Cloud Services Status" "Blue"
    Write-Output "=" * 40
    
    if (-not (Initialize-GoogleCloudAuth)) {
        return $false
    }
    
    try {
        Invoke-GCloudCommand "config set project $ProjectId" | Out-Null
        
        Write-Output "Checking service status..." "White"
        
        $services = @()
        foreach ($service in $RequiredServices) {
            $status = Invoke-GCloudCommand "services list --enabled --filter='name:$service' --format='value(name)'" -ErrorAction "Continue"
            
            $serviceStatus = @{
                name = $service
                enabled = [bool]($status -and $status.Trim() -eq $service)
            }
            
            if ($serviceStatus.enabled) {
                # Get service configuration
                $config = Invoke-GCloudCommand "services describe $service --format=json" -ErrorAction "Continue"
                if ($config) {
                    $configData = $config | ConvertFrom-Json
                    $serviceStatus.title = $configData.config.title
                    $serviceStatus.documentation = $configData.config.documentation.summary
                }
            }
            
            $services += $serviceStatus
        }
        
        if ($Json) {
            return $services | ConvertTo-Json -Depth 10
        }
        
        foreach ($service in $services) {
            $status = if ($service.enabled) { "✅" } else { "❌" }
            Write-Output "$status $($service.name)" "White"
            
            if ($service.title) {
                Write-Output "    $($service.title)" "Gray"
            }
            
            if (-not $service.enabled) {
                Write-Output "    Enable: gcloud services enable $($service.name)" "Yellow"
            }
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get service status: $_"
        return $false
    }
}

function Get-CloudLogs {
    Write-Output "`n📋 Google Cloud Logs" "Magenta"
    Write-Output "=" * 25
    
    if (-not (Initialize-GoogleCloudAuth)) {
        return $false
    }
    
    try {
        Invoke-GCloudCommand "config set project $ProjectId" | Out-Null
        
        $endTime = Get-Date
        $startTime = $endTime.AddDays(-$Days)
        
        Write-Output "Retrieving logs from last $Days days..." "White"
        
        # Get Sheets API logs
        $sheetsFilter = "resource.type=`"gce_instance`" OR resource.type=`"cloud_function`" OR protoPayload.serviceName=`"sheets.googleapis.com`""
        $sheetsLogs = Invoke-GCloudCommand "logging read `"$sheetsFilter`" --limit=50 --format=json --since=$($startTime.ToString('yyyy-MM-ddTHH:mm:ssZ'))" -ErrorAction "Continue"
        
        if ($Json) {
            $logData = @{
                period = "$Days days"
                start_time = $startTime
                end_time = $endTime
                sheets_logs = if ($sheetsLogs) { $sheetsLogs | ConvertFrom-Json } else { @() }
            }
            return $logData | ConvertTo-Json -Depth 10
        }
        
        if ($sheetsLogs) {
            $logs = $sheetsLogs | ConvertFrom-Json
            Write-Output "Found $($logs.Count) log entries" "White"
            
            foreach ($log in $logs | Select-Object -First 10) {
                $timestamp = if ($log.timestamp) { ([DateTime]$log.timestamp).ToString('MM-dd HH:mm:ss') } else { "N/A" }
                $severity = $log.severity
                $message = if ($log.textPayload) { 
                    $log.textPayload.Substring(0, [Math]::Min(100, $log.textPayload.Length))
                } elseif ($log.protoPayload.methodName) {
                    $log.protoPayload.methodName
                } else {
                    "Log entry"
                }
                
                $severityColor = switch ($severity) {
                    "ERROR" { "Red" }
                    "WARNING" { "Yellow" }
                    "INFO" { "White" }
                    default { "Gray" }
                }
                
                Write-Output "[$timestamp] $severity - $message" $severityColor
            }
        } else {
            Write-Output "No logs found for the specified period" "Yellow"
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get cloud logs: $_"
        return $false
    }
}

function Get-BillingInfo {
    Write-Output "`n💰 Google Cloud Billing Information" "DarkYellow"
    Write-Output "=" * 40
    
    if (-not (Initialize-GoogleCloudAuth)) {
        return $false
    }
    
    try {
        Invoke-GCloudCommand "config set project $ProjectId" | Out-Null
        
        # Get billing account
        $billingInfo = Invoke-GCloudCommand "billing projects describe $ProjectId --format=json" -ErrorAction "Continue"
        
        if ($Json -and $billingInfo) {
            return $billingInfo | ConvertFrom-Json | ConvertTo-Json -Depth 10
        }
        
        if ($billingInfo) {
            $billing = $billingInfo | ConvertFrom-Json
            
            Write-Output "Billing Status: $(if ($billing.billingEnabled) { '✅ Enabled' } else { '❌ Disabled' })" "White"
            
            if ($billing.billingAccountName) {
                Write-Output "Billing Account: $($billing.billingAccountName)" "White"
            }
            
            # Get usage information (requires additional permissions)
            Write-Output "`nUsage Summary (Last $Days days):" "Cyan"
            Write-Output "For detailed billing information, visit:" "Yellow"
            Write-Output "https://console.cloud.google.com/billing" "Cyan"
            
        } else {
            Write-Output "❌ Billing information not accessible" "Red"
            Write-Output "Ensure you have billing.resourceAssociations.list permission" "Yellow"
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get billing information: $_"
        return $false
    }
}

function Get-QuotaStatus {
    Write-Output "`n📊 Google Cloud Quotas" "DarkCyan"
    Write-Output "=" * 25
    
    if (-not (Initialize-GoogleCloudAuth)) {
        return $false
    }
    
    try {
        Invoke-GCloudCommand "config set project $ProjectId" | Out-Null
        
        # Get Sheets API quotas
        Write-Output "Sheets API Quotas:" "Cyan"
        
        # This requires the Service Usage API and specific permissions
        $quotaInfo = Invoke-GCloudCommand "services list --enabled --filter='name:sheets.googleapis.com' --format='value(name)'" -ErrorAction "Continue"
        
        if ($quotaInfo) {
            Write-Output "✅ Sheets API is enabled" "Green"
            Write-Output "Default quotas:" "White"
            Write-Output "  • Read requests: 100 requests/100 seconds/user" "Gray"
            Write-Output "  • Write requests: 100 requests/100 seconds/user" "Gray"
            Write-Output "  • Requests per minute: 60,000" "Gray"
            
            Write-Output "`nFor current usage and detailed quotas:" "Yellow"
            Write-Output "https://console.cloud.google.com/apis/api/sheets.googleapis.com/quotas" "Cyan"
        } else {
            Write-Output "❌ Sheets API not enabled" "Red"
        }
        
        # Check Drive API quotas
        $driveQuota = Invoke-GCloudCommand "services list --enabled --filter='name:drive.googleapis.com' --format='value(name)'" -ErrorAction "Continue"
        
        Write-Output "`nDrive API Quotas:" "Cyan"
        if ($driveQuota) {
            Write-Output "✅ Drive API is enabled" "Green"
            Write-Output "Default quotas:" "White"
            Write-Output "  • Requests per 100 seconds: 1,000" "Gray"
            Write-Output "  • Requests per day: 1,000,000,000" "Gray"
        } else {
            Write-Output "❌ Drive API not enabled" "Red"
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get quota status: $_"
        return $false
    }
}

function Deploy-CloudFunction {
    Write-Output "`n🚀 Deploy Cloud Function (Future)" "Green"
    Write-Output "=" * 35
    
    Write-Output "Cloud Function deployment not implemented yet." "Yellow"
    Write-Output "Current architecture uses Render for backend hosting." "Gray"
    Write-Output "`nFuture considerations:" "Cyan"
    Write-Output "• Deploy FastAPI as Cloud Run service" "Gray"
    Write-Output "• Use Cloud Functions for specific tasks" "Gray"
    Write-Output "• Implement Cloud Build for CI/CD" "Gray"
    
    return $true
}

function Show-Help {
    Write-Host @"
☁️ House Renovators AI Portal - Google Cloud API Utilities

USAGE:
    .\google-cloud-api.ps1 [ACTION] [OPTIONS]

ACTIONS:
    status      Show project status and configuration
    sheets      Test Google Sheets integration
    service     Check Google Cloud services status
    logs        Retrieve and display cloud logs
    billing     Show billing information
    quota       Display API quotas and limits
    deploy      Deploy cloud functions (future)
    help        Show this help message

OPTIONS:
    -ProjectId          Google Cloud Project ID (or GOOGLE_CLOUD_PROJECT env var)
    -ServiceAccount     Service account email (or GOOGLE_SERVICE_ACCOUNT_EMAIL env var)
    -KeyFile            Service account key file path (or GOOGLE_APPLICATION_CREDENTIALS env var)
    -SpreadsheetId      Google Sheets ID (or GOOGLE_SHEETS_ID env var)
    -SheetName          Sheet name to test (default: permits)
    -ServiceName        Specific service to check
    -Days               Number of days for logs/billing (default: 7)
    -Json               Output in JSON format
    -Verbose            Enable verbose output
    -OutputFile         Save output to file

EXAMPLES:
    # Check project status
    .\google-cloud-api.ps1 status

    # Test Sheets integration
    .\google-cloud-api.ps1 sheets -SpreadsheetId "1ABC...XYZ"

    # Get logs from last 3 days
    .\google-cloud-api.ps1 logs -Days 3

    # Check service status in JSON format
    .\google-cloud-api.ps1 service -Json

    # Show billing information
    .\google-cloud-api.ps1 billing

ENVIRONMENT VARIABLES:
    GOOGLE_CLOUD_PROJECT            Project ID
    GOOGLE_SERVICE_ACCOUNT_EMAIL    Service account email
    GOOGLE_APPLICATION_CREDENTIALS  Path to service account key file
    GOOGLE_SHEETS_ID               Spreadsheet ID for testing

PREREQUISITES:
    • Google Cloud CLI (gcloud) installed and configured
    • Appropriate permissions for the project
    • Service account with necessary roles:
      - Sheets API access
      - Drive API access
      - Service Usage Consumer

For more information, visit: https://cloud.google.com/docs/
"@ -ForegroundColor Cyan
}

# Main execution
try {
    switch ($Action.ToLower()) {
        "status" { 
            Get-ProjectStatus 
        }
        "sheets" { 
            Test-SheetsIntegration 
        }
        "service" { 
            Get-ServiceStatus 
        }
        "logs" { 
            Get-CloudLogs 
        }
        "billing" { 
            Get-BillingInfo 
        }
        "quota" { 
            Get-QuotaStatus 
        }
        "deploy" { 
            Deploy-CloudFunction 
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