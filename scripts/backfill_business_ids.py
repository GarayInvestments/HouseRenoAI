"""
Backfill business IDs for existing database records.

Purpose: Assign business_id values to records that were created before the business_id
         feature was added (via INSERT without triggers or data migration from Sheets).

Usage:
    # Dry run (preview changes)
    python scripts/backfill_business_ids.py --dry-run
    
    # Backfill specific entity
    python scripts/backfill_business_ids.py --entity clients
    
    # Backfill all entities
    python scripts/backfill_business_ids.py
    
    # Force backfill (overwrite existing business_ids)
    python scripts/backfill_business_ids.py --force

Features:
    - Idempotent: Safe to run multiple times
    - Dry-run mode for preview
    - Entity filtering (clients, projects, permits, payments)
    - Progress reporting
    - Atomic transactions per entity
    - Preserves existing business_ids (unless --force)
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Client, Project, Permit, Payment
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def backfill_clients(session: AsyncSession, dry_run: bool, force: bool) -> int:
    """Backfill business_ids for clients."""
    # Find clients without business_id
    query = select(Client)
    if not force:
        query = query.where(Client.business_id == None)
    
    result = await session.execute(query)
    clients = result.scalars().all()
    
    if not clients:
        print("✓ No clients need business_id backfill")
        return 0
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Found {len(clients)} clients to backfill")
    
    if dry_run:
        for client in clients[:5]:  # Show first 5 as preview
            print(f"  - {client.client_id}: {client.full_name or 'Unnamed'} → Would assign CL-XXXXX")
        if len(clients) > 5:
            print(f"  ... and {len(clients) - 5} more")
        return len(clients)
    
    # Execute backfill
    updated_count = 0
    for client in clients:
        # Trigger will auto-assign business_id if we set it to None and update
        # Alternatively, call the generation function directly
        result = await session.execute(
            select(Client).where(Client.client_id == client.client_id)
        )
        fresh_client = result.scalar_one()
        
        # If business_id is still None, we need to manually set it
        if fresh_client.business_id is None or force:
            # Use raw SQL to call the generation function
            from sqlalchemy import text
            result = await session.execute(
                text("SELECT generate_client_business_id()")
            )
            new_business_id = result.scalar()
            
            await session.execute(
                update(Client)
                .where(Client.client_id == client.client_id)
                .values(business_id=new_business_id)
            )
            updated_count += 1
            print(f"  ✓ {client.client_id}: {client.full_name or 'Unnamed'} → {new_business_id}")
    
    await session.commit()
    print(f"✓ Backfilled {updated_count} clients")
    return updated_count


async def backfill_projects(session: AsyncSession, dry_run: bool, force: bool) -> int:
    """Backfill business_ids for projects."""
    query = select(Project)
    if not force:
        query = query.where(Project.business_id == None)
    
    result = await session.execute(query)
    projects = result.scalars().all()
    
    if not projects:
        print("✓ No projects need business_id backfill")
        return 0
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Found {len(projects)} projects to backfill")
    
    if dry_run:
        for project in projects[:5]:
            print(f"  - {project.project_id}: {project.project_name or 'Unnamed'} → Would assign PRJ-XXXXX")
        if len(projects) > 5:
            print(f"  ... and {len(projects) - 5} more")
        return len(projects)
    
    updated_count = 0
    for project in projects:
        from sqlalchemy import text
        result = await session.execute(
            text("SELECT generate_project_business_id()")
        )
        new_business_id = result.scalar()
        
        await session.execute(
            update(Project)
            .where(Project.project_id == project.project_id)
            .values(business_id=new_business_id)
        )
        updated_count += 1
        print(f"  ✓ {project.project_id}: {project.project_name or 'Unnamed'} → {new_business_id}")
    
    await session.commit()
    print(f"✓ Backfilled {updated_count} projects")
    return updated_count


async def backfill_permits(session: AsyncSession, dry_run: bool, force: bool) -> int:
    """Backfill business_ids for permits."""
    query = select(Permit)
    if not force:
        query = query.where(Permit.business_id == None)
    
    result = await session.execute(query)
    permits = result.scalars().all()
    
    if not permits:
        print("✓ No permits need business_id backfill")
        return 0
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Found {len(permits)} permits to backfill")
    
    if dry_run:
        for permit in permits[:5]:
            print(f"  - {permit.permit_id}: {permit.permit_number or 'Unnamed'} → Would assign PRM-XXXXX")
        if len(permits) > 5:
            print(f"  ... and {len(permits) - 5} more")
        return len(permits)
    
    updated_count = 0
    for permit in permits:
        from sqlalchemy import text
        result = await session.execute(
            text("SELECT generate_permit_business_id()")
        )
        new_business_id = result.scalar()
        
        await session.execute(
            update(Permit)
            .where(Permit.permit_id == permit.permit_id)
            .values(business_id=new_business_id)
        )
        updated_count += 1
        print(f"  ✓ {permit.permit_id}: {permit.permit_number or 'Unnamed'} → {new_business_id}")
    
    await session.commit()
    print(f"✓ Backfilled {updated_count} permits")
    return updated_count


async def backfill_payments(session: AsyncSession, dry_run: bool, force: bool) -> int:
    """Backfill business_ids for payments."""
    query = select(Payment)
    if not force:
        query = query.where(Payment.business_id == None)
    
    result = await session.execute(query)
    payments = result.scalars().all()
    
    if not payments:
        print("✓ No payments need business_id backfill")
        return 0
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Found {len(payments)} payments to backfill")
    
    if dry_run:
        for payment in payments[:5]:
            print(f"  - {payment.payment_id}: ${payment.amount or 0} → Would assign PAY-XXXXX")
        if len(payments) > 5:
            print(f"  ... and {len(payments) - 5} more")
        return len(payments)
    
    updated_count = 0
    for payment in payments:
        from sqlalchemy import text
        result = await session.execute(
            text("SELECT generate_payment_business_id()")
        )
        new_business_id = result.scalar()
        
        await session.execute(
            update(Payment)
            .where(Payment.payment_id == payment.payment_id)
            .values(business_id=new_business_id)
        )
        updated_count += 1
        print(f"  ✓ {payment.payment_id}: ${payment.amount or 0} → {new_business_id}")
    
    await session.commit()
    print(f"✓ Backfilled {updated_count} payments")
    return updated_count


async def main(entity: Optional[str], dry_run: bool, force: bool):
    """Main backfill orchestration."""
    print("=" * 60)
    print("Business ID Backfill Script")
    print("=" * 60)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will modify database)'}")
    print(f"Entity filter: {entity or 'all'}")
    print(f"Force overwrite: {force}")
    print(f"Database: {settings.DATABASE_URL.split('@')[1]}")  # Hide credentials
    print("=" * 60)
    print()
    
    if not dry_run:
        confirm = input("⚠️  This will modify the database. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            return
    
    async with AsyncSessionLocal() as session:
        total_updated = 0
        
        entities_to_process = {
            'clients': backfill_clients,
            'projects': backfill_projects,
            'permits': backfill_permits,
            'payments': backfill_payments
        }
        
        # Filter entities if specified
        if entity:
            if entity not in entities_to_process:
                print(f"❌ Unknown entity: {entity}")
                print(f"   Valid options: {', '.join(entities_to_process.keys())}")
                return
            entities_to_process = {entity: entities_to_process[entity]}
        
        # Process each entity
        for entity_name, backfill_func in entities_to_process.items():
            print(f"\n📊 Processing {entity_name}...")
            try:
                count = await backfill_func(session, dry_run, force)
                total_updated += count
            except Exception as e:
                print(f"❌ Error processing {entity_name}: {e}")
                await session.rollback()
                raise
        
        print("\n" + "=" * 60)
        print(f"{'[DRY RUN] ' if dry_run else ''}Total records {'would be ' if dry_run else ''}updated: {total_updated}")
        print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill business IDs for existing database records"
    )
    parser.add_argument(
        "--entity",
        choices=["clients", "projects", "permits", "payments"],
        help="Backfill only this entity type"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying database"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing business_ids (regenerate)"
    )
    
    args = parser.parse_args()
    
    asyncio.run(main(args.entity, args.dry_run, args.force))
