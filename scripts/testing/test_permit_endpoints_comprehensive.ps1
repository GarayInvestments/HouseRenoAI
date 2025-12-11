# Comprehensive Permit API Endpoint Tests
# Tests all 9 Phase B.1 endpoints after response model fix

Write-Host "`n=== PERMIT API COMPREHENSIVE TEST SUITE ===" -ForegroundColor Cyan
Write-Host "Testing all 9 Phase B.1 endpoints`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"
$testProjectId = "123e4567-e89b-12d3-a456-426614174001"  # PRJ-00013

# 1. Login
Write-Host "[1/9] Testing Authentication..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/v1/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body '{"email":"steve@garayinvestments.com","password":"Stv060485!"}'
    
    $token = $loginResponse.access_token
    $headers = @{ "Authorization" = "Bearer $token" }
    Write-Host "✅ Login successful" -ForegroundColor Green
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Create Permit (POST /v1/permits)
Write-Host "`n[2/9] Testing Create Permit (POST /v1/permits)..." -ForegroundColor Yellow
try {
    $permitData = @{
        project_id = $testProjectId
        permit_type = "Building"
        status = "Draft"
        extra = @{
            jurisdiction = "City of Burnsville"
            notes = "Comprehensive test permit"
        }
    } | ConvertTo-Json
    
    $newPermit = Invoke-RestMethod -Uri "$baseUrl/v1/permits" `
        -Method Post `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $permitData
    
    $testPermitId = $newPermit.permit_id
    $testBusinessId = $newPermit.business_id
    Write-Host "✅ Created permit $testBusinessId (ID: $testPermitId)" -ForegroundColor Green
} catch {
    Write-Host "❌ Create permit failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    exit 1
}

# 3. List Permits (GET /v1/permits)
Write-Host "`n[3/9] Testing List Permits (GET /v1/permits)..." -ForegroundColor Yellow
try {
    $permits = Invoke-RestMethod -Uri "$baseUrl/v1/permits" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✅ Retrieved $($permits.total) permits" -ForegroundColor Green
    if ($permits.total -gt 0) {
        Write-Host "   First permit: $($permits.items[0].business_id)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ List permits failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Get Permit by Business ID (GET /v1/permits/by-business-id/{business_id})
Write-Host "`n[4/9] Testing Get Permit by Business ID..." -ForegroundColor Yellow
try {
    $permit = Invoke-RestMethod -Uri "$baseUrl/v1/permits/by-business-id/$testBusinessId" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✅ Retrieved permit $testBusinessId" -ForegroundColor Green
    Write-Host "   Type: $($permit.permit_type), Status: $($permit.status)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Get by business ID failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Get Permit by UUID (GET /v1/permits/{permit_id})
Write-Host "`n[5/9] Testing Get Permit by UUID..." -ForegroundColor Yellow
try {
    $permit = Invoke-RestMethod -Uri "$baseUrl/v1/permits/$testPermitId" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✅ Retrieved permit by UUID" -ForegroundColor Green
    Write-Host "   Business ID: $($permit.business_id)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Get by UUID failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Update Permit Status (PUT /v1/permits/{permit_id}/status)
Write-Host "`n[6/9] Testing Update Permit Status..." -ForegroundColor Yellow
try {
    $statusUpdate = @{
        status = "Pending Review"
        notes = "Status updated via comprehensive test"
    } | ConvertTo-Json
    
    $updated = Invoke-RestMethod -Uri "$baseUrl/v1/permits/$testPermitId/status" `
        -Method Put `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $statusUpdate
    
    Write-Host "✅ Updated status to: $($updated.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Update status failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# 7. Update Permit (PUT /v1/permits/{permit_id})
Write-Host "`n[7/9] Testing Update Permit (Full)..." -ForegroundColor Yellow
try {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $updateData = @{
        permit_number = "TEST-$timestamp"
        status = "Under Review"
        notes = "Updated via comprehensive test"
    } | ConvertTo-Json
    
    $updated = Invoke-RestMethod -Uri "$baseUrl/v1/permits/$testPermitId" `
        -Method Put `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $updateData
    
    Write-Host "✅ Updated permit successfully" -ForegroundColor Green
    Write-Host "   Permit Number: $($updated.permit_number)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Update permit failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# 8. Submit Permit (POST /v1/permits/{permit_id}/submit)
Write-Host "`n[8/9] Testing Submit Permit..." -ForegroundColor Yellow
try {
    $submitData = @{
        notes = "Submitted via comprehensive test"
    } | ConvertTo-Json
    
    $submitted = Invoke-RestMethod -Uri "$baseUrl/v1/permits/$testPermitId/submit" `
        -Method Post `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $submitData
    
    Write-Host "✅ Submitted permit successfully" -ForegroundColor Green
    Write-Host "   Status: $($submitted.status)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Submit permit failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# 9. Delete Permit (DELETE /v1/permits/{permit_id})
Write-Host "`n[9/9] Testing Delete Permit..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$baseUrl/v1/permits/$testPermitId" `
        -Method Delete `
        -Headers $headers
    
    Write-Host "✅ Deleted permit successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Delete permit failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n=== TEST SUITE COMPLETE ===" -ForegroundColor Cyan
Write-Host "Review results above. All endpoints have been tested." -ForegroundColor Cyan
Write-Host "Note: Some failures expected if endpoints still need PermitService fixes.`n" -ForegroundColor Yellow
