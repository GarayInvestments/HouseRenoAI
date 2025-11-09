# Development Environment Setup Guide

**Last Updated:** November 9, 2025  
**Audience:** Developers setting up complete development environment

Complete guide for setting up the House Renovators AI Portal development environment.

---

## 📋 Table of Contents

1. [Initial Setup](#initial-setup)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [GitHub Actions & CI/CD](#github-actions--cicd)
5. [Secrets Management](#secrets-management)
6. [GitKraken MCP Integration](#gitkraken-mcp-integration)
7. [Testing & Validation](#testing--validation)

---

## 🎯 Initial Setup

### Prerequisites

- **Git** 2.40+ installed
- **Python** 3.11+ installed
- **Node.js** 18+ and npm installed
- **PowerShell** 7+ (Windows) or bash (Linux/Mac)
- **VS Code** (recommended) with extensions:
  - Python
  - Pylance
  - ESLint
  - Prettier

### Clone Repository

```powershell
# Clone the repository
git clone https://github.com/GarayInvestments/HouseRenoAI.git
cd HouseRenoAI

# Checkout main branch
git checkout main
git pull origin main
```

---

## 🐍 Backend Setup

### 1. Create Virtual Environment

```powershell
# Create venv in project root
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```powershell
# Install Python packages
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed')"
python -c "import openai; print('OpenAI installed')"
```

### 3. Configure Environment Variables

Create `.env` file in project root:

```bash
# Google Sheets API
SHEET_ID=1jwBLi2wQMEyZ9pFFIqvdBNxRQ0w_z7yDLRO80zDcqFo
GOOGLE_SERVICE_ACCOUNT_FILE=config/house-renovators-credentials.json

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# QuickBooks (for testing)
QB_CLIENT_ID=your_qb_client_id
QB_CLIENT_SECRET=your_qb_client_secret
QB_REDIRECT_URI=http://localhost:8000/v1/quickbooks/callback
QB_ENVIRONMENT=sandbox  # Use sandbox for development

# JWT Secret (generate random string)
JWT_SECRET=your_random_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080  # 7 days

# API Configuration
API_VERSION=v1
DEBUG=true
PORT=8000
```

### 4. Set Up Google Sheets Credentials

**Option A: Using git-secret (Recommended)**

If credentials are encrypted:
```powershell
# Reveal encrypted files
.\scripts\git-secret-wrapper.ps1 -Action reveal

# Credentials will be decrypted to:
# - .env
# - config/house-renovators-credentials.json
```

**Option B: Manual Setup**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create service account
3. Download JSON key
4. Save as `config/house-renovators-credentials.json`
5. Share Google Sheet with service account email

### 5. Run Backend

```powershell
# Activate venv if not already active
.\venv\Scripts\Activate.ps1

# Start development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/health
```

### 6. Test Backend

```powershell
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy"}

# Test Sheets connection
curl http://localhost:8000/v1/clients

# Should return client list
```

---

## ⚛️ Frontend Setup

### 1. Install Dependencies

```powershell
# Navigate to frontend directory
cd frontend

# Install npm packages
npm install

# Verify installation
npm list react
npm list vite
```

### 2. Configure Environment

Create `frontend/.env`:

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000

# For production testing:
# VITE_API_URL=https://houserenoai.onrender.com
```

### 3. Run Frontend

```powershell
# Still in frontend/ directory
npm run dev

# Frontend available at:
# http://localhost:5173
```

### 4. Test Frontend

1. Open browser to `http://localhost:5173`
2. Should see House Renovators AI Portal
3. Test navigation (Projects, Clients, AI Assistant)
4. Verify backend connection (data should load)

### 5. Build for Production

```powershell
# Create production build
npm run build

# Preview production build
npm run preview

# Build output in: frontend/dist/
```

---

## 🤖 GitHub Actions & CI/CD

### Setup Overview

The project uses GitHub Actions for automated testing and deployment:
- **Backend Tests**: Run on every push/PR
- **Auto-Deploy**: Production deploy on push to `main`

### Configure GitHub Secrets

Required secrets for GitHub Actions:

1. Go to repository → Settings → Secrets and variables → Actions
2. Add the following secrets:

**Backend Secrets:**
```
RENDER_API_KEY              # Render API key for deployments
RENDER_SERVICE_ID           # Backend service ID (srv-d44ak76uk2gs73a3psig)
GOOGLE_SERVICE_ACCOUNT      # Google Sheets service account JSON (base64)
OPENAI_API_KEY              # OpenAI API key
QB_CLIENT_ID                # QuickBooks client ID
QB_CLIENT_SECRET            # QuickBooks client secret
JWT_SECRET                  # JWT signing secret
```

**Frontend Secrets:**
```
CLOUDFLARE_API_TOKEN        # Cloudflare Pages deploy token
CLOUDFLARE_ACCOUNT_ID       # Cloudflare account ID
```

### Workflow Files

**Backend Testing** (`.github/workflows/test-backend.yml`):
```yaml
name: Backend Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=app
```

**Auto-Deploy** (`.github/workflows/deploy.yml`):
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy
        run: |
          curl -X POST "https://api.render.com/v1/services/${{ secrets.RENDER_SERVICE_ID }}/deploys" \
            -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}" \
            -H "Content-Type: application/json"
```

### Testing CI/CD

```powershell
# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin main

# Check GitHub Actions tab
# Should see workflows running
```

---

## 🔐 Secrets Management

### Git-Secret Setup

Git-secret encrypts sensitive files using GPG keys.

**Initial Setup:**

```powershell
# Install GPG (if not installed)
choco install gpg4win  # Windows

# Generate GPG key (if you don't have one)
gpg --full-generate-key
# Follow prompts, use your email

# Initialize git-secret
git secret init

# Add yourself to git-secret
git secret tell your-email@example.com

# Encrypt sensitive files
.\scripts\git-secret-wrapper.ps1 -Action hide

# This encrypts:
# - .env → .env.secret
# - config/*.json → config/*.json.secret
```

**Daily Workflow:**

```powershell
# After pulling changes, decrypt files
.\scripts\git-secret-wrapper.ps1 -Action reveal

# After modifying .env or credentials
.\scripts\git-secret-wrapper.ps1 -Action hide

# Commit encrypted files
git add .env.secret config/*.secret
git commit -m "Update secrets"
git push
```

**Adding Team Members:**

```powershell
# Team member sends their GPG public key fingerprint
# Example: D88ABC088FC640A1DA41201D94A3CF4D06A4772F

# Add team member
.\scripts\git-secret-wrapper.ps1 -Action tell -Email teammate@example.com

# Re-encrypt files for all users
.\scripts\git-secret-wrapper.ps1 -Action hide

# Commit
git add *.secret
git commit -m "Add teammate to secrets"
git push
```

### Alternative: Password-Based Encryption

If GPG is not available:

```powershell
# Encrypt (prompts for password)
.\scripts\encrypt-secrets.ps1 -Action encrypt

# Creates .encrypted files:
# - .env.encrypted
# - config/credentials.json.encrypted

# Decrypt (prompts for password)
.\scripts\encrypt-secrets.ps1 -Action decrypt
```

---

## 🦑 GitKraken MCP Integration

Model Context Protocol (MCP) integration for enhanced development workflows.

### Prerequisites

- **GitKraken CLI** installed
- **GitKraken account** (free tier works)
- **GitHub account** linked to GitKraken

### Setup GitKraken MCP

**1. Install GitKraken CLI:**

```powershell
# Windows (via winget)
winget install GitKraken.cli

# Mac
brew install gitkraken-cli

# Verify installation
gk --version
```

**2. Authenticate:**

```powershell
# Login to GitKraken
gk auth login

# Link GitHub account
gk auth github
```

**3. Configure MCP Server:**

Create `mcp-config.json` in project root:

```json
{
  "mcpServers": {
    "gitkraken": {
      "command": "gk",
      "args": ["mcp"],
      "env": {
        "GITKRAKEN_TOKEN": "your-token-here"
      }
    }
  }
}
```

**4. Test MCP Integration:**

```powershell
# Test MCP connection
gk mcp test

# Expected: ✅ MCP server running
```

### MCP Features Available

**Git Operations:**
- `gk branch list` - List all branches
- `gk branch create <name>` - Create new branch
- `gk checkout <branch>` - Switch branches
- `gk commit -m "message"` - Commit changes
- `gk push` - Push to remote

**Issue Tracking:**
- `gk issue list` - List GitHub issues
- `gk issue view <id>` - View issue details
- `gk issue create` - Create new issue

**Pull Requests:**
- `gk pr list` - List pull requests
- `gk pr create` - Create new PR
- `gk pr view <id>` - View PR details

**Workspaces:**
- `gk workspace list` - List GitKraken workspaces
- `gk workspace open <name>` - Open workspace

### VS Code Integration

Install GitKraken extension in VS Code:

1. Open VS Code Extensions (Ctrl+Shift+X)
2. Search "GitKraken"
3. Install "GitKraken - Git GUI"
4. Reload VS Code
5. GitKraken panel appears in sidebar

---

## 🧪 Testing & Validation

### Backend Tests

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Coverage report: htmlcov/index.html
```

### Frontend Tests

```powershell
cd frontend

# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

### Integration Tests

```powershell
# Test QuickBooks integration
python scripts/testing/test_quickbooks_comprehensive.py

# Test chat functionality
python test_chat_comprehensive.py

# Test client sync
python test_sync_production.py
```

### Manual Testing Checklist

- [ ] **Backend Health**
  - [ ] http://localhost:8000/health returns 200
  - [ ] http://localhost:8000/docs shows API documentation
  - [ ] /v1/clients returns client data

- [ ] **Frontend**
  - [ ] http://localhost:5173 loads without errors
  - [ ] Navigation works (all pages accessible)
  - [ ] Data loads from backend

- [ ] **Authentication**
  - [ ] Login works with test credentials
  - [ ] JWT token stored in localStorage
  - [ ] Protected routes require authentication

- [ ] **QuickBooks**
  - [ ] OAuth flow completes
  - [ ] Customers/invoices load
  - [ ] Chat integration works

- [ ] **AI Chat**
  - [ ] Chat interface loads
  - [ ] Messages send and receive responses
  - [ ] No hallucinated data

---

## 📚 Related Documentation

- **Quick Reference:** `docs/SETUP_QUICK_REFERENCE.md` - Daily commands
- **New Machine Setup:** `docs/SETUP_NEW_MACHINE.md` - Onboarding guide
- **Git-Secret Guide:** `docs/GIT_SECRET_SETUP.md` - Detailed git-secret docs
- **API Documentation:** `docs/API_DOCUMENTATION.md` - API reference
- **Troubleshooting:** `docs/TROUBLESHOOTING.md` - Common issues

---

## 🐛 Common Setup Issues

### Issue: "Module not found" errors

**Solution:**
```powershell
# Ensure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "GOOGLE_SERVICE_ACCOUNT_FILE not found"

**Solution:**
```powershell
# Decrypt credentials
.\scripts\git-secret-wrapper.ps1 -Action reveal

# Verify file exists
Test-Path config/house-renovators-credentials.json
```

### Issue: Frontend can't connect to backend

**Solution:**
```powershell
# Check backend is running
curl http://localhost:8000/health

# Check frontend .env
cat frontend/.env
# Should have: VITE_API_URL=http://localhost:8000

# Restart frontend
cd frontend
npm run dev
```

### Issue: Git-secret "gpg: decryption failed"

**Solution:**
```powershell
# Verify your GPG key
gpg --list-secret-keys

# Re-import key if needed
gpg --import your-private-key.asc

# Try reveal again
.\scripts\git-secret-wrapper.ps1 -Action reveal
```

---

## 🔄 Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-09 | 2.0 | Consolidated from 4 setup docs |
| 2025-11-09 | 1.3 | Added git-secret setup |
| 2025-11-07 | 1.2 | Added GitKraken MCP |
| 2025-11-06 | 1.1 | Added GitHub Actions |
| 2025-11-06 | 1.0 | Initial setup guide |

---

**Ready to Start?**
1. Follow [Initial Setup](#initial-setup)
2. Set up [Backend](#backend-setup)
3. Set up [Frontend](#frontend-setup)
4. Configure [Secrets](#secrets-management)
5. Run [Tests](#testing--validation)
