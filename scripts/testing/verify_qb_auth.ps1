# QuickBooks Authentication Verification Script
# Run after OAuth flow completes

$baseUrl = "https://houserenovators-api.fly.dev"

Write-Host "=== QuickBooks Authentication Verification ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check authentication status
Write-Host "Test 1: Checking QuickBooks authentication status..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "$baseUrl/v1/quickbooks/status" -Method Get
    Write-Host "✓ Status retrieved successfully" -ForegroundColor Green
    Write-Host "  - Authenticated: $($status.authenticated)" -ForegroundColor $(if ($status.authenticated) { "Green" } else { "Red" })
    Write-Host "  - Realm ID: $($status.realm_id)"
    Write-Host "  - Environment: $($status.environment)"
    Write-Host ""
}
catch {
    Write-Host "✗ Failed to get status: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 2: Try fetching customers (if authenticated)
if ($status.authenticated) {
    Write-Host "Test 2: Fetching QuickBooks customers..." -ForegroundColor Yellow
    try {
        $customers = Invoke-RestMethod -Uri "$baseUrl/v1/quickbooks/customers" -Method Get
        Write-Host "✓ Retrieved $($customers.Count) customers" -ForegroundColor Green
        Write-Host ""
    }
    catch {
        Write-Host "✗ Failed to fetch customers: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
    }

    # Test 3: Check sync status
    Write-Host "Test 3: Checking sync status..." -ForegroundColor Yellow
    try {
        $syncStatus = Invoke-RestMethod -Uri "$baseUrl/v1/quickbooks/sync/status" -Method Get
        Write-Host "✓ Sync status retrieved" -ForegroundColor Green
        foreach ($entity in $syncStatus) {
            Write-Host "  - $($entity.entity_name): Last sync $(if ($entity.last_sync_at) { $entity.last_sync_at } else { 'Never' })"
        }
        Write-Host ""
    }
    catch {
        Write-Host "✗ Failed to get sync status: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
    }

    # Test 4: Check scheduler status
    Write-Host "Test 4: Checking scheduler status..." -ForegroundColor Yellow
    try {
        $scheduler = Invoke-RestMethod -Uri "$baseUrl/v1/quickbooks/sync/scheduler" -Method Get
        Write-Host "✓ Scheduler status retrieved" -ForegroundColor Green
        Write-Host "  - Running: $($scheduler.running)"
        Write-Host "  - Next run: $($scheduler.next_run_time)"
        Write-Host ""
    }
    catch {
        Write-Host "✗ Failed to get scheduler status: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
    }
}
else {
    Write-Host "⚠ QuickBooks not authenticated. Please visit:" -ForegroundColor Yellow
    Write-Host "  $baseUrl/v1/quickbooks/connect" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "=== Verification Complete ===" -ForegroundColor Cyan
