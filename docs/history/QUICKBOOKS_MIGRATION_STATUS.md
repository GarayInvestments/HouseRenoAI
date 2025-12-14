# QuickBooks Service Migration Status

**Date**: December 11, 2025  
**Current State**: Partially migrated - OAuth flow updated, API methods need completion

---

## What's Been Done ✅

### 1. Database & Service
- `quickbooks_tokens` table updated with `is_active` column
- `quickbooks_service_v2.py` created with database-backed token storage
- OAuth flow fully implemented (auth, callback, token refresh, revocation)

### 2. Routes - OAuth Endpoints Updated
- `/auth` - ✅ Updated to use v2 service + database
- `/callback` - ✅ Updated to use v2 service + database

---

## What's Left To Do ⏳

### 3. QuickBooks Service V2 - Missing API Methods

The v2 service currently only has these API methods:
- `get_customers()`
- `get_invoices(customer_id)`
- `get_estimates(customer_id)`
- `create_invoice(invoice_data)`

**Missing methods** (need to be added to `quickbooks_service_v2.py`):
```python
# Company Info
async def get_company_info() -> CompanyInfo

# Customers
async def create_customer(customer_data: Dict) -> Customer
async def get_customer_by_id(customer_id: str) -> Customer

# Invoices
async def get_invoice_by_id(invoice_id: str) -> Invoice

# Estimates
async def create_estimate(estimate_data: Dict) -> Estimate

# Vendors & Bills
async def get_vendors() -> List[Vendor]
async def create_bill(bill_data: Dict) -> Bill

# Items
async def get_items() -> List[Item]

# Customer Types
async def get_customer_types() -> List[CustomerType]
async def sync_customer_types(types_data: List[Dict]) -> Dict
```

### 4. Routes Still Using Legacy Service

These routes need `db: AsyncSession = Depends(get_db)` added and converted to v2:

**Status Endpoints**:
- `/disconnect` - Needs `await qb_service.revoke_tokens()`
- `/status` - Needs v2 status method
- `/refresh` - Already has v2 equivalent

**Company**:
- `/company` - Needs `get_company_info()` in v2

**Customers**:
- `/customers` (GET) - ✅ V2 has this
- `/customers` (POST) - Needs `create_customer()` in v2
- `/customers/{customer_id}` - Needs `get_customer_by_id()` in v2

**Invoices**:
- `/invoices` (GET) - ✅ V2 has this
- `/invoices` (POST) - ✅ V2 has this (but needs full implementation)
- `/invoices/{invoice_id}` - Needs `get_invoice_by_id()` in v2

**Estimates**:
- `/estimates` (POST) - Needs `create_estimate()` in v2

**Vendors & Bills**:
- `/vendors` - Needs `get_vendors()` in v2
- `/bills` - Needs `create_bill()` in v2

**Items**:
- `/items` - Needs `get_items()` in v2

**Customer Types**:
- `/customer-types` - Needs `get_customer_types()` in v2
- `/sync-types` - Needs `sync_customer_types()` in v2

---

## Migration Strategy

### Option 1: Complete V2 Service (Recommended)
1. Add all missing methods to `quickbooks_service_v2.py`
2. Update all 18 routes in `quickbooks.py`
3. Test each endpoint
4. Deploy

**Timeline**: 4-6 hours of development

### Option 2: Hybrid Approach (Faster)
1. Keep legacy service for API operations
2. Use v2 service ONLY for token management (OAuth, refresh, storage)
3. Legacy service reads tokens from database instead of Sheets

**Implementation**:
```python
# In quickbooks_service.py (legacy)
async def _load_tokens_from_db(self):
    """Load tokens from database (replaces _load_tokens_from_sheets)"""
    # Use same logic as quickbooks_service_v2.load_tokens_from_db()
    pass

async def _save_tokens_to_db(self, ...):
    """Save tokens to database (replaces _save_tokens_to_sheets)"""
    # Use same logic as quickbooks_service_v2.save_tokens_to_db()
    pass
```

**Pros**:
- Minimal code changes
- All existing routes work immediately
- OAuth flow uses database storage

**Cons**:
- Still maintaining two services
- Less clean architecture

**Timeline**: 1-2 hours of development

### Option 3: Gradual Migration (Safest)
1. Use v2 for OAuth (already done)
2. Migrate one route category at a time (customers → invoices → estimates...)
3. Test after each category
4. Keep legacy service running until all routes migrated

**Timeline**: 2-3 hours per category

---

## Recommendation

**For immediate deployment**: Use Option 2 (Hybrid)
- OAuth and token storage use database ✅
- All API endpoints still work
- No breaking changes
- Can fully migrate to v2 later

**For long-term**: Use Option 1 (Complete V2)
- Clean architecture
- Single source of truth
- Easier maintenance

---

## Current State Summary

**Working**:
- ✅ OAuth flow (`/auth`, `/callback`) uses database
- ✅ Token refresh uses database
- ✅ Database schema ready
- ✅ Migration script created

**Not Working**:
- ❌ API endpoints (`/customers`, `/invoices`, etc.) still use legacy service
- ❌ Legacy service still reads from Google Sheets
- ❌ Google Sheets dependency not removed

**Next Immediate Steps**:
1. Choose migration strategy (recommend Hybrid for speed)
2. Implement token database loading in legacy service if using Hybrid
3. Test OAuth flow end-to-end
4. Deploy

---

## Testing Checklist

Once migration is complete:

- [ ] OAuth connection flow works
- [ ] Tokens stored in database (not Sheets)
- [ ] Token refresh updates database
- [ ] All customer endpoints work
- [ ] All invoice endpoints work
- [ ] All estimate endpoints work
- [ ] Vendor and bill endpoints work
- [ ] Item endpoints work
- [ ] Customer type endpoints work
- [ ] Multi-environment support (sandbox/production)
- [ ] Google Sheets no longer required for QB

---

## Files Status

**Created/Updated**:
- `app/services/quickbooks_service_v2.py` - ✅ OAuth + basic API methods
- `alembic/versions/qb_token_is_active.py` - ✅ Migration applied
- `app/routes/quickbooks.py` - ⚠️ Partially updated (2/18 routes)
- `scripts/migrate_qb_tokens_to_db.py` - ✅ Ready to use

**Legacy (Still in use)**:
- `app/services/quickbooks_service.py` - Still used by 16/18 routes
- Google Sheets QB_Tokens - Still being accessed by legacy service

