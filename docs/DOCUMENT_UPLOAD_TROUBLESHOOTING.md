# Document Upload Troubleshooting

## Issue Overview
**Date**: November 4, 2025
**Status**: 🔴 Active Issue
**Endpoint**: `POST /v1/documents/extract`
**Error**: "Document upload failed: Error: AI returned invalid data format"

## Error Details

### Frontend Error Message
```
Document upload failed: Error: AI returned invalid data format
at w1.uploadDocument (index-DqkRHb6U.js:16:13829128)
at async P (index-DqkRHb6U.js:16:13138021)
```

### Backend Response
```
POST https://houserenoai.onrender.com/v1/documents/extract - 500 (Internal Server Error)
```

## Timeline of Events

1. **Initial Connection Issue** ✅ RESOLVED
   - Frontend was using `localhost:8000` instead of production backend
   - Fixed by adding `VITE_API_URL` to GitHub Actions build step
   - Frontend now successfully connects to `https://houserenoai.onrender.com`

2. **Current Upload Issue** 🔴 ACTIVE
   - File upload now reaches the backend (progress!)
   - Backend returns 500 error with "AI returned invalid data format"
   - Error occurs during AI processing/response parsing

## Error Analysis

### Error Location
Based on the error message "AI returned invalid data format":
- Error occurs in `app/routes/documents.py`
- Likely in the AI response parsing section
- Could be in either `process_with_gpt4_vision()` or `process_with_gpt4_text()` functions

### Recent Code Changes
**File**: `app/routes/documents.py`
**Previous Fix** (Commit: 9ac1e52):
- Fixed `process_with_gpt4_text()` function around line ~185
- Changed from `openai_service.get_completion(prompt)` to `openai_service.client.chat.completions.create()`
- Added proper error handling and null checks

### Possible Root Causes

1. **Invalid JSON Response from OpenAI**
   - OpenAI might be returning text that's not valid JSON
   - JSON parsing might be failing due to formatting issues

2. **Missing or Null Response**
   - Response might be None/null before parsing
   - Empty response from OpenAI API

3. **Response Format Mismatch**
   - Expected response structure doesn't match actual structure
   - Missing required fields in the parsed data

4. **Error Handling Issue**
   - Exception being caught but not properly logged
   - Generic error message hiding the actual issue

## Investigation Steps

### Step 1: Check Backend Logs
Need to verify what's actually happening in the backend:
- [ ] Check Render logs for the actual error
- [ ] Look for OpenAI API response details
- [ ] Check if error is in vision or text processing

### Step 2: Review Error Handling
Examine error handling in `documents.py`:
- [ ] Check if JSON parsing is wrapped in try/catch
- [ ] Verify error messages are descriptive
- [ ] Ensure all null checks are in place

### Step 3: Test OpenAI Response
Verify OpenAI API is returning expected format:
- [ ] Check if OpenAI response contains expected fields
- [ ] Verify JSON is valid before parsing
- [ ] Test with sample document

### Step 4: Review Response Processing
Check how responses are processed:
- [ ] Line ~185: `process_with_gpt4_text()` 
- [ ] Line ~228: `process_with_gpt4_vision()`
- [ ] Verify both functions handle errors consistently

## Code Sections to Review

### 1. OpenAI Response Parsing (Line ~185)
```python
def process_with_gpt4_text(text_content, document_type):
    # Check this section for JSON parsing
    # Look for json.loads() calls
    # Verify null checks on response
```

### 2. Vision Processing (Line ~228)
```python
def process_with_gpt4_vision(image_content, document_type):
    # Check this section for image processing
    # Verify response format handling
```

### 3. Main Extract Endpoint (Line ~30)
```python
@router.post("/extract")
async def extract_document_data(file, document_type, client_id):
    # Check error handling in main endpoint
    # Verify all exceptions are caught and logged
```

## Expected vs Actual Behavior

### Expected Flow
1. ✅ File uploaded from frontend
2. ✅ Request reaches backend
3. ❌ **[FAILING HERE]** AI processes document and returns structured data
4. ❌ Backend parses response and returns to frontend
5. ❌ Frontend displays extracted data

### Error Pattern
```
Frontend → Backend → OpenAI API → [Parse Response] → 500 Error
                                   ↑ Failing here
```

## Next Steps

### Immediate Actions
1. **Check Render Logs**
   - Go to Render dashboard
   - View backend logs for the failed request
   - Copy full error stack trace

2. **Review Response Parsing Code**
   - Read full `process_with_gpt4_text()` function
   - Check JSON parsing logic
   - Verify error handling

3. **Add Better Error Logging**
   - Log raw OpenAI response before parsing
   - Log specific JSON parsing errors
   - Include response content in error messages

### Code Improvements Needed
- [ ] Add try/catch around JSON parsing with detailed error message
- [ ] Log raw OpenAI response for debugging
- [ ] Return more specific error messages to frontend
- [ ] Add response validation before parsing
- [ ] Test with actual PDF and image files

## Test Files
Document types being tested:
- **File**: `Accela Citizen Access.pdf` (0.51 MB)
- **Type**: "Permit" document
- **Expected**: Should extract permit-related data

## Related Files
- `app/routes/documents.py` - Main document processing endpoint
- `app/services/openai_service.py` - OpenAI client wrapper
- `frontend/src/lib/api.js` - Frontend API client
- `frontend/src/pages/AIAssistant.jsx` - Upload UI component

## Environment
- **Backend**: Render.com (https://houserenoai.onrender.com)
- **Frontend**: Cloudflare Pages (https://house-renovators-ai-portal.pages.dev)
- **OpenAI Model**: GPT-4 Vision/Text
- **Python Version**: 3.13
- **FastAPI Version**: Check requirements.txt

## Workarounds
None currently available - this is a critical feature.

## Resolution Status
🔴 **UNRESOLVED** - Investigating backend error handling and OpenAI response parsing

---

## Code Review Findings

### Error Handling in `process_with_gpt4_text()` (Lines 180-210)
```python
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse AI response as JSON: {e}")
    raise HTTPException(status_code=500, detail="AI returned invalid data format")
    # ↑ This is the error message we're seeing!
```

**Issue**: When OpenAI returns text that can't be parsed as JSON, we get this generic error.

**The problem could be**:
1. OpenAI is returning markdown code blocks (```json ... ```)
2. OpenAI is adding explanatory text before/after the JSON
3. OpenAI response format doesn't match expected structure

### Error Handling in `process_with_gpt4_vision()` (Lines 240-283)
```python
# Extract JSON from response (might have markdown code blocks)
if "```json" in result:
    result = result.split("```json")[1].split("```")[0].strip()
elif "```" in result:
    result = result.split("```")[1].split("```")[0].strip()
```

**Good**: Vision processing already handles markdown code blocks!
**But**: Text processing (PDF) doesn't have this handling!

## Root Cause Hypothesis

**Most Likely**: `process_with_gpt4_text()` needs the same markdown code block handling that `process_with_gpt4_vision()` has.

The PDF processing function doesn't strip markdown code blocks, but the image processing does. OpenAI often returns JSON wrapped in markdown:

```
Here's the extracted data:

```json
{
  "Project Name": "Example Project",
  ...
}
```
```

## Recommended Fix

Add markdown code block stripping to `process_with_gpt4_text()` function (around line 200):

```python
# Before json.loads(), add:
content = response.choices[0].message.content
if not content:
    raise ValueError("AI returned empty response")

# Strip markdown code blocks (same logic as vision processing)
if "```json" in content:
    content = content.split("```json")[1].split("```")[0].strip()
elif "```" in content:
    content = content.split("```")[1].split("```")[0].strip()

extracted_data = json.loads(content)
```

## Update Log

### 2025-11-04 - Code Review Complete
- ✅ Identified error message: "AI returned invalid data format"
- ✅ Confirmed frontend-backend connection working
- ✅ Reviewed `process_with_gpt4_text()` function
- ✅ Found inconsistency: Vision processing strips markdown, text processing doesn't
- 🔧 **Fix Identified**: Add markdown stripping to PDF text processing
- ⏳ Next: Apply fix and test
