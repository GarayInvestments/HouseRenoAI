# Invoice Integration Plan: Merge QuickBooks Cache + Internal Database

**Date**: December 15, 2025  
**Status**: Planning Phase  
**Goal**: Show unified invoice view combining QuickBooks data with internal permit/client links

---

## 📊 Current State Analysis

### Database Research Summary

**Internal Invoices Table** (`invoices`):
- **Count**: 0 invoices (empty table)
- **Key Fields**: 
  - `invoice_id` (UUID primary key)
  - `business_id` (auto-generated, e.g., "INV-00001")
  - `qb_invoice_id` (VARCHAR, UNIQUE index) ← **LINKING FIELD**
  - `project_id` (UUID, links to permits)
  - `client_id` (UUID, links to clients)
  - `invoice_number`, `total_amount`, `status`, `line_items` (JSONB)
  - `sync_status`, `last_sync_attempt` (for QB sync tracking)

**QuickBooks Invoices Cache** (`quickbooks_invoices_cache`):
- **Count**: 13 invoices (all QB imports)
- **Key Fields**:
  - `qb_invoice_id` (VARCHAR primary key) ← **LINKING FIELD**
  - `customer_id` (QB customer ID)
  - `doc_number` (e.g., "16530-Ardrey")
  - `total_amount`, `balance`, `due_date`
  - `qb_data` (JSONB with full QB response)

**Clients Table** (`clients`):
- **Count**: 5 clients
- **Key Fields**:
  - `client_id` (UUID primary key)
  - `business_id` (auto-generated, e.g., "CL-00003")
  - `qb_customer_id` (VARCHAR) ← **LINKING FIELD TO QB**
  - `full_name`, `email`, `phone`
  - **Current State**: All `qb_customer_id` fields are NULL (no linkage yet)

**Permits Table** (`permits`):
- **Has**: `client_id` (UUID links to clients)
- **Linkage**: Permit → Client → (needs) QB Customer → QB Invoice

**QuickBooks Customers Cache** (`quickbooks_customers_cache`):
- **Count**: 8 GC Compliance customers
- **Key Fields**:
  - `qb_customer_id` (VARCHAR primary key)
  - `display_name` (e.g., "Ajay Nair")
  - `company_name`, `email`, `phone`

---

## 🔗 Linking Strategy

### Phase 1: Link Clients to QB Customers
**Match internal clients to QB customers by name/email**

```sql
-- Example: Link Ajay Nair
UPDATE clients 
SET qb_customer_id = '164' 
WHERE full_name = 'Ajay Nair';
```

**Matching Logic**:
1. Exact name match (case-insensitive)
2. Email match (if available)
3. Manual mapping for unmatched clients

**Anticipated Issues**:
- ✅ Name variations ("Steve Jones" vs "Stephen Jones")
- ✅ Missing emails in one system
- ✅ Multiple clients with same name

**Solution**: Create matching script with fuzzy matching + manual review list

---

### Phase 2: Sync QB Invoices to Internal Invoices Table
**Copy QB cache invoices → internal invoices with client/project links**

```sql
-- Create internal invoice from QB cache
INSERT INTO invoices (
    qb_invoice_id,
    client_id,
    invoice_number,
    total_amount,
    balance,
    due_date,
    status,
    sync_status,
    line_items
)
SELECT 
    qbc.qb_invoice_id,
    c.client_id,  -- Link to internal client
    qbc.doc_number,
    qbc.total_amount,
    qbc.balance,
    qbc.due_date,
    'sent'::invoice_status_enum,
    'synced',
    qbc.qb_data->'Line'  -- Extract line items from QB JSON
FROM quickbooks_invoices_cache qbc
JOIN quickbooks_customers_cache qcc ON qbc.customer_id = qcc.qb_customer_id
JOIN clients c ON c.qb_customer_id = qcc.qb_customer_id
WHERE qbc.is_active = true
ON CONFLICT (qb_invoice_id) DO UPDATE SET
    total_amount = EXCLUDED.total_amount,
    balance = EXCLUDED.balance,
    updated_at = CURRENT_TIMESTAMP;
```

**What This Does**:
- Creates invoice records in internal database
- Links to clients via `qb_customer_id` matching
- Preserves QB invoice ID for future syncs
- Extracts line items from QB JSONB

**Anticipated Issues**:
- ✅ QB invoice has no matching client (customer not in our system)
  - **Solution**: Create placeholder client or skip invoice
- ✅ Line items format mismatch (QB format vs our format)
  - **Solution**: Transform QB line items to our JSONB structure
- ✅ Status enum mismatch ("EmailSent" vs "sent")
  - **Solution**: Map QB statuses to our enum values
- ✅ Project linking (QB invoice doesn't know which permit)
  - **Solution**: Manual project assignment or permit number matching in line items

---

### Phase 3: Link Invoices to Permits
**Match invoices to permits using permit numbers in line item descriptions**

```sql
-- Example QB line item description:
-- "GC Compliance for permit number RES-ADD-25-000990"

UPDATE invoices
SET project_id = (
    SELECT project_id FROM permits 
    WHERE permit_number ILIKE '%RES-ADD-25-000990%'
)
WHERE qb_invoice_id = '4171';
```

**Matching Logic**:
1. Parse permit number from QB line item description
2. Look up permit by permit_number
3. Link invoice to permit's project_id

**Anticipated Issues**:
- ✅ Permit number format variations
  - **Solution**: Regex pattern matching multiple formats
- ✅ Multiple permits mentioned in one invoice
  - **Solution**: Use first permit or split into multiple invoice records
- ✅ No permit number in description
  - **Solution**: Leave project_id null, show as "Unlinked" in UI

---

## 🎯 Implementation Plan

### Step 1: Client-to-QB Linking Script
**File**: `scripts/link_clients_to_qb.py`

```python
# Pseudocode
async def link_clients_to_qb():
    # Get all QB customers
    qb_customers = await get_qb_customers_cache()
    
    # Get all internal clients
    clients = await get_all_clients()
    
    matches = []
    unmatched_clients = []
    unmatched_qb = []
    
    for client in clients:
        # Try exact name match
        qb_match = find_qb_by_name(qb_customers, client.full_name)
        
        if not qb_match:
            # Try email match
            qb_match = find_qb_by_email(qb_customers, client.email)
        
        if qb_match:
            matches.append((client, qb_match))
        else:
            unmatched_clients.append(client)
    
    # Update database with matches
    for client, qb in matches:
        await update_client_qb_id(client.client_id, qb.qb_customer_id)
    
    # Output manual review list
    print(f"✅ Matched: {len(matches)}")
    print(f"⚠️ Unmatched clients: {unmatched_clients}")
    print(f"⚠️ Unmatched QB customers: {unmatched_qb}")
```

**Expected Outcome**: 5 clients linked to 8 QB customers (some QB customers may not have internal clients yet)

---

### Step 2: QB Invoice Sync Script
**File**: `scripts/sync_qb_invoices_to_internal.py`

```python
async def sync_qb_invoices_to_internal():
    qb_invoices = await get_qb_cache_invoices()
    
    for qb_inv in qb_invoices:
        # Get QB customer
        qb_customer = await get_qb_customer(qb_inv.customer_id)
        
        # Find linked internal client
        client = await find_client_by_qb_id(qb_customer.qb_customer_id)
        
        if not client:
            print(f"⚠️ No client for QB customer {qb_customer.display_name}")
            continue
        
        # Extract permit number from line items
        permit_number = extract_permit_from_description(qb_inv.qb_data)
        project_id = None
        
        if permit_number:
            permit = await find_permit_by_number(permit_number)
            if permit:
                project_id = permit.project_id
        
        # Transform line items
        line_items = transform_qb_line_items(qb_inv.qb_data.get('Line', []))
        
        # Upsert internal invoice
        await upsert_invoice(
            qb_invoice_id=qb_inv.qb_invoice_id,
            client_id=client.client_id,
            project_id=project_id,
            invoice_number=qb_inv.doc_number,
            total_amount=qb_inv.total_amount,
            balance_due=qb_inv.balance,
            due_date=qb_inv.due_date,
            line_items=line_items,
            status=map_qb_status(qb_inv.qb_data.get('EmailStatus')),
            sync_status='synced'
        )
```

**Expected Outcome**: 13 invoices created in `invoices` table, linked to clients, some linked to permits

---

### Step 3: Update Frontend to Show Internal Invoices
**File**: `frontend/src/stores/invoicesStore.js`

```javascript
// Change from QB cache endpoint to internal invoices endpoint
fetchInvoices: async () => {
  const response = await api.request('/invoices'); // Internal database
  
  // Backend will JOIN with:
  // - clients (for customer info)
  // - permits (for permit/project info)
  // - quickbooks_invoices_cache (for QB sync status)
  
  return response.invoices;
}
```

**Backend Endpoint Enhancement**:
```python
# app/routes/invoices.py
@router.get("/")
async def get_invoices():
    # JOIN invoices with clients, permits, QB cache
    query = """
        SELECT 
            i.*,
            c.full_name as customer_name,
            c.email as customer_email,
            p.permit_number,
            p.address,
            qbc.qb_last_modified as qb_last_sync
        FROM invoices i
        LEFT JOIN clients c ON i.client_id = c.client_id
        LEFT JOIN permits p ON i.project_id = p.project_id
        LEFT JOIN quickbooks_invoices_cache qbc ON i.qb_invoice_id = qbc.qb_invoice_id
        ORDER BY i.due_date DESC
    """
```

---

## ⚠️ Anticipated Issues & Solutions

### Issue 1: Duplicate Invoice Creation
**Problem**: Running sync script multiple times creates duplicates

**Solution**: Use `ON CONFLICT (qb_invoice_id) DO UPDATE` (already in place)

---

### Issue 2: QB Invoice Without Internal Client
**Problem**: QB customer not linked to any internal client

**Solutions**:
1. **Auto-create client**: If QB customer has no match, create new internal client
2. **Skip**: Don't sync invoice until client is linked
3. **Show unlinked**: Display invoice but mark as "Needs Client Assignment"

**Recommended**: Option 3 (show but flag for manual review)

---

### Issue 3: Permit Number Extraction Failure
**Problem**: Can't parse permit number from QB line item description

**Regex Patterns to Try**:
```python
patterns = [
    r'permit number ([A-Z]{2,4}-[A-Z]{3,4}-\d{2}-\d{6})',  # RES-ADD-25-000990
    r'permit\s+#?\s*([A-Z0-9-]+)',  # permit #BP-25-35
    r'PRRN(\d+)',  # PRRN202502429
]
```

**Fallback**: Show invoice but leave `project_id` null, allow manual linking in UI

---

### Issue 4: Status Enum Mapping
**QB Statuses**: EmailSent, NeedToPrint, Paid, Pending  
**Our Statuses**: draft, sent, viewed, paid, overdue, canceled

**Mapping**:
```python
QB_STATUS_MAP = {
    'EmailSent': 'sent',
    'Sent': 'sent',
    'NeedToPrint': 'draft',
    'Paid': 'paid',
    'Pending': 'draft',
}
```

---

### Issue 5: Line Items Format Transformation
**QB Format**:
```json
{
  "Line": [{
    "DetailType": "SalesItemLineDetail",
    "Description": "GC Compliance for permit...",
    "Amount": 3000.0,
    "SalesItemLineDetail": {
      "Qty": 1,
      "UnitPrice": 3000,
      "ItemRef": {"name": "GC Permit Oversight"}
    }
  }]
}
```

**Our Format**:
```json
[{
  "description": "GC Compliance for permit...",
  "quantity": 1,
  "unit_price": 3000.00,
  "amount": 3000.00,
  "item_name": "GC Permit Oversight"
}]
```

**Transformation Function**:
```python
def transform_qb_line_items(qb_lines):
    items = []
    for line in qb_lines:
        if line.get('DetailType') == 'SalesItemLineDetail':
            detail = line.get('SalesItemLineDetail', {})
            items.append({
                'description': line.get('Description', ''),
                'quantity': detail.get('Qty', 1),
                'unit_price': float(detail.get('UnitPrice', 0)),
                'amount': float(line.get('Amount', 0)),
                'item_name': detail.get('ItemRef', {}).get('name', '')
            })
    return items
```

---

## 🚀 Execution Order

1. ✅ **Run Client Linking Script** → Links 5 clients to QB customers
2. ✅ **Run Invoice Sync Script** → Creates 13 internal invoices
3. ✅ **Update Frontend Store** → Change from QB cache to internal invoices endpoint
4. ✅ **Test Navigation** → Click invoice, verify permit/client links show
5. ✅ **Deploy** → Push changes to production

**Estimated Time**: 2-3 hours total

---

## 📈 Success Criteria

- ✅ All 5 internal clients have `qb_customer_id` populated
- ✅ All 13 QB invoices exist in `invoices` table
- ✅ Invoices linked to clients (100% success expected)
- ✅ Invoices linked to permits where possible (80%+ success expected)
- ✅ Frontend shows unified invoice list with customer names and permit numbers
- ✅ Invoice details page shows client info, permit links, and line items
- ✅ No duplicate invoices created on re-sync

---

## 🔄 Ongoing Sync Strategy

**After Initial Import**:
1. QuickBooks sync runs 3x daily (already implemented)
2. Updates QB cache tables
3. Trigger script to sync new/updated invoices to internal database
4. Frontend always shows internal database (single source of truth)

**Future Enhancement**: Real-time webhook from QB → instant internal DB update

---

## 📝 Files to Create/Modify

**New Files**:
- `scripts/link_clients_to_qb.py` (Step 1)
- `scripts/sync_qb_invoices_to_internal.py` (Step 2)

**Modified Files**:
- `frontend/src/stores/invoicesStore.js` (Step 3)
- `app/routes/invoices.py` (add JOIN query for enriched data)

**No Changes Needed**:
- QB sync service (already working)
- Invoice cache endpoints (keep for reference)
- InvoiceDetails component (already handles our data structure)

---

## 🎓 Lessons from Recent Work

**What Worked Well**:
1. ✅ Using `qb_data` JSONB column to store full QB response
2. ✅ Parsing JSONB on-the-fly to extract needed fields
3. ✅ Cache tables with indexed `qb_invoice_id` for fast lookups
4. ✅ Frontend fallback patterns (`field1 || field2 || field3`)

**What to Apply**:
1. ✅ Use UPSERT pattern (`ON CONFLICT DO UPDATE`) to prevent duplicates
2. ✅ Transform QB data structures server-side before sending to frontend
3. ✅ Add `.isoformat()` to all datetime fields for JSON serialization
4. ✅ Include `source` field in responses for debugging

**Mistakes to Avoid**:
1. ❌ Assuming field names match between systems (they don't)
2. ❌ Not handling NULL values in JSONB extraction
3. ❌ Forgetting to convert Decimal to float for JSON
4. ❌ Direct frontend-to-QB-cache coupling (should go through internal DB)

---

## 🎯 Next Steps

**Ready to execute?** Let me know and I'll:
1. Create the client linking script
2. Create the invoice sync script
3. Update the frontend to use internal invoices
4. Test the complete flow

**Questions to confirm**:
- Should we auto-create clients for unmatched QB customers?
- What to do with invoices that can't be linked to permits?
- Want a dry-run mode first to see what would be changed?
