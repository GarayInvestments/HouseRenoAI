# Comprehensive Inspection API Endpoint Tests - Phase B.2
# Tests all inspection endpoints

Write-Host "`n=== INSPECTION API COMPREHENSIVE TEST SUITE ===" -ForegroundColor Cyan
Write-Host "Testing all Phase B.2 endpoints`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"
$testProjectId = "123e4567-e89b-12d3-a456-426614174001"  # PRJ-00013

# 1. Login
Write-Host "[1/10] Testing Authentication..." -ForegroundColor Yellow
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

# Get a permit to use for inspections
Write-Host "`n[Setup] Getting a permit for inspection tests..." -ForegroundColor Yellow
try {
    $permits = Invoke-RestMethod -Uri "$baseUrl/v1/permits" -Method Get -Headers $headers
    if ($permits.total -eq 0) {
        # Create a permit first
        $permitData = @{
            project_id = $testProjectId
            permit_type = "Building"
            status = "Draft"
            extra = @{ jurisdiction = "Test City" }
        } | ConvertTo-Json
        
        $permit = Invoke-RestMethod -Uri "$baseUrl/v1/permits" -Method Post -Headers $headers -ContentType "application/json" -Body $permitData
        $testPermitId = $permit.permit_id
        Write-Host "   Created test permit: $($permit.business_id)" -ForegroundColor Gray
    } else {
        $testPermitId = $permits.items[0].permit_id
        Write-Host "   Using existing permit: $($permits.items[0].business_id)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Failed to get/create permit: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Create Inspection (POST /v1/inspections)
Write-Host "`n[2/10] Testing Create Inspection (POST /v1/inspections)..." -ForegroundColor Yellow
try {
    $inspectionData = @{
        permit_id = $testPermitId
        project_id = $testProjectId
        inspection_type = "Framing"
        status = "Scheduled"
        scheduled_date = (Get-Date).AddDays(7).ToString("yyyy-MM-ddTHH:mm:ss")
        inspector = "John Smith"
        notes = "Phase B.2 test inspection"
        extra = @{ test = "true" }
    } | ConvertTo-Json
    
    $newInspection = Invoke-RestMethod -Uri "$baseUrl/v1/inspections" `
        -Method Post `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $inspectionData
    
    $testInspectionId = $newInspection.inspection_id
    $testBusinessId = $newInspection.business_id
    Write-Host "✅ Created inspection $testBusinessId (ID: $testInspectionId)" -ForegroundColor Green
} catch {
    Write-Host "❌ Create inspection failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    exit 1
}

# 3. List Inspections (GET /v1/inspections)
Write-Host "`n[3/10] Testing List Inspections (GET /v1/inspections)..." -ForegroundColor Yellow
try {
    $inspections = Invoke-RestMethod -Uri "$baseUrl/v1/inspections" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✅ Retrieved $($inspections.total) inspections" -ForegroundColor Green
    if ($inspections.total -gt 0) {
        Write-Host "   First inspection: $($inspections.items[0].business_id)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ List inspections failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Get Inspection by Business ID (GET /v1/inspections/by-business-id/{business_id})
Write-Host "`n[4/10] Testing Get Inspection by Business ID..." -ForegroundColor Yellow
try {
    $inspection = Invoke-RestMethod -Uri "$baseUrl/v1/inspections/by-business-id/$testBusinessId" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✅ Retrieved inspection $testBusinessId" -ForegroundColor Green
    Write-Host "   Type: $($inspection.inspection_type), Status: $($inspection.status)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Get by business ID failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Get Inspection by UUID (GET /v1/inspections/{inspection_id})
Write-Host "`n[5/10] Testing Get Inspection by UUID..." -ForegroundColor Yellow
try {
    $inspection = Invoke-RestMethod -Uri "$baseUrl/v1/inspections/$testInspectionId" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✅ Retrieved inspection by UUID" -ForegroundColor Green
    Write-Host "   Business ID: $($inspection.business_id)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Get by UUID failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Update Inspection (PUT /v1/inspections/{inspection_id})
Write-Host "`n[6/10] Testing Update Inspection..." -ForegroundColor Yellow
try {
    $updateData = @{
        status = "In Progress"
        notes = "Inspection started"
    } | ConvertTo-Json
    
    $updated = Invoke-RestMethod -Uri "$baseUrl/v1/inspections/$testInspectionId" `
        -Method Put `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $updateData
    
    Write-Host "✅ Updated inspection" -ForegroundColor Green
    Write-Host "   Status: $($updated.status)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Update inspection failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# 7. Add Photo (POST /v1/inspections/{inspection_id}/photos)
Write-Host "`n[7/10] Testing Add Photo..." -ForegroundColor Yellow
try {
    $photoData = @{
        url = "https://example.com/photo1.jpg"
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        gps = @{ lat = 44.8; lon = -93.3 }
        notes = "Framing photo 1"
    } | ConvertTo-Json
    
    $updated = Invoke-RestMethod -Uri "$baseUrl/v1/inspections/$testInspectionId/photos" `
        -Method Post `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $photoData
    
    Write-Host "✅ Added photo successfully" -ForegroundColor Green
    $photoCount = if ($updated.photos -and $updated.photos.items) { $updated.photos.items.Count } else { 0 }
    Write-Host "   Total photos: $photoCount" -ForegroundColor Gray
} catch {
    Write-Host "❌ Add photo failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# 8. Add Deficiency (POST /v1/inspections/{inspection_id}/deficiencies)
Write-Host "`n[8/10] Testing Add Deficiency..." -ForegroundColor Yellow
try {
    $deficiencyData = @{
        description = "Missing header beam support"
        severity = "High"
        photo_refs = @("https://example.com/photo1.jpg")
        notes = "Must be corrected before proceeding"
    } | ConvertTo-Json
    
    $updated = Invoke-RestMethod -Uri "$baseUrl/v1/inspections/$testInspectionId/deficiencies" `
        -Method Post `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $deficiencyData
    
    Write-Host "✅ Added deficiency successfully" -ForegroundColor Green
    $defCount = if ($updated.deficiencies -and $updated.deficiencies.items) { $updated.deficiencies.items.Count } else { 0 }
    Write-Host "   Total deficiencies: $defCount" -ForegroundColor Gray
} catch {
    Write-Host "❌ Add deficiency failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# 9. List Filtered Inspections (by project and status)
Write-Host "`n[9/10] Testing Filtered List..." -ForegroundColor Yellow
try {
    $filtered = Invoke-RestMethod -Uri "$baseUrl/v1/inspections?project_id=$testProjectId&status_filter=In%20Progress" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✅ Retrieved filtered inspections" -ForegroundColor Green
    Write-Host "   Count: $($filtered.total)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Filtered list failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 10. Cancel Inspection (DELETE /v1/inspections/{inspection_id})
Write-Host "`n[10/10] Testing Cancel Inspection..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$baseUrl/v1/inspections/$testInspectionId" `
        -Method Delete `
        -Headers $headers
    
    Write-Host "✅ Cancelled inspection successfully" -ForegroundColor Green
    
    # Verify it's cancelled (not deleted, just status changed)
    try {
        $cancelled = Invoke-RestMethod -Uri "$baseUrl/v1/inspections/$testInspectionId" -Method Get -Headers $headers
        if ($cancelled.status -eq "Cancelled") {
            Write-Host "   ✓ Verified: Inspection status is Cancelled (soft delete)" -ForegroundColor Gray
        } else {
            Write-Host "   ⚠️  Warning: Expected status 'Cancelled', got '$($cancelled.status)'" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ⚠️  Warning: Could not verify cancellation" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Cancel inspection failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n=== TEST SUITE COMPLETE ===" -ForegroundColor Cyan
Write-Host "Review results above. All Phase B.2 endpoints have been tested.`n" -ForegroundColor Cyan
