import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def check_schema():
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        # Check payment_id column
        result = await conn.execute(text("""
            SELECT column_name, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'payments' AND column_name IN ('payment_id', 'business_id')
            ORDER BY ordinal_position
        """))
        
        print("Payments table columns:")
        for row in result:
            print(f"  {row[0]}: default={row[1]}, nullable={row[2]}")
        
        # Check triggers
        result = await conn.execute(text("""
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers
            WHERE event_object_table = 'payments'
        """))
        
        print("\nPayments table triggers:")
        for row in result:
            print(f"  {row[0]} - {row[1]}: {row[2][:100]}...")

asyncio.run(check_schema())
