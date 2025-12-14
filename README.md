# 🏠 House Renovators AI Portal

![FastAPI](https://img.shields.io/badge/Backend-FastAPI-blue)
![React](https://img.shields.io/badge/Frontend-React_PWA-cyan)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![Supabase](https://img.shields.io/badge/Auth-Supabase-green)
![OpenAI](https://img.shields.io/badge/AI-GPT--4o-purple)
![Fly.io](https://img.shields.io/badge/Deploy-Fly.io-blueviolet)
![Cloudflare](https://img.shields.io/badge/CDN-Cloudflare-orange)

> **AI-powered construction management system with smart permit tracking, QuickBooks integration, and intelligent document processing.**

## ✅ **PRODUCTION STATUS** (December 13, 2025)

- 🚀 **Backend API**: https://houserenovators-api.fly.dev (Fly.io - 3 VMs)
- 📱 **Frontend PWA**: https://portal.houserenovatorsllc.com (Cloudflare Pages)
- 🤖 **AI Engine**: OpenAI GPT-4o with smart context loading (90% fewer API calls)
- 💾 **Database**: PostgreSQL (Supabase) - 8 clients, 13 projects, 9 permits, 1 payment
- 🔐 **Authentication**: Supabase Auth with JWT verification (route-level protection)
- 💼 **QuickBooks**: OAuth2 production (24+ customers, 53+ invoices, auto-sync)
- 📊 **Architecture**: Project-centric data model with business IDs (CL-00001, PRJ-00001, PER-00001)
- ⚡ **Performance**: 100% async operations, smart caching, 80% faster than v1
- 📚 **Documentation**: 60+ docs organized in `/docs` with governance policy

---

## 📁 Project Structure

```
HouseRenovators-api/
├── 📂 app/                     # FastAPI Backend Application
│   ├── config.py               # Configuration and environment variables
│   ├── main.py                 # FastAPI application entry point
│   ├── 📂 handlers/            # AI Function Handlers
│   │   └── ai_functions.py    # QB sync, payments, customer creation (1100+ lines)
│   ├── 📂 memory/              # Session Management
│   │   └── memory_manager.py  # TTL-based session storage
│   ├── 📂 middleware/          # Request Middleware
│   │   └── auth_middleware.py # JWT authentication protection
│   ├── 📂 routes/              # API Endpoint Routes
│   │   ├── auth.py            # Login, register, JWT endpoints
│   │   ├── chat.py            # AI chat with smart context loading
│   │   ├── clients.py         # Client management endpoints
│   │   ├── documents.py       # Document upload & AI extraction
│   │   ├── permits.py         # Permit management endpoints
│   │   ├── projects.py        # Project management endpoints
│   │   ├── payments.py        # Payment tracking & QB sync (NEW Nov 10)
│   │   └── quickbooks.py      # QB OAuth2, customers, invoices, sync
│   ├── 📂 services/            # Core Business Logic
│   │   ├── auth_service.py    # JWT + bcrypt authentication
│   │   ├── db_service.py      # PostgreSQL database operations (async SQLAlchemy)
│   │   ├── google_service.py  # Google Sheets integration (LEGACY - QB tokens only)
│   │   ├── openai_service.py  # OpenAI GPT-4o with function calling
│   │   └── quickbooks_service.py  # QB OAuth2, CRUD operations, sync
│   └── 📂 utils/               # Utility Functions
│       └── context_builder.py # Smart context loading from database
├── 📂 frontend/                # React PWA Frontend Application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── lib/               # Utilities and API client
│   │   ├── pages/             # Main application pages
│   │   │   ├── AIAssistant.jsx  # Chat interface with document upload
│   │   │   ├── Clients.jsx      # Client list with status breakdown
│   │   │   ├── ClientDetails.jsx # Client detail view
│   │   │   ├── Projects.jsx     # Project list with filters
│   │   │   └── Login.jsx        # Authentication page
│   │   └── 📂 stores/         # Zustand State Management
│   │       └── appStore.js    # Global state (navigation, current view)
│   ├── package.json
│   └── vite.config.js
├── 📂 backend/                 # Legacy backend directory (for reference)
├── 📂 docs/                    # Project Documentation (ORGANIZED Nov 10, 2025)
│   ├── README.md              # Documentation hub and navigation guide
│   ├── 📂 guides/             # User and developer guides (6 files)
│   ├── 📂 setup/              # Environment setup docs (4 files)
│   ├── 📂 deployment/         # Deployment guides (3 files)
│   ├── 📂 technical/          # Technical specs and design (6 files)
│   ├── 📂 session-logs/       # Development session summaries
│   ├── 📂 metrics/            # Performance metrics and baselines
│   └── 📂 archive/            # Historical documentation (22 files)
├── 📂 config/                  # Configuration Files
├── 📂 scripts/                 # Utility Scripts
├── 📄 requirements.txt         # Python dependencies (Pillow, PyPDF2 added)
├── 📄 runtime.txt              # Python version specification
├── � Dockerfile               # Container configuration
├── 📄 .env                     # Environment variables (not in git)
└── 📄 README.md                # This file

**NOTE**: The active backend code is in the `app/` directory at the root level. The `backend/` directory contains legacy/reference files from previous restructuring.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (for backend)
- Node.js 18+ (for frontend)
- Git
- GPG (for encrypted secrets) - [Install Gpg4win](https://www.gpg4win.org/download.html) on Windows
- Visual Studio Code (recommended)

### 1. Clone Repository
```bash
git clone https://github.com/GarayInvestments/HouseRenoAI.git
cd HouseRenovators-api
```

### 2. Decrypt Secrets (Git-Secret)
```bash
# Ensure GPG is in PATH (Windows)
# Add to PATH: C:\Program Files (x86)\GnuPG\bin

# If first time on new machine, import GPG private key
# From old machine: gpg --export-secret-keys your@email.com > private-key.asc
# gpg --import private-key.asc

# Decrypt secrets from Git
.\scripts\git-secret-wrapper.ps1 -Action reveal
# This decrypts: .env and config/house-renovators-credentials.json
```

### 3. Backend Setup
```bash
# Create virtual environment (root level)
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL password-less access (one-time)
.\scripts\setup-pgpass.ps1

# Run development server (from root - app/ is at root level)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend runs at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### 4. Frontend Setup
```bash
cd frontend
npm install

# Run development server
npm run dev
# Frontend runs at: http://localhost:5173

# Note: By default, local dev points to PRODUCTION backend (Fly.io)
# To use local backend, create frontend/.env.local:
# VITE_API_URL=http://localhost:8000
```

---

## 🔐 Secrets Management

### **Git-Secret Workflow**

We use **git-secret** to encrypt sensitive files before committing them to Git. This allows secure collaboration without exposing credentials.

#### Daily Workflow
```powershell
# After modifying .env or credentials
.\scripts\git-secret-wrapper.ps1 -Action hide

# Commit encrypted files
git add .env.secret config/*.secret
git commit -m "Update secrets"
git push

# On new machine or after git pull
.\scripts\git-secret-wrapper.ps1 -Action reveal
```

#### Adding Team Members
```powershell
# Team member shares their GPG public key fingerprint
.\scripts\git-secret-wrapper.ps1 -Action tell -Email "teammate@example.com"

# Re-encrypt files so they can decrypt
.\scripts\git-secret-wrapper.ps1 -Action hide
git add *.secret
git commit -m "Add teammate to secrets"
git push
```

#### Encrypted Files in Git
- `.env.secret` - Environment variables (API keys, JWT secrets)
- `config/house-renovators-credentials.json.secret` - Google service account

#### Alternative: PowerShell Encryption (No GPG)
```powershell
# Encrypt with password (no GPG required)
.\scripts\encrypt-secrets.ps1 -Action encrypt

# Decrypt with password
.\scripts\encrypt-secrets.ps1 -Action decrypt
```

**Documentation**: See `docs/SETUP_NEW_MACHINE.md` for complete setup guide.

---

## 🏗️ Architecture

### **Multi-Cloud Infrastructure**
- **Backend**: Fly.io (3 VMs, auto-scaling)
- **Frontend**: Cloudflare Pages (edge CDN)
- **Database**: PostgreSQL (Supabase, connection pooling)
- **Authentication**: Supabase Auth (hosted JWT service)
- **AI**: OpenAI GPT-4o with function calling
- **Payments**: QuickBooks Online (OAuth2 production)
- **CI/CD**: GitHub Actions → Fly.io + Cloudflare Pages

### **Technology Stack**

#### Backend (FastAPI)
- **Framework**: FastAPI 0.104+ with async/await
- **Database**: PostgreSQL 15 via SQLAlchemy 2.0 (async)
- **ORM**: 8 tables with foreign keys, business IDs (CL-00001, PRJ-00001, etc.)
- **Auth**: Supabase JWT verification (route-level dependencies, no middleware)
- **AI**: OpenAI GPT-4o with smart context loading (90% fewer API calls)
- **Integrations**: QuickBooks OAuth2, document parsing (PDF/image)
- **Deployment**: Docker on Fly.io with health checks

#### Frontend (React PWA)
- **Framework**: React 19 with Vite 5
- **State**: Zustand (global state management)
- **Auth**: Supabase Auth SDK (`@supabase/supabase-js`)
- **API**: Axios with automatic Authorization headers
- **PWA**: Service workers, offline support, installable
- **Deployment**: Cloudflare Pages with edge caching

#### Data Model (Project-Centric)
- **Clients** → Many Projects
- **Projects** → Many Permits, Inspections, Site Visits
- **Payments** → Link to Projects or Invoices
- **QuickBooks** → Syncs Customers, Invoices, Payments
- **Business IDs**: Human-readable (CL-00001, PRJ-00001, PER-00001, PAY-00001)

---

## 📚 Documentation

### **Essential Guides**
- 📖 [**API Documentation**](docs/API_DOCUMENTATION.md) - Complete API reference
- 🚀 [**Deployment Guide**](docs/DEPLOYMENT.md) - Production deployment
- 🔧 [**Setup Guide**](docs/SETUP_GUIDE.md) - Full development environment setup **(NEW)**
- 🩺 [**Troubleshooting**](docs/TROUBLESHOOTING.md) - Common issues and solutions
- 🧪 [**Chat Testing SOP**](docs/CHAT_TESTING_SOP.md) - Standard chat testing procedures

### **Quick References**
- ⚡ [**Quick Reference**](docs/SETUP_QUICK_REFERENCE.md) - Daily commands cheat sheet
- 💻 [**New Machine Setup**](docs/SETUP_NEW_MACHINE.md) - Onboarding guide
- 📋 [**Field Mapping**](docs/FIELD_MAPPING.md) - PDF extraction field structure
- 📊 [**Google Sheets Structure**](docs/GOOGLE_SHEETS_STRUCTURE.md) - Complete sheet schemas **(NEW)**
- � [**Project Status**](docs/PROJECT_STATUS.md) - Current status and roadmap

### **Integration Guides**
- 💼 [**QuickBooks Guide**](docs/QUICKBOOKS_GUIDE.md) - Complete QB integration **(NEW)**
- 🔐 [**Git-Secret Setup**](docs/GIT_SECRET_SETUP.md) - Secrets management
- �️ [**Logging & Security**](docs/LOGGING_SECURITY.md) - Security best practices

### **DevOps & Monitoring**
- � [**Render Logs Guide**](docs/RENDER_LOGS_GUIDE.md) - Production log access
- ☁️ [**Render API Guide**](docs/RENDER_API_DEPLOYMENT_GUIDE.md) - Automated deployments
- 📊 [**Baseline Metrics**](docs/BASELINE_METRICS.md) - Performance tracking
- � [**Workflow Guide**](docs/WORKFLOW_GUIDE.md) - Development workflow

---

## 🛠️ Development

### **Backend Development**
```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# API Documentation: http://localhost:8000/docs
```

### **Frontend Development**
```bash
cd frontend
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### **Full Stack Development**
```bash
# Start backend (Terminal 1)
cd backend && uvicorn app.main:app --reload

# Start frontend (Terminal 2)  
cd frontend && npm run dev

# Monitor health (Terminal 3)
.\automation\api-scripts\health-check.ps1 -All -Continuous
```

---

## 🚀 Deployment

### **Automated CI/CD** (GitHub Actions)
- **Trigger**: Push to `main` branch
- **Backend**: Auto-deploys to Fly.io (3 VMs, ~90 seconds build)
- **Frontend**: Auto-deploys to Cloudflare Pages (edge CDN)
- **Secrets**: Stored in Fly.io secrets + Cloudflare env vars
- **Logs**: `fly logs --app houserenovators-api --follow`

### **Manual Deployment**

#### Backend (Fly.io)
```bash
# Deploy from local machine
fly deploy --app houserenovators-api

# View deployment status
fly status --app houserenovators-api

# Stream logs
fly logs --app houserenovators-api --follow

# Set secrets
fly secrets set DATABASE_URL="postgresql://..." --app houserenovators-api
```

#### Frontend (Cloudflare Pages)
- Connected to GitHub `main` branch
- Auto-builds on push (Vite build)
- Environment: `VITE_API_URL=https://houserenovators-api.fly.dev`
- CDN: Global edge network

**See**: `docs/deployment/FLY_IO_DEPLOYMENT.md` for complete guide

### **Environment Variables**

Secrets are managed with **git-secret** and automatically decrypted from Git:

```bash
# Decrypt secrets (contains all required environment variables)
.\scripts\git-secret-wrapper.ps1 -Action reveal

# This creates:
# - .env (API keys, JWT secrets, QuickBooks credentials)
# - config/house-renovators-credentials.json (Google service account)
```

#### Backend Variables (.env):
```env
# Database (PostgreSQL via Supabase)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres

# Supabase Auth
SUPABASE_URL=https://dtfjzjhxtojkgfofrmrr.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_JWT_SECRET=your-jwt-secret

# OpenAI API
OPENAI_API_KEY=sk-proj-your_key

# QuickBooks OAuth2
QB_CLIENT_ID=your_client_id
QB_CLIENT_SECRET=your_client_secret
QB_REDIRECT_URI=https://houserenovators-api.fly.dev/v1/quickbooks/callback
QB_ENVIRONMENT=production

# App Settings
ENVIRONMENT=production
DEBUG=false
API_VERSION=v1
```

#### Frontend Variables (.env):
```env
# By default points to production backend
VITE_API_URL=https://houserenovators-api.fly.dev

# Supabase (public keys, safe to expose)
VITE_SUPABASE_URL=https://dtfjzjhxtojkgfofrmrr.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...

# Override in .env.local for local backend:
# VITE_API_URL=http://localhost:8000
```

**Note**: Backend `.env` encrypted with git-secret. Frontend `.env` contains only public values.

---

## 🤖 AI Features

### **Intelligent AI Assistant**
- **Smart Context Loading**: 90% fewer API calls via keyword-based data source detection
- **Database Integration**: Real-time access to PostgreSQL (clients, projects, permits, payments)
- **QuickBooks Integration**: Customer data, invoices, and payment status
- **Document Processing**: Upload PDFs/images to extract project/permit data with GPT-4 Vision
- **Natural Language**: Conversational interface for all operations
- **Session Memory**: TTL-based context (10-minute sessions, no database storage)
- **Zero Hallucinations**: Validated responses from actual data sources

### **Document Intelligence**
- 📄 **PDF Processing**: Extract text from permit documents and proposals
- 🖼️ **Image Analysis**: GPT-4 Vision analyzes photos of permits and plans
- ✏️ **Field Editing**: Review and edit AI-extracted data before creating records
- 🤖 **Smart Extraction**: Identifies permit numbers, dates, types, addresses, jurisdictions
- ✅ **One-Click Creation**: Confirm extraction and create database records instantly

### **Advanced Capabilities**
- **QuickBooks Operations**: Create invoices, sync payments, manage customers
- **Business ID Support**: Works with human-friendly IDs (CL-00001, PRJ-00001, etc.)
- **Multi-Entity Context**: Load clients + projects + permits + QB data in single query
- **Performance**: Sub-2-second responses for complex queries
- **Function Calling**: 15+ registered AI functions for operations

---

## 🔧 Development & Monitoring

### **Fly.io CLI Commands**
```bash
# Check app status
fly status --app houserenovators-api

# View logs (live stream)
fly logs --app houserenovators-api --follow

# Search logs
fly logs --app houserenovators-api | Select-String "ERROR|CRITICAL"

# SSH into VM
fly ssh console --app houserenovators-api

# Scale instances
fly scale count 3 --app houserenovators-api

# View secrets
fly secrets list --app houserenovators-api
```

### **Database Management**
```bash
# Direct PostgreSQL access (password-less after setup-pgpass.ps1)
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres"

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Check table structures
psql "postgresql://postgres@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres" -c "\dt"
```

### **Health Monitoring**
- **Backend Health**: https://houserenovators-api.fly.dev/health
- **API Docs**: https://houserenovators-api.fly.dev/docs
- **Fly.io Dashboard**: https://fly.io/apps/houserenovators-api

---

## 🤝 Contributing

### **Development Workflow**
1. Fork the repository
2. Create a feature branch (`feature/your-feature-name`)
3. Make your changes with clear commit messages
4. Test thoroughly (backend + frontend + integration)
5. Submit a pull request with description

### **Code Standards**
- **Backend**: PEP 8 for Python, type hints preferred
- **Frontend**: ESLint + Prettier, React best practices
- **Documentation**: Update `/docs` per governance policy
- **Testing**: Add tests for new features, maintain >90% coverage
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)

---

## 📞 Support & Resources

### **Getting Help**
- 📖 [**Troubleshooting Guide**](docs/guides/TROUBLESHOOTING.md) - Common issues & solutions
- 🔍 [**API Documentation**](docs/guides/API_DOCUMENTATION.md) - Complete API reference
- 🤖 [**Copilot Instructions**](.github/copilot-instructions.md) - AI development guidance
- 💬 GitHub Issues - Bug reports and feature requests

### **Key Resources**
- **Docs Hub**: `docs/README.md` - Complete documentation index
- **Setup**: `docs/setup/SETUP_GUIDE.md` - Environment configuration
- **QuickBooks**: `docs/guides/QUICKBOOKS_GUIDE.md` - Integration guide
- **Testing**: `docs/guides/CHAT_TESTING_SOP.md` - Testing procedures

---

## 🎯 System Status (December 13, 2025)

| Component | Status | Platform | Details |
|-----------|--------|----------|---------|
| **Backend API** | ✅ Production | Fly.io | https://houserenovators-api.fly.dev |
| **Frontend PWA** | ✅ Production | Cloudflare | https://portal.houserenovatorsllc.com |
| **Database** | ✅ Operational | Supabase | PostgreSQL 15, 8 tables, async ORM |
| **Authentication** | ✅ Active | Supabase Auth | JWT verification, route-level protection |
| **QuickBooks** | ✅ Connected | OAuth2 Prod | 24+ customers, 53+ invoices, auto-sync |
| **AI Engine** | ✅ Working | OpenAI | GPT-4o, smart context, 90% fewer calls |
| **Business IDs** | ✅ Implemented | PostgreSQL | CL-00001, PRJ-00001, PER-00001, PAY-00001 |

### 📅 **Recent Milestones**

**December 13, 2025** - Documentation Audit & Governance
- ✅ Copilot instructions audited (60% → 95% accuracy)
- ✅ Documentation organized per governance policy
- ✅ All misplaced files moved to proper `/docs` folders

**December 11, 2025** - PostgreSQL Migration Complete
- ✅ Migrated all operational data from Google Sheets to PostgreSQL
- ✅ 8 clients, 13 projects, 9 permits, 1 payment migrated
- ✅ Business IDs implemented (CL-00001, PRJ-00001, etc.)
- ✅ AI context loading updated to use `db_service`
- ✅ 80% performance improvement on database operations

**December 10, 2025** - Supabase Auth Integration
- ✅ Replaced custom JWT with Supabase Auth
- ✅ Route-level protection via `Depends(get_current_user)`
- ✅ Frontend updated with Supabase SDK
- ✅ User management via `/v1/auth/supabase/*` endpoints

**November 10, 2025** - Payments Feature Launch
- ✅ New `/v1/payments` API with full CRUD
- ✅ QuickBooks payment sync functionality
- ✅ AI function handlers for payment operations
- ✅ 11/12 integration tests passed (91.7%)

---

## 📄 License

This project is proprietary software developed for House Renovators LLC.

---

<div align="center">

**Built with ❤️ for construction professionals**

**Last Updated:** December 13, 2025

[🚀 Live App](https://portal.houserenovatorsllc.com) • [📖 Documentation](docs/) • [🤖 API Docs](https://houserenovators-api.fly.dev/docs)

</div>
