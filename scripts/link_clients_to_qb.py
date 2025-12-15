"""
Link existing clients in database to QuickBooks customer IDs.

Maps client names to QB customer IDs and updates the database.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, update
from app.db.session import AsyncSessionLocal
from app.db.models import Client
from app.services.quickbooks_service import get_quickbooks_service

# Client name → QB Customer ID mapping (provided by user)
CLIENT_QB_MAPPING = {
    "Gustavo Roldan": "161",
    "Javier Martinez": "174",
    "Howard Nordin": "162",
    "Ajay Nair": "164",
    "Steve Jones": "165",
    "Marta Alder": "167",
    "Brandon Davis": "169"
}


async def verify_qb_customers(db: AsyncSession):
    """Query QuickBooks to verify these customer IDs and check GC Compliance status"""
    print("\n" + "="*70)
    print("STEP 1: VERIFY QUICKBOOKS CUSTOMERS")
    print("="*70)
    
    qb_service = get_quickbooks_service(db)
    
    verified = {}
    errors = []
    
    for name, qb_id in CLIENT_QB_MAPPING.items():
        try:
            # Query specific customer by ID
            query = f"SELECT * FROM Customer WHERE Id = '{qb_id}'"
            customers = await qb_service.query(query)
            
            if not customers:
                errors.append(f"❌ {name}: QB ID {qb_id} not found")
                continue
            
            customer = customers[0]
            display_name = customer.get('DisplayName', 'N/A')
            customer_type_ref = customer.get('CustomerTypeRef', {})
            customer_type_id = customer_type_ref.get('value') if customer_type_ref else None
            
            # Check if GC Compliance (698682)
            is_gc_compliance = customer_type_id == "698682"
            status = "✅ GC Compliance" if is_gc_compliance else f"⚠️  Type: {customer_type_id}"
            
            print(f"\n{name}:")
            print(f"  QB ID: {qb_id}")
            print(f"  QB Name: {display_name}")
            print(f"  Status: {status}")
            
            verified[name] = {
                "qb_id": qb_id,
                "qb_name": display_name,
                "is_gc_compliance": is_gc_compliance
            }
            
        except Exception as e:
            errors.append(f"❌ {name}: Error querying QB - {e}")
            print(f"\n{name}: ❌ Error - {e}")
    
    if errors:
        print("\n⚠️  Errors encountered:")
        for error in errors:
            print(f"  {error}")
    
    return verified


async def get_database_clients(db: AsyncSession):
    """Get all clients from database"""
    print("\n" + "="*70)
    print("STEP 2: GET DATABASE CLIENTS")
    print("="*70)
    
    result = await db.execute(
        select(Client).order_by(Client.full_name)
    )
    clients = result.scalars().all()
    
    print(f"\nFound {len(clients)} clients in database:")
    for client in clients:
        qb_status = f"QB: {client.qb_customer_id}" if client.qb_customer_id else "No QB ID"
        print(f"  {client.business_id} - {client.full_name} ({qb_status})")
    
    return clients


async def link_clients(db: AsyncSession, verified_customers: dict):
    """Update database clients with QB customer IDs"""
    print("\n" + "="*70)
    print("STEP 3: LINK CLIENTS TO QUICKBOOKS")
    print("="*70)
    
    # Get all clients
    result = await db.execute(select(Client))
    clients = result.scalars().all()
    
    # Create lookup by name (case-insensitive, strip whitespace)
    clients_by_name = {
        client.full_name.strip().lower(): client 
        for client in clients
    }
    
    updated_count = 0
    skipped_count = 0
    not_found_count = 0
    
    for client_name, qb_data in verified_customers.items():
        name_key = client_name.strip().lower()
        
        if name_key not in clients_by_name:
            print(f"\n❌ {client_name}: Not found in database")
            not_found_count += 1
            continue
        
        client = clients_by_name[name_key]
        qb_id = qb_data['qb_id']
        
        # Check if already linked
        if client.qb_customer_id == qb_id:
            print(f"\n⏭️  {client_name}: Already linked to QB ID {qb_id}")
            skipped_count += 1
            continue
        
        # Update the client
        client.qb_customer_id = qb_id
        
        print(f"\n✅ {client_name}:")
        print(f"   DB ID: {client.business_id}")
        print(f"   QB ID: {qb_id} ({qb_data['qb_name']})")
        print(f"   GC Compliance: {'Yes' if qb_data['is_gc_compliance'] else 'No'}")
        
        updated_count += 1
    
    # Commit changes
    await db.commit()
    
    print("\n" + "="*70)
    print("LINK SUMMARY")
    print("="*70)
    print(f"✅ Updated: {updated_count}")
    print(f"⏭️  Skipped (already linked): {skipped_count}")
    print(f"❌ Not found in DB: {not_found_count}")
    print("="*70)


async def verify_links(db: AsyncSession):
    """Verify the links were created successfully"""
    print("\n" + "="*70)
    print("STEP 4: VERIFY LINKS")
    print("="*70)
    
    result = await db.execute(
        text("""
            SELECT 
                c.business_id,
                c.full_name,
                c.qb_customer_id,
                qbc.display_name as qb_name,
                qbc.is_active as qb_active
            FROM clients c
            LEFT JOIN quickbooks_customers_cache qbc ON c.qb_customer_id = qbc.qb_customer_id
            ORDER BY c.full_name
        """)
    )
    
    rows = result.fetchall()
    
    print(f"\nAll clients with QB status:")
    linked = 0
    unlinked = 0
    
    for row in rows:
        if row.qb_customer_id:
            cache_status = f" (cached: {row.qb_name})" if row.qb_name else " (not in cache)"
            print(f"  ✅ {row.business_id} - {row.full_name} → QB {row.qb_customer_id}{cache_status}")
            linked += 1
        else:
            print(f"  ⚪ {row.business_id} - {row.full_name} (no QB link)")
            unlinked += 1
    
    print(f"\nTotal: {linked} linked, {unlinked} unlinked")


async def main():
    """Run the linking process"""
    print("\n" + "="*80)
    print(" LINK CLIENTS TO QUICKBOOKS CUSTOMERS")
    print("="*80)
    
    async with AsyncSessionLocal() as db:
        try:
            # Step 1: Verify QB customers exist and check GC Compliance status
            verified = await verify_qb_customers(db)
            
            if not verified:
                print("\n❌ No customers verified. Aborting.")
                return
            
            # Step 2: Show database clients
            await get_database_clients(db)
            
            # Step 3: Link clients to QB
            await link_clients(db, verified)
            
            # Step 4: Verify the links
            await verify_links(db)
            
            print("\n✅ Client linking complete!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(main())
