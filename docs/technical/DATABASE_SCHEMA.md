# Database Schema Reference

> **Date**: December 14, 2025  
> **Database**: PostgreSQL (Supabase) - `dtfjzjhxtojkgfofrmrr.supabase.co`  
> **ORM**: SQLAlchemy 2.0.35 (async with asyncpg)  
> **Source**: Extracted from `app/db/models.py` + migration `20251214_0100_add_qualifier_compliance_tables.py`

---

## Overview

The House Renovators API uses PostgreSQL as the canonical data store, replacing Google Sheets (completed Dec 11, 2025). All models follow a consistent pattern:

- **UUID Primary Keys** - Unique identification across all tables
- **Business IDs** - Human-friendly immutable IDs (CL-00001, PRJ-00001, etc.)
- **JSONB Extra Column** - Flexible schema evolution without migrations
- **Audit Timestamps** - `created_at` and `updated_at` on every table
- **GIN Indexes** - Fast JSONB queries for dynamic fields

---

## Core Entities

### 1. Clients (`clients`)

**Purpose**: Customer/client records migrated from Google Sheets 'Clients' tab.

**Primary Key**: `client_id` (UUID)  
**Business ID**: `business_id` (CL-00001, CL-00002, ...)  
**Indexes**:
- `ix_clients_business_id` (UNIQUE)
- `ix_clients_full_name` (B-tree)
- `ix_clients_full_name_lower` (case-insensitive search)
- `ix_clients_email` (B-tree)
- `ix_clients_status` (B-tree)
- `ix_clients_qb_customer_id` (B-tree)
- `ix_clients_extra_gin` (GIN for JSONB)

**Typed Columns**:
```python
client_id: UUID (PK)                  # gen_random_uuid()
business_id: String(20) (UNIQUE)      # CL-00001, CL-00002, etc. (trigger-generated)
full_name: String(255)                # Client full name
email: String(255)                    # Contact email
phone: String(50)                     # Primary phone number
address: Text                         # Street address
city: String(100)                     # City
state: String(50)                     # State/province
zip_code: String(20)                  # Postal code
status: String(50)                    # Active, Inactive, Lead
client_type: String(50)               # Residential, Commercial
qb_customer_id: String(50)            # QuickBooks Customer.Id
qb_display_name: String(255)          # QB customer display name
qb_sync_status: String(50)            # synced, pending, error
qb_last_sync: DateTime(TZ)            # Last successful QB sync timestamp
extra: JSONB                          # Dynamic fields (custom fields, legacy columns)
created_at: DateTime(TZ)              # Record creation timestamp
updated_at: DateTime(TZ)              # Last update timestamp
```

**QuickBooks Integration**:
- `qb_customer_id` links to QuickBooks Customer entity
- Sync status tracked in `qb_sync_status` and `qb_last_sync`
- Legacy: Previously stored in Google Sheets, now fully in PostgreSQL

**Data Volume**: 8 clients (as of Dec 11, 2025)

---

### 2. Projects (`projects`)

**Purpose**: Construction/renovation project tracking from 'Projects' sheet tab.

**Primary Key**: `project_id` (UUID)  
**Business ID**: `business_id` (PRJ-00001, PRJ-00002, ...)  
**Foreign Keys**:
- `client_id` → `clients.client_id` (soft FK, not enforced)

**Indexes**:
- `ix_projects_business_id` (UNIQUE)
- `ix_projects_client_id` (B-tree)
- `ix_projects_status` (B-tree)
- `ix_projects_dates` (composite: start_date, end_date)
- `ix_projects_extra_gin` (GIN for JSONB)

**Typed Columns**:
```python
project_id: UUID (PK)                 # gen_random_uuid()
business_id: String(20) (UNIQUE)      # PRJ-00001, PRJ-00002, etc. (trigger-generated)
client_id: UUID (FK)                  # Link to clients table
project_name: String(255)             # Project title/name
project_address: Text                 # Construction site address
project_type: String(100)             # Kitchen Remodel, Addition, New Construction, etc.
status: String(50)                    # Planning, Active, On Hold, Complete, Cancelled
budget: Numeric(12,2)                 # Estimated project budget
actual_cost: Numeric(12,2)            # Actual costs incurred
start_date: DateTime(TZ)              # Planned/actual start date
end_date: DateTime(TZ)                # Planned/target completion date
completion_date: DateTime(TZ)         # Actual completion date
description: Text                     # Detailed project description
notes: Text                           # Project notes and comments
qb_estimate_id: String(50)            # QuickBooks Estimate.Id
qb_invoice_id: String(50)             # QuickBooks Invoice.Id
extra: JSONB                          # Dynamic fields
created_at: DateTime(TZ)              # Record creation timestamp
updated_at: DateTime(TZ)              # Last update timestamp
```

**Design Decision**: Projects are **top-level resources** (not nested under clients), following Buildertrend-influenced architecture. A client can have multiple projects, but projects are independently queryable.

**Data Volume**: 13 projects (as of Dec 11, 2025)

---

### 3. Permits (`permits`)

**Purpose**: Building permit tracking from 'Permits' sheet.

**Primary Key**: `permit_id` (UUID)  
**Business ID**: `business_id` (PER-00001, PER-00002, ...)  
**Foreign Keys**:
- `project_id` → `projects.project_id` (soft FK)
- `client_id` → `clients.client_id` (soft FK, denormalized)

**Indexes**:
- `ix_permits_business_id` (UNIQUE)
- `ix_permits_permit_number` (UNIQUE)
- `ix_permits_project_id` (B-tree)
- `ix_permits_client_id` (B-tree)
- `ix_permits_status` (B-tree)
- `ix_permits_extra_gin` (GIN for JSONB)

**Typed Columns**:
```python
permit_id: UUID (PK)                  # gen_random_uuid()
business_id: String(20) (UNIQUE)      # PER-00001, PER-00002, etc. (trigger-generated)
project_id: UUID (FK)                 # Link to projects table
client_id: UUID (FK)                  # Denormalized link to clients
permit_number: String(100) (UNIQUE)   # Official permit number from authority
permit_type: String(100)              # Building, Electrical, Plumbing, Mechanical, etc.
status: String(50)                    # Pending, Submitted, Under Review, Approved, Expired, Denied
application_date: DateTime(TZ)        # Date permit application submitted
approval_date: DateTime(TZ)           # Date permit approved
expiration_date: DateTime(TZ)         # Permit expiration date
issuing_authority: String(255)        # Government body issuing permit
inspector_name: String(255)           # Assigned inspector name
notes: Text                           # Permit notes and comments
status_history: JSONB                 # Array of {status, timestamp, changed_by}
approved_by: String(255)              # Who approved the permit
approved_at: DateTime(TZ)             # When approval occurred
extra: JSONB                          # Dynamic fields
created_at: DateTime(TZ)              # Record creation timestamp
updated_at: DateTime(TZ)              # Last update timestamp
```

**Workflow Columns** (added migration `7efbcd4142a3`):
- `status_history` - Tracks all status changes with timestamps
- `approved_by` / `approved_at` - Audit trail for approvals

**Data Volume**: 9 permits (as of Dec 11, 2025)

---

### 4. Inspections (`inspections`)

**Purpose**: Building inspection scheduling and tracking - first-class schedulable objects linked to permits.

**Primary Key**: `inspection_id` (UUID)  
**Business ID**: `business_id` (INS-00001, INS-00002, ...)  
**Foreign Keys**:
- `permit_id` → `permits.permit_id` (REQUIRED)
- `project_id` → `projects.project_id` (REQUIRED, denormalized)
- `assigned_to` → `users.user_id` (soft FK)

**Indexes**:
- `ix_inspections_business_id` (UNIQUE)
- `ix_inspections_permit_id` (B-tree)
- `ix_inspections_project_id` (B-tree)
- `ix_inspections_inspection_type` (B-tree)
- `ix_inspections_status` (B-tree)
- `ix_inspections_scheduled_date` (B-tree)
- `ix_inspections_photos_gin` (GIN for JSONB)
- `ix_inspections_deficiencies_gin` (GIN for JSONB)
- `ix_inspections_extra_gin` (GIN for JSONB)

**Typed Columns**:
```python
inspection_id: UUID (PK)              # gen_random_uuid()
business_id: String(20) (UNIQUE)      # INS-00001, INS-00002, etc.
permit_id: UUID (FK, REQUIRED)        # Link to permit
project_id: UUID (FK, REQUIRED)       # Denormalized for query performance
inspection_type: String(100)          # Footing, Foundation, Framing, Rough, Final, etc.
status: String(50)                    # Scheduled, Accepted, In-Progress, Completed, Failed, Cancelled
scheduled_date: DateTime(TZ)          # When inspection is scheduled
completed_date: DateTime(TZ)          # When inspection was completed
inspector: String(255)                # Inspector name or identifier
assigned_to: UUID (FK)                # User ID of assigned person
result: String(50)                    # Pass, Fail, Partial, No-Access
notes: Text                           # Inspection notes and comments
photos: JSONB                         # Array of {url, gps, timestamp, uploaded_by}
deficiencies: JSONB                   # Array of {description, severity, photo_refs, status}
extra: JSONB                          # Dynamic fields
created_at: DateTime(TZ)              # Record creation timestamp
updated_at: DateTime(TZ)              # Last update timestamp
```

**JSONB Structures**:
- `photos`: `[{url: str, gps: str, timestamp: str, uploaded_by: uuid}]`
- `deficiencies`: `[{description: str, severity: str, photo_refs: [int], status: str}]`

**Data Volume**: 0 inspections (table exists, feature not yet used)

---

### 5. Invoices (`invoices`)

**Purpose**: Invoice tracking with QuickBooks sync - supports project billing and permit fees.

**Primary Key**: `invoice_id` (UUID)  
**Business ID**: `business_id` (INV-00001, INV-00002, ...)  
**Foreign Keys**:
- `project_id` → `projects.project_id` (REQUIRED)
- `client_id` → `clients.client_id` (soft FK, denormalized)

**Indexes**:
- `ix_invoices_business_id` (UNIQUE)
- `ix_invoices_invoice_number` (UNIQUE)
- `ix_invoices_qb_invoice_id` (UNIQUE)
- `ix_invoices_project_id` (B-tree)
- `ix_invoices_client_id` (B-tree)
- `ix_invoices_invoice_date` (B-tree)
- `ix_invoices_due_date` (B-tree)
- `ix_invoices_status` (B-tree)
- `ix_invoices_sync_status` (B-tree)
- `ix_invoices_line_items_gin` (GIN for JSONB)
- `ix_invoices_extra_gin` (GIN for JSONB)

**Typed Columns**:
```python
invoice_id: UUID (PK)                 # gen_random_uuid()
business_id: String(20) (UNIQUE)      # INV-00001, INV-00002, etc.
project_id: UUID (FK, REQUIRED)       # Link to project
client_id: UUID (FK)                  # Denormalized link to client
qb_invoice_id: String(50) (UNIQUE)    # QuickBooks Invoice.Id
invoice_number: String(50) (UNIQUE)   # Invoice number (may match QB)
invoice_date: DateTime(TZ)            # Invoice issue date
due_date: DateTime(TZ)                # Payment due date
subtotal: Numeric(12,2)               # Pre-tax amount
tax_amount: Numeric(12,2)             # Tax amount
total_amount: Numeric(12,2)           # Total invoice amount
balance: Numeric(12,2)                # Outstanding balance (LEGACY)
amount_paid: Numeric(12,2)            # Total payments received (migration 1792b711773f)
balance_due: Numeric(12,2)            # Calculated: total_amount - amount_paid
status: String(50)                    # Draft, Sent, Paid, Overdue, Cancelled
line_items: JSONB                     # Array of {description, quantity, rate, amount, item_id}
sync_status: String(50)               # pending, synced, failed, conflict
sync_error: Text                      # Sync error message if failed
last_sync_attempt: DateTime(TZ)       # Timestamp of last sync attempt
notes: Text                           # Invoice notes
extra: JSONB                          # Dynamic fields
created_at: DateTime(TZ)              # Record creation timestamp
updated_at: DateTime(TZ)              # Last update timestamp
```

**QuickBooks Sync**:
- Two-way sync with QuickBooks invoices
- `sync_status` tracks sync state
- `qb_invoice_id` is unique identifier from QB

**JSONB Structure** (`line_items`):
```json
[
  {
    "description": "Labor - Week 1",
    "quantity": 40,
    "rate": 75.00,
    "amount": 3000.00,
    "item_id": "qb_item_123"
  }
]
```

**Data Volume**: 0 invoices (table exists, QB invoices not yet migrated to database)

---

### 6. Payments (`payments`)

**Purpose**: Payment tracking with QuickBooks sync - supports invoice payments and general receipts.

**Primary Key**: `payment_id` (UUID)  
**Business ID**: `business_id` (PAY-00001, PAY-00002, ...)  
**Foreign Keys**:
- `invoice_id` → `invoices.invoice_id` (soft FK, nullable)
- `client_id` → `clients.client_id` (soft FK)
- `project_id` → `projects.project_id` (soft FK)

**Indexes**:
- `ix_payments_business_id` (UNIQUE)
- `ix_payments_qb_payment_id` (UNIQUE)
- `ix_payments_invoice_id` (B-tree)
- `ix_payments_client_id` (B-tree)
- `ix_payments_project_id` (B-tree)
- `ix_payments_payment_date` (B-tree)
- `ix_payments_status` (B-tree)
- `ix_payments_sync_status` (B-tree)
- `ix_payments_extra_gin` (GIN for JSONB)

**Typed Columns**:
```python
payment_id: UUID (PK)                 # gen_random_uuid()
business_id: String(20) (UNIQUE)      # PAY-00001, PAY-00002, etc.
invoice_id: UUID (FK)                 # Link to invoice (nullable - can be general receipt)
client_id: UUID (FK)                  # Link to client
project_id: UUID (FK)                 # Link to project
qb_payment_id: String(50) (UNIQUE)    # QuickBooks Payment.Id
amount: Numeric(12,2)                 # Payment amount
payment_date: DateTime(TZ)            # Date payment received
payment_method: String(50)            # Check, Credit Card, Wire, Cash, ACH, Zelle
status: String(50)                    # Pending, Cleared, Failed, Refunded
reference_number: String(50)          # Check number or transaction ID
check_number: String(50)              # Check number (if applicable)
transaction_id: String(100)           # Bank transaction identifier
sync_status: String(50)               # pending, synced, failed, conflict
sync_error: Text                      # Sync error message if failed
last_sync_attempt: DateTime(TZ)       # Timestamp of last sync attempt
notes: Text                           # Payment notes
extra: JSONB                          # Dynamic fields
created_at: DateTime(TZ)              # Record creation timestamp
updated_at: DateTime(TZ)              # Last update timestamp
```

**Data Volume**: 1 payment (as of Dec 11, 2025)

---

### 7. Site Visits (`site_visits`)

**Purpose**: Site visit tracking - field visits for pre-construction, progress checks, walkthroughs, and punch lists.

**Primary Key**: `visit_id` (UUID)  
**Business ID**: `business_id` (SV-00001, SV-00002, ...)  
**Foreign Keys**:
- `project_id` → `projects.project_id` (REQUIRED)
- `client_id` → `clients.client_id` (soft FK, denormalized)
- `created_by` → `users.user_id` (soft FK)
- `assigned_to` → `users.user_id` (soft FK)

**Indexes**:
- `ix_site_visits_business_id` (UNIQUE)
- `ix_site_visits_project_id` (B-tree)
- `ix_site_visits_client_id` (B-tree)
- `ix_site_visits_visit_type` (B-tree)
- `ix_site_visits_status` (B-tree)
- `ix_site_visits_scheduled_date` (B-tree)
- `ix_site_visits_attendees_gin` (GIN for JSONB)
- `ix_site_visits_photos_gin` (GIN for JSONB)
- `ix_site_visits_deficiencies_gin` (GIN for JSONB)
- `ix_site_visits_follow_up_actions_gin` (GIN for JSONB)
- `ix_site_visits_extra_gin` (GIN for JSONB)

**Typed Columns**:
```python
visit_id: UUID (PK)                   # gen_random_uuid()
business_id: String(20) (UNIQUE)      # SV-00001, SV-00002, etc.
project_id: UUID (FK, REQUIRED)       # Link to project
client_id: UUID (FK)                  # Denormalized link to client
visit_type: String(100)               # Pre-Construction, Progress, Final Walkthrough, Punch List, Client Meeting
status: String(50)                    # Scheduled, In-Progress, Completed, Cancelled
scheduled_date: DateTime(TZ)          # Scheduled visit date/time
start_time: DateTime(TZ)              # Actual check-in timestamp
end_time: DateTime(TZ)                # Actual check-out timestamp
attendees: JSONB                      # Array of {name, role, email, phone}
gps_location: String(100)             # lat,lon format
photos: JSONB                         # Array of {url, gps, timestamp, uploaded_by, caption}
notes: Text                           # Visit notes and observations
weather: String(100)                  # Weather conditions during visit
deficiencies: JSONB                   # Array of {description, severity, location, photo_refs, status}
follow_up_actions: JSONB              # Array of {type, status, created_entity_id, description}
created_by: UUID (FK)                 # User who created the visit
assigned_to: UUID (FK)                # User assigned to conduct visit
extra: JSONB                          # Dynamic fields
created_at: DateTime(TZ)              # Record creation timestamp
updated_at: DateTime(TZ)              # Last update timestamp
```

**JSONB Structures**:
- `attendees`: `[{name: str, role: str, email: str, phone: str}]`
- `photos`: `[{url: str, gps: str, timestamp: str, uploaded_by: uuid, caption: str}]`
- `deficiencies`: `[{description: str, severity: str, location: str, photo_refs: [int], status: str}]`
- `follow_up_actions`: `[{type: str, status: str, created_entity_id: uuid, description: str}]`
  - `type`: 'inspection', 'change_order', 'punchlist'
  - `status`: 'pending', 'created', 'completed'

**Data Volume**: 0 site visits (table exists, feature not yet used)

---

### 8. QuickBooks Tokens (`quickbooks_tokens`)

**Purpose**: QuickBooks OAuth2 token storage - **MIGRATING** from 'QB_Tokens' Google Sheet.

**Primary Key**: `token_id` (UUID)  
**Foreign Keys**: None

**Typed Columns**:
```python
token_id: UUID (PK)                   # gen_random_uuid()
realm_id: String(50) (UNIQUE)         # QuickBooks Company ID
access_token: Text                    # OAuth2 access token (encrypted recommended)
refresh_token: Text                   # OAuth2 refresh token (encrypted recommended)
expires_at: DateTime(TZ)              # Access token expiration timestamp
refresh_expires_at: DateTime(TZ)      # Refresh token expiration (60 days)
token_type: String(50)                # Bearer
scope: Text                           # OAuth2 scopes granted
created_at: DateTime(TZ)              # Token first created
updated_at: DateTime(TZ)              # Token last refreshed
```

**Migration Status**: 
- ⚠️ **PENDING**: Still using Google Sheets ('QB_Tokens' tab) as of Dec 11, 2025
- Table exists, but `quickbooks_service.py` still reads/writes to Sheets
- See `docs/MIGRATION_STATUS.md` for migration plan

---

## Supporting Tables

### 9. Users (`users`)

**Purpose**: User authentication and authorization - managed by Supabase Auth.

**Primary Key**: `user_id` (UUID)  
**Managed By**: Supabase Auth (auth.users table)

**Note**: Application code does not directly manipulate this table. JWT tokens contain user info extracted via `get_current_user()` dependency in routes.

---

## Business ID Triggers

All tables with `business_id` columns use **database triggers** to auto-generate human-friendly IDs on INSERT.

**Trigger Pattern**:
```sql
CREATE OR REPLACE FUNCTION generate_business_id()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.business_id IS NULL THEN
    NEW.business_id := (
      SELECT COALESCE(
        CONCAT(
          TG_ARGV[0], '-',
          LPAD((MAX(CAST(SUBSTRING(business_id FROM '[0-9]+$') AS INTEGER)) + 1)::TEXT, 5, '0')
        ),
        CONCAT(TG_ARGV[0], '-00001')
      )
      FROM (SELECT business_id FROM [table_name] WHERE business_id LIKE CONCAT(TG_ARGV[0], '-%')) subq
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER [table_name]_business_id_trigger
BEFORE INSERT ON [table_name]
FOR EACH ROW EXECUTE FUNCTION generate_business_id('[PREFIX]');
```

**Prefixes**:
- Clients: `CL-`
- Projects: `PRJ-`
- Permits: `PER-`
- Inspections: `INS-`
- Invoices: `INV-`
- Payments: `PAY-`
- Site Visits: `SV-`

**Verification**:
```sql
-- Check trigger exists
SELECT tgname, tgrelid::regclass, tgtype 
FROM pg_trigger 
WHERE tgname LIKE '%business_id%';

-- Verify business_id defaults
SELECT column_name, column_default 
FROM information_schema.columns 
WHERE table_name = 'clients' AND column_name = 'business_id';
-- Expected: FetchedValue() (server-side generation)
```

---

## JSONB Usage Patterns

### Why JSONB?

1. **Schema Flexibility**: Add new fields without migrations
2. **Legacy Migration**: Preserve old Google Sheets columns during transition
3. **Complex Data**: Arrays and nested objects (photos, line items, deficiencies)
4. **Performance**: GIN indexes enable fast JSONB queries

### Common Queries

**Search JSONB for specific key**:
```sql
SELECT * FROM clients WHERE extra->>'custom_field_1' = 'value';
```

**Check if JSONB contains key**:
```sql
SELECT * FROM clients WHERE extra ? 'legacy_id';
```

**Array contains element**:
```sql
SELECT * FROM inspections 
WHERE photos @> '[{"uploaded_by": "user-uuid-here"}]'::jsonb;
```

**Update JSONB field**:
```python
# SQLAlchemy update
stmt = update(Client).where(Client.client_id == client_id).values(
    extra=func.jsonb_set(Client.extra, '{new_key}', '"new_value"', True)
)
```

---

## Index Strategy

### B-Tree Indexes (Default)
- Primary keys (UUID)
- Foreign keys (client_id, project_id, etc.)
- Status columns (frequently filtered)
- Date columns (range queries)

### GIN Indexes (JSONB)
- All `extra` columns
- All JSONB arrays (photos, line_items, deficiencies, etc.)

### Composite Indexes
- `ix_projects_dates` on (start_date, end_date) for date range queries

### Unique Indexes
- `business_id` columns (CL-00001, PRJ-00001, etc.)
- `permit_number` (official government permit numbers)
- `qb_customer_id`, `qb_invoice_id`, `qb_payment_id` (QuickBooks IDs)

---

## Connection Information

**Supabase PostgreSQL**:
```
Host: db.dtfjzjhxtojkgfofrmrr.supabase.co
Port: 5432
Database: postgres
User: postgres
Password: [stored in FLY_SECRETS]
```

**psql Connection** (requires `pgpass.conf`):
```bash
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres"
```

**Setup pgpass.conf** (see `docs/technical/SUPABASE_DATABASE_GUIDE.md`):
```powershell
.\scripts\setup-pgpass.ps1
```

**SQLAlchemy Connection String**:
```python
DATABASE_URL = "postgresql+asyncpg://postgres:[password]@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres"
```

---

## Migration History

**Key Migrations**:
- `7efbcd4142a3` - Added `status_history`, `approved_by`, `approved_at` to permits
- `1792b711773f` - Added `amount_paid`, `balance_due` to invoices
- `[initial]` - Created all core tables from Google Sheets structure

**Alembic Commands**:
```bash
# Generate new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current revision
alembic current
```

---

## Qualifier Compliance Tables (Phase Q.1 - Added Dec 14, 2025)

### 9. Licensed Businesses (`licensed_businesses`)

**Purpose**: Business entities holding NCLBGC licenses qualified by individuals

**Primary Key**: `id` (UUID)  
**Business ID**: `business_id` (LB-00001, LB-00002, ...)  
**Foreign Keys**:
- `qualifying_user_id` → `users.id` (DENORMALIZED - UI only, never use for enforcement)

**Indexes**:
- `ix_licensed_businesses_business_id` (UNIQUE)
- `ix_licensed_businesses_license_number` (UNIQUE)
- `ix_licensed_businesses_qualifying_user_id` (B-tree)

**Enforcement**: None (junction table `licensed_business_qualifiers` enforces capacity)

**Typed Columns**:
```python
id: UUID (PK)                         # gen_random_uuid()
business_id: String(50) (UNIQUE)      # LB-00001, LB-00002 (trigger-generated)
business_name: String(255)            # DBA/trade name (NOT unique - DBAs can collide)
legal_name: String(255)               # Legal entity name
dba_name: String(255) (nullable)      # Doing Business As name
license_number: String(100) (UNIQUE)  # NCLBGC license number
license_type: String(100)             # Unlimited, Intermediate, Limited
license_status: String(50)            # active, inactive, suspended, revoked (CHECK constraint)
license_issue_date: Date (nullable)   # License issue date
license_expiration_date: Date (nullable) # License expiration
qualifying_user_id: UUID (nullable)   # DENORMALIZED / UI ONLY - NEVER use in enforcement
fee_model: String(50) (nullable)      # FLAT, MATRIX, HYBRID
active: Boolean                       # default=true
address, phone, email, notes: Text/String (nullable)
created_at, updated_at: DateTime(TZ)
```

---

### 10. Qualifiers (`qualifiers`)

**Purpose**: Individuals with qualifier status who can qualify licensed businesses

**Primary Key**: `id` (UUID)  
**Business ID**: `qualifier_id` (QF-00001, QF-00002, ...)  
**Foreign Keys**:
- `user_id` → `users.id` (UNIQUE, CASCADE delete - 1:1 relationship)

**Indexes**:
- `ix_qualifiers_qualifier_id` (UNIQUE)
- `ix_qualifiers_user_id` (UNIQUE)

**Enforcement**: Capacity limit enforced via `licensed_business_qualifiers` trigger

**Typed Columns**:
```python
id: UUID (PK)                         # gen_random_uuid()
qualifier_id: String(50) (UNIQUE)     # QF-00001, QF-00002 (trigger-generated)
user_id: UUID (FK, UNIQUE)            # 1:1 link to operational user account
max_licenses_allowed: Integer         # Override for max businesses (default=2, NCLBGC rule)
license_number: String(100) (nullable) # Individual qualifier license (if separate from business)
license_issue_date, expiration_date: Date (nullable)
active: Boolean                       # default=true
notes: Text (nullable)
created_at, updated_at: DateTime(TZ)
```

---

### 11. Licensed Business Qualifiers (`licensed_business_qualifiers`)

**Purpose**: Many-to-many junction with time bounds and capacity enforcement

**Primary Key**: `id` (UUID)  
**Foreign Keys**:
- `licensed_business_id` → `licensed_businesses.id` (CASCADE delete)
- `qualifier_id` → `qualifiers.id` (CASCADE delete)

**Indexes**:
- `ix_lbq_licensed_business_id`, `ix_lbq_qualifier_id` (B-tree)
- `ix_lbq_active` (partial: WHERE end_date IS NULL)
- `ix_lbq_active_dates` (composite: qualifier_id, start_date, end_date)
- **`uq_lbq_active_pair`** (UNIQUE partial: WHERE end_date IS NULL) - prevents duplicate active relationships

**Enforcement Triggers**:
- **`licensed_business_qualifiers_capacity_trigger`** - Blocks INSERT/UPDATE if qualifier serves >max_licenses_allowed with overlapping dates
- Uses `daterange()` operator for overlap detection
- Handles UPDATE properly (excludes OLD.id when counting)

**Typed Columns**:
```python
id: UUID (PK)                         # gen_random_uuid()
licensed_business_id: UUID (FK)       # Business being qualified
qualifier_id: UUID (FK)               # Qualifier providing supervision
relationship_type: String(50)         # QUALIFYING, SECONDARY, ADVISOR (CHECK constraint)
start_date: Date                      # Relationship start
end_date: Date (nullable)             # Relationship end (NULL = active)
cutoff_date: DateTime(TZ) (nullable)  # Hard cutoff after resignation (blocks oversight actions)
notes: Text (nullable)
created_at, updated_at: DateTime(TZ)
```

---

### 12. Oversight Actions (`oversight_actions`)

**Purpose**: Canonical compliance records for qualifier oversight activities

**Primary Key**: `id` (UUID)  
**Business ID**: `action_id` (OA-00001, OA-00002, ...)  
**Foreign Keys**:
- `project_id` → `projects.project_id` (CASCADE delete)
- `licensed_business_id` → `licensed_businesses.id` (CASCADE delete)
- `qualifier_id` → `qualifiers.id` (CASCADE delete)
- `licensed_business_qualifier_id` → `licensed_business_qualifiers.id` (SET NULL - immutable audit trail)
- `created_by` → `users.id` (SET NULL)

**Indexes**:
- `ix_oversight_actions_action_id` (UNIQUE)
- `ix_oversight_actions_project_id`, `ix_oversight_actions_licensed_business_id`, `ix_oversight_actions_qualifier_id` (B-tree)
- `ix_oversight_actions_project_date` (composite: project_id, action_date)

**Enforcement Triggers**:
- **`oversight_actions_cutoff_trigger`** - Blocks INSERT if action_date > relationship.cutoff_date or relationship.end_date
- Uses `action_date` (not CURRENT_DATE) for historical correctness
- Includes guard clauses for NULL project context during backfill

**Typed Columns**:
```python
id: UUID (PK)                         # gen_random_uuid()
action_id: String(50) (UNIQUE)        # OA-00001, OA-00002 (trigger-generated)
project_id: UUID (FK)                 # Project being supervised
licensed_business_id: UUID (FK)       # Business context for audit trail
qualifier_id: UUID (FK)               # Qualifier performing oversight
licensed_business_qualifier_id: UUID (FK, nullable) # Hard FK to exact relationship (Phase Q.2: NOT NULL)
action_type: String(100)              # site_visit, plan_review, permit_review, client_meeting, etc. (CHECK constraint)
action_date: DateTime(TZ)             # When oversight occurred
duration_minutes: Integer (nullable)  # Duration of oversight
location, notes: Text (nullable)
attendees: JSONB (nullable)           # Array of attendee objects
photos: JSONB (nullable)              # Array of photo objects
created_by: UUID (FK, nullable)
created_at, updated_at: DateTime(TZ)
```

**Oversight Hierarchy**: `oversight_actions` is THE CANONICAL COMPLIANCE RECORD. `site_visits` and `inspections` are SUPPORTING EVIDENCE ONLY.

---

### 13. Compliance Justifications (`compliance_justifications`)

**Purpose**: Audit log for rule overrides with approval workflow

**Primary Key**: `id` (UUID)  
**Business ID**: `justification_id` (CJ-00001, CJ-00002, ...)  
**Foreign Keys**:
- `approved_by` → `users.id` (SET NULL)
- `created_by` → `users.id` (SET NULL)

**Indexes**:
- `ix_compliance_justifications_justification_id` (UNIQUE)

**Typed Columns**:
```python
id: UUID (PK)                         # gen_random_uuid()
justification_id: String(50) (UNIQUE) # CJ-00001, CJ-00002 (trigger-generated)
rule_violated: String(255)            # Which compliance rule was overridden
reason: Text                          # Justification explanation
approved_by: UUID (FK, nullable)      # User who approved override
approval_date: DateTime(TZ) (nullable)
created_by: UUID (FK, nullable)
created_at, updated_at: DateTime(TZ)
```

---

### Enhanced Existing Tables (Phase Q.1)

**Projects**:
- Added: `licensed_business_id` (UUID FK), `qualifier_id` (UUID FK), `engagement_model` (VARCHAR CHECK), `oversight_required` (BOOLEAN), `compliance_notes` (TEXT)
- FKs: → `licensed_businesses.id`, → `qualifiers.id`
- Indexes: `ix_projects_licensed_business_id`, `ix_projects_qualifier_id`, `ix_projects_engagement_model`

**Permits**:
- Added: `licensed_business_id` (UUID FK), `qualifier_id` (UUID FK), `license_number_used` (VARCHAR), `responsibility_role` (VARCHAR CHECK)
- FKs: → `licensed_businesses.id`, → `qualifiers.id`

**Site Visits**:
- Added: `oversight_type` (VARCHAR CHECK), `qualifier_id` (UUID FK), `qualifier_present` (BOOLEAN), `oversight_justification` (TEXT)
- FK: → `qualifiers.id`

**Inspections**:
- Added: `qualifier_attended` (BOOLEAN), `oversight_site_visit_id` (UUID FK)
- FK: → `site_visits.visit_id`

**Users**:
- Added: `is_qualifier` (BOOLEAN) - UI convenience flag only, NOT compliance authority

---

## Table Statistics

| Table | Data Volume (Dec 14, 2025) | Business ID Prefix | QuickBooks Sync |
|-------|---------------------------|--------------------|-----------------|
| clients | 8 | CL- | ✅ Yes (customers) |
| projects | 13 | PRJ- | ⚠️ Partial (estimates/invoices) |
| permits | 9 | PER- | ❌ No |
| payments | 1 | PAY- | ✅ Yes (payments) |
| invoices | 0 | INV- | ✅ Yes (invoices) |
| inspections | 0 | INS- | ❌ No |
| site_visits | 0 | SV- | ❌ No |
| **licensed_businesses** | 0 | LB- | ❌ No |
| **qualifiers** | 0 | QF- | ❌ No |
| **licensed_business_qualifiers** | 0 | N/A | ❌ No |
| **oversight_actions** | 0 | OA- | ❌ No |
| **compliance_justifications** | 0 | CJ- | ❌ No |

---

## Related Documentation

- **Migration Status**: `docs/MIGRATION_STATUS.md` - What's migrated, what remains
- **Supabase Guide**: `docs/technical/SUPABASE_DATABASE_GUIDE.md` - Database access and workflows
- **Field Mapping**: `docs/guides/FIELD_MAPPING.md` - Google Sheets → Database field mappings
- **API Models**: `app/db/models.py` - Source of truth for schema definitions
- **QuickBooks Sync**: `docs/guides/QUICKBOOKS_GUIDE.md` - QB integration patterns

---

**Last Updated**: December 14, 2025  
**Schema Version**: PostgreSQL 15 (Supabase) - Phase Q.1 Complete (5 new compliance tables + 14 new columns)  
**ORM Version**: SQLAlchemy 2.0.35
