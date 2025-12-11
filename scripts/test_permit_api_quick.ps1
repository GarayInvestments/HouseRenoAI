# Simplified Permit API Test - Phase B.1
# Tests only the new permit endpoints

Write-Host "`n=== PHASE B.1 PERMIT API TEST ===" -ForegroundColor Cyan
Write-Host "Testing PostgreSQL-backed permit endpoints`n" -ForegroundColor Gray

$API_BASE = "http://localhost:8000"

# Login
Write-Host "Login..." -ForegroundColor Yellow
$r = Invoke-RestMethod -Uri "$API_BASE/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"steve@garayinvestments.com","password":"Stv060485!"}'
$headers = @{"Authorization"="Bearer $($r.access_token)"}
Write-Host "✅ Logged in`n" -ForegroundColor Green

# Get a project ID from Google Sheets (read-only)
Write-Host "Getting project from Google Sheets..." -ForegroundColor Yellow
$projects = Invoke-RestMethod -Uri "$API_BASE/v1/projects" -Headers $headers

if ($projects.Count -gt 0 -and $projects[0].id) {
    $projectId = $projects[0].id
    Write-Host "✅ Using project: $projectId`n" -ForegroundColor Green
} else {
    Write-Host "⚠️  No projects in Google Sheets - using test UUID" -ForegroundColor Yellow
    $projectId = "123e4567-e89b-12d3-a456-426614174001"
    Write-Host "   (Using test project PRJ-00013)`n" -ForegroundColor Gray
}

# TEST 1: Create Permit
Write-Host "TEST 1: Create Permit (POST /v1/permits)" -ForegroundColor Cyan
try {
    $permitData = @{
        project_id = $projectId
        permit_type = "Building"
        jurisdiction = "City of Burnsville"
        notes = "Phase B.1 test permit - PostgreSQL"
    } | ConvertTo-Json
    
    $permit = Invoke-RestMethod -Uri "$API_BASE/v1/permits" -Method Post -Headers $headers -ContentType "application/json" -Body $permitData
    Write-Host "✅ Created permit: $($permit.business_id)" -ForegroundColor Green
    Write-Host "   Status: $($permit.status), Type: $($permit.permit_type)`n" -ForegroundColor Gray
    $permitId = $permit.id
} catch {
    Write-Host "❌ Failed: $_`n" -ForegroundColor Red
    exit 1
}

# TEST 2: List Permits
Write-Host "TEST 2: List Permits (GET /v1/permits)" -ForegroundColor Cyan
try {
    $allPermits = Invoke-RestMethod -Uri "$API_BASE/v1/permits" -Headers $headers
    Write-Host "✅ Retrieved $($allPermits.Count) permit(s)`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_`n" -ForegroundColor Red
}

# TEST 3: Get by Business ID
Write-Host "TEST 3: Get by Business ID (GET /v1/permits/by-business-id/$($permit.business_id))" -ForegroundColor Cyan
try {
    $permitByBizId = Invoke-RestMethod -Uri "$API_BASE/v1/permits/by-business-id/$($permit.business_id)" -Headers $headers
    Write-Host "✅ Retrieved permit: $($permitByBizId.business_id)`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_`n" -ForegroundColor Red
}

# TEST 4: Get by UUID
Write-Host "TEST 4: Get by UUID (GET /v1/permits/$permitId)" -ForegroundColor Cyan
try {
    $permitByUUID = Invoke-RestMethod -Uri "$API_BASE/v1/permits/$permitId" -Headers $headers
    Write-Host "✅ Retrieved permit: $($permitByUUID.business_id)`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_`n" -ForegroundColor Red
}

# TEST 5: Update Permit Details
Write-Host "TEST 5: Update Details (PUT /v1/permits/$permitId)" -ForegroundColor Cyan
try {
    $updateData = @{
        permit_number = "2025-TEST-001"
        authority = "City of Burnsville Building Dept"
        inspector = "John Smith"
    } | ConvertTo-Json
    
    $updated = Invoke-RestMethod -Uri "$API_BASE/v1/permits/$permitId" -Method Put -Headers $headers -ContentType "application/json" -Body $updateData
    Write-Host "✅ Updated - Permit #$($updated.permit_number)`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_`n" -ForegroundColor Red
}

# TEST 6: Submit Permit
Write-Host "TEST 6: Submit Permit (POST /v1/permits/$permitId/submit)" -ForegroundColor Cyan
try {
    $submitData = @{notes = "Submitting for city review"} | ConvertTo-Json
    $submitted = Invoke-RestMethod -Uri "$API_BASE/v1/permits/$permitId/submit" -Method Post -Headers $headers -ContentType "application/json" -Body $submitData
    Write-Host "✅ Submitted - Status: $($submitted.status)`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_`n" -ForegroundColor Red
}

# TEST 7: Update Status
Write-Host "TEST 7: Update Status (PUT /v1/permits/$permitId/status)" -ForegroundColor Cyan
try {
    $statusData = @{
        status = "Approved"
        notes = "All requirements met"
    } | ConvertTo-Json
    
    $approved = Invoke-RestMethod -Uri "$API_BASE/v1/permits/$permitId/status" -Method Put -Headers $headers -ContentType "application/json" -Body $statusData
    Write-Host "✅ Status updated to: $($approved.status)`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_`n" -ForegroundColor Red
}

# TEST 8: Precheck
Write-Host "TEST 8: Precheck (GET /v1/permits/$permitId/precheck)" -ForegroundColor Cyan
try {
    $precheck = Invoke-RestMethod -Uri "$API_BASE/v1/permits/$permitId/precheck?inspection_type=Foundation" -Headers $headers
    Write-Host "✅ Precheck result:" -ForegroundColor Green
    Write-Host "   Can schedule: $($precheck.can_schedule)" -ForegroundColor Gray
    Write-Host "   AI confidence: $($precheck.ai_confidence)`n" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $_`n" -ForegroundColor Red
}

# TEST 9: List with Filters
Write-Host "TEST 9: List with Filters (GET /v1/permits?status=Approved)" -ForegroundColor Cyan
try {
    $filtered = Invoke-RestMethod -Uri "$API_BASE/v1/permits?status=Approved" -Headers $headers
    Write-Host "✅ Found $($filtered.Count) approved permit(s)`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_`n" -ForegroundColor Red
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ PHASE B.1 TESTING COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Test Permit: $($permit.business_id)" -ForegroundColor Yellow
Write-Host "Permit ID: $permitId`n" -ForegroundColor Yellow
