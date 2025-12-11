import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.db.models import Payment

async def check():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        result = await session.execute(select(Payment))
        payments = result.scalars().all()
        print(f'Existing payments: {len(payments)}')
        for p in payments:
            print(f'  - ID: {p.payment_id}, Business ID: {p.business_id}')

asyncio.run(check())
