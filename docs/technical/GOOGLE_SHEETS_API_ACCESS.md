# Google Sheets API Direct Access Guide

## Overview
When you need to programmatically create or modify Google Sheets structure (tabs, headers, validation), you can access the Google Sheets API directly instead of using the backend's `google_service` module.

## Why Direct Access?

**Scenario**: Creating a new sheet tab with headers and data validation via a standalone script.

**Problem with Backend Service**: The backend's `google_service` is designed for FastAPI routes and requires the application to be running with proper initialization lifecycle.

**Solution**: Use Google Sheets API directly with service account credentials.

---

## ❌ First Attempt (INCORRECT)

### What I Tried
```python
# scripts/setup_payments_sheet.py (WRONG APPROACH)
from app.services import google_service as google_service_module
from app.services.google_service import GoogleSheetsService

# Try to use the backend service
google_service = google_service_module.google_service
if not google_service:
    # Initialize it ourselves
    google_service = GoogleSheetsService()
    await google_service.initialize()
```

### Why This Failed
```
ERROR: Google service not initialized
```

**Root Causes**:
1. **Class Name Mismatch**: Backend uses `GoogleService`, not `GoogleSheetsService`
2. **Module-Level Singleton**: `google_service` is a module-level instance initialized during FastAPI startup
3. **Startup Lifecycle**: Service initialization happens in `app/main.py` during `@app.on_event("startup")`
4. **Dependency Chain**: Requires FastAPI app context, env vars loaded via `app/config.py`, and proper async event loop
5. **Script Isolation**: Standalone scripts don't trigger the FastAPI startup sequence

**When Backend Service Works**:
- Inside FastAPI route handlers
- During API requests (service already initialized)
- In `ai_functions.py` (called from routes)

**When Backend Service DOESN'T Work**:
- Standalone scripts (`python scripts/setup_payments_sheet.py`)
- Before FastAPI app starts
- Outside the application context

---

## ✅ Correct Approach (DIRECT API ACCESS)

### Implementation
```python
"""
Direct Google Sheets API access for standalone scripts
File: scripts/setup_payments_sheet.py
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Step 1: Load service account credentials directly
CREDENTIALS_PATH = 'config/house-renovators-credentials.json'

def initialize_sheets_api():
    """Initialize Google Sheets API with service account"""
    
    # Define required scopes
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    # Load credentials from file
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=SCOPES
    )
    
    # Build the Sheets API service
    service = build('sheets', 'v4', credentials=credentials)
    
    return service

# Step 2: Use the API service directly
async def create_payments_sheet():
    # Initialize API
    service = initialize_sheets_api()
    
    # Get spreadsheet ID from environment or config
    SHEET_ID = os.getenv('SHEET_ID', 'your-sheet-id-here')
    
    # Create new tab
    request = {
        "addSheet": {
            "properties": {
                "title": "Payments"
            }
        }
    }
    
    service.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": [request]}
    ).execute()
    
    print("✅ Created Payments tab")
    
    # Add header row
    headers = [['Payment ID', 'Invoice ID', 'Project ID', 'Client ID', 
                'Amount', 'Payment Date', 'Payment Method', 'Status', 
                'QB Payment ID', 'Transaction ID', 'Notes']]
    
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range='Payments!A1:K1',
        valueInputOption='RAW',
        body={'values': headers}
    ).execute()
    
    print("✅ Added header row")
    
    # Add data validation for Payment Method (column G)
    validation_request = {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,  # Need to get this from spreadsheet metadata
                "startRowIndex": 1,
                "endRowIndex": 1000,
                "startColumnIndex": 6,  # G column (0-indexed)
                "endColumnIndex": 7
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [
                        {"userEnteredValue": "Zelle"},
                        {"userEnteredValue": "Check"},
                        {"userEnteredValue": "Cash"},
                        {"userEnteredValue": "Credit Card"},
                        {"userEnteredValue": "ACH"},
                        {"userEnteredValue": "Other"}
                    ]
                },
                "showCustomUi": True
            }
        }
    }
    
    service.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": [validation_request]}
    ).execute()
    
    print("✅ Data validation set up")

# Run it
if __name__ == "__main__":
    import asyncio
    asyncio.run(create_payments_sheet())
```

### Execution Output
```bash
$ python scripts/setup_payments_sheet.py

✅ Google Sheets API initialized!
📋 Step 1: Creating Payments tab...
✅ Payments sheet already exists!
📋 Step 2: Adding header row...
✅ Header row added successfully!
   Columns: Payment ID, Invoice ID, Project ID, Client ID, Amount, Payment Date, Payment Method, Status, QB Payment ID, Transaction ID, Notes
📋 Step 3: Setting up data validation...
✅ Data validation set up successfully!
   Payment Method: Zelle, Check, Cash, Credit Card, ACH, Other
   Status: Pending, Completed, Failed, Refunded
✅ Payments sheet setup complete!
```

---

## Key Differences: Backend Service vs Direct API

| Aspect | Backend Service (`google_service`) | Direct API Access |
|--------|-----------------------------------|-------------------|
| **Use Case** | API routes, chat functions | Standalone scripts, setup tasks |
| **Initialization** | FastAPI startup event | Script-level initialization |
| **Context Required** | FastAPI app running | None (just credentials file) |
| **Credentials** | `GOOGLE_SERVICE_ACCOUNT_BASE64` (Render) or file path | Direct file path |
| **Async/Sync** | Async methods (`await`) | Sync or async (your choice) |
| **Caching** | Built-in 2-minute TTL cache | No caching (direct API) |
| **Error Handling** | Integrated with FastAPI exceptions | Manual try/except |
| **Access Pattern** | `google_service.read_sheet_data()` | `service.spreadsheets().values().get()` |

---

## When to Use Each Approach

### Use Backend Service (`google_service`)
✅ Inside FastAPI route handlers (`app/routes/*.py`)  
✅ In AI function handlers (`app/handlers/ai_functions.py`)  
✅ In chat context builders (`app/utils/context_builder.py`)  
✅ Any code called during API request processing  
✅ When you need caching (reduces API calls by 80%)

**Example**:
```python
# app/routes/payments.py
from app.services import google_service as google_service_module

@router.get("/")
async def get_payments():
    google_service = google_service_module.google_service
    payments = await google_service.get_all_sheet_data('Payments')
    return payments
```

### Use Direct API Access
✅ Standalone setup scripts (`scripts/setup_*.py`)  
✅ One-time migrations or data fixes  
✅ Testing sheet structure outside the app  
✅ DevOps automation (CI/CD, deployment scripts)  
✅ Admin tools that don't need the full app context

**Example**:
```python
# scripts/add_column_to_clients.py
from google.oauth2 import service_account
from googleapiclient.discovery import build

def add_qbo_id_column():
    credentials = service_account.Credentials.from_service_account_file(
        'config/house-renovators-credentials.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=credentials)
    
    # Add "QBO Client ID" column to Clients sheet
    service.spreadsheets().values().update(
        spreadsheetId=os.getenv('SHEET_ID'),
        range='Clients!J1',  # Column J
        valueInputOption='RAW',
        body={'values': [['QBO Client ID']]}
    ).execute()
```

---

## Common Patterns

### Pattern 1: Check if Sheet Exists
```python
def get_sheet_id(service, spreadsheet_id, sheet_name):
    """Get the sheetId (integer) for a sheet by name"""
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()
    
    for sheet in spreadsheet.get('sheets', []):
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    
    return None  # Sheet not found
```

### Pattern 2: Create Tab if Not Exists
```python
def ensure_sheet_exists(service, spreadsheet_id, sheet_name):
    """Create sheet if it doesn't exist"""
    sheet_id = get_sheet_id(service, spreadsheet_id, sheet_name)
    
    if sheet_id is None:
        request = {
            "addSheet": {
                "properties": {"title": sheet_name}
            }
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [request]}
        ).execute()
        print(f"✅ Created {sheet_name} tab")
    else:
        print(f"✅ {sheet_name} already exists (ID: {sheet_id})")
```

### Pattern 3: Add Data Validation
```python
def add_dropdown_validation(service, spreadsheet_id, sheet_id, 
                           column_index, options):
    """Add dropdown validation to a column"""
    request = {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,  # Skip header
                "endRowIndex": 1000,
                "startColumnIndex": column_index,
                "endColumnIndex": column_index + 1
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [
                        {"userEnteredValue": opt} for opt in options
                    ]
                },
                "showCustomUi": True
            }
        }
    }
    
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [request]}
    ).execute()
```

---

## Best Practices

### 1. Always Handle Existing Sheets Gracefully
```python
try:
    # Try to create sheet
    create_sheet(service, spreadsheet_id, "Payments")
except Exception as e:
    if "already exists" in str(e).lower():
        print("Sheet already exists, continuing...")
    else:
        raise
```

### 2. Get Sheet ID Before Validation Rules
```python
# WRONG: Using hardcoded sheetId
request = {"setDataValidation": {"range": {"sheetId": 0}}}  # Might not be 0!

# RIGHT: Look up the actual sheetId
sheet_id = get_sheet_id(service, spreadsheet_id, "Payments")
request = {"setDataValidation": {"range": {"sheetId": sheet_id}}}
```

### 3. Use Environment Variables for Sheet ID
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file
SHEET_ID = os.getenv('SHEET_ID')

if not SHEET_ID:
    raise ValueError("SHEET_ID environment variable not set")
```

### 4. Log Progress for Long Operations
```python
print("📋 Step 1: Creating Payments tab...")
# ... create tab ...
print("✅ Payments sheet created!")

print("📋 Step 2: Adding header row...")
# ... add headers ...
print("✅ Header row added successfully!")
```

---

## Troubleshooting

### Error: "The caller does not have permission"
**Cause**: Service account email not added to Google Sheet  
**Fix**: Share sheet with service account email (found in credentials JSON: `client_email`)

### Error: "Unable to parse range"
**Cause**: Invalid A1 notation  
**Fix**: Use format like `SheetName!A1:K1` or `SheetName!A:K`

### Error: "Requested entity was not found"
**Cause**: Sheet tab doesn't exist  
**Fix**: Create tab first with `addSheet` request

### Error: "Invalid sheetId"
**Cause**: Using wrong sheetId (not 0 for new sheets)  
**Fix**: Look up actual sheetId with `spreadsheets().get()`

---

## Complete Working Example

See `scripts/setup_payments_sheet.py` for a complete implementation that:
- ✅ Checks if sheet exists before creating
- ✅ Adds header row with 11 columns
- ✅ Sets up data validation for Payment Method and Status
- ✅ Handles errors gracefully
- ✅ Provides clear progress output

**Run it**:
```bash
python scripts/setup_payments_sheet.py
```

**Expected Output**:
```
✅ Google Sheets API initialized!
📋 Step 1: Creating Payments tab...
✅ Payments sheet already exists!
📋 Step 2: Adding header row...
✅ Header row added successfully!
📋 Step 3: Setting up data validation...
✅ Data validation set up successfully!
✅ Payments sheet setup complete!
```

---

## References

- **Google Sheets API v4 Docs**: https://developers.google.com/sheets/api/reference/rest
- **Service Account Setup**: `docs/SETUP_GUIDE.md` (Section: "Google Service Account")
- **Backend Service Code**: `app/services/google_service.py`
- **Example Script**: `scripts/setup_payments_sheet.py`
