# Authentication System Architecture

**Version**: 2.0 (JWT with Refresh Tokens)  
**Last Updated**: December 13, 2025  
**Status**: Production (Active)

> **Consolidated from**: AUTH_QUICK_REFERENCE.md, AUTH_MIGRATION_GUIDE.md, AUTH_SYSTEM_SUMMARY.md

---

## 1. Architecture Overview

### Current System (v2.0 - JWT with Refresh Tokens)

**Components**:
- **Access Tokens**: Short-lived (15 min), used for API authentication
- **Refresh Tokens**: Long-lived (30 days), used to obtain new access tokens
- **Token Blacklist**: Revoked tokens stored in PostgreSQL
- **Session Management**: Multi-device support with activity tracking
- **Middleware**: Automatic JWT verification on all routes except PUBLIC_ROUTES

**Storage**:
- **Database**: PostgreSQL `users` table (Supabase)
- **Tokens**: JWT signed with HS256 algorithm
- **Secrets**: `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY` (environment variables)

---

## 2. Authentication Flow

### Login Flow
```
1. User submits credentials (email + password)
   ↓
2. Backend validates via Supabase Auth
   ↓
3. Generate access token (15 min expiry)
   ↓
4. Generate refresh token (30 days expiry)
   ↓
5. Create session record in database
   ↓
6. Return both tokens to client
   ↓
7. Client stores tokens (secure storage)
```

### API Request Flow
```
1. Client sends: Authorization: Bearer <access_token>
   ↓
2. JWTAuthMiddleware intercepts request
   ↓
3. Verify token signature & expiry
   ↓
4. Check token blacklist (not revoked)
   ↓
5. Load user from database
   ↓
6. Attach user to request (available as current_user)
   ↓
7. Route handler executes with authenticated user
```

### Token Refresh Flow
```
1. Access token expires (15 min)
   ↓
2. Client calls POST /v1/auth/refresh with refresh token
   ↓
3. Backend verifies refresh token
   ↓
4. Check session is still active
   ↓
5. Generate new access token (15 min)
   ↓
6. Rotate refresh token (new 30-day token)
   ↓
7. Blacklist old refresh token
   ↓
8. Return new tokens to client
```

### Logout Flow
```
1. Client calls POST /v1/auth/logout
   ↓
2. Backend extracts tokens from request
   ↓
3. Blacklist access token (remaining TTL)
   ↓
4. Blacklist refresh token (full 30 days)
   ↓
5. Mark session as inactive
   ↓
6. Return success
```

---

## 3. API Endpoints

### Authentication Endpoints

#### POST /v1/auth/register
**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

#### POST /v1/auth/login
**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK): Same as register

#### POST /v1/auth/refresh
**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### POST /v1/auth/logout
**Headers**: `Authorization: Bearer <access_token>`

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

#### GET /v1/auth/me
**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-12-13T10:00:00Z"
}
```

---

## 4. Protected Route Pattern

### Backend Implementation

```python
from app.routes.auth_v2 import get_current_user
from app.db.models import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    # current_user is User model from database
    return {"message": f"Hello {current_user.full_name}"}
```

### Frontend Implementation

```javascript
// Store access token securely
const { access_token, refresh_token } = await login(email, password);
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);

// Make authenticated request
const response = await fetch('/v1/protected', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

// Handle 401 (token expired)
if (response.status === 401) {
  // Try to refresh token
  const refreshResponse = await fetch('/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      refresh_token: localStorage.getItem('refresh_token')
    })
  });
  
  if (refreshResponse.ok) {
    const { access_token, refresh_token } = await refreshResponse.json();
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    // Retry original request
  } else {
    // Refresh failed, redirect to login
    window.location.href = '/login';
  }
}
```

---

## 5. Security Features

### Token Security
- ✅ **Short-lived access tokens** (15 min) - Limits exposure window
- ✅ **Refresh token rotation** - New refresh token on every refresh
- ✅ **Token blacklisting** - Revoked tokens cannot be reused
- ✅ **HMAC-SHA256 signing** - Cryptographically secure signatures
- ✅ **Secret key rotation** - Can rotate keys via environment variables

### Password Security
- ✅ **bcrypt hashing** - Industry-standard password hashing
- ✅ **Salt per password** - Prevents rainbow table attacks
- ✅ **Cost factor 12** - Balances security and performance

### Session Security
- ✅ **Device tracking** - User agent and IP address logged
- ✅ **Multi-device support** - Multiple active sessions per user
- ✅ **Session revocation** - Can invalidate all user sessions
- ✅ **Activity timestamps** - Track last activity per session

### Request Security
- ✅ **Automatic middleware** - All routes protected by default
- ✅ **Public route whitelist** - Explicit list of unprotected routes
- ✅ **User injection** - Authenticated user attached to request context
- ✅ **Token validation** - Signature, expiry, and blacklist checks

---

## 6. Database Schema

### users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### token_blacklist Table
```sql
CREATE TABLE token_blacklist (
  id SERIAL PRIMARY KEY,
  token VARCHAR(500) NOT NULL,
  blacklisted_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_token_blacklist_token ON token_blacklist(token);
CREATE INDEX idx_token_blacklist_expires_at ON token_blacklist(expires_at);
```

### sessions Table
```sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  refresh_token VARCHAR(500) NOT NULL,
  user_agent VARCHAR(500),
  ip_address VARCHAR(45),
  created_at TIMESTAMP DEFAULT NOW(),
  last_activity TIMESTAMP DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_refresh_token ON sessions(refresh_token);
```

---

## 7. Configuration

### Environment Variables (Required)

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-min-32-chars
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-here-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Database (Supabase)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Middleware Configuration

```python
# app/middleware/auth_middleware.py

PUBLIC_ROUTES = [
    "/",
    "/health",
    "/v1/auth/register",
    "/v1/auth/login",
    "/v1/auth/refresh",
    "/docs",
    "/redoc",
    "/openapi.json",
]
```

---

## 8. Troubleshooting

### Common Issues

#### "Invalid or expired token"
**Cause**: Access token expired (15 min TTL)  
**Solution**: Call `/v1/auth/refresh` with refresh token

#### "Refresh token invalid"
**Cause**: Refresh token expired (30 days) or blacklisted  
**Solution**: User must log in again

#### "Token has been revoked"
**Cause**: Token in blacklist (after logout or refresh)  
**Solution**: Use new tokens from latest login/refresh

#### "User not found"
**Cause**: User deleted from database but token still valid  
**Solution**: Token will expire naturally, or force logout

### Debugging Tips

```python
# Check if token is blacklisted
from app.services.auth_service import auth_service

is_blacklisted = await auth_service.is_token_blacklisted(token)
print(f"Token blacklisted: {is_blacklisted}")

# Decode token to inspect claims
import jwt
from app.config import settings

decoded = jwt.decode(
    token, 
    settings.JWT_SECRET_KEY, 
    algorithms=[settings.JWT_ALGORITHM]
)
print(f"User ID: {decoded['sub']}")
print(f"Expires: {decoded['exp']}")
```

### Log Monitoring

```bash
# Check authentication logs
fly logs -a houserenovators-api | grep "AUTH"

# Look for patterns:
# [AUTH] Login successful: user@example.com
# [AUTH] Token refresh successful: user_id=...
# [AUTH] Logout successful: user_id=...
# [AUTH] Invalid token: expired
# [AUTH] Token blacklisted: ...
```

---

## 9. Migration History

### v1.0 → v2.0 (November 2025)

**Changes**:
- Added refresh tokens (previously only access tokens)
- Added token blacklist (previously no revocation)
- Added session management (previously stateless)
- Added token rotation on refresh
- Reduced access token TTL (60 min → 15 min)

**Migration Steps**:
1. Create new database tables (token_blacklist, sessions)
2. Update auth_service.py with new logic
3. Deploy backend with new endpoints
4. Update frontend to handle refresh flow
5. Test token expiry and refresh
6. Monitor for issues

**Rollback**: Keep v1.0 endpoints active during migration for backward compatibility

---

## 10. Related Documentation

- **API Reference**: `guides/API_DOCUMENTATION.md`
- **Troubleshooting**: `guides/TROUBLESHOOTING.md`
- **Deployment**: `deployment/DEPLOYMENT.md`

---

**Last Updated**: December 13, 2025  
**Status**: ✅ Production-Ready  
**Version**: 2.0 (JWT with Refresh Tokens)
