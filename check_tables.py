import asyncio
from app.db.session import engine
from sqlalchemy import text

async def check_tables():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"))
        tables = [row[0] for row in result]
        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
        
        # Check row counts
        print("\nRow counts:")
        for table in tables:
            result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  {table}: {count} rows")

if __name__ == "__main__":
    asyncio.run(check_tables())
