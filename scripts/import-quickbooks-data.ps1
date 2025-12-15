#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Import invoices and payments from QuickBooks to local database cache.

.DESCRIPTION
    Performs a full sync of QuickBooks data in the correct order:
    1. Customers (GC Compliance only)
    2. Invoices (linked to GC Compliance customers)
    3. Payments (linked to GC Compliance invoices)

.PARAMETER ApiUrl
    Base API URL (default: production Fly.io)

.PARAMETER Token
    Supabase auth token (will prompt if not provided)

.PARAMETER StepByStep
    If set, waits for confirmation between each sync step

.EXAMPLE
    .\scripts\import-quickbooks-data.ps1
    # Prompts for token, syncs all entities

.EXAMPLE
    .\scripts\import-quickbooks-data.ps1 -StepByStep
    # Prompts between each entity type

.EXAMPLE
    $env:SUPABASE_TOKEN = "your_token_here"
    .\scripts\import-quickbooks-data.ps1
    # Uses token from environment variable
#>

param(
    [string]$ApiUrl = "https://houserenovators-api.fly.dev",
    [string]$Token = $env:SUPABASE_TOKEN,
    [switch]$StepByStep
)

# Color output helpers
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

function Invoke-SyncEndpoint {
    param(
        [string]$EntityType,
        [string]$Token,
        [string]$BaseUrl
    )

    $url = "$BaseUrl/v1/quickbooks/sync/$EntityType`?force_full=true"
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Content-Type" = "application/json"
    }

    try {
        Write-Info "Syncing $EntityType from QuickBooks..."
        $startTime = Get-Date
        
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -TimeoutSec 300
        
        $duration = ((Get-Date) - $startTime).TotalSeconds
        
        if ($response.success) {
            Write-Success "$EntityType sync completed in $([math]::Round($duration, 2))s"
            Write-Host "  Created: $($response.created)" -ForegroundColor Gray
            Write-Host "  Updated: $($response.updated)" -ForegroundColor Gray
            Write-Host "  Skipped: $($response.skipped)" -ForegroundColor Gray
            return $response
        } else {
            Write-Error "$EntityType sync failed"
            return $null
        }
        
    } catch {
        Write-Error "$EntityType sync failed: $($_.Exception.Message)"
        if ($_.ErrorDetails) {
            Write-Host "  Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }
        return $null
    }
}

# Main script
Write-Host "`n🔄 QuickBooks Data Import Script" -ForegroundColor Blue
Write-Host "================================`n" -ForegroundColor Blue

# Check for auth token
if (-not $Token) {
    Write-Warning "No auth token found in environment variable SUPABASE_TOKEN"
    $Token = Read-Host "Enter your Supabase auth token"
    if (-not $Token) {
        Write-Error "Auth token is required. Exiting."
        exit 1
    }
}

Write-Info "Target API: $ApiUrl"
Write-Info "Sync mode: Full sync (force_full=true)"
Write-Host ""

# Confirm before proceeding
$confirm = Read-Host "Start QuickBooks import? (y/n)"
if ($confirm -ne 'y') {
    Write-Warning "Import cancelled by user"
    exit 0
}

Write-Host ""

# Track overall results
$results = @{
    customers = $null
    invoices = $null
    payments = $null
}

# Step 1: Customers
Write-Info "Step 1/3: Importing customers (GC Compliance only)..."
$results.customers = Invoke-SyncEndpoint -EntityType "customers" -Token $Token -BaseUrl $ApiUrl
Write-Host ""

if ($null -eq $results.customers) {
    Write-Error "Customer sync failed. Cannot proceed with invoices/payments."
    exit 1
}

if ($StepByStep) {
    Read-Host "Press Enter to continue with invoices..."
    Write-Host ""
}

# Step 2: Invoices
Write-Info "Step 2/3: Importing invoices (linked to GC Compliance customers)..."
$results.invoices = Invoke-SyncEndpoint -EntityType "invoices" -Token $Token -BaseUrl $ApiUrl
Write-Host ""

if ($null -eq $results.invoices) {
    Write-Warning "Invoice sync failed. You can retry manually or continue to payments."
    if ($StepByStep) {
        $continue = Read-Host "Continue to payments? (y/n)"
        if ($continue -ne 'y') {
            exit 1
        }
    }
}

if ($StepByStep) {
    Read-Host "Press Enter to continue with payments..."
    Write-Host ""
}

# Step 3: Payments
Write-Info "Step 3/3: Importing payments (linked to GC Compliance invoices)..."
$results.payments = Invoke-SyncEndpoint -EntityType "payments" -Token $Token -BaseUrl $ApiUrl
Write-Host ""

# Summary
Write-Host "`n📊 Import Summary" -ForegroundColor Blue
Write-Host "================`n" -ForegroundColor Blue

$totalCreated = 0
$totalUpdated = 0
$totalSkipped = 0

foreach ($entity in @("customers", "invoices", "payments")) {
    $result = $results[$entity]
    if ($result) {
        Write-Success "$entity imported"
        $totalCreated += $result.created
        $totalUpdated += $result.updated
        $totalSkipped += $result.skipped
    } else {
        Write-Error "$entity failed"
    }
}

Write-Host ""
Write-Host "Total created: $totalCreated" -ForegroundColor Green
Write-Host "Total updated: $totalUpdated" -ForegroundColor Yellow
Write-Host "Total skipped: $totalSkipped" -ForegroundColor Gray
Write-Host ""

Write-Success "QuickBooks import complete!"
Write-Info "Data is now cached locally. Future syncs will be incremental (delta-only)."
Write-Host ""
