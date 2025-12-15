"""
QuickBooks POST Method Deep Dive

Purpose: POST method surprisingly worked in initial tests - explore why and how
Hypothesis: POST might work with specific content-type or body format combinations
Framework: Stress-Test Mode (Discovery Phase)
"""

import asyncio
import sys
import os
import time
import json
import urllib.parse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import AsyncSessionLocal
from app.services.quickbooks_service import get_quickbooks_service
import httpx


async def test_post_variant(
    qb_service,
    query_string: str,
    body_format: str,
    content_type: str,
    description: str
):
    """Test POST with different body formats and content types."""
    
    base_url = qb_service.qb_client.api_url_v3
    realm_id = qb_service.realm_id
    token = qb_service.qb_client.access_token
    
    url = f"{base_url}/company/{realm_id}/query?minorversion=75"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type,
        "Accept": "application/json"
    }
    
    # Format body based on variant
    if body_format == "raw_sql":
        body = query_string
    elif body_format == "url_encoded":
        body = f"query={urllib.parse.quote(query_string)}"
    elif body_format == "json":
        body = json.dumps({"query": query_string})
    elif body_format == "json_sql":
        body = json.dumps({"sql": query_string})
    elif body_format == "form_data":
        body = {"query": query_string}
    else:
        body = query_string
    
    print(f"\n{description}")
    print(f"  Content-Type: {content_type}")
    print(f"  Body format: {body_format}")
    print(f"  Body preview: {str(body)[:100]}")
    
    try:
        start = time.time()
        
        async with httpx.AsyncClient() as client:
            if isinstance(body, dict):
                response = await client.post(
                    url,
                    headers=headers,
                    data=body,
                    timeout=30.0
                )
            elif isinstance(body, str):
                response = await client.post(
                    url,
                    headers=headers,
                    content=body,
                    timeout=30.0
                )
            else:
                response = await client.post(
                    url,
                    headers=headers,
                    json=body,
                    timeout=30.0
                )
        
        elapsed = int((time.time() - start) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            query_response = data.get('QueryResponse', {})
            
            count = 0
            for key, value in query_response.items():
                if isinstance(value, list):
                    count = len(value)
                    break
            
            print(f"  ✅ Success: {count} records in {elapsed}ms")
            return True, count, elapsed
        else:
            print(f"  ❌ Failed: HTTP {response.status_code}")
            print(f"     Error: {response.text[:150]}")
            return False, 0, elapsed
    
    except Exception as e:
        print(f"  ❌ Exception: {str(e)[:150]}")
        return False, 0, 0


async def run_post_deep_dive():
    """Run comprehensive POST method tests."""
    
    print("=" * 80)
    print("QuickBooks POST Method Deep Dive")
    print("Investigating why POST unexpectedly works")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        qb_service = get_quickbooks_service(db)
        await qb_service.load_tokens_from_db()
        
        if not qb_service.is_authenticated():
            print("❌ Not authenticated")
            return
        
        print("✅ Authenticated\n")
        
        test_query = "SELECT * FROM Customer WHERE Id = '161'"
        
        # Test matrix: body format × content type
        test_cases = [
            # Raw SQL variants
            ("raw_sql", "text/plain", "POST: Raw SQL + text/plain"),
            ("raw_sql", "application/text", "POST: Raw SQL + application/text"),
            ("raw_sql", "application/x-www-form-urlencoded", "POST: Raw SQL + form-urlencoded"),
            
            # URL-encoded variants
            ("url_encoded", "application/x-www-form-urlencoded", "POST: URL-encoded + form-urlencoded"),
            ("url_encoded", "text/plain", "POST: URL-encoded + text/plain"),
            
            # JSON variants
            ("json", "application/json", "POST: JSON {query: ...} + application/json"),
            ("json_sql", "application/json", "POST: JSON {sql: ...} + application/json"),
            
            # Edge cases
            ("raw_sql", "application/json", "POST: Raw SQL + application/json (mismatch)"),
            ("json", "text/plain", "POST: JSON + text/plain (mismatch)"),
        ]
        
        results = []
        
        print("=" * 80)
        print("Test Cases")
        print("=" * 80)
        
        for body_format, content_type, description in test_cases:
            success, count, elapsed = await test_post_variant(
                qb_service,
                test_query,
                body_format,
                content_type,
                description
            )
            results.append({
                "description": description,
                "body_format": body_format,
                "content_type": content_type,
                "success": success,
                "count": count,
                "elapsed_ms": elapsed
            })
            await asyncio.sleep(0.5)  # Rate limit courtesy
        
        # Compare with GET baseline
        print("\n" + "=" * 80)
        print("Baseline: GET Method Comparison")
        print("=" * 80)
        
        base_url = qb_service.qb_client.api_url_v3
        realm_id = qb_service.realm_id
        token = qb_service.qb_client.access_token
        
        encoded_query = urllib.parse.quote(test_query)
        url = f"{base_url}/company/{realm_id}/query?query={encoded_query}&minorversion=75"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        try:
            start = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
            elapsed = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('QueryResponse', {}).get('Customer', []))
                print(f"\nGET baseline: ✅ {count} records in {elapsed}ms")
                
                # Compare performance
                successful_posts = [r for r in results if r['success']]
                if successful_posts:
                    avg_post_time = sum(r['elapsed_ms'] for r in successful_posts) / len(successful_posts)
                    print(f"\nPOST average: {avg_post_time:.0f}ms")
                    print(f"GET vs POST: GET is {avg_post_time/elapsed:.2f}x faster")
        
        except Exception as e:
            print(f"GET baseline failed: {e}")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\nTotal tests: {len(results)}")
        print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
        print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
        
        if successful:
            print("\n✅ Working POST patterns:")
            for r in successful:
                print(f"  • {r['body_format']} + {r['content_type']}")
        
        if failed:
            print("\n❌ Failed POST patterns:")
            for r in failed:
                print(f"  • {r['body_format']} + {r['content_type']}")
        
        print("\n" + "=" * 80)
        print("CONCLUSIONS")
        print("=" * 80)
        
        if successful:
            print("\n🔍 POST method does work for QuickBooks /query endpoint")
            print(f"   {len(successful)}/{len(results)} content-type combinations succeeded")
            print("\n💡 Implications:")
            print("   - Earlier assumption 'POST doesn't work' was incorrect")
            print("   - Both GET and POST are valid for /query endpoint")
            print("   - GET appears faster and simpler (no body encoding needed)")
            print("   - Recommendation: Continue using GET (simpler, fewer edge cases)")
        else:
            print("\n⚠️  No POST patterns worked in this test")
            print("   Earlier success may have been transient or configuration-dependent")
        
        # Save results
        with open("post_method_deep_dive_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: post_method_deep_dive_results.json")


if __name__ == "__main__":
    asyncio.run(run_post_deep_dive())
