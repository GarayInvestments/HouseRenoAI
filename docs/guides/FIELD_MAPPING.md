# Document Extraction Field Mapping

## Overview
This document explains exactly which fields are extracted from PDFs/images, which ones are saved to Google Sheets, and which ones are used only for Client ID lookup.

---

## Projects Sheet - Column Structure

Based on your Google Sheets Projects sheet (17 columns):

| Column # | Field Name | Source |
|----------|-----------|--------|
| 1 | Project ID | Auto-generated: `P-001`, `P-002`, etc. |
| 2 | Client ID | **Auto-matched** via Applicant Name/Email lookup |
| 3 | Project Name | Extracted from PDF |
| 4 | Project Address | Extracted from PDF |
| 5 | City | Extracted from PDF address |
| 6 | County | Extracted or inferred (e.g., "Cabarrus") |
| 7 | Jurisdiction | Extracted (e.g., "Cabarrus County") |
| 8 | Primary Inspector | ❌ **Left blank** (not in PDFs) |
| 9 | Owner Name (PM's Client) | Extracted from "Owner:" section in PDF |
| 10 | Project Type | Extracted (e.g., "Residential") |
| 11 | HR PC Service Fee | ❌ **Left blank** (not in PDFs) |
| 12 | Start Date | Extracted from application/submission date |
| 13 | Status | Default: "Planning" |
| 14 | Scope of Work | Extracted from project description |
| 15 | Project Cost (Materials + Labor) | Extracted from budget/cost field |
| 16 | Photo Album | ❌ **Left blank** (not in PDFs) |
| 17 | Notes | ❌ **Left blank** or combined extra info |

---

## AI Extraction Fields

### Fields Saved to Projects Sheet ✅

These are extracted AND written to Google Sheets:

```python
{
  "Project ID": "P-001",              # Auto-generated
  "Client ID": "C-012",               # Auto-matched from Applicant
  "Project Name": "1105-Sandy-Bottom_Sunroom",
  "Project Address": "1105 SANDY BOTTOM DR NW, CONCORD, NC 28027",
  "City": "Concord",
  "County": "Cabarrus",
  "Jurisdiction": "Cabarrus County",
  "Owner Name (PM's Client)": "Menon Prashanth",  # Property owner
  "Project Type": "Residential",
  "Start Date": "2025-11-03",
  "Status": "Planning",
  "Scope of Work": "Sunroom Extension to existing house and adding square footage",
  "Project Cost (Materials + Labor)": "85000",
  "Square Footage": "862",
  "Parcel Number": "46717413760000",
  "Permit Record Number": "PRB2025-02843"
}
```

### Fields Used for Lookup Only 🔍

These are extracted but **NOT saved to Projects sheet** (filtered out before saving):

```python
{
  "Applicant Name": "Ajay R Nair",              # Used to lookup Client ID
  "Applicant Company": "2States Carolinas LLC",  # Used to confirm match
  "Applicant Phone": "704-706-4549",             # Used to confirm match
  "Applicant Email": "ajay@2statescarolinas.com" # Used to lookup Client ID
}
```

**Why?** These fields don't exist in your Projects sheet. They're used to automatically find the matching Client ID via the `/v1/clients/lookup` endpoint, then discarded.

---

## Mapping Logic

### Step 1: AI Extraction
```
PDF Document → OpenAI GPT-4o → Extract ALL fields (including Applicant fields)
```

### Step 2: Client ID Lookup
```
Applicant Name + Email → /v1/clients/lookup → Match to Client ID
```

Example:
- Input: `"Ajay R Nair"` + `"ajay@2statescarolinas.com"`
- Lookup Result: `{ client_id: "C-012", confidence: 100 }`
- Action: Auto-fill `extracted_data['Client ID'] = "C-012"`

### Step 3: Filter Lookup-Only Fields
```python
# In create_record_from_extraction():
lookup_only_fields = ['Applicant Name', 'Applicant Company', 'Applicant Phone', 'Applicant Email']
for field in lookup_only_fields:
    extracted_data.pop(field, None)  # Remove before saving
```

### Step 4: Save to Google Sheets
```
Filtered Data → google_service.append_record('Projects', extracted_data)
```

Only fields that match Projects sheet columns are saved.

---

## Field Extraction Details

### Owner Name vs Applicant Name

**Owner Name (PM's Client)** - Column 9:
- Source: PDF "Owner:" section
- Example: "MENON PRASHANTH" → Normalized to "Menon Prashanth"
- Saved to: Projects sheet, Column 9
- Meaning: The property owner (your client's client)

**Applicant Name** - NOT in Projects sheet:
- Source: PDF "Applicant:" section  
- Example: "Ajay R Nair"
- Saved to: ❌ **Not saved** (used only for lookup)
- Meaning: The person managing the project (your actual client)

### City vs Jurisdiction vs County

**City** - Column 5:
- Source: Address line (e.g., "Concord, NC")
- Example: "Concord"

**County** - Column 6:
- Source: Inferred from address if not explicit
- Example: "Cabarrus"

**Jurisdiction** - Column 7:
- Source: Permit portal name in PDF
- Example: "Cabarrus County" (the actual permitting authority)

### Project Cost

**Project Cost (Materials + Labor)** - Column 15:
- Source: Budget/cost field in PDF
- Format: Number only (no $ or commas)
- Example: `85000` (not "$85,000")

---

## Example: Accela Citizen Access.pdf

### What Gets Extracted:
```json
{
  "Project Name": "1105-Sandy-Bottom_Sunroom",
  "Project Address": "1105 SANDY BOTTOM DR NW, CONCORD, NC 28027",
  "City": "Concord",
  "County": "Cabarrus",
  "Jurisdiction": "Cabarrus County",
  "Owner Name (PM's Client)": "Menon Prashanth",
  "Project Type": "Residential",
  "Project Cost (Materials + Labor)": "85000",
  "Scope of Work": "Sunroom Extension to existing house and adding square footage",
  "Square Footage": "862",
  "Parcel Number": "46717413760000",
  "Permit Record Number": "PRB2025-02843",
  "Start Date": "2025-11-03",
  "Status": "Planning",
  
  // These are extracted but removed before saving:
  "Applicant Name": "Ajay R Nair",
  "Applicant Company": "2States Carolinas LLC",
  "Applicant Phone": "704-706-4549",
  "Applicant Email": "ajay@2statescarolinas.com"
}
```

### What Gets Saved to Projects Sheet:
```json
{
  "Project ID": "P-001",  // Auto-generated
  "Client ID": "C-012",   // Auto-matched from "Ajay R Nair"
  "Project Name": "1105-Sandy-Bottom_Sunroom",
  "Project Address": "1105 SANDY BOTTOM DR NW, CONCORD, NC 28027",
  "City": "Concord",
  "County": "Cabarrus",
  "Jurisdiction": "Cabarrus County",
  // "Primary Inspector": "",  // Left blank
  "Owner Name (PM's Client)": "Menon Prashanth",
  "Project Type": "Residential",
  // "HR PC Service Fee": "",  // Left blank
  "Start Date": "2025-11-03",
  "Status": "Planning",
  "Scope of Work": "Sunroom Extension to existing house and adding square footage",
  "Project Cost (Materials + Labor)": "85000",
  // "Photo Album": "",  // Left blank
  "Square Footage": "862",
  "Parcel Number": "46717413760000",
  "Permit Record Number": "PRB2025-02843"
}
```

**Note:** Applicant fields are completely removed.

---

## Fields Left Blank

These columns in Projects sheet are left blank because they don't appear in permit PDFs:

1. **Primary Inspector** (Column 8) - Assigned later
2. **HR PC Service Fee** (Column 11) - Calculated/entered manually
3. **Photo Album** (Column 16) - Added later by PM

---

## Error Prevention

### Before This Fix:
- ❌ All extracted fields (including Applicant) sent to Google Sheets
- ❌ Sheets API error: "Unknown columns: Applicant Name, Applicant Company..."
- ❌ 422 Unprocessable Entity errors

### After This Fix:
- ✅ Applicant fields extracted for Client ID lookup
- ✅ Client ID auto-populated via lookup
- ✅ Applicant fields removed before saving
- ✅ Only valid Projects sheet columns sent to API
- ✅ No more 422 errors

---

## Code Location

**Extraction Logic:**
- File: `app/routes/documents.py`
- Function: `process_with_gpt4_text()` (lines 155-235)
- Function: `process_with_gpt4_vision()` (lines 238-310)

**Filtering Logic:**
- File: `app/routes/documents.py`
- Function: `create_record_from_extraction()` (lines 89-93)
- Code:
  ```python
  # Remove fields that were only for Client ID lookup
  lookup_only_fields = ['Applicant Name', 'Applicant Company', 'Applicant Phone', 'Applicant Email']
  for field in lookup_only_fields:
      extracted_data.pop(field, None)
  ```

**Client Lookup Logic:**
- File: `frontend/src/pages/AIAssistant.jsx`
- Function: `handleUploadDocument()` (lines 141-193)
- API Call: `api.lookupClient(applicantName, applicantEmail)`

---

## Summary

| Field Category | Extracted? | Saved to Sheets? | Purpose |
|----------------|-----------|------------------|---------|
| **Project Fields** | ✅ Yes | ✅ Yes | Core project data |
| **Owner Name** | ✅ Yes | ✅ Yes | Property owner (Column 9) |
| **Applicant Fields** | ✅ Yes | ❌ **No** | Client ID lookup only |
| **Client ID** | ✅ Auto-matched | ✅ Yes | From lookup result |
| **Blank Fields** | ❌ No | - | Left empty (Inspector, Fee, Photos) |

**Key Point:** Applicant fields are a "bridge" between the PDF and your Clients database. They help identify WHO the client is, but aren't stored in the Projects sheet because that information already exists in the Clients sheet.
