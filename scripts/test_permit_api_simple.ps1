# Simple PowerShell test for Permit API endpoints
# Phase B.1 validation

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*79) -ForegroundColor Cyan
Write-Host "PERMIT API TESTS - PHASE B.1 (PowerShell)" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("="*79) -ForegroundColor Cyan
Write-Host ""

$API_BASE = "http://localhost:8000"

# Test 1: Login
Write-Host "TEST 1: Login" -ForegroundColor Cyan
Write-Host "-"*80

try {
    $loginResponse = Invoke-RestMethod -Uri "$API_BASE/v1/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body '{"email":"steve@garayinvestments.com","password":"Stv060485!"}' `
        -ErrorAction Stop
    
    $token = $loginResponse.access_token
    Write-Host "✅ Logged in successfully" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Login failed: $_" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
}

# Test 2: Get or create project
Write-Host "TEST 2: Get Projects" -ForegroundColor Cyan
Write-Host "-"*80

try {
    $projects = Invoke-RestMethod -Uri "$API_BASE/v1/projects" `
        -Headers $headers `
        -ErrorAction Stop
    
    if ($projects.Count -eq 0 -or $null -eq $projects[0].id) {
        Write-Host "No valid projects found - creating test project..." -ForegroundColor Yellow
        
        # Get or create client first
        $clients = Invoke-RestMethod -Uri "$API_BASE/v1/clients" -Headers $headers
        if ($clients.Count -eq 0) {
            $clientData = @{
                name = "Test Client"
                email = "test@example.com"
                phone = "555-0100"
            } | ConvertTo-Json
            $client = Invoke-RestMethod -Uri "$API_BASE/v1/clients" -Method Post -Headers $headers -ContentType "application/json" -Body $clientData
            Write-Host "Created test client: $($client.business_id)" -ForegroundColor Gray
        } else {
            $client = $clients[0]
        }
        
        # Create project
        $projectData = @{
            client_id = $client.id
            name = "Phase B.1 Test Project"
            address = "123 Test Street"
            city = "Burnsville"
            state = "MN"
            zip = "55337"
            status = "Active"
        } | ConvertTo-Json
        
        $project = Invoke-RestMethod -Uri "$API_BASE/v1/projects" -Method Post -Headers $headers -ContentType "application/json" -Body $projectData
        Write-Host "✅ Created project: $($project.business_id) - $($project.name)" -ForegroundColor Green
    } else {
        $project = $projects[0]
        Write-Host "✅ Found project: $($project.business_id) - $($project.name)" -ForegroundColor Green
    }
    
    $projectId = $project.id
    Write-Host ""
} catch {
    Write-Host "❌ Failed to get/create projects: $_" -ForegroundColor Red
    exit 1
}

# Test 3: Create Permit
Write-Host "TEST 3: Create Permit (POST /v1/permits)" -ForegroundColor Cyan
Write-Host "-"*80

$permitData = @{
    project_id = $projectId
    permit_type = "Building"
    jurisdiction = "City of Burnsville"
    notes = "PowerShell test permit - Phase B.1"
} | ConvertTo-Json

try {
    $permit = Invoke-RestMethod -Uri "$API_BASE/v1/permits" `
        -Method Post `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $permitData `
        -ErrorAction Stop
    
    $permitId = $permit.id
    $businessId = $permit.business_id
    
    Write-Host "✅ Created permit: $businessId" -ForegroundColor Green
    Write-Host "   - ID: $permitId"
    Write-Host "   - Type: $($permit.permit_type)"
    Write-Host "   - Status: $($permit.status)"
    Write-Host "   - Jurisdiction: $($permit.jurisdiction)"
    Write-Host ""
} catch {
    Write-Host "❌ Failed to create permit: $_" -ForegroundColor Red
    Write-Host "Response: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    exit 1
}

# Test 4: List Permits
Write-Host "TEST 4: List Permits (GET /v1/permits)" -ForegroundColor Cyan
Write-Host "-"*80

try {
    $permits = Invoke-RestMethod -Uri "$API_BASE/v1/permits" `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "✅ Retrieved $($permits.Count) permit(s)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Failed to list permits: $_" -ForegroundColor Red
    exit 1
}

# Test 5: Get Permit by Business ID
Write-Host "TEST 5: Get Permit by Business ID (GET /v1/permits/by-business-id/$businessId)" -ForegroundColor Cyan
Write-Host "-"*80

try {
    $permitByBizId = Invoke-RestMethod -Uri "$API_BASE/v1/permits/by-business-id/$businessId" `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "✅ Retrieved permit by business ID: $($permitByBizId.business_id)" -ForegroundColor Green
    Write-Host "   - Status: $($permitByBizId.status)"
    Write-Host ""
} catch {
    Write-Host "❌ Failed to get permit by business ID: $_" -ForegroundColor Red
    exit 1
}

# Test 6: Update Permit
Write-Host "TEST 6: Update Permit (PUT /v1/permits/$permitId)" -ForegroundColor Cyan
Write-Host "-"*80

$updateData = @{
    permit_number = "2025-BUILD-001"
    authority = "City of Burnsville Building Department"
    inspector = "John Smith"
} | ConvertTo-Json

try {
    $updatedPermit = Invoke-RestMethod -Uri "$API_BASE/v1/permits/$permitId" `
        -Method Put `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $updateData `
        -ErrorAction Stop
    
    Write-Host "✅ Updated permit details" -ForegroundColor Green
    Write-Host "   - Permit #: $($updatedPermit.permit_number)"
    Write-Host "   - Authority: $($updatedPermit.authority)"
    Write-Host "   - Inspector: $($updatedPermit.inspector)"
    Write-Host ""
} catch {
    Write-Host "❌ Failed to update permit: $_" -ForegroundColor Red
    exit 1
}

# Test 7: Submit Permit
Write-Host "TEST 7: Submit Permit (POST /v1/permits/$permitId/submit)" -ForegroundColor Cyan
Write-Host "-"*80

$submitData = @{
    notes = "Submitting for review via PowerShell test"
} | ConvertTo-Json

try {
    $submittedPermit = Invoke-RestMethod -Uri "$API_BASE/v1/permits/$permitId/submit" `
        -Method Post `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $submitData `
        -ErrorAction Stop
    
    Write-Host "✅ Submitted permit" -ForegroundColor Green
    Write-Host "   - Status: $($submittedPermit.status)"
    Write-Host "   - Application Date: $($submittedPermit.application_date)"
    Write-Host ""
} catch {
    Write-Host "❌ Failed to submit permit: $_" -ForegroundColor Red
    exit 1
}

# Test 8: Update Status to Approved
Write-Host "TEST 8: Update Status (PUT /v1/permits/$permitId/status)" -ForegroundColor Cyan
Write-Host "-"*80

$statusData = @{
    status = "Approved"
    notes = "All requirements met - approved via PowerShell test"
} | ConvertTo-Json

try {
    $approvedPermit = Invoke-RestMethod -Uri "$API_BASE/v1/permits/$permitId/status" `
        -Method Put `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $statusData `
        -ErrorAction Stop
    
    Write-Host "✅ Updated permit status" -ForegroundColor Green
    Write-Host "   - Status: $($approvedPermit.status)"
    Write-Host "   - Approved At: $($approvedPermit.approved_at)"
    Write-Host ""
} catch {
    Write-Host "❌ Failed to update status: $_" -ForegroundColor Red
    exit 1
}

# Test 9: Precheck
Write-Host "TEST 9: Precheck (GET /v1/permits/$permitId/precheck)" -ForegroundColor Cyan
Write-Host "-"*80

try {
    $precheck = Invoke-RestMethod -Uri "$API_BASE/v1/permits/$permitId/precheck?inspection_type=Foundation" `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "✅ Precheck result:" -ForegroundColor Green
    Write-Host "   - Can Schedule: $($precheck.can_schedule)"
    Write-Host "   - AI Confidence: $($precheck.ai_confidence)"
    if ($precheck.missing) {
        Write-Host "   - Missing Items: $($precheck.missing -join ', ')"
    }
    if ($precheck.warnings) {
        Write-Host "   - Warnings: $($precheck.warnings -join ', ')"
    }
    Write-Host ""
} catch {
    Write-Host "❌ Failed to run precheck: $_" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "="*80 -ForegroundColor Green
Write-Host "✅ ALL PERMIT API TESTS PASSED" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Green
Write-Host ""
Write-Host "Test Permit Created: $businessId" -ForegroundColor Yellow
Write-Host "Permit ID: $permitId" -ForegroundColor Yellow
Write-Host ""
