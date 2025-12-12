# Modern Authentication System Migration Guide

## Overview

This guide walks through migrating from the legacy authentication system to a modern, secure token-based system following OAuth2 and industry best practices.

---

## What's New

### 🔐 Security Improvements

**Before (Legacy System)**:
- 7-day access tokens (no rotation)
- Using OPENAI_API_KEY as JWT secret ⚠️
- No token revocation
- No refresh tokens
- No session management
- Mixed Google Sheets + Supabase Auth
- No rate limiting

**After (Modern System)**:
- 15-minute access tokens with refresh token rotation
- Dedicated JWT_SECRET environment variable
- Token blacklist for immediate revocation
- 30-day refresh tokens with automatic rotation
- Session management and device tracking
- Supabase Auth integration (primary)
- Login attempt tracking and rate limiting
- Token family tracking (detects token theft)

### 📊 New Database Tables

1. **`refresh_tokens`** - Refresh token storage with rotation tracking
2. **`token_blacklist`** - Revoked access tokens (before natural expiration)
3. **`user_sessions`** - Active session management and device tracking
4. **`login_attempts`** - Security monitoring and rate limiting

---

## Migration Steps

### Phase 1: Environment Setup

#### 1. Add New Environment Variable

Create a dedicated JWT secret (separate from OPENAI_API_KEY):

```bash
# Generate a strong secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add to `.env`:
```ini
# Dedicated JWT secret (REQUIRED for production)
JWT_SECRET=your-generated-secret-here

# Keep existing for backward compatibility
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
```

Add to Fly.io secrets:
```bash
fly secrets set JWT_SECRET="your-generated-secret-here"
fly secrets set SUPABASE_JWT_SECRET="your-supabase-jwt-secret"
```

#### 2. Update Config

Update `app/config.py`:
```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # JWT Authentication (NEW)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short-lived
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30    # Long-lived
    
    # Supabase JWT (for verification)
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
```

### Phase 2: Database Migration

#### 1. Run Migration

```bash
# Review migration
alembic show 20251211_1630_add_auth_tables

# Apply migration
alembic upgrade head

# Verify tables created
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres" -c "\dt *auth*"
```

Expected output:
```
                  List of relations
 Schema |     Name       | Type  |   Owner   
--------+----------------+-------+-----------
 public | refresh_tokens | table | postgres
 public | token_blacklist| table | postgres
 public | user_sessions  | table | postgres
 public | login_attempts | table | postgres
```

#### 2. Verify Indexes

```bash
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres" -c "
SELECT 
    tablename, 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('refresh_tokens', 'token_blacklist', 'user_sessions', 'login_attempts')
ORDER BY tablename, indexname;
"
```

### Phase 3: Code Update

#### 1. Update Main App

Update `app/main.py`:

```python
# OLD
from app.middleware.auth_middleware import JWTAuthMiddleware

# NEW
from app.middleware.auth_middleware_v2 import JWTAuthMiddleware

# OLD
from app.routes import auth

# NEW
from app.routes import auth_v2 as auth

# Register routes
app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
```

#### 2. Update Database Session

Ensure `app/db/session.py` exports `get_db`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    """Dependency for database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### 3. Update Models Import

Update `app/db/models.py`:

```python
# Add at the end of file
from app.db.models_auth import RefreshToken, TokenBlacklist, UserSession, LoginAttempt

__all__ = [
    "Base",
    "Client",
    "Project",
    "Permit",
    "Payment",
    "User",
    "RefreshToken",
    "TokenBlacklist",
    "UserSession",
    "LoginAttempt",
]
```

### Phase 4: Frontend Update

#### 1. Update Token Storage

Update `frontend/src/services/authService.js`:

```javascript
// OLD: Store single token
localStorage.setItem('token', response.access_token);

// NEW: Store both tokens
localStorage.setItem('access_token', response.access_token);
localStorage.setItem('refresh_token', response.refresh_token);
localStorage.setItem('token_expires', Date.now() + 15 * 60 * 1000); // 15 min
```

#### 2. Implement Token Refresh

Add automatic token refresh:

```javascript
// frontend/src/services/authService.js

export const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }
  
  try {
    const response = await fetch(`${API_URL}/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    
    if (!response.ok) {
      // Refresh token expired - force re-login
      logout();
      throw new Error('Session expired');
    }
    
    const data = await response.json();
    
    // Update stored tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('token_expires', Date.now() + 15 * 60 * 1000);
    
    return data.access_token;
  } catch (error) {
    console.error('Token refresh failed:', error);
    logout();
    throw error;
  }
};

// Axios interceptor for automatic refresh
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const newToken = await refreshAccessToken();
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

#### 3. Update Login/Logout

```javascript
// frontend/src/services/authService.js

export const login = async (email, password) => {
  const response = await fetch(`${API_URL}/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      email, 
      password,
      device_name: `${navigator.platform} - ${navigator.userAgent.split(' ')[0]}`
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  const data = await response.json();
  
  // Store tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem('token_expires', Date.now() + 15 * 60 * 1000);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  return data.user;
};

export const logout = async () => {
  const accessToken = localStorage.getItem('access_token');
  
  if (accessToken) {
    try {
      await fetch(`${API_URL}/v1/auth/logout`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
    } catch (error) {
      console.error('Logout request failed:', error);
    }
  }
  
  // Clear local storage
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('token_expires');
  localStorage.removeItem('user');
  
  window.location.href = '/login';
};
```

### Phase 5: Testing

#### 1. Test Login Flow

```bash
# Test login
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "steve@houserenovatorsllc.com",
    "password": "your-password",
    "device_name": "Testing CLI"
  }'

# Response:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "abc123...",
#   "token_type": "bearer",
#   "expires_in": 900,
#   "user": { ... }
# }
```

#### 2. Test Protected Endpoint

```bash
# Use access token
curl http://localhost:8000/v1/auth/me \
  -H "Authorization: Bearer <access_token>"

# Response: User info
```

#### 3. Test Token Refresh

```bash
# After 15 minutes, access token expires
curl -X POST http://localhost:8000/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'

# Response: New access token + new refresh token
```

#### 4. Test Logout

```bash
# Logout (revokes all tokens)
curl -X POST http://localhost:8000/v1/auth/logout \
  -H "Authorization: Bearer <access_token>"

# Try to use old token (should fail)
curl http://localhost:8000/v1/auth/me \
  -H "Authorization: Bearer <access_token>"

# Response: 401 Unauthorized - Token revoked
```

#### 5. Test Session Management

```bash
# View active sessions
curl http://localhost:8000/v1/auth/sessions \
  -H "Authorization: Bearer <access_token>"

# Revoke specific session
curl -X DELETE http://localhost:8000/v1/auth/sessions/<session_id> \
  -H "Authorization: Bearer <access_token>"
```

---

## Security Features

### Token Rotation

Every time a refresh token is used:
1. Old refresh token is marked as "used"
2. New refresh token is generated
3. If old refresh token is reused → entire token family revoked (token theft detected)

### Rate Limiting

Login attempts limited to:
- 5 attempts per 15 minutes per email
- Tracks IP address for additional security
- Logs all attempts for monitoring

### Token Blacklist

Access tokens can be revoked before natural expiration:
- User logout → blacklist current token
- Password reset → blacklist all tokens
- Admin action → blacklist specific tokens

### Session Management

Users can:
- View all active sessions (devices/locations)
- Revoke specific sessions remotely
- Logout from all devices

---

## Monitoring

### Check Refresh Token Usage

```sql
-- Active refresh tokens per user
SELECT 
    u.email,
    COUNT(*) FILTER (WHERE rt.is_revoked = false) as active_tokens,
    COUNT(*) FILTER (WHERE rt.is_used = true) as used_tokens,
    MAX(rt.issued_at) as last_issued
FROM users u
LEFT JOIN refresh_tokens rt ON u.id = rt.user_id
GROUP BY u.email
ORDER BY last_issued DESC;
```

### Check Login Attempts

```sql
-- Failed login attempts (last 24 hours)
SELECT 
    email,
    COUNT(*) as attempts,
    MAX(attempted_at) as last_attempt,
    string_agg(DISTINCT ip_address::text, ', ') as ip_addresses
FROM login_attempts
WHERE success = false 
AND attempted_at > NOW() - INTERVAL '24 hours'
GROUP BY email
HAVING COUNT(*) > 3
ORDER BY attempts DESC;
```

### Check Active Sessions

```sql
-- Active sessions per user
SELECT 
    u.email,
    COUNT(*) as active_sessions,
    string_agg(us.device_name, ', ') as devices
FROM users u
JOIN user_sessions us ON u.id = us.user_id
WHERE us.is_active = true
GROUP BY u.email
ORDER BY active_sessions DESC;
```

---

## Rollback Plan

If issues arise, rollback to legacy system:

### 1. Revert Code Changes

```bash
git revert <commit-hash>  # Revert to old auth_service.py
```

### 2. Keep Database Tables

Authentication tables don't conflict with legacy system. Keep them for data retention.

### 3. Switch Environment Variables

```bash
# Use SUPABASE_JWT_SECRET instead of JWT_SECRET
fly secrets unset JWT_SECRET
```

---

## Troubleshooting

### Issue: "Invalid or expired token"

**Cause**: Access token expired (15 minutes)
**Solution**: Frontend should automatically refresh using refresh token

### Issue: "Token has been revoked"

**Cause**: User logged out or password was reset
**Solution**: Re-authenticate

### Issue: "Rate limit exceeded"

**Cause**: Too many failed login attempts
**Solution**: Wait 15 minutes or contact admin to clear login_attempts

### Issue: Token theft detected

**Symptom**: All tokens revoked unexpectedly
**Cause**: Refresh token was reused (indicates token was stolen)
**Solution**: Re-authenticate, investigate security breach

---

## Performance

### Token Validation

- Access token verification: < 1ms (no database query)
- Blacklist check: < 5ms (indexed query)
- User lookup: < 10ms (indexed query)

### Token Refresh

- Refresh flow: < 50ms (database writes)
- Includes token rotation and session update

### Session Management

- Active sessions query: < 20ms
- Session revocation: < 30ms

---

## Next Steps

### Phase 1 (Immediate)
- ✅ Run database migration
- ✅ Update environment variables
- ✅ Deploy backend with new auth system
- ⏳ Update frontend token handling

### Phase 2 (Week 1)
- ⏳ Add Supabase Auth API integration
- ⏳ Implement email verification flow
- ⏳ Add "View Active Sessions" UI
- ⏳ Add "Sign out other devices" feature

### Phase 3 (Week 2)
- ⏳ Add 2FA support
- ⏳ Add OAuth providers (Google, Microsoft)
- ⏳ Add security dashboard (failed logins, etc.)
- ⏳ Add automated security alerts

---

## References

- **Token Service**: `app/services/auth_service_v2.py`
- **Auth Routes**: `app/routes/auth_v2.py`
- **Middleware**: `app/middleware/auth_middleware_v2.py`
- **Models**: `app/db/models_auth.py`
- **Migration**: `alembic/versions/20251211_1630_add_auth_tables.py`
