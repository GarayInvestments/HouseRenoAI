"""Inspect the exact prompt sent to OpenAI to understand hallucinations"""
import requests
import json

API_URL = "https://houserenoai.onrender.com/v1"
LOGIN_EMAIL = "steve@garayinvestments.com"
LOGIN_PASSWORD = "Stv060485!"

def get_auth_token():
    response = requests.post(
        f"{API_URL}/auth/login",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    )
    return response.json()["access_token"]

def test_problematic_query():
    """Test the query that triggers hallucinations"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # This query triggered the scanner
    message = "List the first 5 QuickBooks customers with their names and IDs"
    
    print(f"Testing query: {message}\n")
    
    response = requests.post(
        f"{API_URL}/chat",
        headers=headers,
        json={"message": message, "session_id": "diagnostic-001"}
    )
    
    print("Response:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_problematic_query()
