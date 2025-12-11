# Quick test for specific failing endpoint
$baseUrl = "http://localhost:8000"

# Login
$loginResponse = Invoke-RestMethod -Uri "$baseUrl/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"steve@garayinvestments.com","password":"Stv060485!"}'
$token = $loginResponse.access_token
$headers = @{ "Authorization" = "Bearer $token" }

# Get a permit ID from the list
$permits = Invoke-RestMethod -Uri "$baseUrl/v1/permits" -Method Get -Headers $headers
$testPermitId = $permits.items[0].permit_id
Write-Host "Using permit ID: $testPermitId" -ForegroundColor Cyan

# Test GET by UUID
Write-Host "`nTesting GET /v1/permits/$testPermitId" -ForegroundColor Yellow
try {
    $permit = Invoke-RestMethod -Uri "$baseUrl/v1/permits/$testPermitId" -Method Get -Headers $headers
    Write-Host "✅ Success" -ForegroundColor Green
    Write-Host "Business ID: $($permit.business_id)" -ForegroundColor Gray
    Write-Host "Type: $($permit.permit_type)" -ForegroundColor Gray
    Write-Host "Status: $($permit.status)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}
