"""
Query specific customer by ID using GET (not query).
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.quickbooks_service import get_quickbooks_service
from app.db.session import AsyncSessionLocal

async def query_customer_174():
    """Try to retrieve customer 174 directly by ID."""
    
    print("=" * 70)
    print("QUICKBOOKS CUSTOMER 174 DIRECT READ")
    print("=" * 70)
    
    # Get database connection
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
        
        # Try Method 1: Direct GET by ID
        print("\n" + "-"*70)
        print("METHOD 1: Direct GET /customer/174")
        print("-"*70)
        
        try:
            from quickbooks.objects.customer import Customer
            
            customer = Customer.get(174, qb=qb_service.qb_client)
            
            print(f"✅ Customer found:")
            print(f"  ID: {customer.Id}")
            print(f"  DisplayName: {customer.DisplayName}")
            print(f"  GivenName: {customer.GivenName}")
            print(f"  FamilyName: {customer.FamilyName}")
            print(f"  CompanyName: {customer.CompanyName}")
            
            # Check CustomerTypeRef
            if hasattr(customer, 'CustomerTypeRef') and customer.CustomerTypeRef:
                print(f"  CustomerTypeRef.value: {customer.CustomerTypeRef.value}")
                print(f"  CustomerTypeRef.name: {customer.CustomerTypeRef.name if hasattr(customer.CustomerTypeRef, 'name') else 'N/A'}")
            else:
                print(f"  CustomerTypeRef: None")
                
            # Check email
            if hasattr(customer, 'PrimaryEmailAddr') and customer.PrimaryEmailAddr:
                print(f"  Email: {customer.PrimaryEmailAddr.Address}")
            else:
                print(f"  Email: None")
                
            # Check active status
            print(f"  Active: {customer.Active}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Try Method 2: Query by ID
        print("\n" + "-"*70)
        print("METHOD 2: Query SELECT * FROM Customer WHERE Id = '174'")
        print("-"*70)
        
        try:
            query = "SELECT * FROM Customer WHERE Id = '174'"
            print(f"Query: {query}")
            
            customers = await qb_service.query(query)
            print(f"Found {len(customers)} customers")
            
            if customers:
                customer = customers[0]
                print(f"✅ Customer found:")
                print(f"  ID: {customer.get('Id')}")
                print(f"  DisplayName: {customer.get('DisplayName')}")
                print(f"  CustomerTypeRef: {customer.get('CustomerTypeRef')}")
            else:
                print("❌ No customer found with ID 174")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Try Method 3: Query ALL customers and show summary
        print("\n" + "-"*70)
        print("METHOD 3: Query all customers - show IDs only")
        print("-"*70)
        
        try:
            query = "SELECT * FROM Customer STARTPOSITION 1 MAXRESULTS 1000"
            print(f"Query: {query}")
            
            customers = await qb_service.query(query)
            print(f"\nTotal customers: {len(customers)}")
            
            if customers:
                print("\nAll customer IDs:")
                for c in customers[:20]:  # Show first 20
                    cust_id = c.get('Id')
                    name = c.get('DisplayName')
                    active = c.get('Active', 'Unknown')
                    print(f"  {cust_id}: {name} (Active: {active})")
                
                if len(customers) > 20:
                    print(f"  ... and {len(customers) - 20} more")
            else:
                print("❌ Zero customers returned")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(query_customer_174())
