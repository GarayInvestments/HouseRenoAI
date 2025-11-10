# QuickBooks Integration Guide

**Last Updated:** November 9, 2025  
**Status:** ✅ PRODUCTION OPERATIONAL

Complete guide for QuickBooks Online integration with House Renovators AI Portal.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Production Setup](#production-setup)
3. [OAuth2 Authentication](#oauth2-authentication)
4. [API Endpoints](#api-endpoints)
5. [Data Access & Sync](#data-access--sync)
6. [Testing & Validation](#testing--validation)
7. [Troubleshooting](#troubleshooting)
8. [Security & Compliance](#security--compliance)

---

## 🎯 Overview

### What's Connected

- **Company**: House Renovators, LLC
- **Email**: steve@houserenovatorsllc.com  
- **Realm ID**: 9130349982666256
- **Environment**: Production (live data)
- **Data**: 24 customers, 53+ invoices, estimates, bills

### Key Features

- ✅ OAuth2 production integration (Intuit approved)
- ✅ Real-time customer/invoice data access
- ✅ AI chat integration for QB queries
- ✅ Automated client sync with Google Sheets
- ✅ Token auto-refresh (100-day refresh tokens)
- ✅ Secure token storage in Google Sheets

---

## 🚀 Production Setup

### Prerequisites

1. **QuickBooks Online Account**
   - Active QBO account with admin access
   - Company ID (Realm ID) from QuickBooks

2. **Intuit Developer Account**
   - App created at developer.intuit.com
   - Production approval granted
   - Client ID and Secret obtained

3. **Backend Configuration**
   - Render account for hosting
   - Google Sheets API access
   - Domain with HTTPS enabled

### Environment Variables

Set these in Render dashboard (or `.env` for local):

```bash
# QuickBooks Production
QB_CLIENT_ID=ABFDraKIQB1PnJAX1c7yjoEln1XYV7qP74D3r84ivPNLlAG9US
QB_CLIENT_SECRET=eXJ7tbgoiKbqYzQMEjmTIMAH0gNaWJMy4mKVKPTq
QB_REDIRECT_URI=https://houserenoai.onrender.com/v1/quickbooks/callback
QB_ENVIRONMENT=production

# Backend API
API_URL=https://houserenoai.onrender.com
```

### Redirect URI Configuration

**In Intuit Developer Portal:**
1. Go to your app → Keys & OAuth
2. Add Redirect URI: `https://houserenoai.onrender.com/v1/quickbooks/callback`
3. Save changes

**Backend must match exactly** - case-sensitive, including protocol and path.

---

## 🔐 OAuth2 Authentication

### OAuth Flow

```
1. User initiates connection
   ↓
2. GET /v1/quickbooks/connect
   → Redirects to Intuit authorization page
   ↓
3. User grants permissions in QuickBooks
   ↓
4. Intuit calls back: /v1/quickbooks/callback?code=XXX&realmId=YYY
   ↓
5. Backend exchanges code for tokens
   ↓
6. Tokens saved to Google Sheets (QB_Tokens tab)
   - access_token (1 hour expiry)
   - refresh_token (100 days expiry)
   - realm_id (company identifier)
   ↓
7. ✅ Connection active
```

### Token Management

**Access Token:**
- Valid for 1 hour
- Used for all API calls
- Auto-refreshes when expired

**Refresh Token:**
- Valid for 100 days
- Used to get new access tokens
- Stored securely in Google Sheets

**Storage Structure (QB_Tokens sheet):**
```
Key              | Value
-----------------|------------------
access_token     | eyJenc...
refresh_token    | AB11...  
realm_id         | 9130349982666256
token_type       | Bearer
expires_at       | 2025-11-09 18:35:04
```

### Checking Authentication Status

```bash
# Check if authenticated
curl https://houserenoai.onrender.com/v1/quickbooks/status

# Response when authenticated:
{
  "authenticated": true,
  "realm_id": "9130349982666256",
  "company_name": "House Renovators, LLC",
  "token_expires_at": "2025-11-09 18:35:04"
}
```

### Re-authentication

Tokens expire after 100 days. To re-authenticate:

1. Navigate to `/v1/quickbooks/connect`
2. Complete OAuth flow again
3. New tokens replace old ones

---

## 📡 API Endpoints

### Base URL
`https://houserenoai.onrender.com/v1/quickbooks`

### Available Endpoints

#### 1. **Connect to QuickBooks**
```http
GET /v1/quickbooks/connect
```
Opens Intuit authorization page in browser. User grants permissions.

#### 2. **OAuth Callback** (automatic)
```http
GET /v1/quickbooks/callback?code=XXX&realmId=YYY
```
Handles OAuth response from Intuit. Exchanges code for tokens.

#### 3. **Check Status**
```http
GET /v1/quickbooks/status
Authorization: Bearer {jwt_token}
```
Returns authentication status and company info.

**Response:**
```json
{
  "authenticated": true,
  "realm_id": "9130349982666256",
  "company_name": "House Renovators, LLC",
  "token_expires_at": "2025-11-09 18:35:04"
}
```

#### 4. **Get Company Info**
```http
GET /v1/quickbooks/company
Authorization: Bearer {jwt_token}
```
Returns detailed company information from QuickBooks.

#### 5. **List Customers**
```http
GET /v1/quickbooks/customers
Authorization: Bearer {jwt_token}
```
Returns all customers from QuickBooks.

**Response:**
```json
[
  {
    "Id": "164",
    "DisplayName": "Ajay Nair",
    "PrimaryEmailAddr": {"Address": "ajay@2statescarolinas.com"},
    "PrimaryPhone": {"FreeFormNumber": "(555) 123-4567"},
    "BillAddr": {...}
  },
  ...
]
```

#### 6. **List Invoices**
```http
GET /v1/quickbooks/invoices
Authorization: Bearer {jwt_token}
```
Returns all invoices from QuickBooks.

**Response:**
```json
[
  {
    "Id": "123",
    "DocNumber": "1001",
    "CustomerRef": {"value": "164", "name": "Ajay Nair"},
    "TotalAmt": 5000.00,
    "Balance": 0.00,
    "DueDate": "2025-11-15",
    ...
  },
  ...
]
```

#### 7. **Create Invoice**
```http
POST /v1/quickbooks/invoices
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "customer_id": "164",
  "line_items": [
    {
      "description": "Renovation work",
      "amount": 5000.00,
      "quantity": 1
    }
  ],
  "due_date": "2025-12-01"
}
```

#### 8. **Update Invoice**
```http
PUT /v1/quickbooks/invoices/{invoice_id}
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "doc_number": "INV-1234",
  "memo": "Updated invoice details"
}
```

#### 9. **Disconnect**
```http
POST /v1/quickbooks/disconnect
Authorization: Bearer {jwt_token}
```
Clears stored tokens. Requires re-authentication.

---

## 🔄 Data Access & Sync

### Syncing Clients with Google Sheets

The AI can automatically sync Google Sheets clients with QuickBooks customers:

**Via Chat:**
```
User: "Sync all clients with QuickBooks"
AI: [Executes sync function]
```

**What it does:**
1. Fetches all clients from Google Sheets
2. Fetches all customers from QuickBooks
3. Matches by name (handles LLC variations) and email
4. Updates `QBO Client ID` column in Sheets with QB customer IDs

**Sync Results:**
- ✅ Matched: Clients successfully linked
- ⏭️ Already synced: Clients with existing QB IDs
- ❌ Not matched: Clients not found in QuickBooks

**Dry Run Mode:**
```
User: "Sync all clients with QuickBooks in dry run mode"
AI: Shows what would be synced without making changes
```

### Column Mapping

**Google Sheets → QuickBooks:**
- `Full Name` / `Client Name` → `DisplayName`
- `Email` → `PrimaryEmailAddr.Address`
- `QBO Client ID` → `Id` (QB customer ID)

**Important:** Column name is `QBO Client ID` with space, not `QBO_Client_ID`.

---

## 🧪 Testing & Validation

### Test Checklist

- [ ] **Authentication**
  - [ ] OAuth flow completes successfully
  - [ ] Tokens stored in Google Sheets
  - [ ] Status endpoint shows authenticated

- [ ] **Data Access**
  - [ ] Customers endpoint returns 24+ customers
  - [ ] Invoices endpoint returns 53+ invoices
  - [ ] Company info shows "House Renovators, LLC"

- [ ] **AI Integration**
  - [ ] Chat: "List all QuickBooks customers" works
  - [ ] Chat: "Show me invoices for Ajay Nair" works
  - [ ] No hallucinated customer names

- [ ] **Sync Function**
  - [ ] Dry run shows match count
  - [ ] Actual sync updates QBO Client ID column
  - [ ] 6 clients successfully synced

### Test Script

See `docs/CHAT_TESTING_SOP.md` for comprehensive testing procedures.

**Quick Test:**
```python
import requests

BASE_URL = "https://houserenoai.onrender.com"

# Login
login = requests.post(f"{BASE_URL}/v1/auth/login",
    json={"email": "test@houserenoai.com", "password": "TestPass123!"})
token = login.json()["access_token"]

# Test QB customers
response = requests.get(f"{BASE_URL}/v1/quickbooks/customers",
    headers={"Authorization": f"Bearer {token}"})
print(f"Customers: {len(response.json())}")

# Expected: 24+ customers
```

### Known Good Data

**Test Customers:**
- Ajay Nair (ID: 164) - ajay@2statescarolinas.com
- Erica Person (ID: 124)
- Gustavo Roldan (ID: 161)
- Marta Alder (ID: 167)
- Brandon Davis (ID: 169)

**Test Invoices:**
- Multiple invoices with real amounts
- No fabricated invoice numbers (INV-1001, etc.)

---

## 🔧 Troubleshooting

### Issue: "QuickBooks not authenticated"

**Symptoms:**
- API returns `{"authenticated": false}`
- Chat says "QuickBooks connection not available"

**Solutions:**
1. Check status: `curl https://houserenoai.onrender.com/v1/quickbooks/status`
2. Re-authenticate: Navigate to `/v1/quickbooks/connect`
3. Complete OAuth flow
4. Verify tokens in Google Sheets (QB_Tokens tab)

### Issue: "Invalid or expired token"

**Symptoms:**
- API calls return 401 Unauthorized
- Logs show token expiration errors

**Solutions:**
1. Refresh token automatically triggers on next request
2. If refresh token expired (100 days), re-authenticate
3. Check `expires_at` in QB_Tokens sheet

### Issue: Sync not updating QBO Client ID

**Symptoms:**
- AI says "Synced 6 clients" but column empty
- Logs show "Field 'QBO_Client_ID' not found"

**Solution:**
- Column name is `QBO Client ID` (with space), not `QBO_Client_ID` (underscore)
- Fixed in commit `3753e0c` (Nov 9, 2025)

### Issue: AI hallucinates customer names

**Symptoms:**
- AI lists fake names like "John Doe", "Emily Clark"
- Logs show "AI HALLUCINATION DETECTED"

**Solutions:**
- Fixed in commit `0f7cff1` (Nov 9, 2025)
- Increased max_tokens 1000→2000
- Strengthened system prompt
- Added fake name scanner

### Issue: OAuth redirect mismatch

**Symptoms:**
- OAuth callback fails with "redirect_uri mismatch"

**Solutions:**
1. Verify redirect URI in Intuit developer portal matches exactly:
   - `https://houserenoai.onrender.com/v1/quickbooks/callback`
2. Check `QB_REDIRECT_URI` env var in Render
3. No trailing slashes, case-sensitive

### Debug Commands

```powershell
# Check QuickBooks status
curl https://houserenoai.onrender.com/v1/quickbooks/status

# Check production logs
render logs -r srv-d44ak76uk2gs73a3psig --limit 50 --confirm -o text | Select-String "QuickBooks"

# Verify sync results
python check_qbo_sync.py
```

---

## 🛡️ Security & Compliance

### Data Protection

- **Tokens**: Stored in Google Sheets, not in code
- **HTTPS**: All endpoints use SSL/TLS encryption
- **JWT Auth**: Portal access requires valid JWT tokens
- **Refresh Strategy**: Automatic token refresh, no manual handling

### Intuit Compliance

**Required Pages:**
- ✅ Privacy Policy: https://portal.houserenovatorsllc.com/privacy
- ✅ Terms of Service: https://portal.houserenovatorsllc.com/terms

**OAuth Scopes:**
- `com.intuit.quickbooks.accounting` - Full accounting data access

**Audit Trail:**
- All QB API calls logged in Render
- Token refresh events logged
- Authentication attempts tracked

### Best Practices

1. **Never expose credentials** in code or logs
2. **Rotate refresh tokens** every 100 days (automatic)
3. **Monitor token usage** in production logs
4. **Test OAuth flow** after any URL changes
5. **Keep Intuit app settings** synchronized with backend config

---

## 📚 Related Documentation

- **Chat Testing SOP:** `docs/CHAT_TESTING_SOP.md`
- **API Documentation:** `docs/API_DOCUMENTATION.md`
- **Deployment Guide:** `docs/DEPLOYMENT.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`

---

## 🔄 Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-09 | 2.0 | Consolidated from 5 separate QB docs |
| 2025-11-09 | 1.4 | Added client sync feature |
| 2025-11-09 | 1.3 | Fixed column name bug in sync |
| 2025-11-09 | 1.2 | Fixed hallucination issues |
| 2025-11-07 | 1.1 | Production approval granted |
| 2025-11-06 | 1.0 | Initial production integration |

---

**Questions or Issues?**
- Review troubleshooting section above
- Check `docs/CHAT_TESTING_SOP.md` for testing procedures
- Monitor Render logs: `render logs -r srv-d44ak76uk2gs73a3psig --tail`
