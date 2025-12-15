"""
Test hybrid query with detailed logging to verify routing.
"""
import asyncio
import sys
import logging
from pathlib import Path

# Configure logging to see all INFO messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.quickbooks_service import QuickBooksService
from app.db.session import AsyncSessionLocal


async def test_routing():
    """Verify query routing behavior."""
    
    async with AsyncSessionLocal() as db:
        qb_service = QuickBooksService(db=db)
        
        # Load tokens (suppress SQLAlchemy logs)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        await qb_service.load_tokens_from_db()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        
        print("\n" + "=" * 80)
        print("ROUTING TEST - Watch for [QB QUERY] and [METRICS] logs")
        print("=" * 80)
        
        # Test 1: COUNT (should see HTTP routing)
        print("\n1. COUNT query (expect: 'Routing COUNT query to HTTP'):")
        await qb_service.query("SELECT COUNT(*) FROM Customer")
        
        # Test 2: Regular query (should see SDK routing)
        print("\n2. Regular query (expect: 'Routing query to SDK'):")
        await qb_service.query("SELECT * FROM Customer WHERE Active = true")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_routing())
