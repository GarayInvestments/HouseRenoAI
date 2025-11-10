# Payments Feature Design Document

**Date:** November 10, 2025  
**Objective:** Implement Payments tracking in Google Sheets with QuickBooks sync  
**Status:** 📋 Planning Phase

---

## 🎯 Feature Overview

### Purpose
Track invoice payments in Google Sheets and sync with QuickBooks Online payment records. Enable users to:
- View payment history for invoices/projects
- Record manual payments (cash, check, Zelle)
- Sync QuickBooks payment data to Sheets
- Query payment status via AI chat

### Business Value
- **Cash Flow Visibility**: See which invoices are paid vs pending
- **Payment Tracking**: Record Zelle/cash payments outside QB
- **Reconciliation**: Match QB payments to projects/clients
- **AI Queries**: "Has Javier paid his invoice?" "Show me unpaid invoices"

---

## 📋 Google Sheets Structure

### Payments Sheet (New Tab)

**Range:** `Payments!A1:K`  
**Purpose:** Track all invoice payments with QB sync

| Col # | Column Name | Data Type | Required | Source | Notes |
|-------|------------|-----------|----------|---------|-------|
| 1 | Payment ID | String (8-char hex) | ✅ Yes | Auto-generated | Format: `PAY-abc123` |
| 2 | Invoice ID | String | ⚠️ Optional | Manual/QB sync | Links to QB invoice |
| 3 | Project ID | String | ⚠️ Optional | Linked from invoice | Links to Projects sheet |
| 4 | Client ID | String | ✅ Yes | Linked from invoice | Links to Clients sheet |
| 5 | Amount | Number | ✅ Yes | Manual/QB sync | Payment amount (no $ symbol) |
| 6 | Payment Date | Date (YYYY-MM-DD) | ✅ Yes | Manual/QB sync | When payment received |
| 7 | Payment Method | String | ✅ Yes | Manual/QB sync | e.g., "Zelle", "Check", "Credit Card" |
| 8 | Status | String | ✅ Yes | Default: "Pending" | "Pending", "Completed", "Failed", "Refunded" |
| 9 | QB Payment ID | String | ⚠️ Optional | QB sync only | QuickBooks Payment entity ID |
| 10 | Transaction ID | String | ⚠️ Optional | Manual entry | Zelle/check number reference |
| 11 | Notes | String (long) | ❌ No | Manual/AI | Additional payment details |

### Validation Rules
- **Payment ID**: Unique, 8-char hex with `PAY-` prefix
- **Amount**: Must be positive number
- **Payment Method**: Enum - "Zelle", "Check", "Cash", "Credit Card", "ACH", "Other"
- **Status**: Enum - "Pending", "Completed", "Failed", "Refunded"
- **Client ID**: Must match existing client in Clients sheet

### Sample Data
```
Payment ID | Invoice ID | Project ID | Client ID | Amount | Payment Date | Payment Method | Status | QB Payment ID | Transaction ID | Notes
PAY-abc123 | INV-001   | 4717d93f  | 6dd00ad4 | 4000   | 2025-11-08  | Zelle         | Completed | 145        | zelle-xyz789  | Received via Zelle
PAY-def456 | INV-002   | 08833ef5  | 08833ef5 | 3500   | 2025-11-09  | Check         | Completed |            | CHK-12345    | Check #12345
```

---

## 🔗 QuickBooks API Integration

### QB Payment Entity Structure
QuickBooks has a `Payment` entity that links to `Invoice` entities:

```json
{
  "Payment": {
    "Id": "145",
    "CustomerRef": { "value": "161", "name": "Javier Martinez" },
    "TotalAmt": 4000.00,
    "TxnDate": "2025-11-08",
    "PaymentMethodRef": { "value": "1", "name": "Cash" },
    "Line": [
      {
        "Amount": 4000.00,
        "LinkedTxn": [
          {
            "TxnId": "234",
            "TxnType": "Invoice"
          }
        ]
      }
    ]
  }
}
```

### Key QB Payment Fields
- **Id**: QuickBooks Payment ID → Maps to QB Payment ID (col 9)
- **CustomerRef.value**: QB Customer ID → Resolve to Client ID (col 4)
- **TotalAmt**: Payment amount → Maps to Amount (col 5)
- **TxnDate**: Payment date → Maps to Payment Date (col 6)
- **PaymentMethodRef.name**: Payment method → Maps to Payment Method (col 7)
- **Line.LinkedTxn.TxnId**: Invoice ID → Maps to Invoice ID (col 2)

### QB API Endpoints
```
GET /v3/company/{realmId}/query?query=SELECT * FROM Payment
GET /v3/company/{realmId}/payment/{paymentId}
POST /v3/company/{realmId}/payment
```

---

## 🏗️ Architecture Design

### Component Overview
```
Frontend Chat → AI (OpenAI) → AI Functions Handler → QuickBooks Service → QB API
                                      ↓
                                Google Service → Google Sheets Payments Tab
```

### Data Flow

#### Sync Flow (QB → Sheets)
1. User asks: "Show me all payments" or "Has Javier paid?"
2. AI calls `sync_quickbooks_payments()` function
3. QuickBooks Service:
   - Calls QB API: `GET /payment`
   - Retrieves all payments
   - Maps QB fields to Sheets structure
4. Google Service:
   - Checks if Payment ID (QB Payment ID) exists
   - If exists: Update row
   - If new: Insert row
5. Return synced payment data to AI

#### Manual Entry Flow (Sheets only)
1. User says: "Record Zelle payment of $4000 from Javier on Nov 8"
2. AI calls `record_payment()` function with parameters
3. Handler creates payment record:
   - Generate Payment ID
   - Lookup Client ID from client name
   - Set Payment Method = "Zelle"
   - Set Status = "Completed"
   - Leave QB Payment ID empty (manual entry)
4. Google Service inserts row to Payments sheet
5. Return confirmation to AI

#### Query Flow (Read-only)
1. User asks: "What payments has Javier made?"
2. AI loads Payments context (if available) or calls `get_client_payments(client_id)`
3. Filter payments by Client ID
4. Display payment history

---

## 💻 Implementation Details

### 1. Google Sheets Setup

**Task:** Create new "Payments" tab with header row

**Steps:**
1. Open Google Sheet in browser
2. Add new tab: "Payments"
3. Add header row (A1:K1):
   ```
   Payment ID | Invoice ID | Project ID | Client ID | Amount | Payment Date | Payment Method | Status | QB Payment ID | Transaction ID | Notes
   ```
4. Set data validation for columns:
   - **Payment Method (G)**: List of "Zelle,Check,Cash,Credit Card,ACH,Other"
   - **Status (H)**: List of "Pending,Completed,Failed,Refunded"

---

### 2. QuickBooks Service Updates

**File:** `app/services/quickbooks_service.py`

**Add Payment Operations Section:**

```python
# ==================== PAYMENT OPERATIONS ====================

async def get_payments(
    self,
    customer_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve payments from QuickBooks with optional filters.
    
    Args:
        customer_id: Filter by QB customer ID
        start_date: Filter payments after this date (YYYY-MM-DD)
        end_date: Filter payments before this date (YYYY-MM-DD)
    
    Returns:
        List of payment records with mapped fields
    """
    self._check_authentication()
    
    # Build query
    query = "SELECT * FROM Payment"
    conditions = []
    
    if customer_id:
        conditions.append(f"CustomerRef = '{customer_id}'")
    if start_date:
        conditions.append(f"TxnDate >= '{start_date}'")
    if end_date:
        conditions.append(f"TxnDate <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " MAXRESULTS 1000"
    
    response = await self._make_request(
        method="GET",
        endpoint="/query",
        params={"query": query}
    )
    
    payments = response.get("QueryResponse", {}).get("Payment", [])
    logger.info(f"Retrieved {len(payments)} payments from QB API")
    
    return payments

async def get_payment_by_id(self, payment_id: str) -> Dict[str, Any]:
    """Get a specific payment by QB Payment ID"""
    self._check_authentication()
    
    response = await self._make_request(
        method="GET",
        endpoint=f"/payment/{payment_id}",
        params={"minorversion": "73"}
    )
    
    return response.get("Payment", {})

async def sync_payments_to_sheets(
    self,
    google_service,
    days_back: int = 90
) -> Dict[str, Any]:
    """
    Sync QuickBooks payments to Google Sheets Payments tab.
    
    Args:
        google_service: Google Sheets service instance
        days_back: How many days back to sync (default 90)
    
    Returns:
        Sync summary with counts
    """
    from datetime import datetime, timedelta
    
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    # Get QB payments
    qb_payments = await self.get_payments(start_date=start_date)
    
    # Get existing payments from Sheets
    existing_payments = await google_service.get_sheet_data('Payments')
    existing_qb_ids = {p.get('QB Payment ID') for p in existing_payments if p.get('QB Payment ID')}
    
    synced_count = 0
    new_count = 0
    updated_count = 0
    
    for qb_payment in qb_payments:
        payment_id = qb_payment.get('Id')
        
        # Map QB payment to Sheets structure
        sheet_payment = await self._map_qb_payment_to_sheet(qb_payment, google_service)
        
        if payment_id in existing_qb_ids:
            # Update existing
            await google_service.update_record_by_field(
                sheet_name='Payments',
                field_name='QB Payment ID',
                field_value=payment_id,
                updates=sheet_payment
            )
            updated_count += 1
        else:
            # Insert new
            await google_service.append_row('Payments', list(sheet_payment.values()))
            new_count += 1
        
        synced_count += 1
    
    return {
        "status": "success",
        "synced": synced_count,
        "new": new_count,
        "updated": updated_count
    }

async def _map_qb_payment_to_sheet(
    self,
    qb_payment: Dict[str, Any],
    google_service
) -> Dict[str, Any]:
    """Map QuickBooks Payment entity to Sheets Payments row"""
    import uuid
    
    # Extract QB fields
    qb_id = qb_payment.get('Id')
    customer_ref = qb_payment.get('CustomerRef', {}).get('value')
    total_amt = qb_payment.get('TotalAmt', 0)
    txn_date = qb_payment.get('TxnDate')
    payment_method = qb_payment.get('PaymentMethodRef', {}).get('name', 'Unknown')
    
    # Extract linked invoice ID
    invoice_id = None
    lines = qb_payment.get('Line', [])
    for line in lines:
        linked_txns = line.get('LinkedTxn', [])
        for txn in linked_txns:
            if txn.get('TxnType') == 'Invoice':
                invoice_id = txn.get('TxnId')
                break
    
    # Resolve Client ID from QB Customer ID
    # Look up in Clients sheet for matching QBO Client ID
    clients = await google_service.get_sheet_data('Clients')
    client_id = None
    for client in clients:
        if client.get('QBO Client ID') == customer_ref:
            client_id = client.get('Client ID')
            break
    
    # Generate Payment ID
    payment_id = f"PAY-{uuid.uuid4().hex[:8]}"
    
    return {
        'Payment ID': payment_id,
        'Invoice ID': invoice_id or '',
        'Project ID': '',  # Will be filled later if we link invoice to project
        'Client ID': client_id or '',
        'Amount': total_amt,
        'Payment Date': txn_date,
        'Payment Method': payment_method,
        'Status': 'Completed',  # QB payments are completed
        'QB Payment ID': qb_id,
        'Transaction ID': '',
        'Notes': f'Synced from QuickBooks on {datetime.now().strftime("%Y-%m-%d")}'
    }
```

---

### 3. API Routes

**File:** `app/routes/payments.py` (NEW)

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import logging

import app.services.google_service as google_service_module
import app.services.quickbooks_service as quickbooks_service_module
from app.routes.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

def get_google_service():
    if not google_service_module.google_service:
        raise HTTPException(status_code=503, detail="Google service not initialized")
    return google_service_module.google_service

def get_quickbooks_service():
    if not quickbooks_service_module.quickbooks_service:
        raise HTTPException(status_code=503, detail="QuickBooks service not initialized")
    return quickbooks_service_module.quickbooks_service

@router.get("/")
async def get_all_payments(current_user: dict = Depends(get_current_user)):
    """Get all payments from Google Sheets"""
    try:
        google_service = get_google_service()
        payments = await google_service.get_sheet_data('Payments')
        logger.info(f"Retrieved {len(payments)} payments")
        return payments
    except Exception as e:
        logger.error(f"Failed to get payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{payment_id}")
async def get_payment(payment_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific payment by ID"""
    try:
        google_service = get_google_service()
        payments = await google_service.get_sheet_data('Payments')
        
        payment = next((p for p in payments if p.get('Payment ID') == payment_id), None)
        if not payment:
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        
        return payment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get payment {payment_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_quickbooks_payments(
    days_back: int = 90,
    current_user: dict = Depends(get_current_user)
):
    """Sync QuickBooks payments to Google Sheets"""
    try:
        google_service = get_google_service()
        qb_service = get_quickbooks_service()
        
        result = await qb_service.sync_payments_to_sheets(google_service, days_back)
        logger.info(f"Payment sync complete: {result}")
        return result
    except Exception as e:
        logger.error(f"Payment sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def record_payment(
    payment_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Record a manual payment (non-QB)"""
    try:
        import uuid
        from datetime import datetime
        
        google_service = get_google_service()
        
        # Generate Payment ID
        payment_id = f"PAY-{uuid.uuid4().hex[:8]}"
        
        # Build payment record
        payment = {
            'Payment ID': payment_id,
            'Invoice ID': payment_data.get('invoice_id', ''),
            'Project ID': payment_data.get('project_id', ''),
            'Client ID': payment_data.get('client_id', ''),
            'Amount': payment_data.get('amount', 0),
            'Payment Date': payment_data.get('payment_date', datetime.now().strftime('%Y-%m-%d')),
            'Payment Method': payment_data.get('payment_method', 'Other'),
            'Status': payment_data.get('status', 'Completed'),
            'QB Payment ID': '',  # Manual entry - no QB ID
            'Transaction ID': payment_data.get('transaction_id', ''),
            'Notes': payment_data.get('notes', 'Manual entry')
        }
        
        # Append to Payments sheet
        await google_service.append_row('Payments', list(payment.values()))
        
        logger.info(f"Recorded manual payment: {payment_id}")
        return {"status": "success", "payment": payment}
        
    except Exception as e:
        logger.error(f"Failed to record payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Register in `app/main.py`:**
```python
from app.routes import payments

app.include_router(payments.router, prefix="/v1/payments", tags=["payments"])
```

---

### 4. AI Functions

**File:** `app/handlers/ai_functions.py`

**Add Payments Handlers:**

```python
async def handle_sync_payments(
    args: Dict[str, Any],
    google_service,
    quickbooks_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """Sync QuickBooks payments to Sheets"""
    try:
        days_back = args.get("days_back", 90)
        
        result = await quickbooks_service.sync_payments_to_sheets(google_service, days_back)
        
        memory_manager.set(session_id, "last_action", "synced_payments")
        
        logger.info(f"AI executed: Synced {result['synced']} payments")
        
        return {
            "status": "success",
            "details": f"Synced {result['synced']} payments ({result['new']} new, {result['updated']} updated)",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error syncing payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_get_client_payments(
    args: Dict[str, Any],
    google_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """Get all payments for a specific client"""
    try:
        client_id = args["client_id"]
        
        payments = await google_service.get_sheet_data('Payments')
        client_payments = [p for p in payments if p.get('Client ID') == client_id]
        
        memory_manager.set(session_id, "last_client_id", client_id)
        
        logger.info(f"AI executed: Retrieved {len(client_payments)} payments for client {client_id}")
        
        return {
            "status": "success",
            "payments": client_payments,
            "count": len(client_payments)
        }
    except Exception as e:
        logger.error(f"Error getting client payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Register in FUNCTION_HANDLERS:**
```python
FUNCTION_HANDLERS = {
    # ... existing handlers ...
    "sync_quickbooks_payments": handle_sync_payments,
    "get_client_payments": handle_get_client_payments,
}
```

---

### 5. OpenAI Service Integration

**File:** `app/services/openai_service.py`

**Add Payments Context (after Permits section):**

```python
# Add payments data with safe_field sanitization
payments_data = context.get('all_payments', [])
if payments_data:
    context_parts.append("\n\n=== PAYMENTS DATA ===")
    logger.info(f"[DEBUG] Adding {len(payments_data)} payments to context (showing up to 50)")
    for payment in payments_data[:50]:
        payment_id = safe_field(payment.get('Payment ID'))
        client_id = safe_field(payment.get('Client ID'))
        amount = safe_field(payment.get('Amount'))
        payment_date = safe_field(payment.get('Payment Date'))
        payment_method = safe_field(payment.get('Payment Method'))
        status = safe_field(payment.get('Status'))
        invoice_id = safe_field(payment.get('Invoice ID'))
        
        context_parts.append(
            f"\n✓ Payment ID: {payment_id}"
            f"\n  Client ID: {client_id}"
            f"\n  Amount: ${amount}"
            f"\n  Date: {payment_date}"
            f"\n  Method: {payment_method}"
            f"\n  Status: {status}"
            f"\n  Invoice ID: {invoice_id}"
        )
```

**Add Function Definitions (in tools array):**

```python
{
    "type": "function",
    "function": {
        "name": "sync_quickbooks_payments",
        "description": "Sync payment records from QuickBooks Online to Google Sheets. Use when user asks to 'sync payments' or 'update payment data'.",
        "parameters": {
            "type": "object",
            "properties": {
                "days_back": {
                    "type": "integer",
                    "description": "How many days back to sync payments (default 90)"
                }
            },
            "required": []
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_client_payments",
        "description": "Get all payment records for a specific client. Use when user asks about a client's payment history.",
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "The Client ID to get payments for"
                }
            },
            "required": ["client_id"]
        }
    }
}
```

---

### 6. Context Builder Integration

**File:** `app/utils/context_builder.py`

**Add payments keywords:**

```python
PAYMENTS_KEYWORDS = ['payment', 'paid', 'unpaid', 'invoice paid', 'pay', 'zelle', 'check', 'cash']

# In build_context function:
if any(keyword in message_lower for keyword in PAYMENTS_KEYWORDS):
    required_data.add('payments')

# In loading section:
if 'payments' in required_data:
    payments = await google_service.get_sheet_data('Payments')
    context['all_payments'] = payments
    logger.info(f"Loaded {len(payments)} payments")
```

---

## 📊 Testing Plan

### Manual Testing Scenarios

1. **Sync Test:**
   - "Sync payments from QuickBooks"
   - Verify Payments sheet populated with QB data

2. **Query Test:**
   - "Has Javier Martinez paid his invoice?"
   - "Show me all payments from last month"
   - "What payments have we received?"

3. **Manual Entry Test:**
   - "Record a $4000 Zelle payment from Javier on Nov 8"
   - Verify payment appears in Sheets

4. **Invoice Linking Test:**
   - "Show me the payment for invoice INV-001"
   - Verify correct payment displayed

### Expected AI Responses

**Query:** "Has Javier Martinez paid his invoice?"
**Expected:** "Yes, Javier Martinez made a payment of $4,000 via Zelle on November 8, 2025. The payment status is Completed."

**Query:** "Show me all unpaid invoices"
**Expected:** (After syncing invoices and payments) Lists invoices without matching payments

---

## 🚀 Deployment Checklist

- [ ] Create Payments tab in Google Sheets with headers
- [ ] Add data validation for Payment Method and Status columns
- [ ] Implement QB payment operations in `quickbooks_service.py`
- [ ] Create `app/routes/payments.py` with API endpoints
- [ ] Register payments routes in `app/main.py`
- [ ] Add payment handlers to `ai_functions.py`
- [ ] Add payment context to `openai_service.py`
- [ ] Add payment keywords to `context_builder.py`
- [ ] Update `GOOGLE_SHEETS_STRUCTURE.md` with Payments sheet
- [ ] Test QB payments sync with production data
- [ ] Test AI queries about payments
- [ ] Document payment workflows in user guide

---

## 🔐 Security Considerations

1. **Authentication:** All payment routes require JWT authentication
2. **QB Tokens:** Payment sync requires valid QB OAuth tokens
3. **Data Privacy:** Payment amounts and methods are sensitive - log carefully
4. **Audit Trail:** Always log payment sync operations with counts

---

## 📈 Success Metrics

- **Sync Accuracy:** 100% of QB payments sync correctly
- **Query Response:** AI answers payment questions without follow-up
- **Manual Entry:** Users can record non-QB payments easily
- **Performance:** Payment sync completes in <10 seconds for 90 days

---

**Next Steps:** Begin implementation with Todo List tasks 4-8
