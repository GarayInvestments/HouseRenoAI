"""
Test QuickBooks query() method
Tests the newly added query method for fetching payments
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.quickbooks_service import quickbooks_service
from datetime import datetime, timedelta


async def test_query():
    """Test QuickBooks query functionality"""
    
    print("=" * 60)
    print("Testing QuickBooks Query Method")
    print("=" * 60)
    
    # Check authentication
    print("\n1. Checking authentication...")
    if not quickbooks_service.is_authenticated():
        print("❌ Not authenticated. Please connect at /v1/quickbooks/auth")
        return
    
    status = quickbooks_service.get_status()
    print(f"✅ Authenticated")
    print(f"   Realm ID: {status['realm_id']}")
    print(f"   Environment: {status['environment']}")
    print(f"   Token expires: {status['access_token_expires_at']}")
    
    # Test 1: Query all payments (limited)
    print("\n2. Testing: SELECT * FROM Payment MAXRESULTS 5")
    try:
        query = "SELECT * FROM Payment MAXRESULTS 5"
        results = await quickbooks_service.query(query)
        print(f"✅ Query successful")
        print(f"   Found {len(results)} payments")
        
        if results:
            first = results[0]
            print(f"\n   Sample payment:")
            print(f"   - ID: {first.get('Id')}")
            print(f"   - Amount: ${first.get('TotalAmt')}")
            print(f"   - Date: {first.get('TxnDate')}")
            print(f"   - Customer: {first.get('CustomerRef', {}).get('name')}")
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    # Test 2: Query with date filter
    print("\n3. Testing: Delta query (last 30 days)")
    try:
        since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S%z")
        if not since.endswith(('Z', '+00:00', '-00:00')):
            since = since + "-00:00"
        
        query = f"SELECT * FROM Payment WHERE Metadata.LastUpdatedTime > '{since}' MAXRESULTS 10"
        print(f"   Query: {query}")
        results = await quickbooks_service.query(query)
        print(f"✅ Delta query successful")
        print(f"   Found {len(results)} payments modified in last 30 days")
    except Exception as e:
        print(f"❌ Delta query failed: {e}")
    
    # Test 3: Query by customer (if you have customer IDs)
    print("\n4. Testing: Query structure analysis")
    try:
        query = "SELECT * FROM Payment MAXRESULTS 1"
        results = await quickbooks_service.query(query)
        if results:
            print(f"✅ Payment object structure:")
            payment = results[0]
            print(f"   Keys: {list(payment.keys())}")
    except Exception as e:
        print(f"❌ Structure query failed: {e}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_query())
