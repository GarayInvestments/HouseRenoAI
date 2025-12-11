#!/usr/bin/env python3
"""
Schema validation script - compares database schema with SQLAlchemy models.
Run this before deploying to catch field name mismatches.
"""
import asyncio
import sys
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.models import Permit, Inspection, Invoice, Payment, SiteVisit
from app.config import settings

# Map model classes to table names
MODELS_TO_VALIDATE = {
    'permits': Permit,
    'inspections': Inspection,
    'invoices': Invoice,
    'payments': Payment,
    'site_visits': SiteVisit
}

async def get_db_columns(engine, table_name: str) -> set:
    """Get column names from database table."""
    async with engine.connect() as conn:
        result = await conn.execute(text(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            AND table_schema = 'public'
        """))
        return {row[0] for row in result}

def get_model_columns(model_class) -> set:
    """Get mapped column names from SQLAlchemy model."""
    mapper = inspect(model_class)
    return {col.key for col in mapper.columns}

async def validate_schema():
    """Compare database schema with models."""
    print("=" * 80)
    print("SCHEMA VALIDATION REPORT")
    print("=" * 80)
    print()
    
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    all_valid = True
    
    try:
        for table_name, model_class in MODELS_TO_VALIDATE.items():
            print(f"Validating {table_name}...")
            
            # Get columns from DB and model
            db_columns = await get_db_columns(engine, table_name)
            model_columns = get_model_columns(model_class)
            
            # Find mismatches
            in_db_not_model = db_columns - model_columns
            in_model_not_db = model_columns - db_columns
            
            if not in_db_not_model and not in_model_not_db:
                print(f"  ✅ {model_class.__name__} - All columns match!")
            else:
                all_valid = False
                print(f"  ❌ {model_class.__name__} - Mismatches found:")
                
                if in_db_not_model:
                    print(f"     In database but not in model: {sorted(in_db_not_model)}")
                
                if in_model_not_db:
                    print(f"     In model but not in database: {sorted(in_model_not_db)}")
            
            print()
    
    finally:
        await engine.dispose()
    
    print("=" * 80)
    if all_valid:
        print("✅ VALIDATION PASSED - All schemas match!")
        return 0
    else:
        print("❌ VALIDATION FAILED - Schema mismatches detected")
        print("   Run migrations or update models to resolve")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(validate_schema())
    sys.exit(exit_code)
