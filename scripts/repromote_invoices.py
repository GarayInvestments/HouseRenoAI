"""Re-promote invoices from cache to populate new QuickBooks fields."""
import asyncio
from app.services.quickbooks_sync_service import quickbooks_sync_service

async def main():
    print("Re-promoting invoices from cache...")
    result = await quickbooks_sync_service.promote_invoices_to_database()
    print(f"✓ Promoted: {result['promoted']}")
    print(f"  Skipped: {result['skipped']}")
    print(f"  Errors: {result['errors']}")
    
    if result['errors'] > 0:
        print("\nCheck logs for error details")

if __name__ == "__main__":
    asyncio.run(main())
