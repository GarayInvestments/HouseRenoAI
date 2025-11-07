# QuickBooks API Advanced Tests
# Tests POST operations (creating customers, invoices, etc.)

Write-Host "🧪 QuickBooks API Advanced Test Suite" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/v1/quickbooks"

# Test 1: Create a Test Customer
Write-Host "✅ Test 1: Create New Customer" -ForegroundColor Green
$customerData = @{
    DisplayName = "Test Customer $(Get-Date -Format 'MMddHHmmss')"
    GivenName = "John"
    FamilyName = "Doe"
    PrimaryPhone = @{
        FreeFormNumber = "(555) 123-4567"
    }
    PrimaryEmailAddr = @{
        Address = "john.doe@example.com"
    }
    BillAddr = @{
        Line1 = "123 Main Street"
        City = "Anytown"
        CountrySubDivisionCode = "CA"
        PostalCode = "90210"
    }
} | ConvertTo-Json

$newCustomer = Invoke-RestMethod -Uri "$baseUrl/customers" -Method Post -Body $customerData -ContentType "application/json"
Write-Host "Created Customer: $($newCustomer.customer.DisplayName) (ID: $($newCustomer.customer.Id))" -ForegroundColor Yellow
$customerId = $newCustomer.customer.Id
Write-Host ""
Start-Sleep -Seconds 2

# Test 2: Get the Customer We Just Created
Write-Host "✅ Test 2: Retrieve Created Customer" -ForegroundColor Green
$retrievedCustomer = Invoke-RestMethod -Uri "$baseUrl/customers/$customerId" -Method Get
Write-Host "Retrieved: $($retrievedCustomer.customer.DisplayName)" -ForegroundColor Yellow
Write-Host "  Email: $($retrievedCustomer.customer.PrimaryEmailAddr.Address)" -ForegroundColor White
Write-Host "  Phone: $($retrievedCustomer.customer.PrimaryPhone.FreeFormNumber)" -ForegroundColor White
Write-Host ""
Start-Sleep -Seconds 2

# Test 3: Get Available Items (needed for invoice)
Write-Host "✅ Test 3: Get Available Items for Invoice" -ForegroundColor Green
$items = Invoke-RestMethod -Uri "$baseUrl/items" -Method Get
$firstItem = $items.items | Select-Object -First 1
Write-Host "Using Item: $($firstItem.Name) (ID: $($firstItem.Id))" -ForegroundColor Yellow
Write-Host ""
Start-Sleep -Seconds 2

# Test 4: Create an Invoice
Write-Host "✅ Test 4: Create Invoice for New Customer" -ForegroundColor Green
$invoiceData = @{
    CustomerRef = @{
        value = $customerId
    }
    Line = @(
        @{
            Amount = 1500.00
            DetailType = "SalesItemLineDetail"
            SalesItemLineDetail = @{
                ItemRef = @{
                    value = $firstItem.Id
                }
                Qty = 1
            }
            Description = "Renovation Services - Kitchen Remodel"
        }
    )
    TxnDate = (Get-Date -Format "yyyy-MM-dd")
    DueDate = (Get-Date).AddDays(30).ToString("yyyy-MM-dd")
} | ConvertTo-Json -Depth 10

$newInvoice = Invoke-RestMethod -Uri "$baseUrl/invoices" -Method Post -Body $invoiceData -ContentType "application/json"
Write-Host "Created Invoice #$($newInvoice.invoice.DocNumber)" -ForegroundColor Yellow
Write-Host "  Amount: `$$($newInvoice.invoice.TotalAmt)" -ForegroundColor White
Write-Host "  Due Date: $($newInvoice.invoice.DueDate)" -ForegroundColor White
Write-Host ""
Start-Sleep -Seconds 2

# Test 5: Create an Estimate
Write-Host "✅ Test 5: Create Estimate" -ForegroundColor Green
$estimateData = @{
    CustomerRef = @{
        value = $customerId
    }
    Line = @(
        @{
            Amount = 2500.00
            DetailType = "SalesItemLineDetail"
            SalesItemLineDetail = @{
                ItemRef = @{
                    value = $firstItem.Id
                }
                Qty = 1
            }
            Description = "Bathroom Renovation Estimate"
        }
    )
    TxnDate = (Get-Date -Format "yyyy-MM-dd")
} | ConvertTo-Json -Depth 10

$newEstimate = Invoke-RestMethod -Uri "$baseUrl/estimates" -Method Post -Body $estimateData -ContentType "application/json"
Write-Host "Created Estimate #$($newEstimate.estimate.DocNumber)" -ForegroundColor Yellow
Write-Host "  Amount: `$$($newEstimate.estimate.TotalAmt)" -ForegroundColor White
Write-Host ""
Start-Sleep -Seconds 2

# Test 6: Filter Invoices by Customer
Write-Host "✅ Test 6: Get Invoices for New Customer" -ForegroundColor Green
$customerInvoices = Invoke-RestMethod -Uri "$baseUrl/invoices?customer_id=$customerId" -Method Get
Write-Host "Found $($customerInvoices.count) invoice(s) for customer" -ForegroundColor Yellow
$customerInvoices.invoices | ForEach-Object {
    Write-Host "  - Invoice #$($_.DocNumber): `$$($_.TotalAmt)" -ForegroundColor White
}
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✅ All Advanced Tests Completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Yellow
Write-Host "  - Created Customer ID: $customerId" -ForegroundColor White
Write-Host "  - Created Invoice: #$($newInvoice.invoice.DocNumber)" -ForegroundColor White
Write-Host "  - Created Estimate: #$($newEstimate.estimate.DocNumber)" -ForegroundColor White
Write-Host ""
Write-Host "💡 Check QuickBooks sandbox to verify!" -ForegroundColor Yellow
