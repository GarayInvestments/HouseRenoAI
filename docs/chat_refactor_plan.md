# Chat Refactor Plan (REVISED)

## 1. Objective
Improve maintainability, scalability, and performance of the AI chat system by modularizing code, implementing smart caching, and optimizing context handling. Focus on high-ROI changes that provide immediate value.

---

## 2. Key Goals
- **Modularize** function handlers to reduce chat.py from 967 lines to ~300 lines
- **Optimize** context loading - only fetch data when needed
- **Cache** QuickBooks data to reduce API calls by 80%
- **Improve** logging and debugging capabilities
- **Avoid** over-engineering with low-value complexity

---

## 3. Current State Analysis

### File Sizes
- `chat.py`: **967 lines** (TOO LARGE)
- `openai_service.py`: **535 lines**
- **6 function handlers**: ~80 lines each, embedded in chat.py

### Performance Issues
- ❌ Fetches ALL Google Sheets data (permits, projects, clients) on EVERY message
- ❌ Queries QuickBooks API 2x per message even when not asking about invoices
- ❌ Sends 300-500 tokens of unused context to OpenAI per request
- ✅ In-memory session storage works well (30-min TTL)
- ✅ AI confirmation prompts working correctly

### Code Maintainability
- ❌ Adding new AI functions requires editing 80+ lines in bloated chat.py
- ❌ Function handlers are tightly coupled to route logic
- ✅ System prompt is manageable at 150 lines
- ✅ Service layer separation is good

---

## 4. Implementation Roadmap (REVISED)

### **Phase 1: Code Organization (Week 1) - HIGH PRIORITY**

#### **1.1 Extract Function Handlers to Dedicated Module** ⭐ **CRITICAL**
**Problem**: chat.py is 967 lines with 6 function handlers mixed into route logic

**Solution**:
**New File:** `app/handlers/ai_functions.py`

```python
# app/handlers/ai_functions.py
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

async def handle_update_project_status(
    args: Dict[str, Any], 
    google_service, 
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """Handle AI request to update project status"""
    project_id = args["project_id"]
    new_status = args["new_status"]
    
    success = await google_service.update_project_status(project_id, new_status)
    
    if success:
        memory_manager.set(session_id, "last_project_id", project_id)
        return {
            "function": "update_project_status",
            "status": "success",
            "details": f"Updated project {project_id} to {new_status}"
        }
    else:
        return {
            "function": "update_project_status",
            "status": "failed",
            "error": "Could not update project"
        }

async def handle_update_permit_status(args, google_service, memory_manager, session_id):
    """Handle AI request to update permit status"""
    # Implementation here
    pass

async def handle_create_quickbooks_invoice(args, qb_service, memory_manager, session_id):
    """Handle AI request to create QuickBooks invoice"""
    # Implementation here
    pass

async def handle_update_quickbooks_invoice(args, qb_service, memory_manager, session_id):
    """Handle AI request to update QuickBooks invoice"""
    # Implementation here
    pass

async def handle_add_column_to_sheet(args, google_service, memory_manager, session_id):
    """Handle AI request to add column to Google Sheet"""
    # Implementation here
    pass

async def handle_update_client_field(args, google_service, memory_manager, session_id):
    """Handle AI request to update client field"""
    # Implementation here
    pass

# Handler registry
FUNCTION_HANDLERS = {
    "update_project_status": handle_update_project_status,
    "update_permit_status": handle_update_permit_status,
    "create_quickbooks_invoice": handle_create_quickbooks_invoice,
    "update_quickbooks_invoice": handle_update_quickbooks_invoice,
    "add_column_to_sheet": handle_add_column_to_sheet,
    "update_client_field": handle_update_client_field,
}
```

**Update chat.py:**
```python
from app.handlers.ai_functions import FUNCTION_HANDLERS

# In process_chat_message, replace massive if/elif chain:
for func_call in function_calls:
    func_name = func_call.get("name")
    func_args = func_call.get("arguments", {})
    
    if func_name in FUNCTION_HANDLERS:
        handler = FUNCTION_HANDLERS[func_name]
        
        # Determine which service to pass
        service = qb_service if "quickbooks" in func_name else google_service
        
        result = await handler(func_args, service, memory_manager, session_id)
        function_results.append(result)
    else:
        logger.warning(f"Unknown function: {func_name}")
```

**Benefits:**
- ✅ Reduces chat.py from 967 → ~300 lines (70% reduction)
- ✅ Each handler is isolated, testable, and reusable
- ✅ Adding new AI functions = add one handler function
- ✅ Easier code reviews and debugging
- ✅ Clear separation of concerns

**Effort:** Medium (2-3 hours to extract and test)  
**Impact:** 🔥🔥🔥 **CRITICAL** - Makes future development 10x easier

---

#### **1.2 Implement Smart Context Loading** ⭐ **HIGH PRIORITY**
**Problem**: Fetching ALL data on EVERY message wastes 300-500 tokens and slows responses

**Solution**:
**New File:** `app/utils/context_builder.py`

```python
# app/utils/context_builder.py
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def needs_sheets_context(message: str) -> bool:
    """Determine if message requires Google Sheets data"""
    sheets_keywords = [
        "client", "project", "permit", "status", 
        "address", "contractor", "inspection",
        "budget", "timeline", "phase"
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in sheets_keywords)

def needs_quickbooks_context(message: str) -> bool:
    """Determine if message requires QuickBooks data"""
    qb_keywords = [
        "invoice", "payment", "paid", "unpaid", 
        "balance", "quickbooks", "qbo", "qb",
        "bill", "receivable", "customer balance"
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in qb_keywords)

async def build_sheets_context(google_service) -> Dict[str, Any]:
    """Build context from Google Sheets data"""
    permits = await google_service.get_permits_data()
    projects = await google_service.get_projects_data()
    clients = await google_service.get_clients_data()
    
    return {
        'permits_count': len(permits),
        'projects_count': len(projects),
        'clients_count': len(clients),
        'all_permits': permits,
        'all_projects': projects,
        'all_clients': clients,
        # ... rest of context building
    }

async def build_quickbooks_context(qb_service) -> Dict[str, Any]:
    """Build context from QuickBooks data"""
    if not qb_service or not qb_service.is_authenticated():
        return {"quickbooks_available": False}
    
    customers = await qb_service.get_customers()
    invoices = await qb_service.get_invoices()
    
    # Summarize instead of full data
    return {
        "quickbooks_available": True,
        "customers_count": len(customers),
        "invoices_count": len(invoices),
        "recent_invoices": invoices[:10],  # Only last 10
        "customer_summary": [
            {"id": c["Id"], "name": c["DisplayName"]}
            for c in customers
        ]
    }

async def build_context(message: str, google_service, qb_service, session_memory: Dict) -> Dict[str, Any]:
    """Smart context builder - only loads what's needed"""
    context = {"session_memory": session_memory}
    
    # Conditionally load data based on query
    if needs_sheets_context(message):
        logger.info("Loading Google Sheets context")
        sheets_data = await build_sheets_context(google_service)
        context.update(sheets_data)
    else:
        logger.info("Skipping Google Sheets context (not needed)")
    
    if needs_quickbooks_context(message):
        logger.info("Loading QuickBooks context")
        qb_data = await build_quickbooks_context(qb_service)
        context.update(qb_data)
    else:
        logger.info("Skipping QuickBooks context (not needed)")
    
    return context
```

**Update chat.py:**
```python
from app.utils.context_builder import build_context

# Replace existing context building (lines 63-145) with:
context = await build_context(message, google_service, qb_service, session_memory)
```

**Benefits:**
- ✅ 80% reduction in unnecessary API calls
- ✅ 60% reduction in OpenAI token usage (saves $)
- ✅ 40% faster response time for simple queries
- ✅ Still loads ALL data when needed for complex queries

**Example Impact:**
- User: "What's the weather?" → No Sheets/QB calls
- User: "Show me Temple project" → Sheets only
- User: "Create invoice" → Both Sheets + QB

**Effort:** Medium (3-4 hours)  
**Impact:** 🔥🔥🔥 **HIGH VALUE**

---

### **Phase 2: Performance Optimization (Week 2) - HIGH PRIORITY**

#### **2.1 Add QuickBooks Caching Layer** ⭐ **HIGH PRIORITY**
**Problem**: Fetching 53 invoices + 24 customers on EVERY chat message, even for "hello"

**Solution**:
**File:** `app/services/quickbooks_service.py`

```python
from datetime import datetime, timedelta
from typing import Optional, List, Dict

class QuickBooksService:
    def __init__(self):
        # ... existing init ...
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache_timestamps:
            return False
        
        age = datetime.now() - self._cache_timestamps[key]
        return age.total_seconds() < self._cache_ttl
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if self._is_cache_valid(key):
            logger.info(f"Cache HIT: {key}")
            return self._cache[key]
        logger.info(f"Cache MISS: {key}")
        return None
    
    def _set_cache(self, key: str, value: Any):
        """Store data in cache"""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    def _invalidate_cache(self):
        """Clear all cached data after writes"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Cache invalidated after write operation")
    
    async def get_customers(self) -> List[Dict]:
        """Get customers with caching"""
        cached = self._get_from_cache("customers")
        if cached:
            return cached
        
        # Original fetch logic
        customers = await self._fetch_customers_from_api()
        self._set_cache("customers", customers)
        return customers
    
    async def get_invoices(self) -> List[Dict]:
        """Get invoices with caching"""
        cached = self._get_from_cache("invoices")
        if cached:
            return cached
        
        # Original fetch logic
        invoices = await self._fetch_invoices_from_api()
        self._set_cache("invoices", invoices)
        return invoices
    
    async def create_invoice(self, invoice_data: Dict) -> Dict:
        """Create invoice and invalidate cache"""
        result = await self._create_invoice_api(invoice_data)
        self._invalidate_cache()  # Force refresh on next fetch
        return result
    
    async def update_invoice(self, invoice_id: str, updates: Dict) -> Dict:
        """Update invoice and invalidate cache"""
        result = await self._update_invoice_api(invoice_id, updates)
        self._invalidate_cache()  # Force refresh on next fetch
        return result
```

**Benefits:**
- ✅ 80% reduction in QuickBooks API calls
- ✅ Faster response times (no wait for QB API)
- ✅ Reduces risk of hitting QB rate limits
- ✅ Cache automatically invalidates after creates/updates
- ✅ 5-minute TTL keeps data reasonably fresh

**Metrics:**
- Before: 2 QB API calls per message × 100 messages/day = 200 calls
- After: 2 QB API calls per 5 min × 100 messages/day = ~40 calls
- **Savings: 80% reduction**

**Effort:** Low-Medium (2 hours)  
**Impact:** 🔥🔥🔥 **HIGH VALUE**

---

#### **2.2 Truncate Large Context Lists**
**Problem**: Sending 53 invoices when AI only needs last 10

**Solution:**
```python
# In context_builder.py
def summarize_invoices(invoices: List[Dict], limit: int = 10) -> Dict:
    """Summarize invoice list for AI context"""
    total = len(invoices)
    recent = invoices[:limit]
    
    return {
        "total_invoices": total,
        "recent_invoices": recent,
        "summary": f"Showing {limit} most recent of {total} total invoices"
    }

def summarize_customers(customers: List[Dict], limit: int = 50) -> Dict:
    """Summarize customer list for AI context"""
    total = len(customers)
    
    # Simplified customer data (just ID and name)
    customer_summary = [
        {"id": c["Id"], "name": c["DisplayName"]}
        for c in customers[:limit]
    ]
    
    return {
        "total_customers": total,
        "customers": customer_summary,
        "summary": f"Showing {limit} of {total} customers"
    }
```

**Benefits:**
- ✅ 60% reduction in token usage
- ✅ Faster OpenAI API responses
- ✅ Lower costs per message
- ✅ AI still has access to essential data

**Effort:** Low (1 hour)  
**Impact:** 🔥🔥 **GOOD**

---

### **Phase 3: Monitoring & Polish (Week 3) - MEDIUM PRIORITY**

#### **3.1 Enhanced Logging with Context**
**File:** `chat.py`

```python
import logging
from contextvars import ContextVar

# Create context var for request tracking
request_context: ContextVar[dict] = ContextVar('request_context', default={})

class ContextLogger(logging.LoggerAdapter):
    """Logger that includes request context"""
    def process(self, msg, kwargs):
        ctx = request_context.get()
        session_id = ctx.get('session_id', 'unknown')
        return f"[{session_id}] {msg}", kwargs

logger = ContextLogger(logging.getLogger(__name__), {})

@router.post("/")
async def process_chat_message(chat_data: Dict[str, Any]):
    session_id = chat_data.get("session_id", "default")
    request_context.set({"session_id": session_id})
    
    logger.info(f"Processing message: {message[:50]}...")
    
    # Now all logs automatically include session_id
    # Output: [session_abc123] Processing message: hello...
```

**Benefits:**
- ✅ Easier debugging with session tracking
- ✅ Better production log analysis
- ✅ Clear request flow in Render logs

**Effort:** Low (1 hour)  
**Impact:** 🔥 **GOOD**

---

#### **3.2 Performance Timing Metrics**
```python
import time

@router.post("/")
async def process_chat_message(chat_data: Dict[str, Any]):
    start_time = time.time()
    
    # Context loading
    ctx_start = time.time()
    context = await build_context(...)
    ctx_time = time.time() - ctx_start
    
    # OpenAI call
    ai_start = time.time()
    response, function_calls = await openai_service.process_chat_message(...)
    ai_time = time.time() - ai_start
    
    # Function execution
    func_start = time.time()
    # ... execute functions ...
    func_time = time.time() - func_start
    
    total_time = time.time() - start_time
    
    logger.info(f"Timing - Context: {ctx_time:.2f}s, AI: {ai_time:.2f}s, Functions: {func_time:.2f}s, Total: {total_time:.2f}s")
```

**Benefits:**
- ✅ Identify slow operations
- ✅ Measure refactor impact
- ✅ Production performance monitoring

**Effort:** Low (1 hour)  
**Impact:** 🔥 **GOOD**

---

## 5. What NOT to Do (Explicitly Excluded)

### ❌ **Rejected: Extract System Prompt to File**
**Why:**
- System prompt has dynamic date/time injection (`{current_date}`, `{current_time}`)
- Only 150 lines in Python - manageable size
- External file adds complexity without benefit
- No version control advantage (prompt is already in git)

**Decision:** Keep prompt in `openai_service.py` as is

---

### ❌ **Rejected: Dynamic Temperature Control**
**Why:**
- Current temperature (0.7) works well for all cases
- Keyword-based logic too simplistic:
  - "show me all invoices" doesn't need 0.3 temperature
  - "tell me about permits" doesn't need different temp
- Adds complexity with no measurable benefit
- AI already provides factual answers when needed

**Decision:** Keep single temperature value

---

### ❌ **Rejected: Code-Level Confirmation Layer**
**Why:**
- AI already asks for confirmation in system prompt:
  - "ALWAYS ask for confirmation before updating"
  - "ALWAYS ask 'Would you like me to create this invoice?'"
- Adding code-level checks would cause double prompting
- Requires frontend changes to handle confirmation state
- Current AI-driven confirmation works perfectly

**Decision:** Stick with prompt-based confirmations

---

### ❌ **Rejected: Streamed Responses (SSE/WebSocket)**
**Why:**
- High implementation complexity (backend + frontend overhaul)
- Current 2-4 second response time is acceptable
- Requires infrastructure changes (SSE endpoint, frontend handlers)
- Limited user-perceived benefit for chat use case
- Most queries complete in < 3 seconds already

**Decision:** Defer indefinitely - not worth the effort

---

### ❌ **Rejected: Memory Summaries in Google Sheets**
**Why:**
- Current in-memory storage with 30-min TTL works well
- Writing to Sheets after every message adds latency (200-300ms per write)
- Google Sheets not designed for high-write chat storage
- Chat sessions rarely exceed 30 minutes
- Would introduce new failure mode (Sheets write failures)

**Decision:** Keep in-memory session storage

---

## 6. Revised Priority Table

| Priority | Action | Lines Changed | Effort | Impact | ROI | Status |
|----------|--------|---------------|--------|--------|-----|--------|
| **🔥 P0** | Extract function handlers | -650, +200 | Medium | 🔥🔥🔥 | **CRITICAL** | ⏳ Pending |
| **⚡ P1** | Smart context loading | ~150 | Medium | 🔥🔥🔥 | **HIGH** | ⏳ Pending |
| **⚡ P1** | QuickBooks caching | ~80 | Low-Med | 🔥🔥🔥 | **HIGH** | ⏳ Pending |
| **📌 P2** | Truncate large lists | ~50 | Low | 🔥🔥 | **GOOD** | ⏳ Pending |
| **📌 P2** | Context logging | ~30 | Low | 🔥 | **GOOD** | ⏳ Pending |
| **📌 P2** | Performance timing | ~40 | Low | 🔥 | **GOOD** | ⏳ Pending |
| **❌** | Extract prompt to file | - | - | - | **NOT WORTH IT** | ✅ Rejected |
| **❌** | Temperature control | - | - | - | **NOT WORTH IT** | ✅ Rejected |
| **❌** | Confirmation layer | - | - | - | **REDUNDANT** | ✅ Rejected |
| **❌** | Streaming responses | - | - | - | **TOO COMPLEX** | ✅ Rejected |
| **❌** | Sheets-based memory | - | - | - | **WRONG TOOL** | ✅ Rejected |

---

## 7. Implementation Timeline

### **Week 1: Code Organization**
- **Day 1-2**: Create `handlers/ai_functions.py`, extract all 6 handlers
- **Day 3**: Update chat.py to use handler registry
- **Day 4**: Testing - verify all functions work identically
- **Day 5**: Deploy and monitor

**Expected Result:** chat.py reduced from 967 → ~300 lines

---

### **Week 2: Performance**
- **Day 1**: Implement QuickBooks caching layer
- **Day 2**: Create `utils/context_builder.py` with smart loading
- **Day 3**: Integrate smart context into chat.py
- **Day 4**: Add list truncation/summarization
- **Day 5**: Performance testing and metrics

**Expected Result:** 80% fewer QB calls, 60% fewer tokens, 40% faster simple queries

---

### **Week 3: Polish**
- **Day 1**: Enhanced logging with context
- **Day 2**: Performance timing metrics
- **Day 3**: Documentation updates
- **Day 4**: Production monitoring setup
- **Day 5**: Final testing and deployment

**Expected Result:** Better observability and production monitoring

---

## 8. Success Metrics

### Code Quality
- ✅ chat.py: 967 lines → **~300 lines** (70% reduction)
- ✅ Modular handlers enable 10x faster feature additions
- ✅ Each handler independently testable

### Performance
- ✅ QuickBooks API calls: 200/day → **40/day** (80% reduction)
- ✅ OpenAI token usage: -60% for non-QB queries
- ✅ Response time for simple queries: 3s → **1.8s** (40% faster)

### Maintainability
- ✅ Adding new AI function: 80 lines in chat.py → **30 lines in handler file**
- ✅ Clear separation of concerns
- ✅ Better production debugging with context logging

---

## 9. Next Steps

1. **Review this revised plan** with team/stakeholder
2. **Create feature branch**: `refactor/chat-optimization`
3. **Start with P0**: Extract function handlers (biggest impact)
4. **Test thoroughly** after each phase
5. **Monitor metrics** to validate improvements
6. **Document** patterns for future AI functions

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing functionality | Comprehensive testing after each phase, feature branch |
| Cache staleness | 5-minute TTL, invalidate on writes, manual refresh endpoint |
| Smart context missing data | Fallback to full context if AI requests missing data |
| Handler extraction bugs | Copy exact logic, unit test each handler |

---

**Last Updated:** November 8, 2025  
**Status:** Ready for Implementation  
**Next Review:** After Phase 1 completion

