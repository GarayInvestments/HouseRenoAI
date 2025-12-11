# Password Rotation Quick Guide

## ⚠️ CRITICAL: Exposed Credentials

Your Supabase PostgreSQL password was exposed in git history. Follow these steps to secure your database.

---

## 🚨 Step 1: Rotate Password (5 minutes)

1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Go to: Settings → Database → Database Settings
3. Scroll to "Connection string" section
4. Click "Reset database password"
5. Copy the new password

---

## 🔧 Step 2: Update Local Environment (2 minutes)

```powershell
# Open .env and replace DATABASE_URL with new password
# Format: postgresql+asyncpg://postgres:NEW_PASSWORD_HERE@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres

# Re-encrypt secrets
.\scripts\git-secret-wrapper.ps1 -Action hide

# Update pgpass.conf
.\scripts\setup-pgpass.ps1

# Test connection (should work without password prompt)
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres" -c "SELECT 1"
```

---

## 🚀 Step 3: Update Render (3 minutes)

1. Open Render Dashboard: https://dashboard.render.com/
2. Select service: "houserenoai" (srv-d44ak76uk2gs73a3psig)
3. Go to: Environment tab
4. Find: `DATABASE_URL`
5. Click Edit, paste new connection string (with +asyncpg):
   ```
   postgresql+asyncpg://postgres:NEW_PASSWORD_HERE@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres
   ```
6. Save (Render will auto-redeploy)

---

## ✅ Step 4: Verify (2 minutes)

```powershell
# Wait 2-3 minutes for Render deployment
render logs -r srv-d44ak76uk2gs73a3psig --tail --confirm

# Test production API
curl https://houserenoai.onrender.com/v1/clients
```

---

## 📋 Checklist

- [ ] Rotated Supabase password
- [ ] Updated `.env` file
- [ ] Re-encrypted with git-secret
- [ ] Ran `setup-pgpass.ps1`
- [ ] Tested local psql connection
- [ ] Updated Render DATABASE_URL
- [ ] Verified production API works

---

**Total Time:** ~12 minutes

**After completion:** The exposed password in git history is now useless. The old password no longer grants access to your database.

**Optional:** Clean git history using BFG Repo-Cleaner (see SECURITY_INCIDENT_RESPONSE.md for details).

---

**Need help?** Check SECURITY_INCIDENT_RESPONSE.md for detailed instructions.
