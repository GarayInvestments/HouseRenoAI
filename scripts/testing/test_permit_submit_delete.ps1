# Test Submit and Delete endpoints with fresh permits
Write-Host "`n=== TESTING SUBMIT & DELETE ENDPOINTS ===" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"
$testProjectId = "123e4567-e89b-12d3-a456-426614174001"

# Login
$loginResponse = Invoke-RestMethod -Uri "$baseUrl/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"steve@garayinvestments.com","password":"Stv060485!"}'
$token = $loginResponse.access_token
$headers = @{ "Authorization" = "Bearer $token" }
Write-Host "✅ Logged in`n" -ForegroundColor Green

# Test 1: Submit Permit
Write-Host "[1/2] Testing Submit Permit..." -ForegroundColor Yellow
try {
    # Create a fresh permit
    $permitData = @{
        project_id = $testProjectId
        permit_type = "Electrical"
        status = "Draft"
        extra = @{ jurisdiction = "City of Test"; notes = "For submit test" }
    } | ConvertTo-Json
    
    $permit = Invoke-RestMethod -Uri "$baseUrl/v1/permits" -Method Post -Headers $headers -ContentType "application/json" -Body $permitData
    Write-Host "   Created permit: $($permit.business_id)" -ForegroundColor Gray
    
    # Submit it
    $submitData = @{ notes = "Submitted for approval" } | ConvertTo-Json
    $submitted = Invoke-RestMethod -Uri "$baseUrl/v1/permits/$($permit.permit_id)/submit" -Method Post -Headers $headers -ContentType "application/json" -Body $submitData
    
    Write-Host "✅ Submit successful" -ForegroundColor Green
    Write-Host "   Status after submit: $($submitted.status)" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Submit failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# Test 2: Delete Permit
Write-Host "`n[2/2] Testing Delete Permit..." -ForegroundColor Yellow
try {
    # Create a fresh permit
    $permitData = @{
        project_id = $testProjectId
        permit_type = "Plumbing"
        status = "Draft"
        extra = @{ jurisdiction = "City of Test"; notes = "For delete test" }
    } | ConvertTo-Json
    
    $permit = Invoke-RestMethod -Uri "$baseUrl/v1/permits" -Method Post -Headers $headers -ContentType "application/json" -Body $permitData
    Write-Host "   Created permit: $($permit.business_id)" -ForegroundColor Gray
    
    # Delete it
    Invoke-RestMethod -Uri "$baseUrl/v1/permits/$($permit.permit_id)" -Method Delete -Headers $headers
    
    Write-Host "✅ Delete successful" -ForegroundColor Green
    
    # Verify it's gone
    try {
        Invoke-RestMethod -Uri "$baseUrl/v1/permits/$($permit.permit_id)" -Method Get -Headers $headers
        Write-Host "   ⚠️  Warning: Permit still exists after delete" -ForegroundColor Yellow
    } catch {
        if ($_.Exception.Response.StatusCode.value__ -eq 404) {
            Write-Host "   ✓ Verified: Permit no longer exists" -ForegroundColor Gray
        }
    }
    
} catch {
    Write-Host "❌ Delete failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Cyan
