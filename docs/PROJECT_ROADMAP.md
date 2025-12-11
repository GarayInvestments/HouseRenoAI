# House Renovators AI Portal - Implementation Roadmap v3.0

**Version**: 3.0 (Implementation Blueprint)  
**Date**: December 10, 2025  
**Status**: Active Development  
**Architecture**: Buildertrend-Influenced PostgreSQL Backend

---

## 1. High-Level Status

Platform moved off Google Sheets toward a **PostgreSQL-backed app running on Fly.io**. Core infrastructure, clients/projects migration, CI/CD, and baseline metrics are in place.

**Current State**:
- ✅ Backend: Fly.io (https://houserenovators-api.fly.dev)
- ✅ Frontend: Cloudflare Pages with custom domain
- ✅ Database: Supabase PostgreSQL with UUID primary keys
- ✅ Data: 8 clients + 12 projects migrated
- ✅ CI/CD: GitHub Actions auto-deploy for both frontend/backend
- ✅ HTTPS: Working correctly with proxy middleware

**Strategic Shift**: Buildertrend-inspired architecture with **projects as top-level resources**, **permits as first-class children**, and **inspections as schedulable objects**. Core pillars: AI prechecks, QuickBooks billing, zero-downtime migration.

---

## 2. Key Design & Architecture Decisions

### 2.1 Project-Centric Model
- **Projects are the top-level resource** for UX and billing
- Permits are structured children of projects (not flat rows)
- Hierarchical navigation: Client → Projects → Permits → Inspections

### 2.2 Inspections as First-Class Objects
- Inspections are **schedulable entities** linked to permits and projects
- Scheduling parity: schedule items map bidirectionally to inspections
- Inspector PWA flows: accept/decline, complete, no-access handling

### 2.3 PostgreSQL + JSONB as Canonical Data Store
- **Supabase PostgreSQL** is the source of truth
- GIN indexes on JSONB fields for flexible schema evolution
- Google Sheets is **transitional only** and will be fully removed

### 2.4 Business-Facing IDs
Human-readable IDs for all core entities:
- Clients: `CL-00001`, `CL-00002`
- Projects: `PRJ-00001`, `PRJ-00002`
- Permits: `PER-00001`, `PER-00002`
- Inspections: `INS-00001`, `INS-00002`
- Invoices: `INV-00001`, `INV-00002`
- Payments: `PAY-00001`, `PAY-00002`

**Implementation**: PostgreSQL sequences + triggers for atomic generation. Immutable once assigned. Exposed via API and used in UI.

### 2.5 Supabase Auth for Authentication
- **Supabase Auth** handles user authentication and session management
- Frontend uses `@supabase/supabase-js` for login/signup
- Backend verifies JWT via Supabase JWKS or Admin API
- Backend maps `supabase_user_id` (sub claim) to internal `users` table for roles and app metadata

**Migration Path**: Export users from Sheets → Create Supabase users via Admin API or invite links → Map to internal users table.

### 2.6 QuickBooks Integration: DB-Cached Model
- **Encrypted tokens** stored in database (use KMS or application-level encryption)
- **Cached QuickBooks objects** in PostgreSQL (customers, invoices, payments)
- Background sync every 5 minutes (only fetch changed records)
- Invoice/payment helpers for creating and syncing
- Webhook processing for real-time updates
- Circuit breaker pattern for API resilience

**Performance Target**: 90% reduction in QuickBooks API calls.

---

## 3. Data Model (Essential Tables)

> Full SQL schemas with all fields, constraints, and indexes in **Phase A.1 Implementation** section below.

### Core Tables

**clients**
- `id` (UUID PK), `business_id` (CL-00001), `name`, `email`, `phone`, `qb_customer_id`

**projects**
- `id` (UUID PK), `business_id` (PRJ-00001), `client_id` FK, `address`, `status`, `budget`, `qb_customer_id`, `estimated_start_date`, `estimated_completion_date`, `extra` JSONB

**permits**
- `id` (UUID PK), `business_id` (PER-00001), `project_id` FK, `permit_type`, `status`, `jurisdiction`, `permit_number`, applied/approved/expiration dates, `fee_amount`, `fee_paid`, `qb_invoice_id`, `notes`, `extra` JSONB

**inspections**
- `id` (UUID PK), `business_id` (INS-00001), `permit_id` FK, `project_id` FK (denormalized for query performance), `inspection_type`, `status`, `scheduled_date`, `completed_date`, `inspector`, `result`, `notes`, `photos` JSONB, `deficiencies` JSONB

**permit_status_events**
- Audit timeline for every permit status change
- `id`, `permit_id` FK, `old_status`, `new_status`, `changed_by`, `changed_at`, `notes`, `ai_confidence`, `extra` JSONB

**jurisdictions**
- `id`, `name`, `state`, `requirements` JSONB (rules for prechecks)

**optional_inspections**
- Fee catalog: Special Housing (SH), Trade-Ups (TU), IBA, etc.
- `id`, `code`, `name`, `fee_amount`, `description`

**site_visits**
- `id` (UUID PK), `business_id` (SV-00001), `project_id` FK, `visit_type` (Pre-Construction, Progress, Final Walkthrough, Punch List, Client Meeting), `status` (Scheduled, In-Progress, Completed, Cancelled), `scheduled_date`, `start_time`, `end_time`, `attendees` JSONB (array of {name, role, email}), `gps_location` (lat/lon), `photos` JSONB (array of {url, gps, timestamp, uploaded_by}), `notes` TEXT, `deficiencies` JSONB (array of {description, severity, photo_refs}), `follow_up_actions` JSONB (array of {type, status, created_entity_id}), `created_by`, `extra` JSONB

**schedule_items**
- `id`, `project_id` FK, `inspection_id` FK (nullable), `title`, `scheduled_date`, `assigned_to`, `status`, `notes`

### Financial Tables

**invoices**
- `id` (UUID PK), `business_id` (INV-00001), `project_id` FK, `qb_invoice_id`, `invoice_number`, `invoice_date`, `due_date`, `total_amount`, `balance`, `status`, `line_items` JSONB, `sync_status` ENUM, `sync_error`, `last_sync_attempt`

**payments**
- `id` (UUID PK), `business_id` (PAY-00001), `invoice_id` FK, `qb_payment_id`, `payment_date`, `amount`, `payment_method`, `reference_number`, `sync_status` ENUM, `sync_error`, `last_sync_attempt`

### QuickBooks Cache Tables

**qb_customers_cache**
- Cached QuickBooks customer records
- `id`, `qb_customer_id`, `display_name`, `balance`, `metadata` JSONB, `cached_at`

**qb_invoices_cache**
- Cached QuickBooks invoice records
- `id`, `qb_invoice_id`, `customer_id`, `total_amount`, `balance`, `due_date`, `status`, `metadata` JSONB, `cached_at`

**qb_payments_cache**
- Cached QuickBooks payment records

**quickbooks_tokens**
- Encrypted OAuth tokens
- `id`, `realm_id`, `access_token_encrypted`, `refresh_token_encrypted`, `expires_at`, `created_at`, `updated_at`

**webhook_events**
- QuickBooks webhook event log
- `id`, `qb_event_id` (unique), `event_type`, `entity_id`, `payload` JSONB, `processed_at`, `error`

### System Tables

**users**
- `id` (UUID PK), `supabase_user_id` (unique), `email`, `name`, `role` ENUM('admin', 'pm', 'inspector', 'client', 'finance'), `created_at`

**business_id_aliases**
- Handle business ID merges and retirements
- `id`, `alias_id`, `canonical_id`, `entity_type`, `retired_at`

**job_runs**
- Background job monitoring
- `id`, `job_name`, `status` ENUM('running', 'success', 'failed'), `started_at`, `completed_at`, `error`, `metadata` JSONB

---

## 4. API Surface (Resource-Based Routes)

**Move away from root-driven routes**. Use resource-based routing under `/projects`, `/clients`, `/permits`, `/invoices`, `/payments`, `/quickbooks`.

### 4.1 Projects & Clients

```
GET    /v1/clients
GET    /v1/clients/{id}
GET    /v1/clients/by-business-id/{business_id}
POST   /v1/clients

GET    /v1/projects
GET    /v1/projects/{id}
GET    /v1/projects/by-business-id/{business_id}
POST   /v1/projects
PUT    /v1/projects/{id}
```

### 4.2 Permits

```
POST   /v1/projects/{project_id}/permits         # Create permit for project
GET    /v1/permits                                # List all permits
GET    /v1/permits/{permit_id}
GET    /v1/permits/by-business-id/{business_id}
PUT    /v1/permits/{permit_id}
PUT    /v1/permits/{permit_id}/submit            # Submit for approval
GET    /v1/permits/{permit_id}/precheck?type={inspection_type}  # Check before scheduling
```

### 4.3 Inspections

```
POST   /v1/permits/{permit_id}/inspections       # Create inspection (runs AI precheck)
                                                   # Returns: { ok: bool, missing: [], ai_confidence: 0.85 }
GET    /v1/inspections/{inspection_id}
PUT    /v1/inspections/{inspection_id}/complete  # Record result/notes/photos
POST   /v1/inspections/{inspection_id}/photos    # Upload photos with GPS/timestamp
GET    /v1/projects/{project_id}/inspections     # All inspections for project
```

### 4.4 Site Visits

```
POST   /v1/projects/{project_id}/site-visits     # Schedule site visit
GET    /v1/projects/{project_id}/site-visits     # List project site visits
GET    /v1/site-visits/{id}                      # Site visit details
GET    /v1/site-visits/by-business-id/{business_id}  # Lookup by SV-00001
PUT    /v1/site-visits/{id}/start                # Start visit (check-in with GPS)
PUT    /v1/site-visits/{id}/complete             # Complete visit (check-out, add notes/deficiencies)
POST   /v1/site-visits/{id}/photos               # Upload photos with GPS + timestamp
POST   /v1/site-visits/{id}/follow-ups           # Create follow-up actions (inspection/change_order/punchlist)
DELETE /v1/site-visits/{id}                      # Cancel visit (soft delete)
```

### 4.5 Invoices & Payments

```
POST   /v1/projects/{project_id}/invoices        # Create invoice
GET    /v1/projects/{project_id}/invoices        # List project invoices
GET    /v1/invoices/{invoice_id}
POST   /v1/invoices/{invoice_id}/send            # Create/send and push to QuickBooks
POST   /v1/invoices/{invoice_id}/apply-payment   # Apply payment idempotently

POST   /v1/projects/{project_id}/payments        # Record payment
GET    /v1/payments/{payment_id}
GET    /v1/invoices/{invoice_id}/payments        # Payments for invoice
```

### 4.5 QuickBooks Integration

```
POST   /v1/quickbooks/webhook                    # Webhook receiver
POST   /v1/quickbooks/invoices/sync              # Manual sync invoices
POST   /v1/quickbooks/payments/sync              # Manual sync payments
POST   /v1/quickbooks/cache/clear                # Clear cache (admin)
GET    /v1/quickbooks/status                     # Auth status
GET    /v1/quickbooks/connect                    # OAuth flow
```

### 4.6 Admin & Jobs

```
POST   /v1/admin/jobs/expire_permits             # Test trigger expire job
POST   /v1/admin/jobs/sync_qb                    # Test trigger QB sync
GET    /v1/admin/jobs                            # List recent job runs
GET    /v1/admin/jobs/{job_id}                   # Job run details
```

---

## 5. QuickBooks Invoice/Payment Sync Model

### 5.1 App → QuickBooks (Push)

When an invoice is sent or payment recorded:
1. Call QuickBooks API to create the resource
2. Persist `qb_invoice_id` or `qb_payment_id` in database
3. Set `sync_status = 'synced'`
4. Background retry on transient errors (exponential backoff)

### 5.2 QuickBooks → App (Pull via Webhooks)

1. **Webhook receiver** persists events to `webhook_events` table
2. **Idempotent workers** process events and update local `invoices`/`payments`
3. Use `qb_event_id` for deduplication
4. **Periodic incremental sync** (every 15 minutes) to reconcile missed events

### 5.3 Idempotency

- **Unique indexes**: `qb_invoice_id`, `qb_payment_id`, `qb_event_id`
- **Webhook events**: Store raw payload, track processing status
- **API requests**: Support `Idempotency-Key` header for direct create requests

### 5.4 Reconciliation Job (Daily)

```python
async def reconcile_qb_data():
    """
    Compare app data vs QuickBooks:
    1. Fetch recent invoices/payments from QB
    2. Compare with local records
    3. Flag mismatches (amounts, statuses, missing records)
    4. Auto-correct safe cases (status updates)
    5. Create finance tickets for complex discrepancies
    """
```

### 5.5 Circuit Breaker Configuration

```python
max_failures = 5
timeout_window = 60  # seconds (5 failures in 60s trips breaker)
recovery_timeout = 300  # seconds (wait 5 min before retry)
```

---

## 6. AI & Prechecks

### 6.1 Document Extraction

**Pipeline**: OCR + OpenAI Vision API
- Extract permit fields from uploaded PDFs
- Produce confidence scores for each field
- Store in `permits.extra` and `permit_status_events`

```python
async def extract_permit_data(pdf_file):
    """
    Returns: {
        "permit_number": {"value": "2024-BLD-12345", "confidence": 0.92},
        "issued_date": {"value": "2024-11-15", "confidence": 0.88},
        "expiration_date": {"value": "2025-05-15", "confidence": 0.85}
    }
    """
```

### 6.2 Precheck Service

Validates inspection eligibility before scheduling:

```python
async def inspection_precheck(permit_id: UUID, inspection_type: str) -> PrecheckResult:
    """
    Validates:
    - Permit status is "Approved"
    - Required prior inspections completed and passed
    - Required documents uploaded
    - Permit not expired
    - Fees paid (if required)
    
    Returns: PrecheckResult(
        can_schedule: bool,
        missing: List[str],  # ["Footing inspection must pass first", "Permit fee unpaid"]
        ai_confidence: float,  # 0.0-1.0
        suggestions: List[str]
    )
    """
```

**Jurisdiction Rules**: Loaded from `jurisdictions.requirements` JSONB:

```json
{
  "inspection_sequence": {
    "Footing": [],
    "Foundation": ["Footing"],
    "Framing": ["Foundation"],
    "Final": ["Framing"]
  },
  "required_documents": {
    "Framing": ["structural_plans", "energy_calcs"]
  },
  "expiration_rules": {
    "permit_validity_months": 12,
    "extension_allowed": true
  }
}
```

**AI Confidence Threshold**: If `ai_confidence < 0.70`:
- **UX Decision**: Show warning, allow manual override by admin/PM
- Log override in `permit_status_events` for audit

### 6.3 Photo Analysis (Optional)

AI-powered defect analysis:

```python
async def analyze_inspection_photos(photos: List[bytes]) -> DefectAnalysis:
    """
    Use OpenAI Vision API to:
    - Summarize visible defects
    - Suggest probable causes
    - Generate follow-up recommendations
    
    Stored in: inspections.deficiencies JSONB
    """
```

---

## 7. Supabase Auth & Google Sheets Removal

### 7.1 Supabase Auth Implementation

**Frontend**:
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Login
const { data, error } = await supabase.auth.signInWithPassword({
  email, password
})

// Get session token
const { data: { session } } = await supabase.auth.getSession()
const jwt = session.access_token  // Send to backend
```

**Backend**:
```python
from fastapi import Depends, HTTPException
from supabase import create_client

async def get_current_user(authorization: str = Header(...)):
    """
    Verify JWT via Supabase, map to internal user
    """
    token = authorization.replace("Bearer ", "")
    
    # Verify JWT via Supabase Admin API
    supabase_user = supabase.auth.get_user(token)
    
    # Map to internal user
    user = await db.users.get_by_supabase_id(supabase_user.id)
    
    if not user:
        raise HTTPException(401, "User not found")
    
    return user  # { "id": UUID, "email": str, "role": str }
```

**JWT Refresh Strategy**:
- Supabase tokens expire after 1 hour
- Frontend: Implement silent refresh using `supabase.auth.refreshSession()`
- Backend: Grace period of 5 minutes for expired tokens (allow recent tokens)

### 7.2 User Migration from Google Sheets

**Step 1**: Export users from Sheets
```python
async def export_users_from_sheets():
    users = await google_service.get_sheet_data("Users")
    return [{"email": u["Email"], "name": u["Name"], "role": u["Role"]} for u in users]
```

**Step 2**: Create Supabase users
```python
from supabase import create_client

admin_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

for user in sheet_users:
    # Create Supabase auth user
    supabase_user = admin_supabase.auth.admin.create_user({
        "email": user["email"],
        "password": generate_temp_password(),
        "email_confirm": True
    })
    
    # Create internal user record
    await db.users.create({
        "supabase_user_id": supabase_user.id,
        "email": user["email"],
        "name": user["name"],
        "role": user["role"]
    })
    
    # Send password reset email
    admin_supabase.auth.admin.generate_link({
        "type": "recovery",
        "email": user["email"]
    })
```

### 7.3 Google Sheets Removal

**Phase 1: Migrate All Domain Data**
- ✅ Clients (done)
- ✅ Projects (done)
- ⏳ Permits, Inspections, Invoices, Payments (pending)

**Phase 2: Dry-Run Migration**
- Run migration scripts with `DRY_RUN=true`
- Validate data integrity
- Compare record counts, key fields

**Phase 3: Dual-Write Mode (Safety)**
- Write to both DB and Sheets
- Read from DB primarily, fallback to Sheets if missing
- Monitor for discrepancies

**Phase 4: Full Cutover**
- Set `DB_READ_FALLBACK=false`
- Stop writing to Sheets
- Remove `GoogleService` from codebase
- Archive Sheets documentation

---

## 8. Business IDs Implementation

### 8.1 PostgreSQL Sequences

```sql
CREATE SEQUENCE client_business_id_seq START 1;
CREATE SEQUENCE project_business_id_seq START 1;
CREATE SEQUENCE permit_business_id_seq START 1;
CREATE SEQUENCE inspection_business_id_seq START 1;
CREATE SEQUENCE invoice_business_id_seq START 1;
CREATE SEQUENCE payment_business_id_seq START 1;
```

### 8.2 Trigger Functions

```sql
CREATE OR REPLACE FUNCTION generate_client_business_id()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.business_id IS NULL THEN
    NEW.business_id := 'CL-' || LPAD(nextval('client_business_id_seq')::TEXT, 5, '0');
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER client_business_id_trigger
BEFORE INSERT ON clients
FOR EACH ROW EXECUTE FUNCTION generate_client_business_id();
```

Repeat for projects, permits, inspections, invoices, payments.

### 8.3 Backfill Existing Records

```python
async def backfill_business_ids():
    """
    Populate business_id for existing records.
    MUST be ordered by created_at ASC to preserve chronology.
    Idempotent: Skip records that already have business_id.
    """
    # Clients
    clients = await db.query(
        "SELECT id FROM clients WHERE business_id IS NULL ORDER BY created_at ASC"
    )
    for client in clients:
        await db.execute(
            "UPDATE clients SET business_id = 'CL-' || LPAD(nextval('client_business_id_seq')::TEXT, 5, '0') WHERE id = $1",
            client.id
        )
    
    # Repeat for projects, permits, etc.
```

**Critical**: Use `ORDER BY created_at ASC` so oldest records get lowest IDs (CL-00001 is the first client).

### 8.4 API Exposure

All API responses include `business_id`:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "business_id": "CL-00001",
  "name": "John Smith",
  "email": "john@example.com"
}
```

Frontend displays `business_id` in UI (tables, detail views, breadcrumbs).

---

## 9. Background Jobs & Workers

### 9.1 Job Infrastructure

**Technology**: Celery with Redis broker (or RQ for simpler setup)

```python
# celery_app.py
from celery import Celery

celery = Celery('house_renovators', broker='redis://localhost:6379/0')

celery.conf.task_routes = {
    'jobs.expire_permits': {'queue': 'scheduled'},
    'jobs.sync_qb': {'queue': 'integrations'},
    'jobs.process_webhook': {'queue': 'webhooks'}
}
```

### 9.2 Scheduled Jobs

**Expire Permits Job** (Daily at 2 AM):
```python
@celery.task
async def expire_permits_job():
    """
    Enforce 6/12 month expiration rules:
    - Residential: 6 months
    - Commercial: 12 months
    """
    expired_permits = await db.permits.find_expired()
    
    for permit in expired_permits:
        await db.permits.update_status(permit.id, "Expired")
        await create_status_event(
            permit_id=permit.id,
            old_status=permit.status,
            new_status="Expired",
            changed_by="system",
            notes="Auto-expired per jurisdiction rules"
        )
```

**QuickBooks Sync Job** (Every 5 minutes):
```python
@celery.task
async def sync_qb_job():
    """
    Incremental sync: Only fetch records changed since last sync.
    """
    with redis.lock('qb_sync_lock', timeout=300):  # Prevent concurrent runs
        last_sync = await get_last_sync_time()
        
        # Fetch changed customers
        customers = await qb_service.get_customers(changed_since=last_sync)
        for customer in customers:
            await db.qb_customers_cache.upsert(customer)
        
        # Fetch changed invoices
        invoices = await qb_service.get_invoices(changed_since=last_sync)
        for invoice in invoices:
            await db.qb_invoices_cache.upsert(invoice)
        
        await set_last_sync_time(datetime.now())
```

**Reconciliation Job** (Daily at 3 AM):
```python
@celery.task
async def reconcile_qb_job():
    """
    Compare app data vs QuickBooks, flag discrepancies.
    """
    app_invoices = await db.invoices.get_all(with_qb_id=True)
    qb_invoices = await qb_service.get_invoices(limit=1000)
    
    mismatches = []
    for app_inv in app_invoices:
        qb_inv = find_by_qb_id(qb_invoices, app_inv.qb_invoice_id)
        
        if not qb_inv:
            mismatches.append(f"Invoice {app_inv.business_id} missing in QB")
        elif app_inv.total_amount != qb_inv.total_amount:
            mismatches.append(f"Amount mismatch: {app_inv.business_id}")
    
    if mismatches:
        await notify_finance_team(mismatches)
```

### 9.3 Event-Driven Jobs

**Process QuickBooks Webhook**:
```python
@celery.task
async def process_qb_webhook(event_id: str):
    """
    Idempotent processing of QB webhook events.
    """
    event = await db.webhook_events.get_by_qb_event_id(event_id)
    
    if event.processed_at:
        return  # Already processed
    
    try:
        if event.event_type == "Invoice.Create":
            await sync_invoice_from_qb(event.entity_id)
        elif event.event_type == "Payment.Create":
            await sync_payment_from_qb(event.entity_id)
        
        await db.webhook_events.mark_processed(event.id)
    except Exception as e:
        await db.webhook_events.record_error(event.id, str(e))
        raise
```

### 9.4 Job Monitoring

Track all job runs in `job_runs` table:

```python
async def run_tracked_job(job_name: str, job_func):
    """
    Wrapper to track job execution.
    """
    job_run = await db.job_runs.create({
        "job_name": job_name,
        "status": "running",
        "started_at": datetime.now()
    })
    
    try:
        result = await job_func()
        await db.job_runs.update(job_run.id, {
            "status": "success",
            "completed_at": datetime.now(),
            "metadata": result
        })
    except Exception as e:
        await db.job_runs.update(job_run.id, {
            "status": "failed",
            "completed_at": datetime.now(),
            "error": str(e)
        })
        raise
```

**Alerting**: If a job fails 3 times in a row, send alert to ops team.

---

## 10. Tests, Acceptance & Rollout

### 10.1 Acceptance Criteria

**Database & Migrations**:
- [ ] Alembic migrations create `permits`, `inspections`, `permit_status_events`, `jurisdictions`, `optional_inspections` tables
- [ ] All tables have proper indexes (B-tree for lookups, GIN for JSONB)
- [ ] Business ID sequences and triggers work correctly
- [ ] Backfill script populates business IDs in chronological order

**Permits & Inspections**:
- [ ] `POST /v1/permits/{id}/inspections` runs AI precheck
- [ ] Precheck blocks scheduling if missing required items
- [ ] Precheck allows scheduling when all criteria met
- [ ] `GET /v1/permits/{id}/precheck` returns eligibility status
- [ ] Inspection completion updates permit status if needed

**QuickBooks Integration**:
- [ ] Invoice creation pushes to QuickBooks and stores `qb_invoice_id`
- [ ] Payment recording pushes to QuickBooks and stores `qb_payment_id`
- [ ] Webhook receiver processes events idempotently
- [ ] Reconciliation job detects and flags mismatches
- [ ] Circuit breaker trips after 5 failures in 60 seconds

**Background Jobs**:
- [ ] `expire_permits_job` enforces 6/12 month rules
- [ ] `sync_qb_job` runs every 5 minutes and updates cache
- [ ] `reconcile_qb_job` runs daily and reports discrepancies
- [ ] Job runs are tracked in `job_runs` table

**Authentication**:
- [ ] Supabase Auth works end-to-end (login, JWT verification)
- [ ] `get_current_user` dependency returns user with role
- [ ] Protected routes require valid JWT
- [ ] Users table correctly maps `supabase_user_id` to internal user

**Google Sheets Removal**:
- [ ] No runtime reliance on Google Sheets (`DB_READ_FALLBACK=false`)
- [ ] All domain data (clients, projects, permits, inspections, invoices, payments) in PostgreSQL
- [ ] Migration scripts have dry-run mode and validation
- [ ] Data integrity verified (record counts, key fields match)

### 10.2 Testing Strategy

**Unit Tests** (~100 tests):
- Models: Field validation, business logic methods
- Services: CRUD operations, QB sync logic, precheck validation
- Utils: Business ID generation, JWT verification

**Contract Tests** (~30 tests):
- API response shapes (ensure frontend compatibility)
- AI context structure (validate prompt templates)
- QuickBooks webhook payload handling

**Integration Tests** (~40 tests):
- QB sync idempotency (duplicate webhook processing)
- Invoice/payment creation and QB push
- Precheck logic with jurisdiction rules
- Background job execution and monitoring

**Migration Tests** (~20 tests):
- Dry-run mode produces accurate reports
- Backfill scripts are idempotent
- Data validation detects missing/corrupt records

**E2E Tests** (~15 tests):
- Full permit workflow: Create → Submit → Approve → Schedule Inspection → Complete
- Invoice workflow: Create → Send → QuickBooks sync → Apply Payment
- Inspector workflow: Accept inspection → Complete → Upload photos

**Test Coverage Target**: >85% code coverage

### 10.3 Rollout Strategy

**Phase 1: Dual-Write Mode** (1-2 weeks)
- Write to both PostgreSQL and Google Sheets
- Read from PostgreSQL, fallback to Sheets if missing
- Monitor for discrepancies (alerting via Slack)
- Fix any data sync issues

**Phase 2: Canary (10% Traffic)** (Week 3)
- 10% of API requests read from PostgreSQL only
- Monitor error rates, query performance, data integrity
- Roll back if error rate > 0.5%

**Phase 3: Full Cutover (100% Traffic)** (Week 4)
- All API requests use PostgreSQL
- Google Sheets becomes read-only backup
- Remove dual-write code

**Phase 4: Decommission Sheets** (Week 5+)
- Stop writing to Sheets entirely
- Remove `GoogleService` from codebase
- Archive Sheets-related documentation
- Export Sheets data for historical backup

**Success Metrics**:
- Zero data loss during migration
- API response times < 500ms (p95)
- Error rate < 0.1%
- 90% reduction in external API calls (QB)

**Rollback Plan**:
- **Immediate rollback** (< 5 minutes): Set `DB_READ_FALLBACK=true`, restart backend
- **Data reconciliation** (1-2 hours): Run `compare_sheets_db.py` script, identify gaps
- **Post-mortem required** for any rollback

---

## 11. Scheduling Parity & Inspector Workflow

### 11.1 Schedule Items ↔ Inspections Mapping

**Database Schema**:
```sql
ALTER TABLE schedule_items ADD COLUMN inspection_id UUID REFERENCES inspections(id);
CREATE INDEX idx_schedule_items_inspection_id ON schedule_items(inspection_id);
```

**Bidirectional Sync**:
- When inspection is scheduled, create or update `schedule_items`
- When schedule item date changes, update `inspections.scheduled_date`
- Sync is immediate (not background job)

**API**:
```python
@router.post("/v1/permits/{permit_id}/inspections")
async def create_inspection(permit_id: UUID, inspection_data: InspectionCreate):
    # 1. Run precheck
    precheck = await inspection_precheck(permit_id, inspection_data.inspection_type)
    if not precheck.can_schedule:
        raise HTTPException(400, {"message": "Cannot schedule", "missing": precheck.missing})
    
    # 2. Create inspection
    inspection = await db.inspections.create({
        "permit_id": permit_id,
        "inspection_type": inspection_data.inspection_type,
        "scheduled_date": inspection_data.scheduled_date,
        "status": "Scheduled"
    })
    
    # 3. Create schedule item
    schedule_item = await db.schedule_items.create({
        "project_id": inspection.project_id,
        "inspection_id": inspection.id,
        "title": f"{inspection_data.inspection_type} Inspection",
        "scheduled_date": inspection_data.scheduled_date,
        "assigned_to": inspection_data.inspector
    })
    
    return {"inspection": inspection, "schedule_item": schedule_item}
```

### 11.2 Inspector PWA Workflow

**Accept/Decline Assignment**:
```python
@router.put("/v1/inspections/{inspection_id}/accept")
async def accept_inspection(inspection_id: UUID, current_user: User = Depends(get_current_user)):
    if current_user.role != "inspector":
        raise HTTPException(403, "Only inspectors can accept")
    
    await db.inspections.update(inspection_id, {
        "status": "Accepted",
        "inspector": current_user.id
    })
    
    # Notify PM
    await notify_pm(inspection_id, "Inspection accepted")
```

**Complete Inspection**:
```python
@router.put("/v1/inspections/{inspection_id}/complete")
async def complete_inspection(
    inspection_id: UUID,
    result: InspectionResult,  # Pass, Fail, Partial, No-Access
    notes: str,
    deficiencies: List[Deficiency],
    current_user: User = Depends(get_current_user)
):
    inspection = await db.inspections.update(inspection_id, {
        "status": "Completed",
        "completed_date": datetime.now(),
        "result": result,
        "notes": notes,
        "deficiencies": deficiencies
    })
    
    # If failed, create punchlist items
    if result == "Fail":
        for deficiency in deficiencies:
            await create_punchlist_item(inspection.project_id, deficiency)
    
    # If no-access, create follow-up inspection (+2 days)
    if result == "No-Access":
        await db.inspections.create({
            "permit_id": inspection.permit_id,
            "inspection_type": inspection.inspection_type,
            "scheduled_date": inspection.scheduled_date + timedelta(days=2),
            "status": "Scheduled",
            "notes": f"Follow-up from no-access: {notes}"
        })
    
    return inspection
```

**Photo Upload**:
```python
@router.post("/v1/inspections/{inspection_id}/photos")
async def upload_photos(
    inspection_id: UUID,
    photos: List[UploadFile],
    gps_coords: str,  # "lat,lon"
    current_user: User = Depends(get_current_user)
):
    photo_data = []
    
    for photo in photos:
        # Upload to S3 or similar
        url = await storage.upload(photo, f"inspections/{inspection_id}")
        
        photo_data.append({
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "gps": gps_coords,
            "uploaded_by": current_user.id
        })
    
    # Append to photos JSONB array
    await db.inspections.append_photos(inspection_id, photo_data)
    
    return {"uploaded": len(photo_data)}
```

### 11.3 Reconciliation Job (Nightly)

**Detect Orphaned Records**:
```python
@celery.task
async def reconcile_schedules_and_inspections():
    """
    Find mismatches:
    - Schedule items with no inspection_id
    - Inspections with no linked schedule_items
    """
    orphaned_schedules = await db.query("""
        SELECT * FROM schedule_items 
        WHERE inspection_id IS NULL 
        AND title ILIKE '%inspection%'
    """)
    
    orphaned_inspections = await db.query("""
        SELECT i.* FROM inspections i
        LEFT JOIN schedule_items s ON s.inspection_id = i.id
        WHERE s.id IS NULL
    """)
    
    # Auto-fix simple cases
    for schedule in orphaned_schedules:
        # Try to find matching inspection by date + project
        inspection = await find_matching_inspection(schedule)
        if inspection:
            await db.schedule_items.update(schedule.id, {"inspection_id": inspection.id})
    
    # Flag complex cases for manual review
    if orphaned_inspections:
        await notify_ops_team(f"Found {len(orphaned_inspections)} orphaned inspections")
```

---

## 12. Implementation Phases & Timeline

### Phase A: Core Data & Migration (1-2 weeks, 🔥🔥🔥)

**A.1: Database Models & Migrations** (4-5 hours)
- [ ] Create Alembic migration for `permits`, `inspections`, `permit_status_events`, `jurisdictions`, `optional_inspections`
- [ ] Add indexes (B-tree on FKs, GIN on JSONB)
- [ ] Create `invoices`, `payments`, `qb_*_cache` tables
- [ ] Add `sync_status`, `sync_error`, `last_sync_attempt` fields

**A.2: Business ID System** (3-4 hours)
- [ ] Create sequences for all entities
- [ ] Write trigger functions
- [ ] Apply triggers to tables
- [ ] Write backfill script (idempotent, chronological)
- [ ] Test backfill on staging

**A.3: Database Service Layer** (5-6 hours)
- [ ] Implement `PermitService`: CRUD, precheck, status updates
- [ ] Implement `InspectionService`: CRUD, complete, upload photos
- [ ] Implement `InvoiceService`: CRUD, QB sync
- [ ] Implement `PaymentService`: CRUD, QB sync
- [ ] Background job runners: expire permits, sync QB

**A.4: Migration Scripts** (3-4 hours)
- [ ] Extend migration for permits/inspections
- [ ] Add dry-run mode
- [ ] Jurisdiction validation and auto-create
- [ ] Migration report generation

### Phase B: API & Business Flows (1-2 weeks, 🔥🔥🔥)

**B.1: Permit API Endpoints** (3-4 hours)
- [ ] `POST /v1/projects/{id}/permits`
- [ ] `GET /v1/permits`, `GET /v1/permits/{id}`
- [ ] `PUT /v1/permits/{id}/submit`
- [ ] `GET /v1/permits/{id}/precheck`

**B.2: Inspection API Endpoints** (3-4 hours)
- [ ] `POST /v1/permits/{id}/inspections` (with precheck)
- [ ] `PUT /v1/inspections/{id}/complete`
- [ ] `POST /v1/inspections/{id}/photos`
- [ ] `GET /v1/projects/{id}/inspections`

**B.3: AI Precheck & Document Extraction** (4-5 hours)
- [ ] PDF extraction service (OpenAI Vision API)
- [ ] Precheck logic (jurisdiction rules + extraction results)
- [ ] Confidence scoring
- [ ] Store in `permits.extra` and `permit_status_events`

**B.4: QuickBooks Billing Integration** (2-3 hours)
- [ ] `create_permit_fee_invoice()` helper
- [ ] `create_inspection_fee_invoice()` helper (optional fees)
- [ ] Payment status sync back to permits

### Phase C: Scheduling Parity (1 week, 🔥🔥)

**C.1: Schedule ↔ Inspection Mapping** (2-3 hours)
- [ ] Add `inspection_id` FK to `schedule_items`
- [ ] Create schedule on inspection creation
- [ ] Bidirectional date sync

**C.2: Inspector Workflow** (4-5 hours)
- [ ] Accept/decline endpoints
- [ ] Complete with result/notes/photos
- [ ] No-access flow (auto follow-up +2 days)
- [ ] Failure creates punchlist items
- [ ] Photo upload with GPS/timestamp

**C.3: Reconciliation Job** (2-3 hours)
- [ ] Nightly job to detect orphans
- [ ] Auto-fix simple cases
- [ ] Flag complex cases for manual review

**C.4: Site Visits Feature** (8-10 hours, 🔥🔥🔥 NEW)
- [ ] Create `site_visits` SQLAlchemy model with business_id (SV-00001)
- [ ] Alembic migration: table, indexes, business_id sequence/trigger
- [ ] Model fields: `project_id`, `visit_type`, `status`, `scheduled_date`, `start_time`, `end_time`, `attendees` JSONB, `gps_location`, `photos` JSONB, `notes`, `deficiencies` JSONB, `follow_up_actions` JSONB
- [ ] API endpoints:
  - `POST /v1/projects/{project_id}/site-visits` (schedule visit)
  - `GET /v1/projects/{project_id}/site-visits` (list project visits)
  - `GET /v1/site-visits/{id}` (visit details)
  - `PUT /v1/site-visits/{id}/start` (check-in with GPS)
  - `PUT /v1/site-visits/{id}/complete` (check-out, add notes/deficiencies)
  - `POST /v1/site-visits/{id}/photos` (upload with GPS + timestamp)
- [ ] Object storage integration (S3/Cloudflare R2) for photos
- [ ] Follow-up action wiring:
  - `create_inspection` (from deficiency requiring permit work)
  - `create_change_order` (from scope change)
  - `create_punchlist` (from minor deficiency)
- [ ] Role-based auth: PM/inspector can create, client can view
- [ ] Background job hooks:
  - Photo AI analysis (defect detection, similarity to plans)
  - Auto-create follow-ups from visit notes
  - Notify stakeholders on completion
- [ ] Unit tests: model validation, business_id generation
- [ ] Integration tests: schedule→start→complete flow with follow-up creation
- [ ] Idempotency tests: duplicate photo upload, double complete

### Phase D: Performance & Cost Control (1 week, 🔥🔥🔥)

**D.1: DB-Centered QuickBooks Strategy** (4-5 hours)
- [ ] Create `qb_customers_cache`, `qb_invoices_cache`, `qb_payments_cache` tables
- [ ] Background sync job (every 5 min, incremental)
- [ ] Context builder reads from DB cache
- [ ] Measure API call reduction

**D.2: Context Size Optimization** (2-3 hours)
- [ ] Intelligent truncation (last 10 invoices + summary stats)
- [ ] Filter to query-relevant records
- [ ] Measure token reduction

**D.3: Retire Sheets Optimizations** (1-2 hours)
- [ ] Mark Sheets batching as transitional
- [ ] Remove after full DB cutover
- [ ] Keep minimal Sheets service for historical access

### Phase E: Documentation, Testing & Rollout (Ongoing, 🔥🔥🔥)

**E.1: Documentation Updates** (3-4 hours)
- [ ] `POSTGRES_MIGRATION_GUIDE.md`
- [ ] `PERMIT_WORKFLOW.md`
- [ ] `INSPECTOR_GUIDE.md`
- [ ] `SITE_VISIT_GUIDE.md` (NEW: Workflow for scheduling, conducting, and completing site visits)
- [ ] Update `API_DOCUMENTATION.md` (add site visits endpoints)
- [ ] Update `TROUBLESHOOTING.md`

**E.2: Test Coverage** (4-5 hours)
- [ ] Unit tests for new services (permits, inspections, site visits)
- [ ] Integration tests for QB sync
- [ ] E2E tests for permit → inspection → invoice flows
- [ ] E2E tests for site visit → follow-up action flows
- [ ] Contract tests for API shapes
- [ ] Site visit tests: schedule→start→complete with photo upload and follow-up creation
- [ ] Idempotency tests for site visit photo uploads and completion

**E.3: Staging Rollout** (Ongoing monitoring)
- [ ] Phase 1: Dual-write (1-2 weeks)
- [ ] Phase 2: Canary 10% (week 3)
- [ ] Phase 3: Full cutover (week 4)
- [ ] Phase 4: Decommission Sheets (week 5+)

**E.4: Rollback Plan** (Documented)
- [ ] Immediate rollback procedure (< 5 min)
- [ ] Data reconciliation scripts
- [ ] Post-mortem template

---

## Timeline Summary

| Phase | Duration | Effort | Priority | Status |
|-------|----------|--------|----------|--------|
| **A: Core Data & Migration** | 1-2 weeks | 15-20 hours | 🔥🔥🔥 | 🚧 In Progress |
| **B: API & Business Flows** | 1-2 weeks | 12-16 hours | 🔥🔥🔥 | ⏳ Pending |
| **C: Scheduling Parity + Site Visits** | 1.5-2 weeks | 17-22 hours | 🔥🔥🔥 | ⏳ Pending |
| **D: Performance & Costs** | 1 week | 8-11 hours | 🔥🔥🔥 | ⏳ Pending |
| **E: Docs, Tests, Rollout** | Ongoing | 10-15 hours | 🔥🔥🔥 | 🚧 In Progress |

**Total Estimated Effort**: 62-84 hours (7-10 weeks at 10 hrs/week)

---

## Next Immediate Actions

1. **Complete Phase A.1**: Finish permit/inspection/site_visit table migrations with indexes
2. **Complete Phase A.2**: Implement business ID system with sequences and triggers (including SV-00001)
3. **Complete Phase A.3**: Build database service layer for permits/inspections/site visits
4. **Complete Phase A.4**: Test migration scripts in dry-run mode on staging data

**Estimated time to Phase A completion**: 1-2 weeks

---

## Success Metrics

**Phase A**:
- ✅ All tables created with proper indexes
- ✅ Business IDs generated correctly for new records
- ✅ Backfill script populates existing records in order
- ✅ Migration dry-run completes without errors

**Phase B**:
- ✅ Precheck blocks invalid scheduling requests
- ✅ AI confidence scores stored in database
- ✅ Invoice/payment creation pushes to QuickBooks
- ✅ `qb_invoice_id`/`qb_payment_id` persisted correctly

**Phase C**:
- ✅ Schedule items automatically created from inspections
- ✅ Inspector can complete inspections with photos
- ✅ No-access flow creates follow-up inspections
- ✅ Reconciliation job detects orphaned records

**Phase D**:
- ✅ 90% reduction in QuickBooks API calls (via caching)
- ✅ 40-50% token reduction (via truncation)
- ✅ Sub-2s response time for all AI queries
- ✅ Context builder reads from DB cache, not QB API

**Phase E**:
- ✅ Zero data loss during migration
- ✅ Error rate < 0.1% post-cutover
- ✅ Test coverage > 85%
- ✅ Google Sheets fully decommissioned

---

## Support & Questions

For implementation details:
- See `docs/guides/API_DOCUMENTATION.md` for API reference
- See `docs/technical/POSTGRES_MIGRATION_GUIDE.md` for migration procedures
- See `docs/guides/PERMIT_WORKFLOW.md` for business logic
- Check `docs/DEPLOYMENT_TROUBLESHOOTING.md` for infrastructure issues

**Roadmap maintained by**: Development Team  
**Last Review**: December 10, 2025  
**Next Review**: Weekly during Phase A-D implementation

