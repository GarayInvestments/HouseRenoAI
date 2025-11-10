"""Test client mapping locally"""
import requests
import json

url = "http://localhost:8000/v1/chat/"
payload = {
    "message": "Show me how clients would map to QB without making changes",
    "session_id": "test_local_mapping"
}

print("Sending request to local backend...")
response = requests.post(url, json=payload)

print(f"\nStatus Code: {response.status_code}")
print(f"\nResponse:")
print(json.dumps(response.json(), indent=2))
