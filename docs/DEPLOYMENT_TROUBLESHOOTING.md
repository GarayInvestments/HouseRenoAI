# Deployment Troubleshooting Guide

## Mixed Content Errors (HTTP vs HTTPS)

### Issue: Frontend Using HTTP Instead of HTTPS

**Symptoms:**
```
Mixed Content: The page at 'https://[domain]' was loaded over HTTPS, 
but requested an insecure resource 'http://houserenovators-api.fly.dev/v1/clients/'
```

**Root Causes:**
1. **FastAPI redirects not preserving HTTPS behind proxy** - FastAPI redirects `/v1/clients` → `/v1/clients/` but loses HTTPS scheme (**FIXED**: Added `HTTPSRedirectFixMiddleware`)
2. **Fly.io port mismatch** - App listening on different port than `fly.toml` `internal_port` (**FIXED**: Updated Dockerfile to use port 8000)
3. **Fallback URL in source code** - If `import.meta.env.VITE_API_URL` is undefined, code falls back to hardcoded value
4. **Environment variables not set during build** - Cloudflare Pages needs env vars in dashboard
5. **Browser/CDN caching old bundle** - Even after rebuild, old JavaScript may be cached

**Diagnosis Steps:**

1. **Check Browser Console Logs:**
   ```javascript
   [API Service] Environment: production
   [API Service] API URL: https://houserenovators-api.fly.dev
   [API Request] Full URL: https://houserenovators-api.fly.dev/v1/clients
   ```
   - If logs show `https://` but errors show `http://`, there's a caching issue
   - If logs show `http://`, the environment variable isn't being read

2. **Verify Cloudflare Build Logs:**
   ```
   Build environment variables: 
     - VITE_API_URL: https://houserenovators-api.fly.dev
     - VITE_ENV: production
   ```
   - Look for this in deployment logs at Cloudflare Dashboard → Pages → houserenoai → Deployments

3. **Check Source Code Fallbacks:**
   ```javascript
   // frontend/src/lib/api.js
   const API_URL = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev';
   
   // frontend/src/stores/appStore.js  
   const API_URL = import.meta.env.VITE_API_URL || 'https://api.houserenovatorsllc.com'
   ```
   - Ensure fallback values use `https://`, never `http://`

**Solutions:**

### Solution 1: Set Environment Variables in Cloudflare Dashboard

1. Go to Cloudflare Dashboard → Pages → houserenoai → Settings
2. Scroll to "Environment variables"
3. Under "Production", add:
   - `VITE_API_URL` = `https://houserenovators-api.fly.dev`
   - `VITE_ENV` = `production`
   - `VITE_ENABLE_DEBUG` = `false`

4. Trigger rebuild:
   ```powershell
   git commit --allow-empty -m "Rebuild with env vars"
   git push origin main
   ```

### Solution 2: Update Fallback URLs

If environment variables aren't being read, update fallback values:

```javascript
// frontend/src/lib/api.js
const API_URL = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev';

// frontend/src/stores/appStore.js
const API_URL = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev'
```

**Never use `http://localhost:8000` as fallback in production builds!**

### Solution 3: Clear Browser/CDN Cache

1. **Hard refresh browser:**
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **Clear Cloudflare cache:**
   - Cloudflare Dashboard → Caching → Configuration → Purge Everything

3. **Wait for new deployment:**
   - Each git push creates new bundle with different hash (e.g., `index-BrKpPELy.js`)
   - Old hash = old cached bundle
   - New hash = fresh build

### Solution 4: Check wrangler.toml

Ensure environment variables are also in `wrangler.toml` for local builds:

```toml
[env.production.vars]
VITE_API_URL = "https://houserenovators-api.fly.dev"
VITE_ENV = "production"
VITE_ENABLE_DEBUG = "false"
```

**Note:** These only affect `wrangler deploy` commands, not Cloudflare Git builds.

### Solution 5: Fix FastAPI Redirects Behind Proxy (CRITICAL)

**Problem:** FastAPI automatically redirects URLs without trailing slashes:
- Request: `https://houserenovators-api.fly.dev/v1/clients`
- Redirect: `http://houserenovators-api.fly.dev/v1/clients/` ❌ (HTTP!)

**Root Cause:** FastAPI doesn't know it's behind an HTTPS proxy and generates HTTP redirects.

**Solution:** Add middleware to preserve HTTPS scheme:

```python
# app/main.py
from starlette.middleware.base import BaseHTTPMiddleware

class HTTPSRedirectFixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # If request came via HTTPS proxy (Fly.io), ensure redirects use HTTPS
        if request.headers.get("x-forwarded-proto") == "https":
            request.scope["scheme"] = "https"
        response = await call_next(request)
        return response

app.add_middleware(HTTPSRedirectFixMiddleware)
```

**Verification:**
```powershell
curl -I https://houserenovators-api.fly.dev/v1/clients
# Should show: location: https://... (not http://...)
```

**Status:** ✅ Fixed in commit d700d5d

### Solution 6: Fix Port Mismatch (CRITICAL)

**Problem:** Fly.io proxy couldn't connect to the app.

**Symptoms:**
```
error.message="instance refused connection. is your app listening on 0.0.0.0:8000?"
```

**Root Cause:** Mismatch between:
- `fly.toml`: `internal_port = 8000`
- `Dockerfile`: `CMD ["uvicorn", "app.main:app", "--port", "10000"]`

**Solution:** Update all three port references in Dockerfile:

```dockerfile
# EXPOSE port
EXPOSE 8000  # Changed from 10000

# HEALTHCHECK
CMD curl -f http://localhost:8000/health || exit 1  # Changed from 10000

# Run command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]  # Changed from 10000
```

**Verification:**
```powershell
flyctl logs -a houserenovators-api -n | Select-String "Uvicorn running"
# Should show: Uvicorn running on http://0.0.0.0:8000
```

**Status:** ✅ Fixed in commits cf795e6 and 81251bc

---

## CORS Errors

### Issue: Backend Rejecting Frontend Origin

**Symptoms:**
```
Access to fetch at 'https://houserenovators-api.fly.dev/v1/auth/login' 
from origin 'https://[random].houserenoai.pages.dev' has been blocked by CORS policy
```

**Root Cause:** Backend CORS configuration doesn't include the frontend domain.

**Solution:**

Update `app/main.py` CORS configuration:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.(house-renovators-ai-portal|houserenoai)\.pages\.dev",
    allow_origins=[
        "https://portal.houserenovatorsllc.com",
        "https://houserenoai.pages.dev",  # Main domain
        # Add any other custom domains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

**The regex pattern allows all preview URLs:** `https://[hash].houserenoai.pages.dev`

---

## Fly.io Machines Stopped

### Issue: API Requests Failing Because Backend is Down

**Symptoms:**
- API returns 503 Service Unavailable
- Requests hang for 30+ seconds before failing
- Fly.io status shows machines stopped

**Diagnosis:**
```powershell
flyctl status -a houserenovators-api
```

Output shows:
```
Machines
PROCESS ID              STATE   
app     83dde4c79e1478  stopped
app     e825544a1d2368  stopped
```

**Root Cause:** 
Auto-stop configuration (`min_machines_running = 0` in `fly.toml`)

**Additional Check - Connection Issues:**
If machines show "started" but still failing:
```powershell
flyctl logs -a houserenovators-api -n | Select-String "refused connection"
```

If you see `"instance refused connection. is your app listening on 0.0.0.0:8000?"`, this is a **port mismatch issue** (see Solution 6 above).

**Solutions:**

### Option 1: Manually Start Machines (Temporary)
```powershell
flyctl machine start 83dde4c79e1478 -a houserenovators-api
flyctl machine start e825544a1d2368 -a houserenovators-api
```

**Trade-off:** Machines will auto-stop again after 10-15 minutes of inactivity.

### Option 2: Keep One Machine Always Running (Recommended for Production)

Edit `fly.toml`:
```toml
[http_service]
  auto_stop_machines = 'stop'
  auto_start_machines = true
  min_machines_running = 1  # Changed from 0
```

Deploy changes:
```powershell
flyctl deploy
```

**Cost Impact:** ~$5/month for one always-on machine.

### Option 3: Accept Cold Start Delay (Current Setup)

Leave `min_machines_running = 0`:
- **Pros:** Saves money (~$5-9/month)
- **Cons:** First request after idle has 2-3 second cold start

---

## Environment Variable Not Found During Build

### Issue: Build Logs Show Empty/Missing Variables

**Symptoms:**
Cloudflare build logs show:
```
Build environment variables: 
  (empty or missing VITE_API_URL)
```

**Root Cause:** Variables not set in Cloudflare dashboard.

**Solution:**

1. **Verify in Cloudflare Dashboard:**
   - Pages → houserenoai → Settings → Environment variables
   - Check "Production" tab (not Preview)
   - Variables must be "Plaintext" type, not "Secret"

2. **Re-save variables:**
   - Click "Edit" on each variable
   - Re-enter value
   - Click "Save"

3. **Trigger new deployment:**
   ```powershell
   git commit --allow-empty -m "Trigger rebuild"
   git push origin main
   ```

---

## Custom Domain Not Updating

### Issue: Custom Domain Shows Old Deployment

**Symptoms:**
- `portal.houserenovatorsllc.com` shows old version
- Preview URLs (`https://[hash].houserenoai.pages.dev`) work correctly

**Root Cause:** DNS/CDN propagation delay.

**Timeline:**
- **Preview URLs:** Immediate (Cloudflare edge)
- **Custom domains:** 5-30 minutes (DNS + CDN cache)

**Solutions:**

1. **Wait for propagation** (preferred)
2. **Purge Cloudflare cache:**
   - Cloudflare Dashboard → Caching → Purge Everything
3. **Verify DNS:**
   ```powershell
   nslookup portal.houserenovatorsllc.com
   ```

---

## Vite Build Warnings

### Issue: Chunk Size Warning

**Symptoms:**
```
(!) Some chunks are larger than 500 kB after minification.
dist/assets/index-BNSO0yqS.js   532.99 kB │ gzip: 139.05 kB
```

**Impact:** 
- Slower initial page load
- Not critical but should be optimized

**Solution (Future):**

Implement code splitting in `vite.config.js`:

```javascript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'router': ['zustand'],
          'icons': ['lucide-react'],
        }
      }
    }
  }
})
```

---

## Debugging Checklist

When deployment issues occur:

### Quick Checks
- [ ] Check Cloudflare build logs for environment variables
- [ ] Verify browser console shows correct API URL
- [ ] Check bundle hash changed (new deployment = new hash)
- [ ] Hard refresh browser (`Ctrl + Shift + R`)
- [ ] Test with deployment preview URL (not custom domain)

### Backend Health
- [ ] Verify Fly.io machines running: `flyctl status -a houserenovators-api`
- [ ] Check backend accessible: `curl https://houserenovators-api.fly.dev/health`
- [ ] Test HTTPS redirects: `curl -I https://houserenovators-api.fly.dev/v1/clients`
  - Should redirect to `https://...` not `http://...`
- [ ] Verify port: `flyctl logs -a houserenovators-api -n | Select-String "Uvicorn running"`
  - Should show port 8000

### Network Analysis
- [ ] Check browser Network tab for actual request URL
- [ ] Look for "Mixed Content" errors in console
- [ ] Verify Authorization header is being sent
- [ ] Review CORS configuration in `app/main.py`

### Deep Debugging
- [ ] Check if redirect preserves HTTPS:
  ```powershell
  curl -I https://houserenovators-api.fly.dev/v1/clients
  # location: header should be https://...
  ```
- [ ] Test with trailing slash:
  ```powershell
  curl https://houserenovators-api.fly.dev/v1/clients/
  # Should return data, not redirect
  ```
- [ ] Check Fly.io logs for connection errors:
  ```powershell
  flyctl logs -a houserenovators-api -n | Select-String "error|refused"
  ```

---

## Common Patterns

### Testing After Deployment

```powershell
# 1. Check backend health
curl https://houserenovators-api.fly.dev/health

# 2. Test CORS
curl -X OPTIONS https://houserenovators-api.fly.dev/v1/auth/login `
  -H "Origin: https://houserenoai.pages.dev" `
  -H "Access-Control-Request-Method: POST" -I

# 3. Verify Fly.io machines
flyctl status -a houserenovators-api

# 4. Check HTTPS redirects work correctly
curl -I https://houserenovators-api.fly.dev/v1/clients
# location: header MUST be https://, not http://

# 5. Check recent deployments
# Cloudflare Dashboard → Pages → houserenoai → Deployments
```

### Critical Configuration Files

**fly.toml:**
```toml
[http_service]
  internal_port = 8000  # MUST match Dockerfile port
  force_https = true
```

**Dockerfile:**
```dockerfile
EXPOSE 8000  # MUST match fly.toml internal_port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**app/main.py:**
```python
# MUST include HTTPSRedirectFixMiddleware for proxy support
app.add_middleware(HTTPSRedirectFixMiddleware)
```

### Lessons Learned

1. **Always check the redirect location header**, not just the final response
2. **Port mismatches cause "instance refused connection" errors**
3. **FastAPI needs middleware to handle HTTPS behind proxies**
4. **Browser console logs can be misleading** - they show constructed URLs, not actual network requests
5. **Test with trailing slashes** - FastAPI redirects can expose protocol issues

### Force Complete Rebuild

```powershell
# 1. Clear local git cache
git commit --allow-empty -m "Force rebuild"

# 2. Push to trigger both deployments
git push origin main

# 3. Monitor builds
# Backend: GitHub Actions → fly-deploy.yml
# Frontend: Cloudflare Dashboard → Deployments

# 4. Wait 2-3 minutes for completion

# 5. Test with new preview URL (find in Cloudflare Deployments)
```

---

## Contact & Support

**Internal Documentation:**
- Setup: `docs/setup/SETUP_GUIDE.md`
- API: `docs/guides/API_DOCUMENTATION.md`
- Deployment: `docs/deployment/DEPLOYMENT.md`

**Service Dashboards:**
- Fly.io: https://fly.io/dashboard
- Cloudflare: https://dash.cloudflare.com/
- GitHub Actions: https://github.com/GarayInvestments/HouseRenoAI/actions

**Emergency Commands:**
```powershell
# Restart everything
flyctl machine restart -a houserenovators-api
git commit --allow-empty -m "Emergency rebuild" && git push

# Check all services
flyctl status -a houserenovators-api
# Then check Cloudflare Dashboard for frontend status
```
