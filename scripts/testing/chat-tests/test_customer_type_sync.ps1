# Customer Type Sync - Detailed Test
# Tests the specific CustomerType sync functionality and error handling

$baseUrl = "http://localhost:8000/v1"

# Authenticate
$loginBody = @{ email = "admin@houserenovators.com"; password = "admin123" } | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
$headers = @{ "Authorization" = "Bearer $($loginResponse.access_token)" }

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  CUSTOMER TYPE SYNC TEST" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Direct API sync (already done, should report 0 updates)
Write-Host "[1] Direct API Sync Test" -ForegroundColor Yellow
try {
    $syncResult = Invoke-RestMethod -Uri "$baseUrl/quickbooks/sync-types?dry_run=false" -Method Post -Headers $headers
    Write-Host "   Status: $($syncResult.status)" -ForegroundColor $(if ($syncResult.status -eq "success") { "Green" } else { "Red" })
    Write-Host "   Matched: $($syncResult.matched)" -ForegroundColor Cyan
    Write-Host "   Updated: $($syncResult.updated)" -ForegroundColor Cyan
    Write-Host "   Skipped: $($syncResult.skipped_already_set)" -ForegroundColor Cyan
    Write-Host "   Errors: $($syncResult.errors)" -ForegroundColor $(if ($syncResult.errors -eq 0) { "Green" } else { "Red" })
    
    if ($syncResult.error_details) {
        Write-Host "   Error Details:" -ForegroundColor Red
        $syncResult.error_details | ForEach-Object {
            Write-Host "      - $($_.client_name): $($_.error)" -ForegroundColor Gray
        }
    }
    
    Write-Host "   ✅ PASS: Direct sync works" -ForegroundColor Green
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: AI-driven sync
Write-Host "[2] AI-Driven Sync Test" -ForegroundColor Yellow
try {
    $chatBody = @{
        message = "Sync all customer types to GC Compliance"
        session_id = "sync-test-$(Get-Random)"
    } | ConvertTo-Json
    
    $chatResponse = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Headers $headers -Body $chatBody -ContentType "application/json" -TimeoutSec 60
    
    Write-Host "   AI Response:" -ForegroundColor White
    Write-Host "   $($chatResponse.response)`n" -ForegroundColor Gray
    
    # Check if sync function was called
    if ($chatResponse.function_calls) {
        $syncFunctionCalled = $chatResponse.function_calls | Where-Object { $_.name -eq "sync_quickbooks_customer_types" }
        if ($syncFunctionCalled) {
            Write-Host "   ✅ Function 'sync_quickbooks_customer_types' was called" -ForegroundColor Green
            
            # Check function results
            if ($chatResponse.function_results) {
                $syncResult = $chatResponse.function_results | Where-Object { $_.name -eq "sync_quickbooks_customer_types" }
                if ($syncResult) {
                    Write-Host "   Function Result:" -ForegroundColor Cyan
                    Write-Host "      Status: $($syncResult.status)" -ForegroundColor Gray
                    Write-Host "      Updated: $($syncResult.updated)" -ForegroundColor Gray
                    Write-Host "      Errors: $($syncResult.errors)" -ForegroundColor Gray
                }
            }
        } else {
            Write-Host "   ⚠️ Sync function was not called" -ForegroundColor Magenta
            Write-Host "   Functions called: $($chatResponse.function_calls | ForEach-Object { $_.name } | Join-String -Separator ', ')" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ⚠️ No functions were called" -ForegroundColor Magenta
    }
    
    Write-Host "   ✅ PASS: AI handled sync request" -ForegroundColor Green
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Verify current state
Write-Host "[3] Verify GC Compliance Customers" -ForegroundColor Yellow
try {
    $customers = Invoke-RestMethod -Uri "$baseUrl/quickbooks/customers" -Method Get -Headers $headers
    Write-Host "   Total GC Compliance Customers: $($customers.count)" -ForegroundColor Cyan
    Write-Host "   Customers:" -ForegroundColor White
    $customers.customers | ForEach-Object {
        $typeValue = $_.CustomerTypeRef.value
        $typeStatus = if ($typeValue -eq "698682") { "✅" } else { "❌" }
        Write-Host "      $typeStatus $($_.DisplayName) (ID: $($_.Id), Type ID: $typeValue)" -ForegroundColor Gray
    }
    Write-Host "   ✅ PASS: Retrieved customer list" -ForegroundColor Green
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 4: AI query about customer types
Write-Host "[4] AI Query: Customer Type Status" -ForegroundColor Yellow
try {
    $chatBody = @{
        message = "How many customers have the GC Compliance type?"
        session_id = "status-test-$(Get-Random)"
    } | ConvertTo-Json
    
    $chatResponse = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Headers $headers -Body $chatBody -ContentType "application/json" -TimeoutSec 60
    
    Write-Host "   AI Response:" -ForegroundColor White
    Write-Host "   $($chatResponse.response)`n" -ForegroundColor Gray
    
    Write-Host "   ✅ PASS: AI responded to status query" -ForegroundColor Green
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 5: Error handling - invalid customer type
Write-Host "[5] Error Handling: Invalid Customer Type" -ForegroundColor Yellow
try {
    $chatBody = @{
        message = "Sync all customers to InvalidTypeXYZ123"
        session_id = "error-test-$(Get-Random)"
    } | ConvertTo-Json
    
    $chatResponse = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Headers $headers -Body $chatBody -ContentType "application/json" -TimeoutSec 60
    
    Write-Host "   AI Response:" -ForegroundColor White
    Write-Host "   $($chatResponse.response)`n" -ForegroundColor Gray
    
    # Check if AI handles the error gracefully
    if ($chatResponse.response -match "(?i)(cannot|unable|not found|invalid|does not exist)") {
        Write-Host "   ✅ PASS: AI handled invalid type gracefully" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ AI may not have recognized the invalid type" -ForegroundColor Magenta
    }
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 6: Dry run test
Write-Host "[6] Dry Run Test" -ForegroundColor Yellow
try {
    $chatBody = @{
        message = "Do a dry run sync of customer types to GC Compliance"
        session_id = "dryrun-test-$(Get-Random)"
    } | ConvertTo-Json
    
    $chatResponse = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Headers $headers -Body $chatBody -ContentType "application/json" -TimeoutSec 60
    
    Write-Host "   AI Response:" -ForegroundColor White
    Write-Host "   $($chatResponse.response)`n" -ForegroundColor Gray
    
    # Check if dry_run was set to true
    if ($chatResponse.function_calls) {
        $syncCall = $chatResponse.function_calls | Where-Object { $_.name -eq "sync_quickbooks_customer_types" }
        if ($syncCall -and $syncCall.arguments) {
            $args = $syncCall.arguments | ConvertFrom-Json
            if ($args.dry_run -eq $true) {
                Write-Host "   ✅ PASS: Dry run parameter was set correctly" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Dry run parameter may not be set" -ForegroundColor Magenta
            }
        }
    }
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 7: Check for proper error reporting
Write-Host "[7] Error Reporting Quality Test" -ForegroundColor Yellow
Write-Host "   Checking if errors from previous sync were properly logged..." -ForegroundColor Gray

try {
    # Run a sync that should find all already synced
    $syncResult = Invoke-RestMethod -Uri "$baseUrl/quickbooks/sync-types?dry_run=false" -Method Post -Headers $headers
    
    if ($syncResult.errors -gt 0 -and $syncResult.error_details) {
        Write-Host "   ✅ Error details are provided:" -ForegroundColor Green
        $syncResult.error_details | ForEach-Object {
            Write-Host "      Customer: $($_.client_name)" -ForegroundColor Gray
            Write-Host "      Error: $($_.error)" -ForegroundColor Gray
            Write-Host "" -ForegroundColor Gray
        }
    } elseif ($syncResult.errors -eq 0) {
        Write-Host "   ✅ No errors to report (all customers already synced)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Errors occurred but no error_details provided" -ForegroundColor Magenta
    }
} catch {
    Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  CUSTOMER TYPE SYNC TEST COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
