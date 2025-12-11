# Fly.io Deployment Guide

**Created**: December 11, 2025  
**Purpose**: Complete guide to deploying House Renovators API on Fly.io  
**App Name**: `houserenovators-api`  
**Region**: `ord` (Chicago)

---

## 🚀 Overview

Fly.io is a platform for running full-stack apps globally. The House Renovators backend deploys to Fly.io with:
- **Auto-deploy**: Push to `main` → automatic deployment
- **2 Machines**: 256MB RAM each for redundancy
- **Health checks**: `/v1/auth/supabase/health` endpoint
- **Secrets management**: `fly secrets` command
- **Zero-downtime deploys**: Rolling updates

---

## 📋 Prerequisites

### 1. Install Fly CLI

**Windows (PowerShell)**:
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**macOS/Linux**:
```bash
curl -L https://fly.io/install.sh | sh
```

**Verify Installation**:
```bash
fly version
# Expected: flyctl v0.x.x (or later)
```

### 2. Authenticate

```bash
fly auth login
# Opens browser for authentication
```

### 3. Clone Repository

```bash
git clone https://github.com/yourusername/HouseRenovators-api.git
cd HouseRenovators-api
```

---

## 🏗️ Initial Setup (One-Time)

### 1. Create Fly App

```bash
fly launch
# Follow prompts:
# - App name: houserenovators-api
# - Region: ord (Chicago) or nearest
# - PostgreSQL: No (using Supabase)
# - Deploy now: No (set secrets first)
```

This creates `fly.toml` configuration file.

### 2. Configure `fly.toml`

**Current Configuration** (already in repository):
```toml
# fly.toml
app = "houserenovators-api"
primary_region = "ord"

[build]

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 2
  processes = ["app"]

  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/v1/auth/supabase/health"

[[vm]]
  memory = "256mb"
  cpu_kind = "shared"
  cpus = 1
```

### 3. Set Secrets

**Required Secrets**:
```bash
# Database (Supabase PostgreSQL)
fly secrets set DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres"

# Supabase Auth
fly secrets set SUPABASE_URL="https://dtfjzjhxtojkgfofrmrr.supabase.co"
fly secrets set SUPABASE_ANON_KEY="[YOUR_SUPABASE_ANON_KEY]"
fly secrets set SUPABASE_JWT_SECRET="[YOUR_SUPABASE_JWT_SECRET]"

# OpenAI API
fly secrets set OPENAI_API_KEY="sk-proj-[YOUR_KEY]"

# Google Sheets (legacy - QB tokens only)
fly secrets set SHEET_ID="[YOUR_SHEET_ID]"
fly secrets set GOOGLE_SERVICE_ACCOUNT_BASE64="[BASE64_ENCODED_JSON]"

# QuickBooks OAuth (if using production)
fly secrets set QB_CLIENT_ID="[YOUR_CLIENT_ID]"
fly secrets set QB_CLIENT_SECRET="[YOUR_CLIENT_SECRET]"
fly secrets set QB_REDIRECT_URI="https://houserenovators-api.fly.dev/v1/quickbooks/callback"
fly secrets set QB_ENVIRONMENT="production"  # or "sandbox"

# Application settings
fly secrets set DEBUG="false"
fly secrets set PORT="8000"
```

**View Secrets** (names only, not values):
```bash
fly secrets list
```

**Remove a Secret**:
```bash
fly secrets unset SECRET_NAME
```

---

## 🚀 Deployment Workflows

### Deploy from Local Machine

```bash
# Deploy current directory
fly deploy

# Deploy specific branch
git checkout main
fly deploy

# Deploy with build logs
fly deploy --verbose
```

### Auto-Deploy from GitHub (Recommended)

**Setup** (already configured):
1. GitHub Actions workflow in `.github/workflows/fly-deploy.yml`
2. Fly API token stored in GitHub Secrets (`FLY_API_TOKEN`)
3. Push to `main` → automatic deploy

**Workflow**:
```yaml
# .github/workflows/fly-deploy.yml
name: Fly.io Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

**Generate API Token**:
```bash
fly tokens create deploy -x 999999h
# Save token in GitHub repo → Settings → Secrets → Actions → FLY_API_TOKEN
```

---

## 📊 Monitoring & Logs

### View Logs

**Live tail** (real-time logs):
```bash
fly logs
```

**Last 200 lines**:
```bash
fly logs --limit 200
```

**Search for errors**:
```bash
fly logs | Select-String -Pattern "ERROR|CRITICAL|Exception"
```

**Filter by machine**:
```bash
fly logs --instance [MACHINE_ID]
```

### Machine Status

**List all machines**:
```bash
fly machines list
```

**Output**:
```
ID              NAME    STATE   REGION  HEALTH  LAST UPDATED
1234567890abcd  app-1   started ord     passing 2025-12-11T22:00:00Z
abcdef123456    app-2   started ord     passing 2025-12-11T22:00:00Z
```

**Machine details**:
```bash
fly machines show [MACHINE_ID]
```

### App Status

**Overall status**:
```bash
fly status
```

**Health checks**:
```bash
fly checks list
```

**Resource usage**:
```bash
fly vm status
```

---

## 🔧 Scaling

### Horizontal Scaling (More Machines)

**Scale to 3 machines**:
```bash
fly scale count 3
```

**Scale to 1 machine** (not recommended for production):
```bash
fly scale count 1
```

**Current**: 2 machines for redundancy

### Vertical Scaling (More Resources)

**Increase memory**:
```bash
fly scale memory 512  # MB
```

**Current**: 256MB RAM per machine

**Note**: Fly.io charges based on memory allocation. 256MB is sufficient for current load.

---

## 🛠️ Troubleshooting

### Deployment Fails

**Check build logs**:
```bash
fly deploy --verbose
```

**Common issues**:
1. **Missing secrets**: Ensure all required secrets are set (`fly secrets list`)
2. **Port mismatch**: `fly.toml` internal_port must match app's PORT
3. **Health check failure**: Verify `/v1/auth/supabase/health` endpoint works locally

### App Won't Start

**Check machine logs**:
```bash
fly logs --limit 500
```

**SSH into machine**:
```bash
fly ssh console
# Inside machine:
ps aux  # Check running processes
curl localhost:8000/v1/auth/supabase/health  # Test endpoint
```

### Machines Stuck in "Stopping" State

**Force restart**:
```bash
fly machines restart [MACHINE_ID]
```

**Destroy and recreate**:
```bash
fly machines destroy [MACHINE_ID] --force
fly deploy  # Creates new machine
```

### Database Connection Issues

**Verify DATABASE_URL**:
```bash
fly ssh console
echo $DATABASE_URL  # Should show PostgreSQL connection string
```

**Test connection**:
```python
# Inside SSH console
python3 -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://...'))"
```

---

## 🔐 Security

### Secrets Rotation

**Update a secret**:
```bash
fly secrets set DATABASE_URL="new_connection_string"
# Triggers automatic redeployment
```

**Rotate all secrets** (recommended quarterly):
1. Generate new credentials (Supabase, OpenAI, etc.)
2. Update secrets via `fly secrets set`
3. Verify app restarts successfully
4. Deactivate old credentials

### Network Security

**Fly.io provides**:
- ✅ Automatic HTTPS (TLS 1.3)
- ✅ DDoS protection
- ✅ WAF (Web Application Firewall)
- ✅ Private networking between machines

**Additional security** (already implemented):
- JWT authentication on all routes
- CORS restrictions in `app/config.py`
- Rate limiting (planned)

---

## 📦 Backup & Recovery

### Database Backups

**Supabase handles backups**:
- Daily automated backups (7-day retention)
- Point-in-time recovery available
- Manual backups via Supabase dashboard

**No Fly.io-specific backup needed** (database is external).

### App State Recovery

**Rollback to previous deployment**:
```bash
fly releases list  # View all releases
fly releases rollback [RELEASE_VERSION]
```

**Redeploy from specific commit**:
```bash
git checkout [COMMIT_HASH]
fly deploy
git checkout main  # Return to main
```

---

## 🌐 Custom Domains

### Current Setup

**Fly.io provides**:
- `houserenovators-api.fly.dev` (automatic)

**Custom domain** (if needed):
```bash
fly certs create houserenovators.com
fly certs show houserenovators.com
# Add DNS records as instructed
```

**DNS Configuration**:
```
Type: CNAME
Name: api
Value: houserenovators-api.fly.dev
TTL: 3600
```

---

## 📊 Performance Optimization

### Current Configuration

- **Min machines**: 2 (always running)
- **Auto-stop**: Disabled (no cold starts)
- **Auto-start**: Enabled (recovery from failures)
- **Health checks**: Every 30s
- **Memory**: 256MB (sufficient for current load)

### Monitoring Recommendations

1. **Set up alerts** (via Fly.io dashboard):
   - Health check failures
   - High memory usage (>200MB sustained)
   - Response time >1s

2. **Monitor logs** for:
   - `[METRICS]` entries (performance data)
   - Error patterns
   - Database query times

3. **Review monthly** (in Fly.io dashboard):
   - Request volume trends
   - Resource usage patterns
   - Error rates

---

## 💰 Cost Management

### Current Usage

- **2 machines** × 256MB = 512MB total
- **Estimated cost**: ~$3-5/month (Fly.io pricing)
- **Database**: Covered by Supabase free tier

### Cost Optimization

**Free tier strategy**:
- Use shared CPU (not dedicated)
- Keep memory at 256MB unless needed
- Only scale up during high load

**Monitor usage**:
```bash
fly dashboard  # Opens web dashboard
# Navigate to Usage tab
```

---

## 🔗 Related Documentation

- **Deployment Status**: `docs/CURRENT_STATUS.md` - Current deployment state
- **Database Guide**: `docs/technical/SUPABASE_DATABASE_GUIDE.md` - Database access
- **API Documentation**: `docs/guides/API_DOCUMENTATION.md` - API reference
- **Troubleshooting**: `docs/guides/TROUBLESHOOTING.md` - Common issues

---

## 📞 Support

### Fly.io Resources
- **Dashboard**: https://fly.io/dashboard/houserenovators-api
- **Documentation**: https://fly.io/docs
- **Community**: https://community.fly.io
- **Status**: https://status.fly.io

### Emergency Procedures

**Total outage**:
1. Check Fly.io status page
2. Review recent logs: `fly logs --limit 500`
3. Check machine status: `fly machines list`
4. Restart machines: `fly machines restart [ID]`
5. If persistent, rollback: `fly releases rollback`

**Database issues**:
1. Check Supabase dashboard: https://supabase.com/dashboard
2. Verify DATABASE_URL secret is correct
3. Test connection via SSH console
4. Contact Supabase support if needed

---

**Last Updated**: December 11, 2025  
**Fly.io Version**: flyctl v0.3.61  
**App Status**: ✅ Operational (2 machines, ord region)
