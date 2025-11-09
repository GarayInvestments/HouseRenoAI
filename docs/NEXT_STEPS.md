# Next Steps After Phase 0

**Current Status:** ✅ Phase 0 Complete  
**Date:** November 8, 2025  
**Next Milestone:** Phase 1 (Handler Extraction)

---

## 📅 Immediate Actions (Nov 8-10, 2025)

### 1. Collect Baseline Metrics (3 Days)

Run the metrics collection script **multiple times per day**:

```bash
python scripts/collect_metrics.py
```

**Recommended Schedule:**
- Morning (9-10 AM): Capture start-of-day performance
- Midday (12-1 PM): Capture peak usage
- Afternoon (3-4 PM): Capture sustained load
- End of day (5-6 PM): Capture cleanup operations

**What It Does:**
- Tests production endpoints (Simple Chat, Projects, Permits, Clients)
- Measures response times (milliseconds)
- Saves timestamped JSON files to `docs/metrics/baseline/`
- Generates summary statistics

**Output Files:**
- `docs/metrics/baseline/metrics_YYYYMMDD_HHMMSS.json`

### 2. Monitor Production Stability

**Keep the system stable during metrics collection:**
- ❌ No experimental changes
- ❌ No refactoring work
- ❌ No major feature additions
- ✅ Bug fixes are okay (but document them)
- ✅ Document any outages or anomalies
- ✅ Note high-traffic events

**Why:** We need clean baseline data to prove refactoring improvements.

### 3. Save Render Logs

**November 11, 2025:**
1. Go to https://dashboard.render.com
2. Select HouseRenovators-api service
3. Click "Logs" tab
4. Filter by date range: Nov 8-10
5. Export or screenshot key sections:
   - Response times
   - API call patterns
   - Error rates
   - Request volumes

---

## 📊 After Collection (Nov 11, 2025)

### 1. Analyze Baseline Data

**Review all metrics:**
```bash
# View all collected metrics
ls docs/metrics/baseline/

# Optionally create analysis script
python scripts/analyze_baseline.py  # Create this if needed
```

**Update BASELINE_METRICS.md with:**
- Average response times per endpoint
- P95 and P99 latencies
- Total API calls (QB, Sheets, OpenAI)
- Token counts and costs
- Error rates

### 2. Execute Backup

**Before ANY refactoring work:**

```powershell
./scripts/backup-before-refactor.ps1
```

**Expected Output:**
- Branch: `backup/pre-refactor-2025-11-11_HHMMSS`
- Tag: `backup-2025-11-11_HHMMSS`
- Both pushed to GitHub

**Verify Backup:**
```bash
git branch -r | grep backup
git tag -l | grep backup
git show backup-2025-11-11_HHMMSS  # View backup details
```

### 3. Review Refactor Plan

**Read these documents:**
- `docs/chat_refactor_plan.md` - Full implementation guide (1461 lines)
- `docs/PHASE_0_COMPLETE.md` - Phase 0 summary (what we just did)
- `tests/test_current_chat_handlers.py` - Tests that must pass

**Key Points for Phase 1:**
- Extract 6 handlers from `chat.py` (lines 224-560)
- Create `app/handlers/ai_functions.py`
- Implement `FUNCTION_HANDLERS` registry
- Update `chat.py` to use registry
- Target: Reduce `chat.py` from 967 → ~300 lines (70% reduction)

---

## 🚀 Phase 1 Kickoff (Nov 11+)

### Step 1: Create Handler Module

```bash
# Create handlers directory
mkdir app/handlers
touch app/handlers/__init__.py

# Create handlers file
touch app/handlers/ai_functions.py
```

### Step 2: Extract First Handler

**Start with simplest handler:**
- `update_project_status` (lines 224-248 in chat.py)
- Copy to `app/handlers/ai_functions.py`
- Wrap in try/except/HTTPException pattern
- Add to `FUNCTION_HANDLERS` registry

**Example:**
```python
# app/handlers/ai_functions.py

from fastapi import HTTPException
from app.services import google_service as google_service_module

FUNCTION_HANDLERS = {}

def update_project_status(arguments: dict) -> dict:
    """Update project status in Google Sheets"""
    try:
        google_service = google_service_module.google_service
        if not google_service:
            raise HTTPException(
                status_code=503, 
                detail="Google service not initialized"
            )
        
        # Handler logic here...
        
        return {"success": True, "message": "..."}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating project: {str(e)}"
        )

FUNCTION_HANDLERS["update_project_status"] = update_project_status
```

### Step 3: Update chat.py

**Import and use handler:**
```python
# app/routes/chat.py

from app.handlers.ai_functions import FUNCTION_HANDLERS

# In process_chat_stream(), replace direct function call:
# OLD:
if function_name == "update_project_status":
    result = update_project_status(arguments)

# NEW:
if function_name in FUNCTION_HANDLERS:
    handler = FUNCTION_HANDLERS[function_name]
    result = handler(arguments)
```

### Step 4: Test After Extraction

**Run tests after EVERY handler extraction:**
```bash
pytest tests/ -v
```

**All 9 tests MUST pass:**
- ✅ test_update_project_status
- ✅ test_update_permit_status
- ✅ test_update_client_field
- ✅ test_create_quickbooks_invoice
- ✅ test_update_quickbooks_invoice_docnumber
- ✅ test_add_column_to_sheet
- ✅ test_error_handling
- ✅ test_quickbooks_authentication_check
- ✅ test_function_registry_concept

**If tests fail:** Revert changes and investigate before continuing.

### Step 5: Commit Incrementally

**Commit after each handler extraction:**
```bash
git add app/handlers/ app/routes/chat.py
git commit -m "Phase 1.1: Extract update_project_status handler"
git push
```

**Why:** Small commits make it easy to identify what broke if tests fail.

---

## ⚠️ Important Reminders

### DO:
- ✅ Run tests after every change
- ✅ Commit incrementally
- ✅ Keep backup branch as rollback point
- ✅ Measure performance after refactor
- ✅ Update documentation

### DON'T:
- ❌ Extract all handlers at once (too risky)
- ❌ Skip testing between extractions
- ❌ Change handler logic during extraction
- ❌ Refactor without backup
- ❌ Rush the process

---

## 🎯 Success Criteria for Phase 1

When Phase 1 is complete, you should have:

### Code Changes:
- ✅ `app/handlers/ai_functions.py` exists (300-400 lines)
- ✅ 6 handlers extracted and working
- ✅ `FUNCTION_HANDLERS` registry implemented
- ✅ `chat.py` reduced from 967 → ~300 lines
- ✅ All imports updated correctly

### Testing:
- ✅ All 9 tests passing
- ✅ Test coverage maintained at 99%+
- ✅ GitHub Actions workflow passing
- ✅ No regressions detected

### Documentation:
- ✅ Handler docstrings added
- ✅ Registry usage documented
- ✅ Phase 1 summary written

### Performance:
- ✅ Response times measured
- ✅ Compared to baseline (should be similar or better)
- ✅ No performance regressions

---

## 📞 Need Help?

**Reference Documents:**
- `docs/chat_refactor_plan.md` - Full plan with examples
- `docs/PHASE_0_COMPLETE.md` - What we just completed
- `tests/test_current_chat_handlers.py` - Test patterns
- `.github/copilot-instructions.md` - Project conventions

**Common Issues:**
- Tests failing → Check imports and function signatures
- Performance slower → Review async patterns and API calls
- CI failing → Check coverage threshold (80% minimum)
- Backup fails → Commit uncommitted changes first

---

## 🎉 You're Ready!

Phase 0 is complete. All safety measures are in place:
- ✅ 9 tests (99% coverage)
- ✅ CI automation (GitHub Actions)
- ✅ Backup script ready
- ✅ Baseline metrics template
- ✅ Metrics collection script

**Now:** Focus on collecting 3 days of baseline data (Nov 8-10).  
**Then:** Execute backup and begin Phase 1 (Nov 11+).

**Estimated Phase 1 Duration:** 1-2 weeks  
**Target Completion:** November 15-22, 2025

Good luck! 🚀
