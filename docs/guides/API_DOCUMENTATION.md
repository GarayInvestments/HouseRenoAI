# House Renovators AI Portal - API Documentation

**Version**: 3.2 (Phase F - Frontend CRUD Completion)  
**Last Updated**: December 13, 2025  
**Status**: PostgreSQL + Supabase Auth (Phases D-E locked ✅)

## 🌐 **Base URL**
```
Production: https://api.houserenovatorsllc.com
Local Dev:  http://localhost:8000
```

## 📖 **Interactive Documentation**
- **Swagger UI**: https://api.houserenovatorsllc.com/docs (enabled only when `DEBUG=true`)
- **ReDoc**: https://api.houserenovatorsllc.com/redoc (enabled only when `DEBUG=true`)

---

## 🏗️ **Permit Management API** (PostgreSQL)

All endpoints below are PostgreSQL-backed and require a Supabase JWT:

`Authorization: Bearer <SUPABASE_ACCESS_TOKEN>`

Dates are ISO-8601 (e.g. `2025-12-13T15:04:05Z`).

### **GET /v1/permits**
List permits (paginated).

**Query Parameters**:
- `project_id` (uuid, optional)
- `status_filter` (string, optional)
- `jurisdiction` (string, optional) (stored in `extra.jurisdiction`)
- `skip` (int, default 0)
- `limit` (int, default 100)

**Response**:
```json
{
  "items": [
    {
      "permit_id": "2c6c2f1e-6ce1-4d16-8c86-0e7c7b4c5a6a",
      "business_id": "PER-00001",
      "project_id": "8f9b2f64-0fbb-4b70-90d9-3de0b2a2f9ad",
      "client_id": "b0e4d9b1-9b35-4ef8-8b35-7a2c0b7f64f9",
      "permit_number": "BC-25-0409",
      "permit_type": "Building",
      "status": "Draft",
      "application_date": null,
      "approval_date": null,
      "expiration_date": null,
      "issuing_authority": null,
      "inspector_name": null,
      "notes": null,
      "approved_by": null,
      "approved_at": null,
      "extra": {"jurisdiction": "Concord"},
      "created_at": "2025-12-13T12:00:00Z",
      "updated_at": "2025-12-13T12:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Example**:
```bash
curl "https://api.houserenovatorsllc.com/v1/permits" \
  -H "Authorization: Bearer $TOKEN"
```

---

### **POST /v1/permits**
Create a permit.

**Request Body**:
```json
{
  "project_id": "8f9b2f64-0fbb-4b70-90d9-3de0b2a2f9ad",
  "permit_type": "Building",
  "jurisdiction": "Concord",
  "permit_number": "BC-25-0409",
  "application_date": "2025-12-13T12:00:00Z",
  "issuing_authority": "City of Concord",
  "inspector_name": "Jane Inspector",
  "notes": "Initial submission"
}
```

**Example**:
```bash
curl -X POST "https://api.houserenovatorsllc.com/v1/permits" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id":"8f9b2f64-0fbb-4b70-90d9-3de0b2a2f9ad","permit_type":"Building","jurisdiction":"Concord"}'
```

---

### **GET /v1/permits/{permit_id}**
Get a permit by UUID.

---

### **GET /v1/permits/by-business-id/{business_id}**
Get a permit by business ID (e.g. `PER-00001`).

---

### **PUT /v1/permits/{permit_id}**
Update permit fields (does not change status).

**Request Body (any fields optional)**:
```json
{
  "permit_number": "BC-25-0409",
  "permit_type": "Building",
  "jurisdiction": "Concord",
  "issuing_authority": "City of Concord",
  "inspector_name": "Jane Inspector",
  "notes": "Updated notes"
}
```

---

### **PUT /v1/permits/{permit_id}/status**
Update permit status with history tracking.

**Request Body**:
```json
{
  "status": "Submitted",
  "notes": "Submitted for review"
}
```

---

### **POST /v1/permits/{permit_id}/submit**
Submit a permit for review (Draft → Submitted).

**Request Body (optional)**:
```json
{
  "application_date": "2025-12-13T12:00:00Z",
  "notes": "Submitted via portal"
}
```

---

### **GET /v1/permits/{permit_id}/precheck?inspection_type=...**
Run a basic precheck to determine if an inspection can be scheduled.

---

### **DELETE /v1/permits/{permit_id}**
Soft delete (sets status to `Cancelled`). Only allowed for permits in `Draft` or `Submitted`.

---

## 🤖 **AI Chat API**

**Authentication**: Not required (public endpoint for MVP)

### **POST /v1/chat**
Process chat message with AI using smart context loading (only fetches relevant data).

**Request Body**:
```json
{
  "message": "How many permits are currently approved?",
  "session_id": "user-123-session",
  "context": {
    "user_id": "optional"
  }
}
```

**Response**:
```json
{
  "response": "Based on the database, you have 4 permits currently approved...",
  "action_taken": null,
  "data_updated": false,
  "function_results": [],
  "contexts_loaded": ["database"]
}
```

**Example Questions**:
```bash
# Count permits by status
curl -X POST https://api.houserenovatorsllc.com/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "How many permits are approved?", "session_id": "user-123"}'

# Find specific permits
curl -X POST https://api.houserenovatorsllc.com/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me permits for project PER-00001", "session_id": "user-123"}'

# QuickBooks queries
curl -X POST https://api.houserenovatorsllc.com/v1/chat/ \
     -H "Content-Type: application/json" \
     -d '{"message": "What permits were submitted this month?"}'

# Analysis requests
curl -X POST https://api.houserenovatorsllc.com/v1/chat/ \
     -H "Content-Type: application/json" \
     -d '{"message": "Analyze permit approval times"}'
```

---

### **GET /v1/chat/status**
Get chat system status

**Response**:
```json
{
  "status": "operational",
  "openai_status": "connected",
  "database_status": "connected",
  "quickbooks_status": "authenticated",
  "features": [
    "Natural language queries",
    "Smart context loading (80% API reduction)",
    "Session memory (10-min TTL)",
    "QuickBooks integration",
    "Multi-user support"
  ]
}
```

**Example**:
```bash
curl https://api.houserenovatorsllc.com/v1/chat/status
```

---

## 🔍 **System Health API**

### **GET /**
Basic health check

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-03T12:00:00Z"
}
```

---

### **GET /health**  
Detailed health status

**Response**:
```json
{
  "status": "healthy",
  "api_version": "v1",
  "debug_mode": false
}
```

---

### **GET /debug**
System configuration status

**Response**:
```json
{
  "database_url_configured": true,
  "supabase_url_configured": true,
  "quickbooks_configured": {
    "client_id": true,
    "environment": "production",
    "tokens_in_database": true
  },
  "google_sheets": "DEPRECATED (Phase D.3 complete)"
}
```

---

## 🚨 **Error Responses**

### **Common Error Codes**

| Code | Meaning | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Permit ID not found |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Google service not initialized |

### **Error Response Format**
```json
{
  "detail": "Error message description",
  "error_code": "PERMIT_NOT_FOUND",
  "timestamp": "2025-11-03T12:00:00Z"
}
```

### **Database Errors**
```json
{
  "detail": "Database connection failed",
  "status_code": 503
}
```

---

## 🔐 **Authentication**

**Status**: Supabase Auth with JWT tokens (Phase E complete - Dec 13, 2025)

### **Auth Flow**
1. **Frontend**: User signs up/logs in via Supabase client SDK (`@supabase/supabase-js`)
2. **Supabase**: Returns JWT access token (15-min expiry)
3. **Frontend**: Sends token in `Authorization: Bearer <token>` header
4. **Backend**: Verifies JWT and maps to User model in database

### **Protected Routes**
All routes except the following require authentication:
- `/` (health check)
- `/health`, `/debug`, `/version`
- `/docs`, `/redoc`, `/openapi.json`
- `/v1/auth/supabase/*` (Supabase auth endpoints)
- `/v1/chat` (public for MVP)

### **Auth Endpoints**

**GET /v1/auth/supabase/me**
```bash
curl https://api.houserenovatorsllc.com/v1/auth/supabase/me \
  -H "Authorization: Bearer $SUPABASE_TOKEN"
```

Response:
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "pm",
  "is_active": true,
  "is_email_verified": true,
  "created_at": "2025-12-01T00:00:00Z"
}
```

**PUT /v1/auth/supabase/users/{user_id}/role** (Admin only)
Update user role: `admin`, `pm`, `inspector`, `client`, `finance`

---

## 📊 **Rate Limits**

**Current**: No rate limits implemented

**Recommended Usage**:
- Chat API: Max 10 requests/minute per user
- Permit API: Max 100 requests/minute
- Analysis API: Max 5 requests/minute

---

## 🔄 **Data Architecture**

### **Database: PostgreSQL (Supabase)**
- **Primary Storage**: All operational data (clients, projects, permits, inspections, invoices, payments, site visits)
- **Schema**: UUID primary keys + human-friendly business IDs (CL-00001, PRJ-00001, PER-00001)
- **Caching**: QuickBooks data cached in `qb_customers_cache` and `qb_invoices_cache` tables
- **Performance**: 90% reduction in API calls (Phase D.1 complete)

### **QuickBooks Integration**
- **OAuth2**: Production-approved integration
- **Sync**: Bi-directional sync for customers/invoices
- **Token Storage**: Encrypted in PostgreSQL `quickbooks_tokens` table
- **Auto-refresh**: Tokens refresh automatically before expiry

### **Google Sheets (Legacy)**
- **Status**: DEPRECATED (Phase D.3 complete - Dec 12, 2025)
- **Remaining Use**: QuickBooks token storage only (migration TODO)
- **All other data**: Migrated to PostgreSQL

---

## 🧪 **Testing**

### **Postman Collection**
Import this collection for testing:
```json
{
  "info": {
    "name": "House Renovators AI Portal",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get All Permits",
      "request": {
        "method": "GET",
        "url": "https://api.houserenovatorsllc.com/v1/permits/"
      }
    },
    {
      "name": "Chat Query",
      "request": {
        "method": "POST",
        "url": "https://api.houserenovatorsllc.com/v1/chat/",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "raw": "{\"message\": \"How many permits are approved?\"}"
        }
      }
    }
  ]
}
```

### **cURL Test Suite**
```bash
#!/bin/bash
BASE_URL="https://api.houserenovatorsllc.com"
TOKEN="your_supabase_jwt_token"

echo "Testing Health Endpoints (no auth required)..."
curl -s "$BASE_URL/" | jq .
curl -s "$BASE_URL/health" | jq .
curl -s "$BASE_URL/debug" | jq .

echo "Testing Auth Endpoint..."
curl -s "$BASE_URL/v1/auth/supabase/me" \
     -H "Authorization: Bearer $TOKEN" | jq .

echo "Testing Permit Endpoints (auth required)..."
curl -s "$BASE_URL/v1/permits" \
     -H "Authorization: Bearer $TOKEN" | jq .

curl -s "$BASE_URL/v1/permits/by-business-id/PER-00001" \
     -H "Authorization: Bearer $TOKEN" | jq .

echo "Testing Chat Endpoint (no auth for MVP)..."
curl -s -X POST "$BASE_URL/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How many permits are approved?", "session_id": "test-123"}' | jq .
```

---

## 📈 **Performance**

### **Response Times** (Production - Phase D optimizations)
- Health check: ~50ms
- Get permits (paginated): ~200ms  
- Single permit by ID: ~100ms
- Chat query: ~800ms-2s (smart context loading, 80% faster)
- QuickBooks sync: ~500ms (cached data)

**Phase D Performance Improvements**:
- 90% reduction in QuickBooks API calls (cached in PostgreSQL)
- 40-50% reduction in OpenAI token usage (smart context loading)
- 2-3x faster AI chat responses

### **Optimization Tips**
- Use specific permit IDs when possible
- Implement client-side caching for static data
- Batch multiple permit requests
- Use search filters to reduce response size

---

## 📄 **Document Processing API**

### **POST /v1/documents/extract**

Extract structured data from uploaded documents (PDFs or images) using AI.

**Request Format:** `multipart/form-data`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | File | Yes | PDF, JPG, JPEG, PNG, or WEBP file (max 10MB) |
| document_type | string | Yes | Type of document: "project" or "permit" |
| client_id | string | No | Client ID to associate with the extracted data |

**Supported File Types:**
- PDF documents (.pdf)
- Images: JPG, JPEG, PNG, WEBP

**AI Processing:**
- PDFs: Text extraction with PyPDF2 + GPT-4 analysis
- Images: GPT-4 Vision analysis

**Response Format:**
```json
{
  "status": "success",
  "filename": "kitchen_plans.pdf",
  "document_type": "project",
  "extracted_data": {
    "Project Name": "Kitchen Renovation",
    "Description": "Complete kitchen remodel with new cabinets",
    "Status": "Planning",
    "Budget": "$25,000",
    "Start Date": "2025-12-01",
    "Address": "123 Main St"
  },
  "applicant_info": {
    "Applicant Name": "John Contractor",
    "Applicant Phone": "555-0100"
  },
  "message": "Data extracted successfully. Review and confirm to create project."
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Unsupported file type"
}
```

**Example (cURL):**
```bash
curl -X POST "https://api.houserenovatorsllc.com/v1/documents/extract" \
  -F "file=@kitchen_plans.pdf" \
  -F "document_type=project" \
  -F "client_id=CLI-001"
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('document_type', 'project');
formData.append('client_id', 'CLI-001');

const response = await fetch('https://api.houserenovatorsllc.com/v1/documents/extract', {
  method: 'POST',
  body: formData
});
const result = await response.json();
```

---

### **POST /v1/documents/create-from-extract**

Create a project or permit record from AI-extracted document data.

**Request Body:**
```json
{
  "document_type": "project",
  "extracted_data": {
    "Project Name": "Kitchen Renovation",
    "Description": "Complete kitchen remodel",
    "Status": "Planning",
    "Budget": "$25,000",
    "Start Date": "2025-12-01",
    "Client ID": "CLI-001"
  }
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| document_type | string | Yes | "project" or "permit" |
| extracted_data | object | Yes | Field-value pairs extracted from document |

**Response Format:**
```json
{
  "status": "success",
  "message": "Project created successfully",
  "record_id": "P-001",
  "data": {
    "Project Name": "Kitchen Renovation",
    "Description": "Complete kitchen remodel",
    "Status": "Planning",
    "Budget": "$25,000",
    "Start Date": "2025-12-01",
    "Client ID": "CLI-001",
    "Project ID": "P-001"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Invalid document type. Must be 'project' or 'permit'."
}
```

**Example (cURL):**
```bash
curl -X POST "https://api.houserenovatorsllc.com/v1/documents/create-from-extract" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "project",
    "extracted_data": {
      "Project Name": "Kitchen Renovation",
      "Description": "Complete kitchen remodel",
      "Status": "Planning",
      "Budget": "$25,000",
      "Client ID": "CLI-001"
    }
  }'
```

**Example (JavaScript):**
```javascript
const response = await fetch('https://api.houserenovatorsllc.com/v1/documents/create-from-extract', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    document_type: 'project',
    extracted_data: {
      'Project Name': 'Kitchen Renovation',
      'Description': 'Complete kitchen remodel',
      'Status': 'Planning',
      'Budget': '$25,000',
      'Client ID': 'CLI-001'
    }
  })
});
const result = await response.json();
```

---

### **Document Processing Workflow**

**Complete Upload & Create Flow:**

1. **Upload Document**
   ```javascript
   // Step 1: Extract data from document
   const formData = new FormData();
   formData.append('file', document);
   formData.append('document_type', 'project');
   
   const extractResponse = await fetch('/v1/documents/extract', {
     method: 'POST',
     body: formData
   });
   const { extracted_data } = await extractResponse.json();
   ```

2. **Review & Edit** (Optional)
   ```javascript
   // User can review and modify extracted fields
   extracted_data['Project Name'] = 'Updated Name';
   extracted_data['Budget'] = '$30,000';
   ```

3. **Create Record**
   ```javascript
   // Step 2: Create record from extracted data
   const createResponse = await fetch('/v1/documents/create-from-extract', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       document_type: 'project',
       extracted_data: extracted_data
     })
   });
   const { success, record_id } = await createResponse.json();
   ```

---

### **AI Extraction Fields**

**Project Documents:**
- Project Name
- Description
- Status
- Budget
- Start Date
- End Date (if available)
- Address
- Client ID (if provided in upload)
- Contractor Name (if available)
- Scope of Work

**Permit Documents:**
- Permit Number
- Permit Type
- Status
- Issue Date
- Expiration Date
- Description
- Address
- Project ID (if provided)
- Inspector Name (if available)
- Approval Conditions

---

## 🆕 **Version History**

### **v3.2** (Current) - December 13, 2025 🔥
**Phase F: Frontend CRUD Completion (In Progress)**
- 🚧 Permits page field mapping fix
- ⏳ Inspections, Invoices, Payments, Site Visits pages

### **v3.1** - December 12, 2025 🔒 **LOCKED**
**Phase D-E Complete: Performance & Production Hardening**
- ✅ PostgreSQL migration (Phases A-C complete)
- ✅ 90% QuickBooks API reduction (cached in database)
- ✅ 40-50% OpenAI token reduction (smart context loading)
- ✅ 2-3x faster AI responses
- ✅ Supabase Auth integration (JWT with refresh)
- ✅ Test coverage: 90/91 tests (99%)
- ✅ Google Sheets retired (QB tokens only)

### **v1.1.0** - November 2025
**Document Processing**
- ✅ AI Document Processing (GPT-4 Vision)
- ✅ PDF and Image Upload
- ✅ Automated Data Extraction

### **v1.0.0** - November 2025
**MVP Launch**
- ✅ AI chat with permit data access
- ✅ Complete CRUD operations
- ✅ Production deployment (Fly.io + Cloudflare)

### **Upcoming Features**
- v3.3: Frontend CRUD completion (Phases F.2-F.4)
- v3.4: Advanced site visits features (GPS, photo AI)
- v3.5: Role-based access control (RBAC)
- v4.0: Multi-jurisdiction support