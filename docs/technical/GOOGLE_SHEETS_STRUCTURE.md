# Google Sheets Structure Reference

## Overview
Complete structure of all tabs/sheets in the House Renovators Google Sheets database. This document serves as the single source of truth for column names, data types, and usage across all sheets.

**Last Updated:** November 10, 2025  
**Verification Status:** ✅ Clients & Projects verified via API | ⚠️ Other sheets inferred from code  
**Sheet ID:** (Stored in `SHEET_ID` environment variable)

---

## 📋 Projects Sheet (17 Columns)

**Range:** `Projects!A1:Q`  
**Purpose:** Track construction projects with permit oversight

| Col # | Column Name | Data Type | Required | Source | Notes |
|-------|------------|-----------|----------|---------|-------|
| 1 | Project ID | String (8-char hex) | ✅ Yes | Auto-generated | Format: `P-001`, `P-002`, etc. |
| 2 | Client ID | String (8-char hex) | ✅ Yes | Auto-matched | Links to Clients sheet |
| 3 | Project Name | String | ✅ Yes | PDF extraction | Short descriptive name |
| 4 | Project Address | String | ✅ Yes | PDF extraction | Full address with city, state, zip |
| 5 | City | String | ✅ Yes | PDF extraction | City name only |
| 6 | County | String | ⚠️ Optional | PDF extraction/inferred | e.g., "Cabarrus" |
| 7 | Jurisdiction | String | ⚠️ Optional | PDF extraction | Permit authority (e.g., "Cabarrus County") |
| 8 | Primary Inspector | String | ❌ No | Manual entry | Left blank initially |
| 9 | Owner Name (PM's Client) | String | ⚠️ Optional | PDF extraction | Property owner name |
| 10 | Project Type | String | ⚠️ Optional | PDF extraction | e.g., "Residential", "Commercial" |
| 11 | **HR PC Service Fee** | Number | ❌ No | Manual entry | **CRITICAL: Used for invoice amounts** |
| 12 | Start Date | Date (YYYY-MM-DD) | ⚠️ Optional | PDF extraction | Project/permit submission date |
| 13 | Status | String | ✅ Yes | Default: "Planning" | e.g., "Planning", "Active", "Complete" |
| 14 | Scope of Work | String (long) | ⚠️ Optional | PDF extraction | Project description |
| 15 | Project Cost (Materials + Labor) | Number | ⚠️ Optional | PDF extraction | **NOT for invoicing - budget only** |
| 16 | Photo Album | String (URL) | ❌ No | Manual entry | Link to photo storage |
| 17 | Notes | String (long) | ❌ No | Manual/AI | Additional project notes |

### Additional Fields (Not in standard 17 columns)
These may appear in extracted data but aren't standard columns:
- **Square Footage** - Building area
- **Parcel Number** - Tax parcel ID
- **Permit Record Number** - Official permit ID

### Critical Usage Notes:
- **Column 11 (HR PC Service Fee)**: Used for QuickBooks invoice amounts
- **Column 15 (Project Cost)**: For project budgeting, NOT for invoicing
- **Column 2 (Client ID)**: Links projects to clients (MUST match Clients sheet)
- **Column 4 (Project Address)**: Used for invoice numbering (e.g., "1105-Sandy-Bottom")

---

## 👥 Clients Sheet (11 Columns) ✅ VERIFIED

**Range:** `Clients!A1:K`  
**Purpose:** Store client/contractor contact information

| Col # | Column Name | Data Type | Required | Notes |
|-------|------------|-----------|----------|-------|
| 1 | Client ID | String (8-char hex) | ✅ Yes | Unique identifier (e.g., `08833ef5`, `6dd00ad4`) |
| 2 | Full Name | String | ✅ Yes | Client's full legal name |
| 3 | Address | String | ⚠️ Optional | Mailing/business address with full formatting |
| 4 | Status | String | ✅ Yes | e.g., "5. Active", "3. Intake Completed", "4. GCPC Completed" |
| 5 | Role | String | ⚠️ Optional | e.g., "Owner", "Project Manager" |
| 6 | Company Name | String | ⚠️ Optional | Business name if applicable |
| 7 | Phone | String (phone) | ⚠️ Optional | Contact phone number (no formatting) |
| 8 | **Email** | String (email) | ⚠️ Optional | **CRITICAL: Used for invoice delivery** |
| 9 | Notes | String (long) | ❌ No | Additional client notes |
| 10 | File Upload | String (URL) | ❌ No | Link to uploaded files |
| 11 | QBO Client ID | String | ⚠️ Optional | QuickBooks Online customer ID for sync |

### Validation Rules:
- **Client ID**: 8-character hex format (e.g., `08833ef5`)
- **Full Name**: Must not contain address markers (St, Ave, Dr, Ln, Rd)
- **Email**: Used for QuickBooks BillEmail field in invoices
- **Status**: Includes numeric prefix for sorting (e.g., "5. Active", "3. Intake Completed")

### Critical Usage Notes:
- **Column 8 (Email)**: Pulled for invoice creation to enable QuickBooks email delivery
- **Column 1 (Client ID)**: Links to Projects sheet Column 2
- **Column 2 (Full Name)**: Used for invoice customer name if QB customer not found
- **Column 11 (QBO Client ID)**: Links to QuickBooks customer records for sync operations

---

## 📄 Permits Sheet

**Range:** `Permits!A1:Z`  
**Purpose:** Track permit applications and status

| Col # | Column Name | Data Type | Required | Notes |
|-------|------------|-----------|----------|-------|
| 1 | Permit ID | String | ✅ Yes | Unique permit identifier |
| 2 | Project ID | String | ✅ Yes | Links to Projects sheet |
| 3 | Permit Type | String | ✅ Yes | e.g., "Building", "Electrical", "Plumbing" |
| 4 | Status | String | ✅ Yes | e.g., "Applied", "Approved", "Inspected" |
| 5 | Application Date | Date | ⚠️ Optional | When permit was applied for |
| 6 | Approval Date | Date | ⚠️ Optional | When permit was approved |
| 7 | Permit Number | String | ⚠️ Optional | Official permit number from jurisdiction |
| 8 | Notes | String (long) | ❌ No | Additional permit details |

---

## 🔐 Users Sheet

**Range:** `Users!A1:Z`  
**Purpose:** Store user authentication and authorization data

| Col # | Column Name | Data Type | Required | Notes |
|-------|------------|-----------|----------|-------|
| 1 | User ID | String | ✅ Yes | Unique user identifier |
| 2 | Email | String (email) | ✅ Yes | Login email (unique) |
| 3 | Name | String | ✅ Yes | User's display name |
| 4 | Password Hash | String (bcrypt) | ✅ Yes | Hashed password (never plaintext) |
| 5 | Role | String | ✅ Yes | e.g., "admin", "user", "viewer" |
| 6 | Status | String | ✅ Yes | e.g., "active", "inactive" |
| 7 | Created At | Timestamp | ✅ Yes | Account creation date |
| 8 | Last Login | Timestamp | ⚠️ Optional | Last successful login |

### Security Notes:
- **Password Hash**: Must be bcrypt hashed, never store plaintext
- **Email**: Used for login authentication (case-insensitive)
- **Role**: Controls access permissions in JWT tokens

---

## 💬 Sessions Sheet

**Range:** `Sessions!A1:Z`  
**Purpose:** Store AI chat conversation sessions

| Col # | Column Name | Data Type | Required | Notes |
|-------|------------|-----------|----------|-------|
| 1 | Session ID | String (UUID) | ✅ Yes | Unique session identifier |
| 2 | User Email | String (email) | ✅ Yes | User who owns the session |
| 3 | Title | String | ⚠️ Optional | Session title/summary |
| 4 | Created At | Timestamp | ✅ Yes | When session started |
| 5 | Last Activity | Timestamp | ✅ Yes | Last message timestamp |
| 6 | Message Count | Number | ✅ Yes | Total messages in session |
| 7 | Session Data | JSON String | ✅ Yes | Serialized conversation history |

### Usage Notes:
- **Session Data**: Contains full conversation history as JSON
- **Last Activity**: Updated on each message for cleanup purposes
- **Message Count**: Helps identify active vs stale sessions

---

## 🔑 QB_Tokens Sheet

**Range:** `QB_Tokens!A1:Z`  
**Purpose:** Store QuickBooks OAuth tokens (encrypted)

| Col # | Column Name | Data Type | Required | Notes |
|-------|------------|-----------|----------|-------|
| 1 | Token ID | String | ✅ Yes | Usually "production" or "sandbox" |
| 2 | Access Token | String (encrypted) | ✅ Yes | QuickBooks API access token |
| 3 | Refresh Token | String (encrypted) | ✅ Yes | Token for refreshing access |
| 4 | Realm ID | String | ✅ Yes | QuickBooks company ID |
| 5 | Expires At | Timestamp | ✅ Yes | When access token expires |
| 6 | Created At | Timestamp | ✅ Yes | When tokens were obtained |
| 7 | Updated At | Timestamp | ✅ Yes | Last token refresh |

### Security Notes:
- **Access Token**: Expires after 1 hour
- **Refresh Token**: Valid for 60 days
- **Realm ID**: QuickBooks company identifier (NOT sensitive)

---

## 📎 Documents Sheet

**Range:** `Documents!A1:Z`  
**Purpose:** Track uploaded documents and extraction status

| Col # | Column Name | Data Type | Required | Notes |
|-------|------------|-----------|----------|-------|
| 1 | Document ID | String | ✅ Yes | Unique document identifier |
| 2 | Project ID | String | ⚠️ Optional | Links to Projects sheet if associated |
| 3 | File Name | String | ✅ Yes | Original uploaded filename |
| 4 | File Path | String (URL) | ✅ Yes | Storage location/URL |
| 5 | Upload Date | Timestamp | ✅ Yes | When document was uploaded |
| 6 | Document Type | String | ⚠️ Optional | e.g., "Permit Application", "Invoice", "Photo" |
| 7 | Extraction Status | String | ⚠️ Optional | e.g., "Pending", "Extracted", "Failed" |
| 8 | Extracted Data | JSON String | ❌ No | AI-extracted fields (if applicable) |

---

## � Payments Sheet

**Range:** `Payments!A1:K`  
**Purpose:** Track invoice payments with QuickBooks sync

| Col # | Column Name | Data Type | Required | Source | Notes |
|-------|------------|-----------|----------|---------|-------|
| 1 | Payment ID | String (8-char hex) | ✅ Yes | Auto-generated | Format: `PAY-abc123` |
| 2 | Invoice ID | String | ⚠️ Optional | Manual/QB sync | QuickBooks invoice ID |
| 3 | Project ID | String | ⚠️ Optional | Linked from invoice | Links to Projects sheet |
| 4 | Client ID | String | ✅ Yes | Linked from invoice | Links to Clients sheet |
| 5 | Amount | Number | ✅ Yes | Manual/QB sync | Payment amount (no $ symbol) |
| 6 | Payment Date | Date (YYYY-MM-DD) | ✅ Yes | Manual/QB sync | When payment received |
| 7 | Payment Method | String | ✅ Yes | Manual/QB sync | e.g., "Zelle", "Check", "Credit Card" |
| 8 | Status | String | ✅ Yes | Default: "Pending" | "Pending", "Completed", "Failed", "Refunded" |
| 9 | QB Payment ID | String | ⚠️ Optional | QB sync only | QuickBooks Payment entity ID |
| 10 | Transaction ID | String | ⚠️ Optional | Manual entry | Zelle/check number reference |
| 11 | Notes | String (long) | ❌ No | Manual/AI | Additional payment details |

### Validation Rules:
- **Payment ID**: Unique, 8-char hex with `PAY-` prefix
- **Amount**: Must be positive number
- **Payment Method**: "Zelle", "Check", "Cash", "Credit Card", "ACH", "Other"
- **Status**: "Pending", "Completed", "Failed", "Refunded"
- **Client ID**: Must match existing client in Clients sheet

### Critical Usage Notes:
- **Column 9 (QB Payment ID)**: Links to QuickBooks Payment records
- **Column 4 (Client ID)**: Links payments to clients for tracking
- **Column 2 (Invoice ID)**: Links payments to specific QB invoices
- **Column 7 (Payment Method)**: "Zelle" for Zelle payments to steve@houserenovatorsllc.com

---

## �🔗 Relationships & Linking

### Primary Relationships
```
Clients (Client ID) ←→ Projects (Client ID)
Projects (Project ID) ←→ Permits (Project ID)
Projects (Project ID) ←→ Documents (Project ID)
Clients (Client ID) ←→ Payments (Client ID)
Users (Email) ←→ Sessions (User Email)
```

### QuickBooks Integration
```
Clients (Client ID) → Find QB Customer by name/email matching
Clients (QBO Client ID) → Direct QuickBooks customer link (preferred - faster)
Projects (HR PC Service Fee) → QuickBooks Invoice (Amount)
Projects (Project Address) → QuickBooks Invoice (DocNumber)
Clients (Email) → QuickBooks Invoice (BillEmail)
Payments (QB Payment ID) → QuickBooks Payment (Id)
Payments (Invoice ID) → QuickBooks Invoice (Id)
```

**Note:** Always check for QBO Client ID first - it provides instant customer lookup without searching.

---

## 🎯 Common Data Access Patterns

### Syncing QuickBooks Payments to Sheets
1. Call QB API: `GET /payment?start_date=YYYY-MM-DD`
2. For each QB Payment:
   - Extract: QB Payment ID, Customer ID, Total Amount, Payment Date, Payment Method
   - Find linked Invoice ID from Payment.Line.LinkedTxn
   - Resolve Customer ID → Client ID using Clients sheet QBO Client ID
   - Generate Payment ID or update existing by QB Payment ID
3. Insert/Update row in Payments sheet
4. Return sync summary (new, updated, total)

### Creating Invoice from Project (Optimized)
1. Get Project → Read Columns 2 (Client ID), 4 (Address), 11 (HR PC Service Fee)
2. Get Client → Read Column 11 (QBO Client ID) using Client ID from step 1
   - **If QBO Client ID exists:** Use it directly (skip step 3)
   - **If QBO Client ID missing:** Read Column 8 (Email) and Column 2 (Full Name) for matching
3. Find QB Customer (only if no QBO Client ID):
   - Match by QBO Client ID (instant) OR
   - Search by Full Name/Email (slower)
4. Create Invoice → Use QB Customer ID, HR PC Service Fee, Email (Column 8), Address

**Performance:** Using QBO Client ID eliminates customer search, reducing API calls by ~80%.

### Checking Payment Status
1. User asks: "Has [Client] paid their invoice?"
2. Find Client ID from Clients sheet
3. Query Payments sheet for matching Client ID
4. Check Status column (Completed, Pending, etc.)
5. Show payment details (Amount, Date, Method)

### Project-Client Lookup
1. User asks about client → Find in Clients sheet Column 2 (Full Name)
2. Get Client ID from Column 1
3. Search Projects sheet Column 2 for matching Client ID
4. Return all matching projects

### Document to Project Linking
1. Upload document → Extract project data
2. Match "Applicant Name" + "Applicant Email" → Find Client ID in Clients sheet
3. Use Client ID to link to existing or create new Project
4. Store document reference in Documents sheet with Project ID

---

## 📊 Data Validation Rules

### ID Formats
- **Client ID**: 8-character lowercase hex (e.g., `abc12345`) or custom format
- **Project ID**: Sequential with prefix (e.g., `P-001`, `P-002`)
- **Session ID**: UUID v4 format
- **Document ID**: UUID v4 or custom format

### Required Field Validation
- **Projects**: Must have Project ID, Client ID, Project Name, Address, Status
- **Clients**: Must have Client ID, Full Name, Status
- **Users**: Must have unique Email, Password Hash, Role

### Data Type Validation
- **Dates**: YYYY-MM-DD format preferred
- **Timestamps**: ISO 8601 format
- **Numbers**: Numeric only, no currency symbols
- **Emails**: Valid email format with @ symbol
- **Phone**: String format (allows various formats)

---

## 🔧 Code References

### Where These Structures Are Used

**Context Builder** (`app/utils/context_builder.py`):
- Loads Projects, Clients for AI context
- Critical columns: Client ID, Project Address, HR PC Service Fee

**OpenAI Service** (`app/services/openai_service.py`):
- Formats data for AI display
- References all Client and Project columns

**Google Service** (`app/services/google_service.py`):
- CRUD operations on all sheets
- Validates column existence before write operations

**AI Functions** (`app/handlers/ai_functions.py`):
- Creates invoices using Projects columns 4, 11 and Clients column 6
- Updates records across all sheets

---

## ⚠️ Critical Notes for Developers

1. **HR PC Service Fee vs Project Cost**:
   - Column 11 (HR PC Service Fee) = Invoice amount
   - Column 15 (Project Cost) = Project budget (NOT for invoicing)

2. **Client ID Linking**:
   - Projects Column 2 MUST match a Client ID in Clients Column 1
   - Used for finding client email and details

3. **Email for Invoicing**:
   - Clients Column 6 (Email) is pulled for QuickBooks invoice delivery
   - Optional but recommended for all clients

4. **Invoice Number Generation**:
   - Projects Column 4 (Project Address) is parsed for invoice numbering
   - Format: "1105 Sandy Bottom Dr" → "1105-Sandy-Bottom"

5. **Field Name Variations**:
   - Code handles multiple field name formats for backward compatibility
   - Example: `'Full Name'` or `'Name'` or `'Client Name'`
   - Always check code for `client.get()` fallback chains

---

## 📝 Change Log

### November 10, 2025 - Payments Sheet Added
- ✅ Added Payments sheet documentation (11 columns)
- ✅ Documented QB Payment sync integration
- ✅ Added payment tracking workflows
- ✅ Updated relationships to include Payments ←→ Clients/Invoices
- ✅ Added payment status checking pattern

### November 10, 2025 - VERIFIED WITH API
- ✅ Verified Clients sheet: 11 columns (added QBO Client ID, Notes, File Upload)
- ✅ Verified Projects sheet: 17 columns confirmed
- ✅ Corrected column order for Clients (Address is col 3, not col 8)
- ✅ Added actual Status format examples ("5. Active", "3. Intake Completed")
- ✅ Confirmed Client ID format (8-char hex without hyphens)
- Added HR PC Service Fee to Projects context
- Documented Email column usage for invoicing
- Added QuickBooks invoice integration fields

### Previous
- Initial structure documented in FIELD_MAPPING.md
- Project extraction fields defined
