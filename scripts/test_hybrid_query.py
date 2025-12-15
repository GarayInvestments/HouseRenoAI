"""
Test hybrid query implementation after stress testing.

Validates:
1. CustomerTypeRef guard blocks invalid queries
2. COUNT routed to HTTP
3. Regular queries routed to SDK
4. Performance improvement visible in logs
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.quickbooks_service import QuickBooksService
from app.db.session import AsyncSessionLocal


async def test_hybrid_query():
    """Test hybrid query routing after implementation."""
    
    async with AsyncSessionLocal() as db:
        qb_service = QuickBooksService(db=db)
        
        print("=" * 80)
        print("HYBRID QUERY METHOD TEST")
        print("=" * 80)
        
        # Load tokens
        print("\n1. Loading tokens from database...")
        if not await qb_service.load_tokens_from_db():
            print("❌ Failed to load tokens")
            return
        print("✅ Tokens loaded")
        
        # Test 1: CustomerTypeRef guard (should fail)
        print("\n2. Testing CustomerTypeRef guard (should block)...")
        try:
            result = await qb_service.query(
                "SELECT * FROM Customer WHERE CustomerTypeRef = '698682'"
            )
            print("❌ Guard failed - query should have been blocked!")
        except ValueError as e:
            print(f"✅ Guard working - blocked with message:")
            print(f"   {str(e)[:100]}...")
        
        # Test 2: COUNT query (should route to HTTP)
        print("\n3. Testing COUNT query (should use HTTP)...")
        print("   Look for log: '[QB QUERY] Routing COUNT query to HTTP'")
        try:
            result = await qb_service.query("SELECT COUNT(*) FROM Customer")
            count = result.get("totalCount", 0)
            print(f"✅ COUNT query successful: {count} customers")
        except Exception as e:
            print(f"❌ COUNT query failed: {e}")
        
        # Test 3: Regular query (should route to SDK)
        print("\n4. Testing regular query (should use SDK)...")
        print("   Look for log: '[QB QUERY] Routing query to SDK'")
        try:
            result = await qb_service.query("SELECT * FROM Customer WHERE Active = true")
            print(f"✅ SDK query successful: {len(result)} active customers")
        except Exception as e:
            print(f"❌ SDK query failed: {e}")
        
        # Test 4: CustomerRef filter (now supported!)
        print("\n5. Testing CustomerRef filter (should work with SDK)...")
        try:
            result = await qb_service.query("SELECT * FROM Invoice WHERE CustomerRef = '161'")
            print(f"✅ CustomerRef filter successful: {len(result)} invoices found")
        except Exception as e:
            print(f"❌ CustomerRef filter failed: {e}")
        
        print("\n" + "=" * 80)
        print("HYBRID QUERY TEST COMPLETE")
        print("=" * 80)
        print("\nCheck logs above for:")
        print("  - CustomerTypeRef guard message")
        print("  - '[QB QUERY] Routing COUNT query to HTTP'")
        print("  - '[QB QUERY] Routing query to SDK'")
        print("  - '[METRICS]' performance logs")


if __name__ == "__main__":
    asyncio.run(test_hybrid_query())
