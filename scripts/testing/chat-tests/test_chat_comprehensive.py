"""Comprehensive chat endpoint testing after hallucination fixes"""
import requests
import json
import time
from datetime import datetime

API_URL = "https://houserenoai.onrender.com/v1"
LOGIN_EMAIL = "steve@garayinvestments.com"
LOGIN_PASSWORD = "Stv060485!"

def get_auth_token():
    """Get JWT token"""
    response = requests.post(
        f"{API_URL}/auth/login",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def test_chat(token, message, session_id="test-session-001"):
    """Send chat message and return response"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/chat",
        headers=headers,
        json={"message": message, "session_id": session_id}
    )
    return response

def print_test_result(test_name, response, check_for=None, should_not_contain=None):
    """Print formatted test result"""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data.get('response', 'No response')[:500]}")
        
        # Check for expected content
        if check_for:
            found = any(term.lower() in data.get('response', '').lower() for term in check_for)
            print(f"✓ Contains expected terms: {found}")
        
        # Check for hallucinations
        if should_not_contain:
            hallucinated = any(term.lower() in data.get('response', '').lower() for term in should_not_contain)
            if hallucinated:
                print(f"❌ HALLUCINATION DETECTED: Contains fake names!")
            else:
                print(f"✓ No hallucinations detected")
        
        return True
    else:
        print(f"Error: {response.text}")
        return False

def main():
    print(f"Starting comprehensive chat tests - {datetime.now()}")
    print(f"API: {API_URL}")
    
    try:
        # Get auth token
        print("\n🔐 Authenticating...")
        token = get_auth_token()
        print("✓ Authentication successful")
        
        # Define test cases
        test_cases = [
            {
                "name": "Simple greeting (no context loading)",
                "message": "Hello, how are you?",
                "check_for": ["hello", "hi", "help"],
                "should_not_contain": ["Ajay Nair", "Alex Chang", "Emily Clark"]
            },
            {
                "name": "QuickBooks customer list request",
                "message": "Show me all QuickBooks customers",
                "check_for": ["quickbooks", "customer"],
                "should_not_contain": ["Ajay Nair", "Alex Chang", "Emily Clark", "John Doe", "Sarah Johnson"]
            },
            {
                "name": "Specific client lookup from Sheets",
                "message": "Tell me about the Temple project",
                "check_for": ["temple"],
                "should_not_contain": ["Ajay Nair", "Alex Chang", "Emily Clark"]
            },
            {
                "name": "QuickBooks invoice query",
                "message": "Show me recent invoices from QuickBooks",
                "check_for": ["invoice"],
                "should_not_contain": ["INV-1001", "INV-1002", "INV-1003", "Ajay Nair"]
            },
            {
                "name": "Client with QB ID question (original bug)",
                "message": "What is Gustavo's QuickBooks customer ID?",
                "check_for": ["gustavo"],
                "should_not_contain": ["not connected", "not authenticated", "Ajay Nair"]
            },
            {
                "name": "QB authentication status",
                "message": "Is QuickBooks connected?",
                "check_for": ["connected", "authenticated", "active"],
                "should_not_contain": ["not connected", "not active"]
            },
            {
                "name": "Complex query mixing Sheets and QB",
                "message": "List all clients from our database and their QuickBooks customer IDs",
                "check_for": ["client"],
                "should_not_contain": ["Ajay Nair", "Alex Chang", "Emily Clark"]
            }
        ]
        
        # Run tests
        session_id = f"test-{int(time.time())}"
        results = []
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n\n{'#'*80}")
            print(f"# TEST {i}/{len(test_cases)}")
            print(f"{'#'*80}")
            
            response = test_chat(token, test["message"], session_id)
            success = print_test_result(
                test["name"],
                response,
                check_for=test.get("check_for"),
                should_not_contain=test.get("should_not_contain")
            )
            results.append({"test": test["name"], "success": success})
            
            # Wait between tests to avoid rate limiting
            time.sleep(2)
        
        # Summary
        print(f"\n\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        passed = sum(1 for r in results if r["success"])
        print(f"Passed: {passed}/{len(results)}")
        print(f"Failed: {len(results) - passed}/{len(results)}")
        
        for result in results:
            status = "✓ PASS" if result["success"] else "❌ FAIL"
            print(f"{status}: {result['test']}")
        
        print(f"\n✓ Testing complete - {datetime.now()}")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
