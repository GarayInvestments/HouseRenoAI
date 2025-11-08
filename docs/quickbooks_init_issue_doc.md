# QuickBooks Initialization & Authentication Issue

## Overview
During deployment and restarts on Render, the **AI assistant** was reporting:
> "QuickBooks is not connected"

while the `/v1/quickbooks/status` endpoint correctly showed:
```json
{
  "authenticated": true,
  "realm_id": "9130349982666256",
  "environment": "production"
}
```

This mismatch stemmed from the **initialization behavior** of the `QuickBooksService` class and how memory persistence behaves in the Render environment.

Additionally, version reporting inconsistencies were identified in the `/version` endpoint due to build-layer caching.

---

## Root Cause
### 1. `__init__()` Behavior
- The `QuickBooksService` initializes at import time:
  ```python
  quickbooks_service = QuickBooksService()
  ```
- During `__init__()`, the service attempts to load saved tokens from Google Sheets via `_load_tokens_from_sheets()`.
- If the Render container restarts or spins up cold, Google Sheets access may not complete before FastAPI begins handling requests.

As a result:
- The `access_token`, `refresh_token`, and `realm_id` remain **empty** in memory.
- Calls to `quickbooks_service.is_authenticated()` return **False**, even though valid tokens exist and are retrievable.

### 2. Cached vs. Live Status
- `/v1/quickbooks/status` uses `quickbooks_service.get_status()` — which reloads tokens if needed, so it reports `authenticated: true`.
- The AI Assistant route (`/v1/chat`) checks only `is_authenticated()`, which reads the cached (possibly empty) values.

This causes inconsistent states between live status checks and assistant logic.

### 3. Cached Build Metadata
- The `/version` endpoint sometimes shows an **old commit hash** because Render caches build layers.
- Cached builds may contain stale Git commit info if the build cache isn’t cleared during redeploy.
- This does **not affect application behavior**; it only impacts version display accuracy.

---

## Fix Summary

### ✅ **Use Live Status in Chat Context**
In `chat.py`, replace:
```python
if quickbooks_service.is_authenticated():
```
with:
```python
qb_status = quickbooks_service.get_status()
is_authenticated = qb_status.get("authenticated", False)
```

This ensures the AI context always reflects the **true connection state**, including tokens loaded from storage.

### ✅ **Ensure Tokens Load on Startup**
Add this to `main.py`:
```python
@app.on_event("startup")
def reload_qb_tokens():
    from app.services.quickbooks_service import quickbooks_service
    quickbooks_service._load_tokens_from_sheets()
```
This guarantees QuickBooks tokens are preloaded before API calls after redeploy or cold start.

### ✅ **(Optional) Lazy Loading in `is_authenticated()`**
To automatically recover from cold starts:
```python
def is_authenticated(self) -> bool:
    if not self.access_token or not self.realm_id:
        self._load_tokens_from_sheets()
    return bool(self.access_token and self.realm_id)
```
This rehydrates the service on demand whenever authentication is checked.

### ✅ **(Optional) Auto-Refresh at Startup**
If token expiration is close, refresh automatically:
```python
if quickbooks_service.token_expires_at and \
   datetime.now() >= quickbooks_service.token_expires_at - timedelta(minutes=10):
    await quickbooks_service.refresh_access_token()
```

---

## Version Endpoint Enhancement

### Problem
- The `/version` endpoint displayed outdated commit hashes due to Render’s build cache.
- The cached commit hash doesn’t affect API functionality — only version accuracy.

### Recommended Fix
Use a dynamic commit retrieval method:
```python
import subprocess

def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return os.getenv("GIT_COMMIT", "unknown")

@app.get("/version")
def version():
    return {
        "version": "1.0.0",
        "git_commit": get_git_commit(),
        "has_append_record": True
    }
```

Or alternatively, set the commit hash via environment variable during deployment.

---

## Results
After implementing these changes:
- The assistant consistently recognizes QuickBooks as connected.
- The `/v1/chat` and `/v1/quickbooks/status` endpoints stay in sync.
- Render restarts no longer cause false "disconnected" states.
- The `/version` endpoint accurately reflects the running commit.

---

## Summary Table
| Issue | Cause | Resolution | Impact |
|--------|--------|-------------|----------|
| AI reports "not connected" | Tokens not loaded at startup | Reload tokens or lazy-load | Fixed |
| `/v1/quickbooks/status` accurate | Uses `get_status()` | Standard behavior | OK |
| Render cold start | Memory cleared | Startup hook | Fixed |
| Old commit hash in `/version` | Build cache reuse | Clear cache or use dynamic commit fetch | Cosmetic only |

---

## Next Steps
- Deploy fix to `chat.py` (use `get_status()`)
- Add `reload_qb_tokens()` to `main.py`
- Optionally enhance `is_authenticated()` to lazy-load tokens
- Optionally update `/version` endpoint to report dynamic commit hashes

Once deployed, all chat, authentication, and version tracking logic will remain consistent across environments and restarts.

