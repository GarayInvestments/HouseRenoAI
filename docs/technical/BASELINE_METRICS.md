# Baseline Metrics - Pre-Refactor Performance

**Collection Period:** November 8-10, 2025 (3 days)  
**Purpose:** Establish baseline performance before chat.py refactor  
**Target:** Prove 50%+ improvement in response time and maintainability  

---

## 1. Response Time (ms)

### Current Measurements

| Endpoint Type | Day 1 (Nov 8) | Day 2 (Nov 9) | Day 3 (Nov 10) | Average | P95 | P99 |
|--------------|---------------|---------------|----------------|---------|-----|-----|
| Simple Chat (no tools) | _pending_ | _pending_ | _pending_ | _TBD_ | _TBD_ | _TBD_ |
| Invoice Query (QB read) | _pending_ | _pending_ | _pending_ | _TBD_ | _TBD_ | _TBD_ |
| Create Invoice (QB write) | _pending_ | _pending_ | _pending_ | _TBD_ | _TBD_ | _TBD_ |
| Update Project (Sheets write) | _pending_ | _pending_ | _pending_ | _TBD_ | _TBD_ | _TBD_ |
| Update Permit (Sheets write) | _pending_ | _pending_ | _pending_ | _TBD_ | _TBD_ | _TBD_ |
| Update Client (Sheets write) | _pending_ | _pending_ | _pending_ | _TBD_ | _TBD_ | _TBD_ |
| Add Column (Sheets schema) | _pending_ | _pending_ | _pending_ | _TBD_ | _TBD_ | _TBD_ |

### Target Post-Refactor

| Endpoint Type | Target Avg (ms) | Target P95 (ms) | Expected Improvement |
|--------------|-----------------|-----------------|----------------------|
| Simple Chat | < 500 | < 800 | 30-50% faster |
| Invoice Query | < 1200 | < 2000 | 40% faster (caching) |
| Create Invoice | < 1500 | < 2500 | 35% faster |
| Update Project | < 800 | < 1500 | 50% faster (parallel) |
| Update Permit | < 800 | < 1500 | 50% faster (parallel) |
| Update Client | < 800 | < 1500 | 50% faster (parallel) |
| Add Column | < 1000 | < 1800 | 40% faster |

---

## 2. API Call Counts

### QuickBooks API

| Day | Total Calls | is_authenticated | create_invoice | update_invoice | get_invoice_by_id | Errors |
|-----|-------------|------------------|----------------|----------------|-------------------|--------|
| Nov 8 | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| Nov 9 | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| Nov 10 | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| **Avg** | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

**Target Reduction:** 30% fewer calls via smart caching and batch operations

### Google Sheets API

| Day | Total Calls | Read Operations | Write Operations | Schema Changes | Errors |
|-----|-------------|-----------------|------------------|----------------|--------|
| Nov 8 | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| Nov 9 | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| Nov 10 | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| **Avg** | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

**Target Reduction:** 40% fewer calls via smart caching and deduplication

### OpenAI API

| Day | Total Calls | Function Calls | Tokens In | Tokens Out | Total Tokens | Cost ($) |
|-----|-------------|----------------|-----------|------------|--------------|----------|
| Nov 8 | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| Nov 9 | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| Nov 10 | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| **Avg** | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

**Target Reduction:** 25% fewer tokens via smart context management

---

## 3. Current Issues (Pre-Refactor)

### Code Quality Issues
- [ ] 967-line monolithic route file
- [ ] 6 function handlers embedded in route (lines 224-560)
- [ ] No handler registry pattern
- [ ] Limited error context in logs
- [ ] No performance metrics collection
- [ ] Manual context string building (300+ lines)

### Performance Issues
- [ ] Sequential API calls (no parallelization)
- [ ] No caching (repeated QB/Sheets calls)
- [ ] Full context sent every request (token waste)
- [ ] No connection pooling

### Maintainability Issues
- [ ] Adding new handlers requires editing 967-line file
- [ ] No clear separation of concerns
- [ ] Difficult to test individual handlers
- [ ] No handler documentation
- [ ] Mixed responsibilities (routing + business logic)

---

## 4. Data Collection Commands

### Render Dashboard Logs
```bash
# Access Render logs for production backend
# 1. Go to https://dashboard.render.com
# 2. Select HouseRenovators-api service
# 3. Click "Logs" tab
# 4. Filter by date range: Nov 8-10, 2025
# 5. Search for:
#    - "POST /v1/chat" (chat requests)
#    - "Response time:" (performance logs - need to add these)
#    - "QuickBooks" (QB operations)
#    - "Google Sheets" (Sheets operations)
#    - "Error" or "Exception" (failures)
```

### Local Testing Script
```python
# scripts/collect_metrics.py (create this for testing)
import time
import requests
import json
from datetime import datetime

API_URL = "https://houserenoai.onrender.com/v1"

def test_endpoint(name, method, path, data=None):
    """Test endpoint and measure response time"""
    start = time.time()
    response = requests.request(method, f"{API_URL}{path}", json=data)
    duration = (time.time() - start) * 1000  # ms
    
    print(f"{name}: {duration:.2f}ms - {response.status_code}")
    return {
        "timestamp": datetime.now().isoformat(),
        "endpoint": name,
        "duration_ms": duration,
        "status_code": response.status_code
    }

# Run daily and append to metrics.json
results = []
results.append(test_endpoint("Simple Chat", "POST", "/chat", {"message": "Hello"}))
results.append(test_endpoint("Get Projects", "GET", "/projects"))
# ... add more tests

with open(f"metrics_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Performance Logging (Add to chat.py temporarily)
```python
# Add at start of process_chat_stream() - line ~180
import time
request_start = time.time()

# Add before return statement - line ~220
response_time_ms = (time.time() - request_start) * 1000
logger.info(f"Chat response time: {response_time_ms:.2f}ms")
```

---

## 5. Success Criteria

After refactoring is complete, we expect to see:

### Performance Improvements
- ✅ 50% faster response times for Sheets operations (parallel execution)
- ✅ 40% reduction in Google Sheets API calls (smart caching)
- ✅ 30% reduction in QuickBooks API calls (connection pooling)
- ✅ 25% reduction in OpenAI token usage (smart context)
- ✅ P95 response times under target thresholds

### Code Quality Improvements
- ✅ chat.py reduced from 967 → ~300 lines (70% reduction)
- ✅ 6 handlers extracted to dedicated module
- ✅ Handler registry pattern implemented
- ✅ Test coverage maintained at 99%+
- ✅ All 9 integration tests passing
- ✅ Clear separation of concerns

### Maintainability Improvements
- ✅ New handlers add-able via registry (no file editing)
- ✅ Individual handler testing possible
- ✅ Performance metrics auto-collected
- ✅ Rich error context in logs
- ✅ Developer onboarding guide (REFACTOR_README.md)

---

## 6. Data Collection Schedule

| Date | Task | Status |
|------|------|--------|
| Nov 8, 2025 | Create baseline metrics file | ✅ Complete |
| Nov 8, 2025 | Add temporary performance logging | ⏳ Pending |
| Nov 8-10, 2025 | Collect 3 days of production data | ⏳ Pending |
| Nov 11, 2025 | Analyze baseline metrics | ⏳ Pending |
| Nov 11, 2025 | Document current performance | ⏳ Pending |
| Nov 11, 2025 | Begin Phase 1 refactor | ⏳ Pending |
| Nov 25, 2025 | Collect post-refactor metrics | ⏳ Pending |
| Nov 25, 2025 | Compare before/after performance | ⏳ Pending |
| Nov 25, 2025 | Calculate ROI and improvements | ⏳ Pending |

---

## 7. Notes

- Metrics will be collected during normal business hours (9 AM - 5 PM PST)
- Focus on real user interactions, not synthetic tests
- Document any anomalies (deployments, outages, high-traffic events)
- Keep production stable - no experimental changes during collection period
- Save raw logs from Render for detailed analysis

---

## 8. Raw Data Storage

Store collected metrics in:
- `docs/metrics/baseline/` directory
- Files: `metrics_20251108.json`, `metrics_20251109.json`, `metrics_20251110.json`
- Render logs: Screenshot or export key log sections
- Document collection methodology for reproducibility

---

**Last Updated:** November 8, 2025  
**Next Review:** November 11, 2025 (after 3-day collection)  
**Owner:** Development Team
