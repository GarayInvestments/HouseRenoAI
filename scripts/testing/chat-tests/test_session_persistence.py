"""
Test script to verify session persistence to Google Sheets
Tests that sessions survive backend restarts
"""

import asyncio
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services import google_service as google_service_module
from app.config import settings
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_session_persistence():
    """Test saving and loading sessions from Google Sheets"""
    
    print("\n" + "="*60)
    print("Testing Session Persistence to Google Sheets")
    print("="*60 + "\n")
    
    # Initialize Google service
    try:
        from app.main import initialize_google_service
        await initialize_google_service()
        google_service = google_service_module.google_service
        
        if not google_service:
            print("❌ Google service failed to initialize")
            return False
            
        print("✅ Google service initialized\n")
        
    except Exception as e:
        print(f"❌ Failed to initialize Google service: {e}")
        return False
    
    # Test 1: Save a new session
    print("Test 1: Save New Session")
    print("-" * 40)
    
    test_session_id = f"test_session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    session_data = {
        'session_id': test_session_id,
        'user_email': 'test@example.com',
        'title': 'Test Session - Persistence',
        'created_at': datetime.utcnow().isoformat(),
        'last_activity': datetime.utcnow().isoformat(),
        'message_count': 0
    }
    
    saved = await google_service.save_session(session_data)
    
    if saved:
        print(f"✅ Session saved: {test_session_id}")
        print(f"   Title: {session_data['title']}")
        print(f"   User: {session_data['user_email']}")
    else:
        print(f"❌ Failed to save session")
        return False
    
    print()
    
    # Test 2: Load the session back
    print("Test 2: Load Session")
    print("-" * 40)
    
    loaded = await google_service.load_session(test_session_id)
    
    if loaded:
        print(f"✅ Session loaded successfully")
        print(f"   Session ID: {loaded['session_id']}")
        print(f"   Title: {loaded['title']}")
        print(f"   User: {loaded['user_email']}")
        print(f"   Message Count: {loaded['message_count']}")
        
        # Verify data matches
        if loaded['session_id'] == test_session_id:
            print("   ✅ Session ID matches")
        else:
            print("   ❌ Session ID doesn't match")
            return False
            
    else:
        print(f"❌ Failed to load session")
        return False
    
    print()
    
    # Test 3: Update session (simulate message sent)
    print("Test 3: Update Session Activity")
    print("-" * 40)
    
    session_data['message_count'] = 5
    session_data['last_activity'] = datetime.utcnow().isoformat()
    
    updated = await google_service.save_session(session_data)
    
    if updated:
        print(f"✅ Session updated")
        
        # Load again to verify update
        loaded_again = await google_service.load_session(test_session_id)
        if loaded_again and loaded_again['message_count'] == 5:
            print(f"   ✅ Message count updated to: {loaded_again['message_count']}")
        else:
            print(f"   ❌ Message count not updated correctly")
            return False
    else:
        print(f"❌ Failed to update session")
        return False
    
    print()
    
    # Test 4: Load all sessions
    print("Test 4: Load All Sessions")
    print("-" * 40)
    
    all_sessions = await google_service.load_all_sessions()
    
    print(f"✅ Loaded {len(all_sessions)} total sessions from Sheets")
    
    # Find our test session
    found = False
    for session in all_sessions:
        if session['session_id'] == test_session_id:
            found = True
            print(f"   ✅ Test session found in list")
            break
    
    if not found:
        print(f"   ❌ Test session not found in list")
        return False
    
    print()
    
    # Test 5: Load sessions by user
    print("Test 5: Load Sessions by User")
    print("-" * 40)
    
    user_sessions = await google_service.load_all_sessions('test@example.com')
    
    print(f"✅ Loaded {len(user_sessions)} sessions for test@example.com")
    
    found_user_session = False
    for session in user_sessions:
        if session['session_id'] == test_session_id:
            found_user_session = True
            break
    
    if found_user_session:
        print(f"   ✅ Test session found in user filter")
    else:
        print(f"   ❌ Test session not found in user filter")
        return False
    
    print()
    
    # Test 6: Delete session
    print("Test 6: Delete Session")
    print("-" * 40)
    
    deleted = await google_service.delete_session(test_session_id)
    
    if deleted:
        print(f"✅ Session deleted successfully")
        
        # Verify it's gone
        loaded_deleted = await google_service.load_session(test_session_id)
        if loaded_deleted is None:
            print(f"   ✅ Session no longer exists")
        else:
            print(f"   ❌ Session still exists after deletion")
            return False
    else:
        print(f"❌ Failed to delete session")
        return False
    
    print()
    print("="*60)
    print("✅ All Tests Passed!")
    print("="*60)
    
    return True


if __name__ == "__main__":
    result = asyncio.run(test_session_persistence())
    sys.exit(0 if result else 1)
