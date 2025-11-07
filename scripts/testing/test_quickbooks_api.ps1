# QuickBooks API Test Script
# Run this in a separate terminal while the backend is running

Write-Host "🧪 QuickBooks API Test Suite" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/v1/quickbooks"

# Test 1: Status Check
Write-Host "✅ Test 1: Connection Status" -ForegroundColor Green
curl "$baseUrl/status" | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host ""
Start-Sleep -Seconds 1

# Test 2: Company Info
Write-Host "✅ Test 2: Company Information" -ForegroundColor Green
curl "$baseUrl/company" | ConvertFrom-Json | ConvertTo-Json -Depth 10
Write-Host ""
Start-Sleep -Seconds 1

# Test 3: List Customers
Write-Host "✅ Test 3: List Customers (First 5)" -ForegroundColor Green
$customersResponse = curl "$baseUrl/customers" | ConvertFrom-Json
Write-Host "Total Customers: $($customersResponse.count)" -ForegroundColor Yellow
$customersResponse.customers | Select-Object -First 5 | ForEach-Object {
    Write-Host "  - $($_.DisplayName) (ID: $($_.Id))" -ForegroundColor White
}
Write-Host ""
Start-Sleep -Seconds 1

# Test 4: List Invoices
Write-Host "✅ Test 4: List Invoices (First 5)" -ForegroundColor Green
$invoicesResponse = curl "$baseUrl/invoices" | ConvertFrom-Json
Write-Host "Total Invoices: $($invoicesResponse.count)" -ForegroundColor Yellow
$invoicesResponse.invoices | Select-Object -First 5 | ForEach-Object {
    Write-Host "  - Invoice #$($_.DocNumber): $$($_.TotalAmt) (Customer ID: $($_.CustomerRef.value))" -ForegroundColor White
}
Write-Host ""
Start-Sleep -Seconds 1

# Test 5: List Items/Services
Write-Host "✅ Test 5: List Items/Services (First 5)" -ForegroundColor Green
$itemsResponse = curl "$baseUrl/items" | ConvertFrom-Json
Write-Host "Total Items: $($itemsResponse.count)" -ForegroundColor Yellow
$itemsResponse.items | Select-Object -First 5 | ForEach-Object {
    Write-Host "  - $($_.Name) (Type: $($_.Type), ID: $($_.Id))" -ForegroundColor White
}
Write-Host ""
Start-Sleep -Seconds 1

# Test 6: List Vendors
Write-Host "✅ Test 6: List Vendors (First 5)" -ForegroundColor Green
$vendorsResponse = curl "$baseUrl/vendors" | ConvertFrom-Json
Write-Host "Total Vendors: $($vendorsResponse.count)" -ForegroundColor Yellow
$vendorsResponse.vendors | Select-Object -First 5 | ForEach-Object {
    Write-Host "  - $($_.DisplayName) (ID: $($_.Id))" -ForegroundColor White
}
Write-Host ""

Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ All Tests Completed!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test creating a customer: POST $baseUrl/customers" -ForegroundColor White
Write-Host "  2. Test creating an invoice: POST $baseUrl/invoices" -ForegroundColor White
Write-Host "  3. View API docs: http://localhost:8000/docs" -ForegroundColor White
