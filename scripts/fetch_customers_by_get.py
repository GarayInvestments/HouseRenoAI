"""
Fetch all 7 customers directly using GET (not query).
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.quickbooks_service import get_quickbooks_service
from app.db.session import AsyncSessionLocal

# User's client ID mappings
CUSTOMER_IDS = {
    "Gustavo Roldan": "161",
    "Javier Martinez": "174",
    "Howard Nordin": "162",
    "Ajay Nair": "164",
    "Steve Jones": "165",
    "Marta Alder": "167",
    "Brandon Davis": "169"
}

async def fetch_customers_by_get():
    """Fetch all 7 customers using direct GET requests."""
    
    print("=" * 70)
    print("FETCH CUSTOMERS BY ID USING GET")
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
        
        print("\n" + "-"*70)
        print("FETCHING 7 CUSTOMERS BY ID")
        print("-"*70)
        
        from quickbooks.objects.customer import Customer
        
        results = []
        
        for name, qb_id in CUSTOMER_IDS.items():
            try:
                customer = Customer.get(int(qb_id), qb=qb_service.qb_client)
                
                # Extract CustomerTypeRef
                customer_type = "None"
                if hasattr(customer, 'CustomerTypeRef') and customer.CustomerTypeRef:
                    if isinstance(customer.CustomerTypeRef, dict):
                        customer_type = customer.CustomerTypeRef.get('value', 'None')
                    else:
                        customer_type = getattr(customer.CustomerTypeRef, 'value', 'None')
                
                # Extract email
                email = "None"
                if hasattr(customer, 'PrimaryEmailAddr') and customer.PrimaryEmailAddr:
                    if isinstance(customer.PrimaryEmailAddr, dict):
                        email = customer.PrimaryEmailAddr.get('Address', 'None')
                    else:
                        email = getattr(customer.PrimaryEmailAddr, 'Address', 'None')
                
                results.append({
                    'expected_name': name,
                    'qb_id': qb_id,
                    'qb_name': customer.DisplayName,
                    'customer_type': customer_type,
                    'email': email,
                    'active': customer.Active,
                    'found': True
                })
                
                status = "✅"
                type_status = "✅" if customer_type == "698682" else f"❌ Type: {customer_type}"
                print(f"{status} {qb_id}: {customer.DisplayName} ({type_status})")
                if email != "None":
                    print(f"     Email: {email}")
                
            except Exception as e:
                results.append({
                    'expected_name': name,
                    'qb_id': qb_id,
                    'found': False,
                    'error': str(e)
                })
                print(f"❌ {qb_id}: {name} - NOT FOUND ({e})")
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        
        found = [r for r in results if r['found']]
        not_found = [r for r in results if not r['found']]
        gc_compliance = [r for r in found if r.get('customer_type') == '698682']
        
        print(f"\nTotal customers checked: {len(CUSTOMER_IDS)}")
        print(f"Found in QuickBooks: {len(found)}")
        print(f"Not found: {len(not_found)}")
        print(f"With GC Compliance type (698682): {len(gc_compliance)}")
        
        if gc_compliance:
            print("\n✅ Ready to link (GC Compliance customers):")
            for r in gc_compliance:
                print(f"   {r['qb_id']}: {r['qb_name']}")
        
        if found and len(gc_compliance) < len(found):
            print("\n⚠️  Need CustomerType update:")
            for r in found:
                if r.get('customer_type') != '698682':
                    print(f"   {r['qb_id']}: {r['qb_name']} (Type: {r.get('customer_type')})")
        
        if not_found:
            print("\n❌ Not found in QuickBooks:")
            for r in not_found:
                print(f"   {r['qb_id']}: {r['expected_name']}")
        
        print("\n" + "=" * 70)
        
        return results

if __name__ == "__main__":
    asyncio.run(fetch_customers_by_get())
