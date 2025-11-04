# House Renovators AI Portal - API Documentation

## 🌐 **Base URL**
```
Production: https://houserenoai.onrender.com
Local Dev:  http://localhost:8000
```

## 📖 **Interactive Documentation**
- **Swagger UI**: https://houserenoai.onrender.com/docs
- **ReDoc**: https://houserenoai.onrender.com/redoc

---

## 🏗️ **Permit Management API**

### **GET /v1/permits/**
Get all permits from Google Sheets

**Response**: Array of permit objects
```json
[
  {
    "Permit ID": "3adc25e3",
    "Project ID": "86d7ce24", 
    "Permit Number": "BC-25-0409",
    "Date Submitted": "5/21/2025",
    "Date Approved": "5/21/2025",
    "Permit Status": "Approved",
    "City Portal Link": "",
    "File Upload": "Permits_Images/3adc25e3.File Upload.144559.jpg"
  }
]
```

**Example**:
```bash
curl https://houserenoai.onrender.com/v1/permits/
```

---

### **GET /v1/permits/{permit_id}**
Get specific permit by ID

**Parameters**:
- `permit_id` (string): Unique permit identifier

**Response**:
```json
{
  "permit_id": "3adc25e3",
  "data": {
    "Permit ID": "3adc25e3",
    "Project ID": "86d7ce24",
    "Permit Number": "BC-25-0409",
    "Date Submitted": "5/21/2025",
    "Date Approved": "5/21/2025", 
    "Permit Status": "Approved",
    "City Portal Link": "",
    "File Upload": "Permits_Images/3adc25e3.File Upload.144559.jpg"
  },
  "last_updated": "5/21/2025"
}
```

**Example**:
```bash
curl https://houserenoai.onrender.com/v1/permits/3adc25e3
```

---

### **PUT /v1/permits/{permit_id}**
Update a specific permit

**Parameters**:
- `permit_id` (string): Unique permit identifier

**Request Body**:
```json
{
  "updates": {
    "Permit Status": "Approved",
    "Date Approved": "2025-11-03"
  },
  "notify_team": true
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Permit 3adc25e3 updated successfully"
}
```

**Example**:
```bash
curl -X PUT https://houserenoai.onrender.com/v1/permits/3adc25e3 \
     -H "Content-Type: application/json" \
     -d '{"updates": {"Permit Status": "Approved"}, "notify_team": true}'
```

---

### **GET /v1/permits/search/**
Search permits with filters

**Query Parameters**:
- `query` (string, required): Search query or "all"
- `status` (string, optional): Filter by permit status
- `project_id` (string, optional): Filter by project ID

**Response**: Array of matching permits

**Examples**:
```bash
# Search approved permits
curl "https://houserenoai.onrender.com/v1/permits/search/?query=approved&status=approved"

# Search by project
curl "https://houserenoai.onrender.com/v1/permits/search/?query=all&project_id=86d7ce24"

# Natural language search
curl "https://houserenoai.onrender.com/v1/permits/search/?query=permits submitted this month"
```

---

### **POST /v1/permits/analyze**
AI analysis of all permits

**Response**:
```json
{
  "total_permits": 6,
  "analysis": {
    "summary": {
      "total_permits": 6,
      "approved_permits": 4,
      "under_review_permits": 1,
      "pending_approval_permits": 1
    },
    "issues": {
      "missing_approval_dates": [
        {
          "Permit ID": "7f4f969c",
          "Permit Status": "Approved"
        }
      ],
      "missing_file_uploads": [
        {
          "Permit ID": "7f4f969c", 
          "Permit Status": "Approved"
        }
      ]
    },
    "next_steps": {
      "for_under_review": "Follow up on permit 'cd7193a0' to expedite review",
      "for_missing_uploads": "Complete file uploads for permit '7f4f969c'"
    },
    "timeline": {
      "average_approval_time": "1 day",
      "longest_pending": {
        "Permit ID": "cd7193a0",
        "Days Pending": "Pending since 10/13/2025"
      }
    }
  },
  "generated_at": "2025-11-03T12:00:00"
}
```

**Example**:
```bash
curl -X POST https://houserenoai.onrender.com/v1/permits/analyze
```

---

## 🤖 **AI Chat API**

### **POST /v1/chat/**
Process chat message with AI and permit data access

**Request Body**:
```json
{
  "message": "How many permits are currently approved?",
  "context": {
    "user_id": "optional",
    "session_id": "optional"
  }
}
```

**Response**:
```json
{
  "response": "Out of the recent permits, four are currently approved. Here are the details:\n\n1. **Permit Number**: BC-25-0409\n   - **Status**: Approved\n   - **Approval Date**: 5/21/2025\n\n2. **Permit Number**: BP-25-35\n   - **Status**: Approved\n   - **Approval Date**: 5/6/2025...",
  "action_taken": null,
  "data_updated": false
}
```

**Example Questions**:
```bash
# Count permits by status
curl -X POST https://houserenoai.onrender.com/v1/chat/ \
     -H "Content-Type: application/json" \
     -d '{"message": "How many permits are approved?"}'

# Find specific permits
curl -X POST https://houserenoai.onrender.com/v1/chat/ \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me permits that need file uploads"}'

# Timeline questions
curl -X POST https://houserenoai.onrender.com/v1/chat/ \
     -H "Content-Type: application/json" \
     -d '{"message": "What permits were submitted this month?"}'

# Analysis requests
curl -X POST https://houserenoai.onrender.com/v1/chat/ \
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
  "sheets_status": "connected", 
  "features": [
    "Natural language queries",
    "Permit data access",
    "Project tracking",
    "Automated notifications"
  ]
}
```

**Example**:
```bash
curl https://houserenoai.onrender.com/v1/chat/status
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
  "services": {
    "database": "operational",
    "openai": "connected", 
    "google_sheets": "connected"
  },
  "version": "1.0.0",
  "uptime": "2 hours"
}
```

---

### **GET /debug/**
Google service initialization status

**Response**:
```json
{
  "google_service_initialized": {
    "credentials": true,
    "sheets_service": true,
    "drive_service": true
  },
  "environment": "production",
  "debug_mode": false
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

### **Google Service Errors**
```json
{
  "detail": "Google service not initialized",
  "status_code": 503
}
```

---

## 🔐 **Authentication**

**Current Status**: No authentication required (internal API)

**Future Plans**: 
- API key authentication
- JWT token-based auth
- Role-based access control

---

## 📊 **Rate Limits**

**Current**: No rate limits implemented

**Recommended Usage**:
- Chat API: Max 10 requests/minute per user
- Permit API: Max 100 requests/minute
- Analysis API: Max 5 requests/minute

---

## 🔄 **Data Sync**

### **Google Sheets Integration**
- **Real-time**: API reads directly from Google Sheets
- **Caching**: No caching implemented (always fresh data)
- **Updates**: Writes to Google Sheets are immediate
- **Notifications**: Team notifications sent via Google Chat webhook

### **Data Structure**
Expected Google Sheets columns:
- Permit ID
- Project ID  
- Permit Number
- Date Submitted
- Date Approved
- Permit Status
- City Portal Link
- File Upload

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
        "url": "https://houserenoai.onrender.com/v1/permits/"
      }
    },
    {
      "name": "Chat Query",
      "request": {
        "method": "POST",
        "url": "https://houserenoai.onrender.com/v1/chat/",
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
BASE_URL="https://houserenoai.onrender.com"

echo "Testing Health Endpoints..."
curl -s "$BASE_URL/" | jq .
curl -s "$BASE_URL/health" | jq .
curl -s "$BASE_URL/debug/" | jq .

echo "Testing Permit Endpoints..."
curl -s "$BASE_URL/v1/permits/" | jq '. | length'
curl -s "$BASE_URL/v1/permits/3adc25e3" | jq .

echo "Testing Chat Endpoint..."
curl -s -X POST "$BASE_URL/v1/chat/" \
     -H "Content-Type: application/json" \
     -d '{"message": "How many permits are approved?"}' | jq .

echo "Testing Analysis Endpoint..."
curl -s -X POST "$BASE_URL/v1/permits/analyze" | jq .
```

---

## 📈 **Performance**

### **Response Times** (Production)
- Health check: ~50ms
- Get all permits: ~300ms  
- Single permit: ~150ms
- Chat query: ~2-5s (depends on AI processing)
- Analysis: ~3-8s (depends on data size)

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
  "success": true,
  "document_type": "project",
  "extracted_data": {
    "Project Name": "Kitchen Renovation",
    "Description": "Complete kitchen remodel with new cabinets",
    "Status": "Planning",
    "Budget": "$25,000",
    "Start Date": "2025-12-01",
    "Address": "123 Main St"
  },
  "client_id": "CLI-001"
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
curl -X POST "https://houserenoai.onrender.com/v1/documents/extract" \
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

const response = await fetch('https://houserenoai.onrender.com/v1/documents/extract', {
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
  "success": true,
  "message": "Project created successfully",
  "record_id": "PROJ-123",
  "created_data": {
    "Project Name": "Kitchen Renovation",
    "Description": "Complete kitchen remodel",
    "Status": "Planning",
    "Budget": "$25,000",
    "Start Date": "2025-12-01",
    "Client ID": "CLI-001",
    "Created Date": "2025-11-04"
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
curl -X POST "https://houserenoai.onrender.com/v1/documents/create-from-extract" \
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
const response = await fetch('https://houserenoai.onrender.com/v1/documents/create-from-extract', {
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

### **v1.1.0** (Current) - November 2025
- ✅ AI Document Processing (GPT-4 Vision)
- ✅ PDF and Image Upload
- ✅ Automated Data Extraction
- ✅ Editable Field Validation
- ✅ One-Click Record Creation
- ✅ Enhanced Status Tracking
- ✅ Client Status Breakdown

### **v1.0.0** - November 2025
- ✅ Full Google Sheets integration
- ✅ AI chat with permit data access
- ✅ Complete CRUD operations
- ✅ Real-time analysis and insights
- ✅ Production deployment

### **Upcoming Features**
- v1.2.0: Authentication and rate limiting
- v1.3.0: Webhook endpoints for real-time updates
- v1.4.0: Advanced analytics and reporting
- v1.5.0: Batch document processing
- v2.0.0: Multi-project support