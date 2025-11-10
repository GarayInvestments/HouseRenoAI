"""Test GC Compliance filtering in PRODUCTION."""
import requests

PROD_URL = "https://api.houserenovatorsllc.com"

# Login
print("🔐 Logging in to production...")
login_response = requests.post(
    f"{PROD_URL}/v1/auth/login",
    json={
        "email": "steve@garayinvestments.com",
        "password": "Stv060485!"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Logged in successfully\n")

headers = {"Authorization": f"Bearer {token}"}

# Test 1: QB customer query
print("=" * 70)
print("TEST: QuickBooks Query (Should trigger GC Compliance filtering)")
print("=" * 70)

chat_response = requests.post(
    f"{PROD_URL}/v1/chat",
    headers=headers,
    json={
        "message": "Show me all QuickBooks customers",
        "session_id": "test_gc_prod_filtering"
    },
    timeout=30
)

if chat_response.status_code == 200:
    result = chat_response.json()
    print(f"\n✅ Response: {result['response'][:300]}...")
    print(f"\n📊 Check Render logs for:")
    print("  - '[QB CONTEXT] Filtered to X GC Compliance customers from Y total'")
    print("  - '[QB CONTEXT] Filtered to X GC Compliance invoices from Y total'")
else:
    print(f"❌ Failed: {chat_response.status_code}")
    print(chat_response.text)
