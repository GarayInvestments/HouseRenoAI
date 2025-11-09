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

### **Phase 0: Pre-Refactor Testing (CRITICAL - 1-2 Days)** ⭐ **NEW**

#### **0.1 Write Integration Tests for All Handlers**
**Problem**: Refactoring without tests risks breaking existing functionality

**Solution**:
**New File:** `tests/test_ai_handlers.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.handlers.ai_functions import (
    handle_update_project_status,
    handle_update_permit_status,
    handle_create_quickbooks_invoice,
    handle_update_quickbooks_invoice,
    handle_add_column_to_sheet,
    handle_update_client_field
)

@pytest.mark.asyncio
async def test_update_project_status_handler():
    """Test project status update handler"""
    mock_google = AsyncMock()
    mock_google.update_project_status.return_value = True
    mock_memory = MagicMock()
    
    result = await handle_update_project_status(
        {"project_id": "P123", "new_status": "Active"},
        mock_google,
        mock_memory,
        "test_session"
    )
    
    assert result["status"] == "success"
    assert "P123" in result["details"]
    mock_google.update_project_status.assert_called_once_with("P123", "Active")

@pytest.mark.asyncio
async def test_update_invoice_docnumber():
    """Regression test for DocNumber update feature (Nov 8, 2025)"""
    mock_qb = AsyncMock()
    mock_qb.get_invoice_by_id.return_value = {
        "Id": "4155",
        "DocNumber": "1234",
        "Line": [{"Amount": 1000}],
        "SyncToken": "0"
    }
    mock_qb.update_invoice.return_value = {
        "DocNumber": "TTD-6441-11-08"
    }
    mock_memory = MagicMock()
    
    result = await handle_update_quickbooks_invoice(
        {
            "invoice_id": "4155",
            "updates": {"doc_number": "TTD-6441-11-08"}
        },
        mock_qb,
        mock_memory,
        "test_session"
    )
    
    assert result["status"] == "success"
    assert "TTD-6441-11-08" in result["details"]
    mock_qb.update_invoice.assert_called_once()

@pytest.mark.asyncio
async def test_create_invoice_handler():
    """Test invoice creation handler"""
    mock_qb = AsyncMock()
    mock_qb.is_authenticated.return_value = True
    mock_qb.create_invoice.return_value = {
        "Id": "5000",
        "DocNumber": "5000"
    }
    mock_memory = MagicMock()
    
    result = await handle_create_quickbooks_invoice(
        {
            "customer_id": "C123",
            "amount": 5000,
            "description": "Test invoice"
        },
        mock_qb,
        mock_memory,
        "test_session"
    )
    
    assert result["status"] == "success"
    assert "invoice_id" in result
    assert "invoice_link" in result

@pytest.mark.asyncio
async def test_handler_error_handling():
    """Test that handlers gracefully handle errors"""
    mock_google = AsyncMock()
    mock_google.update_project_status.side_effect = Exception("API Error")
    mock_memory = MagicMock()
    
    result = await handle_update_project_status(
        {"project_id": "P123", "new_status": "Active"},
        mock_google,
        mock_memory,
        "test_session"
    )
    
    assert result["status"] == "failed"
    assert "error" in result
    assert "API Error" in result["error"]

@pytest.mark.asyncio
async def test_update_client_field_handler():
    """Test client field update handler"""
    mock_google = AsyncMock()
    mock_google.update_client_field.return_value = True
    mock_memory = MagicMock()
    
    result = await handle_update_client_field(
        {
            "client_identifier": "Ajay Nair",
            "field_name": "QBO ID",
            "field_value": "164"
        },
        mock_google,
        mock_memory,
        "test_session"
    )
    
    assert result["status"] == "success"
```

**Testing Checklist:**
- ✅ Test all 6 current handlers
- ✅ Test error handling in each handler
- ✅ Test DocNumber update (today's feature)
- ✅ Test QB authentication checks
- ✅ Test memory manager interactions
- ✅ Test Google Sheets write operations

**New File:** `tests/conftest.py`
```python
import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def mock_google_service():
    """Mock Google Sheets service"""
    mock = AsyncMock()
    mock.update_project_status.return_value = True
    mock.update_permit_status.return_value = True
    mock.update_client_field.return_value = True
    mock.add_column_to_sheet.return_value = True
    return mock

@pytest.fixture
def mock_quickbooks_service():
    """Mock QuickBooks service"""
    mock = AsyncMock()
    mock.is_authenticated.return_value = True
    mock.create_invoice.return_value = {"Id": "123", "DocNumber": "123"}
    mock.update_invoice.return_value = {"Id": "123", "DocNumber": "TTD-123"}
    mock.get_invoice_by_id.return_value = {
        "Id": "123",
        "SyncToken": "0",
        "Line": [{"Amount": 1000}]
    }
    return mock

@pytest.fixture
def mock_memory_manager():
    """Mock memory manager"""
    mock = MagicMock()
    mock.get_all.return_value = {}
    return mock
```

**Benefits:**
- ✅ Catch breaking changes immediately
- ✅ Confidence to refactor aggressively
- ✅ Document expected behavior
- ✅ Regression protection for new features
- ✅ Faster debugging when tests fail

**Effort:** Low-Medium (1-2 days)  
**Impact:** 🔥🔥🔥 **CRITICAL** - Must do before any refactoring

---

### **Phase 1: Code Organization (Week 1) - HIGH PRIORITY**

#### **1.1 Extract Function Handlers to Dedicated Module** ⭐ **CRITICAL**
**Problem**: chat.py is 967 lines with 6 function handlers mixed into route logic

**Solution**:
**New File:** `app/handlers/ai_functions.py`

```python
# app/handlers/ai_functions.py
from typing import Dict, Any
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

async def handle_update_project_status(
    args: Dict[str, Any], 
    google_service, 
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """Handle AI request to update project status"""
    try:
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
    
    except HTTPException:
        raise  # Re-raise FastAPI exceptions
    except Exception as e:
        logger.exception(f"Error in handle_update_project_status: {e}")
        return {
            "function": "update_project_status",
            "status": "failed",
            "error": str(e)
        }

async def handle_update_permit_status(args, google_service, memory_manager, session_id):
    """Handle AI request to update permit status"""
    try:
        # Implementation here
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in handle_update_permit_status: {e}")
        return {"function": "update_permit_status", "status": "failed", "error": str(e)}

async def handle_create_quickbooks_invoice(args, qb_service, memory_manager, session_id):
    """Handle AI request to create QuickBooks invoice"""
    try:
        # Implementation here
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in handle_create_quickbooks_invoice: {e}")
        return {"function": "create_quickbooks_invoice", "status": "failed", "error": str(e)}

async def handle_update_quickbooks_invoice(args, qb_service, memory_manager, session_id):
    """Handle AI request to update QuickBooks invoice"""
    try:
        # Implementation here
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in handle_update_quickbooks_invoice: {e}")
        return {"function": "update_quickbooks_invoice", "status": "failed", "error": str(e)}

async def handle_add_column_to_sheet(args, google_service, memory_manager, session_id):
    """Handle AI request to add column to Google Sheet"""
    try:
        # Implementation here
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in handle_add_column_to_sheet: {e}")
        return {"function": "add_column_to_sheet", "status": "failed", "error": str(e)}

async def handle_update_client_field(args, google_service, memory_manager, session_id):
    """Handle AI request to update client field"""
    try:
        # Implementation here
        pass
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in handle_update_client_field: {e}")
        return {"function": "update_client_field", "status": "failed", "error": str(e)}

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
        
        try:
            result = await handler(func_args, service, memory_manager, session_id)
            function_results.append(result)
        except Exception as e:
            logger.exception(f"Handler execution failed: {e}")
            function_results.append({
                "function": func_name,
                "status": "failed",
                "error": "Internal error processing function"
            })
    else:
        logger.warning(f"Unknown function: {func_name}")
```

**Error Handling Pattern:**
- ✅ Try/except in every handler
- ✅ Re-raise HTTPException (FastAPI errors)
- ✅ Log full exception with stack trace
- ✅ Return consistent error format
- ✅ Double safety: handler + caller error handling

**Benefits:**
- ✅ Reduces chat.py from 967 → ~300 lines (70% reduction)
- ✅ Each handler is isolated, testable, and reusable
- ✅ Adding new AI functions = add one handler function
- ✅ Easier code reviews and debugging
- ✅ Clear separation of concerns
- ✅ Robust error handling prevents cascade failures

**Future Organization** (when file exceeds 500 lines):
```
app/handlers/
├── __init__.py              # Exports FUNCTION_HANDLERS dict
├── sheets_handlers.py       # update_project, update_permit, add_column, update_client
└── quickbooks_handlers.py   # create_invoice, update_invoice
```

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
from typing import Dict, Any, Set

logger = logging.getLogger(__name__)

def get_required_contexts(message: str) -> Set[str]:
    """
    Determine which contexts are needed based on message content.
    Returns set to avoid duplicates.
    
    Keyword-based approach is simple and effective for current scale.
    If we add 10+ context types, revisit with router pattern.
    """
    contexts = set()
    
    # Sheets keywords - projects, permits, clients
    sheets_keywords = [
        "client", "project", "permit", "address", "status", 
        "contractor", "inspection", "budget", "timeline", 
        "phase", "scope", "jurisdiction", "subcontractor"
    ]
    
    # QuickBooks keywords - invoices, payments, customers
    qb_keywords = [
        "invoice", "payment", "paid", "unpaid", "balance", 
        "quickbooks", "qbo", "qb", "bill", "receivable", 
        "customer balance", "create invoice", "update invoice"
    ]
    
    msg_lower = message.lower()
    
    # Check for Sheets-related content
    if any(kw in msg_lower for kw in sheets_keywords):
        contexts.add("sheets")
    
    # Check for QuickBooks-related content
    if any(kw in msg_lower for kw in qb_keywords):
        contexts.add("quickbooks")
    
    # Default: if no keywords matched, assume Sheets (most common)
    if not contexts:
        contexts.add("sheets")
        logger.info("No specific keywords found, defaulting to Sheets context")
    
    return contexts

async def build_sheets_context(google_service) -> Dict[str, Any]:
    """Build context from Google Sheets data"""
    logger.info("Building Google Sheets context")
    
    permits = await google_service.get_permits_data()
    projects = await google_service.get_projects_data()
    clients = await google_service.get_clients_data()
    
    # Extract IDs for quick reference
    client_ids = [c.get('Client ID', 'N/A') for c in clients if c.get('Client ID')]
    project_ids = [p.get('Project ID', 'N/A') for p in projects if p.get('Project ID')]
    permit_ids = [p.get('Permit ID', 'N/A') for p in permits if p.get('Permit ID')]
    
    return {
        # Counts
        'permits_count': len(permits),
        'projects_count': len(projects),
        'clients_count': len(clients),
        
        # ID Lists
        'client_ids': client_ids,
        'project_ids': project_ids,
        'permit_ids': permit_ids,
        
        # Full data
        'all_permits': permits,
        'all_projects': projects,
        'all_clients': clients,
        
        # Summaries
        'permits_by_status': _group_by_field(permits, 'Permit Status'),
        'projects_by_status': _group_by_field(projects, 'Status'),
        'clients_by_status': _group_by_field(clients, 'Status'),
    }

async def build_quickbooks_context(qb_service) -> Dict[str, Any]:
    """Build context from QuickBooks data"""
    logger.info("Building QuickBooks context")
    
    if not qb_service or not qb_service.is_authenticated():
        logger.info("QuickBooks not authenticated, skipping context")
        return {"quickbooks_available": False}
    
    # Get data (will use cache if available)
    customers = await qb_service.get_customers()
    invoices = await qb_service.get_invoices()
    
    # Summarize instead of full data to reduce tokens
    return {
        "quickbooks_available": True,
        "customers_count": len(customers),
        "invoices_count": len(invoices),
        
        # Only recent invoices (last 10)
        "recent_invoices": [
            {
                "Id": inv.get("Id"),
                "DocNumber": inv.get("DocNumber"),
                "CustomerRef": inv.get("CustomerRef", {}).get("name"),
                "TotalAmt": inv.get("TotalAmt"),
                "Balance": inv.get("Balance"),
                "DueDate": inv.get("DueDate")
            }
            for inv in invoices[:10]
        ],
        
        # Simplified customer list (id + name only)
        "customer_summary": [
            {"id": c["Id"], "name": c["DisplayName"]}
            for c in customers
        ]
    }

async def build_context(
    message: str, 
    google_service, 
    qb_service, 
    session_memory: Dict
) -> Dict[str, Any]:
    """
    Smart context builder - only loads what's needed based on query.
    
    Examples:
    - "What's the weather?" → No contexts loaded
    - "Show me Temple project" → Sheets only
    - "Create invoice" → Both Sheets + QB
    """
    context = {"session_memory": session_memory}
    
    # Determine required contexts
    required = get_required_contexts(message)
    logger.info(f"Required contexts: {required}")
    
    # Conditionally load data
    if "sheets" in required:
        sheets_data = await build_sheets_context(google_service)
        context.update(sheets_data)
    else:
        logger.info("Skipping Google Sheets context (not needed)")
    
    if "quickbooks" in required:
        qb_data = await build_quickbooks_context(qb_service)
        context.update(qb_data)
    else:
        logger.info("Skipping QuickBooks context (not needed)")
    
    return context

def _group_by_field(data: list, field: str) -> dict:
    """Helper: Group data items by field value"""
    grouped = {}
    for item in data:
        value = item.get(field, 'Unknown')
        if value not in grouped:
            grouped[value] = []
        grouped[value].append(item)
    return {k: len(v) for k, v in grouped.items()}
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
- ✅ Simple keyword-based logic (easy to understand and extend)
- ✅ Default to Sheets if uncertain (safest assumption)

**Example Impact:**
| Query | Before | After | Savings |
|-------|--------|-------|---------|
| "What's the weather?" | Sheets + QB | Nothing | 100% |
| "Show me Temple project" | Sheets + QB | Sheets only | 50% |
| "Create invoice for Temple" | Sheets + QB | Sheets + QB | 0% (needed) |
| "List all clients" | Sheets + QB | Sheets only | 50% |

**Why Simple Keyword Approach:**
- Easy to read and maintain
- Fast execution (no complex routing)
- Easy to extend (just add keywords)
- **If we reach 10+ context types**, revisit with router pattern

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
- ✅ **Manual cache invalidation after writes** (critical for data consistency)
- ✅ 5-minute TTL keeps data reasonably fresh

**Why Manual Invalidation is Critical:**
- TTL alone is NOT sufficient for write operations
- User creates invoice → cache still shows old data for up to 5 minutes
- Manual invalidation ensures immediate consistency
- Pattern: After ANY create/update/delete, call `_invalidate_cache()`

**Example Usage:**
```python
# User creates invoice
await qb_service.create_invoice(invoice_data)
# Cache automatically cleared by create_invoice()
# Next get_invoices() will fetch fresh data

# Without manual invalidation (BAD):
await qb_service.create_invoice(invoice_data)
invoices = await qb_service.get_invoices()  # Returns stale cached data!
# User sees old invoice list, missing their just-created invoice
```

**Testing Cache Behavior:**
```python
# Test cache hit/miss logging
invoices1 = await qb_service.get_invoices()  # MISS - fetches from API
invoices2 = await qb_service.get_invoices()  # HIT - returns cached

# Test invalidation
await qb_service.create_invoice(data)
invoices3 = await qb_service.get_invoices()  # MISS - cache cleared, fetches fresh
```

**Monitoring:**
- Watch logs for "Cache HIT" vs "Cache MISS" patterns
- High HIT rate (>80%) indicates caching working well
- Check API call reduction in QB usage dashboard
- Verify no stale data issues after writes

**Effort:** Medium (4-5 hours)  
**Impact:** 🔥🔥🔥 **HIGH VALUE**

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

#### **3.1 Enhanced Logging with Session Context** ⭐ **RECOMMENDED**
**Problem**: Multi-user logs mixed together, hard to debug production issues

**Solution:**
**File:** `chat.py`

```python
import logging
from datetime import datetime

class SessionLogger:
    """
    Logger wrapper that automatically includes session context.
    Simpler than ContextVar - just pass session_id to each log call.
    """
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
    
    def _format_msg(self, session_id: str, msg: str) -> str:
        """Format message with session context"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{session_id}] [{timestamp}] {msg}"
    
    def info(self, session_id: str, msg: str):
        self.logger.info(self._format_msg(session_id, msg))
    
    def error(self, session_id: str, msg: str):
        self.logger.error(self._format_msg(session_id, msg))
    
    def exception(self, session_id: str, msg: str):
        self.logger.exception(self._format_msg(session_id, msg))

logger = SessionLogger(__name__)

@router.post("/")
async def process_chat_message(chat_data: Dict[str, Any]):
    session_id = chat_data.get("session_id", "default")
    message = chat_data.get("message", "")
    
    logger.info(session_id, f"Processing message: {message[:50]}...")
    
    try:
        # Context loading
        ctx_start = time.time()
        context = await build_context(message, google_service, qb_service, session_memory)
        ctx_time = time.time() - ctx_start
        logger.info(session_id, f"Context loaded in {ctx_time:.2f}s")
        
        # AI call
        ai_start = time.time()
        response = await openai_service.process_message(message, context)
        ai_time = time.time() - ai_start
        logger.info(session_id, f"AI response in {ai_time:.2f}s")
        
        return response
    
    except Exception as e:
        logger.exception(session_id, f"Error processing message: {e}")
        raise
```

**Example Logs (Production):**
```
[session_abc123] [14:23:45] Processing message: Show me Temple project
[session_abc123] [14:23:45] Loading Google Sheets context
[session_abc123] [14:23:46] Context loaded in 0.78s
[session_abc123] [14:23:48] AI response in 1.92s
[session_xyz789] [14:23:47] Processing message: Create invoice
[session_xyz789] [14:23:47] Loading QuickBooks context
[session_xyz789] [14:23:48] Context loaded in 0.42s (cache HIT)
```

**Benefits:**
- ✅ Clear separation of multi-user requests
- ✅ Easy to trace a specific user's session
- ✅ Timing data for performance monitoring
- ✅ Works with Render's log aggregation
- ✅ Simple pattern - just pass session_id

**Why This Over ContextVar:**
- Simpler to understand and debug
- No async context issues
- Explicit > implicit for session tracking
- Easy to add to existing code

**Effort:** Low (1-2 hours)  
**Impact:** 🔥🔥 **GOOD**

---

#### **3.2 Performance Timing Metrics**
**Problem**: No visibility into which operations are slow

**Solution:**
```python
import time
from typing import Dict, Any

def log_timing(session_id: str, operation: str, duration: float):
    """Log operation timing for analysis"""
    logger.info(session_id, f"TIMING: {operation} took {duration:.3f}s")
    
    # Optional: Send to monitoring service
    # metrics.gauge(f"chat.{operation}.duration", duration)

@router.post("/")
async def process_chat_message(chat_data: Dict[str, Any]):
    start_time = time.time()
    session_id = chat_data.get("session_id", "default")
    
    # Context loading timing
    ctx_start = time.time()
    context = await build_context(message, google_service, qb_service, session_memory)
    log_timing(session_id, "context_build", time.time() - ctx_start)
    
    # AI call timing
    ai_start = time.time()
    response = await openai_service.process_message(message, context)
    log_timing(session_id, "openai_call", time.time() - ai_start)
    
    # Function execution timing (if AI called a function)
    if response.get("function_called"):
        fn_start = time.time()
        result = await execute_function(response["function_name"], response["arguments"])
        log_timing(session_id, f"function_{response['function_name']}", time.time() - fn_start)
    
    # Total request timing
    log_timing(session_id, "total_request", time.time() - start_time)
    
    return response
```

**Example Logs:**
```
[session_abc] TIMING: context_build took 0.823s
[session_abc] TIMING: openai_call took 1.942s
[session_abc] TIMING: function_update_project_status took 0.445s
[session_abc] TIMING: total_request took 3.210s
```

**Benefits:**
- ✅ Identify slow operations (context loading, AI, functions)
- ✅ Track performance over time
- ✅ Easy to add monitoring service later (DataDog, New Relic)
- ✅ Debug production slowness issues

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
| **🔥 P0** | **Write integration tests** | +300 | **Medium** | 🔥🔥🔥 | **CRITICAL** | ⏳ Pending |
| **🔥 P0** | Extract function handlers | -650, +200 | Medium | 🔥🔥🔥 | **CRITICAL** | ⏳ Pending |
| **⚡ P1** | Smart context loading | ~150 | Medium | 🔥🔥🔥 | **HIGH** | ⏳ Pending |
| **⚡ P1** | QuickBooks caching | ~80 | Low-Med | 🔥🔥🔥 | **HIGH** | ⏳ Pending |
| **📌 P2** | Truncate large lists | ~50 | Low | 🔥🔥 | **GOOD** | ⏳ Pending |
| **📌 P2** | Session logging | ~40 | Low | 🔥🔥 | **GOOD** | ⏳ Pending |
| **📌 P2** | Performance timing | ~40 | Low | 🔥 | **GOOD** | ⏳ Pending |
| **❌** | Extract prompt to file | - | - | - | **NOT WORTH IT** | ✅ Rejected |
| **❌** | Temperature control | - | - | - | **NOT WORTH IT** | ✅ Rejected |
| **❌** | Confirmation layer | - | - | - | **REDUNDANT** | ✅ Rejected |
| **❌** | Streaming responses | - | - | - | **TOO COMPLEX** | ✅ Rejected |
| **❌** | Sheets-based memory | - | - | - | **WRONG TOOL** | ✅ Rejected |

---

## 7. Implementation Timeline

### **Week 0: Pre-Refactor Safety (NEW - CRITICAL)** ⚠️
- **Day 1-2**: Create `tests/conftest.py` with mock fixtures
- **Day 3-4**: Create `tests/test_ai_handlers.py` with all 6 handler tests
- **Day 5**: Add regression test for DocNumber update feature
- **Day 6**: Run full test suite, fix any issues
- **Day 7**: Document testing patterns, commit test infrastructure

**Expected Result:** Full test coverage of existing behavior, safety net for refactoring

**Why This Week Matters:**
- Without tests, refactoring is **DANGEROUS**
- Tests document current behavior
- Catch breaking changes immediately
- Build confidence in subsequent changes

---

### **Week 1: Code Organization**
- **Day 1-2**: Create `handlers/ai_functions.py`, extract all 6 handlers
- **Day 3**: Add error handling pattern to all handlers
- **Day 4**: Update chat.py to use handler registry
- **Day 5**: Run tests - verify all pass, no regressions
- **Day 6**: Deploy to staging, monitor for issues
- **Day 7**: Production deployment

**Expected Result:** chat.py reduced from 967 → ~300 lines, all tests passing

---

### **Week 2: Performance**
- **Day 1-2**: Implement QuickBooks caching layer with manual invalidation
- **Day 2**: Test cache behavior (HIT/MISS logging)
- **Day 3**: Create `utils/context_builder.py` with smart loading
- **Day 4**: Integrate smart context into chat.py
- **Day 5**: Add list truncation/summarization
- **Day 6**: Performance testing and metrics collection
- **Day 7**: Deploy and monitor cache behavior

**Expected Result:** 80% fewer QB calls, 60% fewer tokens, 40% faster simple queries

---

### **Week 3: Polish**
- **Day 1**: Enhanced logging with session context
- **Day 2**: Performance timing metrics
- **Day 3**: Documentation updates (README, API docs)
- **Day 4**: Production monitoring setup
- **Day 5**: Final testing and validation
- **Day 6**: Team review and feedback
- **Day 7**: Final deployment

**Expected Result:** Better observability, production monitoring, complete documentation

---

## 8. Success Metrics

### Testing & Safety
- ✅ **100% test coverage** of all 6 AI function handlers
- ✅ **Regression tests** for critical features (DocNumber update, etc.)
- ✅ **Zero breaking changes** during refactoring
- ✅ Tests run in < 5 seconds (fast feedback loop)

### Code Quality
- ✅ chat.py: 967 lines → **~300 lines** (70% reduction)
- ✅ Modular handlers enable 10x faster feature additions
- ✅ Each handler independently testable
- ✅ Consistent error handling across all handlers

### Performance
- ✅ QuickBooks API calls: 200/day → **40/day** (80% reduction)
- ✅ OpenAI token usage: -60% for non-QB queries
- ✅ Response time for simple queries: 3s → **1.8s** (40% faster)
- ✅ Cache HIT rate > 80%

### Maintainability
- ✅ Adding new AI function: 80 lines in chat.py → **30 lines in handler file**
- ✅ Clear separation of concerns
- ✅ Session-aware logging for multi-user debugging
- ✅ Performance metrics for production monitoring
- ✅ Session-aware logging for multi-user debugging
- ✅ Performance metrics for production monitoring

---

## 9. Next Steps

1. **Review this revised plan** with team/stakeholder
2. **Create feature branch**: `refactor/chat-optimization`
3. **START WITH PHASE 0**: Write integration tests FIRST (critical safety measure)
4. **Then Phase 1**: Extract function handlers (biggest code impact)
5. **Test thoroughly** after each phase
6. **Monitor metrics** to validate improvements
7. **Document** patterns for future AI functions

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Refactoring breaks features** | **Phase 0: Write tests FIRST**, run after each change |
| Breaking existing functionality | Feature branch, comprehensive testing after each phase |
| Cache staleness | 5-minute TTL, **manual invalidation after writes** |
| Cache data inconsistency | Invalidate after create/update/delete operations |
| Smart context missing data | Default to Sheets context if no keywords match |
| Handler extraction bugs | Copy exact logic, error handling pattern, unit test each |
| Session logging overhead | Minimal - just string formatting, no I/O |
| Performance regression | Timing metrics before/after, monitor in production |

---

**Last Updated:** November 8, 2025 (Updated with external feedback)  
**Status:** Ready for Implementation  
**Next Review:** After Phase 0 (testing) completion

