# Subcontractor Form - User Flow & Architecture

## User Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT/SUBCONTRACTOR                      │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Receives Form Link  │
                    │ /subcontractors/form │
                    │ ?projectId=abc-123   │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────────────────────┐
                    │   SubcontractorForm Component        │
                    │  - Fills out basic info              │
                    │  - Selects trade (dropdown)          │
                    │  - Enters license info               │
                    │  - Adds bond info (if Mecklenburg)   │
                    │  - Uploads COI file                  │
                    │  - Uploads Workers Comp file         │
                    └──────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────────────────────┐
                    │   Form Validation (Frontend)         │
                    │  - Required fields check             │
                    │  - Email format validation           │
                    │  - File size/type check              │
                    └──────────────────────────────────────┘
                               │
                               ▼ (Submit)
                    ┌──────────────────────────────────────┐
                    │   POST /v1/subcontractors/form       │
                    │  (multipart/form-data)               │
                    └──────────────────────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────────────┐
        │              BACKEND PROCESSING                   │
        │                                                    │
        │  1. Validate project_id OR permit_id exists       │
        │  2. Store form data in database                   │
        │  3. Auto-generate business_id (SUB-00001, etc)    │
        │  4. Set status = "pending_approval"               │
        │  5. Return success response                       │
        │                                                    │
        └──────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────────────────────┐
                    │     Database: subcontractors table    │
                    │                                       │
                    │  subcontractor_id: uuid              │
                    │  business_id: SUB-00001              │
                    │  project_id: (link to project)       │
                    │  full_name, email, phone             │
                    │  trade, license_number               │
                    │  bond_number, bond_amount            │
                    │  coi_document_id                     │
                    │  workers_comp_document_id            │
                    │  status: pending_approval             │
                    │  created_at: timestamp                │
                    │  extra: JSONB (for future)            │
                    │                                       │
                    └──────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────────────────────┐
                    │   Success Response to Client         │
                    │                                       │
                    │  {                                    │
                    │    "success": true,                   │
                    │    "business_id": "SUB-00001",        │
                    │    "status": "pending_approval",      │
                    │    "message": "Awaiting approval"     │
                    │  }                                    │
                    └──────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────────────────────┐
                    │      Admin Review (Your Team)         │
                    │                                       │
                    │  GET /v1/subcontractors/project/:id   │
                    │  → Lists all pending subcontractors   │
                    │                                       │
                    │  Review documents:                    │
                    │  - License verification               │
                    │  - Bond documentation                 │
                    │  - COI & Workers Comp                 │
                    │                                       │
                    └──────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                      │
                    ▼                      ▼
          ┌─────────────────┐    ┌─────────────────────┐
          │  PATCH /approve │    │  PATCH /reject      │
          │                 │    │                     │
          │ status: approved│    │ status: rejected    │
          │ approved_by: uid│    │ rejection_reason... │
          │ approved_at: ts │    │                     │
          └─────────────────┘    └─────────────────────┘
                    │                      │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────────────────────┐
                    │  Update in Database & Notify Client  │
                    │                                       │
                    │  (Phase 2: Email notifications)       │
                    │  - Approved ✓                         │
                    │  - Rejected ✗ (with reason)           │
                    │                                       │
                    └──────────────────────────────────────┘
```

## System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         SubcontractorForm.jsx Component                  │   │
│  │                                                           │   │
│  │  • Form state management (formData, files)               │   │
│  │  • Input validation (required fields)                    │   │
│  │  • File upload handling (COI, Workers Comp)              │   │
│  │  • Error/success messaging                               │   │
│  │  • URL parameter detection (projectId, permitId)         │   │
│  │  • Responsive Tailwind CSS styling                       │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                       │
│              POST /v1/subcontractors/form                       │
│         (multipart/form-data with files)                        │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │      app/routes/subcontractors.py                         │   │
│  │                                                           │   │
│  │  POST /form                                              │   │
│  │    ├─ Validate project_id OR permit_id                   │   │
│  │    ├─ Parse form data                                    │   │
│  │    ├─ Handle file uploads (placeholder)                  │   │
│  │    ├─ Create Subcontractor object                        │   │
│  │    └─ Return business_id                                 │   │
│  │                                                           │   │
│  │  GET /project/{id}  [Protected]                          │   │
│  │    └─ List subcontractors for project                    │   │
│  │                                                           │   │
│  │  PATCH /approve     [Protected]                          │   │
│  │    └─ Mark as approved, set approved_by, approved_at     │   │
│  │                                                           │   │
│  │  PATCH /reject      [Protected]                          │   │
│  │    └─ Mark as rejected, add rejection_reason             │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                       │
│          SQLAlchemy ORM + AsyncSession                          │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         subcontractors TABLE                             │   │
│  │                                                           │   │
│  │  Columns:                                                 │   │
│  │  ├─ subcontractor_id (UUID, PK)                          │   │
│  │  ├─ business_id (SUB-00001, unique, auto-gen)            │   │
│  │  ├─ project_id (FK → projects)                           │   │
│  │  ├─ permit_id (FK → permits)                             │   │
│  │  ├─ full_name, email, phone                              │   │
│  │  ├─ trade, license_number, license_state                 │   │
│  │  ├─ bond_number, bond_amount                             │   │
│  │  ├─ coi_document_id, workers_comp_document_id            │   │
│  │  ├─ status (pending_approval, approved, rejected)        │   │
│  │  ├─ approved_by (FK → users)                             │   │
│  │  ├─ created_at, updated_at                               │   │
│  │  └─ extra (JSONB)                                         │   │
│  │                                                           │   │
│  │  Indexes:                                                 │   │
│  │  ├─ project_id (for quick project lookup)                │   │
│  │  ├─ permit_id (for quick permit lookup)                  │   │
│  │  ├─ status (for filtering pending/approved)              │   │
│  │  ├─ trade (for trade-based reports)                      │   │
│  │  └─ extra (GIN index for JSONB queries)                  │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow: Form Submission

```
Step 1: User fills form
┌──────────────────────────────────────────┐
│ formData = {                             │
│   full_name: "John Smith",               │
│   email: "john@example.com",             │
│   phone: "(555) 123-4567",               │
│   trade: "ELECTRICAL",                   │
│   license_number: "EC-12345",            │
│   bond_number: "BD-67890",               │
│   project_id: "abc-123"                  │
│ }                                        │
│ files = {                                │
│   coi_file: File(...),                   │
│   workers_comp_file: File(...)           │
│ }                                        │
└──────────────────────────────────────────┘
                  │
Step 2: Frontend validation
                  │
                  ▼
┌──────────────────────────────────────────┐
│ ✓ full_name required                     │
│ ✓ email required                         │
│ ✓ phone required                         │
│ ✓ email format valid                     │
│ ✓ project_id OR permit_id present        │
└──────────────────────────────────────────┘
                  │
Step 3: Create FormData with files
                  │
                  ▼
┌──────────────────────────────────────────┐
│ FormData {                               │
│   full_name: "John Smith",               │
│   email: "john@example.com",             │
│   phone: "(555) 123-4567",               │
│   trade: "ELECTRICAL",                   │
│   license_number: "EC-12345",            │
│   bond_number: "BD-67890",               │
│   project_id: "abc-123",                 │
│   coi_file: <binary>,                    │
│   workers_comp_file: <binary>            │
│ }                                        │
└──────────────────────────────────────────┘
                  │
Step 4: POST to backend
                  │
                  ▼
POST /v1/subcontractors/form (multipart/form-data)
                  │
Step 5: Backend processing
                  │
                  ▼
┌──────────────────────────────────────────┐
│ 1. Parse multipart form data             │
│ 2. Get project from DB (validate)        │
│ 3. Create Subcontractor object:          │
│    - subcontractor_id: UUID()            │
│    - trade: "ELECTRICAL".upper()         │
│    - status: "pending_approval"          │
│    - coi_document_id: "coi_<uuid>"       │
│    - workers_comp_document_id: "..."     │
│ 4. db.add(subcontractor)                 │
│ 5. db.commit()                           │
│ 6. db.refresh() → business_id generated  │
└──────────────────────────────────────────┘
                  │
Step 6: DB trigger creates business_id
                  │
                  ▼
┌──────────────────────────────────────────┐
│ INSERT INTO subcontractors (...)         │
│ VALUES (...)                             │
│                                          │
│ TRIGGER: set_subcontractor_business_id() │
│   → business_id = "SUB-00001"             │
└──────────────────────────────────────────┘
                  │
Step 7: Return success response
                  │
                  ▼
┌──────────────────────────────────────────┐
│ {                                        │
│   "success": true,                       │
│   "subcontractor_id": "a1b2c3d4-...",   │
│   "business_id": "SUB-00001",             │
│   "status": "pending_approval",          │
│   "message": "Awaiting approval"         │
│ }                                        │
└──────────────────────────────────────────┘
                  │
Step 8: Frontend shows success
                  │
                  ▼
┌──────────────────────────────────────────┐
│ ✓ Success!                               │
│                                          │
│ Subcontractor John Smith submitted for   │
│ approval. (ID: SUB-00001)                │
│                                          │
│ [Form resets after 3 seconds]            │
└──────────────────────────────────────────┘
```

## Integration Points

### With Projects
```
Project Details Page
    ↓
    [Add Subcontractor] button
    ↓
    Link: /subcontractors/form?projectId=<project_id>
    ↓
    Subcontractor Form
    ↓
    Creates entry with project_id link
    ↓
    Can view from Project Details:
    GET /v1/subcontractors/project/<id>
```

### With Permits
```
Permit Details Page
    ↓
    [Add Subcontractor] button
    ↓
    Link: /subcontractors/form?permitId=<permit_id>
    ↓
    Subcontractor Form
    ↓
    Creates entry with permit_id link
    ↓
    Can view from Permit Details:
    GET /v1/subcontractors/permit/<id>
```

### With Admin Dashboard (Phase 2)
```
Admin Dashboard
    ↓
    Pending Approvals List
    ↓
    GET /v1/subcontractors/project/<id>
        (filter status = "pending_approval")
    ↓
    Review & Approve
    ↓
    PATCH /v1/subcontractors/<id>/approve
    ↓
    Update status → "approved"
    ↓
    Send email notification (Phase 2)
```

This architecture ensures clean separation of concerns and allows for easy future enhancements.
