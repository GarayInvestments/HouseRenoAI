"""
QuickBooks Encoding & Special Characters Edge Cases

Purpose: Comprehensive testing of special characters, operators, and encoding requirements
Framework: Stress-Test Mode (Discovery Phase)
"""

import asyncio
import sys
import os
import urllib.parse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import AsyncSessionLocal
from app.services.quickbooks_service import get_quickbooks_service
from quickbooks.objects.customer import Customer


async def test_query_encoding(qb_service, query_string: str, description: str, should_encode: bool = True):
    """Test query with specific encoding approach."""
    
    print(f"\n{description}")
    print(f"  Query: {query_string[:80]}...")
    print(f"  Encoding: {'URL-encoded' if should_encode else 'Raw'}")
    
    try:
        # Try HTTP method (our current implementation)
        base_url = qb_service.qb_client.api_url_v3
        realm_id = qb_service.realm_id
        token = qb_service.qb_client.access_token
        
        if should_encode:
            encoded_query = urllib.parse.quote(query_string)
        else:
            encoded_query = query_string
        
        url = f"{base_url}/company/{realm_id}/query?query={encoded_query}&minorversion=75"
        
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                },
                timeout=30.0
            )
        
        if response.status_code == 200:
            data = response.json()
            query_response = data.get('QueryResponse', {})
            
            # Count results
            count = 0
            for key, value in query_response.items():
                if key == 'totalCount':
                    count = value
                    break
                elif isinstance(value, list):
                    count = len(value)
                    break
            
            print(f"  ✅ Success: {count} records")
            return True, count
        else:
            print(f"  ❌ HTTP {response.status_code}: {response.text[:100]}")
            return False, 0
    
    except Exception as e:
        print(f"  ❌ Exception: {str(e)[:100]}")
        return False, 0


async def run_encoding_tests():
    """Run comprehensive encoding tests."""
    
    print("=" * 80)
    print("QuickBooks Encoding & Special Characters Tests")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        qb_service = get_quickbooks_service(db)
        await qb_service.load_tokens_from_db()
        
        if not qb_service.is_authenticated():
            print("❌ Not authenticated")
            return
        
        print("✅ Authenticated\n")
        
        results = []
        
        # ============================================================
        # Category 1: LIKE Operator Variations
        # ============================================================
        print("=" * 80)
        print("Category 1: LIKE Operator Variations")
        print("=" * 80)
        
        like_tests = [
            ("SELECT * FROM Customer WHERE DisplayName LIKE 'Gustavo%'", "LIKE with %", True),
            ("SELECT * FROM Customer WHERE DisplayName LIKE 'Gust%'", "LIKE prefix match", True),
            ("SELECT * FROM Customer WHERE DisplayName LIKE '%Roldan'", "LIKE suffix match", True),
            ("SELECT * FROM Customer WHERE DisplayName LIKE '%usta%'", "LIKE contains", True),
            ("SELECT * FROM Customer WHERE DisplayName LIKE 'Gustavo Roldan'", "LIKE exact (no %)", True),
        ]
        
        for query, desc, should_encode in like_tests:
            success, count = await test_query_encoding(qb_service, query, desc, should_encode)
            results.append({"category": "LIKE", "test": desc, "success": success, "count": count})
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 2: Special Characters in Strings
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 2: Special Characters in Strings")
        print("=" * 80)
        
        # Test with customer 162: Howard C. Nording (has period)
        special_char_tests = [
            ("SELECT * FROM Customer WHERE DisplayName = 'Howard C. Nording'", "Period in name", True),
            ("SELECT * FROM Customer WHERE DisplayName LIKE 'Howard C%'", "Period + LIKE", True),
            ("SELECT * FROM Customer WHERE DisplayName LIKE '%C.%'", "Period in middle", True),
        ]
        
        for query, desc, should_encode in special_char_tests:
            success, count = await test_query_encoding(qb_service, query, desc, should_encode)
            results.append({"category": "Special chars", "test": desc, "success": success, "count": count})
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 3: Date Format Variations
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 3: Date Format Variations")
        print("=" * 80)
        
        date_tests = [
            ("SELECT * FROM Customer WHERE MetaData.CreateTime > '2020-01-01'", "ISO date (YYYY-MM-DD)", True),
            ("SELECT * FROM Customer WHERE MetaData.CreateTime > '2020-01-01T00:00:00'", "ISO datetime", True),
            ("SELECT * FROM Customer WHERE MetaData.CreateTime > '2020-01-01T00:00:00Z'", "ISO datetime UTC", True),
            ("SELECT * FROM Customer WHERE MetaData.CreateTime >= '2020-01-01' AND MetaData.CreateTime < '2025-01-01'", "Date range", True),
        ]
        
        for query, desc, should_encode in date_tests:
            success, count = await test_query_encoding(qb_service, query, desc, should_encode)
            results.append({"category": "Date formats", "test": desc, "success": success, "count": count})
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 4: Operator Combinations
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 4: Operator Combinations")
        print("=" * 80)
        
        operator_tests = [
            ("SELECT * FROM Customer WHERE Active = true AND Id > '160'", "AND with comparison", True),
            ("SELECT * FROM Customer WHERE Id >= '160' AND Id <= '170'", "Range with AND", True),
            ("SELECT * FROM Customer WHERE Active = true AND DisplayName LIKE 'G%'", "AND with LIKE", True),
            ("SELECT * FROM Customer WHERE Id IN ('161', '162', '164')", "IN clause", True),
            ("SELECT * FROM Customer WHERE Id IN ('161','162','164')", "IN no spaces", True),
        ]
        
        for query, desc, should_encode in operator_tests:
            success, count = await test_query_encoding(qb_service, query, desc, should_encode)
            results.append({"category": "Operators", "test": desc, "success": success, "count": count})
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 5: Quote Escaping
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 5: Quote Escaping (if any customers have quotes)")
        print("=" * 80)
        
        quote_tests = [
            ("SELECT * FROM Customer WHERE DisplayName LIKE 'Test%'", "Single quotes (normal)", True),
            ('SELECT * FROM Customer WHERE DisplayName LIKE "Test%"', "Double quotes", True),
        ]
        
        for query, desc, should_encode in quote_tests:
            success, count = await test_query_encoding(qb_service, query, desc, should_encode)
            results.append({"category": "Quotes", "test": desc, "success": success, "count": count})
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 6: Whitespace Handling
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 6: Whitespace Handling")
        print("=" * 80)
        
        whitespace_tests = [
            ("SELECT * FROM Customer WHERE Id='161'", "No spaces around =", True),
            ("SELECT * FROM Customer WHERE Id = '161'", "Spaces around =", True),
            ("SELECT  *  FROM  Customer  WHERE  Id  =  '161'", "Extra spaces everywhere", True),
            ("SELECT * FROM Customer WHERE Id = '161' ", "Trailing space", True),
        ]
        
        for query, desc, should_encode in whitespace_tests:
            success, count = await test_query_encoding(qb_service, query, desc, should_encode)
            results.append({"category": "Whitespace", "test": desc, "success": success, "count": count})
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 7: Case Sensitivity
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 7: Case Sensitivity")
        print("=" * 80)
        
        case_tests = [
            ("SELECT * FROM Customer WHERE DisplayName = 'Gustavo Roldan'", "Exact case", True),
            ("SELECT * FROM Customer WHERE DisplayName = 'gustavo roldan'", "Lowercase", True),
            ("SELECT * FROM Customer WHERE DisplayName = 'GUSTAVO ROLDAN'", "Uppercase", True),
            ("SELECT * FROM Customer WHERE DisplayName LIKE 'gust%'", "LIKE lowercase", True),
        ]
        
        for query, desc, should_encode in case_tests:
            success, count = await test_query_encoding(qb_service, query, desc, should_encode)
            results.append({"category": "Case sensitivity", "test": desc, "success": success, "count": count})
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 8: Raw vs Encoded Comparison
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 8: Raw vs Encoded Direct Comparison")
        print("=" * 80)
        
        test_query = "SELECT * FROM Customer WHERE DisplayName LIKE 'Gustavo%'"
        
        success_encoded, count_encoded = await test_query_encoding(
            qb_service,
            test_query,
            "Same query: URL-encoded",
            should_encode=True
        )
        
        success_raw, count_raw = await test_query_encoding(
            qb_service,
            test_query,
            "Same query: Raw (no encoding)",
            should_encode=False
        )
        
        if success_encoded and not success_raw:
            print("\n  💡 Encoding REQUIRED for queries with special characters")
        elif success_encoded and success_raw:
            print("\n  💡 Encoding OPTIONAL for this query")
        elif not success_encoded and success_raw:
            print("\n  ⚠️  Raw works but encoded fails (unexpected)")
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        total = len(results)
        successful = len([r for r in results if r['success']])
        
        print(f"\nTotal tests: {total}")
        print(f"Successful: {successful} ({successful/total*100:.1f}%)")
        print(f"Failed: {total - successful} ({(total-successful)/total*100:.1f}%)")
        
        # By category
        categories = {}
        for r in results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = {'success': 0, 'total': 0}
            categories[cat]['total'] += 1
            if r['success']:
                categories[cat]['success'] += 1
        
        print("\nResults by category:")
        for cat, stats in categories.items():
            success_rate = stats['success'] / stats['total'] * 100
            print(f"  {cat}: {stats['success']}/{stats['total']} ({success_rate:.0f}%)")
        
        # Key findings
        print("\n" + "=" * 80)
        print("KEY FINDINGS")
        print("=" * 80)
        
        like_success = [r for r in results if r['category'] == 'LIKE' and r['success']]
        if like_success:
            print(f"\n✅ LIKE operator: {len(like_success)}/{len([r for r in results if r['category'] == 'LIKE'])} patterns work")
        
        date_success = [r for r in results if r['category'] == 'Date formats' and r['success']]
        if date_success:
            print(f"✅ Date formats: {len(date_success)}/{len([r for r in results if r['category'] == 'Date formats'])} formats accepted")
        
        case_results = [r for r in results if r['category'] == 'Case sensitivity']
        if case_results:
            case_matches = [r for r in case_results if r['success'] and r['count'] > 0]
            if len(case_matches) < len(case_results):
                print("⚠️  Case sensitivity: QuickBooks appears case-sensitive for DisplayName")
            else:
                print("✅ Case sensitivity: Appears case-insensitive")
        
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print("1. Always URL-encode queries containing special characters (LIKE, %, spaces)")
        print("2. Use ISO date format: YYYY-MM-DD for date comparisons")
        print("3. Single quotes preferred for string literals in QB SQL")
        print("4. Whitespace tolerance: Extra spaces generally handled")
        print("5. LIKE operator requires % for wildcard matching")
        
        import json
        with open("encoding_edge_cases_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to: encoding_edge_cases_results.json")


if __name__ == "__main__":
    asyncio.run(run_encoding_tests())
