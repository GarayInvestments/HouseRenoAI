# Data Migration & Sync Script Best Practices

**Created**: Dec 15, 2025  
**Context**: Lessons learned from invoice sync script (13 rounds of debugging)

---

## 🎯 Pre-Flight Checklist (MANDATORY)

### 1. **Database Schema Inspection** (5 minutes, saves hours)

```powershell
# ALWAYS run these BEFORE writing migration scripts:

# Check table structure
psql "postgresql://..." -c "\d table_name"

# Check enum values (critical!)
psql "postgresql://..." -c "SELECT unnest(enum_range(NULL::enum_type_name))"

# Check constraints (NOT NULL, UNIQUE, etc.)
psql "postgresql://..." -c "SELECT column_name, is_nullable, column_default 
  FROM information_schema.columns WHERE table_name = 'your_table'"

# Sample actual data to see formats
psql "postgresql://..." -c "SELECT * FROM table_name LIMIT 3"
```

**What we missed**: 
- ❌ Assumed enum values were lowercase (`'sent'`) but they're UPPERCASE (`'SENT'`)
- ❌ Assumed `project_id` could be NULL but it was `NOT NULL`
- ❌ Didn't check actual JSONB structure before parsing

### 2. **Sample Data Extraction** (3 minutes, prevents 5+ bugs)

```python
# ALWAYS inspect source data first
async with AsyncSessionLocal() as session:
    result = await session.execute(
        text("SELECT * FROM source_table LIMIT 1")
    )
    sample = result.fetchone()
    
    # Print EVERYTHING
    print("Sample record:")
    for key, value in sample._mapping.items():
        print(f"  {key}: {value!r} (type: {type(value).__name__})")
    
    # For JSONB fields, print full structure
    if hasattr(sample, 'qb_data'):
        print("\nQB Data structure:")
        print(json.dumps(sample.qb_data, indent=2))
```

**What we missed**:
- ❌ Didn't check that `SalesItemLineDetail` could be `None`
- ❌ Didn't verify date format (string vs datetime)

### 3. **Incremental Testing Pattern** (test 1 record, not 13)

```python
# Add a LIMIT parameter for testing
async def sync_qb_invoices(limit: int = None):
    """Sync QB invoices to internal database.
    
    Args:
        limit: For testing - sync only N invoices (default: all)
    """
    query = "SELECT ... FROM quickbooks_invoices_cache WHERE is_active = true"
    if limit:
        query += f" LIMIT {limit}"
    
    # ... rest of sync logic

# Test with 1 record first
if __name__ == '__main__':
    import sys
    test_limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(sync_qb_invoices(limit=test_limit))
```

**Usage**:
```powershell
# Test with 1 record
python scripts/sync_script.py 1

# Test with 3 records
python scripts/sync_script.py 3

# Run full sync
python scripts/sync_script.py
```

---

## 🛡️ Code Patterns That Prevent Bugs

### 1. **Always Use ORM Over Raw SQL**

❌ **BAD** (caused SQL parameter syntax errors):
```python
query = text("""
    INSERT INTO invoices (...) 
    VALUES (:param1::uuid, :param2::timestamp, ...)
""")
await session.execute(query, params)
```

✅ **GOOD** (SQLAlchemy handles types automatically):
```python
new_invoice = Invoice(
    project_id=UUID(data['project_id']) if data['project_id'] else None,
    invoice_date=datetime.fromisoformat(data['invoice_date']),
    status=data['status']  # SQLAlchemy validates enum
)
session.add(new_invoice)
```

### 2. **Explicit Type Conversion**

❌ **BAD** (assumes data is correct type):
```python
invoice_data = {
    'invoice_date': qb_data.get('TxnDate'),  # String!
    'client_id': client.client_id,  # UUID object!
    'status': 'sent'  # Wrong case!
}
```

✅ **GOOD** (explicit conversions with fallbacks):
```python
from datetime import datetime
from uuid import UUID

# Dates: always parse strings
invoice_date_str = qb_data.get('TxnDate')
invoice_date = datetime.fromisoformat(invoice_date_str) if invoice_date_str else None

# UUIDs: convert to string or UUID consistently
client_id = UUID(str(client.client_id))

# Enums: always uppercase, use mapping
status = map_qb_status(qb_data.get('Status')).upper()
```

### 3. **Defensive JSONB Parsing**

❌ **BAD** (crashes on None):
```python
item_name = detail.get('ItemRef', {}).get('name', '')  # Error if ItemRef is None!
```

✅ **GOOD** (handles None):
```python
detail = line.get('SalesItemLineDetail') or {}
item_ref = detail.get('ItemRef') or {}
item_name = item_ref.get('name', '')
```

### 4. **Avoid Unicode in Windows Scripts**

❌ **BAD** (Windows terminal encoding errors):
```python
print("🔍 Searching...")
print("✅ Success!")
```

✅ **GOOD** (ASCII-safe):
```python
print("[*] Searching...")
print("[OK] Success!")
```

### 5. **Validate Imports Early**

✅ **Add at top of script**:
```python
# Validate imports immediately
try:
    from app.db.session import AsyncSessionLocal
    from app.db.models import Invoice, Client, Permit
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    print("Available in app.db.session:", dir(__import__('app.db.session')))
    sys.exit(1)
```

---

## 🧪 Testing Strategy

### Dry-Run Mode (ALWAYS implement this)

```python
async def sync_qb_invoices(dry_run: bool = True, limit: int = None):
    """
    Args:
        dry_run: If True, print what would be done without committing
        limit: Max records to process (for testing)
    """
    # ... processing logic ...
    
    if dry_run:
        print("\n[DRY RUN] Would have created/updated:")
        for invoice in invoices_to_create:
            print(f"  - {invoice.invoice_number}")
        print("\n[DRY RUN] No changes made. Run with --commit to apply.")
        await session.rollback()
    else:
        await session.commit()
        print(f"[OK] Committed {len(invoices_to_create)} invoices")

# CLI usage
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', action='store_true', help='Actually commit changes')
    parser.add_argument('--limit', type=int, help='Process only N records')
    args = parser.parse_args()
    
    asyncio.run(sync_qb_invoices(dry_run=not args.commit, limit=args.limit))
```

**Workflow**:
```powershell
# 1. Test with 1 record, dry-run
python scripts/sync.py --limit 1

# 2. Test with 3 records, dry-run
python scripts/sync.py --limit 3

# 3. Full sync, dry-run
python scripts/sync.py

# 4. Commit (only after above passes)
python scripts/sync.py --commit
```

---

## 📋 Pre-Migration Validation Script

Create `scripts/validate_migration.py`:

```python
"""Validates data migration readiness before running sync."""
import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def validate_migration():
    """Run all validation checks."""
    print("="*80)
    print("MIGRATION VALIDATION CHECKS")
    print("="*80)
    
    async with AsyncSessionLocal() as session:
        # 1. Check source data exists
        result = await session.execute(
            text("SELECT COUNT(*) FROM quickbooks_invoices_cache WHERE is_active = true")
        )
        source_count = result.scalar()
        print(f"✓ Source records found: {source_count}")
        
        # 2. Check target table schema
        result = await session.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'invoices'
            ORDER BY ordinal_position
        """))
        print("\n✓ Target table schema:")
        for row in result:
            nullable = "NULL" if row.is_nullable == 'YES' else "NOT NULL"
            print(f"  {row.column_name}: {row.data_type} ({nullable})")
        
        # 3. Check enum values
        result = await session.execute(
            text("SELECT unnest(enum_range(NULL::invoice_status_enum))")
        )
        enum_values = [row[0] for row in result]
        print(f"\n✓ Invoice status enum values: {enum_values}")
        
        # 4. Check foreign key targets exist
        result = await session.execute(
            text("SELECT COUNT(*) FROM clients WHERE qb_customer_id IS NOT NULL")
        )
        linked_clients = result.scalar()
        print(f"\n✓ Clients with QB IDs: {linked_clients}")
        
        # 5. Sample JSONB structure
        result = await session.execute(
            text("SELECT qb_data FROM quickbooks_invoices_cache LIMIT 1")
        )
        sample_qb = result.scalar()
        print(f"\n✓ Sample QB data keys: {list(sample_qb.keys())}")
        print(f"  - TxnDate type: {type(sample_qb.get('TxnDate'))}")
        print(f"  - EmailStatus: {sample_qb.get('EmailStatus')}")
        if 'Line' in sample_qb and len(sample_qb['Line']) > 0:
            line = sample_qb['Line'][0]
            print(f"  - Line[0] keys: {list(line.keys())}")
            if 'SalesItemLineDetail' in line:
                detail = line['SalesItemLineDetail']
                print(f"  - SalesItemLineDetail type: {type(detail)}")
    
    print("\n" + "="*80)
    print("[OK] Validation complete. Review above before running sync.")
    print("="*80)

if __name__ == '__main__':
    asyncio.run(validate_migration())
```

---

## 🎓 Lessons from Invoice Sync Debugging

| Error | Root Cause | Prevention |
|-------|-----------|------------|
| SQL syntax error (`:param::cast`) | Mixed named + positional params | Use ORM or pure named params |
| Unicode encoding error | Emoji on Windows | Use ASCII only: `[OK]` not `✅` |
| Import error | Wrong name in import | Check `dir(module)` first |
| Date type mismatch | String passed to datetime field | Explicit `datetime.fromisoformat()` |
| Enum value rejected | Lowercase `'sent'` vs `'SENT'` | Check enum values with psql |
| NOT NULL violation | Assumed NULL allowed | Check `\d table_name` constraints |
| None.get() crash | JSONB field was None | Use `or {}` pattern |

---

## 🚀 Quick Start Template

```python
"""
Data migration script template with all best practices.
"""
import asyncio
import json
from datetime import datetime
from uuid import UUID
from sqlalchemy import text, select
from app.db.session import AsyncSessionLocal
from app.db.models import YourModel

async def validate_before_sync():
    """Pre-flight checks."""
    print("[*] Running validation...")
    # Add schema checks, enum checks, sample data inspection
    print("[OK] Validation passed\n")

async def sync_data(dry_run: bool = True, limit: int = None):
    """Main sync logic."""
    stats = {'created': 0, 'updated': 0, 'skipped': 0}
    
    async with AsyncSessionLocal() as session:
        # Fetch source data with optional limit
        query = select(SourceTable)
        if limit:
            query = query.limit(limit)
        
        result = await session.execute(query)
        records = result.scalars().all()
        
        print(f"[*] Processing {len(records)} records...")
        
        for record in records:
            try:
                # Parse data with explicit type conversions
                data = parse_record(record)
                
                # Check if exists
                existing = await find_existing(session, data['unique_key'])
                
                if existing:
                    # Update
                    update_model(existing, data)
                    stats['updated'] += 1
                else:
                    # Create using ORM
                    new_obj = YourModel(**data)
                    session.add(new_obj)
                    stats['created'] += 1
                
            except Exception as e:
                print(f"[ERROR] {record.id}: {e}")
                stats['skipped'] += 1
        
        # Dry run or commit
        if dry_run:
            print("\n[DRY RUN] Would have made these changes:")
            print(f"  Created: {stats['created']}")
            print(f"  Updated: {stats['updated']}")
            print(f"  Skipped: {stats['skipped']}")
            await session.rollback()
        else:
            await session.commit()
            print(f"\n[OK] Committed: {stats}")

def parse_record(record) -> dict:
    """Parse with explicit type conversions."""
    return {
        'date_field': datetime.fromisoformat(record.date_str) if record.date_str else None,
        'uuid_field': UUID(str(record.uuid_field)) if record.uuid_field else None,
        'enum_field': map_enum(record.status).upper(),
        'jsonb_field': (record.jsonb_field or {}).get('key', 'default')
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', action='store_true')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    
    asyncio.run(validate_before_sync())
    asyncio.run(sync_data(dry_run=not args.commit, limit=args.limit))
```

---

## ✅ Pre-Commit Checklist

Before running ANY data migration:

- [ ] Ran validation script
- [ ] Checked database schema with psql
- [ ] Inspected enum values
- [ ] Tested with `--limit 1`
- [ ] Tested with `--limit 3`
- [ ] Ran full dry-run (no --commit)
- [ ] Reviewed dry-run output
- [ ] Backed up data (if destructive)
- [ ] Added rollback plan to docs

**Time investment**: 10-15 minutes  
**Bugs prevented**: 5-10+ errors  
**Net savings**: Hours of debugging
