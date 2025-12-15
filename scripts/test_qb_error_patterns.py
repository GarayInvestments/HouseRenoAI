"""
QuickBooks Error Response Patterns

Purpose: Document error responses for malformed queries to build error handling patterns
Framework: Stress-Test Mode (Discovery Phase)
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import AsyncSessionLocal
from app.services.quickbooks_service import get_quickbooks_service
from quickbooks.objects.customer import Customer


async def test_error_pattern(qb_service, query_string: str, description: str, expected_error: str):
    """Test query expected to fail and document error pattern."""
    
    print(f"\n{description}")
    print(f"  Query: {query_string[:80]}...")
    print(f"  Expected: {expected_error}")
    
    try:
        # Try with SDK first
        result = Customer.query(query_string, qb=qb_service.qb_client)
        
        # If we get here, query unexpectedly succeeded
        count = len(result) if isinstance(result, list) else (1 if result else 0)
        print(f"  ⚠️  Unexpected success: {count} records")
        return {
            "test": description,
            "query": query_string,
            "expected_error": expected_error,
            "actual_result": "success",
            "count": count,
            "error_details": None
        }
    
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        # Extract QB error code if present
        error_code = None
        if 'code' in error_msg.lower() or 'error' in error_msg.lower():
            # Try to extract error code
            import re
            code_match = re.search(r'code[\'"]?\s*:\s*[\'"]?(\d+)', error_msg, re.IGNORECASE)
            if code_match:
                error_code = code_match.group(1)
        
        print(f"  ✅ Failed as expected: {error_type}")
        print(f"     Message: {error_msg[:150]}")
        if error_code:
            print(f"     Error code: {error_code}")
        
        return {
            "test": description,
            "query": query_string,
            "expected_error": expected_error,
            "actual_result": "error",
            "error_type": error_type,
            "error_message": error_msg[:500],
            "error_code": error_code
        }


async def run_error_pattern_tests():
    """Run comprehensive error pattern tests."""
    
    print("=" * 80)
    print("QuickBooks Error Response Patterns")
    print("Documenting errors for malformed queries")
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
        # Category 1: SQL Syntax Errors
        # ============================================================
        print("=" * 80)
        print("Category 1: SQL Syntax Errors")
        print("=" * 80)
        
        syntax_tests = [
            ("SELECT FROM Customer", "Missing column list", "Syntax error"),
            ("SELECT * Customer", "Missing FROM", "Syntax error"),
            ("SELECT * FROM Customer WHRE Id = '161'", "Typo in WHERE", "Syntax error"),
            ("SELECT * FROM Customer WHERE", "Incomplete WHERE", "Syntax error"),
            ("SELECT * FROM Customer WHERE Id =", "Incomplete condition", "Syntax error"),
            ("SELECT * FROM Customer ORDER BY DisplayName", "ORDER BY (unsupported)", "Unsupported clause"),
            ("SELECT * FROM Customer GROUP BY Active", "GROUP BY (unsupported)", "Unsupported clause"),
        ]
        
        for query, desc, expected in syntax_tests:
            result = await test_error_pattern(qb_service, query, desc, expected)
            results.append(result)
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 2: Invalid Entity Names
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 2: Invalid Entity Names")
        print("=" * 80)
        
        entity_tests = [
            ("SELECT * FROM Customers", "Plural entity name", "Invalid entity"),
            ("SELECT * FROM customer", "Lowercase entity", "Invalid entity"),
            ("SELECT * FROM User", "Non-existent entity", "Invalid entity"),
            ("SELECT * FROM Client", "Wrong entity name", "Invalid entity"),
        ]
        
        for query, desc, expected in entity_tests:
            result = await test_error_pattern(qb_service, query, desc, expected)
            results.append(result)
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 3: Invalid Field Names
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 3: Invalid Field Names")
        print("=" * 80)
        
        field_tests = [
            ("SELECT Name FROM Customer", "Incorrect field name", "Invalid field"),
            ("SELECT * FROM Customer WHERE Name = 'Test'", "WHERE on invalid field", "Invalid field"),
            ("SELECT * FROM Customer WHERE CustomerName = 'Test'", "Non-existent field", "Invalid field"),
            ("SELECT * FROM Customer WHERE customer_id = '161'", "Snake_case field", "Invalid field"),
        ]
        
        for query, desc, expected in field_tests:
            result = await test_error_pattern(qb_service, query, desc, expected)
            results.append(result)
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 4: Invalid Operators
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 4: Invalid Operators")
        print("=" * 80)
        
        operator_tests = [
            ("SELECT * FROM Customer WHERE Id != '161'", "!= operator", "Unsupported operator"),
            ("SELECT * FROM Customer WHERE Id <> '161'", "<> operator", "Unsupported operator"),
            ("SELECT * FROM Customer WHERE DisplayName CONTAINS 'Gust'", "CONTAINS (not LIKE)", "Unsupported operator"),
            ("SELECT * FROM Customer WHERE Id BETWEEN '160' AND '170'", "BETWEEN operator", "Unsupported operator"),
            ("SELECT * FROM Customer WHERE Active IS true", "IS operator", "Unsupported operator"),
            ("SELECT * FROM Customer WHERE Active IS NOT NULL", "IS NOT NULL", "Unsupported operator"),
        ]
        
        for query, desc, expected in operator_tests:
            result = await test_error_pattern(qb_service, query, desc, expected)
            results.append(result)
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 5: Type Mismatches
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 5: Type Mismatches")
        print("=" * 80)
        
        type_tests = [
            ("SELECT * FROM Customer WHERE Id = Gustavo", "String without quotes", "Type mismatch"),
            ("SELECT * FROM Customer WHERE Active = 1", "Boolean as int", "Type mismatch"),
            ("SELECT * FROM Customer WHERE Id = null", "null keyword", "Type mismatch"),
            ("SELECT * FROM Customer WHERE Id = true", "Boolean for ID", "Type mismatch"),
        ]
        
        for query, desc, expected in type_tests:
            result = await test_error_pattern(qb_service, query, desc, expected)
            results.append(result)
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 6: Reference Field Errors (Known QB Limitation)
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 6: Reference Field Errors (Known QB Limitation)")
        print("=" * 80)
        
        ref_tests = [
            ("SELECT * FROM Customer WHERE CustomerTypeRef = '698682'", "CustomerTypeRef direct", "Property not queryable"),
            ("SELECT * FROM Customer WHERE CustomerTypeRef.value = '698682'", "CustomerTypeRef.value", "Property not queryable"),
            ("SELECT * FROM Customer WHERE CustomerTypeRef.name = 'GC Compliance'", "CustomerTypeRef.name", "Property not queryable"),
            ("SELECT * FROM Invoice WHERE CustomerRef = '161'", "CustomerRef direct", "Property not queryable"),
        ]
        
        for query, desc, expected in ref_tests:
            result = await test_error_pattern(qb_service, query, desc, expected)
            results.append(result)
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 7: Pagination Errors
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 7: Pagination Errors")
        print("=" * 80)
        
        pagination_tests = [
            ("SELECT * FROM Customer MAXRESULTS 2000", "MAXRESULTS > 1000", "Value too large"),
            ("SELECT * FROM Customer STARTPOSITION -1", "Negative STARTPOSITION", "Invalid value"),
            ("SELECT * FROM Customer MAXRESULTS 0", "MAXRESULTS 0", "Invalid value"),
            ("SELECT * FROM Customer LIMIT 10", "LIMIT instead of MAXRESULTS", "Unsupported clause"),
            ("SELECT * FROM Customer OFFSET 10", "OFFSET instead of STARTPOSITION", "Unsupported clause"),
        ]
        
        for query, desc, expected in pagination_tests:
            result = await test_error_pattern(qb_service, query, desc, expected)
            results.append(result)
            await asyncio.sleep(0.3)
        
        # ============================================================
        # Category 8: Logical Operator Errors
        # ============================================================
        print("\n" + "=" * 80)
        print("Category 8: Logical Operator Errors")
        print("=" * 80)
        
        logical_tests = [
            ("SELECT * FROM Customer WHERE Id = '161' OR Id = '162'", "OR operator", "Unsupported operator"),
            ("SELECT * FROM Customer WHERE NOT Active = true", "NOT operator", "Unsupported operator"),
            ("SELECT * FROM Customer WHERE (Id = '161' OR Id = '162') AND Active = true", "OR in parentheses", "Unsupported operator"),
        ]
        
        for query, desc, expected in logical_tests:
            result = await test_error_pattern(qb_service, query, desc, expected)
            results.append(result)
            await asyncio.sleep(0.3)
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        total = len(results)
        errors_as_expected = len([r for r in results if r['actual_result'] == 'error'])
        unexpected_success = len([r for r in results if r['actual_result'] == 'success'])
        
        print(f"\nTotal tests: {total}")
        print(f"Errored as expected: {errors_as_expected} ({errors_as_expected/total*100:.1f}%)")
        print(f"Unexpected success: {unexpected_success} ({unexpected_success/total*100:.1f}%)")
        
        # Extract error codes
        error_codes = {}
        for r in results:
            if r['actual_result'] == 'error' and r.get('error_code'):
                code = r['error_code']
                if code not in error_codes:
                    error_codes[code] = []
                error_codes[code].append(r['test'])
        
        if error_codes:
            print("\nError codes encountered:")
            for code, tests in error_codes.items():
                print(f"  Code {code}: {len(tests)} occurrences")
                for test in tests[:3]:  # Show first 3
                    print(f"    - {test}")
        
        # Common error types
        error_types = {}
        for r in results:
            if r['actual_result'] == 'error':
                etype = r.get('error_type', 'Unknown')
                if etype not in error_types:
                    error_types[etype] = 0
                error_types[etype] += 1
        
        print("\nError types distribution:")
        for etype, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {etype}: {count} occurrences")
        
        # Key findings
        print("\n" + "=" * 80)
        print("KEY FINDINGS")
        print("=" * 80)
        
        print("\n✅ Documented error patterns:")
        print("  • SQL syntax errors: Clear error messages")
        print("  • Invalid entity/field names: Caught at query parse time")
        print("  • Unsupported operators: OR, NOT, BETWEEN, IS NULL, etc.")
        print("  • Reference fields: Not queryable (QB limitation)")
        print("  • Pagination limits: MAXRESULTS ≤ 1000, STARTPOSITION ≥ 1")
        
        if unexpected_success:
            print("\n⚠️  Unexpected successful queries:")
            for r in results:
                if r['actual_result'] == 'success':
                    print(f"  • {r['test']}: Expected to fail but returned {r['count']} records")
        
        print("\n" + "=" * 80)
        print("ERROR HANDLING RECOMMENDATIONS")
        print("=" * 80)
        print("1. Validate entity names before querying (Customer, Invoice, Payment, etc.)")
        print("2. Check MAXRESULTS ≤ 1000 before sending query")
        print("3. Never use OR operator - split into multiple queries")
        print("4. Avoid filtering on reference fields - post-filter in Python")
        print("5. Use proper field names (case-sensitive, exact match)")
        print("6. Handle QueryValidationError specifically in error handling")
        
        with open("error_patterns_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to: error_patterns_results.json")


if __name__ == "__main__":
    asyncio.run(run_error_pattern_tests())
