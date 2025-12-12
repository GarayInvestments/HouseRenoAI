# Authentication Quick Reference

## 🚀 Quick Start (Local Development)

### 1. Run Database Migration
```bash
alembic upgrade head
```

### 2. Generate JWT Secret
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Add to `.env`
```ini
JWT_SECRET=your-generated-secret-here
```

### 4. Test Login
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

---

## 📋 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v1/auth/login` | Login with email/password | No |
| POST | `/v1/auth/register` | Register new user | No |
| POST | `/v1/auth/refresh` | Refresh access token | No (needs refresh_token) |
| POST | `/v1/auth/logout` | Logout current session | Yes |
| POST | `/v1/auth/logout-all` | Logout all devices | Yes |
| GET | `/v1/auth/me` | Get current user info | Yes |
| GET | `/v1/auth/sessions` | List active sessions | Yes |
| DELETE | `/v1/auth/sessions/{id}` | Revoke specific session | Yes |

---

## 🔑 Token Lifetimes

| Token Type | Lifetime | Storage | Rotation |
|------------|----------|---------|----------|
| **Access Token** | 15 minutes | Client (memory/localStorage) | No - expires naturally |
| **Refresh Token** | 30 days | Database (hashed) + Client | Yes - rotates on use |

---

## 💻 Frontend Code Examples

### Login
```javascript
const response = await fetch('/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password, device_name: 'Chrome on Windows' })
});

const data = await response.json();
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
```

### Use Access Token
```javascript
const response = await fetch('/v1/clients', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
});
```

### Refresh Access Token
```javascript
const response = await fetch('/v1/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    refresh_token: localStorage.getItem('refresh_token') 
  })
});

const data = await response.json();
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token); // New refresh token!
```

### Auto-Refresh on 401 (Axios)
```javascript
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      const response = await fetch('/v1/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      error.config.headers['Authorization'] = `Bearer ${data.access_token}`;
      return axios(error.config);
    }
    
    return Promise.reject(error);
  }
);
```

---

## 🛡️ Security Features

### Rate Limiting
- **Login**: 5 attempts per 15 minutes per email
- **After 5 failures**: Account locked for 15 minutes
- **Tracked by**: Email + IP address

### Token Rotation
- Every refresh creates **new** access token + **new** refresh token
- Old refresh token marked as "used" (cannot be reused)
- If used token presented → **entire token family revoked** (theft detected)

### Token Blacklist
- Access tokens can be revoked before natural expiration
- Use cases: Logout, password reset, security breach
- Performance: O(1) lookup (indexed by JTI)

### Session Management
- Tracks all active sessions per user
- Shows device name, IP, location, last activity
- Users can revoke specific sessions remotely

---

## 🔍 Debugging

### Check Token Validity
```python
from app.services.auth_service_v2 import get_token_service

token_service = get_token_service()
payload = token_service.verify_access_token(your_token)
print(payload)  # None if invalid/expired
```

### Check if Token is Blacklisted
```sql
SELECT * FROM token_blacklist WHERE jti = 'your-jti-claim';
```

### Check Active Refresh Tokens
```sql
SELECT * FROM refresh_tokens 
WHERE user_id = 'user-uuid' 
AND is_revoked = false 
AND is_used = false;
```

### Check Login Attempts
```sql
SELECT * FROM login_attempts 
WHERE email = 'test@example.com' 
ORDER BY attempted_at DESC 
LIMIT 10;
```

### Check Active Sessions
```sql
SELECT * FROM user_sessions 
WHERE user_id = 'user-uuid' 
AND is_active = true;
```

---

## ⚠️ Common Errors

### `401 Unauthorized - Invalid or expired token`
**Cause**: Access token expired (15 minutes)  
**Solution**: Use refresh token to get new access token

### `401 Unauthorized - Token has been revoked`
**Cause**: User logged out or password reset  
**Solution**: Re-authenticate with login endpoint

### `429 Too Many Requests`
**Cause**: Exceeded rate limit (5 login attempts)  
**Solution**: Wait 15 minutes or contact admin

### `401 Unauthorized - Token reuse detected`
**Cause**: Attempted to use old refresh token after it was rotated  
**Solution**: Security measure - must re-authenticate

---

## 📊 Monitoring

### Check System Health
```bash
# Active users (last 24 hours)
psql "..." -c "
SELECT COUNT(DISTINCT user_id) as active_users 
FROM user_sessions 
WHERE last_activity_at > NOW() - INTERVAL '24 hours';
"

# Failed login attempts (last hour)
psql "..." -c "
SELECT COUNT(*) as failed_attempts 
FROM login_attempts 
WHERE success = false 
AND attempted_at > NOW() - INTERVAL '1 hour';
"

# Active refresh tokens
psql "..." -c "
SELECT COUNT(*) as active_tokens 
FROM refresh_tokens 
WHERE is_revoked = false 
AND is_used = false 
AND expires_at > NOW();
"
```

---

## 🎯 Migration Checklist

### Pre-Migration
- [x] Review migration guide
- [ ] Generate JWT_SECRET
- [ ] Add to environment (.env + Fly.io)
- [ ] Backup database

### Database
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify tables: `\dt *auth*`
- [ ] Check indexes: See migration guide

### Code
- [ ] Update main.py (auth_v2 routes)
- [ ] Update middleware (auth_middleware_v2)
- [ ] Import auth models in models.py

### Frontend
- [ ] Update token storage (both tokens)
- [ ] Implement auto-refresh
- [ ] Update login/logout
- [ ] Test complete flow

### Testing
- [ ] Login flow
- [ ] Token refresh
- [ ] Logout
- [ ] Rate limiting
- [ ] Session management

### Deployment
- [ ] Deploy backend
- [ ] Monitor logs
- [ ] Test production auth
- [ ] Deploy frontend

---

## 📚 Documentation

- **Complete Guide**: `docs/guides/AUTH_MIGRATION_GUIDE.md`
- **System Summary**: `docs/guides/AUTH_SYSTEM_SUMMARY.md`
- **This Reference**: `docs/guides/AUTH_QUICK_REFERENCE.md`

---

## 🔗 Useful Links

- **Models**: `app/db/models_auth.py`
- **Service**: `app/services/auth_service_v2.py`
- **Routes**: `app/routes/auth_v2.py`
- **Middleware**: `app/middleware/auth_middleware_v2.py`
- **Migration**: `alembic/versions/20251211_1630_add_auth_tables.py`
