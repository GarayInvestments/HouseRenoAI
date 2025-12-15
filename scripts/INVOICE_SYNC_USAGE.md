# Invoice Sync Script - Usage Guide

## Quick Reference

```powershell
# Test with 1 invoice (dry-run, safe)
python scripts/sync_qb_invoices_to_internal.py --limit 1

# Test with 3 invoices (dry-run, safe)
python scripts/sync_qb_invoices_to_internal.py --limit 3

# Full dry-run (see what would happen, no changes)
python scripts/sync_qb_invoices_to_internal.py

# Actually commit changes (ONLY after dry-run passes)
python scripts/sync_qb_invoices_to_internal.py --commit
```

## ✅ Current Features (Post-Debugging)

The script now includes:

- ✅ **Dry-run mode by default** - No changes unless `--commit` flag used
- ✅ **Incremental testing** - `--limit N` to test with small batches
- ✅ **ORM-based inserts** - No SQL syntax issues with parameter mixing
- ✅ **Explicit type conversions** - Dates, UUIDs, enums handled correctly
- ✅ **Defensive JSONB parsing** - Handles None values gracefully
- ✅ **ASCII-only output** - No Unicode encoding errors on Windows
- ✅ **Detailed progress tracking** - Shows client/permit linking status

## Debugging History (13 Rounds)

1. **SQL parameter syntax** - Mixed `:named` and `$positional` → Fixed by using ORM
2. **Unicode encoding** - Emoji on Windows → Replaced with ASCII `[OK]`
3. **Import error** - Wrong module name → Fixed to `AsyncSessionLocal`
4. **Date type mismatch** - String vs datetime → Added `datetime.fromisoformat()`
5. **Enum case mismatch** - Lowercase vs UPPERCASE → Fixed status mapping
6. **NOT NULL violation** - `project_id` required → Altered column to allow NULL
7. **None.get() crash** - JSONB field was None → Added `or {}` pattern

## Prevention Checklist

Before writing ANY migration script:

- [ ] Run `docs/guides/DATA_MIGRATION_BEST_PRACTICES.md` checklist
- [ ] Inspect database schema with `psql "..." -c "\d table_name"`
- [ ] Check enum values: `psql "..." -c "SELECT unnest(enum_range(NULL::enum_type))"`
- [ ] Sample actual data to verify types and structures
- [ ] Use validation script: `python scripts/validate_migration_template.py`
- [ ] Test with `--limit 1` first
- [ ] Always dry-run before `--commit`
