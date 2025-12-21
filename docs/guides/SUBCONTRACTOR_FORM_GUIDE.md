# Subcontractor Form Feature

**Date**: December 21, 2025  
**Status**: Ready for Implementation  
**Version**: 1.0

## Overview

A public-facing form allows clients to submit subcontractor information for their building permits. The form captures trade information, licensing, bonding requirements (especially for Mecklenburg County), and insurance documents (COI and Workers Comp).

## Features

### Data Captured
- **Basic Info**: Full name, email, phone, company name
- **Trade**: Dropdown selection (Electrical, Plumbing, HVAC, etc.)
- **Licensing**: License number, state, expiration date
- **Bonding**: Bond number, amount, expiration date (Mecklenburg County specific)
- **Insurance**: 
  - Certificate of Insurance (COI) file upload
  - Workers Compensation insurance file upload with expiration date
- **Notes**: Additional information field
- **Status**: Pending approval, approved, or rejected

### Endpoints

#### Public Endpoint - Form Submission
```
POST /v1/subcontractors/form
Content-Type: multipart/form-data

Parameters:
- full_name (string, required)
- email (string, required)
- phone (string, required)
- company_name (string, optional)
- trade (string, required) - enum
- license_number (string, optional)
- license_state (string, optional) - 2-char state code
- bond_number (string, optional)
- bond_amount (number, optional)
- notes (string, optional)
- project_id (string, optional) - UUID
- permit_id (string, optional) - UUID
- coi_file (file, optional) - PDF, JPG, PNG
- workers_comp_file (file, optional) - PDF, JPG, PNG

Response:
{
  "success": true,
  "subcontractor_id": "uuid",
  "business_id": "SUB-00001",
  "status": "pending_approval",
  "message": "Subcontractor information submitted. Awaiting approval."
}
```

#### Authenticated Endpoints

**List subcontractors for a project:**
```
GET /v1/subcontractors/project/{project_id}
Authorization: Bearer {token}

Response:
{
  "project_id": "uuid",
  "subcontractors": [...],
  "count": 5
}
```

**List subcontractors for a permit:**
```
GET /v1/subcontractors/permit/{permit_id}
Authorization: Bearer {token}

Response:
{
  "permit_id": "uuid",
  "subcontractors": [...],
  "count": 3
}
```

**Get single subcontractor:**
```
GET /v1/subcontractors/{subcontractor_id}
Authorization: Bearer {token}
```

**Approve subcontractor:**
```
PATCH /v1/subcontractors/{subcontractor_id}/approve
Authorization: Bearer {token}

Response:
{
  "success": true,
  "subcontractor": {...},
  "status": "approved"
}
```

**Reject subcontractor:**
```
PATCH /v1/subcontractors/{subcontractor_id}/reject?rejection_reason=License%20expired
Authorization: Bearer {token}

Response:
{
  "success": true,
  "subcontractor": {...},
  "status": "rejected"
}
```

## Frontend Usage

### Standalone Page
Create a public-facing route that renders the form:

```jsx
// In App.jsx routing
import SubcontractorForm from './pages/SubcontractorForm';

// Route for public form
<Route path="/projects/:projectId/subcontractors/form" element={<SubcontractorForm />} />

// Or standalone
<SubcontractorForm projectId={projectId} permitId={permitId} />
```

### Via URL Parameters
The form auto-detects IDs from URL query parameters:
```
/subcontractors/form?projectId=abc-123&permitId=def-456
or
/subcontractors/form?project_id=abc-123&permit_id=def-456
```

### As a Component
```jsx
import SubcontractorForm from './pages/SubcontractorForm';

export default function ProjectPage() {
  return (
    <SubcontractorForm 
      projectId={project.id} 
      permitId={permit.id}
    />
  );
}
```

## Database Schema

### Subcontractor Table

```sql
CREATE TABLE subcontractors (
  subcontractor_id UUID PRIMARY KEY,
  business_id VARCHAR(20) UNIQUE,        -- Auto-generated: SUB-00001, SUB-00002, etc.
  project_id UUID,                        -- Foreign key to projects
  permit_id UUID,                         -- Foreign key to permits
  
  -- Contact Information
  full_name VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(20),
  company_name VARCHAR(255),
  
  -- Trade & Licensing
  trade VARCHAR(100) NOT NULL,            -- ELECTRICAL, PLUMBING, HVAC, etc.
  license_number VARCHAR(100),
  license_state VARCHAR(2),               -- NC, SC, VA, etc.
  license_expires TIMESTAMP,
  
  -- Bonding (Mecklenburg County)
  bond_number VARCHAR(100),
  bond_amount NUMERIC(12, 2),
  bond_expires TIMESTAMP,
  
  -- Insurance Documents
  coi_document_id VARCHAR(255),           -- Document storage reference
  coi_uploaded_at TIMESTAMP,
  workers_comp_document_id VARCHAR(255),
  workers_comp_uploaded_at TIMESTAMP,
  workers_comp_expires TIMESTAMP,
  
  -- Approval Workflow
  status VARCHAR(50) DEFAULT 'pending_approval',  -- pending_approval, approved, rejected
  approved_by UUID,                       -- Foreign key to users
  approved_at TIMESTAMP,
  rejection_reason TEXT,
  
  -- Metadata
  notes TEXT,
  extra JSONB,                            -- For future extensibility
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX ix_subcontractors_project ON subcontractors(project_id);
CREATE INDEX ix_subcontractors_permit ON subcontractors(permit_id);
CREATE INDEX ix_subcontractors_status ON subcontractors(status);
CREATE INDEX ix_subcontractors_trade ON subcontractors(trade);
CREATE INDEX ix_subcontractors_email ON subcontractors(email);
CREATE INDEX ix_subcontractors_extra_gin ON subcontractors USING GIN(extra);
```

## Implementation Checklist

- [x] Database model created (Subcontractor class)
- [x] Backend routes implemented
- [x] Frontend form component created
- [x] Alembic migration created
- [ ] Run migration: `alembic upgrade head`
- [ ] Test form submission (local backend)
- [ ] Test file uploads
- [ ] Test approval/rejection workflow
- [ ] Integrate form into ProjectDetails page
- [ ] Add navigation links to submit subcontractor info
- [ ] Set up email notifications for approvals/rejections
- [ ] Document API in OpenAPI schema
- [ ] Deploy to production

## Next Steps

### 1. Run the Migration
```bash
# Activate venv
.\venv\Scripts\Activate.ps1

# Apply migration
alembic upgrade head
```

### 2. Test the Form Locally
```bash
# Start backend
python -m uvicorn app.main:app --reload

# Start frontend
cd frontend
npm run dev

# Navigate to form
http://localhost:5173/subcontractors/form?projectId=YOUR_PROJECT_ID
```

### 3. Add to Project Details
In `ProjectDetails.jsx`, add a section to show subcontractors and link to the form:

```jsx
// In ProjectDetails.jsx

const [subcontractors, setSubcontractors] = useState([]);

useEffect(() => {
  fetchSubcontractors();
}, [currentProjectId]);

const fetchSubcontractors = async () => {
  try {
    const response = await api.get(`/v1/subcontractors/project/${currentProjectId}`);
    setSubcontractors(response.data.subcontractors || []);
  } catch (err) {
    console.error('Failed to fetch subcontractors:', err);
  }
};

// In render:
<section>
  <h2>Subcontractors</h2>
  <div className="flex justify-between items-center mb-4">
    <p>Total: {subcontractors.length}</p>
    <Button onClick={() => navigate(`/projects/${currentProjectId}/subcontractors/form`)}>
      Add Subcontractor
    </Button>
  </div>
  <SubcontractorsList subcontractors={subcontractors} />
</section>
```

### 4. Email Notifications
Add email notification service for:
- Form submitted (to admin)
- Subcontractor approved (to contact email)
- Subcontractor rejected (to contact email with reason)

### 5. Admin Dashboard
Create admin view to:
- List pending subcontractors
- Review documents
- Approve/reject with notes
- View approval history

## Security Considerations

1. **Public Endpoint**: The form submission endpoint is public (no auth required) but validates project/permit existence
2. **File Uploads**: Currently simplified - should implement:
   - File type validation (server-side)
   - File size limits (max 10MB per file)
   - Virus scanning (optional)
   - Secure storage (S3, Cloudflare R2, etc.)
3. **Data Validation**: All required fields validated on both frontend and backend
4. **Rate Limiting**: Consider adding rate limiting to prevent abuse
5. **CORS**: Form submission uses fetch which respects CORS

## Trade Definitions

Current supported trades (expandable via dropdown):
- ELECTRICAL
- PLUMBING
- HVAC
- ROOFING
- CARPENTRY
- MASONRY
- PAINTING
- FLOORING
- LANDSCAPING
- CONCRETE
- FRAMING
- DRYWALL
- INSULATION
- OTHER

Add more as needed by editing the `TRADES` array in `SubcontractorForm.jsx`.

## Troubleshooting

### Form submission returns 400 "Must provide either project_id or permit_id"
- Ensure the form is accessed with URL parameters or passed as props
- Check browser console for the error message

### Files not uploading
- Check browser console for fetch errors
- Verify CORS settings in backend
- Check file size limits (currently unlimited in code)

### Status always shows "pending_approval"
- Migration hasn't run yet - check database
- Check backend logs for errors during submission

## API Documentation

For complete OpenAPI schema, visit:
- Local: `http://localhost:8000/docs`
- Production: `https://houserenovators-api.fly.dev/docs`

Look for `/v1/subcontractors/*` endpoints in the Swagger UI.
