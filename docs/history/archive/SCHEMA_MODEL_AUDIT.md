# Schema vs Model Audit - December 11, 2025

## Critical Issues Found

### ❌ SiteVisit Model/Service Mismatches

**Database Schema (site_visits table)**:
- `start_time` - TIMESTAMP (actual check-in time)
- `end_time` - TIMESTAMP (actual check-out time) 
- `gps_location` - VARCHAR(100) (lat,lon format string)
- `photos` - JSONB (array)
- `deficiencies` - JSONB (array)
- `follow_up_actions` - JSONB (array)

**Service Issues**:
1. **start_visit()** references `actual_start_time` (doesn't exist) → should be `start_time`
2. **complete_visit()** references `actual_end_time` (doesn't exist) → should be `end_time`
3. **complete_visit()** references `summary` (doesn't exist) → should use `notes`
4. **start_visit()** passes dict to `gps_location` → needs conversion to "lat,lon" string
5. **add_photos()** uses `.extend()` on JSONB → JSONB is dict, needs proper array handling
6. **add_follow_up_action()** uses `.extend()` on JSONB → same issue

### ✅ Permits - CORRECT
All fields match between database, model, and service.

### ✅ Inspections - CORRECT  
All fields match between database, model, and service.

### ✅ Invoices - CORRECT
All fields match after migration 1792b711773f added amount_paid/balance_due.

### ✅ Payments - CORRECT
All fields match between database, model, and service.

## Root Cause Analysis

**Why so many mistakes?**

1. **No automated schema validation** - Services/models drift from database without detection
2. **Copy-paste errors** - Service methods written with field names that don't exist
3. **Type confusion** - JSONB arrays vs dicts not clearly documented
4. **No type checking enforcement** - SQLAlchemy Mapped types not catching mismatches
5. **Manual testing only** - Integration tests catch issues late in development

## Prevention Strategy

### Immediate Actions:
1. Create `scripts/validate_schema.py` - Compares DB schema to models
2. Fix all SiteVisit service methods
3. Add field name validation to service tests
4. Document JSONB field structures in models

### Long-term:
1. Use Alembic autogenerate to detect model/DB drift
2. Add pytest fixtures that validate schema on startup
3. Use Pydantic for service input validation
4. CI/CD schema validation check before deploy
5. Add type stubs for SQLAlchemy models
