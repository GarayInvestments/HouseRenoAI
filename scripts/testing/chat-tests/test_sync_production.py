"""Test QuickBooks sync in production via chat API"""
import requests
import json
import sys

# Production API endpoint
BASE_URL = "https://houserenoai.onrender.com"
TEST_EMAIL = "test@houserenoai.com"
TEST_PASSWORD = "TestPass123!"

def test_sync_dry_run():
    """Test sync via chat with dry-run"""
    print("="*80)
    print("TESTING QUICKBOOKS CLIENT SYNC IN PRODUCTION - DRY RUN")
    print("="*80)
    print()
    
    # Login
    print("1. Logging in to production...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return False
        
        token = login_response.json()["access_token"]
        print("✅ Logged in successfully")
        print()
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test dry-run sync
    print("2. Testing dry-run sync (preview only)...")
    print("-"*80)
    print("Message: 'Sync all clients with QuickBooks in dry run mode'")
    print()
    
    try:
        chat_response = requests.post(
            f"{BASE_URL}/v1/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Sync all clients with QuickBooks in dry run mode",
                "session_id": "test_sync_prod_session"
            },
            timeout=60
        )
        
        if chat_response.status_code != 200:
            print(f"❌ Chat request failed: {chat_response.status_code}")
            print(chat_response.text)
            return False
        
        result = chat_response.json()
        print()
        print("AI RESPONSE:")
        print("="*80)
        print(result.get("response", "No response"))
        print()
        
        # Check if function was called
        if "function_call" in result:
            print("FUNCTION CALL DETECTED:")
            print(json.dumps(result["function_call"], indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def test_sync_actual():
    """Test actual sync via chat"""
    print()
    print("="*80)
    print("TESTING ACTUAL SYNC IN PRODUCTION - UPDATING DATABASE")
    print("="*80)
    print()
    
    # Login
    print("1. Logging in to production...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()["access_token"]
        print("✅ Logged in successfully")
        print()
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Actual sync
    print("2. Running actual sync (WILL UPDATE DATABASE)...")
    print("-"*80)
    print("Message: 'Sync all clients with QuickBooks'")
    print()
    
    try:
        chat_response = requests.post(
            f"{BASE_URL}/v1/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "Sync all clients with QuickBooks",
                "session_id": "test_sync_prod_session"
            },
            timeout=60
        )
        
        if chat_response.status_code != 200:
            print(f"❌ Chat request failed: {chat_response.status_code}")
            print(chat_response.text)
            return False
        
        result = chat_response.json()
        print()
        print("AI RESPONSE:")
        print("="*80)
        print(result.get("response", "No response"))
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

if __name__ == "__main__":
    print("⚠️  NOTE: Testing against PRODUCTION environment")
    print(f"URL: {BASE_URL}")
    print()
    
    # Check if production is reachable
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=10)
        if health.status_code != 200:
            print("❌ Production not responding")
            sys.exit(1)
        print("✅ Production is reachable")
        print()
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach production: {e}")
        sys.exit(1)
    
    # Run dry-run test
    success = test_sync_dry_run()
    
    if success:
        print()
        print("="*80)
        print("Dry run completed!")
        print()
        print("To run actual sync (update database), run:")
        print("  python test_sync_production.py --actual")
        print("="*80)
        
        # Check if --actual flag provided
        if "--actual" in sys.argv:
            print()
            input("⚠️  Press Enter to continue with actual sync (or Ctrl+C to cancel)...")
            test_sync_actual()
