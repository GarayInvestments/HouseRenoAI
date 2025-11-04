# House Renovators AI Portal - Troubleshooting Guide

## 🚨 Common Issues & Solutions

### 1. **Google Service Not Initialized**

**Error**: `503 Service Unavailable: Google service not initialized`

**Cause**: Google service didn't initialize properly during FastAPI startup

**Solutions**:
```bash
# Check debug endpoint
curl https://houserenoai.onrender.com/debug/

# Should return:
{
  "google_service_initialized": {
    "credentials": true,
    "sheets_service": true, 
    "drive_service": true
  }
}
```

**If credentials=false**:
- Check `GOOGLE_CREDENTIALS_B64` environment variable is set
- Verify base64 encoding is correct
- Ensure service account JSON is valid

**If services=false**:
- Check Google APIs are enabled (Sheets API, Drive API)
- Verify service account has proper permissions
- Check Google Sheet is shared with service account email

### 2. **Google Sheets Access Denied**

**Error**: `403 Forbidden` or `The caller does not have permission`

**Solution**:
1. **Share Google Sheet** with service account email:
   - Email: `house-renovators-service@house-renovators-ai.iam.gserviceaccount.com`
   - Permission: Editor or Owner
   
2. **Verify Sheet ID** in environment variables:
   ```bash
   # From sheet URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
   SHEET_ID=1BvDHl8XS9p_example_sheet_id
   ```

### 3. **OpenAI API Errors**

**Error**: `401 Unauthorized` or `429 Rate Limit`

**Solutions**:
- Check `OPENAI_API_KEY` is valid and has credits
- Verify API key format: `sk-...`
- Monitor usage at https://platform.openai.com/usage

### 4. **Module Import Errors**

**Error**: `'NoneType' object has no attribute 'get_permits_data'`

**Cause**: Route imported Google service before it was initialized

**Solution**: Already fixed with dynamic import pattern:
```python
# Routes use this pattern:
def get_google_service():
    if not hasattr(google_service_module, 'google_service') or google_service_module.google_service is None:
        raise HTTPException(status_code=503, detail="Google service not initialized")
    return google_service_module.google_service
```

### 5. **Environment Variable Issues**

**Common Problems**:
- Newlines in base64 encoded credentials
- Missing required environment variables
- Incorrect variable names

**Verification**:
```bash
# Check all required variables are set in Render
GOOGLE_CREDENTIALS_B64=eyJ0eXBlI...
OPENAI_API_KEY=sk-...
SHEET_ID=1BvDHl8...
CHAT_WEBHOOK_URL=https://chat.googleapis.com...
DEBUG=false
PORT=10000
```

### 6. **422 Unprocessable Entity - Document Upload**

**Error**: `POST /v1/documents/create-from-extract 422 (Unprocessable Content)`

**⚠️ IMPORTANT: ASK USER WHICH ISSUE TO INVESTIGATE FIRST**

Don't assume the problem. Ask the user which troubleshooting path to try:

**Quick Diagnostic Questions**:
1. Is the error showing a specific field name or validation error?
2. Are you seeing this in browser console or Render logs?
3. Did this work before or is this a new feature?
4. Have you verified Render dashboard shows latest commit deployed?

**Common Root Causes** (in order of likelihood):

#### A. **Content-Type Mismatch** (Most Common)
**Symptom**: 422 with no specific field errors, just "Unprocessable Entity"
**Cause**: Frontend sending JSON but backend expecting Form data (or vice versa)
**Fix**: Check that frontend Content-Type matches backend expectation
```python
# Backend should accept what frontend sends:
async def create_record_from_extraction(request_data: dict):  # For JSON
# OR
async def create_record_from_extraction(
    document_type: str = Form(...),
    extracted_data: dict = Form(...)
):  # For Form data
```

#### B. **Field Mapping Issues**
**Symptom**: 422 with warnings about specific fields in Render logs
**Check Render Logs** for:
```
[WARNING] Fields not found in Projects headers: ['Square Footage', 'Parcel Number']
```
**Solution**: Extra fields should be filtered or combined into Notes

#### C. **Missing Required Fields**
**Symptom**: Error mentions missing fields like 'document_type' or 'extracted_data'
**Check**: Request payload includes all required fields
```javascript
// Frontend should send:
{
  document_type: 'project',
  extracted_data: { ... }
}
```

#### D. **Google Sheets Column Mismatch**
**Symptom**: Logs show field names that don't exist in sheet
**Verify**: Google Sheets has exact column names being sent
- **Projects sheet expected columns** (17 total):
  - Project ID, Client ID, Project Name, Address, City, State, Zip Code
  - Property Type, Estimated Start Date, Estimated End Date
  - Actual Start Date, Actual End Date, Budget, Status, Notes, Last Updated

**Debugging Commands**:
```bash
# 1. Check if endpoint exists
curl -X OPTIONS https://houserenoai.onrender.com/v1/documents/create-from-extract

# 2. Check Render logs (Render Dashboard → Logs tab)
# Look for: [INFO], [DEBUG], [WARNING], [ERROR] messages

# 3. Check deployed version (if /version endpoint exists)
curl https://houserenoai.onrender.com/version

# 4. Test with minimal payload
curl -X POST https://houserenoai.onrender.com/v1/documents/create-from-extract \
  -H "Content-Type: application/json" \
  -d '{"document_type":"project","extracted_data":{"Project ID":"TEST-001"}}'
```

**Enable Debug Logging**:
```bash
# In Render dashboard, set environment variable:
LOG_LEVEL=DEBUG

# Then check logs for detailed field mapping:
[DEBUG] Received extracted_data keys: [...]
[DEBUG] Projects headers: [...]
[DEBUG] Row values: [...]
```

## 🔧 Debugging Tools

### 1. **Health Check Endpoints**

```bash
# Basic health
curl https://houserenoai.onrender.com/

# Detailed status  
curl https://houserenoai.onrender.com/health

# Google service status
curl https://houserenoai.onrender.com/debug/

# Chat system status
curl https://houserenoai.onrender.com/v1/chat/status
```

### 2. **Test Individual Services**

```bash
# Test permit data access
curl https://houserenoai.onrender.com/v1/permits/

# Test AI chat
curl -X POST https://houserenoai.onrender.com/v1/chat/ \
     -H "Content-Type: application/json" \
     --data-binary '{"message": "test"}'

# Test specific permit
curl https://houserenoai.onrender.com/v1/permits/3adc25e3
```

### 3. **Log Analysis**

**In Render Dashboard**:
1. Go to your service
2. Click "Logs" tab
3. Look for:
   - `Google service initialized successfully`
   - `Retrieved X permits`
   - Error stack traces

**Common Log Messages**:
```
✅ [INFO] Google service initialized successfully
✅ [INFO] Retrieved 6 permits  
❌ [ERROR] Failed to initialize Google service: [details]
❌ [ERROR] Google service not initialized
```

## 🚀 Performance Issues

### 1. **Slow API Responses**

**Causes**:
- Large Google Sheets data
- Network latency to Google APIs
- Cold start delays

**Solutions**:
- Implement caching for permit data
- Use async operations for concurrent requests
- Consider pagination for large datasets

### 2. **Memory Issues**

**Monitoring**:
```bash
# Check service metrics in Render dashboard
# Look for memory usage trends
```

**Solutions**:
- Optimize data processing
- Clear large variables after use
- Consider upgrading Render plan

## 🔄 Deployment Issues

### 1. **Build Failures**

**Common Causes**:
- Missing dependencies in requirements.txt
- Python version compatibility
- Import errors

**Solutions**:
```bash
# Check build logs in Render
# Verify all dependencies are listed
pip freeze > requirements.txt
```

### 2. **Startup Failures**

**Check**:
- Port configuration (should be 10000)
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
- Environment variables are all set

### 3. **502 Bad Gateway**

**Causes**:
- Service not starting properly
- Port conflicts
- Startup timeout

**Solutions**:
- Check application logs
- Verify health endpoint responds
- Restart service in Render dashboard

## 📊 Monitoring & Alerts

### 1. **Set Up Monitoring**

```bash
# Regular health checks
curl https://houserenoai.onrender.com/health

# Monitor response times
curl -w "@curl-format.txt" https://houserenoai.onrender.com/v1/permits/

# Check Google Sheets connectivity
curl https://houserenoai.onrender.com/debug/
```

### 2. **Key Metrics to Monitor**

- API response times
- Google service initialization status
- Error rates
- Memory/CPU usage
- Google API quota usage

## 🆘 Emergency Procedures

### 1. **Service Down**

1. **Check Render Status**: https://status.render.com
2. **Restart Service**: Render Dashboard → Deploy → Restart
3. **Check Logs**: Look for startup errors
4. **Verify Environment**: All variables still set

### 2. **Google API Issues**

1. **Check Google Cloud Status**: https://status.cloud.google.com
2. **Verify API Quotas**: Google Cloud Console → APIs
3. **Test Service Account**: Download new key if needed
4. **Re-share Google Sheet**: Ensure permissions intact

### 3. **OpenAI API Issues**

1. **Check OpenAI Status**: https://status.openai.com
2. **Verify API Key**: Platform usage dashboard
3. **Check Credits**: Ensure account has sufficient balance

## 📞 Support Contacts

### **Internal Support**
- **Developer**: Check logs and environment variables
- **Google Issues**: Verify service account and Sheet permissions
- **OpenAI Issues**: Check API key and usage limits

### **External Support**
- **Render Support**: https://render.com/docs
- **Google Cloud Support**: https://cloud.google.com/support
- **OpenAI Support**: https://help.openai.com

## 🔍 Advanced Debugging

### 1. **Local Development Setup**

```bash
# Clone and setup locally for debugging
git clone https://github.com/yourusername/house-renovators-ai.git
cd house-renovators-ai
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CREDENTIALS_B64="your_base64_credentials"
export OPENAI_API_KEY="your_api_key"
export SHEET_ID="your_sheet_id"

# Run locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. **Test Google Service Manually**

```python
# Test in Python REPL
import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Decode credentials
creds_b64 = "your_base64_string"
creds_json = base64.b64decode(creds_b64).decode('utf-8')
creds_dict = json.loads(creds_json)

# Create credentials
credentials = service_account.Credentials.from_service_account_info(creds_dict)

# Test Sheets API
service = build('sheets', 'v4', credentials=credentials)
sheet_id = "your_sheet_id"
result = service.spreadsheets().values().get(
    spreadsheetId=sheet_id, 
    range='A1:Z1000'
).execute()

print(f"Retrieved {len(result.get('values', []))} rows")
```

This troubleshooting guide covers all major issues and their solutions based on the successful implementation.