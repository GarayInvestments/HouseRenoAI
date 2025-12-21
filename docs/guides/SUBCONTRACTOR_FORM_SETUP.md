# Subcontractor Form - Quick Integration Guide

## What Was Created

✅ **Database Model**: `Subcontractor` class with automatic business_id generation (SUB-00001, etc.)
✅ **Backend Routes**: Public form endpoint + authenticated admin endpoints
✅ **Frontend Form**: Complete React component with file uploads
✅ **Alembic Migration**: Database schema creation script

## Files Modified/Created

### Backend
- `app/db/models.py` - Added `Subcontractor` model class
- `app/routes/subcontractors.py` - New file with all API endpoints
- `app/main.py` - Registered subcontractors router
- `alembic/versions/subcontractors_table_001.py` - Migration script

### Frontend
- `frontend/src/pages/SubcontractorForm.jsx` - New form component

### Documentation
- `docs/guides/SUBCONTRACTOR_FORM_GUIDE.md` - Complete reference

## Step-by-Step Setup

### Step 1: Apply Database Migration

```powershell
# Navigate to project root
cd C:\Users\Steve Garay\Desktop\HouseRenovators-api

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run migration
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> subcontractors_table_001
```

### Step 2: Verify Backend Routes

```powershell
# Start backend (in a dedicated terminal)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Check logs for new routes
# Should see: GET /v1/subcontractors/* endpoints in Swagger
```

Visit `http://localhost:8000/docs` and search for "subcontractors" to see the endpoints.

### Step 3: Access the Form

#### As a Standalone Public Page
```
http://localhost:5173/subcontractors/form?projectId=abc-123-def
http://localhost:5173/subcontractors/form?permitId=xyz-789-uvw
```

#### Embedded in ProjectDetails
Add this code to `frontend/src/pages/ProjectDetails.jsx`:

```jsx
// At the top with other imports
import { Button } from '@/components/ui/button';

// In the component, add this section after other project info:
<div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
  <h3 className="font-bold text-lg mb-2">Subcontractors</h3>
  <p className="text-gray-700 mb-4">
    Have clients submit their subcontractor information for this project.
  </p>
  <Button 
    onClick={() => window.open(`/subcontractors/form?projectId=${project.project_id}`, '_blank')}
    className="bg-blue-600 hover:bg-blue-700"
  >
    → Share Subcontractor Form with Client
  </Button>
</div>
```

### Step 4: Test the Form

1. **Open the form**: `http://localhost:5173/subcontractors/form?projectId=YOUR_PROJECT_ID`
2. **Fill out the form**:
   - Full Name: John Smith
   - Email: john@example.com
   - Phone: (555) 123-4567
   - Trade: ELECTRICAL
   - License #: EC-12345
   - (Optional) Upload COI and Workers Comp files
3. **Submit** - Should see success message
4. **Check database**:
   ```sql
   SELECT * FROM subcontractors ORDER BY created_at DESC LIMIT 1;
   ```

### Step 5: Test Admin Endpoints (with auth token)

```powershell
# Get a Supabase JWT token first, then:

# List subcontractors for a project
curl -X GET "http://localhost:8000/v1/subcontractors/project/YOUR_PROJECT_ID" `
  -H "Authorization: Bearer YOUR_TOKEN"

# Approve a subcontractor
curl -X PATCH "http://localhost:8000/v1/subcontractors/SUB-ID/approve" `
  -H "Authorization: Bearer YOUR_TOKEN"

# Reject a subcontractor
curl -X PATCH "http://localhost:8000/v1/subcontractors/SUB-ID/reject?rejection_reason=License+expired" `
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Form Features

### What Users Can Submit
- ✅ Subcontractor name, email, phone
- ✅ Company name
- ✅ Trade type (dropdown with 14+ options)
- ✅ License number and state
- ✅ Bonding info (for Mecklenburg County)
- ✅ Certificate of Insurance (file upload)
- ✅ Workers Compensation insurance (file upload)
- ✅ Additional notes

### Validation
- ✅ Frontend: Required fields, email format
- ✅ Backend: Project/permit verification
- ✅ Auto-generates business_id (SUB-00001, SUB-00002, etc.)
- ✅ Sets status to "pending_approval"

## Customization

### Add More Trades
Edit `frontend/src/pages/SubcontractorForm.jsx`:
```jsx
const TRADES = [
  'ELECTRICAL',
  'PLUMBING',
  'HVAC',
  'YOUR_CUSTOM_TRADE',  // ← Add here
  // ...
];
```

### Change Default States
Edit the same file:
```jsx
const STATES = [
  'NC', 'SC', 'VA', 'GA', 'TN', 'WV', 'PA', 'KY', 'OH', 'MD'
  // Add more as needed
];
```

### Modify Form Fields
Edit `SubcontractorForm.jsx` to add/remove fields. Fields must also be added to:
1. `formData` state in component
2. Database model in `app/db/models.py`
3. Backend route handler in `app/routes/subcontractors.py`

## Security Notes

⚠️ **Current Implementation (MVP)**
- Public form submission endpoint (no auth required)
- Basic file upload (simplified - no actual storage)
- Document IDs are just placeholders

⚠️ **Before Production**
Implement:
1. **File Storage**: Use S3, Cloudflare R2, or similar
2. **File Validation**: Validate MIME types server-side
3. **Rate Limiting**: Add rate limiting to prevent spam
4. **Virus Scanning**: Consider adding antivirus scan for uploads
5. **Email Notifications**: Send confirmation emails
6. **Admin Dashboard**: Create approval UI for staff

## Common Issues & Solutions

### Issue: "Cannot find module 'SubcontractorForm'"
**Solution**: Ensure file path is correct: `frontend/src/pages/SubcontractorForm.jsx`

### Issue: Form submits but status shows "pending_approval" forever
**Solution**: Your admin hasn't reviewed it yet. Use the PATCH endpoints to approve/reject

### Issue: Files not uploading
**Solution**: 
- Check browser console for errors
- Verify CORS is working: `http://localhost:8000/v1/subcontractors/form` should be accessible
- Check request payload is FormData, not JSON

### Issue: Migration fails
**Solution**:
1. Check PostgreSQL is running
2. Check connection string in `.env`
3. Run: `alembic current` to see current revision
4. Run: `alembic upgrade --sql head` to see SQL before applying

## Next Phase Features

📋 **Admin Dashboard**
- Pending approvals list
- Document viewer (COI, Workers Comp)
- Bulk approval/rejection
- Email notifications

📧 **Email Integration**
- Confirmation when submitted
- Approval/rejection emails
- Reminders for pending items

📊 **Reporting**
- Subcontractor compliance report
- Trade breakdown by project
- Insurance expiration tracking

🔗 **Integration**
- Link to project permits
- Sync with QuickBooks
- Compliance tracking

## Support

For issues or questions:
1. Check `docs/guides/SUBCONTRACTOR_FORM_GUIDE.md` for complete docs
2. Check backend logs: `fly logs --app houserenovators-api --follow`
3. Check frontend console: Browser DevTools → Console
4. Test API endpoints: `http://localhost:8000/docs` (Swagger UI)

## Summary

You now have a complete public subcontractor form system that:
- Captures all required information (licenses, bonding, insurance)
- Supports file uploads for COI and Workers Comp
- Integrates with your project/permit system
- Provides admin approval workflow
- Auto-generates business IDs (SUB-00001, etc.)

The form is production-ready for MVP use. Enhance with file storage and email notifications in the next phase.
