"""
Query QuickBooks for specific customer IDs to verify they exist.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.services.quickbooks_service import get_quickbooks_service

# Customer IDs to verify
CUSTOMER_IDS = ["161", "162", "164", "165", "167", "169", "174"]

async def query_qb_customers():
    """Query QuickBooks for customers"""
    
    async with AsyncSessionLocal() as db:
        try:
            qb_service = get_quickbooks_service(db)
            
            print("\n" + "="*70)
            print("QUICKBOOKS CUSTOMER QUERY")
            print("="*70)
            
            # CRITICAL: Load tokens from database FIRST
            print("\nLoading tokens from database...")
            await qb_service.load_tokens_from_db()
            
            # Check authentication
            print(f"Authentication: {'✅ Yes' if qb_service.is_authenticated() else '❌ No'}")
            print(f"Realm ID: {qb_service.realm_id}")
            print(f"Environment: {qb_service.environment}")
            
            if not qb_service.is_authenticated():
                print("\n❌ Not authenticated with QuickBooks")
                print("Run: http://localhost:8000/v1/quickbooks/auth")
                return
            
            print(f"\nQuerying for {len(CUSTOMER_IDS)} customers...")
            
            # Method 1: Query ALL customers, then filter by CustomerTypeRef in Python
            # NOTE: QB API doesn't support WHERE on CustomerTypeRef - must post-filter
            print("\n" + "-"*70)
            print("METHOD 1: Query all customers, filter by GC Compliance")
            print("-"*70)
            
            try:
                # Fetch ALL customers (QB doesn't support WHERE on CustomerTypeRef)
                query = "SELECT * FROM Customer STARTPOSITION 1 MAXRESULTS 1000"
                print(f"Query: {query}")
                
                all_customers = await qb_service.query(query)
                print(f"\nTotal customers in QB: {len(all_customers)}")
                
                # Post-filter by CustomerTypeRef.value = '698682'
                gc_customers = [
                    c for c in all_customers
                    if c.get('CustomerTypeRef', {}).get('value') == '698682'
                ]
                
                print(f"GC Compliance customers: {len(gc_customers)}")
                
                for customer in gc_customers:
                    cust_id = customer.get('Id')
                    name = customer.get('DisplayName')
                    customer_type = customer.get('CustomerTypeRef', {}).get('value', 'N/A')
                    print(f"  {cust_id}: {name} (Type: {customer_type})")
                    
                # Check if our IDs are in the results
                found_ids = {c.get('Id') for c in customers}
                print(f"\nChecking our IDs against GC Compliance customers:")
                for cust_id in CUSTOMER_IDS:
                    status = "✅ Found" if cust_id in found_ids else "❌ Not in GC Compliance"
                    print(f"  {cust_id}: {status}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
            
            # Method 2: Query each customer by ID individually
            print("\n" + "-"*70)
            print("METHOD 2: Query each customer by ID (no filter)")
            print("-"*70)
            
            for cust_id in CUSTOMER_IDS:
                try:
                    query = f"SELECT * FROM Customer WHERE Id = '{cust_id}'"
                    customers = await qb_service.query(query)
                    
                    if customers:
                        customer = customers[0]
                        name = customer.get('DisplayName')
                        customer_type_ref = customer.get('CustomerTypeRef', {})
                        customer_type = customer_type_ref.get('value', 'N/A')
                        is_gc = "✅ GC Compliance" if customer_type == "698682" else f"⚠️  Type {customer_type}"
                        
                        print(f"\n{cust_id}: {name}")
                        print(f"  Type: {is_gc}")
                        print(f"  Email: {customer.get('PrimaryEmailAddr', {}).get('Address', 'N/A')}")
                    else:
                        print(f"\n{cust_id}: ❌ Not found")
                        
                except Exception as e:
                    print(f"\n{cust_id}: ❌ Error - {e}")
            
            # Method 3: Query ALL customers (no filter) to see what we have
            print("\n" + "-"*70)
            print("METHOD 3: Query ALL customers")
            print("-"*70)
            
            try:
                query = "SELECT * FROM Customer STARTPOSITION 1 MAXRESULTS 100"
                print(f"Query: {query}")
                customers = await qb_service.query(query)
                print(f"\nTotal customers in QB: {len(customers)}")
                
                if len(customers) == 0:
                    print("\n⚠️  No customers found in QuickBooks!")
                    print("   This could mean:")
                    print("   1. Wrong realm ID")
                    print("   2. No customers exist")
                    print("   3. API permissions issue")
                else:
                    print("\nAll customers:")
                    for customer in customers:
                        cust_id = customer.get('Id')
                        name = customer.get('DisplayName')
                        customer_type_ref = customer.get('CustomerTypeRef', {})
                        customer_type = customer_type_ref.get('value', 'N/A') if customer_type_ref else 'N/A'
                        
                        # Highlight if it's one of our IDs
                        marker = "👉 " if cust_id in CUSTOMER_IDS else "   "
                        gc_marker = " [GC]" if customer_type == "698682" else ""
                        print(f"{marker}{cust_id}: {name} (Type: {customer_type}{gc_marker})")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n" + "="*70)
            
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(query_qb_customers())
