# Simple inspection test
Write-Host "Testing Inspection API..." -ForegroundColor Cyan

# Login
Write-Host "`n1. Login..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"steve@garayinvestments.com","password":"Stv060485!"}'
    $token = $loginResponse.access_token
    Write-Host "✅ Logged in" -ForegroundColor Green
} catch {
    Write-Host "❌ Login failed" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{ "Authorization" = "Bearer $token" }

# Get a permit
Write-Host "`n2. Getting permits..." -ForegroundColor Yellow
$permits = Invoke-RestMethod -Uri "http://localhost:8000/v1/permits" -Method Get -Headers $headers
Write-Host "✅ Found $($permits.total) permits" -ForegroundColor Green
$testPermitId = $permits.items[0].permit_id
$testProjectId = $permits.items[0].project_id

# Create inspection
Write-Host "`n3. Creating inspection..." -ForegroundColor Yellow
$inspectionData = @{
    permit_id = $testPermitId
    project_id = $testProjectId
    inspection_type = "Framing"
    status = "Scheduled"
} | ConvertTo-Json

try {
    $inspection = Invoke-RestMethod -Uri "http://localhost:8000/v1/inspections" -Method Post -Headers $headers -ContentType "application/json" -Body $inspectionData
    Write-Host "✅ Created inspection: $($inspection.business_id)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

Write-Host "`nDone!" -ForegroundColor Cyan
