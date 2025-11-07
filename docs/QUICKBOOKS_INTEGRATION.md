# QuickBooks Online Integration Guide

## 🎯 Overview

The House Renovators API now integrates with QuickBooks Online for financial management. This enables:
- **Customer Sync**: Sync clients from Google Sheets to QuickBooks customers
- **Invoice Creation**: Create invoices for projects
- **Estimate Generation**: Generate estimates from project data
- **Financial Reporting**: Track payments and outstanding balances
- **Vendor Management**: Track contractors and suppliers

## 📋 Prerequisites

1. **QuickBooks Online Account** (Sandbox or Production)
2. **Intuit Developer Account** (https://developer.intuit.com/)
3. **QuickBooks App Created** in Intuit Developer Dashboard

## 🔧 Setup Instructions

### Step 1: Create QuickBooks App

1. Go to [Intuit Developer Dashboard](https://developer.intuit.com/)
2. Click "Create App"
3. Select "QuickBooks Online and Payments"
4. Fill in app details:
   - **App Name**: House Renovators AI Portal
   - **Description**: AI-powered construction management
5. Click "Create App"

### Step 2: Configure OAuth2 Credentials

1. In your app dashboard, go to **Keys & credentials**
2. Copy your **Client ID** and **Client Secret**
3. Add to `.env` file:
   ```bash
   QB_CLIENT_ID=your_client_id_here
   QB_CLIENT_SECRET=your_client_secret_here
   ```

### Step 3: Set Redirect URI

1. In **Keys & credentials** tab, scroll to **Redirect URIs**
2. Add these URIs:
   - **Development**: `http://localhost:8000/v1/quickbooks/callback`
   - **Production**: `https://api.houserenovatorsllc.com/v1/quickbooks/callback`
3. Save changes

### Step 4: Environment Configuration

Update your `.env` file:
```bash
# QuickBooks Configuration
QB_CLIENT_ID=ABkMGIeBEEgM0EJa4EqMkiYgPMJ16kVGHTyiT8gRfNu5XO3h5x
QB_CLIENT_SECRET=your_secret_from_dashboard
QB_REDIRECT_URI=http://localhost:8000/v1/quickbooks/callback
QB_ENVIRONMENT=sandbox  # Use 'production' for live QuickBooks
```

### Step 5: Test OAuth Flow

1. Start your backend:
   ```bash
   cd c:\Users\Steve Garay\Desktop\HouseRenovators-api
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. Visit authorization URL:
   ```
   http://localhost:8000/v1/quickbooks/auth
   ```

3. You'll be redirected to QuickBooks login page
4. Login with your QuickBooks credentials
5. Authorize the app
6. You'll be redirected back to `/callback` with tokens

7. Check connection status:
   ```
   http://localhost:8000/v1/quickbooks/status
   ```

## 📚 API Endpoints

### OAuth & Authentication

#### `GET /v1/quickbooks/auth`
Initiate OAuth2 flow (redirects to QuickBooks login)

#### `GET /v1/quickbooks/callback`
OAuth2 callback endpoint (handles authorization code)

#### `POST /v1/quickbooks/disconnect`
Disconnect from QuickBooks (clear tokens)

#### `GET /v1/quickbooks/status`
Check connection status
```json
{
  "authenticated": true,
  "realm_id": "123456789",
  "environment": "sandbox",
  "token_expires_at": "2025-01-06T12:00:00"
}
```

### Customer Operations

#### `GET /v1/quickbooks/customers`
Get all customers
```bash
curl http://localhost:8000/v1/quickbooks/customers
```

#### `POST /v1/quickbooks/customers`
Create a new customer
```json
{
  "DisplayName": "John Doe",
  "PrimaryPhone": {"FreeFormNumber": "(555) 123-4567"},
  "PrimaryEmailAddr": {"Address": "john@example.com"},
  "BillAddr": {
    "Line1": "123 Main St",
    "City": "Anytown",
    "CountrySubDivisionCode": "CA",
    "PostalCode": "12345"
  }
}
```

#### `GET /v1/quickbooks/customers/{customer_id}`
Get specific customer by ID

### Invoice Operations

#### `GET /v1/quickbooks/invoices`
Get all invoices (with optional filters)
```bash
# All invoices
curl http://localhost:8000/v1/quickbooks/invoices

# Filter by customer
curl http://localhost:8000/v1/quickbooks/invoices?customer_id=123

# Filter by date range
curl http://localhost:8000/v1/quickbooks/invoices?start_date=2025-01-01&end_date=2025-01-31
```

#### `POST /v1/quickbooks/invoices`
Create a new invoice
```json
{
  "CustomerRef": {"value": "123"},
  "Line": [
    {
      "Amount": 1000.00,
      "DetailType": "SalesItemLineDetail",
      "SalesItemLineDetail": {
        "ItemRef": {"value": "1"},
        "Qty": 1
      },
      "Description": "Renovation work"
    }
  ],
  "TxnDate": "2025-01-06",
  "DueDate": "2025-02-06",
  "DocNumber": "INV-001"
}
```

#### `GET /v1/quickbooks/invoices/{invoice_id}`
Get specific invoice by ID

### Estimate Operations

#### `POST /v1/quickbooks/estimates`
Create an estimate (same structure as invoice)

### Vendor Operations

#### `GET /v1/quickbooks/vendors`
Get all vendors

#### `POST /v1/quickbooks/bills`
Create a bill
```json
{
  "VendorRef": {"value": "123"},
  "Line": [
    {
      "Amount": 500.00,
      "DetailType": "AccountBasedExpenseLineDetail",
      "AccountBasedExpenseLineDetail": {
        "AccountRef": {"value": "1"}
      },
      "Description": "Materials"
    }
  ],
  "TxnDate": "2025-01-06"
}
```

### Items/Services

#### `GET /v1/quickbooks/items`
Get items/services
```bash
# All items
curl http://localhost:8000/v1/quickbooks/items

# Filter by type
curl http://localhost:8000/v1/quickbooks/items?item_type=Service
```

### Company Info

#### `GET /v1/quickbooks/company`
Get company information from QuickBooks

## 🧪 Testing with Sandbox

1. Create a **Sandbox Test Company**:
   - Go to [QuickBooks Sandbox](https://developer.intuit.com/app/developer/sandbox)
   - Create a test company
   - Add sample data (customers, items, etc.)

2. Set environment to sandbox:
   ```bash
   QB_ENVIRONMENT=sandbox
   ```

3. Test OAuth flow with sandbox credentials

4. Once working, switch to production:
   ```bash
   QB_ENVIRONMENT=production
   QB_REDIRECT_URI=https://api.houserenovatorsllc.com/v1/quickbooks/callback
   ```

## 🚀 Production Deployment

### Render Configuration

1. Go to Render dashboard for your backend service
2. Add environment variables:
   - `QB_CLIENT_ID`
   - `QB_CLIENT_SECRET`
   - `QB_REDIRECT_URI` (use production URL)
   - `QB_ENVIRONMENT=production`

3. In Intuit Developer Dashboard:
   - Go to Production Keys
   - Add production redirect URI
   - Get production Client ID and Secret

### Cloudflare Pages (Frontend)

Update frontend to call QuickBooks endpoints:
```javascript
// Example: Initiate OAuth
window.location.href = 'https://api.houserenovatorsllc.com/v1/quickbooks/auth';

// Example: Check status
const response = await fetch('https://api.houserenovatorsllc.com/v1/quickbooks/status');
const status = await response.json();
```

## ⚠️ Important Notes

### Token Storage
- **Current**: Tokens stored in memory (lost on restart)
- **Production**: Consider storing in Google Sheets or database
- **Security**: Never expose tokens in logs or responses

### Token Expiration
- Access tokens expire after 1 hour
- Service automatically refreshes tokens when needed
- Refresh tokens valid for 100 days

### Rate Limits
QuickBooks API has rate limits:
- **Sandbox**: 100 requests/minute
- **Production**: 500 requests/minute

### Data Sync Strategy
1. **Initial Sync**: Create customers in QuickBooks for existing clients
2. **New Clients**: Auto-create customer when client added to Google Sheets
3. **Projects**: Create invoices when project marked as complete
4. **Payments**: Sync payment status back to Google Sheets

## 🐛 Troubleshooting

### "Not authenticated" Error
```bash
# Check status
curl http://localhost:8000/v1/quickbooks/status

# If not authenticated, visit:
http://localhost:8000/v1/quickbooks/auth
```

### "Invalid Client" Error
- Verify `QB_CLIENT_ID` and `QB_CLIENT_SECRET` in `.env`
- Check credentials match Intuit Developer Dashboard

### "Redirect URI Mismatch" Error
- Verify `QB_REDIRECT_URI` in `.env`
- Check URI is added in Intuit Developer Dashboard
- Ensure exact match (including http/https)

### Token Expired Error
Service auto-refreshes, but if manually needed:
```python
from app.services.quickbooks_service import quickbooks_service
await quickbooks_service.refresh_access_token()
```

### API Request Errors
Check logs for details:
```bash
# View backend logs
tail -f logs/app.log
```

## 📖 Resources

- [QuickBooks API Documentation](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customer)
- [OAuth 2.0 Guide](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)
- [Sandbox Testing](https://developer.intuit.com/app/developer/qbo/docs/develop/sandboxes)
- [API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)

## 🎉 Next Steps

1. **AI Integration**: Use AI to suggest invoice items based on project type
2. **Auto-Sync**: Automatically sync new clients to QuickBooks
3. **Payment Tracking**: Track payments and update project status
4. **Financial Reports**: Generate financial summaries in AI chat
5. **Expense Management**: Track project expenses with bills
