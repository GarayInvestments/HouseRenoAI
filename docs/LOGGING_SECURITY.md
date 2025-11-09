# Logging Security Guide

## Overview
The `app/utils/sanitizer.py` module provides automatic sanitization of sensitive data in logs to prevent credential leakage.

## What Gets Redacted

### Automatic Pattern Detection:
- **JWT Tokens**: `eyJhbGci...` → Shows first 8 + last 4 chars
- **Bearer Tokens**: `Bearer xyz123...` → `[REDACTED]`
- **API Keys**: Long alphanumeric strings (32+ chars)
- **Passwords**: Any field named `password`, `pwd`, `passwd`
- **OAuth Tokens**: `access_token`, `refresh_token`, `client_secret`
- **Authorization Headers**: Full header value redacted

### Sensitive Dictionary Keys:
Any key containing these words (case-insensitive):
- `password`, `secret`, `token`, `api_key`, `authorization`, `auth`
- `OPENAI_API_KEY`, `QUICKBOOKS_CLIENT_SECRET`, `JWT_SECRET_KEY`

## Usage Examples

### 1. Sanitize Before Logging (Manual)
```python
from app.utils.sanitizer import sanitize_log_message
import logging

logger = logging.getLogger(__name__)

# Sanitize strings
user_input = "My token is eyJhbGci..."
logger.info(f"User input: {sanitize_log_message(user_input)}")
# Output: User input: My token is eyJhbGci...sR8U

# Sanitize dicts
request_data = {
    "email": "user@example.com",
    "password": "secret123",
    "access_token": "sk-proj-abc123"
}
logger.info(f"Request: {sanitize_log_message(request_data)}")
# Output: Request: {'email': 'user@example.com', 'password': '[REDACTED]', 'access_token': '[REDACTED]'}
```

### 2. Automatic Sanitization (Recommended)
```python
from app.utils.sanitizer import create_safe_logger
import logging

logger = create_safe_logger(logging.getLogger(__name__))

# All messages automatically sanitized
logger.info("Token: eyJhbGci...")  # Automatically redacted
logger.error(f"Auth failed: {auth_header}")  # Automatically sanitized
logger.debug(request_data)  # Sensitive keys automatically redacted
```

### 3. Apply to Existing Routes
**Before:**
```python
# app/routes/auth.py
logger.info(f"Login attempt: {request_data}")  # ⚠️ May leak password
```

**After:**
```python
from app.utils.sanitizer import sanitize_log_message

logger.info(f"Login attempt: {sanitize_log_message(request_data)}")  # ✅ Safe
```

## When to Use

### ✅ Always Sanitize:
- Request/response bodies containing user input
- Authentication headers (`Authorization: Bearer ...`)
- OAuth token exchanges
- Error messages that might contain sensitive data
- Database query parameters with passwords
- Environment variables being logged

### ❌ No Need to Sanitize:
- Simple status messages ("User logged in", "Request completed")
- Performance metrics (timing, counts)
- Non-sensitive IDs (project IDs, client IDs - not auth tokens)
- Public data (project names, addresses)

## Implementation Checklist

### Critical Routes to Update:
- [x] ~~`app/routes/auth.py`~~ - Login/register (passwords, tokens)
- [ ] `app/routes/chat.py` - May log request data with session IDs
- [ ] `app/services/openai_service.py` - API key in headers
- [ ] `app/services/quickbooks_service.py` - OAuth tokens, refresh tokens
- [ ] `app/services/auth_service.py` - Password hashing, JWT generation
- [ ] `app/middleware/auth_middleware.py` - JWT validation errors

### Testing
Run the sanitizer test:
```bash
python app/utils/sanitizer.py
```

Expected output:
```
Testing sanitizer...

JWT: eyJhbGci...sR8U
Dict: {'email': 'user@example.com', 'password': '[REDACTED]', 'access_token': '[REDACTED]', 'client_name': 'John Doe'}
Auth Header: [REDACTED]
```

## Production Monitoring

### Check Render Logs for Leaks:
```bash
# Search for potential JWT tokens
render logs -r srv-d44ak76uk2gs73a3psig --text "eyJ" --limit 50 --confirm

# Search for Bearer tokens
render logs -r srv-d44ak76uk2gs73a3psig --text "Bearer" --limit 50 --confirm

# Search for password fields
render logs -r srv-d44ak76uk2gs73a3psig --text "password" --limit 50 --confirm
```

If you find unsanitized secrets:
1. Rotate the exposed credentials immediately
2. Update the route to use `sanitize_log_message()`
3. Deploy fix to production
4. Verify in logs that data is now redacted

## Best Practices

1. **Sanitize Early**: Apply sanitization at the logging call, not in the sanitizer itself
2. **Test Thoroughly**: Check logs after deploying changes
3. **Don't Over-Redact**: Keep useful debugging info (client names, IDs, timestamps)
4. **Document Exceptions**: If a route legitimately needs to log sensitive data (e.g., secure audit logs), document why
5. **Regular Audits**: Periodically review production logs for new leak patterns

## Examples from Codebase

### Chat Route (High Priority)
```python
# app/routes/chat.py
from app.utils.sanitizer import sanitize_log_message

logger.info(f"Chat request: {sanitize_log_message(chat_data)}")
logger.info(f"Context: {sanitize_log_message(context)}")  # May contain tokens
```

### QuickBooks Service
```python
# app/services/quickbooks_service.py
from app.utils.sanitizer import sanitize_log_message

logger.info(f"QB token refresh: {sanitize_log_message(token_response)}")
logger.debug(f"Auth header: {sanitize_log_message(headers)}")
```

### Auth Middleware
```python
# app/middleware/auth_middleware.py
from app.utils.sanitizer import sanitize_log_message

logger.error(f"JWT validation failed: {sanitize_log_message(str(e))}")
```

## Migration Plan

1. ✅ Create sanitizer utility
2. ✅ Document usage guidelines
3. Update critical routes (auth, QB, OpenAI)
4. Test in development
5. Deploy to production
6. Monitor logs for 24 hours
7. Audit remaining routes

## Security Impact

**Before Sanitization:**
```
2025-11-09 16:42:14  INFO: Login request: {"email": "admin@example.com", "password": "MyP@ssw0rd123"}
2025-11-09 16:42:15  INFO: JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0...
```

**After Sanitization:**
```
2025-11-09 16:42:14  INFO: Login request: {"email": "admin@example.com", "password": "[REDACTED]"}
2025-11-09 16:42:15  INFO: JWT token: eyJhbGci...R8U
```

✅ **Prevents**: Credential theft, session hijacking, API key exposure  
✅ **Preserves**: Debugging context, error tracing, performance metrics
