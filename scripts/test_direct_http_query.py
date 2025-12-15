"""
Test QuickBooks Query using direct HTTP GET (bypassing SDK).
Following Intuit's exact specification.
"""
import asyncio
import sys
from pathlib import Path
import urllib.parse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.quickbooks_service import get_quickbooks_service
from app.db.session import AsyncSessionLocal
import httpx

async def test_direct_http_query():
    """Make direct HTTP GET requests to QB Query endpoint."""
    
    print("=" * 70)
    print("QUICKBOOKS DIRECT HTTP QUERY TEST")
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
        print(f"Access Token: {qb_service.access_token[:20]}...")
        
        # Base URL - use api_url_v3
        base_url = qb_service.qb_client.api_url_v3
        realm_id = qb_service.realm_id
        
        print(f"\nBase URL: {base_url}")
        print(f"Company ID: {realm_id}")
        
        # Test queries
        queries = [
            ("All customers", "SELECT * FROM Customer STARTPOSITION 1 MAXRESULTS 10"),
            ("Count customers", "SELECT COUNT(*) FROM Customer"),
            ("Customer 174", "SELECT * FROM Customer WHERE Id = '174'"),
            ("Active customers", "SELECT * FROM Customer WHERE Active = true STARTPOSITION 1 MAXRESULTS 10"),
        ]
        
        async with httpx.AsyncClient() as client:
            for idx, (description, sql) in enumerate(queries, 1):
                print(f"\n{'-'*70}")
                print(f"TEST {idx}: {description}")
                print(f"{'-'*70}")
                print(f"SQL: {sql}")
                
                # Encode query for URL
                encoded_query = urllib.parse.quote(sql)
                
                # Build URL with minorversion
                url = f"{base_url}/company/{realm_id}/query?query={encoded_query}&minorversion=75"
                
                print(f"URL: {url[:100]}...")
                
                # Headers
                headers = {
                    "Authorization": f"Bearer {qb_service.access_token}",
                    "Accept": "application/json",
                    "Content-Type": "text/plain"
                }
                
                try:
                    response = await client.get(url, headers=headers, timeout=30.0)
                    
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check for QueryResponse
                        if "QueryResponse" in data:
                            query_response = data["QueryResponse"]
                            
                            # Check for Customer data
                            if "Customer" in query_response:
                                customers = query_response["Customer"]
                                if isinstance(customers, list):
                                    print(f"✅ Found {len(customers)} customers")
                                    for customer in customers[:3]:
                                        cust_id = customer.get('Id')
                                        name = customer.get('DisplayName')
                                        cust_type = customer.get('CustomerTypeRef', {})
                                        cust_type_val = cust_type.get('value', 'None')
                                        print(f"   • {cust_id}: {name} (Type: {cust_type_val})")
                                else:
                                    print(f"✅ Found 1 customer: {customers.get('DisplayName')}")
                            else:
                                # Check for count
                                if "totalCount" in query_response:
                                    print(f"✅ Total count: {query_response['totalCount']}")
                                else:
                                    print(f"⚠️  Empty QueryResponse: {query_response}")
                        
                        # Check for Fault
                        elif "Fault" in data:
                            fault = data["Fault"]
                            print(f"❌ Fault: {fault}")
                        
                        else:
                            print(f"⚠️  Unexpected response structure: {list(data.keys())}")
                            
                    else:
                        print(f"❌ HTTP {response.status_code}")
                        print(f"Response: {response.text[:200]}")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
        
        print("\n" + "=" * 70)
        print("COMPARISON: Direct HTTP GET vs SDK query()")
        print("=" * 70)
        print("\nIf HTTP GET returns data but SDK returns 0:")
        print("• SDK is sending malformed requests")
        print("• Use direct HTTP for queries going forward")
        print("\nIf both return 0:")
        print("• Query permissions may be missing from OAuth token")
        print("• Re-authenticate with fresh OAuth flow")

if __name__ == "__main__":
    asyncio.run(test_direct_http_query())
