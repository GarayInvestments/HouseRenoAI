#!/usr/bin/env python3
"""
Direct QuickBooks sync script - runs without API authentication.

Uses the backend's existing QuickBooks OAuth connection to import data directly.
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import get_db
from app.services.quickbooks_sync_service import qb_sync_service
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Import all QuickBooks data: customers, invoices, payments."""
    
    print("\n🔄 QuickBooks Data Import (Direct Backend)")
    print("=" * 50)
    print("\nThis will import:")
    print("  • Customers (GC Compliance only)")
    print("  • Invoices (linked to GC Compliance customers)")
    print("  • Payments (linked to GC Compliance invoices)")
    print()
    
    confirm = input("Start import? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Import cancelled")
        return
    
    print()
    
    # Get database session
    async for db in get_db():
        results = {}
        
        try:
            # Clear sync_status to force full sync
            print("🔄 Resetting sync status for full import...")
            await db.execute(text("DELETE FROM sync_status WHERE entity_type IN ('customers', 'invoices', 'payments')"))
            await db.commit()
            print()
            
            # Step 1: Customers
            print("📋 Step 1/3: Importing customers...")
            result = await qb_sync_service.sync_customers(db, since=None)  # Force full sync
            results['customers'] = result
            print(f"✅ Customers: {result['created']} created, {result['updated']} updated, {result['skipped']} skipped")
            print()
            
            # Step 2: Invoices
            print("📋 Step 2/3: Importing invoices...")
            result = await qb_sync_service.sync_invoices(db, since=None)
            results['invoices'] = result
            print(f"✅ Invoices: {result['created']} created, {result['updated']} updated, {result['skipped']} skipped")
            print()
            
            # Step 3: Payments
            print("📋 Step 3/3: Importing payments...")
            result = await qb_sync_service.sync_payments(db, since=None)
            results['payments'] = result
            print(f"✅ Payments: {result['created']} created, {result['updated']} updated, {result['skipped']} skipped")
            print()
            
            # Summary
            print("=" * 50)
            print("📊 Import Summary")
            print("=" * 50)
            total_created = sum(r['created'] for r in results.values())
            total_updated = sum(r['updated'] for r in results.values())
            total_skipped = sum(r['skipped'] for r in results.values())
            
            print(f"Total created: {total_created}")
            print(f"Total updated: {total_updated}")
            print(f"Total skipped: {total_skipped}")
            print()
            print("✅ QuickBooks import complete!")
            print()
            
        except Exception as e:
            logger.error(f"Import failed: {e}", exc_info=True)
            print(f"\n❌ Import failed: {e}")
            print("Check logs for details.")
            sys.exit(1)
        
        break  # Only use first session


if __name__ == "__main__":
    asyncio.run(main())
