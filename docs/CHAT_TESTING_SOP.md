# Chat Testing SOP (Standard Operating Procedure)

**Last Updated:** November 9, 2025  
**Purpose:** Standard process for testing chat functionality after deployments, bug fixes, or new features

---

## 🎯 When to Test Chat

- After deploying bug fixes (especially AI hallucination issues)
- After adding new AI functions
- After QuickBooks/Google Sheets integration changes
- After system prompt modifications
- Before major production releases
- When investigating user-reported issues

---

## 🛠️ Testing Environment

### Prerequisites
1. **Production URL:** `https://houserenoai.onrender.com`
2. **Test Credentials:**
   - Email: `test@houserenoai.com`
   - Password: `TestPass123!`
   - *(Create if doesn't exist: See "Creating Test User" section)*

### Tools Needed
- Python 3.x with `requests` library
- PowerShell (for Render logs)
- Render CLI configured (`render` command)

---

## 📋 Standard Test Suite

### 1. **QuickBooks Customer Listing Test**

**Purpose:** Verify AI returns real QuickBooks data without hallucinating fake names

**Test Script:**
```python
import requests

BASE_URL = "https://houserenoai.onrender.com"

# Login
login = requests.post(
    f"{BASE_URL}/v1/auth/login",
    json={"email": "test@houserenoai.com", "password": "TestPass123!"},
    timeout=10
)
token = login.json()["access_token"]

# Test chat
response = requests.post(
    f"{BASE_URL}/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "message": "List all QuickBooks customers",
        "session_id": "test_qb_customers"
    },
    timeout=60
)

print(response.json()["response"])
```

**Expected Result:**
- Shows real QB customer names (e.g., Ajay Nair, Gustavo Roldan, Erica Person, etc.)
- No fake/generic names (e.g., John Doe, Emily Clark, Alex Chang, Sarah Johnson)
- Response references actual customer count from QuickBooks

**Check Logs For:**
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 50 --confirm -o text | Select-String -Pattern "hallucination|fake name|SYNC DEBUG" | Select-Object -Last 10
```

---

### 2. **QuickBooks Invoice Query Test**

**Purpose:** Verify AI returns real invoice data

**Test Command:**
```python
response = requests.post(
    f"{BASE_URL}/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "message": "Show me invoices for Ajay Nair",
        "session_id": "test_invoices"
    },
    timeout=60
)
print(response.json()["response"])
```

**Expected Result:**
- Shows real invoice numbers from QuickBooks
- Invoice amounts match actual data
- No fabricated invoice numbers (INV-1001, INV-1002, etc.)
- Customer ID 164 referenced (Ajay Nair's actual QB ID)

---

### 3. **Google Sheets Client Query Test**

**Purpose:** Verify AI retrieves and displays client data correctly

**Test Command:**
```python
response = requests.post(
    f"{BASE_URL}/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "message": "Show me all clients from the database",
        "session_id": "test_clients"
    },
    timeout=60
)
print(response.json()["response"])
```

**Expected Result:**
- Lists real client names from Google Sheets
- Shows correct client details (phone, email, address)
- No "Unnamed Client" entries (field mapping working)

---

### 4. **QuickBooks Sync Function Test**

**Purpose:** Verify sync function matches clients with QB customers

**Dry Run Test:**
```python
response = requests.post(
    f"{BASE_URL}/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "message": "Sync all clients with QuickBooks in dry run mode",
        "session_id": "test_sync_dry"
    },
    timeout=60
)
print(response.json()["response"])
```

**Expected Result:**
- Shows match count (e.g., "Matched: 6")
- Shows already synced count
- Shows not matched count
- No actual database updates (dry run)

**Actual Sync Test:**
```python
# First message
response = requests.post(
    f"{BASE_URL}/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "message": "Sync all clients with QuickBooks",
        "session_id": "test_sync_actual"
    },
    timeout=60
)
print(response.json()["response"])

# Confirmation (if AI asks)
response = requests.post(
    f"{BASE_URL}/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "message": "Yes, proceed",
        "session_id": "test_sync_actual"
    },
    timeout=60
)
print(response.json()["response"])
```

**Verify in Sheets:**
```python
clients = requests.get(
    f"{BASE_URL}/v1/clients",
    headers={"Authorization": f"Bearer {token}"},
    timeout=30
).json()

for client in clients:
    name = client.get('Full Name') or client.get('Client Name')
    qbo_id = client.get('QBO Client ID')
    status = "✅" if qbo_id else "❌"
    print(f"{status} {name}: QBO Client ID = {qbo_id or 'NONE'}")
```

**Expected Result:**
- QBO Client ID column populated for matched clients
- Logs show: `QB Sync: Matched X, Already synced Y, Not matched Z, Updated N`

---

### 5. **Context Loading Performance Test**

**Purpose:** Verify smart context loading is working efficiently

**Test Commands:**
```python
# Test 1: Should load NO context (greeting)
response = requests.post(
    f"{BASE_URL}/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={"message": "Hello", "session_id": "test_context_1"},
    timeout=60
)

# Test 2: Should load SHEETS only
response = requests.post(
    f"{BASE_URL}/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={"message": "Show me Temple project", "session_id": "test_context_2"},
    timeout=60
)

# Test 3: Should load SHEETS + QUICKBOOKS
response = requests.post(
    f"{BASE_URL}/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={"message": "Create invoice for Temple", "session_id": "test_context_3"},
    timeout=60
)
```

**Check Logs:**
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 50 --confirm -o text | Select-String -Pattern "Smart context loading" | Select-Object -Last 5
```

**Expected Log Output:**
- Test 1: `Smart context loading: {'none'} for message: 'Hello'`
- Test 2: `Smart context loading: {'sheets'} for message: 'Show me Temple project'`
- Test 3: `Smart context loading: {'sheets', 'quickbooks'} for message: 'Create invoice for Temple'`

---

### 6. **Token Usage Validation**

**Purpose:** Ensure responses aren't truncated due to token limits

**Check Logs:**
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 30 --confirm -o text | Select-String -Pattern "METRICS.*OpenAI" | Select-Object -Last 5
```

**Expected Log Output:**
```
[METRICS] OpenAI API - Prompt tokens: 3500, Completion tokens: 450, Total: 3950
```

**Validation Rules:**
- Completion tokens should be < 2000 (max_tokens limit)
- If completion tokens = 2000 exactly → Response likely truncated (INVESTIGATE)
- Prompt tokens typically 3000-5000 for full context
- Total tokens should be reasonable for operation

---

## 🔍 Log Monitoring

### Key Patterns to Search

**Hallucination Detection:**
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 100 --confirm -o text | Select-String -Pattern "hallucination|fake name|fabricated" -Context 2,2
```

**Function Execution:**
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 50 --confirm -o text | Select-String -Pattern "AI executed|Function call|SYNC DEBUG"
```

**Performance Metrics:**
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 30 --confirm -o text | Select-String -Pattern "TIMING|METRICS|Request completed"
```

**Errors:**
```powershell
render logs -r srv-d44ak76uk2gs73a3psig --limit 100 --confirm -o text | Select-String -Pattern "ERROR|CRITICAL|Exception" -Context 3,3
```

---

## 🚨 Known Issues & Troubleshooting

### Issue: "AI HALLUCINATION DETECTED"

**Symptoms:**
- Logs show: `AI HALLUCINATION DETECTED: Fabricated name found matching pattern...`
- Response blocked with error message

**Check:**
1. Is the name actually fake? Cross-reference with `qb_customers_actual.json`
2. Is the name in the fake patterns list? (`app/routes/chat.py` lines 103-110)
3. If legitimate customer, remove from fake patterns

**Fix:**
- Update fake name patterns in `chat.py`
- Commit and deploy

### Issue: Column Name Mismatch

**Symptoms:**
- Logs show: `WARNING: Field 'XYZ' not found in [Sheet] headers`
- Updates appear successful but data not in Sheets

**Check:**
```python
# Get actual column names from API
clients = requests.get(f"{BASE_URL}/v1/clients", headers={"Authorization": f"Bearer {token}"}).json()
print(list(clients[0].keys()))
```

**Common Mismatches:**
- `QBO_Client_ID` vs `QBO Client ID` (space vs underscore)
- `Full Name` vs `Client Name`
- `Client ID` vs `ID`

**Fix:**
- Update code to use correct column name (with spaces if needed)
- Use field fallbacks: `client.get('Full Name') or client.get('Client Name')`

### Issue: QuickBooks Not Authenticated

**Symptoms:**
- Logs show: `QuickBooks not authenticated`
- Chat responses say "QuickBooks connection not available"

**Fix:**
1. Check QB status: `curl https://houserenoai.onrender.com/v1/quickbooks/status`
2. If expired, re-authenticate: Navigate to `/v1/quickbooks/connect` in browser
3. Complete OAuth flow
4. Verify: Status should show `authenticated: true`

### Issue: Session Memory Not Persisting

**Symptoms:**
- AI forgets context between messages
- User says "show me their invoices" but AI doesn't know which client

**Check:**
- Verify same `session_id` used across messages
- Check TTL hasn't expired (default 10 minutes)

**Example:**
```python
# Message 1
response1 = requests.post(..., json={"message": "Show client Ajay Nair", "session_id": "test_123"})

# Message 2 (should remember Ajay)
response2 = requests.post(..., json={"message": "Show their invoices", "session_id": "test_123"})
```

---

## 📊 Pre-Deployment Checklist

Before deploying chat-related changes to production:

- [ ] Run full test suite (tests 1-6 above)
- [ ] Check for hallucination warnings in logs
- [ ] Verify token usage is within limits
- [ ] Test both dry-run and actual operations (if applicable)
- [ ] Verify field names match Google Sheets column names
- [ ] Check QuickBooks authentication status
- [ ] Review system prompt changes (if any)
- [ ] Test with multiple session IDs (parallel users)
- [ ] Verify cache invalidation after updates

---

## 🧪 Full Test Script Template

**File:** `test_chat_comprehensive.py`

```python
"""Comprehensive chat testing script"""
import requests
import time

BASE_URL = "https://houserenoai.onrender.com"
TEST_EMAIL = "test@houserenoai.com"
TEST_PASSWORD = "TestPass123!"

def login():
    """Get auth token"""
    response = requests.post(
        f"{BASE_URL}/v1/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        timeout=10
    )
    return response.json()["access_token"]

def test_chat(token, message, session_id):
    """Send chat message and return response"""
    response = requests.post(
        f"{BASE_URL}/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": message, "session_id": session_id},
        timeout=60
    )
    return response.json()["response"]

def main():
    print("="*80)
    print("COMPREHENSIVE CHAT TEST SUITE")
    print("="*80)
    print()
    
    # Login
    print("1. Authenticating...")
    token = login()
    print("✅ Logged in\n")
    
    # Test 1: QB Customers
    print("2. Testing QuickBooks customer listing...")
    response = test_chat(token, "List all QuickBooks customers", "test_qb_customers")
    print(f"Response: {response[:200]}...")
    print("✅ QB customers test complete\n")
    
    # Test 2: QB Invoices
    print("3. Testing QuickBooks invoice query...")
    response = test_chat(token, "Show me invoices for Ajay Nair", "test_invoices")
    print(f"Response: {response[:200]}...")
    print("✅ QB invoices test complete\n")
    
    # Test 3: Sheets Clients
    print("4. Testing Google Sheets client query...")
    response = test_chat(token, "Show me all clients from the database", "test_clients")
    print(f"Response: {response[:200]}...")
    print("✅ Sheets clients test complete\n")
    
    # Test 4: Sync Dry Run
    print("5. Testing QuickBooks sync (dry run)...")
    response = test_chat(token, "Sync all clients with QuickBooks in dry run mode", "test_sync")
    print(f"Response: {response}")
    print("✅ Sync dry run test complete\n")
    
    # Test 5: Context Loading
    print("6. Testing smart context loading...")
    test_chat(token, "Hello", "test_context_1")
    test_chat(token, "Show me Temple project", "test_context_2")
    test_chat(token, "Create invoice for Temple", "test_context_3")
    print("✅ Context loading test complete")
    print("   Check logs for 'Smart context loading' messages\n")
    
    print("="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)
    print()
    print("Next steps:")
    print("1. Check Render logs for hallucination warnings")
    print("2. Verify token usage with: render logs ... | Select-String 'METRICS'")
    print("3. Review 'Smart context loading' patterns")

if __name__ == "__main__":
    main()
```

**Run with:**
```powershell
python test_chat_comprehensive.py
```

---

## 📝 Creating Test User

If test user doesn't exist:

```powershell
# Via API
$body = @{
    email = 'test@houserenoai.com'
    password = 'TestPass123!'
    name = 'Test User'
} | ConvertTo-Json

curl -X POST "https://houserenoai.onrender.com/v1/auth/register" `
    -H "Content-Type: application/json" `
    -d $body
```

---

## 🎓 Best Practices

1. **Always test in production** after deploying chat changes
2. **Use descriptive session IDs** (e.g., `test_qb_customers_20251109`)
3. **Check logs immediately** after running tests
4. **Keep test scripts up to date** with new features
5. **Document new issues** in this SOP as discovered
6. **Use same test data** for consistency (Ajay Nair, Temple project, etc.)
7. **Test edge cases** (empty responses, long queries, special characters)

---

## 📚 Related Documentation

- **API Documentation:** `docs/API_DOCUMENTATION.md`
- **QuickBooks Integration:** `docs/QUICKBOOKS_INTEGRATION_COMPLETE.md`
- **Deployment Guide:** `docs/DEPLOYMENT.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`
- **Baseline Metrics:** `docs/BASELINE_METRICS.md`

---

## 🔄 Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-09 | 1.0 | Initial SOP created after QB sync feature deployment |

---

**Questions or Issues?**
- Check `docs/TROUBLESHOOTING.md`
- Review Render logs: `render logs -r srv-d44ak76uk2gs73a3psig --tail`
- Verify QuickBooks auth: `curl https://houserenoai.onrender.com/v1/quickbooks/status`
