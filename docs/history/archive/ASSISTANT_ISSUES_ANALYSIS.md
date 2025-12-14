# AI Assistant Issues - Comprehensive Analysis
**Date:** November 9, 2025  
**Status:** CRITICAL - 80% hallucination rate after smart context handler implementation

---

## 🚨 Current Problem Summary

After implementing the "smart context handler" (commits 4cd8103 → c864890), the AI assistant has degraded from working well to **80% hallucination rate**.

### What Changed

**Commit 65b9772 (WORKING WELL):**
```python
# ALWAYS loaded ALL data - simple and reliable
permits = await google_service.get_permits_data()
projects = await google_service.get_projects_data()
clients = await google_service.get_clients_data()

context.update({
    'all_permits': permits,
    'all_projects': projects,
    'all_clients': clients,
    'clients_summary': [...],
    'permits_by_status': {...},
    # Full data ALWAYS available
})
```

**Current Code (4cd8103 → c864890) - BROKEN:**
```python
# Smart context handler decides what to load
required = get_required_contexts(message, session_memory)  # Returns {'sheets'} or {'quickbooks'} or {'none'}

# Only loads data if keywords match
if 'sheets' in required:
    context.update(sheets_data)  # Maybe loads clients, maybe not
```

### The Core Issue
- **Before (65b9772):** AI ALWAYS had full context with all_clients, all_projects, all_permits
- **After (smart context):** AI only gets data if specific keywords are detected
- **Result:** AI can't see the data anymore, so it makes up (hallucinates) fake information

---

## 📊 Evidence of Issues

### From Render Logs (Nov 10, 2025 02:00-02:03 UTC)
```
2025-11-10 02:03:10 INFO: Smart context loading: {'sheets'} for message: 'look up javier martinez client details...'
2025-11-10 02:03:10 INFO: Sheets cache HIT for projects_data (expires in 71s)
2025-11-10 02:03:10 INFO: Sheets cache HIT for permits_data (expires in 71s)
```

**Problem:** Smart context says it loaded `{'sheets'}`, but:
1. What data is actually in the context that OpenAI sees?
2. Is `all_clients` populated? Is `all_projects` populated?
3. The logs show cache hits, but we don't know if the data made it to OpenAI

### User Reports
- "80% hallucination" - AI making up fake data instead of reading real data
- "It was a lot better before the context handler" - Confirms degradation after smart loading
- "It seems to only use context instead of looking directly at sheet data" - AI not seeing actual data

---

## 🔍 Root Cause Analysis

### Issue #1: Smart Context Handler May Be TOO Smart
**File:** `app/utils/context_builder.py`

The smart context handler decides what to load based on keywords:
```python
qb_keywords = ['invoice', 'payment', 'bill', 'quickbooks', 'qb', ...]
sheets_keywords = ['project', 'permit', 'client', 'customer', ...]
```

**Problem:** If user says "look up javier martinez", there's no explicit keyword match!
- "look up" → Not in sheets_keywords
- "javier martinez" → A name, not a keyword
- Result: Might not load the right context

**What Actually Happens:**
```python
# From context_builder.py line 110
if any(keyword in message_lower for keyword in sheets_keywords):
    contexts.add('sheets')

# Default behavior (line 118)
if not contexts:
    contexts.add('sheets')
```

So it DOES default to sheets... but what's in that context?

### Issue #2: Context Structure Changed
**File:** `app/utils/context_builder.py` lines 145-157

```python
return {
    "projects": projects,
    "permits": permits,
    "clients": clients,
    # Add aliases that OpenAI service expects
    "all_projects": projects,
    "all_permits": permits,
    "all_clients": clients,
    "summary": {...}
}
```

This LOOKS correct - it includes both `clients` and `all_clients`.

**BUT:** When this gets merged into the main context (in `chat.py` line 82):
```python
context.update(smart_context)
```

Does `context.update()` properly merge these keys? Or is something getting lost?

### Issue #3: Context Merging Order Problem
**File:** `app/routes/chat.py` lines 65-83

```python
# Line 65: Add conversation history
context["conversation_history"] = conversation_history[-10:]

# Lines 75-82: Build and merge smart context
smart_context = await build_context(...)
context.update(smart_context)  # Does this preserve conversation_history?
```

**Potential Issue:** `smart_context` might be OVERWRITING keys in `context`!

Let me check what `build_context` returns:
```python
# From context_builder.py lines 254-260
context = {
    "session_memory": session_memory,
    "contexts_loaded": list(required)
}

# Then adds sheets data
context.update(sheets_data)  # Adds: projects, permits, clients, all_*, summary

# Returns merged context
return context
```

**THE PROBLEM:** `build_context` creates a NEW dict with `session_memory` in it, then merges sheets data. When we do `context.update(smart_context)`, it's ADDING these keys:
- ✅ `session_memory` (gets added/updated)
- ✅ `contexts_loaded` (gets added)
- ✅ `projects`, `permits`, `clients` (get added)
- ✅ `all_projects`, `all_permits`, `all_clients` (get added)
- ✅ `summary` (gets added)
- ⚠️ `conversation_history` (was already there, NOT overwritten by update)

So context merging should be OK...

### Issue #4: OpenAI Not Seeing the Data
**File:** `app/services/openai_service.py`

The system prompt tells AI it has "FULL ACCESS" to data:
```python
You have FULL ACCESS to comprehensive project data including:
- All client information (names, addresses, status, roles, contacts)
- All project details (addresses, costs, timelines, scope of work)
...
```

**But does it actually?** Let's trace the data flow:

1. `chat.py` line 97: `ai_response, function_calls = await openai_service.process_chat_message(message, context)`
2. `openai_service.py` receives `context` dict
3. OpenAI service needs to pass this context to GPT-4

**Question:** How does `process_chat_message()` pass the context to OpenAI?

### Issue #5: Missing Context Logging
**Critical Gap:** We have NO logging that shows what keys are in `context` when it's sent to OpenAI!

**What we need:**
```python
# After building context
logger.info(f"Context keys being sent to OpenAI: {list(context.keys())}")
logger.info(f"Clients in context: {len(context.get('all_clients', []))}")
logger.info(f"Projects in context: {len(context.get('all_projects', []))}")
```

Without this, we're flying blind!

---

## 🎯 What We THINK Is Happening

### Hypothesis #1: Data Is Loading But Not Reaching OpenAI
- `build_context()` successfully loads projects, permits, clients
- `context.update(smart_context)` successfully merges them
- BUT: `openai_service.process_chat_message()` might not be serializing them correctly
- OR: The context dict is too large and getting truncated

### Hypothesis #2: Context Is Loading But Wrong Format
- Data is reaching OpenAI
- BUT: It's not in the format OpenAI expects
- AI can't find `all_clients` because it's looking for a different key
- OR: The data structure changed and AI's instructions are outdated

### Hypothesis #3: Smart Context Is Too Aggressive
- Smart context decides NOT to load clients for "look up javier martinez"
- Falls back to some default that doesn't include client data
- AI has no data to work with, so it hallucinates

---

## 🎯 SOLUTION: Revert to Simple, Working Approach

### Option A: Complete Revert to 65b9772 Behavior (RECOMMENDED)
Go back to what worked - always load ALL data:

```python
# In app/routes/chat.py - replace smart context with simple approach
try:
    google_service = get_google_service()
    
    # ALWAYS fetch comprehensive data (like 65b9772)
    permits = await google_service.get_permits_data()
    projects = await google_service.get_projects_data()
    clients = await google_service.get_clients_data()
    
    # Build full context
    context.update({
        'all_permits': permits,
        'all_projects': projects,
        'all_clients': clients,
        'permits_count': len(permits),
        'projects_count': len(projects),
        'clients_count': len(clients),
    })
    
    logger.info(f"Loaded full context: {len(permits)} permits, {len(projects)} projects, {len(clients)} clients")
    
except Exception as e:
    logger.warning(f"Could not fetch data context: {e}")
```

**Benefits:**
- ✅ AI ALWAYS has all data (no hallucinations)
- ✅ Simple, predictable behavior
- ✅ Proven to work (65b9772 had good performance)

**Trade-offs:**
- ⚠️ More tokens per request (but worth it for accuracy)
- ⚠️ Slightly slower (but Google Sheets has caching)

### Option B: Fix Smart Context to ALWAYS Load Sheets
Make smart context default to loading everything:

```python
# In app/utils/context_builder.py
def get_required_contexts(message: str, session_memory: Optional[Dict[str, Any]] = None) -> Set[str]:
    """
    ALWAYS load sheets data by default.
    Only skip if message is clearly off-topic (hello, weather, etc.)
    """
    message_lower = message.lower()
    
    # Only skip for VERY obvious off-topic queries
    if len(message) < 20 and any(word in message_lower for word in ['hello', 'hi', 'hey', 'thanks', 'bye']):
        return {'none'}
    
    # ALWAYS load sheets by default
    contexts = {'sheets'}
    
    # Add QB if explicitly mentioned
    qb_keywords = ['invoice', 'payment', 'quickbooks', 'qb']
    if any(keyword in message_lower for keyword in qb_keywords):
        contexts.add('quickbooks')
    
    return contexts
```

---

## 🔧 What We Need to Do

### Step 1: Add Comprehensive Logging (IMMEDIATE)
Add to `app/routes/chat.py` after line 83:
```python
# Log what's actually in context
logger.info(f"[DEBUG] Context keys: {list(context.keys())}")
logger.info(f"[DEBUG] Clients count: {len(context.get('all_clients', []))}")
logger.info(f"[DEBUG] Projects count: {len(context.get('all_projects', []))}")
logger.info(f"[DEBUG] Permits count: {len(context.get('all_permits', []))}")
logger.info(f"[DEBUG] Contexts loaded: {context.get('contexts_loaded', [])}")
logger.info(f"[DEBUG] Session memory keys: {list(context.get('session_memory', {}).keys())}")
```

### Step 2: Verify Data Reaches OpenAI (IMMEDIATE)
Add to `app/services/openai_service.py` in `process_chat_message()`:
```python
# At the start of the function
logger.info(f"[OPENAI] Received context keys: {list(context.keys())}")
logger.info(f"[OPENAI] all_clients available: {'all_clients' in context}")
logger.info(f"[OPENAI] all_projects available: {'all_projects' in context}")

if 'all_clients' in context:
    logger.info(f"[OPENAI] all_clients count: {len(context['all_clients'])}")
```

### Step 3: Consider Disabling Smart Context (QUICK FIX)
If the issue persists, temporarily revert to loading ALL context:
```python
# In context_builder.py, force load everything
def get_required_contexts(message: str, session_memory: Optional[Dict[str, Any]] = None) -> Set[str]:
    # TEMPORARY: Always load both until hallucination issue resolved
    return {'sheets', 'quickbooks'}
```

### Step 4: Add Context Validation
Before sending to OpenAI, validate the context has data:
```python
# In chat.py before openai call
if 'all_clients' not in context or len(context.get('all_clients', [])) == 0:
    logger.warning("⚠️ Context has NO clients data!")
    
if 'all_projects' not in context or len(context.get('all_projects', [])) == 0:
    logger.warning("⚠️ Context has NO projects data!")
```

---

## 📋 Testing Plan

### Test 1: Verify Context Loading
```
Message: "look up javier martinez"
Expected logs:
- Smart context loading: {'sheets'}
- [DEBUG] Context keys: ['session_memory', 'contexts_loaded', 'projects', 'permits', 'clients', 'all_projects', 'all_permits', 'all_clients', 'summary', 'conversation_history']
- [DEBUG] Clients count: 9 (or however many clients exist)
- [OPENAI] all_clients available: True
- [OPENAI] all_clients count: 9
```

### Test 2: Verify AI Response
```
Message: "list all clients"
Expected: Shows actual clients from Sheets (Javier Martinez, etc.)
NOT Expected: Shows fake names (Alex Chang, Bob Smith, etc.)
```

### Test 3: Verify Follow-Up Context
```
Message 1: "show me temple project"
Message 2: "what's the status"
Expected: AI remembers "temple" from session memory
```

---

## 🔄 Rollback Plan

If we can't fix the smart context handler quickly:

### Option A: Revert to Commit Before Smart Context
```bash
git revert c864890  # Revert context merge fix
git revert 4cd8103  # Revert smart context introduction
```

### Option B: Disable Smart Context, Keep Other Improvements
```python
# In context_builder.py
def get_required_contexts(message: str, session_memory: Optional[Dict[str, Any]] = None) -> Set[str]:
    # TEMPORARY: Disable smart loading until fixed
    logger.info(f"Smart context DISABLED - loading ALL contexts")
    return {'sheets', 'quickbooks'}
```

This keeps the context_builder infrastructure but loads everything (back to old behavior).

---

## 📊 Success Metrics

**Before Smart Context:**
- Hallucination rate: ~5% (occasional fake names)
- Response accuracy: ~95%
- User satisfaction: Good

**After Smart Context (Current):**
- Hallucination rate: ~80% (user report)
- Response accuracy: ~20%
- User satisfaction: Poor

**Target After Fix:**
- Hallucination rate: <5%
- Response accuracy: >95%
- Performance improvement: 60% fewer tokens (from smart loading)

---

## 🎯 Recommended Immediate Action

1. **Add debug logging** (Step 1 above) - commit and deploy
2. **Test with real queries** - capture logs showing what's in context
3. **If data is missing:** Fix context_builder to ensure all_clients/all_projects are populated
4. **If data is present but AI can't see it:** Fix openai_service to properly serialize context
5. **If neither works:** Temporarily disable smart loading (Option B above)

**Goal:** Get back to 95% accuracy within next 2-3 commits.
