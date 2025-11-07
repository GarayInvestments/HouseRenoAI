# Securing House Renovators Portal

**URGENT**: App is currently publicly accessible

---

## 🚨 IMMEDIATE: Lock Down with Cloudflare Access (10 minutes)

### Step 1: Enable Cloudflare Access

1. Go to: https://dash.cloudflare.com/
2. Select your account
3. Click **Zero Trust** in left sidebar
4. Go to **Access** → **Applications**
5. Click **Add an application**

### Step 2: Configure Application

**Application Details**:
```
Name: House Renovators Portal
Subdomain: portal
Domain: houserenovatorsllc.com
```

**Result**: https://portal.houserenovatorsllc.com

### Step 3: Set Access Policy

**Policy Name**: Authorized Users Only

**Policy Type**: Allow

**Include Rules**:
```
Selector: Emails
Value: your-email@example.com (add all authorized users)
```

**Or use:**
```
Selector: Email domain
Value: houserenovatorsllc.com (allow anyone @houserenovatorsllc.com)
```

### Step 4: Exception for Legal Pages

**Important**: Keep /privacy and /terms public for QuickBooks!

**Add Bypass Policy**:
```
Name: Public Legal Pages
Action: Bypass
Include:
  - Path: /privacy
  - Path: /terms
```

### Step 5: Save and Test

1. Click **Save application**
2. Visit: https://portal.houserenovatorsllc.com
3. Should see Cloudflare Access login screen
4. Enter authorized email
5. Verify /privacy and /terms still work without login

---

## 🔐 PERMANENT: Add Built-in Authentication (30-60 minutes)

### Option A: Simple Email/Password Auth

**Pros**:
- Full control
- No third-party dependencies
- Quick to implement

**Cons**:
- Need to manage passwords
- Less secure than OAuth

### Implementation:

1. **Backend**: Add `/v1/auth/login` and `/v1/auth/register` endpoints
2. **Frontend**: Create Login page component
3. **Store**: Save auth token in localStorage
4. **Protect**: Check token on all API calls
5. **Routes**: Redirect to login if not authenticated

### Option B: OAuth (Google/Microsoft)

**Pros**:
- More secure
- Professional
- No password management

**Cons**:
- More complex setup
- Requires OAuth provider setup

---

## 🎯 RECOMMENDED APPROACH

### Phase 1: NOW (10 minutes)
✅ Enable Cloudflare Access
✅ Whitelist your email(s)
✅ Bypass /privacy and /terms
✅ Test access

### Phase 2: LATER (when ready)
⏳ Build proper auth UI
⏳ Add user management
⏳ Disable Cloudflare Access
⏳ Use built-in auth

---

## 📋 Quick Decision Matrix

| Option | Time | Security | Control | Cost |
|--------|------|----------|---------|------|
| **Cloudflare Access** | 10 min | High | Medium | Free (up to 50 users) |
| **Email/Password Auth** | 30-60 min | Medium | High | Free |
| **OAuth (Google)** | 1-2 hours | High | Medium | Free |

---

## 🚀 Let's Lock It Down NOW

Want me to:
1. **Walk you through Cloudflare Access setup** (10 min - safest)
2. **Build email/password auth** (30 min - more work but own it)
3. **Both** (Cloudflare now, then build auth later)

**What do you prefer?**
