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

**Cause**: Extracted fields don't match Google Sheets column headers exactly

**Debugging Steps**:

1. **Check Render Logs** for detailed field information:
   ```
   [INFO] Creating project from extracted data
   [DEBUG] Received extracted_data keys: ['Project ID', 'Client ID', ...]
   [INFO] Projects headers: ['Project ID', 'Client ID', 'Project Name', ...]
   [WARNING] Fields not found in Projects headers: ['Square Footage', 'Parcel Number']
   ```

2. **Verify Google Sheets columns** match extracted fields:
   - **Projects sheet has 17 columns**:
     - Project ID, Client ID, Project Name, Address, City, State, Zip Code
     - Property Type, Square Footage (if added), Estimated Start Date, Estimated End Date
     - Actual Start Date, Actual End Date, Budget, Status, Notes, Last Updated
   
3. **Check field extraction** in backend logs:
   ```
   [DEBUG] Extracted data: {'Project ID': 'P-001', 'Client ID': 'C-123', ...}
   [INFO] Appending row with 17 values to Projects
   [DEBUG] Row values: ['P-001', 'C-123', 'Main St Renovation', ...]
   ```

4. **Common Issues**:
   - **Extra fields extracted** that don't exist in sheet (e.g., Parcel Number, Permit Record Number)
   - **Field name mismatches** (e.g., 'Full Name' vs 'Client Name')
   - **Missing required fields** (e.g., Project ID not generated)

**Solutions**:

- **Backend filters unwanted fields** before sending to Google Sheets
- **Extra fields are combined into Notes** field (Square Footage, Parcel Number, Permit Record Number)
- **Applicant fields** (Name, Company, Phone, Email) are used for Client ID lookup only, not saved to sheet

**Verify Fix**:
```bash
# Check logs show field filtering
curl https://houserenoai.onrender.com/v1/documents/create-from-extract \
  -F "document_type=project" \
  -F "extracted_data={...}" \
  | grep "WARNING.*Fields not found"

# Should show NO warnings about unmatched fields
```

**Enable Debug Logging** (if needed):
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