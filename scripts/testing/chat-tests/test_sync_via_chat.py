"""Test QuickBooks sync via chat API (requires backend running)"""
import requests
import json
import sys

# API endpoint
BASE_URL = "http://localhost:8000"

def test_sync_dry_run():
    """Test sync via chat with dry-run"""
    print("="*80)
    print("TESTING QUICKBOOKS CLIENT SYNC VIA CHAT API - DRY RUN")
    print("="*80)
    print()
    
    # First, need to login to get token
    print("1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/v1/auth/login",
        json={"email": "admin@houserenoai.com", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return False
    
    token = login_response.json()["access_token"]
    print("✅ Logged in successfully")
    print()
    
    # Test dry-run sync
    print("2. Testing dry-run sync (preview only)...")
    print("-"*80)
    
    chat_response = requests.post(
        f"{BASE_URL}/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "Sync all clients with QuickBooks in dry run mode",
            "session_id": "test_sync_session"
        }
    )
    
    if chat_response.status_code != 200:
        print(f"❌ Chat request failed: {chat_response.status_code}")
        print(chat_response.text)
        return False
    
    result = chat_response.json()
    print()
    print("RESPONSE:")
    print("="*80)
    print(result.get("response", "No response"))
    print()
    
    return True

def test_sync_actual():
    """Test actual sync via chat"""
    print()
    print("="*80)
    print("TESTING ACTUAL SYNC - UPDATING DATABASE")
    print("="*80)
    print()
    
    # Login
    print("1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/v1/auth/login",
        json={"email": "admin@houserenoai.com", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    print("✅ Logged in successfully")
    print()
    
    # Actual sync
    print("2. Running actual sync (WILL UPDATE DATABASE)...")
    print("-"*80)
    
    chat_response = requests.post(
        f"{BASE_URL}/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "Sync all clients with QuickBooks",
            "session_id": "test_sync_session"
        }
    )
    
    if chat_response.status_code != 200:
        print(f"❌ Chat request failed: {chat_response.status_code}")
        print(chat_response.text)
        return False
    
    result = chat_response.json()
    print()
    print("RESPONSE:")
    print("="*80)
    print(result.get("response", "No response"))
    print()
    
    return True

if __name__ == "__main__":
    print("⚠️  NOTE: Backend server must be running on http://localhost:8000")
    print()
    
    # Check if backend is running
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=2)
        if health.status_code != 200:
            print("❌ Backend not responding. Start with: uvicorn app.main:app --reload")
            sys.exit(1)
        print("✅ Backend is running")
        print()
    except requests.exceptions.RequestException:
        print("❌ Backend not running. Start with: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Run dry-run test
    success = test_sync_dry_run()
    
    if success:
        print()
        print("="*80)
        print("Dry run completed!")
        print()
        print("To run actual sync (update database), run:")
        print("  python test_sync_via_chat.py --actual")
        print("="*80)
        
        # Check if --actual flag provided
        if "--actual" in sys.argv:
            print()
            input("Press Enter to continue with actual sync (or Ctrl+C to cancel)...")
            test_sync_actual()
