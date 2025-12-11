"""
Backfill business IDs for existing records (Phase A.2 Task 2.5)

Assigns business IDs to all existing records in chronological order (created_at ASC).
Idempotent - skips records with existing business_id.
Uses raw SQL for simplicity and performance.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.config import settings


async def backfill_business_ids():
    """Backfill business IDs for all existing records"""
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("\n" + "="*80)
        print("BACKFILL BUSINESS IDs - PHASE A.2 TASK 2.5")
        print("="*80)
        print("\nStrategy:")
        print("  1. Process records in chronological order (created_at ASC)")
        print("  2. Skip records with existing business_id")
        print("  3. Assign sequential business IDs using sequences")
        print("  4. Idempotent - safe to run multiple times")
        print("="*80)
        
        # Tables to backfill: (table_name, id_column, sequence_name, prefix)
        tables = [
            ("clients", "client_id", "client_business_id_seq", "CL"),
            ("projects", "project_id", "project_business_id_seq", "PRJ"),
            ("permits", "permit_id", "permit_business_id_seq", "PER"),
            ("inspections", "inspection_id", "inspection_business_id_seq", "INS"),
            ("invoices", "invoice_id", "invoice_business_id_seq", "INV"),
            ("payments", "payment_id", "payment_business_id_seq", "PAY"),
            ("site_visits", "visit_id", "site_visit_business_id_seq", "SV"),
        ]
        
        total_backfilled = 0
        total_skipped = 0
        
        for table_name, id_column, seq_name, prefix in tables:
            print(f"\n" + "-"*80)
            print(f"Processing: {table_name.upper()}")
            print("-"*80)
            
            # Count records needing backfill
            count_query = text(f"""
                SELECT COUNT(*) 
                FROM {table_name} 
                WHERE business_id IS NULL
            """)
            result = await session.execute(count_query)
            null_count = result.scalar()
            
            # Count records with business_id
            has_id_query = text(f"""
                SELECT COUNT(*) 
                FROM {table_name} 
                WHERE business_id IS NOT NULL
            """)
            result = await session.execute(has_id_query)
            has_id_count = result.scalar()
            
            print(f"  Records without business_id: {null_count}")
            print(f"  Records with business_id: {has_id_count}")
            
            if null_count == 0:
                print(f"  ✅ All {table_name} already have business IDs")
                total_skipped += has_id_count
                continue
            
            # Backfill in chronological order
            # This UPDATE with CTE ensures records are processed in created_at order
            backfill_query = text(f"""
                WITH ordered_records AS (
                    SELECT {id_column}
                    FROM {table_name}
                    WHERE business_id IS NULL
                    ORDER BY created_at ASC
                )
                UPDATE {table_name}
                SET business_id = :prefix || '-' || LPAD(nextval(:seq_name)::TEXT, 5, '0')
                FROM ordered_records
                WHERE {table_name}.{id_column} = ordered_records.{id_column}
                RETURNING {table_name}.business_id
            """)
            
            result = await session.execute(
                backfill_query,
                {"prefix": prefix, "seq_name": seq_name}
            )
            backfilled_ids = result.fetchall()
            
            await session.commit()
            
            count_backfilled = len(backfilled_ids)
            total_backfilled += count_backfilled
            total_skipped += has_id_count
            
            print(f"  ✅ Backfilled {count_backfilled} records")
            if count_backfilled > 0:
                print(f"     First: {backfilled_ids[0][0]}")
                print(f"     Last: {backfilled_ids[-1][0]}")
        
        print("\n" + "="*80)
        print("BACKFILL COMPLETE!")
        print("="*80)
        print(f"  Total records backfilled: {total_backfilled}")
        print(f"  Total records skipped (already had ID): {total_skipped}")
        print("\n  ✅ All existing records now have business IDs")
        print("  ✅ New records will auto-generate IDs via triggers")
        print("\n  Next: Update tracker and commit Phase A.2")
        print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(backfill_business_ids())
