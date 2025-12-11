# Supabase Auth Setup Guide

## Overview

The HouseRenovators API now uses **Supabase Auth** for authentication instead of custom JWT + Google Sheets. This provides:

- ✅ Enterprise-grade authentication (email/password, OAuth, MFA)
- ✅ Automatic password hashing and email verification
- ✅ JWT token management with automatic refresh
- ✅ Role-based access control (RBAC) in app layer
- ✅ Scalable user management

## Architecture

### **Auth Flow**:
1. Frontend uses `@supabase/supabase-js` to handle login/signup
2. Supabase Auth issues JWT access tokens
3. Frontend sends token in `Authorization: Bearer <token>` header
4. Backend verifies JWT and maps to app user table
5. App user table stores roles, permissions, preferences

### **Two User Tables**:
- **`auth.users`** (Supabase managed): Email, password hash, verification status
- **`public.users`** (App managed): Roles, permissions, app metadata, activity tracking

## Required Environment Variables

Add these to `.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://dtfjzjhxtojkgfofrmrr.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
SUPABASE_JWT_SECRET=<your-jwt-secret>

# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRE_HOURS=24
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
```

### How to Get Supabase Keys:

1. Go to **Supabase Dashboard** → https://supabase.com/dashboard
2. Select your project: `HouseRenovators`
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_ANON_KEY`
   - **service_role key** → `SUPABASE_SERVICE_ROLE_KEY`
5. Go to **Settings** → **API** → **JWT Settings**
6. Copy **JWT Secret** → `SUPABASE_JWT_SECRET`

## Database Migration

The users table has been recreated with Supabase Auth integration:

```sql
-- Already applied via scripts/migrate_users_supabase.sql

CREATE TABLE users (
    id UUID PRIMARY KEY,
    supabase_user_id UUID UNIQUE NOT NULL,  -- Links to auth.users.id
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    role VARCHAR(50) DEFAULT 'client',      -- admin, pm, inspector, client, finance
    is_active BOOLEAN DEFAULT true,
    is_email_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    app_metadata JSONB,                      -- Permissions, preferences, settings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Backend Integration

### **New Services**:
- `app/services/supabase_auth_service.py` - JWT verification, user management
- `app/middleware/supabase_auth_middleware.py` - Automatic JWT verification on all protected routes
- `app/routes/auth_supabase.py` - `/v1/auth/me`, `/v1/auth/users/{id}/role` endpoints

### **Usage in Routes**:

```python
from app.routes.auth_supabase import get_current_user, get_current_admin_user
from app.db.models import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    # current_user is User model with id, email, role, app_metadata, etc.
    return {"message": f"Hello {current_user.full_name}"}

@router.post("/admin-only")
async def admin_route(current_user: User = Depends(get_current_admin_user)):
    # Only users with role='admin' can access this
    return {"message": "Admin access granted"}
```

## Frontend Integration

### 1. Install Supabase Client

```bash
npm install @supabase/supabase-js
```

### 2. Initialize Supabase Client

```javascript
// src/lib/supabase.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### 3. Sign Up

```javascript
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password123',
  options: {
    data: {
      full_name: 'John Doe'  // Stored in auth.users.raw_user_meta_data
    }
  }
})

if (error) {
  console.error('Signup error:', error.message)
} else {
  console.log('User created:', data.user)
  // Supabase sends verification email automatically
}
```

### 4. Sign In

```javascript
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password123'
})

if (error) {
  console.error('Login error:', error.message)
} else {
  const accessToken = data.session.access_token
  localStorage.setItem('supabase_token', accessToken)
  
  // Call backend /v1/auth/me to get app user (role, permissions)
  const response = await fetch('https://api.example.com/v1/auth/me', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  })
  const appUser = await response.json()
  console.log('App user:', appUser)  // { id, email, role, app_metadata, ... }
}
```

### 5. Get Current Session

```javascript
const { data: { session } } = await supabase.auth.getSession()

if (session) {
  const accessToken = session.access_token
  // Use token for API requests
} else {
  // User not logged in
  window.location.href = '/login'
}
```

### 6. Sign Out

```javascript
const { error } = await supabase.auth.signOut()
localStorage.removeItem('supabase_token')
window.location.href = '/login'
```

### 7. Auto Token Refresh

Supabase automatically refreshes tokens when they expire:

```javascript
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'TOKEN_REFRESHED') {
    const newToken = session.access_token
    localStorage.setItem('supabase_token', newToken)
  }
  
  if (event === 'SIGNED_OUT') {
    localStorage.removeItem('supabase_token')
  }
})
```

## API Endpoints

### **Public Endpoints** (no auth required):
- `GET /health` - Health check
- `GET /v1/auth/health` - Auth service health

### **User Endpoints** (authenticated):
- `GET /v1/auth/me` - Get current user info (role, permissions)
- `PUT /v1/auth/me/metadata` - Update user preferences/settings

### **Admin Endpoints** (admin role required):
- `GET /v1/auth/users/{user_id}` - Get user by ID
- `PUT /v1/auth/users/{user_id}/role` - Update user role
- `DELETE /v1/auth/users/{user_id}` - Deactivate user (soft delete)

## User Roles

Valid roles in `public.users.role`:
- **`admin`** - Full system access, can manage users
- **`pm`** - Project manager, can create/edit projects, permits, inspections
- **`inspector`** - Can complete inspections, upload photos
- **`client`** - Read-only access to their own projects
- **`finance`** - Can manage invoices and payments

## Testing Auth

### 1. Create Test User via Supabase Dashboard

1. Go to **Supabase Dashboard** → **Authentication** → **Users**
2. Click **Add User**
3. Enter email and password
4. User will be created in `auth.users`
5. Backend will auto-create app user in `public.users` on first login

### 2. Test API with cURL

```bash
# 1. Sign in via Supabase (use Supabase client SDK or API)
# Get access token

# 2. Test /v1/auth/me
curl -H "Authorization: Bearer <access_token>" \
  https://api.example.com/v1/auth/me

# 3. Test protected endpoint
curl -H "Authorization: Bearer <access_token>" \
  https://api.example.com/v1/projects
```

### 3. Update User Role (Admin Only)

```bash
# First, manually update a user to admin role in database:
psql "postgresql://..." -c "UPDATE users SET role='admin' WHERE email='admin@example.com'"

# Then use that admin user to update other users:
curl -X PUT \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "uuid-here", "role": "pm"}' \
  https://api.example.com/v1/auth/users/uuid-here/role
```

## Migration from Old Auth System

### Export Existing Users from Google Sheets

```python
# scripts/export_users_from_sheets.py
import asyncio
from app.services import google_service_module

async def export_users():
    google_service = google_service_module.google_service
    users = await google_service.get_sheet_data("Users")
    
    print(f"Found {len(users)} users to migrate:")
    for user in users:
        print(f"- {user.get('Email')} ({user.get('Role')})")

asyncio.run(export_users())
```

### Create Users in Supabase

Option 1: **Via Supabase Dashboard** (for small number of users)
- Manually add each user via Authentication → Users

Option 2: **Via Admin API** (for bulk migration)
```python
# Requires SUPABASE_SERVICE_ROLE_KEY
from supabase import create_client

admin_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

for user in sheet_users:
    # Create auth user
    auth_response = admin_supabase.auth.admin.create_user({
        "email": user["Email"],
        "password": "ChangeMe123!",  # Force password reset on first login
        "email_confirm": True,
        "user_metadata": {
            "full_name": user.get("Name", "")
        }
    })
    
    # App user will be auto-created on first login
    # Or manually insert if needed
```

## Troubleshooting

### "Invalid or expired token"
- Token has expired (access tokens expire after 1 hour)
- Solution: Frontend should refresh token using `supabase.auth.refreshSession()`

### "User account is deactivated"
- User's `is_active` flag is false in `public.users`
- Solution: Admin updates via `PUT /v1/auth/users/{id}/role` or direct SQL

### "Admin access required"
- User's role is not 'admin'
- Solution: Update role in database (only admins can update via API)

### JWT verification fails
- Missing or incorrect `SUPABASE_JWT_SECRET`
- Solution: Copy exact JWT secret from Supabase Dashboard → Settings → API

### User not created in `public.users`
- Auto-sync trigger not working
- Solution: User will be created on first API request automatically via middleware

## Security Best Practices

1. ✅ **Never expose `SUPABASE_SERVICE_ROLE_KEY`** to frontend
2. ✅ Use `SUPABASE_ANON_KEY` in frontend only
3. ✅ Always verify JWTs on backend (don't trust frontend)
4. ✅ Use HTTPS for all API requests
5. ✅ Implement rate limiting on auth endpoints
6. ✅ Log all role changes for audit trail
7. ✅ Use Row Level Security (RLS) in Supabase for database access

## Next Steps

1. ✅ Add Supabase env vars to `.env`
2. ✅ Update frontend to use Supabase Auth
3. ✅ Migrate existing users from Google Sheets
4. ✅ Set up admin user(s) in database
5. ✅ Test auth flow end-to-end
6. ✅ Remove old auth system (Google Sheets Users tab)
7. ✅ Deploy and monitor

## References

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Supabase JS Client](https://supabase.com/docs/reference/javascript/auth-api)
- [JWT Best Practices](https://supabase.com/docs/guides/auth/jwts)
- [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
