# 🔄 House Renovators AI Portal - Daily Workflow Guide

**Version**: 1.0.0  
**Last Updated**: November 3, 2025  
**For**: Development Team Daily Operations

---

## 📋 Table of Contents
- [Daily Development Workflow](#-daily-development-workflow)
- [Git & Version Control](#-git--version-control)
- [Backend Development](#-backend-development)
- [Frontend Development](#-frontend-development)
- [Deployment Procedures](#-deployment-procedures)
- [Testing & Validation](#-testing--validation)
- [Quick Reference Commands](#-quick-reference-commands)
- [Common Scenarios](#-common-scenarios)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Daily Development Workflow

### **Morning Startup Routine**

```powershell
# 1. Navigate to project root
cd "c:\Users\Steve Garay\Desktop\HouseRenovators-api"

# 2. Pull latest changes (main repo)
git pull origin main

# 3. Update backend submodule
cd backend
git pull origin main
cd ..

# 4. Check system health
curl https://houserenoai.onrender.com/health
curl https://houserenoai.onrender.com/debug/

# 5. Start local development (if needed)
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

### **Development Session Structure**

**Recommended Terminal Layout:**
- **Terminal 1**: Backend development (`backend/`)
- **Terminal 2**: Frontend development (`frontend/`)
- **Terminal 3**: Git operations (root directory)
- **Optional Terminal 4**: Health monitoring

---

## 🔀 Git & Version Control

### **Repository Structure**
```
Main Repo (HouseRenoAI)
├── Root directory: Project-wide files, docs, automation
├── backend/: Separate Git submodule (backend repo)
└── frontend/: Part of main repo
```

### **Standard Git Workflow**

#### **For Main Repo Changes (Root, Frontend, Docs)**
```powershell
# From root directory
cd "c:\Users\Steve Garay\Desktop\HouseRenovators-api"

# Check status
git status

# Stage changes
git add .
# OR specific files
git add docs/WORKFLOW_GUIDE.md
git add frontend/src/App.jsx

# Commit with clear message
git commit -m "Feature: Add new dashboard widget"

# Pull latest (avoid conflicts)
git pull origin main

# Push changes
git push origin main
```

#### **For Backend Changes (Submodule)**
```powershell
# Navigate to backend directory
cd "c:\Users\Steve Garay\Desktop\HouseRenovators-api\backend"

# Backend is a separate repository!
git status

# Stage and commit
git add app/routes/chat.py app/services/openai_service.py
git commit -m "Fix: Improve AI response formatting"

# Pull first (important for submodules)
git pull --rebase origin main

# Push backend changes
git push origin main

# Return to root and update submodule reference
cd ..
git add backend
git commit -m "Update backend submodule to latest"
git push origin main
```

### **Branch Management**

#### **Main Branch** (Default)
- Production-ready code
- Auto-deploys to Render (backend) and Cloudflare (frontend)
- Always pull before pushing

#### **Production Branch** (If needed)
```powershell
# Switch to production branch
git checkout production

# Make production-specific changes
git add .
git commit -m "Production: Update environment config"

# Push to production
git push origin production

# Switch back to main
git checkout main
```

### **Handling Merge Conflicts**

```powershell
# If you see "non-fast-forward" error
git pull origin main

# Check for conflicts
git status
# Look for files marked "both modified"

# If merge conflicts exist:
# 1. Open conflicted files
# 2. Look for conflict markers:
<<<<<<< HEAD
Your changes
=======
Remote changes
>>>>>>> commit-hash

# 3. Resolve conflicts manually
# 4. Remove conflict markers
# 5. Stage resolved files
git add conflicted-file.py

# 6. Complete merge
git commit -m "Merge: Resolve conflicts in conflicted-file.py"

# 7. Push
git push origin main
```

**⚠️ Common Mistake**: Forgetting to remove `<<<<<<< HEAD` markers causes syntax errors!

---

## 🐍 Backend Development

### **Local Development Setup**

```powershell
# Navigate to backend
cd "c:\Users\Steve Garay\Desktop\HouseRenovators-api\backend"

# Activate virtual environment
.\venv\Scripts\activate

# Install/update dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs
```

### **Environment Variables (Local)**

Create `.env` file in `backend/` directory:
```env
GOOGLE_SERVICE_ACCOUNT_BASE64=eyJ0eXBlIjoic2Vydm...
SHEET_ID=1BvDHl8XS9p7eKl4Q8F2wJ3mR5nT6uY9vI0pA7sS8dF1gH
OPENAI_API_KEY=sk-proj-...
CHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/...
DEBUG=true
PORT=8000
```

### **Common Backend Tasks**

#### **Test API Endpoints Locally**
```powershell
# Health check
curl http://localhost:8000/health

# Debug info
curl http://localhost:8000/debug/

# Get permits
curl http://localhost:8000/v1/permits/

# Test chat
curl -X POST http://localhost:8000/v1/chat/ `
  -H "Content-Type: application/json" `
  -d '{"message": "How many permits are approved?"}'
```

#### **Add New Endpoint**
1. Create/modify route in `app/routes/`
2. Add service logic in `app/services/`
3. Update `app/main.py` if needed
4. Test locally
5. Update `API_DOCUMENTATION.md`
6. Commit and deploy

#### **Update Dependencies**
```powershell
# Add new package
pip install new-package

# Update requirements.txt
pip freeze > requirements.txt

# Commit changes
git add requirements.txt
git commit -m "Deps: Add new-package for feature X"
```

---

## ⚛️ Frontend Development

### **Local Development Setup**

```powershell
# Navigate to frontend
cd "c:\Users\Steve Garay\Desktop\HouseRenovators-api\frontend"

# Install dependencies
npm install

# Run development server (with hot reload)
npm run dev

# Access at http://localhost:5173
```

### **Environment Variables (Local)**

Create `.env.local` file in `frontend/` directory:
```env
VITE_API_URL=http://localhost:8000
# OR for production testing:
# VITE_API_URL=https://houserenoai.onrender.com

VITE_ENV=development
VITE_ENABLE_DEBUG=true
```

### **Common Frontend Tasks**

#### **Build for Production**
```powershell
cd frontend

# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview
# Access at http://localhost:4173
```

#### **Check Build Size**
```powershell
npm run build

# Look for output like:
# dist/index.html                   0.46 kB
# dist/assets/index-abc123.css     72.83 kB
# dist/assets/index-def456.js     182.79 kB
```

#### **Lint and Format**
```powershell
# Run ESLint
npm run lint

# Auto-fix issues
npm run lint -- --fix
```

---

## 🚀 Deployment Procedures

### **Backend Deployment (Render)**

#### **Method 1: Auto-Deploy (Recommended)**
```powershell
# From backend directory
cd "c:\Users\Steve Garay\Desktop\HouseRenovators-api\backend"

# Make your changes, then:
git add .
git commit -m "Feature: Description of changes"
git push origin main

# ✅ Render automatically detects push and deploys
# ⏱️ Takes ~4 minutes for Starter tier
# 📊 Monitor: https://dashboard.render.com
```

**Deployment Timeline:**
- 0-30s: Clone repository
- 30s-1m: Install dependencies
- 1m-2m: Upload build
- 2m-4m: Health checks and go-live

#### **Method 2: Manual Deploy (If Auto-Deploy Fails)**
1. Go to https://dashboard.render.com
2. Select "house-renovators-ai-portal" service
3. Click "Manual Deploy" → "Deploy latest commit"
4. Monitor build logs

#### **Verify Backend Deployment**
```powershell
# Check health immediately after deploy
curl https://houserenoai.onrender.com/health

# Verify Google service
curl https://houserenoai.onrender.com/debug/

# Test permit endpoint
curl https://houserenoai.onrender.com/v1/permits/

# Test AI chat
curl -X POST https://houserenoai.onrender.com/v1/chat/ `
  -H "Content-Type: application/json" `
  -d '{"message": "System check"}'
```

### **Frontend Deployment (Cloudflare Pages)**

#### **Method 1: Wrangler CLI (Immediate Deploy)**
```powershell
# Navigate to frontend
cd "c:\Users\Steve Garay\Desktop\HouseRenovators-api\frontend"

# Build production bundle
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages deploy dist --project-name=house-renovators-ai-portal --branch=main

# ✅ Deployment completes in ~30 seconds
# 🌐 Available immediately at Cloudflare URLs
```

**Output URLs:**
- Deployment URL: `https://[hash].house-renovators-ai-portal.pages.dev`
- Production URL: `https://house-renovators-ai-portal.pages.dev`

#### **Method 2: Git-Triggered (If Configured)**
```powershell
# Commit and push changes
git add frontend/
git commit -m "Frontend: Update dashboard UI"
git push origin main

# Cloudflare detects push and auto-deploys
```

#### **Verify Frontend Deployment**
```powershell
# Check if accessible
curl https://house-renovators-ai-portal.pages.dev

# Check specific deployment
curl https://26a6cac5.house-renovators-ai-portal.pages.dev
```

### **Full Stack Deployment (Both)**

```powershell
# Option 1: Sequential (Safe)
# 1. Deploy backend first
cd backend
git add . && git commit -m "Update backend" && git push origin main

# 2. Wait for backend deployment (~4 min)
# 3. Test backend health

# 4. Deploy frontend
cd ../frontend
npm run build
npx wrangler pages deploy dist --project-name=house-renovators-ai-portal --branch=main

# Option 2: Parallel (Advanced)
# Deploy both simultaneously and monitor both dashboards
```

---

## 🧪 Testing & Validation

### **Pre-Deployment Checklist**

```powershell
# 1. Run local tests
cd backend
pytest  # If tests exist

# 2. Check for syntax errors
python -m py_compile app/main.py
python -m py_compile app/routes/chat.py

# 3. Test API endpoints locally
curl http://localhost:8000/health
curl http://localhost:8000/v1/permits/

# 4. Build frontend without errors
cd ../frontend
npm run build

# 5. Check for console errors
npm run preview
# Visit http://localhost:4173 and check browser console
```

### **Post-Deployment Validation**

```powershell
# Backend validation
curl https://houserenoai.onrender.com/health | jq
curl https://houserenoai.onrender.com/debug/ | jq
curl https://houserenoai.onrender.com/v1/permits/ | jq '. | length'

# Frontend validation
curl -I https://house-renovators-ai-portal.pages.dev
# Should return "200 OK"

# End-to-end test
# Visit frontend URL in browser
# Try chat: "How many permits are approved?"
# Verify response is formatted and accurate
```

### **Health Monitoring Script**

```powershell
# Create health-check.ps1
$backend = Invoke-RestMethod -Uri "https://houserenoai.onrender.com/health"
$debug = Invoke-RestMethod -Uri "https://houserenoai.onrender.com/debug/"

Write-Host "Backend Status: $($backend.status)"
Write-Host "Google Service: $($debug.google_service_initialized.sheets_service)"
Write-Host "Permits Available: $((Invoke-RestMethod -Uri "https://houserenoai.onrender.com/v1/permits/").Count)"

if ($backend.status -eq "healthy") {
    Write-Host "✅ All systems operational"
} else {
    Write-Host "❌ Issues detected"
}
```

---

## ⚡ Quick Reference Commands

### **Navigation**
```powershell
# Root directory
cd "c:\Users\Steve Garay\Desktop\HouseRenovators-api"

# Backend
cd backend

# Frontend  
cd frontend

# Automation tools
cd automation
```

### **Git Operations**
```powershell
# Status check
git status

# Pull latest
git pull origin main

# Stage all changes
git add .

# Commit
git commit -m "Type: Description"

# Push
git push origin main

# Undo last commit (local only)
git reset --soft HEAD~1

# Force push (dangerous - use carefully)
git push origin main --force
```

### **Backend**
```powershell
# Activate venv
cd backend && .\venv\Scripts\activate

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Install deps
pip install -r requirements.txt

# Update deps
pip freeze > requirements.txt

# Test endpoint
curl http://localhost:8000/health
```

### **Frontend**
```powershell
# Install deps
npm install

# Dev server
npm run dev

# Build
npm run build

# Deploy
npx wrangler pages deploy dist --project-name=house-renovators-ai-portal --branch=main

# Preview build
npm run preview
```

### **Health Checks**
```powershell
# Backend health
curl https://houserenoai.onrender.com/health

# Google service status
curl https://houserenoai.onrender.com/debug/

# Get permits
curl https://houserenoai.onrender.com/v1/permits/

# Frontend status
curl -I https://house-renovators-ai-portal.pages.dev
```

---

## 🎭 Common Scenarios

### **Scenario 1: Fix Bug in Backend**

```powershell
# 1. Identify issue in production
curl https://houserenoai.onrender.com/debug/

# 2. Reproduce locally
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
curl http://localhost:8000/debug/

# 3. Fix code in app/services/ or app/routes/

# 4. Test locally
curl http://localhost:8000/debug/

# 5. Commit and deploy
git add .
git commit -m "Fix: Resolve Google service initialization issue"
git push origin main

# 6. Monitor deployment
# Watch Render dashboard for ~4 minutes

# 7. Verify fix
curl https://houserenoai.onrender.com/debug/
```

### **Scenario 2: Add New Frontend Feature**

```powershell
# 1. Start dev server
cd frontend
npm run dev

# 2. Make changes to src/components/ or src/pages/

# 3. Test in browser at http://localhost:5173

# 4. Build for production
npm run build

# 5. Preview production build
npm run preview

# 6. Deploy
npx wrangler pages deploy dist --project-name=house-renovators-ai-portal --branch=main

# 7. Commit changes
cd ..
git add frontend/
git commit -m "Feature: Add new dashboard widget"
git push origin main
```

### **Scenario 3: Update AI System Prompt**

```powershell
# 1. Edit backend/app/services/openai_service.py
# Modify system_prompt variable

# 2. Test locally
cd backend
uvicorn app.main:app --reload
curl -X POST http://localhost:8000/v1/chat/ `
  -H "Content-Type: application/json" `
  -d '{"message": "test query"}'

# 3. Deploy
git add app/services/openai_service.py
git commit -m "AI: Update system prompt for better responses"
git push origin main

# 4. Wait for deployment (~4 min)

# 5. Test production
curl -X POST https://houserenoai.onrender.com/v1/chat/ `
  -H "Content-Type: application/json" `
  -d '{"message": "test query"}'
```

### **Scenario 4: Add New Environment Variable**

**Backend (Render):**
1. Go to https://dashboard.render.com
2. Select service → Settings → Environment
3. Add new key-value pair
4. Click "Save Changes"
5. Service automatically restarts

**Frontend (Cloudflare):**
1. Edit `frontend/.env.local` for local development
2. For production:
   ```powershell
   cd frontend
   npx wrangler pages deployment create \
     --env production \
     --var KEY=VALUE
   ```
3. Or add via Cloudflare Dashboard → Pages → Settings → Environment Variables

### **Scenario 5: Emergency Rollback**

**Backend:**
```powershell
# Option 1: Render Dashboard
# 1. Go to Deploys tab
# 2. Find last working deployment
# 3. Click "Rollback"

# Option 2: Git revert
cd backend
git log --oneline  # Find last working commit
git revert HEAD~1  # Revert last commit
git push origin main
```

**Frontend:**
```powershell
# Redeploy previous version
cd frontend
git log --oneline
git checkout <previous-commit-hash>
npm run build
npx wrangler pages deploy dist --project-name=house-renovators-ai-portal --branch=main
git checkout main  # Return to latest
```

---

## 🚨 Troubleshooting

### **"Git push rejected - non-fast-forward"**

**Cause**: Remote has changes you don't have locally

**Solution**:
```powershell
# Pull with rebase (preferred)
git pull --rebase origin main

# OR standard merge
git pull origin main

# Then push
git push origin main
```

### **"Merge conflict in file.py"**

**Cause**: Your changes conflict with remote changes

**Solution**:
```powershell
# 1. Pull to trigger merge
git pull origin main

# 2. Check conflicted files
git status

# 3. Open conflicted file, look for:
<<<<<<< HEAD
Your code
=======
Remote code
>>>>>>> commit-hash

# 4. Manually resolve:
# - Keep your version, OR
# - Keep remote version, OR
# - Combine both
# - DELETE conflict markers (<<<, ===, >>>)

# 5. Stage resolved file
git add resolved-file.py

# 6. Complete merge
git commit -m "Merge: Resolve conflicts in resolved-file.py"

# 7. Push
git push origin main
```

**⚠️ CRITICAL**: Always remove conflict markers or deployment will fail with syntax errors!

### **"Backend deployment failed"**

**Check Render logs:**
1. Go to https://dashboard.render.com
2. Select service → Logs
3. Look for error messages

**Common Issues:**
- Syntax errors (forgot to remove `<<<<<<< HEAD`)
- Missing dependencies in requirements.txt
- Environment variables not set
- Google service account issues

**Quick Fix:**
```powershell
# Test build locally
cd backend
pip install -r requirements.txt
python -m py_compile app/main.py

# If syntax error found, fix and redeploy
git add .
git commit -m "Fix: Resolve syntax error"
git push origin main
```

### **"Frontend not updating after deployment"**

**Cause**: Browser caching or build not deployed

**Solution**:
```powershell
# 1. Force new build
cd frontend
rm -rf dist
npm run build

# 2. Deploy with explicit project name
npx wrangler pages deploy dist --project-name=house-renovators-ai-portal --branch=main

# 3. Clear browser cache (Ctrl+Shift+R)

# 4. Check deployment URL returned by Wrangler
# Visit the specific deployment URL, not cached one
```

### **"AI responses not formatted properly"**

**Check system prompt:**
```powershell
# 1. Verify latest code is deployed
curl https://houserenoai.onrender.com/debug/
# Check timestamp

# 2. Test specific query
curl -X POST https://houserenoai.onrender.com/v1/chat/ `
  -H "Content-Type: application/json" `
  -d '{"message": "list all clients grouped by Status"}' | jq

# 3. If formatting is wrong, check:
# - backend/app/services/openai_service.py system_prompt
# - Ensure formatting rules are present
# - Redeploy if needed
```

### **"Google service not initialized"**

**Debug steps:**
```powershell
# 1. Check debug endpoint
curl https://houserenoai.onrender.com/debug/

# 2. If credentials=false:
# - Verify GOOGLE_SERVICE_ACCOUNT_BASE64 is set in Render
# - Check it's valid base64
# - Ensure newlines are handled correctly

# 3. If services=false:
# - Verify Google APIs are enabled
# - Check service account permissions
# - Ensure Sheet is shared with service account

# 4. Restart service in Render dashboard
```

### **"Can't find client ID in data"**

**Cause**: Context not being passed to AI properly

**Solution**:
```powershell
# 1. Check recent backend deployment
curl https://houserenoai.onrender.com/debug/

# 2. Verify data is loading
curl https://houserenoai.onrender.com/v1/permits/ | jq '. | length'

# 3. Test with explicit ID from permit data
curl https://houserenoai.onrender.com/v1/permits/ | jq '.[0]["Client ID"]'

# 4. Use that ID in chat query
curl -X POST https://houserenoai.onrender.com/v1/chat/ `
  -H "Content-Type: application/json" `
  -d '{"message": "details of client <ID>"}'
```

---

## 📊 Monitoring & Maintenance

### **Daily Health Check**
```powershell
# Run this every morning
.\automation\api-scripts\health-check.ps1 -All

# OR manual checks:
curl https://houserenoai.onrender.com/health | jq
curl https://houserenoai.onrender.com/debug/ | jq
curl https://houserenoai.onrender.com/v1/permits/ | jq '. | length'
```

### **Weekly Tasks**
- Review Render logs for errors
- Check Google API quota usage
- Monitor OpenAI API costs
- Update dependencies if needed
- Review and update documentation

### **Monthly Tasks**
- Security audit (rotate API keys)
- Performance optimization review
- Backup verification
- Capacity planning

---

## 🔗 Related Documentation

- **[README.md](README.md)** - Project overview
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[DEPLOYMENT.md](backend/DEPLOYMENT.md)** - Detailed deployment guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Advanced troubleshooting
- **[automation/README.md](automation/README.md)** - DevOps automation toolkit
- **[IMPLEMENTATION_PROGRESS.md](docs/IMPLEMENTATION_PROGRESS.md)** - Development status

---

**📞 Need Help?**
- Check troubleshooting section above
- Review related documentation
- Check Render/Cloudflare dashboards
- Review recent commit history for changes

**✨ Pro Tips:**
- Always pull before pushing
- Test locally before deploying
- Monitor deployments to completion
- Keep documentation updated
- Commit small, focused changes
- Use clear commit messages

---

**Last Updated**: November 3, 2025  
**Maintained By**: Development Team  
**Version**: 1.0.0
