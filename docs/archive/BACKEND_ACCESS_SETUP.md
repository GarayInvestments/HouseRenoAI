# 🔐 Backend System Access Setup

**Date:** November 3, 2025  
**Status:** ⏳ Pending Access Grant

---

## 📋 Overview

This document outlines the steps to ensure the House Renovators AI backend system has full access to all Google Sheets data.

---

## ✅ Configuration Status

### Backend Environment (.env)
- ✅ **OpenAI API Key:** Configured
- ✅ **Sheet ID:** `1Wp1MZFTA2rCm55IMAkNmh6z_2-vEa0mdhEkcufQVnnI`
- ✅ **Service Account File:** `../config/ultra-fresh-credentials.json`
- ✅ **CORS Origins:** Updated for Cloudflare deployment

### Service Account Credentials
- ✅ **File:** `config/ultra-fresh-credentials.json`
- ✅ **Email:** `house-renovators-service@house-renovators-ai.iam.gserviceaccount.com`
- ✅ **Project:** `house-renovators-ai`
- ✅ **Private Key:** Present and valid

---

## 🔑 Grant Sheet Access (REQUIRED)

### Step 1: Open Google Sheet
Open the sheet in your browser:
```
https://docs.google.com/spreadsheets/d/1Wp1MZFTA2rCm55IMAkNmh6z_2-vEa0mdhEkcufQVnnI
```

### Step 2: Share with Service Account
1. Click **"Share"** button (top-right corner)
2. In "Add people and groups" field, paste:
   ```
   house-renovators-service@house-renovators-ai.iam.gserviceaccount.com
   ```
3. Set permission to **"Editor"** (recommended) or **"Viewer"** (minimum)
4. **UNCHECK** "Notify people" ⚠️ (service accounts don't receive emails)
5. Click **"Share"** or **"Done"**

### Step 3: Verify Access
Run the test script:
```bash
cd "C:\Users\Steve Garay\Desktop\HouseRenovators-api"
C:/Python313/python.exe backend/test_google_access.py
```

---

## 🧪 Testing & Verification

### Available Test Scripts

#### 1. Setup Instructions
```bash
python setup_sheet_access.py
```
Shows service account email and access setup instructions.

#### 2. Schema Verification
```bash
python verify_sheets_schema.py
```
Verifies all 12 sheets exist with correct column structure.

#### 3. Backend Access Test
```bash
python backend/test_google_access.py
```
Tests backend's ability to read data from all sheets.

---

## 📊 Sheets That Need Access

The service account needs access to read/write from these 12 sheets:

| Sheet | Columns | Purpose |
|-------|---------|---------|
| Clients | 10 | Client contact information |
| Projects | 17 | Project details and tracking |
| Permits | 8 | Permit status and documentation |
| Site Visits | 10 | Inspection visits and photos |
| Subcontractors | 13 | Subcontractor management |
| Documents | 7 | Document storage and links |
| Tasks | 7 | Task assignment and tracking |
| Payments | 13 | Invoice and payment tracking |
| Jurisdiction | 11 | Permit authority contacts |
| Inspectors | 11 | Inspector tracking and notes |
| Construction Phase Tracking | 9 | Phase management |
| Phase Tracking Images | 6 | Progress photo documentation |

---

## 🔧 Backend Service Methods

Once access is granted, the backend will have these capabilities:

### General Methods
```python
# Read any range from any sheet
await google_service.read_sheet_data('SheetName!A1:Z100')

# Write data to a range
await google_service.write_sheet_data('SheetName!A2:C2', [['value1', 'value2', 'value3']])

# Append new rows
await google_service.append_sheet_data('SheetName!A:Z', [['row', 'data']])
```

### Specific Data Methods
```python
# Get all clients
clients = await google_service.get_clients_data()

# Get all projects
projects = await google_service.get_projects_data()

# Get all permits
permits = await google_service.get_permits_data()
```

---

## 🚀 API Endpoints (After Deployment)

Once deployed, the backend will expose these endpoints:

### Chat Endpoint
```
POST /api/chat
```
AI-powered chat interface for permit compliance questions.

### Permits Endpoint
```
GET /api/permits
GET /api/permits/{permit_id}
POST /api/permits
PUT /api/permits/{permit_id}
```

### Projects Endpoint
```
GET /api/projects
GET /api/projects/{project_id}
POST /api/projects
PUT /api/projects/{project_id}
```

### Health Check
```
GET /health
```

---

## 🔒 Security Considerations

### Service Account Best Practices
- ✅ Service account credentials stored in `config/` directory
- ✅ `.gitignore` includes credential files
- ✅ Minimal permissions (Sheets + Drive readonly)
- ✅ Project-specific service account

### Environment Variables
- ✅ Sensitive data in `.env` file (not committed to git)
- ✅ Production credentials managed via Render environment variables
- ✅ CORS configured for production domains only

### API Security
- ✅ CORS protection enabled
- ✅ Request validation on all endpoints
- ✅ Rate limiting (when deployed to production)

---

## 📦 Required Python Packages

Ensure these packages are installed:

```bash
# Google API packages
pip install google-auth google-auth-oauthlib google-api-python-client

# Backend framework
pip install fastapi uvicorn python-dotenv

# AI integration
pip install openai

# Utilities
pip install requests pydantic
```

Or install all at once:
```bash
pip install -r backend/requirements.txt
```

---

## 🎯 Next Steps Checklist

- [ ] **1. Grant Sheet Access** - Share sheet with service account email
- [ ] **2. Test Access** - Run `python backend/test_google_access.py`
- [ ] **3. Test Locally** - Start backend: `cd backend && uvicorn app.main:app --reload`
- [ ] **4. Deploy Backend** - Deploy to Render with environment variables
- [ ] **5. Update Frontend** - Point frontend API_URL to production backend
- [ ] **6. Test End-to-End** - Verify frontend can communicate with backend

---

## 🐛 Troubleshooting

### "Permission denied" or "Forbidden" errors
- **Solution:** Service account not granted access to the sheet. Follow "Grant Sheet Access" steps above.

### "Service account file not found"
- **Solution:** Ensure `config/ultra-fresh-credentials.json` exists at project root.

### "Module not found" errors
- **Solution:** Install required packages: `pip install -r backend/requirements.txt`

### "Invalid credentials"
- **Solution:** Verify credentials file is valid JSON and contains `private_key` and `client_email`.

### Test script timeout
- **Solution:** Check internet connection and Google API service status.

---

## 📚 Related Documentation

- **Schema Verification:** `SHEETS_VERIFICATION_COMPLETE.md`
- **Backend API Docs:** `backend/API_DOCUMENTATION.md`
- **Deployment Guide:** `backend/DEPLOYMENT.md`
- **Frontend Deployment:** `DEPLOY_NOW.md`

---

## 📞 Support Resources

- **Google Sheets API Docs:** https://developers.google.com/sheets/api
- **Service Account Guide:** https://cloud.google.com/iam/docs/service-accounts
- **FastAPI Documentation:** https://fastapi.tiangolo.com

---

**Status:** Ready for access grant. Please share the Google Sheet with the service account email and run the test script to verify.
