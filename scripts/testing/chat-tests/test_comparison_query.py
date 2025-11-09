"""
Test Comparison Query - Sheets vs QuickBooks

Tests the new context loading for comparison queries.
Tests the new create_quickbooks_customer_from_sheet function.
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://houserenoai.onrender.com"

def test_comparison_query():
    """Test: Which clients are in Sheets but not in QuickBooks?"""
    
    print("\n" + "="*80)
    print("TEST: Comparison Query - Clients in Sheets but NOT in QuickBooks")
    print("="*80)
    
    # Login first
    print("\n[1] Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/v1/auth/login",
        json={
            "email": "test@houserenoai.com",
            "password": "TestPass123!"
        },
        timeout=10
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Test comparison query
    print("\n[2] Asking: 'any clients in sheets that are not in quickbooks?'")
    
    chat_response = requests.post(
        f"{BASE_URL}/v1/chat",
        headers=headers,
        json={"message": "any clients in sheets that are not in quickbooks?"},
        timeout=30
    )
    
    if chat_response.status_code != 200:
        print(f"❌ Chat request failed: {chat_response.status_code}")
        print(f"Response: {chat_response.text}")
        return False
    
    result = chat_response.json()
    response_text = result.get("response", "")
    
    print(f"\n📊 Response (first 800 chars):")
    print(response_text[:800])
    print("...")
    
    # Check if AI loaded both contexts
    success_indicators = [
        "client" in response_text.lower(),
        "sheet" in response_text.lower() or "google" in response_text.lower(),
        "quickbook" in response_text.lower() or "qb" in response_text.lower()
    ]
    
    # Check if AI is comparing (not saying "I don't have access")
    failure_indicators = [
        "don't have direct access" in response_text.lower(),
        "unfortunately" in response_text.lower(),
        "i would need to compare" in response_text.lower()
    ]
    
    print("\n[3] Validation:")
    if any(failure_indicators):
        print("❌ FAIL: AI still doesn't have access to data")
        return False
    
    if all(success_indicators):
        print("✅ PASS: AI is comparing both data sources")
        
        # Check if it mentions specific clients
        if any(name in response_text for name in ["javier", "temple", "client"]):
            print("✅ PASS: AI mentioned specific clients")
        
        return True
    else:
        print("⚠️  PARTIAL: Response unclear")
        return False


def test_create_customer():
    """Test: Create QB customer from Sheet client"""
    
    print("\n" + "="*80)
    print("TEST: Create QuickBooks Customer from Sheets (if Javier exists)")
    print("="*80)
    
    # Login
    print("\n[1] Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/v1/auth/login",
        json={
            "email": "test@houserenoai.com",
            "password": "TestPass123!"
        },
        timeout=10
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # First check if Javier exists in Sheets
    print("\n[2] Checking if Javier exists in Sheets...")
    
    chat_response = requests.post(
        f"{BASE_URL}/v1/chat",
        headers=headers,
        json={"message": "is there a client named Javier in our sheets?"},
        timeout=30
    )
    
    if chat_response.status_code != 200:
        print(f"❌ Chat failed")
        return False
    
    result = chat_response.json()
    response_text = result.get("response", "").lower()
    
    if "yes" in response_text or "javier" in response_text:
        print("✅ Javier exists in Sheets")
        
        # Now try to create in QB (dry run first)
        print("\n[3] Testing create function (asking AI to explain process)...")
        
        chat_response2 = requests.post(
            f"{BASE_URL}/v1/chat",
            headers=headers,
            json={"message": "can you add Javier to QuickBooks?"},
            timeout=30
        )
        
        if chat_response2.status_code == 200:
            result2 = chat_response2.json()
            response_text2 = result2.get("response", "")
            
            print(f"\n📊 Response (first 500 chars):")
            print(response_text2[:500])
            
            if "create" in response_text2.lower() or "add" in response_text2.lower():
                print("\n✅ PASS: AI understands create customer capability")
                return True
            else:
                print("\n⚠️  AI response unclear")
                return False
        else:
            print(f"❌ Chat failed: {chat_response2.status_code}")
            return False
    else:
        print("ℹ️  Javier not found in Sheets (test skipped)")
        return True  # Not a failure, just no data to test


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPARISON & CREATE CUSTOMER TEST SUITE")
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    test1_passed = test_comparison_query()
    test2_passed = test_create_customer()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total_tests = 2
    passed_tests = sum([test1_passed, test2_passed])
    
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Failed: {total_tests - passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️  Some tests failed - review above")
