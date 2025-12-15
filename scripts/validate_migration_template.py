"""
Migration validation template - run BEFORE any data sync script.

Usage:
    python scripts/validate_migration_template.py

Customize the checks for your specific migration.
"""
import asyncio
import json
from sqlalchemy import text
from app.db.session import AsyncSessionLocal


async def validate_migration():
    """Run comprehensive validation checks before migration."""
    
    print("="*80)
    print("MIGRATION VALIDATION CHECKS")
    print("="*80 + "\n")
    
    async with AsyncSessionLocal() as session:
        
        # ========== 1. SOURCE DATA CHECKS ==========
        print("[1] Checking source data...")
        
        # Count source records
        result = await session.execute(
            text("SELECT COUNT(*) FROM source_table WHERE is_active = true")
        )
        source_count = result.scalar()
        print(f"    [OK] Source records: {source_count}")
        
        # Sample source data
        result = await session.execute(
            text("SELECT * FROM source_table LIMIT 1")
        )
        sample = result.fetchone()
        if sample:
            print(f"    [OK] Sample record fields: {list(sample._mapping.keys())}")
        
        # ========== 2. TARGET SCHEMA CHECKS ==========
        print("\n[2] Checking target table schema...")
        
        result = await session.execute(text("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = 'target_table'
            ORDER BY ordinal_position
        """))
        
        print("    Target table columns:")
        for row in result:
            nullable = "NULL" if row.is_nullable == 'YES' else "NOT NULL"
            default = f" (default: {row.column_default})" if row.column_default else ""
            print(f"      - {row.column_name}: {row.data_type} {nullable}{default}")
        
        # ========== 3. ENUM VALUE CHECKS ==========
        print("\n[3] Checking enum types...")
        
        # Check if enum type exists
        result = await session.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'your_enum_type'
            )
        """))
        enum_exists = result.scalar()
        
        if enum_exists:
            result = await session.execute(
                text("SELECT unnest(enum_range(NULL::your_enum_type))")
            )
            enum_values = [row[0] for row in result]
            print(f"    [OK] Enum 'your_enum_type' values: {enum_values}")
        else:
            print("    [WARNING] Enum type 'your_enum_type' not found")
        
        # ========== 4. FOREIGN KEY CHECKS ==========
        print("\n[4] Checking foreign key targets...")
        
        # Check referenced tables exist and have data
        result = await session.execute(
            text("SELECT COUNT(*) FROM clients WHERE qb_customer_id IS NOT NULL")
        )
        linked_count = result.scalar()
        print(f"    [OK] Clients with QB IDs: {linked_count}")
        
        # ========== 5. JSONB STRUCTURE INSPECTION ==========
        print("\n[5] Inspecting JSONB data structures...")
        
        result = await session.execute(
            text("SELECT jsonb_field FROM source_table WHERE jsonb_field IS NOT NULL LIMIT 1")
        )
        sample_jsonb = result.scalar()
        
        if sample_jsonb:
            print(f"    [OK] JSONB top-level keys: {list(sample_jsonb.keys())}")
            
            # Inspect nested structures
            if 'nested_array' in sample_jsonb and len(sample_jsonb['nested_array']) > 0:
                first_item = sample_jsonb['nested_array'][0]
                print(f"    [OK] First array item keys: {list(first_item.keys())}")
                
                # Check for potential None values
                for key, value in first_item.items():
                    if value is None:
                        print(f"    [WARNING] Field '{key}' can be None")
        
        # ========== 6. DATA TYPE SAMPLING ==========
        print("\n[6] Sampling data types...")
        
        result = await session.execute(
            text("SELECT date_field, status_field FROM source_table LIMIT 3")
        )
        samples = result.fetchall()
        
        for i, sample in enumerate(samples, 1):
            print(f"    Sample {i}:")
            for key, value in sample._mapping.items():
                print(f"      {key}: {value!r} (type: {type(value).__name__})")
        
        # ========== 7. CONSTRAINT CHECKS ==========
        print("\n[7] Checking constraints...")
        
        result = await session.execute(text("""
            SELECT 
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'target_table'
            ORDER BY tc.constraint_type, kcu.ordinal_position
        """))
        
        constraints = result.fetchall()
        if constraints:
            print("    Target table constraints:")
            for constraint in constraints:
                print(f"      - {constraint.constraint_type}: {constraint.column_name} ({constraint.constraint_name})")
        
        # ========== 8. INDEX CHECKS ==========
        print("\n[8] Checking indexes...")
        
        result = await session.execute(text("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = 'target_table'
        """))
        
        indexes = result.fetchall()
        if indexes:
            print("    Target table indexes:")
            for idx in indexes:
                print(f"      - {idx.indexname}")
        
    print("\n" + "="*80)
    print("[OK] VALIDATION COMPLETE")
    print("="*80)
    print("\nReview the output above before running your migration script.")
    print("Update this script to match your specific migration needs.\n")


if __name__ == '__main__':
    asyncio.run(validate_migration())
