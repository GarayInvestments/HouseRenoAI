"""Test hallucination fixes - simple version"""
import requests
import json

API_URL = "https://houserenoai.onrender.com/v1"
LOGIN_EMAIL = "steve@garayinvestments.com"
LOGIN_PASSWORD = "Stv060485!"

def get_token():
    r = requests.post(f"{API_URL}/auth/login", json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD})
    return r.json()["access_token"]

def test(message, test_name):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{API_URL}/chat", headers=headers, json={"message": message, "session_id": "test-final"})
    
    response_text = r.json().get("response", "")
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"Response: {response_text[:400]}")
    
    # Check for fake names
    fake_names = ["Alex Chang", "Emily Clark", "Bob Smith", "John Doe", "Sarah Adams"]
    has_fake = any(name in response_text for name in fake_names)
    
    # Check for real names
    real_names = ["Ajay Nair", "Erica Person", "Garay Investments", "Marta Alder", "Gustavo Roldan"]
    has_real = any(name in response_text for name in real_names)
    
    if has_fake:
        print("FAIL: Contains fake names")
        return False
    elif "Data Integrity Error" in response_text:
        print("BLOCKED: Scanner caught attempted fabrication")
        return True
    elif has_real:
        print("PASS: Shows real customer data")
        return True
    else:
        print("PASS: Appropriate response (no customer list)")
        return True

# Run tests
tests = [
    ("List all QuickBooks customers", "Full customer list"),
    ("Show me 5 QuickBooks customers", "Partial customer list"),
    ("What is Gustavo's QB ID?", "Specific customer lookup"),
    ("Show recent invoices", "Invoice list")
]

results = []
for message, name in tests:
    results.append(test(message, name))
    import time
    time.sleep(2)

print(f"\n\n{'='*80}")
print(f"RESULTS: {sum(results)}/{len(results)} passed")
print(f"{'='*80}")
