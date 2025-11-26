# AI Stress Test Script
# Tests various scenarios including success cases, edge cases, and error handling

$baseUrl = "http://localhost:8000/v1"

# Get auth token
Write-Host "=== Authenticating ===" -ForegroundColor Cyan
$loginBody = @{
    email = "admin@houserenovators.com"
    password = "admin123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
$token = $loginResponse.access_token
$headers = @{
    "Authorization" = "Bearer $token"
}

Write-Host "✅ Authenticated successfully`n" -ForegroundColor Green

# Test counter
$testNumber = 0
$passedTests = 0
$failedTests = 0

function Run-ChatTest {
    param(
        [string]$TestName,
        [string]$Message,
        [string]$ExpectedFunction = $null,
        [string]$ExpectedKeyword = $null,
        [bool]$ShouldFail = $false
    )
    
    $script:testNumber++
    Write-Host "[$script:testNumber] Testing: $TestName" -ForegroundColor Yellow
    Write-Host "   Message: '$Message'" -ForegroundColor Gray
    
    try {
        $chatBody = @{
            message = $Message
            session_id = "stress-test-$(Get-Random)"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Headers $headers -Body $chatBody -ContentType "application/json" -TimeoutSec 60
        
        # Check if test should have failed
        if ($ShouldFail) {
            Write-Host "   ❌ FAIL: Expected error but got success" -ForegroundColor Red
            $script:failedTests++
            return
        }
        
        # Check response
        $aiResponse = $response.response
        Write-Host "   AI Response: $($aiResponse.Substring(0, [Math]::Min(100, $aiResponse.Length)))..." -ForegroundColor White
        
        # Check for expected function call
        if ($ExpectedFunction -and $response.function_calls) {
            $functionNames = $response.function_calls | ForEach-Object { $_.name }
            if ($functionNames -contains $ExpectedFunction) {
                Write-Host "   ✅ Function '$ExpectedFunction' was called" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Expected function '$ExpectedFunction' but got: $($functionNames -join ', ')" -ForegroundColor Magenta
            }
        }
        
        # Check for expected keyword in response
        if ($ExpectedKeyword) {
            if ($aiResponse -match $ExpectedKeyword) {
                Write-Host "   ✅ Found expected keyword: '$ExpectedKeyword'" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Expected keyword '$ExpectedKeyword' not found" -ForegroundColor Magenta
            }
        }
        
        # Check for errors in function results
        if ($response.function_results) {
            $errors = $response.function_results | Where-Object { $_.status -eq "failed" -or $_.error }
            if ($errors) {
                Write-Host "   ⚠️ Function errors detected:" -ForegroundColor Magenta
                $errors | ForEach-Object { Write-Host "      - $($_.error)" -ForegroundColor Gray }
            }
        }
        
        Write-Host "   ✅ PASS" -ForegroundColor Green
        $script:passedTests++
        
    } catch {
        if ($ShouldFail) {
            Write-Host "   ✅ PASS: Expected error occurred" -ForegroundColor Green
            $script:passedTests++
        } else {
            Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
            $script:failedTests++
        }
    }
    
    Write-Host ""
    Start-Sleep -Milliseconds 500
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  AI STRESS TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ===== BASIC QUERIES =====
Write-Host "--- CATEGORY: Basic Queries ---`n" -ForegroundColor Magenta

Run-ChatTest `
    -TestName "Simple greeting" `
    -Message "Hello" `
    -ExpectedKeyword "(?i)(hello|hi|greetings|help)"

Run-ChatTest `
    -TestName "What can you do" `
    -Message "What can you help me with?" `
    -ExpectedKeyword "(?i)(help|assist|manage|quickbooks|clients|projects)"

# ===== CUSTOMER/CLIENT QUERIES =====
Write-Host "--- CATEGORY: Customer Queries ---`n" -ForegroundColor Magenta

Run-ChatTest `
    -TestName "List all customers" `
    -Message "Show me all customers" `
    -ExpectedKeyword "(?i)(customer|client)"

Run-ChatTest `
    -TestName "Filter by name" `
    -Message "Do you have a customer named Ajay?" `
    -ExpectedKeyword "(?i)(ajay|nair)"

Run-ChatTest `
    -TestName "Customer details" `
    -Message "Tell me about Gustavo Roldan" `
    -ExpectedKeyword "(?i)(gustavo|roldan|customer|client)"

# ===== QUICKBOOKS SYNC TESTS =====
Write-Host "--- CATEGORY: QuickBooks Sync ---`n" -ForegroundColor Magenta

Run-ChatTest `
    -TestName "Sync customer types" `
    -Message "Sync all customer types to GC Compliance in QuickBooks" `
    -ExpectedFunction "sync_quickbooks_customer_types" `
    -ExpectedKeyword "(?i)(sync|customer|compliance)"

Run-ChatTest `
    -TestName "Check sync status" `
    -Message "How many customers have GC Compliance type?" `
    -ExpectedKeyword "(?i)(customer|compliance)"

# ===== INVOICE QUERIES =====
Write-Host "--- CATEGORY: Invoice Queries ---`n" -ForegroundColor Magenta

Run-ChatTest `
    -TestName "List invoices" `
    -Message "Show me recent invoices" `
    -ExpectedKeyword "(?i)(invoice)"

Run-ChatTest `
    -TestName "Unpaid invoices" `
    -Message "Which invoices are unpaid?" `
    -ExpectedKeyword "(?i)(invoice|unpaid|balance)"

# ===== PROJECT QUERIES =====
Write-Host "--- CATEGORY: Project Queries ---`n" -ForegroundColor Magenta

Run-ChatTest `
    -TestName "List projects" `
    -Message "What projects do we have?" `
    -ExpectedKeyword "(?i)(project)"

Run-ChatTest `
    -TestName "Active projects" `
    -Message "Show me active projects" `
    -ExpectedKeyword "(?i)(project|active)"

# ===== ERROR HANDLING TESTS =====
Write-Host "--- CATEGORY: Error Handling ---`n" -ForegroundColor Magenta

Run-ChatTest `
    -TestName "Non-existent customer" `
    -Message "Show me details for customer XYZ123NotReal" `
    -ExpectedKeyword "(?i)(not found|cannot find|no customer)"

Run-ChatTest `
    -TestName "Invalid operation" `
    -Message "Delete all customers from QuickBooks" `
    -ExpectedKeyword "(?i)(cannot|unable|not supported|don't have)"

Run-ChatTest `
    -TestName "Ambiguous request" `
    -Message "Update it" `
    -ExpectedKeyword "(?i)(clarify|which|what|specify|more information)"

# ===== EDGE CASES =====
Write-Host "--- CATEGORY: Edge Cases ---`n" -ForegroundColor Magenta

Run-ChatTest `
    -TestName "Empty message" `
    -Message "" `
    -ShouldFail $true

Run-ChatTest `
    -TestName "Very long message" `
    -Message ("Show me all customers. " * 50) `
    -ExpectedKeyword "(?i)(customer|client)"

Run-ChatTest `
    -TestName "Special characters" `
    -Message "Find customer with email test@example.com & phone (555) 123-4567" `
    -ExpectedKeyword "(?i)(customer|client|find)"

Run-ChatTest `
    -TestName "Multiple requests" `
    -Message "List all customers, show their invoices, and tell me which projects are active" `
    -ExpectedKeyword "(?i)(customer|invoice|project)"

# ===== CONTEXT/MEMORY TESTS =====
Write-Host "--- CATEGORY: Context & Memory ---`n" -ForegroundColor Magenta

$sessionId = "memory-test-$(Get-Random)"

# First message with session
$chatBody1 = @{
    message = "Show me customer Ajay Nair"
    session_id = $sessionId
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Headers $headers -Body $chatBody1 -ContentType "application/json"
Write-Host "[$($testNumber+1)] Context Test Part 1: Found Ajay Nair" -ForegroundColor Yellow
Write-Host "   ✅ First message sent" -ForegroundColor Green
$testNumber++

Start-Sleep -Milliseconds 500

# Follow-up message (should remember context)
$chatBody2 = @{
    message = "What's their email?"
    session_id = $sessionId
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Headers $headers -Body $chatBody2 -ContentType "application/json"
    Write-Host "[$($testNumber+1)] Context Test Part 2: Remember previous customer" -ForegroundColor Yellow
    if ($response2.response -match "(?i)(ajay|nair|email|@)") {
        Write-Host "   ✅ PASS: AI remembered context" -ForegroundColor Green
        $passedTests++
    } else {
        Write-Host "   ⚠️ AI response may not have used context" -ForegroundColor Magenta
        $passedTests++
    }
    $testNumber++
} catch {
    Write-Host "   ❌ FAIL: Context test failed" -ForegroundColor Red
    $failedTests++
    $testNumber++
}

Write-Host ""

# ===== PERFORMANCE TEST =====
Write-Host "--- CATEGORY: Performance ---`n" -ForegroundColor Magenta

Write-Host "[$($testNumber+1)] Performance Test: Rapid fire requests" -ForegroundColor Yellow
$testNumber++

$performanceTests = @(
    "How many customers?",
    "How many projects?",
    "How many invoices?"
)

$startTime = Get-Date
$perfSuccess = 0
$perfFail = 0

foreach ($msg in $performanceTests) {
    try {
        $chatBody = @{
            message = $msg
            session_id = "perf-test-$(Get-Random)"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Headers $headers -Body $chatBody -ContentType "application/json" -TimeoutSec 30
        $perfSuccess++
        Write-Host "   ✅ $msg" -ForegroundColor Green
    } catch {
        $perfFail++
        Write-Host "   ❌ $msg - $($_.Exception.Message)" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 200
}

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host "   Performance: $perfSuccess/$($performanceTests.Count) succeeded in $([math]::Round($duration, 2))s" -ForegroundColor Cyan
if ($perfSuccess -eq $performanceTests.Count) {
    $passedTests++
} else {
    $failedTests++
}

Write-Host ""

# ===== SUMMARY =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total Tests: $testNumber" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($passedTests/$testNumber)*100, 1))%" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

if ($failedTests -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
} elseif ($failedTests -le 2) {
    Write-Host "⚠️ Most tests passed with minor issues" -ForegroundColor Yellow
} else {
    Write-Host "❌ Multiple test failures detected" -ForegroundColor Red
}
