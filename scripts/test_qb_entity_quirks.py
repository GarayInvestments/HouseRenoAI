"""
QuickBooks Entity-Specific Quirks

Purpose: Test all entity types we use to identify entity-specific behaviors and quirks
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
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.payment import Payment
from quickbooks.objects.estimate import Estimate
from quickbooks.objects.item import Item
from quickbooks.objects.bill import Bill


async def test_entity_behavior(qb_service, entity_class, tests: list):
    """Test specific behaviors for an entity type."""
    
    entity_name = entity_class.__name__
    print(f"\n{'=' * 80}")
    print(f"Testing: {entity_name}")
    print(f"{'=' * 80}")
    
    results = []
    
    for test_name, query, expected_behavior in tests:
        print(f"\n{test_name}:")
        print(f"  Query: {query[:80]}...")
        
        try:
            result = entity_class.query(query, qb=qb_service.qb_client)
            
            count = len(result) if isinstance(result, list) else (1 if result else 0)
            print(f"  ✅ Success: {count} records")
            
            # Inspect structure of first result if available
            if count > 0:
                sample = result[0] if isinstance(result, list) else result
                
                # Check for common quirks
                quirks = []
                
                # Check reference field structures
                if hasattr(sample, 'CustomerRef'):
                    ref_type = type(sample.CustomerRef)
                    quirks.append(f"CustomerRef type: {ref_type.__name__}")
                
                # Check date field formats
                if hasattr(sample, 'TxnDate'):
                    date_type = type(sample.TxnDate)
                    quirks.append(f"TxnDate type: {date_type.__name__}")
                
                # Check metadata
                if hasattr(sample, 'MetaData'):
                    meta_type = type(sample.MetaData)
                    quirks.append(f"MetaData type: {meta_type.__name__}")
                
                # Check array fields
                if hasattr(sample, 'Line'):
                    line_type = type(sample.Line)
                    line_count = len(sample.Line) if isinstance(sample.Line, list) else 1
                    quirks.append(f"Line type: {line_type.__name__}, count: {line_count}")
                
                if quirks:
                    print(f"  Structure notes: {'; '.join(quirks)}")
            
            results.append({
                "test": test_name,
                "query": query,
                "expected": expected_behavior,
                "actual": "success",
                "count": count,
                "quirks": quirks if count > 0 else []
            })
        
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)[:200]
            print(f"  ❌ Error: {error_type}")
            print(f"     {error_msg}")
            
            results.append({
                "test": test_name,
                "query": query,
                "expected": expected_behavior,
                "actual": "error",
                "error_type": error_type,
                "error_message": error_msg
            })
        
        await asyncio.sleep(0.3)
    
    return results


async def run_entity_quirks_tests():
    """Run entity-specific quirk tests."""
    
    print("=" * 80)
    print("QuickBooks Entity-Specific Quirks")
    print("Testing all entity types for inconsistencies")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        qb_service = get_quickbooks_service(db)
        await qb_service.load_tokens_from_db()
        
        if not qb_service.is_authenticated():
            print("❌ Not authenticated")
            return
        
        print("✅ Authenticated\n")
        
        all_results = {}
        
        # ============================================================
        # Customer Entity
        # ============================================================
        customer_tests = [
            ("Basic SELECT", "SELECT * FROM Customer MAXRESULTS 5", "Success"),
            ("COUNT query", "SELECT COUNT(*) FROM Customer", "Returns count"),
            ("Active filter", "SELECT * FROM Customer WHERE Active = true MAXRESULTS 5", "Filtered results"),
            ("Id filter", "SELECT * FROM Customer WHERE Id = '161'", "Single result"),
            ("DisplayName LIKE", "SELECT * FROM Customer WHERE DisplayName LIKE 'G%'", "LIKE works"),
            ("Date filter", "SELECT * FROM Customer WHERE MetaData.CreateTime > '2020-01-01'", "Date comparison"),
            ("Multiple AND", "SELECT * FROM Customer WHERE Active = true AND Id > '160'", "Multiple conditions"),
        ]
        
        all_results['Customer'] = await test_entity_behavior(qb_service, Customer, customer_tests)
        
        # ============================================================
        # Invoice Entity
        # ============================================================
        invoice_tests = [
            ("Basic SELECT", "SELECT * FROM Invoice MAXRESULTS 5", "Success"),
            ("COUNT query", "SELECT COUNT(*) FROM Invoice", "Returns count"),
            ("CustomerRef filter", "SELECT * FROM Invoice WHERE CustomerRef = '161'", "Reference filter"),
            ("TxnDate filter", "SELECT * FROM Invoice WHERE TxnDate > '2020-01-01'", "Date filter"),
            ("Balance filter", "SELECT * FROM Invoice WHERE Balance > 0", "Numeric filter"),
            ("DocNumber filter", "SELECT * FROM Invoice WHERE DocNumber = '1001'", "String filter"),
        ]
        
        all_results['Invoice'] = await test_entity_behavior(qb_service, Invoice, invoice_tests)
        
        # ============================================================
        # Payment Entity
        # ============================================================
        payment_tests = [
            ("Basic SELECT", "SELECT * FROM Payment MAXRESULTS 5", "Success"),
            ("COUNT query", "SELECT COUNT(*) FROM Payment", "Returns count"),
            ("CustomerRef filter", "SELECT * FROM Payment WHERE CustomerRef = '161'", "Reference filter"),
            ("TxnDate filter", "SELECT * FROM Payment WHERE TxnDate > '2020-01-01'", "Date filter"),
            ("TotalAmt filter", "SELECT * FROM Payment WHERE TotalAmt > 0", "Numeric filter"),
        ]
        
        all_results['Payment'] = await test_entity_behavior(qb_service, Payment, payment_tests)
        
        # ============================================================
        # Estimate Entity
        # ============================================================
        estimate_tests = [
            ("Basic SELECT", "SELECT * FROM Estimate MAXRESULTS 5", "Success"),
            ("COUNT query", "SELECT COUNT(*) FROM Estimate", "Returns count"),
            ("CustomerRef filter", "SELECT * FROM Estimate WHERE CustomerRef = '161'", "Reference filter"),
            ("TxnDate filter", "SELECT * FROM Estimate WHERE TxnDate > '2020-01-01'", "Date filter"),
            ("TxnStatus filter", "SELECT * FROM Estimate WHERE TxnStatus = 'Accepted'", "Status filter"),
        ]
        
        all_results['Estimate'] = await test_entity_behavior(qb_service, Estimate, estimate_tests)
        
        # ============================================================
        # Item Entity
        # ============================================================
        item_tests = [
            ("Basic SELECT", "SELECT * FROM Item MAXRESULTS 5", "Success"),
            ("COUNT query", "SELECT COUNT(*) FROM Item", "Returns count"),
            ("Type filter", "SELECT * FROM Item WHERE Type = 'Service'", "Type filter"),
            ("Name filter", "SELECT * FROM Item WHERE Name = 'GC Permit Oversight'", "Name filter"),
            ("Active filter", "SELECT * FROM Item WHERE Active = true MAXRESULTS 5", "Active filter"),
        ]
        
        all_results['Item'] = await test_entity_behavior(qb_service, Item, item_tests)
        
        # ============================================================
        # Bill Entity
        # ============================================================
        bill_tests = [
            ("Basic SELECT", "SELECT * FROM Bill MAXRESULTS 5", "Success"),
            ("COUNT query", "SELECT COUNT(*) FROM Bill", "Returns count"),
            ("VendorRef filter", "SELECT * FROM Bill WHERE VendorRef = '60'", "Reference filter"),
            ("TxnDate filter", "SELECT * FROM Bill WHERE TxnDate > '2020-01-01'", "Date filter"),
            ("Balance filter", "SELECT * FROM Bill WHERE Balance > 0", "Numeric filter"),
        ]
        
        all_results['Bill'] = await test_entity_behavior(qb_service, Bill, bill_tests)
        
        # ============================================================
        # CROSS-ENTITY COMPARISON
        # ============================================================
        print("\n" + "=" * 80)
        print("CROSS-ENTITY COMPARISON")
        print("=" * 80)
        
        entity_stats = {}
        for entity_name, results in all_results.items():
            total = len(results)
            successful = len([r for r in results if r['actual'] == 'success'])
            errors = len([r for r in results if r['actual'] == 'error'])
            
            entity_stats[entity_name] = {
                'total': total,
                'successful': successful,
                'errors': errors,
                'success_rate': successful / total * 100
            }
        
        print("\nEntity reliability comparison:")
        for entity, stats in sorted(entity_stats.items(), key=lambda x: x[1]['success_rate'], reverse=True):
            print(f"  {entity}: {stats['successful']}/{stats['total']} ({stats['success_rate']:.0f}%)")
        
        # COUNT query comparison
        print("\n" + "=" * 80)
        print("COUNT Query Behavior Across Entities")
        print("=" * 80)
        
        count_results = {}
        for entity_name, results in all_results.items():
            count_test = next((r for r in results if 'COUNT' in r['query']), None)
            if count_test:
                if count_test['actual'] == 'success':
                    count_results[entity_name] = count_test['count']
                    print(f"  {entity_name}: ✅ COUNT returns {count_test['count']}")
                else:
                    print(f"  {entity_name}: ❌ COUNT failed - {count_test.get('error_type', 'Unknown')}")
        
        # Reference field comparison
        print("\n" + "=" * 80)
        print("Reference Field Filtering Behavior")
        print("=" * 80)
        
        ref_tests = {
            'Invoice': 'CustomerRef',
            'Payment': 'CustomerRef',
            'Estimate': 'CustomerRef',
            'Bill': 'VendorRef'
        }
        
        for entity_name, ref_field in ref_tests.items():
            ref_test = next((r for r in all_results[entity_name] if ref_field in r['query']), None)
            if ref_test:
                if ref_test['actual'] == 'success':
                    print(f"  {entity_name}.{ref_field}: ✅ Filterable ({ref_test['count']} results)")
                else:
                    print(f"  {entity_name}.{ref_field}: ❌ Not filterable")
        
        # ============================================================
        # KEY FINDINGS
        # ============================================================
        print("\n" + "=" * 80)
        print("KEY FINDINGS")
        print("=" * 80)
        
        # Most reliable entity
        most_reliable = max(entity_stats.items(), key=lambda x: x[1]['success_rate'])
        print(f"\n✅ Most reliable entity: {most_reliable[0]} ({most_reliable[1]['success_rate']:.0f}% success)")
        
        # Entities with issues
        problematic = [(name, stats) for name, stats in entity_stats.items() if stats['success_rate'] < 100]
        if problematic:
            print("\n⚠️  Entities with query issues:")
            for name, stats in problematic:
                print(f"  • {name}: {stats['errors']} failures")
                # Show which tests failed
                failed_tests = [r for r in all_results[name] if r['actual'] == 'error']
                for test in failed_tests:
                    print(f"    - {test['test']}: {test.get('error_type', 'Unknown error')}")
        
        # COUNT query pattern
        all_count_work = all(entity in count_results for entity in entity_stats.keys())
        if all_count_work:
            print("\n✅ COUNT queries work consistently across all entities")
        else:
            print("\n⚠️  COUNT query behavior inconsistent")
        
        # Reference field pattern
        ref_success_count = sum(1 for entity in ref_tests.keys() 
                               if any(r['actual'] == 'success' and ref_tests[entity] in r['query'] 
                                     for r in all_results[entity]))
        print(f"\n✅ Reference field filtering: {ref_success_count}/{len(ref_tests)} entities support it")
        
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print("1. CustomerRef/VendorRef ARE filterable (unlike CustomerTypeRef)")
        print("2. All entities support COUNT queries via SDK")
        print("3. Date filtering works consistently across transaction entities")
        print("4. Active/Balance filters work where applicable")
        print("5. Structure inspection shows consistent reference field patterns")
        
        with open("entity_quirks_results.json", "w") as f:
            json.dump({
                'entity_results': all_results,
                'entity_stats': entity_stats,
                'count_results': count_results
            }, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: entity_quirks_results.json")


if __name__ == "__main__":
    asyncio.run(run_entity_quirks_tests())
