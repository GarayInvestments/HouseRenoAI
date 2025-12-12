# Full CRUD Implementation Plan
**Date**: December 12, 2025  
**Goal**: Complete CRUD UI for all 13 database tables

## Current State Analysis

### ✅ Tables with Backend CRUD
- **Permits**: POST, PUT, DELETE (full CRUD)
- **Inspections**: POST, PUT, DELETE (full CRUD)
- **Projects**: PUT (update only)
- **Payments**: POST (create only)

### ❌ Tables Missing Backend CRUD
- **Clients**: Only GET (need POST/PUT/DELETE)
- **Invoices**: No routes at all
- **Site Visits**: No routes at all
- **Jurisdictions**: No routes at all
- **Users**: No routes at all
- **QuickBooks caches**: Read-only (OK - managed by QB sync)

### Frontend UI Status
- **Read-only pages**: Clients, Projects, Permits
- **Missing pages**: Payments, Invoices, Inspections, Site Visits, Jurisdictions, Users
- **Missing CRUD forms**: All Create/Edit/Delete modals

## Implementation Strategy

### Phase 1: Backend API Routes (2-3 hours)
1. **Clients CRUD** (`app/routes/clients.py`)
   - POST `/v1/clients` - Create client
   - PUT `/v1/clients/{id}` - Update client
   - DELETE `/v1/clients/{id}` - Delete client

2. **Create new route files**:
   - `app/routes/invoices.py` - Full CRUD
   - `app/routes/site_visits.py` - Full CRUD
   - `app/routes/jurisdictions.py` - Full CRUD
   - `app/routes/users.py` - Full CRUD (admin only)

3. **Extend db_service.py** with CRUD methods for each table

### Phase 2: Reusable Frontend Components (1-2 hours)
1. **Modal Component** (`frontend/src/components/Modal.jsx`)
   - Reusable modal wrapper with overlay
   - Close on escape/click outside
   - Confirm/Cancel buttons

2. **FormField Component** (`frontend/src/components/FormField.jsx`)
   - Text input, textarea, select, date picker
   - Validation states and error messages
   - Consistent styling

3. **DataTable Component** (`frontend/src/components/DataTable.jsx`)
   - Sortable columns
   - Search/filter
   - Action buttons (Edit/Delete)
   - Pagination

4. **ConfirmDialog Component** (`frontend/src/components/ConfirmDialog.jsx`)
   - Delete confirmations
   - Dangerous action warnings

### Phase 3: Enhance Existing Pages (2-3 hours)
1. **Clients.jsx** - Add:
   - "+ New Client" button → Create modal
   - Edit button on each card → Edit modal
   - Delete button → Confirm dialog
   - Form fields: name, email, phone, address, city, state, zip, type, status

2. **Projects.jsx** - Add:
   - "+ New Project" button → Create modal
   - Edit button on each card
   - Delete button
   - Form fields: name, address, client (dropdown), status, description

3. **Permits.jsx** - Add:
   - "+ New Permit" button → Create modal
   - Edit button on each card
   - Delete button (already exists in backend)
   - Form fields: type, number, status, project (dropdown), jurisdiction

### Phase 4: New Pages (3-4 hours)
1. **Payments.jsx** - Full CRUD
   - List all payments with amount, date, method, client
   - Create payment → Link to project/invoice
   - Edit payment details
   - Delete payment
   - QuickBooks sync button

2. **Invoices.jsx** - Full CRUD
   - List all invoices with number, amount, status, client
   - Create invoice → Line items editor
   - Edit invoice
   - Delete invoice
   - "Send to QuickBooks" button

3. **Inspections.jsx** - Full CRUD
   - List all inspections with date, type, result, project
   - Create inspection → Photo upload, deficiencies
   - Edit inspection
   - Delete inspection (already exists in backend)

4. **SiteVisits.jsx** - Full CRUD
   - List site visits with date, purpose, attendees
   - Create site visit → Link to project
   - Edit visit notes
   - Delete visit

5. **Jurisdictions.jsx** - Full CRUD
   - List all jurisdictions with name, contact, phone
   - Create jurisdiction
   - Edit jurisdiction
   - Delete jurisdiction

6. **UserManagement.jsx** - Admin only
   - List all users with email, name, role, status
   - Create user → Send invite email
   - Edit user role (admin, pm, inspector, client, finance)
   - Deactivate/activate user
   - Reset password link

### Phase 5: Routing & Navigation (1 hour)
1. **Update App.jsx** - Add routes for new pages
2. **Update TopBar.jsx** - Add navigation links
3. **Update appStore.js** - Add navigation methods
4. **Add role-based access** - Hide admin pages for non-admins

### Phase 6: Testing & Polish (2-3 hours)
1. Test all Create operations
2. Test all Update operations
3. Test all Delete operations with confirmations
4. Test form validation
5. Test error handling
6. Test on mobile/responsive
7. Deploy to production

## Total Estimated Time: 11-16 hours

## Data Models for Forms

### Client Form
```javascript
{
  full_name: string (required),
  email: string (required, email validation),
  phone: string,
  address: string,
  city: string,
  state: string,
  zip_code: string,
  client_type: 'Residential' | 'Commercial',
  status: 'Active' | 'Inactive' | 'Lead'
}
```

### Project Form
```javascript
{
  project_name: string (required),
  project_address: string (required),
  client_id: UUID (required, dropdown),
  status: 'Planning' | 'Active' | 'Completed' | 'On Hold',
  description: text,
  start_date: date,
  target_completion: date
}
```

### Permit Form
```javascript
{
  permit_type: string (required),
  permit_number: string,
  project_id: UUID (required, dropdown),
  jurisdiction_id: UUID (dropdown),
  status: 'Draft' | 'Submitted' | 'Under Review' | 'Approved' | 'Rejected',
  application_date: date,
  approval_date: date,
  expiration_date: date
}
```

### Payment Form
```javascript
{
  amount: decimal (required),
  payment_date: date (required),
  payment_method: 'Cash' | 'Check' | 'Credit Card' | 'ACH' | 'Wire',
  project_id: UUID (dropdown),
  invoice_id: UUID (dropdown),
  notes: text,
  qb_payment_id: string (auto from QB sync)
}
```

### Invoice Form
```javascript
{
  invoice_number: string (auto-generated),
  client_id: UUID (required, dropdown),
  project_id: UUID (dropdown),
  invoice_date: date (required),
  due_date: date (required),
  status: 'Draft' | 'Sent' | 'Paid' | 'Overdue' | 'Cancelled',
  line_items: [{
    description: string,
    quantity: decimal,
    rate: decimal,
    amount: decimal (calculated)
  }],
  subtotal: decimal (calculated),
  tax: decimal,
  total: decimal (calculated),
  qb_invoice_id: string (auto from QB sync)
}
```

### Inspection Form
```javascript
{
  inspection_type: string (required),
  inspection_date: date (required),
  project_id: UUID (required, dropdown),
  permit_id: UUID (dropdown),
  inspector_name: string,
  result: 'Pass' | 'Fail' | 'Conditional' | 'Pending',
  deficiencies: text,
  photos: file[] (upload),
  notes: text
}
```

### Site Visit Form
```javascript
{
  visit_date: date (required),
  project_id: UUID (required, dropdown),
  purpose: string (required),
  attendees: string,
  observations: text,
  action_items: text,
  photos: file[] (upload)
}
```

### Jurisdiction Form
```javascript
{
  name: string (required),
  jurisdiction_type: 'City' | 'County' | 'State',
  contact_name: string,
  phone: string,
  email: string,
  website: string,
  address: string,
  notes: text
}
```

### User Form (Admin Only)
```javascript
{
  email: string (required, unique),
  full_name: string (required),
  phone: string,
  role: 'admin' | 'pm' | 'inspector' | 'client' | 'finance' (required),
  is_active: boolean,
  send_invite_email: boolean
}
```

## API Endpoints to Create

### Clients
- `POST /v1/clients` - Create client
- `PUT /v1/clients/{id}` - Update client
- `DELETE /v1/clients/{id}` - Delete client

### Projects  
- `POST /v1/projects` - Create project (already have PUT)
- `DELETE /v1/projects/{id}` - Delete project

### Invoices (New File)
- `GET /v1/invoices` - List all
- `GET /v1/invoices/{id}` - Get one
- `POST /v1/invoices` - Create
- `PUT /v1/invoices/{id}` - Update
- `DELETE /v1/invoices/{id}` - Delete
- `POST /v1/invoices/{id}/send-to-qb` - Sync to QuickBooks

### Site Visits (New File)
- `GET /v1/site-visits` - List all
- `GET /v1/site-visits/{id}` - Get one
- `POST /v1/site-visits` - Create
- `PUT /v1/site-visits/{id}` - Update
- `DELETE /v1/site-visits/{id}` - Delete

### Jurisdictions (New File)
- `GET /v1/jurisdictions` - List all
- `GET /v1/jurisdictions/{id}` - Get one
- `POST /v1/jurisdictions` - Create
- `PUT /v1/jurisdictions/{id}` - Update
- `DELETE /v1/jurisdictions/{id}` - Delete

### Users (New File - Admin Only)
- `GET /v1/users` - List all (admin only)
- `GET /v1/users/{id}` - Get one
- `POST /v1/users` - Create user (admin only)
- `PUT /v1/users/{id}` - Update user (admin only)
- `PUT /v1/users/{id}/role` - Change role (admin only)
- `PUT /v1/users/{id}/activate` - Activate (admin only)
- `PUT /v1/users/{id}/deactivate` - Deactivate (admin only)
- `DELETE /v1/users/{id}` - Delete user (admin only)

## Success Criteria
- ✅ All 13 tables have full CRUD operations
- ✅ All operations work in UI with proper validation
- ✅ Confirmation dialogs for all delete operations
- ✅ Error handling with user-friendly messages
- ✅ Role-based access (admin sees Users page)
- ✅ Mobile-responsive forms
- ✅ Consistent UI/UX across all pages
- ✅ QuickBooks sync works for invoices/payments
- ✅ All operations deployed to production

## Next Steps
1. Start with backend API routes (foundation)
2. Build reusable components (efficiency)
3. Enhance existing pages (quick wins)
4. Create new pages (bulk of work)
5. Add routing and navigation
6. Test thoroughly and deploy
