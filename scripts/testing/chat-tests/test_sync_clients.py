"""Test script for QuickBooks client sync functionality"""
import asyncio
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from app.handlers.ai_functions import handle_sync_quickbooks_clients
from app.services import google_service as google_service_module
from app.services import quickbooks_service as quickbooks_service_module
from app.memory.memory_manager import memory_manager
from app.config import settings

async def initialize_services():
    """Initialize Google and QuickBooks services"""
    print("Initializing services...")
    
    # Initialize Google Sheets service
    try:
        if not google_service_module.google_service:
            from app.services.google_service import GoogleService
            google_service_module.google_service = GoogleService()
        print("✅ Google Sheets service initialized")
    except Exception as e:
        print(f"❌ Google Sheets initialization failed: {e}")
        return False
    
    # Initialize QuickBooks service
    try:
        if not quickbooks_service_module.quickbooks_service.is_authenticated():
            print("⚠️  QuickBooks not authenticated")
            print("   Run backend server and navigate to: http://localhost:8000/v1/quickbooks/connect")
            return False
        print("✅ QuickBooks service authenticated")
    except Exception as e:
        print(f"❌ QuickBooks check failed: {e}")
        return False
    
    return True

async def test_sync_dry_run():
    """Test sync in dry-run mode (no changes)"""
    print("="*80)
    print("TESTING QUICKBOOKS CLIENT SYNC - DRY RUN MODE")
    print("="*80)
    print()
    
    # Get services
    google_service = google_service_module.google_service
    quickbooks_service = quickbooks_service_module.quickbooks_service
    
    if not google_service:
        print("❌ ERROR: Google Sheets service not initialized")
        print("Make sure .env file has GOOGLE_SERVICE_ACCOUNT_FILE and SHEET_ID")
        return
    
    if not quickbooks_service.is_authenticated():
        print("❌ ERROR: QuickBooks not authenticated")
        print("Run: http://localhost:8000/v1/quickbooks/connect")
        return
    
    print("✅ Services initialized")
    print()
    
    # Test dry run
    print("Testing DRY RUN (preview only, no changes)...")
    print("-"*80)
    
    result = await handle_sync_quickbooks_clients(
        {"dry_run": True},
        quickbooks_service,
        memory_manager,
        "test_session"
    )
    
    print()
    print("RESULT STATUS:", result.get("status"))
    print()
    print(result.get("details", "No details provided"))
    print()
    
    if "sync_stats" in result:
        print("="*80)
        print("DETAILED STATISTICS")
        print("="*80)
        stats = result["sync_stats"]
        print(f"✅ Matched: {stats.get('matched', 0)}")
        print(f"⏭️  Already Synced: {stats.get('already_synced', 0)}")
        print(f"❌ Not Matched: {stats.get('not_matched', 0)}")
        print(f"📝 Would Update: {stats.get('updated', 0)} records")
        print()
    
    # Show sample matches if available
    if "matched_clients" in result:
        print("="*80)
        print("SAMPLE MATCHES (first 5)")
        print("="*80)
        for i, match in enumerate(result["matched_clients"][:5], 1):
            print(f"{i}. {match['client_name']} → QB: {match['qb_name']} (ID: {match['qb_id']})")
        print()
    
    return result

async def test_sync_actual():
    """Test actual sync (makes changes)"""
    print()
    print("="*80)
    print("TESTING ACTUAL SYNC - UPDATING DATABASE")
    print("="*80)
    print()
    
    # Get services
    google_service = google_service_module.google_service
    quickbooks_service = quickbooks_service_module.quickbooks_service
    
    print("⚠️  WARNING: This will update the QBO_Client_ID column in Google Sheets!")
    print()
    
    result = await handle_sync_quickbooks_clients(
        {"dry_run": False},
        quickbooks_service,
        memory_manager,
        "test_session"
    )
    
    print()
    print("RESULT STATUS:", result.get("status"))
    print()
    print(result.get("details", "No details provided"))
    print()
    
    if "sync_stats" in result:
        print("="*80)
        print("ACTUAL SYNC RESULTS")
        print("="*80)
        stats = result["sync_stats"]
        print(f"✅ Matched: {stats.get('matched', 0)}")
        print(f"⏭️  Already Synced: {stats.get('already_synced', 0)}")
        print(f"❌ Not Matched: {stats.get('not_matched', 0)}")
        print(f"📝 UPDATED: {stats.get('updated', 0)} records in database")
        print()
    
    return result

if __name__ == "__main__":
    # Initialize services first
    if not asyncio.run(initialize_services()):
        print("\n❌ Service initialization failed. Exiting.")
        sys.exit(1)
    
    print()
    
    # Run dry run test
    result = asyncio.run(test_sync_dry_run())
    
    # Ask if user wants to run actual sync
    if result and result.get("status") == "success":
        print()
        print("="*80)
        print("Dry run completed successfully!")
        print("To run actual sync (update database), run:")
        print("  python test_sync_clients.py --actual")
        print("="*80)
        
        # Check if --actual flag provided
        if "--actual" in sys.argv:
            print()
            input("Press Enter to continue with actual sync (or Ctrl+C to cancel)...")
            asyncio.run(test_sync_actual())
