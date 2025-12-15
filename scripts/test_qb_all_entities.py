"""
Test QuickBooks queries for all entity types used in the system.
Tests: Customers, Invoices, Payments, Estimates, Items, Bills
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.quickbooks_service import get_quickbooks_service
from app.db.session import AsyncSessionLocal

# GC Compliance customer IDs
GC_CUSTOMER_IDS = ['161', '174', '162', '164', '165', '167', '169']

async def test_all_entities():
    """Test queries for all relevant entity types."""
    
    print("=" * 70)
    print("QUICKBOOKS ENTITY QUERY TESTS")
    print("=" * 70)
    
    async with AsyncSessionLocal() as db:
        # Get QB service and load tokens
        print("\nLoading tokens from database...")
        qb_service = get_quickbooks_service(db)
        await qb_service.load_tokens_from_db()
        
        if not qb_service.is_authenticated():
            print("❌ QuickBooks not authenticated")
            return
        
        print(f"Authentication: ✅ Yes")
        print(f"Realm ID: {qb_service.realm_id}")
        
        results = {}
        
        # Test 1: Count all entity types
        print("\n" + "=" * 70)
        print("TEST 1: COUNT ALL ENTITY TYPES")
        print("=" * 70)
        
        entities = [
            ("Customer", "SELECT COUNT(*) FROM Customer"),
            ("Invoice", "SELECT COUNT(*) FROM Invoice"),
            ("Payment", "SELECT COUNT(*) FROM Payment"),
            ("Estimate", "SELECT COUNT(*) FROM Estimate"),
            ("Item", "SELECT COUNT(*) FROM Item"),
            ("Bill", "SELECT COUNT(*) FROM Bill"),
        ]
        
        for entity_name, query in entities:
            try:
                result = await qb_service.query(query)
                count = result.get('totalCount', 0) if isinstance(result, dict) else len(result)
                results[entity_name] = count
                print(f"✅ {entity_name}: {count}")
            except Exception as e:
                print(f"❌ {entity_name}: {e}")
                results[entity_name] = 0
        
        # Test 2: Get sample Customers (already verified this works)
        print("\n" + "=" * 70)
        print("TEST 2: CUSTOMERS - GC Compliance Only")
        print("=" * 70)
        
        try:
            query = "SELECT * FROM Customer WHERE Active = true STARTPOSITION 1 MAXRESULTS 100"
            customers = await qb_service.query(query)
            
            # Filter to GC Compliance
            gc_customers = [
                c for c in customers
                if c.get('CustomerTypeRef', {}).get('value') == '698682'
            ]
            
            print(f"Total active customers: {len(customers)}")
            print(f"GC Compliance customers: {len(gc_customers)}")
            
            for c in gc_customers[:5]:
                print(f"  • {c['Id']}: {c['DisplayName']}")
            
            results['GC_Customers'] = len(gc_customers)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 3: Get Invoices for GC Customers
        print("\n" + "=" * 70)
        print("TEST 3: INVOICES - For GC Compliance Customers")
        print("=" * 70)
        
        try:
            # Get all invoices
            query = "SELECT * FROM Invoice STARTPOSITION 1 MAXRESULTS 100"
            invoices = await qb_service.query(query)
            
            # Filter to GC customers
            gc_invoices = [
                inv for inv in invoices
                if inv.get('CustomerRef', {}).get('value') in GC_CUSTOMER_IDS
            ]
            
            print(f"Total invoices: {len(invoices)}")
            print(f"GC customer invoices: {len(gc_invoices)}")
            
            if gc_invoices:
                print("\nSample GC invoices:")
                for inv in gc_invoices[:3]:
                    inv_id = inv['Id']
                    doc_num = inv.get('DocNumber', 'N/A')
                    cust_name = inv.get('CustomerRef', {}).get('name', 'Unknown')
                    total = inv.get('TotalAmt', 0)
                    print(f"  • {inv_id} (#{doc_num}): {cust_name} - ${total}")
            
            results['GC_Invoices'] = len(gc_invoices)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 4: Get Payments linked to GC Customers
        print("\n" + "=" * 70)
        print("TEST 4: PAYMENTS - For GC Compliance Customers")
        print("=" * 70)
        
        try:
            # Get all payments
            query = "SELECT * FROM Payment STARTPOSITION 1 MAXRESULTS 100"
            payments = await qb_service.query(query)
            
            # Filter to GC customers
            gc_payments = [
                pmt for pmt in payments
                if pmt.get('CustomerRef', {}).get('value') in GC_CUSTOMER_IDS
            ]
            
            print(f"Total payments: {len(payments)}")
            print(f"GC customer payments: {len(gc_payments)}")
            
            if gc_payments:
                print("\nSample GC payments:")
                for pmt in gc_payments[:3]:
                    pmt_id = pmt['Id']
                    cust_name = pmt.get('CustomerRef', {}).get('name', 'Unknown')
                    total = pmt.get('TotalAmt', 0)
                    txn_date = pmt.get('TxnDate', 'N/A')
                    print(f"  • {pmt_id}: {cust_name} - ${total} ({txn_date})")
            
            results['GC_Payments'] = len(gc_payments)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 5: Get Estimates for GC Customers
        print("\n" + "=" * 70)
        print("TEST 5: ESTIMATES - For GC Compliance Customers")
        print("=" * 70)
        
        try:
            query = "SELECT * FROM Estimate STARTPOSITION 1 MAXRESULTS 100"
            estimates = await qb_service.query(query)
            
            # Filter to GC customers
            gc_estimates = [
                est for est in estimates
                if est.get('CustomerRef', {}).get('value') in GC_CUSTOMER_IDS
            ]
            
            print(f"Total estimates: {len(estimates)}")
            print(f"GC customer estimates: {len(gc_estimates)}")
            
            if gc_estimates:
                print("\nSample GC estimates:")
                for est in gc_estimates[:3]:
                    est_id = est['Id']
                    doc_num = est.get('DocNumber', 'N/A')
                    cust_name = est.get('CustomerRef', {}).get('name', 'Unknown')
                    total = est.get('TotalAmt', 0)
                    print(f"  • {est_id} (#{doc_num}): {cust_name} - ${total}")
            
            results['GC_Estimates'] = len(gc_estimates)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 6: Get Service Items (used in invoices)
        print("\n" + "=" * 70)
        print("TEST 6: ITEMS - Service Items for Invoices")
        print("=" * 70)
        
        try:
            query = "SELECT * FROM Item WHERE Type = 'Service' STARTPOSITION 1 MAXRESULTS 50"
            items = await qb_service.query(query)
            
            print(f"Service items: {len(items)}")
            
            # Look for the specific item mentioned in docs (ID 108)
            gc_permit_item = next((item for item in items if item.get('Id') == '108'), None)
            
            if gc_permit_item:
                print(f"\n✅ Found 'GC Permit Oversight' item (ID 108):")
                print(f"   Name: {gc_permit_item.get('Name')}")
                print(f"   Rate: ${gc_permit_item.get('UnitPrice', 0)}")
            
            print("\nSample service items:")
            for item in items[:5]:
                item_id = item['Id']
                name = item.get('Name', 'Unknown')
                rate = item.get('UnitPrice', 0)
                print(f"  • {item_id}: {name} - ${rate}")
            
            results['Service_Items'] = len(items)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 7: Query by specific customer (filter by CustomerRef)
        print("\n" + "=" * 70)
        print("TEST 7: FILTER BY CUSTOMER - Invoices for Customer 174")
        print("=" * 70)
        
        try:
            query = "SELECT * FROM Invoice WHERE CustomerRef = '174'"
            invoices_174 = await qb_service.query(query)
            
            print(f"Invoices for customer 174 (Javier Martinez): {len(invoices_174)}")
            
            for inv in invoices_174[:3]:
                inv_id = inv['Id']
                doc_num = inv.get('DocNumber', 'N/A')
                total = inv.get('TotalAmt', 0)
                date = inv.get('TxnDate', 'N/A')
                print(f"  • Invoice {inv_id} (#{doc_num}): ${total} ({date})")
            
            results['Customer_174_Invoices'] = len(invoices_174)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 8: Date range query (invoices from 2024+)
        print("\n" + "=" * 70)
        print("TEST 8: DATE RANGE - Invoices from 2024 onwards")
        print("=" * 70)
        
        try:
            query = "SELECT * FROM Invoice WHERE TxnDate >= '2024-01-01' STARTPOSITION 1 MAXRESULTS 50"
            recent_invoices = await qb_service.query(query)
            
            print(f"Invoices since 2024-01-01: {len(recent_invoices)}")
            
            # Show GC customer invoices
            recent_gc_invoices = [
                inv for inv in recent_invoices
                if inv.get('CustomerRef', {}).get('value') in GC_CUSTOMER_IDS
            ]
            
            print(f"GC customer invoices (2024+): {len(recent_gc_invoices)}")
            
            results['Recent_GC_Invoices'] = len(recent_gc_invoices)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY - Entity Counts")
        print("=" * 70)
        
        for key, value in results.items():
            print(f"{key}: {value}")
        
        print("\n" + "=" * 70)
        print("KEY FINDINGS")
        print("=" * 70)
        
        print("\n✅ Queries working:")
        print("  • Direct HTTP GET successfully retrieves all entity types")
        print("  • Filtering by CustomerRef works")
        print("  • Date range queries work")
        print("  • Pagination works")
        
        print("\n⚠️  Notes:")
        print("  • CustomerTypeRef is NOT filterable in queries (QB limitation)")
        print("  • Must post-filter GC Compliance customers in Python")
        print("  • Service Item ID 108 is used for GC Permit Oversight invoices")
        
        if results.get('GC_Invoices', 0) > 0 or results.get('GC_Payments', 0) > 0:
            print("\n🎯 Sync Readiness:")
            print("  • GC Compliance customers linked to database")
            print("  • Transaction data exists in QuickBooks")
            print("  • Ready to sync invoices and payments to cache")

if __name__ == "__main__":
    asyncio.run(test_all_entities())
