# House Renovators AI Portal - Project Roadmap

**Last Updated**: December 10, 2025  
**Current Version**: Production v2.0 (PostgreSQL + Fly.io)  
**Status**: ✅ Phases 0-2 Complete, 🚧 Phase A (PostgreSQL Migration) In Progress

---

## 📊 Current State (December 10, 2025)

### ✅ Recently Completed

#### Infrastructure Modernization (Dec 10, 2025)
**Status**: ✅ COMPLETE  
**Duration**: 1 day  
**Commits**: cf795e6, 81251bc, d700d5d, 82e7d45

**Achievements**:
- ✅ **PostgreSQL Backend**: Migrated from Google Sheets to Supabase PostgreSQL with UUID primary keys
  - 8 clients migrated
  - 12 projects migrated  
  - 11 permits migrated
- ✅ **Fly.io Deployment**: Backend deployed with GitHub Actions auto-deploy
  - 2 machines in `ord` region
  - Auto-stop/auto-start enabled (min_machines_running = 0)
  - Port 8000 configuration fixed
- ✅ **HTTPS Redirect Fix**: Added `HTTPSRedirectFixMiddleware` to preserve HTTPS behind proxy
- ✅ **Cloudflare Pages**: Frontend auto-deploy on push to main
- ✅ **Complete CI/CD Pipeline**: Both frontend and backend auto-deploy from GitHub

**Impact**: Modern infrastructure, native database support, auto-scaling deployment

---

### 🏆 Production Metrics (As of Dec 10, 2025)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Backend Uptime** | 99.9% | 99%+ | ✅ |
| **PostgreSQL Performance** | <100ms queries | <200ms | ✅ |
| **Fly.io Deployment** | Auto-deploy working | Active | ✅ |
| **QuickBooks Integration** | 24 customers, 53+ invoices | Active | ✅ |
| **Payments Tracking** | Active | Live | ✅ |
| **HTTPS Working** | No mixed content errors | Secure | ✅ |

---

## 🚀 New Strategic Direction: Buildertrend-Influenced Architecture

### Vision
Shift from Sheets-centric workflow to **project-centric + permit-driven** architecture with PostgreSQL backend, mirroring Buildertrend's structured approach to construction management.

### Core Principles
1. **Projects are first-class citizens** with permits as structured children
2. **Inspections as first-class entities** with scheduling parity
3. **AI-powered prechecks** before inspection scheduling
4. **QuickBooks integration** for permit fees and optional inspection billing
5. **Zero-downtime migration** with fallback to Sheets during transition

---

## 📋 Phase A: Core Data & Migration (🔥🔥🔥 TOP PRIORITY)

**Timeline**: 1-2 weeks  
**Status**: 🚧 IN PROGRESS  
**Goal**: Complete database schema and migrate all permit/inspection data

### A.1: Database Models & Migrations
**Priority**: 🔥🔥🔥 CRITICAL  
**Effort**: 4-6 hours  
**Status**: 🚧 IN PROGRESS (clients/projects done)

**Implementation Tasks**:
- [x] Create `clients` and `projects` tables with UUIDs
- [x] Migrate initial client/project data (8 clients, 12 projects)
- [ ] Add `permits` table with full Buildertrend-style fields:
  ```sql
  CREATE TABLE permits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id VARCHAR(50) UNIQUE NOT NULL,  -- PER-00001
    project_id UUID REFERENCES projects(id) NOT NULL,
    permit_type VARCHAR(50) NOT NULL,  -- Building, Electrical, Plumbing, etc.
    status VARCHAR(50) NOT NULL,  -- Draft, Submitted, Under Review, Approved, etc.
    jurisdiction VARCHAR(100),
    permit_number VARCHAR(100),
    applied_date TIMESTAMP,
    approved_date TIMESTAMP,
    expiration_date TIMESTAMP,
    fee_amount DECIMAL(10,2),
    fee_paid BOOLEAN DEFAULT FALSE,
    qb_invoice_id VARCHAR(50),
    notes TEXT,
    extra JSONB,  -- Flexible field for jurisdiction-specific data
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );
  CREATE INDEX idx_permits_project ON permits(project_id);
  CREATE INDEX idx_permits_business_id ON permits(business_id);
  CREATE INDEX idx_permits_status ON permits(status);
  CREATE INDEX idx_permits_extra_gin ON permits USING GIN (extra);
  ```
- [ ] Add `inspections` table:
  ```sql
  CREATE TABLE inspections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id VARCHAR(50) UNIQUE NOT NULL,  -- INS-00001
    permit_id UUID REFERENCES permits(id) NOT NULL,
    inspection_type VARCHAR(100) NOT NULL,  -- Footing, Framing, Final, etc.
    status VARCHAR(50) NOT NULL,  -- Scheduled, Passed, Failed, No Access
    scheduled_date TIMESTAMP,
    completed_date TIMESTAMP,
    inspector_name VARCHAR(200),
    result VARCHAR(50),  -- Pass, Fail, Partial
    notes TEXT,
    photos JSONB,  -- Array of photo URLs/metadata
    deficiencies JSONB,  -- Array of issues found
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );
  CREATE INDEX idx_inspections_permit ON inspections(permit_id);
  CREATE INDEX idx_inspections_business_id ON inspections(business_id);
  CREATE INDEX idx_inspections_scheduled_date ON inspections(scheduled_date);
  CREATE INDEX idx_inspections_photos_gin ON inspections USING GIN (photos);
  ```
- [ ] Add `permit_status_events` table for audit trail:
  ```sql
  CREATE TABLE permit_status_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    permit_id UUID REFERENCES permits(id) NOT NULL,
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    changed_by VARCHAR(200),
    reason TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
  );
  CREATE INDEX idx_permit_events_permit ON permit_status_events(permit_id);
  ```
- [ ] Add `jurisdictions` table for precheck rules:
  ```sql
  CREATE TABLE jurisdictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL UNIQUE,
    state VARCHAR(2) NOT NULL,
    requirements JSONB,  -- Required docs, inspections, etc.
    contact_info JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );
  ```
- [ ] Add `optional_inspections` configuration table
- [ ] Create Alembic migrations for all tables
- [ ] Add GIN indexes on JSONB columns (`extra`, `photos`, `deficiencies`)

**Success Criteria**:
- ✅ `alembic upgrade head` creates all tables without errors
- ✅ All indexes created successfully
- ✅ Foreign key constraints working
- ✅ JSONB columns accept valid JSON data

**Files to Create/Modify**:
- `app/db/models.py` (+300 lines)
- `alembic/versions/003_add_permits_inspections.py` (new migration)
- `app/db/schemas.py` (+200 lines for Pydantic models)

---

### A.2: Business ID System
**Priority**: 🔥🔥🔥 CRITICAL  
**Effort**: 2-3 hours  
**Status**: ⏳ PENDING

**Problem**: UUIDs are not human-friendly. Need readable IDs for customer communication.

**Solution**: Add `business_id` sequences for all entities:
- Clients: `CL-00001`, `CL-00002`
- Projects: `PRJ-00001`, `PRJ-00002`  
- Permits: `PER-00001`, `PER-00002`
- Inspections: `INS-00001`, `INS-00002`

**Implementation Tasks**:
- [ ] Create PostgreSQL sequences:
  ```sql
  CREATE SEQUENCE client_business_id_seq START 1;
  CREATE SEQUENCE project_business_id_seq START 1;
  CREATE SEQUENCE permit_business_id_seq START 1;
  CREATE SEQUENCE inspection_business_id_seq START 1;
  ```
- [ ] Add trigger functions to auto-generate business IDs:
  ```sql
  CREATE OR REPLACE FUNCTION generate_client_business_id()
  RETURNS TRIGGER AS $$
  BEGIN
    NEW.business_id = 'CL-' || LPAD(nextval('client_business_id_seq')::TEXT, 5, '0');
    RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;
  
  CREATE TRIGGER client_business_id_trigger
  BEFORE INSERT ON clients
  FOR EACH ROW
  WHEN (NEW.business_id IS NULL)
  EXECUTE FUNCTION generate_client_business_id();
  ```
- [ ] Create backfill script for existing data:
  ```python
  # scripts/backfill_business_ids.py
  async def backfill_business_ids():
      # Update existing clients with CL-00001, CL-00002, etc.
      # Update existing projects with PRJ-00001, PRJ-00002, etc.
      pass
  ```
- [ ] Update API responses to include business IDs
- [ ] Update frontend to display business IDs instead of UUIDs

**Success Criteria**:
- ✅ New entities get auto-generated business IDs
- ✅ Existing entities backfilled with sequential IDs
- ✅ Business IDs are unique and human-readable
- ✅ Frontend shows business IDs in UI

**Files to Create/Modify**:
- `alembic/versions/004_add_business_ids.py` (new migration)
- `scripts/backfill_business_ids.py` (new script)
- `app/routes/*.py` (+50 lines to include business IDs)

---

### A.3: Database Service Layer
**Priority**: 🔥🔥🔥 CRITICAL  
**Effort**: 5-7 hours  
**Status**: 🚧 IN PROGRESS (basic CRUD done for clients/projects)

**Implementation Tasks**:
- [x] Basic client CRUD: `get_clients()`, `get_client_by_id()`, `create_client()`
- [x] Basic project CRUD: `get_projects()`, `get_project_by_id()`, `create_project()`
- [ ] Permit CRUD:
  ```python
  async def get_permits(project_id: UUID = None) -> List[Permit]
  async def get_permit_by_id(permit_id: UUID) -> Permit
  async def get_permit_by_business_id(business_id: str) -> Permit
  async def upsert_permit(permit: PermitCreate) -> Permit
  async def update_permit_status(permit_id: UUID, status: str, reason: str)
  ```
- [ ] Inspection CRUD:
  ```python
  async def create_inspection(inspection: InspectionCreate) -> Inspection
  async def get_inspections(permit_id: UUID) -> List[Inspection]
  async def complete_inspection(inspection_id: UUID, result: InspectionResult)
  async def upload_inspection_photos(inspection_id: UUID, photos: List[Photo])
  ```
- [ ] Precheck logic:
  ```python
  async def inspection_precheck(permit_id: UUID, inspection_type: str) -> PrecheckResult:
      """
      Validates if inspection can be scheduled:
      - Checks required prior inspections completed
      - Validates required documents uploaded
      - Checks permit expiration
      - Returns structured list of blockers
      """
      pass
  ```
- [ ] Background jobs:
  ```python
  async def expire_permits_job():
      """Find permits past expiration and mark as expired"""
      pass
  
  async def sync_qb_permit_fees():
      """Sync permit fee payment status from QuickBooks"""
      pass
  ```

**Success Criteria**:
- ✅ All CRUD operations work with UUID and business_id lookups
- ✅ Precheck logic correctly identifies missing requirements
- ✅ Status transitions trigger audit events
- ✅ Background jobs run on schedule

**Files to Create/Modify**:
- `app/services/database_service.py` (+400 lines)
- `app/services/precheck_service.py` (+150 lines, new file)
- `app/jobs/permit_jobs.py` (+100 lines, new file)

---

### A.4: Migration Scripts
**Priority**: 🔥🔥 HIGH  
**Effort**: 4-5 hours  
**Status**: 🚧 IN PROGRESS (clients/projects done)

**Implementation Tasks**:
- [x] Migrate clients from Sheets to PostgreSQL (✅ 8 clients)
- [x] Migrate projects from Sheets to PostgreSQL (✅ 12 projects)
- [ ] Extend `scripts/migrate_sheets_to_db.py` for permits:
  ```python
  async def migrate_permits(dry_run=True):
      """
      1. Read permits from Sheets
      2. Validate jurisdiction exists
      3. Match to existing projects by project_id or name
      4. Create permit records with business IDs
      5. Log any mismatches or errors
      """
      pass
  ```
- [ ] Migrate inspections data (if exists in Sheets)
- [ ] Add jurisdiction validation and auto-create missing jurisdictions
- [ ] Create detailed migration report:
  ```
  Permit Migration Report
  =======================
  Total permits in Sheets: 45
  Successfully migrated: 43
  Skipped (no matching project): 2
  
  Jurisdiction Issues:
  - "City of Charlotte" → auto-created
  - "Concord Building Dept" → auto-created
  
  Warnings:
  - Permit #12345 has no expiration date
  - Permit #67890 references deleted project
  ```

**Success Criteria**:
- ✅ Dry-run mode prints clear report without making changes
- ✅ All valid permits migrated with correct project relationships
- ✅ Jurisdiction mismatches flagged for review
- ✅ Migration is idempotent (can run multiple times safely)

**Files to Create/Modify**:
- `scripts/migrate_sheets_to_db.py` (+200 lines)
- `scripts/validate_migration.py` (+100 lines, new file)

---

## 📋 Phase B: API & Business Flows (NEXT - 1-2 weeks)

**Goal**: Build REST API for permit and inspection workflows

### B.1: Permit API Endpoints
**Priority**: 🔥🔥🔥 CRITICAL  
**Effort**: 3-4 hours

**Endpoints to Create**:
```python
POST   /v1/projects/{project_id}/permits          # Create permit
GET    /v1/permits                                 # List all permits (with filters)
GET    /v1/permits/{id}                            # Get permit details
GET    /v1/permits/by-business-id/{business_id}   # Get by business ID
PUT    /v1/permits/{id}                            # Update permit
PUT    /v1/permits/{id}/submit                     # Submit to jurisdiction
PUT    /v1/permits/{id}/approve                    # Mark as approved
DELETE /v1/permits/{id}                            # Soft delete
```

**Features**:
- Query params for filtering: `?status=approved&jurisdiction=Charlotte`
- Include related inspections in response
- Validate status transitions (can't go from Draft → Approved)
- Return business IDs in responses for human-readable references

**Success Criteria**:
- ✅ All CRUD operations working
- ✅ Proper validation and error messages
- ✅ Status transitions logged in audit trail
- ✅ Integration tests pass

**Files to Create**:
- `app/routes/permits.py` (already exists, extend +200 lines)
- `app/schemas/permit.py` (+100 lines, new file)

---

### B.2: Inspection API Endpoints  
**Priority**: 🔥🔥🔥 CRITICAL  
**Effort**: 3-4 hours

**Endpoints to Create**:
```python
POST   /v1/permits/{permit_id}/inspections           # Schedule inspection
GET    /v1/inspections                                # List all inspections
GET    /v1/inspections/{id}                           # Get inspection details
PUT    /v1/inspections/{id}/complete                  # Mark complete with result
POST   /v1/inspections/{id}/photos                    # Upload photos
PUT    /v1/inspections/{id}/no-access                 # Mark as no-access
DELETE /v1/inspections/{id}                           # Cancel inspection
```

**Features**:
- **Precheck before scheduling**: Automatically runs validation before allowing schedule
- **Photo upload**: Support multiple photos with metadata (timestamp, GPS, notes)
- **Result types**: Pass, Fail, Partial, No Access
- **Auto status updates**: Completing inspection updates permit status

**Precheck Integration**:
```python
@router.post("/permits/{permit_id}/inspections")
async def schedule_inspection(permit_id: UUID, inspection: InspectionCreate):
    # Run precheck first
    precheck = await inspection_precheck(permit_id, inspection.inspection_type)
    
    if not precheck.can_schedule:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Inspection cannot be scheduled",
                "missing": precheck.missing,  # List of blockers
                "suggestions": precheck.suggestions
            }
        )
    
    # If precheck passes, create inspection
    return await create_inspection(inspection)
```

**Success Criteria**:
- ✅ Precheck blocks scheduling when requirements not met
- ✅ Completing inspection updates permit status correctly
- ✅ Photo uploads work with metadata
- ✅ No-access flow creates follow-up inspection

**Files to Create/Modify**:
- `app/routes/inspections.py` (+250 lines, new file)
- `app/schemas/inspection.py` (+120 lines, new file)

---

### B.3: AI Precheck & Document Extraction
**Priority**: 🔥🔥 HIGH  
**Effort**: 4-5 hours

**Goal**: Use AI to extract permit data from PDFs and validate inspection readiness

**Document Extraction**:
```python
async def extract_permit_data(pdf_file: bytes) -> PermitData:
    """
    Extract permit details from uploaded PDF using OpenAI Vision API:
    - Permit number
    - Jurisdiction
    - Permit type
    - Expiration date
    - Fee amount
    - Required inspections
    """
    # Use GPT-4 Vision to read PDF
    # Return structured PermitData object
    pass
```

**Precheck Logic**:
```python
async def inspection_precheck(permit_id: UUID, inspection_type: str) -> PrecheckResult:
    """
    Returns PrecheckResult with:
    - can_schedule: bool
    - missing: List[str] - What's blocking
    - suggestions: List[str] - How to fix
    
    Checks:
    1. Permit must be approved (not draft/pending)
    2. Prior inspections must pass (footing → framing → rough → final)
    3. Required documents uploaded (plans, engineering, etc.)
    4. Permit not expired
    5. Fees paid (if required by jurisdiction)
    """
    missing = []
    
    permit = await get_permit_by_id(permit_id)
    
    if permit.status != "Approved":
        missing.append(f"Permit must be approved (current: {permit.status})")
    
    if permit.expiration_date < datetime.now():
        missing.append("Permit expired - renewal required")
    
    # Check prerequisite inspections
    if inspection_type == "Framing":
        footing = await get_inspection_by_type(permit_id, "Footing")
        if not footing or footing.result != "Pass":
            missing.append("Footing inspection must pass first")
    
    # Check documents
    required_docs = get_required_docs(permit.jurisdiction, inspection_type)
    uploaded_docs = await get_permit_documents(permit_id)
    missing_docs = set(required_docs) - set(uploaded_docs)
    if missing_docs:
        missing.extend([f"Missing document: {doc}" for doc in missing_docs])
    
    return PrecheckResult(
        can_schedule=len(missing) == 0,
        missing=missing,
        suggestions=generate_suggestions(missing)
    )
```

**Success Criteria**:
- ✅ PDF extraction works for common permit formats
- ✅ Precheck identifies all blockers correctly
- ✅ Helpful suggestions guide users to fix issues
- ✅ Integration with inspection scheduling endpoint

**Files to Create/Modify**:
- `app/services/document_extraction.py` (+200 lines, new file)
- `app/services/precheck_service.py` (+250 lines, new file)
- `app/routes/documents.py` (+100 lines for upload)

---

### B.4: QuickBooks Billing Integration
**Priority**: 🔥🔥 HIGH  
**Effort**: 2-3 hours

**Goal**: Automate permit fee and inspection fee invoicing

**Implementation**:
```python
async def create_permit_fee_invoice(permit_id: UUID) -> Invoice:
    """
    Create QB invoice for permit fees:
    1. Get permit details
    2. Get client QB customer ID
    3. Create invoice with permit fee line item
    4. Store invoice ID in permit record
    """
    permit = await get_permit_by_id(permit_id)
    client = await get_client_by_id(permit.project.client_id)
    
    line_items = [{
        "description": f"Permit Fee - {permit.permit_type} ({permit.business_id})",
        "amount": permit.fee_amount,
        "item_ref": "Permit Fees"  # QB item
    }]
    
    invoice = await quickbooks_service.create_invoice(
        customer_id=client.qb_customer_id,
        line_items=line_items,
        memo=f"Permit {permit.business_id} for project {permit.project.business_id}"
    )
    
    # Update permit with invoice ID
    await update_permit(permit_id, qb_invoice_id=invoice.Id)
    
    return invoice

async def create_inspection_fee_invoice(inspection_id: UUID) -> Invoice:
    """Optional inspection fees (re-inspections, rush fees, etc.)"""
    # Similar logic to permit fees
    pass
```

**Success Criteria**:
- ✅ Permit fee invoices created automatically
- ✅ Invoice linked to permit and project
- ✅ Payment status synced back to permit
- ✅ Optional inspection fees supported

**Files to Create/Modify**:
- `app/services/billing_service.py` (+150 lines, new file)
- `app/handlers/ai_functions.py` (+80 lines for billing commands)

---

## 📋 Phase C: Scheduling Parity & Buildertrend Mapping (NEXT - 1 week)

**Goal**: Ensure scheduling system mirrors Buildertrend's inspector workflow

### C.1: Schedule Items → Inspections Mapping
**Priority**: 🔥🔥 HIGH  
**Effort**: 3-4 hours

**Problem**: Existing schedule system doesn't connect to permits/inspections

**Solution**:
```python
# Add inspection_id foreign key to schedule_items table
ALTER TABLE schedule_items ADD COLUMN inspection_id UUID REFERENCES inspections(id);

# When inspection scheduled, create schedule item
async def create_schedule_from_inspection(inspection: Inspection):
    schedule_item = ScheduleItemCreate(
        title=f"{inspection.inspection_type} Inspection",
        project_id=inspection.permit.project_id,
        inspection_id=inspection.id,
        scheduled_date=inspection.scheduled_date,
        assigned_to=inspection.inspector_name,
        type="inspection"
    )
    await create_schedule_item(schedule_item)
```

**Success Criteria**:
- ✅ Inspections appear in project schedule
- ✅ Schedule changes update inspection dates
- ✅ Completing inspection removes from schedule

**Files to Modify**:
- `alembic/versions/005_link_schedule_inspections.py` (new migration)
- `app/services/schedule_service.py` (+100 lines)

---

### C.2: Inspector Workflow
**Priority**: 🔥🔥 HIGH  
**Effort**: 4-5 hours

**Features to Implement**:
1. **Accept/Decline**: Inspector can accept or decline assignment
2. **Complete**: Mark inspection complete with result (pass/fail/partial)
3. **No Access**: Mark as no-access and auto-create follow-up
4. **Photo Upload**: Upload photos with GPS and timestamp
5. **Deficiency Notes**: Structured list of issues found

**API Flow**:
```python
# Inspector accepts inspection
PUT /v1/inspections/{id}/accept
→ Updates status to "Accepted"
→ Notifies project manager

# Inspector arrives, finds no access
PUT /v1/inspections/{id}/no-access
→ Status: "No Access"
→ Creates follow-up inspection (same type, +2 days)
→ Notifies PM

# Inspector completes with failure
PUT /v1/inspections/{id}/complete
{
  "result": "Fail",
  "deficiencies": [
    {"item": "Missing hurricane clips", "location": "North wall"},
    {"item": "Improper wiring", "location": "Kitchen outlet"}
  ]
}
→ Status: "Failed"  
→ Permit status: "Corrections Required"
→ Creates punchlist items
→ Notifies PM and contractor
```

**Success Criteria**:
- ✅ Full inspector workflow supported
- ✅ No-access creates automatic follow-up
- ✅ Failures create punchlist items
- ✅ Timeline shows all inspection events

**Files to Modify**:
- `app/routes/inspections.py` (+150 lines)
- `app/services/notification_service.py` (+100 lines, new file)

---

### C.3: Reconciliation Job
**Priority**: 🔥 MEDIUM  
**Effort**: 2-3 hours

**Goal**: Detect and fix orphaned schedule items or inspections

**Implementation**:
```python
async def reconcile_schedule_inspections():
    """
    Runs nightly to check:
    1. Schedule items with no inspection → flag for review
    2. Inspections with no schedule item → create schedule
    3. Mismatched dates → sync inspection date to schedule
    4. Completed inspections still in schedule → remove
    """
    orphaned_schedules = await find_orphaned_schedule_items()
    orphaned_inspections = await find_orphaned_inspections()
    
    report = {
        "orphaned_schedules": len(orphaned_schedules),
        "orphaned_inspections": len(orphaned_inspections),
        "auto_fixed": 0,
        "requires_manual_review": []
    }
    
    # Auto-fix simple cases
    for inspection in orphaned_inspections:
        await create_schedule_from_inspection(inspection)
        report["auto_fixed"] += 1
    
    # Flag complex cases
    for schedule in orphaned_schedules:
        if schedule.type == "inspection":
            report["requires_manual_review"].append(schedule.id)
    
    logger.info(f"Reconciliation complete: {report}")
    return report
```

**Success Criteria**:
- ✅ Runs automatically every night
- ✅ Auto-fixes simple mismatches
- ✅ Flags complex cases for review
- ✅ Provides clear reconciliation report

**Files to Create**:
- `app/jobs/reconciliation_job.py` (+200 lines, new file)

---

## 📋 Phase D: Performance & Cost Control (NEXT - 1 week)

**Goal**: Optimize QuickBooks usage and reduce AI token costs

### D.1: DB-Centered QuickBooks Strategy
**Priority**: 🔥🔥🔥 CRITICAL  
**Effort**: 5-6 hours

**Problem**: Fetching 53 invoices + 24 customers on every query is wasteful

**Solution**: Cache QB data in PostgreSQL + background sync

**Implementation**:
```sql
-- Cache QB data in database
CREATE TABLE qb_customers_cache (
  qb_id VARCHAR(50) PRIMARY KEY,
  client_id UUID REFERENCES clients(id),
  display_name VARCHAR(200),
  company_name VARCHAR(200),
  email VARCHAR(200),
  phone VARCHAR(50),
  balance DECIMAL(10,2),
  synced_at TIMESTAMP DEFAULT NOW(),
  raw_data JSONB
);

CREATE TABLE qb_invoices_cache (
  qb_id VARCHAR(50) PRIMARY KEY,
  client_id UUID REFERENCES clients(id),
  project_id UUID REFERENCES projects(id),
  invoice_number VARCHAR(100),
  txn_date DATE,
  due_date DATE,
  total_amount DECIMAL(10,2),
  balance DECIMAL(10,2),
  status VARCHAR(50),
  synced_at TIMESTAMP DEFAULT NOW(),
  raw_data JSONB
);

CREATE INDEX idx_qb_customers_client ON qb_customers_cache(client_id);
CREATE INDEX idx_qb_invoices_client ON qb_invoices_cache(client_id);
CREATE INDEX idx_qb_invoices_project ON qb_invoices_cache(project_id);
```

**Background Sync**:
```python
async def sync_qb_to_db_job():
    """
    Runs every 5 minutes:
    1. Fetch changed QB records (use change data capture)
    2. Update database cache
    3. Keep small hot cache in memory (last 10 minutes)
    """
    # Fetch only changed records
    since = datetime.now() - timedelta(minutes=5)
    changed_customers = await qb_service.get_customers(changed_since=since)
    changed_invoices = await qb_service.get_invoices(changed_since=since)
    
    # Update DB cache
    for customer in changed_customers:
        await upsert_qb_customer_cache(customer)
    
    for invoice in changed_invoices:
        await upsert_qb_invoice_cache(invoice)
    
    logger.info(f"QB sync: {len(changed_customers)} customers, {len(changed_invoices)} invoices")
```

**Context Builder Update**:
```python
# OLD: Fetch from QB API every time
customers = await qb_service.get_customers()  # 500ms, every request

# NEW: Read from DB cache
customers = await get_qb_customers_from_cache()  # 20ms, from DB
```

**Success Criteria**:
- ✅ QB API calls reduced by 90%+
- ✅ Context building 10x faster (20ms vs 500ms)
- ✅ Data freshness < 5 minutes
- ✅ No stale data issues

**Files to Create/Modify**:
- `alembic/versions/006_qb_cache_tables.py` (new migration)
- `app/services/qb_cache_service.py` (+300 lines, new file)
- `app/jobs/qb_sync_job.py` (+150 lines, new file)
- `app/utils/context_builder.py` (~100 lines modified)

---

### D.2: Context Size Optimization
**Priority**: 🔥🔥 HIGH  
**Effort**: 2-3 hours

**Problem**: Sending all 53 invoices costs tokens; AI only needs recent ones

**Solution**: Intelligent truncation with summary stats

**Implementation**:
```python
def optimize_context_size(data: dict, query: str) -> dict:
    """
    Reduce context size while maintaining usefulness:
    1. Invoices: Return last 10 + summary stats
    2. Customers: Filter to query-relevant only
    3. Projects: Include only active + query-mentioned
    """
    optimized = {}
    
    # Invoices: Last 10 + summary
    if 'invoices' in data:
        all_invoices = data['invoices']
        recent_invoices = sorted(all_invoices, key=lambda x: x['TxnDate'], reverse=True)[:10]
        
        optimized['invoices'] = {
            'recent': recent_invoices,
            'summary': {
                'total_count': len(all_invoices),
                'total_amount': sum(i['TotalAmt'] for i in all_invoices),
                'unpaid_amount': sum(i['Balance'] for i in all_invoices)
            }
        }
    
    # Projects: Active only (unless query asks for all)
    if 'projects' in data and 'all projects' not in query.lower():
        optimized['projects'] = [
            p for p in data['projects'] 
            if p['status'] in ['Active', 'In Progress']
        ]
    
    return optimized
```

**Success Criteria**:
- ✅ 40-50% token reduction for list queries
- ✅ AI can still request full data when needed
- ✅ No functionality loss

**Files to Modify**:
- `app/utils/context_builder.py` (+150 lines)
- `app/services/openai_service.py` (+50 lines for instructions)

---

### D.3: Retire Sheets Heavy Optimizations  
**Priority**: 🔥 LOW  
**Effort**: 1-2 hours

**Goal**: Remove Sheets-specific optimizations once DB cutover is complete

**Tasks**:
- [ ] Mark Sheets batching as transitional only
- [ ] Remove Sheets caching after full DB migration
- [ ] Keep minimal Sheets service for historical data access
- [ ] Update documentation to reflect DB-first approach

**Success Criteria**:
- ✅ Sheets code clearly marked as legacy/transitional
- ✅ All new features use DB exclusively
- ✅ Sheets fallback can be disabled with config flag

---

## 📋 Phase E: Documentation, Testing & Rollout (ONGOING)

**Goal**: Ensure safe, documented, tested migration to new architecture

### E.1: Documentation Updates
**Priority**: 🔥🔥 HIGH  
**Effort**: Ongoing

**Tasks**:
- [ ] Update PROJECT_ROADMAP.md with current plan (this document)
- [ ] Create POSTGRES_MIGRATION_GUIDE.md with step-by-step instructions
- [ ] Document new API endpoints in API_DOCUMENTATION.md
- [ ] Add permit/inspection workflow diagrams
- [ ] Update TROUBLESHOOTING.md with DB-specific issues
- [ ] Document business ID system and sequences
- [ ] Create INSPECTOR_WORKFLOW.md for field users

**Files to Create/Update**:
- `docs/PROJECT_ROADMAP.md` (✅ in progress)
- `docs/guides/POSTGRES_MIGRATION_GUIDE.md` (new)
- `docs/guides/PERMIT_WORKFLOW.md` (new)
- `docs/guides/INSPECTOR_GUIDE.md` (new)

---

### E.2: Test Coverage
**Priority**: 🔥🔥🔥 CRITICAL  
**Effort**: Ongoing

**Current Test Coverage**: 91.7% (from Phase 0-2)

**New Tests Needed**:
```python
# tests/test_permits.py
async def test_create_permit()
async def test_permit_status_transitions()
async def test_permit_expiration_job()
async def test_business_id_generation()

# tests/test_inspections.py
async def test_schedule_inspection()
async def test_inspection_precheck_blocks_invalid()
async def test_inspection_precheck_allows_valid()
async def test_complete_inspection_updates_permit()
async def test_no_access_creates_followup()
async def test_photo_upload_metadata()

# tests/test_billing.py
async def test_create_permit_fee_invoice()
async def test_create_inspection_fee_invoice()
async def test_payment_sync_from_qb()

# tests/test_migration.py
async def test_migrate_permits_dry_run()
async def test_migrate_permits_with_validation()
async def test_jurisdiction_auto_create()

# Contract tests for AI context shape
async def test_context_contains_permits()
async def test_context_optimized_size()
```

**Target**: Maintain > 85% test coverage through all phases

---

### E.3: Staging Rollout Strategy
**Priority**: 🔥🔥🔥 CRITICAL  
**Effort**: 2-3 hours

**Rollout Phases**:

**Phase 1: Dual-Write Mode** (Week 1-2)
```python
# Write to both Sheets and DB
DB_WRITE_ENABLED = True
SHEETS_WRITE_ENABLED = True  # Keep as backup
DB_READ_FALLBACK = True  # Read from Sheets if DB fails
```

**Phase 2: Canary Testing** (Week 3)
```python
# 10% of traffic reads from DB
DB_READ_PERCENTAGE = 10
SHEETS_WRITE_ENABLED = True  # Still writing to both
```

**Phase 3: Full DB Cutover** (Week 4)
```python
# All reads from DB
DB_READ_PERCENTAGE = 100
SHEETS_WRITE_ENABLED = False  # DB is source of truth
DB_READ_FALLBACK = True  # Emergency fallback only
```

**Phase 4: Decommission Sheets** (Week 5+)
```python
# Remove Sheets writes completely
DB_READ_FALLBACK = False
# Archive Sheets data
# Remove google_service.py (except minimal read-only)
```

**Monitoring During Rollout**:
- Track DB query performance (target: < 100ms)
- Monitor error rates (target: < 0.1%)
- Compare Sheets vs DB data integrity
- Watch for race conditions in dual-write mode

---

### E.4: Rollback Plan
**Priority**: 🔥🔥🔥 CRITICAL  
**Effort**: 1 hour

**If Issues Arise During Rollout**:

1. **Immediate Rollback** (< 5 minutes)
   ```python
   # Set environment variables
   DB_READ_ENABLED = False
   SHEETS_READ_ENABLED = True
   
   # Restart service
   flyctl machine restart --app houserenovators-api
   ```

2. **Data Reconciliation** (1-2 hours)
   ```python
   # Compare DB vs Sheets data
   python scripts/compare_sheets_db.py
   
   # Identify discrepancies
   # Manually fix or re-run migration
   ```

3. **Post-Mortem** (Required)
   - Document what went wrong
   - Update tests to catch the issue
   - Fix root cause before retry

---

## 🎯 Success Metrics

### Phase A Success Criteria
- ✅ All tables created with proper indexes
- ✅ Business IDs working for all entities
- ✅ Permit and inspection CRUD working
- ✅ Migration scripts tested in dry-run mode
- ✅ Unit tests passing (> 85% coverage)

### Phase B Success Criteria
- ✅ All API endpoints working
- ✅ Precheck blocking invalid inspections
- ✅ QB invoices created automatically
- ✅ Integration tests passing

### Phase C Success Criteria
- ✅ Schedule ↔ inspection parity working
- ✅ Inspector workflow complete
- ✅ Reconciliation job running nightly
- ✅ No orphaned records

### Phase D Success Criteria
- ✅ QB API calls reduced by 90%+
- ✅ Token usage down 40-50%
- ✅ Context building < 50ms (from DB cache)
- ✅ No performance regressions

### Phase E Success Criteria
- ✅ All documentation updated
- ✅ Test coverage > 85%
- ✅ Successful staging rollout
- ✅ Zero data loss
- ✅ Sheets decommissioned

---

## 📊 Timeline Summary

| Phase | Duration | Effort | Priority | Status |
|-------|----------|--------|----------|--------|
| **A: Core Data & Migration** | 1-2 weeks | 15-20 hours | 🔥🔥🔥 | 🚧 In Progress |
| **B: API & Business Flows** | 1-2 weeks | 12-16 hours | 🔥🔥🔥 | ⏳ Pending |
| **C: Scheduling Parity** | 1 week | 9-12 hours | 🔥🔥 | ⏳ Pending |
| **D: Performance & Costs** | 1 week | 8-11 hours | 🔥🔥🔥 | ⏳ Pending |
| **E: Docs, Tests, Rollout** | Ongoing | 10-15 hours | 🔥🔥🔥 | 🚧 In Progress |

**Total Estimated Effort**: 54-74 hours (6-9 weeks at 10 hrs/week)

---

## 🗂️ Preserved from Original Roadmap

### Items Still Relevant (Integrated Above)
- ✅ DB migration / Postgres backend (Phase A)
- ✅ Payments / QuickBooks integration (Phase B.4)
- ✅ Context size optimization (Phase D.2)
- ✅ Document intelligence (Phase B.3)
- ✅ Test coverage and CI/CD (Phase E.2)

### Items Deprioritized
- ⏸️ Google Sheets rate-limit optimization (Transitional only, Phase D.3)
- ⏸️ Large-scale QB caching (Replaced by DB-centered strategy, Phase D.1)
- ⏸️ Sheets-as-primary patterns (Replaced by DB-first, Phase D.3)

---

## 🚀 Next Immediate Actions

1. **Complete A.1**: Finish permit/inspection table migrations
2. **Complete A.2**: Implement business ID system with sequences
3. **Complete A.3**: Build database service layer for permits/inspections
4. **Complete A.4**: Test migration scripts in dry-run mode

**Estimated time to Phase A completion**: 1-2 weeks

---

## 📞 Support & Questions

For questions about this roadmap or implementation details:
- See `docs/DEPLOYMENT_TROUBLESHOOTING.md` for infrastructure issues
- See `docs/guides/API_DOCUMENTATION.md` for API reference
- Check `docs/technical/` for detailed technical specs

