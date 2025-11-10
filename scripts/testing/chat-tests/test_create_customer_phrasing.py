"""
Test create customer function with various phrasings.

Tests different ways users might ask to create a QuickBooks customer.
Verifies that AI calls the function automatically without asking for details.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "https://houserenoai.onrender.com"
LOGIN_EMAIL = "test@houserenoai.com"
LOGIN_PASSWORD = "TestPass123!"

# Test phrases - different ways to ask
TEST_PHRASES = [
    "Create QuickBooks customer for Javier Martinez",
    "Add Javier Martinez to QuickBooks",
    "Create QB customer for Javier",
    "Add Javier to QB",
    "Can you create a QuickBooks customer for Javier Martinez?",
    "I need to add Javier Martinez as a QuickBooks customer",
]

def login():
    """Login and get access token."""
    response = requests.post(
        f"{API_BASE_URL}/v1/auth/login",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")

def send_chat_message(token, message, session_id="test-create-customer"):
    """Send a chat message and get response."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/v1/chat/",
        headers=headers,
        json={
            "message": message,
            "session_id": session_id
        }
    )
    
    return response

def check_response_quality(response_text):
    """Check if AI is calling the function vs asking for details."""
    response_lower = response_text.lower()
    
    # Bad patterns - AI asking for info that's already in Sheets
    bad_patterns = [
        "please provide",
        "provide me with",
        "need the following",
        "email address (optional)",
        "phone number (optional)",
        "any other relevant details"
    ]
    
    # Good patterns - AI showing data or calling function
    good_patterns = [
        "javier martinez",
        "tg building",
        "project manager",
        "828-721-0611",
        "tgbuilding6@gmail.com",
        "would you like me to",
        "shall i proceed",
        "confirm",
    ]
    
    asking_for_details = any(pattern in response_lower for pattern in bad_patterns)
    showing_details = any(pattern in response_lower for pattern in good_patterns)
    
    return {
        "asking_for_details": asking_for_details,
        "showing_details": showing_details,
        "quality": "GOOD" if showing_details and not asking_for_details else "BAD"
    }

def main():
    print("=" * 80)
    print("CREATE CUSTOMER FUNCTION - PHRASING TEST")
    print("=" * 80)
    print(f"Testing against: {API_BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Login
    print("[1] Logging in...")
    try:
        token = login()
        print("✅ Login successful\n")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    # Test each phrase
    results = []
    for i, phrase in enumerate(TEST_PHRASES, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/{len(TEST_PHRASES)}: \"{phrase}\"")
        print("=" * 80)
        
        # Use unique session ID for each test
        session_id = f"test-create-{i}-{int(time.time())}"
        
        try:
            print(f"[{i}.1] Sending message...")
            response = send_chat_message(token, phrase, session_id)
            
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get("response", "")
                
                print(f"✅ Response received ({len(response_text)} chars)")
                print()
                print("Response (first 500 chars):")
                print("-" * 80)
                print(response_text[:500])
                if len(response_text) > 500:
                    print("... (truncated)")
                print("-" * 80)
                print()
                
                # Analyze response quality
                quality = check_response_quality(response_text)
                
                print(f"[{i}.2] Analysis:")
                print(f"   - Asking for details: {quality['asking_for_details']}")
                print(f"   - Showing client data: {quality['showing_details']}")
                print(f"   - Quality: {quality['quality']}")
                
                if quality['quality'] == "GOOD":
                    print("   ✅ AI is calling function or showing data")
                else:
                    print("   ❌ AI is asking for details (should auto-call function)")
                
                results.append({
                    "phrase": phrase,
                    "quality": quality['quality'],
                    "asking_for_details": quality['asking_for_details'],
                    "showing_details": quality['showing_details']
                })
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                results.append({
                    "phrase": phrase,
                    "quality": "ERROR",
                    "asking_for_details": False,
                    "showing_details": False
                })
        
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "phrase": phrase,
                "quality": "ERROR",
                "asking_for_details": False,
                "showing_details": False
            })
        
        # Wait between tests to avoid rate limiting
        if i < len(TEST_PHRASES):
            print("\nWaiting 3 seconds before next test...")
            time.sleep(3)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    good_count = sum(1 for r in results if r['quality'] == 'GOOD')
    bad_count = sum(1 for r in results if r['quality'] == 'BAD')
    error_count = sum(1 for r in results if r['quality'] == 'ERROR')
    
    print(f"\nResults: {good_count}/{len(TEST_PHRASES)} tests passed")
    print(f"  ✅ Good: {good_count}")
    print(f"  ❌ Bad:  {bad_count}")
    print(f"  ⚠️  Error: {error_count}")
    print()
    
    print("Individual Results:")
    for i, result in enumerate(results, 1):
        icon = "✅" if result['quality'] == 'GOOD' else "❌"
        print(f"  {icon} Test {i}: {result['quality']}")
        print(f"     Phrase: \"{result['phrase']}\"")
        if result['asking_for_details']:
            print(f"     ⚠️  AI asked for details (should auto-call function)")
        if result['showing_details']:
            print(f"     ✅ AI showed client data")
        print()
    
    # Success criteria
    if good_count == len(TEST_PHRASES):
        print("✅ ALL TESTS PASSED - AI correctly calls function for all phrasings!")
    elif good_count >= len(TEST_PHRASES) * 0.8:
        print(f"⚠️  MOSTLY PASSED - {good_count}/{len(TEST_PHRASES)} tests passed (80%+)")
    else:
        print(f"❌ TESTS FAILED - Only {good_count}/{len(TEST_PHRASES)} passed")
        print("\nThe AI should automatically call the create customer function")
        print("and show client details from Sheets WITHOUT asking user for info.")

if __name__ == "__main__":
    main()
