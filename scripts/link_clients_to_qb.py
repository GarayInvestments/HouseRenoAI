"""
Link Internal Clients to QuickBooks Customers

Matches internal clients with QB customers by name and email,
then updates the clients.qb_customer_id field.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models import Client
import re


def normalize_name(name: str) -> str:
    """Normalize name for matching (lowercase, remove extra spaces)."""
    if not name:
        return ""
    return re.sub(r'\s+', ' ', name.strip().lower())


def normalize_email(email: str) -> str:
    """Normalize email for matching (lowercase, strip)."""
    if not email:
        return ""
    return email.strip().lower()


async def get_qb_customers(session: AsyncSession):
    """Fetch all QB customers from cache."""
    result = await session.execute(
        text("""
            SELECT qb_customer_id, display_name, company_name, email, given_name, family_name
            FROM quickbooks_customers_cache
            WHERE is_active = true
            ORDER BY display_name
        """)
    )
    return result.fetchall()


async def get_internal_clients(session: AsyncSession):
    """Fetch all internal clients."""
    result = await session.execute(
        select(Client).order_by(Client.full_name)
    )
    return result.scalars().all()


def find_qb_match(client, qb_customers):
    """
    Find matching QB customer for internal client.
    
    Tries:
    1. Exact name match (display_name or company_name)
    2. Email match
    3. Given name + family name match
    """
    client_name_norm = normalize_name(client.full_name)
    client_email_norm = normalize_email(client.email)
    
    for qb in qb_customers:
        # Try display_name match
        if normalize_name(qb.display_name) == client_name_norm:
            return qb, "exact_name"
        
        # Try company_name match
        if qb.company_name and normalize_name(qb.company_name) == client_name_norm:
            return qb, "company_name"
        
        # Try email match
        if client_email_norm and qb.email and normalize_email(qb.email) == client_email_norm:
            return qb, "email"
        
        # Try given + family name match
        if qb.given_name and qb.family_name:
            qb_full_name = normalize_name(f"{qb.given_name} {qb.family_name}")
            if qb_full_name == client_name_norm:
                return qb, "given_family_name"
    
    return None, None


async def link_clients_to_qb():
    """Main function to link clients to QB customers."""
    async with AsyncSessionLocal() as session:
        print("🔍 Fetching data...")
        
        # Get all QB customers
        qb_customers = await get_qb_customers(session)
        print(f"   Found {len(qb_customers)} QB customers")
        
        # Get all internal clients
        clients = await get_internal_clients(session)
        print(f"   Found {len(clients)} internal clients")
        
        print("\n" + "="*80)
        print("MATCHING CLIENTS TO QUICKBOOKS CUSTOMERS")
        print("="*80 + "\n")
        
        matches = []
        unmatched_clients = []
        
        for client in clients:
            qb_match, match_type = find_qb_match(client, qb_customers)
            
            if qb_match:
                matches.append({
                    'client': client,
                    'qb': qb_match,
                    'match_type': match_type
                })
                print(f"✅ MATCH ({match_type}):")
                print(f"   Client: {client.full_name} ({client.email or 'no email'})")
                print(f"   QB:     {qb_match.display_name} (ID: {qb_match.qb_customer_id})")
                print()
            else:
                unmatched_clients.append(client)
                print(f"⚠️  NO MATCH:")
                print(f"   Client: {client.full_name} ({client.email or 'no email'})")
                print()
        
        # Show unmatched QB customers
        matched_qb_ids = {m['qb'].qb_customer_id for m in matches}
        unmatched_qb = [qb for qb in qb_customers if qb.qb_customer_id not in matched_qb_ids]
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"✅ Matched: {len(matches)}")
        print(f"⚠️  Unmatched clients: {len(unmatched_clients)}")
        print(f"⚠️  Unmatched QB customers: {len(unmatched_qb)}")
        
        if unmatched_clients:
            print("\n📋 Unmatched Internal Clients:")
            for client in unmatched_clients:
                print(f"   - {client.full_name} ({client.email or 'no email'})")
        
        if unmatched_qb:
            print("\n📋 Unmatched QB Customers:")
            for qb in unmatched_qb:
                print(f"   - {qb.display_name} (ID: {qb.qb_customer_id})")
        
        # Ask for confirmation
        print("\n" + "="*80)
        print("CONFIRMATION")
        print("="*80)
        response = input(f"\nUpdate {len(matches)} clients with QB customer IDs? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Aborted. No changes made.")
            return
        
        # Update clients
        print("\n🔄 Updating clients...")
        updated_count = 0
        
        for match in matches:
            client = match['client']
            qb = match['qb']
            
            await session.execute(
                update(Client)
                .where(Client.client_id == client.client_id)
                .values(
                    qb_customer_id=qb.qb_customer_id,
                    qb_display_name=qb.display_name
                )
            )
            updated_count += 1
            print(f"   ✅ Updated: {client.full_name} → QB ID {qb.qb_customer_id}")
        
        await session.commit()
        
        print(f"\n✅ Successfully updated {updated_count} clients!")
        print("\n📊 Next Steps:")
        print("   1. Run: python scripts/sync_qb_invoices_to_internal.py")
        print("   2. Restart frontend to see unified invoices")


if __name__ == "__main__":
    print("="*80)
    print("CLIENT TO QUICKBOOKS LINKING SCRIPT")
    print("="*80)
    print()
    
    asyncio.run(link_clients_to_qb())
