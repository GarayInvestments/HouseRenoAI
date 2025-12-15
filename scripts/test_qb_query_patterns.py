"""
Test different QuickBooks Query patterns to understand what works.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.quickbooks_service import get_quickbooks_service
from app.db.session import AsyncSessionLocal

async def test_query_patterns():
    """Try multiple query patterns to see what returns data."""
    
    print("=" * 70)
    print("QUICKBOOKS QUERY PATTERN TESTING")
    print("=" * 70)
    
    async with AsyncSessionLocal() as db:
        # Get QB service and load tokens
        print("\nLoading tokens from database...")
        qb_service = get_quickbooks_service(db)
        await qb_service.load_tokens_from_db()
        
        # Verify authentication
        if not qb_service.is_authenticated():
            print("❌ QuickBooks not authenticated")
            return
        
        print(f"Authentication: ✅ Yes")
        print(f"Realm ID: {qb_service.realm_id}")
        print(f"Environment: {qb_service.environment}")
        
        # Test patterns
        patterns = [
            # Basic queries
            ("All customers (no filter)", "SELECT * FROM Customer"),
            ("All customers with pagination", "SELECT * FROM Customer STARTPOSITION 1 MAXRESULTS 100"),
            ("Count customers", "SELECT COUNT(*) FROM Customer"),
            
            # Filter by Active status
            ("Active customers only", "SELECT * FROM Customer WHERE Active = true"),
            ("Active + pagination", "SELECT * FROM Customer WHERE Active = true STARTPOSITION 1 MAXRESULTS 100"),
            
            # Filter by specific ID
            ("Customer ID 174", "SELECT * FROM Customer WHERE Id = '174'"),
            ("Customer ID 161", "SELECT * FROM Customer WHERE Id = '161'"),
            
            # Multiple IDs with IN
            ("Multiple IDs (IN clause)", "SELECT * FROM Customer WHERE Id IN ('161', '174', '162')"),
            
            # Filter by DisplayName
            ("DisplayName exact match", "SELECT * FROM Customer WHERE DisplayName = 'Javier Martinez'"),
            ("DisplayName LIKE", "SELECT * FROM Customer WHERE DisplayName LIKE 'Javier%'"),
            
            # Filter by GivenName
            ("GivenName = 'Javier'", "SELECT * FROM Customer WHERE GivenName = 'Javier'"),
            
            # CustomerTypeRef attempts (we know these fail, but let's confirm)
            ("CustomerTypeRef direct", "SELECT * FROM Customer WHERE CustomerTypeRef = '698682'"),
            ("CustomerTypeRef.value", "SELECT * FROM Customer WHERE CustomerTypeRef.value = '698682'"),
            
            # Date filters
            ("Updated in last year", "SELECT * FROM Customer WHERE MetaData.LastUpdatedTime > '2024-01-01'"),
        ]
        
        for idx, (description, query) in enumerate(patterns, 1):
            print(f"\n{'-'*70}")
            print(f"TEST {idx}: {description}")
            print(f"{'-'*70}")
            print(f"Query: {query}")
            
            try:
                result = await qb_service.query(query)
                
                if isinstance(result, dict) and 'totalCount' in result:
                    # COUNT query
                    print(f"✅ Result: {result['totalCount']} customers")
                elif isinstance(result, list):
                    print(f"✅ Result: {len(result)} customers returned")
                    if result:
                        # Show first few
                        for customer in result[:3]:
                            cust_id = customer.get('Id')
                            name = customer.get('DisplayName')
                            active = customer.get('Active', 'Unknown')
                            cust_type = customer.get('CustomerTypeRef', {})
                            cust_type_val = cust_type.get('value', 'None') if isinstance(cust_type, dict) else 'None'
                            print(f"   • {cust_id}: {name} (Active: {active}, Type: {cust_type_val})")
                        if len(result) > 3:
                            print(f"   ... and {len(result) - 3} more")
                else:
                    print(f"⚠️  Unexpected result type: {type(result)}")
                    print(f"   {result}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                # Don't print full traceback for cleaner output
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print("\nIf all queries return 0 results but GET works, this confirms:")
        print("• QuickBooks Query endpoint has issues with this realm/token")
        print("• Data exists (proven by GET)")
        print("• Workaround: Use Customer.get(id) for known IDs")
        print("• For discovery: Query may be unreliable, consider alternate approaches")

if __name__ == "__main__":
    asyncio.run(test_query_patterns())
