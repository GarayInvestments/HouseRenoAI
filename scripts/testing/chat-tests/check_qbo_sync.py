"""Check if QBO_Client_ID was actually synced"""
import requests

BASE_URL = "https://houserenoai.onrender.com"

# Login
print("Logging in...")
login_response = requests.post(
    f"{BASE_URL}/v1/auth/login",
    json={"email": "test@houserenoai.com", "password": "TestPass123!"},
    timeout=10
)
token = login_response.json()["access_token"]
print("✅ Logged in\n")

# Get clients
print("Fetching clients...")
clients_response = requests.get(
    f"{BASE_URL}/v1/clients",
    headers={"Authorization": f"Bearer {token}"},
    timeout=30
)
clients = clients_response.json()
print(f"✅ Got {len(clients)} clients\n")

# Check QBO_Client_ID column
print("="*80)
print("QBO_Client_ID STATUS")
print("="*80)

synced = 0
not_synced = 0

for client in clients:
    name = client.get('Full Name') or client.get('Client Name') or 'Unknown'
    qbo_id = client.get('QBO_Client_ID') or client.get('QBO Client ID')
    
    if qbo_id and str(qbo_id).strip() and str(qbo_id) != 'nan':
        print(f"✅ {name}: QBO_Client_ID = {qbo_id}")
        synced += 1
    else:
        print(f"❌ {name}: QBO_Client_ID = NONE")
        not_synced += 1

print()
print("="*80)
print(f"SUMMARY: {synced} synced, {not_synced} not synced")
print("="*80)
