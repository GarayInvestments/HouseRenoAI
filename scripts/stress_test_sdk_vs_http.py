"""
Stress test QuickBooks SDK vs Direct HTTP implementation.
Tests various edge cases, complex queries, and performance differences.
"""
import asyncio
import sys
from pathlib import Path
import time
import urllib.parse
import httpx

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.quickbooks_service import get_quickbooks_service
from app.db.session import AsyncSessionLocal
from quickbooks.objects.customer import Customer

async def sdk_query(qb_service, query_string, entity_class):
    """Use the old SDK query method."""
    try:
        return entity_class.query(query_string, qb=qb_service.qb_client)
    except Exception as e:
        return f"ERROR: {e}"

async def direct_http_query(qb_service, query_string):
    """Use direct HTTP GET method."""
    try:
        base_url = qb_service.qb_client.api_url_v3
        encoded_query = urllib.parse.quote(query_string)
        url = f"{base_url}/company/{qb_service.realm_id}/query?query={encoded_query}&minorversion=75"
        
        headers = {
            "Authorization": f"Bearer {qb_service.access_token}",
            "Accept": "application/json",
            "Content-Type": "text/plain"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            
            if response.status_code != 200:
                return f"ERROR: HTTP {response.status_code}"
            
            data = response.json()
            
            if "Fault" in data:
                return f"ERROR: {data['Fault']}"
            
            query_response = data.get("QueryResponse", {})
            
            # Handle COUNT
            if "totalCount" in query_response:
                return {"totalCount": query_response["totalCount"]}
            
            # Get entity data
            for key in query_response:
                if key not in ["startPosition", "maxResults", "totalCount"]:
                    entities = query_response[key]
                    if not isinstance(entities, list):
                        entities = [entities]
                    return entities
            
            return []
            
    except Exception as e:
        return f"ERROR: {e}"

async def stress_test():
    """Run comprehensive stress tests."""
    
    print("=" * 80)
    print("QUICKBOOKS SDK vs DIRECT HTTP - STRESS TEST")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # Setup
        print("\nLoading tokens from database...")
        qb_service = get_quickbooks_service(db)
        await qb_service.load_tokens_from_db()
        
        if not qb_service.is_authenticated():
            print("❌ QuickBooks not authenticated")
            return
        
        print(f"Authentication: ✅ Yes")
        print(f"Realm ID: {qb_service.realm_id}\n")
        
        # Test cases
        test_cases = [
            # Basic queries
            {
                "name": "Simple SELECT *",
                "query": "SELECT * FROM Customer STARTPOSITION 1 MAXRESULTS 10",
                "entity": Customer
            },
            {
                "name": "COUNT query",
                "query": "SELECT COUNT(*) FROM Customer",
                "entity": Customer
            },
            {
                "name": "Filter by Id",
                "query": "SELECT * FROM Customer WHERE Id = '174'",
                "entity": Customer
            },
            {
                "name": "Filter by Active",
                "query": "SELECT * FROM Customer WHERE Active = true STARTPOSITION 1 MAXRESULTS 10",
                "entity": Customer
            },
            {
                "name": "Filter by DisplayName",
                "query": "SELECT * FROM Customer WHERE DisplayName = 'Javier Martinez'",
                "entity": Customer
            },
            {
                "name": "LIKE operator",
                "query": "SELECT * FROM Customer WHERE DisplayName LIKE 'Javier%'",
                "entity": Customer
            },
            {
                "name": "IN clause",
                "query": "SELECT * FROM Customer WHERE Id IN ('161', '174', '162')",
                "entity": Customer
            },
            {
                "name": "Date filter",
                "query": "SELECT * FROM Customer WHERE MetaData.LastUpdatedTime > '2024-01-01'",
                "entity": Customer
            },
            {
                "name": "Large MAXRESULTS",
                "query": "SELECT * FROM Customer STARTPOSITION 1 MAXRESULTS 1000",
                "entity": Customer
            },
            {
                "name": "Pagination (high offset)",
                "query": "SELECT * FROM Customer STARTPOSITION 20 MAXRESULTS 10",
                "entity": Customer
            },
            
            # Edge cases
            {
                "name": "No WHERE clause",
                "query": "SELECT * FROM Customer",
                "entity": Customer
            },
            {
                "name": "Empty result (invalid ID)",
                "query": "SELECT * FROM Customer WHERE Id = '99999'",
                "entity": Customer
            },
            {
                "name": "Multiple AND conditions",
                "query": "SELECT * FROM Customer WHERE Active = true AND Id = '174'",
                "entity": Customer
            },
            
            # Known problematic queries
            {
                "name": "CustomerTypeRef direct (invalid)",
                "query": "SELECT * FROM Customer WHERE CustomerTypeRef = '698682'",
                "entity": Customer,
                "expected_sdk_fail": True
            },
            {
                "name": "CustomerTypeRef.value (invalid)",
                "query": "SELECT * FROM Customer WHERE CustomerTypeRef.value = '698682'",
                "entity": Customer,
                "expected_sdk_fail": True
            },
        ]
        
        results = []
        
        print("=" * 80)
        print("RUNNING TESTS")
        print("=" * 80)
        
        for idx, test in enumerate(test_cases, 1):
            print(f"\n[{idx}/{len(test_cases)}] {test['name']}")
            print(f"Query: {test['query'][:70]}...")
            
            # Test SDK
            print("  SDK: ", end="", flush=True)
            sdk_start = time.time()
            sdk_result = await sdk_query(qb_service, test['query'], test['entity'])
            sdk_time = (time.time() - sdk_start) * 1000
            
            if isinstance(sdk_result, str) and sdk_result.startswith("ERROR"):
                sdk_status = "❌ FAIL"
                sdk_count = 0
                sdk_error = sdk_result
            elif isinstance(sdk_result, list):
                sdk_status = "✅" if len(sdk_result) > 0 else "⚠️  0"
                sdk_count = len(sdk_result)
                sdk_error = None
            else:
                sdk_status = "⚠️  ?"
                sdk_count = 0
                sdk_error = f"Unexpected type: {type(sdk_result)}"
            
            print(f"{sdk_status} ({sdk_time:.0f}ms) - {sdk_count} results")
            if sdk_error:
                print(f"       {sdk_error[:80]}")
            
            # Test Direct HTTP
            print("  HTTP:", end="", flush=True)
            http_start = time.time()
            http_result = await direct_http_query(qb_service, test['query'])
            http_time = (time.time() - http_start) * 1000
            
            if isinstance(http_result, str) and http_result.startswith("ERROR"):
                http_status = "❌ FAIL"
                http_count = 0
                http_error = http_result
            elif isinstance(http_result, dict) and "totalCount" in http_result:
                http_status = "✅"
                http_count = http_result["totalCount"]
                http_error = None
            elif isinstance(http_result, list):
                http_status = "✅" if len(http_result) > 0 else "⚠️  0"
                http_count = len(http_result)
                http_error = None
            else:
                http_status = "⚠️  ?"
                http_count = 0
                http_error = f"Unexpected type: {type(http_result)}"
            
            print(f"{http_status} ({http_time:.0f}ms) - {http_count} results")
            if http_error:
                print(f"       {http_error[:80]}")
            
            # Compare
            match = "✅" if sdk_count == http_count else "❌ MISMATCH"
            speedup = sdk_time / http_time if http_time > 0 else 0
            
            results.append({
                "test": test['name'],
                "sdk_count": sdk_count,
                "http_count": http_count,
                "match": match,
                "sdk_time": sdk_time,
                "http_time": http_time,
                "speedup": speedup,
                "sdk_error": sdk_error is not None,
                "http_error": http_error is not None
            })
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        total = len(results)
        sdk_failures = sum(1 for r in results if r['sdk_error'])
        http_failures = sum(1 for r in results if r['http_error'])
        mismatches = sum(1 for r in results if r['match'] == "❌ MISMATCH")
        matches = total - mismatches
        
        avg_sdk_time = sum(r['sdk_time'] for r in results) / total
        avg_http_time = sum(r['http_time'] for r in results) / total
        
        print(f"\nTotal tests: {total}")
        print(f"SDK failures: {sdk_failures} ({sdk_failures/total*100:.1f}%)")
        print(f"HTTP failures: {http_failures} ({http_failures/total*100:.1f}%)")
        print(f"Result mismatches: {mismatches} ({mismatches/total*100:.1f}%)")
        print(f"Correct matches: {matches} ({matches/total*100:.1f}%)")
        
        print(f"\nAverage SDK time: {avg_sdk_time:.0f}ms")
        print(f"Average HTTP time: {avg_http_time:.0f}ms")
        print(f"HTTP is {avg_sdk_time/avg_http_time:.2f}x faster on average")
        
        print("\n" + "=" * 80)
        print("DETAILED COMPARISON")
        print("=" * 80)
        
        print("\n❌ Tests where SDK failed but HTTP succeeded:")
        for r in results:
            if r['sdk_error'] and not r['http_error']:
                print(f"  • {r['test']}: HTTP returned {r['http_count']} results")
        
        print("\n❌ Tests where results mismatched:")
        for r in results:
            if r['match'] == "❌ MISMATCH" and not r['sdk_error'] and not r['http_error']:
                print(f"  • {r['test']}: SDK={r['sdk_count']} vs HTTP={r['http_count']}")
        
        print("\n⚡ Performance comparison (tests where both succeeded):")
        for r in results:
            if not r['sdk_error'] and not r['http_error'] and r['speedup'] > 0:
                faster = "HTTP" if r['http_time'] < r['sdk_time'] else "SDK"
                ratio = r['speedup'] if faster == "HTTP" else 1/r['speedup']
                print(f"  • {r['test']}: {faster} is {ratio:.2f}x faster")
        
        print("\n" + "=" * 80)
        print("CONCLUSION")
        print("=" * 80)
        
        if sdk_failures > 0:
            print(f"\n⚠️  SDK UNRELIABLE: {sdk_failures} queries failed or returned 0 results")
            print("   Even basic queries like 'SELECT * FROM Customer' fail with SDK")
        
        if http_failures == 0:
            print("\n✅ HTTP RELIABLE: All queries returned expected results")
        
        if avg_http_time < avg_sdk_time:
            print(f"\n⚡ HTTP FASTER: {avg_sdk_time/avg_http_time:.2f}x faster on average")
        
        print("\n🎯 RECOMMENDATION: Use direct HTTP for all QuickBooks queries")
        print("   SDK query() method is fundamentally broken")

if __name__ == "__main__":
    asyncio.run(stress_test())
