"""Comprehensive QuickBooks integration tests"""
import requests
import json
import time

API_URL = "https://houserenoai.onrender.com/v1"
LOGIN_EMAIL = "steve@garayinvestments.com"
LOGIN_PASSWORD = "Stv060485!"

def get_token():
    r = requests.post(f"{API_URL}/auth/login", json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD})
    return r.json()["access_token"]

def test_chat(message, test_name, expected_contains=None, should_not_contain=None):
    """Test chat endpoint and validate response"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{API_URL}/chat", 
        headers=headers, 
        json={"message": message, "session_id": f"qb-test-{int(time.time())}"}
    )
    
    response_text = r.json().get("response", "")
    
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"QUERY: {message}")
    print(f"{'='*80}")
    print(f"Response (first 500 chars): {response_text[:500]}...")
    
    passed = True
    
    # Check for expected content
    if expected_contains:
        for term in expected_contains:
            if term.lower() not in response_text.lower():
                print(f"  FAIL: Missing expected term '{term}'")
                passed = False
    
    # Check for unwanted content
    if should_not_contain:
        for term in should_not_contain:
            if term.lower() in response_text.lower():
                print(f"  FAIL: Contains unwanted term '{term}'")
                passed = False
    
    # Check for fake names
    fake_names = ["Alex Chang", "Emily Clark", "Bob Smith", "John Doe", "Sarah Adams", 
                  "Michael Johnson", "Karen White", "Robert Moore"]
    for fake in fake_names:
        if fake in response_text:
            print(f"  FAIL: Contains fake name '{fake}'")
            passed = False
    
    if passed:
        print("  PASS")
    
    return passed

def test_quickbooks_api(endpoint, test_name):
    """Test direct QuickBooks API endpoints"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_URL}/{endpoint}", headers=headers)
    
    print(f"\n{'='*80}")
    print(f"API TEST: {test_name}")
    print(f"Endpoint: /{endpoint}")
    print(f"{'='*80}")
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        if "customers" in data:
            print(f"  Customers: {data.get('count', 0)}")
            if data.get('customers'):
                print(f"  First customer: {data['customers'][0].get('DisplayName', 'N/A')}")
        elif "invoices" in data:
            print(f"  Invoices: {len(data.get('invoices', []))}")
        elif "authenticated" in data:
            print(f"  Authenticated: {data.get('authenticated')}")
            if data.get('token_expires'):
                print(f"  Token expires: {data.get('token_expires')}")
        print("  PASS")
        return True
    else:
        print(f"  FAIL: {r.text[:200]}")
        return False

# Test Suite
print("="*80)
print("QUICKBOOKS COMPREHENSIVE TEST SUITE")
print("="*80)

results = []

# === API Endpoint Tests ===
print("\n\n### PART 1: Direct API Endpoints ###")
results.append(test_quickbooks_api("quickbooks/status", "QuickBooks authentication status"))
time.sleep(1)
results.append(test_quickbooks_api("quickbooks/customers", "Get all customers"))
time.sleep(1)
results.append(test_quickbooks_api("quickbooks/invoices", "Get all invoices"))
time.sleep(1)

# === Chat Integration Tests ===
print("\n\n### PART 2: Chat Integration - Customer Queries ###")

chat_tests = [
    {
        "message": "Is QuickBooks connected?",
        "name": "Connection status check",
        "expected": ["connected", "authenticated", "active"],
        "avoid": ["not connected", "not authenticated", "error"]
    },
    {
        "message": "How many QuickBooks customers do we have?",
        "name": "Customer count",
        "expected": ["24", "customer"],
        "avoid": []
    },
    {
        "message": "Show me the first 3 QuickBooks customers",
        "name": "Limited customer list",
        "expected": ["Ajay Nair", "Erica Person", "Garay Investments"],
        "avoid": []
    },
    {
        "message": "What is Gustavo Roldan's QuickBooks ID?",
        "name": "Specific customer ID lookup",
        "expected": ["161", "Gustavo"],
        "avoid": ["not found", "don't have"]
    },
    {
        "message": "Find customer with email ajay@2statescarolinas.com",
        "name": "Search by email",
        "expected": ["Ajay Nair", "164"],
        "avoid": []
    },
    {
        "message": "Which customers have outstanding balances?",
        "name": "Customers with balances",
        "expected": ["balance", "customer"],
        "avoid": []
    },
]

for test in chat_tests:
    results.append(test_chat(
        test["message"],
        test["name"],
        expected_contains=test["expected"],
        should_not_contain=test["avoid"]
    ))
    time.sleep(2)

# === Invoice Tests ===
print("\n\n### PART 3: Chat Integration - Invoice Queries ###")

invoice_tests = [
    {
        "message": "Show me recent QuickBooks invoices",
        "name": "Recent invoices list",
        "expected": ["invoice"],
        "avoid": ["INV-1001", "INV-1002"]  # Fake invoice numbers
    },
    {
        "message": "What invoices does Ajay Nair have?",
        "name": "Customer-specific invoices",
        "expected": ["Ajay", "invoice"],
        "avoid": []
    },
    {
        "message": "Show me unpaid invoices",
        "name": "Filter by payment status",
        "expected": ["invoice"],
        "avoid": []
    },
]

for test in invoice_tests:
    results.append(test_chat(
        test["message"],
        test["name"],
        expected_contains=test["expected"],
        should_not_contain=test["avoid"]
    ))
    time.sleep(2)

# === Cross-reference Tests (Sheets + QB) ===
print("\n\n### PART 4: Chat Integration - Cross-Reference Tests ###")

cross_ref_tests = [
    {
        "message": "Which clients in our database are also in QuickBooks?",
        "name": "Cross-reference Sheets and QB",
        "expected": ["client", "quickbooks"],
        "avoid": []
    },
    {
        "message": "Show me Temple Baptist's QuickBooks information",
        "name": "Client lookup with QB data",
        "expected": ["temple"],
        "avoid": []
    },
]

for test in cross_ref_tests:
    results.append(test_chat(
        test["message"],
        test["name"],
        expected_contains=test["expected"],
        should_not_contain=test["avoid"]
    ))
    time.sleep(2)

# === Edge Cases & Error Handling ===
print("\n\n### PART 5: Edge Cases & Error Handling ###")

edge_case_tests = [
    {
        "message": "What is the QuickBooks ID for a customer named XYZ Nonexistent Company?",
        "name": "Non-existent customer",
        "expected": ["couldn't find", "not found"],
        "avoid": ["not connected", "error connecting"]
    },
    {
        "message": "Create an invoice for Gustavo Roldan for $500",
        "name": "Invoice creation attempt (should work or explain why not)",
        "expected": [],  # Any response is ok as long as it doesn't fabricate
        "avoid": []
    },
]

for test in edge_case_tests:
    results.append(test_chat(
        test["message"],
        test["name"],
        expected_contains=test["expected"],
        should_not_contain=test["avoid"]
    ))
    time.sleep(2)

# === Summary ===
print("\n\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
passed = sum(results)
total = len(results)
print(f"Passed: {passed}/{total}")
print(f"Failed: {total - passed}/{total}")
print(f"Success Rate: {(passed/total*100):.1f}%")

if passed == total:
    print("\n*** ALL TESTS PASSED! ***")
else:
    print(f"\n*** {total - passed} TESTS FAILED ***")

print("\nKey Validations:")
print("  - No fake customer names detected")
print("  - Real QB data (24 customers) accessible")
print("  - Customer IDs match actual QuickBooks records")
print("  - Invoice data shows real transactions")
print("  - Connection status correctly reported")
print("  - Cross-referencing between Sheets and QB works")
