# Client ID Automatic Lookup Feature

## Overview
Automatically matches Applicant Name and Email from uploaded documents to existing Client IDs in Google Sheets, with visual confirmation via tooltip.

## Implementation Details

### Backend Endpoint
**Route:** `GET /v1/clients/lookup?name={name}&email={email}`

**Parameters:**
- `name` (optional): Client name to search for
- `email` (optional): Client email to search for
- At least one parameter must be provided

**Matching Algorithm:**
1. **Exact Name Match**: +100 points
2. **Partial Name Match**: +70 points (substring match)
3. **Company Name Match**: +50 points
4. **Word Overlap**: +30 points per overlapping word
5. **Exact Email Match**: +100 points
6. **Email Domain Match**: +40 points (same @domain.com)

**Response:**
```json
{
  "client": { /* full client data */ },
  "confidence": 85,
  "matches": ["exact_name", "email_domain"],
  "client_id": "C-001",
  "full_name": "Ajay R Nair",
  "email": "ajay@2statescarolinas.com",
  "company": "2States Carolinas LLC",
  "phone": "704-555-0123"
}
```

**Confidence Threshold:**
- Only returns matches with confidence > 30%
- Returns `{ client: null, confidence: 0 }` if no good match

### Frontend Integration

**Auto-Lookup Flow:**
1. User uploads PDF document
2. AI extracts `Applicant Name` and `Applicant Email`
3. Frontend automatically calls `/v1/clients/lookup` with both fields
4. If match found (confidence > 30), auto-fills `Client ID` field
5. Shows green badge: "✓ Auto-matched (85%)"

**Visual Confirmation:**
- **Badge**: Green checkmark with confidence percentage
- **Tooltip on Hover**: Shows full client details
  - Client Full Name
  - Company Name
  - Email Address
  - Phone Number
  - Match Confidence

**User Control:**
- Client ID field is still editable
- User can change if auto-match is incorrect
- Tooltip helps verify the match is correct

## Field Mappings

### From PDF Document
- **Applicant Name** → Used for Client ID lookup (not stored in Projects sheet)
- **Applicant Email** → Used for Client ID lookup (not stored in Projects sheet)
- **Owner Name (PM's Client)** → Property owner, stored in Projects sheet

### Client Sheet Fields
The lookup checks multiple field name variations:
- `Full Name` / `Client Name` / `Name`
- `Email` / `Client Email`
- `Company` / `Client Company`
- `Phone` / `Client Phone`

## Example Scenarios

### Scenario 1: Exact Match
**Input:** 
- Name: "Ajay R Nair"
- Email: "ajay@2statescarolinas.com"

**Result:**
- Confidence: 200 (capped at 100)
- Client ID: C-012
- Badge: "✓ Auto-matched (100%)"

### Scenario 2: Partial Match
**Input:**
- Name: "Ajay Nair" (missing middle initial)
- Email: null

**Result:**
- Confidence: 70 (partial name match)
- Client ID: C-012
- Badge: "✓ Auto-matched (70%)"

### Scenario 3: No Match
**Input:**
- Name: "John Smith"
- Email: "john@example.com"

**Result:**
- Confidence: 0
- Client ID: (blank, user must select manually)
- No badge shown

## Files Modified

### Backend
- `app/routes/clients.py` - Added `/lookup` endpoint with fuzzy matching logic

### Frontend
- `frontend/src/lib/api.js` - Added `lookupClient(name, email)` method
- `frontend/src/pages/AIAssistant.jsx`:
  - Call lookup after document extraction
  - Store `clientLookup` data in message state
  - Render badge and tooltip for Client ID field
  - Hover state management

## Testing

### Test with Sample Document
Use `docs/Accela Citizen Access.pdf`:
- **Applicant:** Ajay R Nair (2States Carolinas LLC)
- **Owner:** Menon Prashanth
- **Expected:** Auto-match to Client ID based on "Ajay R Nair"

### Manual Testing
1. Upload a project PDF with Applicant info
2. Verify Client ID auto-fills
3. Hover over Client ID input to see tooltip
4. Confirm client name, email, company display correctly
5. Edit Client ID if needed

## Future Enhancements
- Handle "Client Not Found" → Offer to create new client
- Project ID format: Include project name (e.g., "P-001-Sandy-Bottom")
- Bulk upload with client matching
- Client deduplication tools
