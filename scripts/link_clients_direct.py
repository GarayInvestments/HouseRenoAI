"""
Directly link clients to QuickBooks customer IDs in database.
No QB API calls required - trusts the provided mapping.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from app.db.session import AsyncSessionLocal
from app.db.models import Client

# Client name → QB Customer ID mapping (user provided)
CLIENT_QB_MAPPING = {
    "Gustavo Roldan": "161",
    "Javier Martinez": "174",
    "Howard Nordin": "162",
    "Ajay Nair": "164",
    "Steve Jones": "165",
    "Marta Alder": "167",
    "Brandon Davis": "169"
}


async def link_clients():
    """Update database clients with QB customer IDs"""
    print("\n" + "="*70)
    print("LINK CLIENTS TO QUICKBOOKS (DIRECT DATABASE UPDATE)")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        try:
            # Get all clients
            result = await db.execute(select(Client))
            clients = result.scalars().all()
            
            # Create lookup by name (case-insensitive, strip whitespace)
            clients_by_name = {
                client.full_name.strip().lower(): client 
                for client in clients
            }
            
            print(f"\nFound {len(clients)} clients in database")
            print(f"Mapping {len(CLIENT_QB_MAPPING)} QB customers")
            
            updated_count = 0
            skipped_count = 0
            not_found_count = 0
            
            print("\n" + "-"*70)
            
            for client_name, qb_id in CLIENT_QB_MAPPING.items():
                name_key = client_name.strip().lower()
                
                if name_key not in clients_by_name:
                    print(f"❌ {client_name}: Not found in database")
                    not_found_count += 1
                    continue
                
                client = clients_by_name[name_key]
                
                # Check if already linked
                if client.qb_customer_id == qb_id:
                    print(f"⏭️  {client_name}: Already linked to QB {qb_id}")
                    skipped_count += 1
                    continue
                
                # Update the client
                old_id = client.qb_customer_id
                client.qb_customer_id = qb_id
                
                print(f"✅ {client_name}:")
                print(f"   Business ID: {client.business_id}")
                print(f"   QB ID: {old_id or 'None'} → {qb_id}")
                
                updated_count += 1
            
            # Commit changes
            await db.commit()
            
            print("\n" + "="*70)
            print("UPDATE SUMMARY")
            print("="*70)
            print(f"✅ Updated: {updated_count}")
            print(f"⏭️  Skipped (already linked): {skipped_count}")
            print(f"❌ Not found in DB: {not_found_count}")
            
            # Show final state
            print("\n" + "-"*70)
            print("FINAL CLIENT-QB MAPPING")
            print("-"*70)
            
            result = await db.execute(
                text("""
                    SELECT business_id, full_name, qb_customer_id
                    FROM clients
                    ORDER BY full_name
                """)
            )
            
            rows = result.fetchall()
            for row in rows:
                qb_status = f"→ QB {row.qb_customer_id}" if row.qb_customer_id else "(no QB link)"
                print(f"{row.business_id} - {row.full_name} {qb_status}")
            
            print("\n✅ Client linking complete!")
            print("\nNext step: Run QuickBooks sync to populate customer cache:")
            print("  POST https://houserenovators-api.fly.dev/v1/quickbooks/sync/customers")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(link_clients())
