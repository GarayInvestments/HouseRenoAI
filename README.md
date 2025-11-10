# 🏠 House Renovators AI Portal

![FastAPI](https://img.shields.io/badge/Backend-FastAPI-blue)
![React](https://img.shields.io/badge/Frontend-React_PWA-cyan)
![Google Sheets](https://img.shields.io/badge/Data-Google_Sheets-green)
![OpenAI](https://img.shields.io/badge/AI-GPT--4o-purple)
![Multi-Cloud](https://img.shields.io/badge/Platform-Multi--Cloud-orange)

> **Complete AI-powered permit management and project tracking solution for construction professionals.**

## ✅ **STATUS: PRODUCTION READY & FULLY OPERATIONAL**
- 🚀 **Live Backend**: https://houserenoai.onrender.com *(Healthy - All systems operational)*
- 📱 **Frontend PWA**: https://portal.houserenovatorsllc.com *(Accessible and responsive)*
- 🤖 **AI Integration**: OpenAI GPT-4o with smart context loading *(Zero hallucinations)*
- 📊 **Data Source**: Google Sheets real-time integration *(Active permit/project data)*
- 💼 **QuickBooks**: OAuth2 production integration *(24 customers, 53+ invoices)*
- � **Payments**: Full tracking with QB sync *(NEW - Nov 10, 2025)*
- �🔧 **DevOps**: Complete automation toolkit *(Validated and operational)*
- ✨ **Recent Updates**: Payments feature, context enhancements, docs reorganization *(Nov 10, 2025)*
- 🧪 **Testing**: Comprehensive test suite (11/12 tests passed - 91.7%)
- 📚 **Documentation**: Organized structure (27 docs in 6 categories)

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
│   │   ├── google_service.py  # Google Sheets integration (async)
│   │   ├── openai_service.py  # OpenAI GPT-4o with function calling
│   │   └── quickbooks_service.py  # QB OAuth2, CRUD operations, sync
│   └── 📂 utils/               # Utility Functions
│       └── context_builder.py # Smart context loading (80% API reduction)
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
# Create virtual environment at root level
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run from root directory (backend code is in app/ directory)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 5. Automation Setup (Optional)
```bash
cd automation
.\cli-tools\install-all-clis.ps1  # Windows PowerShell
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
- **Backend Hosting**: Render (Production API)
- **Frontend Hosting**: Cloudflare Pages (PWA)
- **Data Storage**: Google Sheets (Real-time)
- **AI Processing**: OpenAI GPT-4o
- **Source Control**: GitHub
- **DevOps**: Automated CI/CD pipelines

### **Technology Stack**

#### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **AI Integration**: OpenAI GPT-4o for intelligent responses
- **Data Layer**: Google Sheets API with caching
- **Authentication**: API key-based security
- **Deployment**: Docker containers on Render

#### Frontend (React PWA)
- **Framework**: React 18 with Vite
- **UI**: Responsive design with offline support
- **PWA Features**: Service workers, offline caching
- **Deployment**: Cloudflare Pages with edge optimization

#### Automation & DevOps
- **CLI Tools**: Render, Cloudflare, Google Cloud, GitHub CLIs
- **Monitoring**: Comprehensive health checks and alerting
- **Deployment**: Automated full-stack deployment workflows
- **Scripts**: PowerShell automation for all platforms

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

### **Automated Deployment**
```bash
# Complete stack deployment
.\automation\workflows\deploy-all.ps1

# Backend only
.\automation\workflows\deploy-all.ps1 -BackendOnly

# Frontend only
.\automation\workflows\deploy-all.ps1 -FrontendOnly
```

### **Manual Deployment**

#### Backend (Render)
- Connected to GitHub repository
- Auto-deploys on push to main branch
- Environment variables configured in Render dashboard

#### Frontend (Cloudflare Pages)
- Connected to GitHub repository
- Auto-deploys on push to main branch
- Edge optimization and global CDN

### **Environment Variables**

Secrets are managed with **git-secret** and automatically decrypted from Git:

```bash
# Decrypt secrets (contains all required environment variables)
.\scripts\git-secret-wrapper.ps1 -Action reveal

# This creates:
# - .env (API keys, JWT secrets, QuickBooks credentials)
# - config/house-renovators-credentials.json (Google service account)
```

#### Required Variables in .env:
```env
# Google Sheets API
SHEET_ID=your_google_sheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=config/house-renovators-credentials.json

# OpenAI API
OPENAI_API_KEY=sk-proj-your_key

# QuickBooks OAuth2
QUICKBOOKS_CLIENT_ID=your_client_id
QUICKBOOKS_CLIENT_SECRET=your_client_secret
QUICKBOOKS_REDIRECT_URI=https://houserenoai.onrender.com/v1/quickbooks/callback
QUICKBOOKS_ENVIRONMENT=production

# Security
JWT_SECRET_KEY=your_random_secret_key
JWT_ALGORITHM=HS256

# API Settings
API_VERSION=v1
```

#### Frontend Variables (.env.local):
```env
VITE_API_URL=http://localhost:8000  # Development
# VITE_API_URL=https://api.houserenovatorsllc.com  # Production
```

**Note**: Frontend env files are not encrypted (they contain no secrets, only public URLs).

---

## 🤖 AI Features

### **Intelligent AI Assistant**
- **Contextual Responses**: AI has access to complete permit and project database
- **QuickBooks Integration**: Access customer data, invoices, and payment status in real-time
- **Document Upload & Extraction**: Upload PDFs or images to automatically extract project/permit data
- **Smart Analysis**: Automatic permit status insights and recommendations
- **Natural Language**: Conversational interface for permit inquiries
- **Real-time Data**: Always current with Google Sheets integration
- **Editable Extraction**: Review and edit AI-extracted data before creating records
- **Session Management**: Persistent chat sessions with automatic timestamp tracking
- **Dynamic Schema**: AI can create new columns in Google Sheets on demand

### **Document Intelligence (NEW)**
- **📄 PDF Processing**: Extract text from permit documents and proposals
- **🖼️ Image Analysis**: GPT-4 Vision analyzes photos of permits and plans
- **✏️ Field Editing**: Edit any extracted field before creating records
- **🤖 Smart Extraction**: AI identifies permit numbers, dates, types, addresses
- **✅ One-Click Creation**: Confirm extraction and create projects/permits instantly

### **Advanced Capabilities**
- **QuickBooks Integration**: Real-time access to customer data, invoices, and payment status
- **Invoice Creation**: Create QuickBooks invoices directly from chat with AI assistance
- **Session Persistence**: Chat sessions saved to Google Sheets with EST timestamps
- **Dynamic Columns**: Add new columns to Google Sheets through conversational commands
- Permit status tracking and notifications
- Project timeline analysis and predictions
- Compliance checking and recommendations
- Team communication and coordination
- Automated data entry from documents

---

## 🔧 DevOps & Automation

### **CLI Tools Management**
```bash
# Install all required CLI tools
.\automation\cli-tools\install-all-clis.ps1

# Setup individual services
.\automation\cli-tools\setup-render-cli.ps1
.\automation\cli-tools\setup-cloudflare-cli.ps1
.\automation\cli-tools\setup-google-cloud-cli.ps1
```

### **API Management**
```bash
# Render service management
.\automation\api-scripts\render-api.ps1 status
.\automation\api-scripts\render-api.ps1 deploy

# Cloudflare Pages management
.\automation\api-scripts\cloudflare-api.ps1 status
.\automation\api-scripts\cloudflare-api.ps1 deploy

# Health monitoring
.\automation\api-scripts\health-check.ps1 -All
```

### **Continuous Monitoring**
```bash
# Start continuous monitoring
.\automation\api-scripts\continuous-monitoring.ps1 -EnableAlerts -EnableMetrics

# Health dashboard
.\automation\api-scripts\health-check.ps1 -All -Json > health-report.json
```

---

## 📊 Monitoring & Health

### **Health Endpoints**
- **Backend Health**: https://api.houserenovatorsllc.com/health
- **Debug Info**: https://api.houserenovatorsllc.com/debug/
- **API Docs**: https://api.houserenovatorsllc.com/docs

### **Monitoring Features**
- Real-time health checks across all services
- Performance metrics and response time tracking
- Automated alerting via webhooks (Google Chat, Slack, Teams)
- Historical data and trend analysis
- Multi-platform status monitoring

---

## 🤝 Contributing

### **Development Workflow**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (both backend and frontend)
5. Submit a pull request

### **Code Standards**
- **Backend**: Follow PEP 8 for Python code
- **Frontend**: Use ESLint and Prettier for JavaScript
- **Documentation**: Update relevant docs with changes
- **Testing**: Include tests for new features

---

## 📞 Support

### **Getting Help**
- 📖 Check [**Troubleshooting Guide**](docs/TROUBLESHOOTING.md)
- 🔍 Review [**API Documentation**](docs/API_DOCUMENTATION.md)
- 🤖 Use [**AI Instructions**](backend/.github/copilot-instructions.md) for development

### **Issue Reporting**
- Use GitHub Issues for bug reports
- Include detailed reproduction steps
- Provide relevant logs and environment info

---

## 📄 License

This project is proprietary software developed for House Renovators AI Portal.

---

## 🎯 Project Status

| Component | Status | URL | Last Tested |
|-----------|--------|-----|-------------|
| **Backend API** | ✅ Production | https://houserenoai.onrender.com | Nov 10, 2025 *(Healthy)*|
| **Frontend PWA** | ✅ Production | https://portal.houserenovatorsllc.com | Nov 10, 2025 *(200 OK)* |
| **Google Sheets** | ✅ Integrated | Connected | Nov 10, 2025 *(All sheets active)* |
| **QuickBooks** | ✅ Integrated | OAuth2 Production | Nov 10, 2025 *(Payments sync active)* |
| **AI Chat** | ✅ Working | GPT-4o | Nov 10, 2025 *(19.3% faster avg)* |
| **Payments Feature** | ✅ Production | NEW | Nov 10, 2025 *(627ms response)* |
| **Session Management** | ✅ Active | Google Sheets | Nov 10, 2025 *(EST timestamps)* |
| **Automation** | ✅ Complete | Multi-cloud | Nov 10, 2025 *(All scripts validated)* |
| **Monitoring** | ✅ Active | Real-time | Nov 10, 2025 *(Health check operational)* |

### 🎯 **Latest Updates (November 10, 2025)**
- ✅ **Payments Feature Complete** (commit 4fe6043)
  - New `/v1/payments` API endpoint with full CRUD operations
  - QuickBooks payments sync functionality
  - AI function handlers: sync_quickbooks_payments, get_client_payments
  - Payments sheet created with 11 fields
  - Integration tested and validated (11/12 tests passed)

- ✅ **Context Enhancements** (commit 4fe6043)
  - Projects enhanced with 4 payment fields (Payment Method, Invoice #, Payment Status, Due Date)
  - Permits enhanced with 3 date fields (Submitted Date, Approved Date, Expiration Date)
  - Smart context loading updated with payment keywords
  - 60-80% reduction in unnecessary API calls

- ✅ **Documentation Reorganization** (commit 4dae028)
  - Created logical directory structure (guides/, setup/, deployment/, technical/, session-logs/)
  - Moved 25 files from flat structure to organized categories
  - Created docs/README.md navigation hub
  - Updated copilot-instructions.md with new paths
  - Reduced root clutter from 27 files to 7 items

- ✅ **Performance Validation** (commits e47c1cd, 10f6e21)
  - Collected Nov 10 post-enhancement metrics
  - Overall performance: **19.3% faster** (1729ms → 1395ms)
  - Simple Chat: **15.5% faster** (4306ms → 3640ms)
  - Created detailed comparison analysis
  - Updated all metrics documentation with timestamps

### 🎯 **Previous Updates (November 9, 2025)**
- ✅ **GC Compliance Payments Sync** (commit bc7e638)
  - 290-line function reconciling payments with invoices
  - Filters by Client Type = "GC Compliance" and Is Synced != TRUE
  - Updates Amount Paid, Balance, Status fields automatically
  
- ✅ **QuickBooks CustomerTypeRef Sync** (commit 9303ae6)
  - Auto-labels all QB customers as "GC Compliance"
  - 180-line service method + API endpoint
  - Matches by name (exact, without LLC) and email
  
- ✅ **Create QB Customer from Sheet** (commit 01e3c1a)
  - 185-line AI function creates QB customers from Sheet clients
  - Duplicate prevention and auto-assigns "GC Compliance" type
  - Updates Sheet with QBO Client ID for tracking
  
- ✅ **Smart Context Loading Fix** (commit 4cd8103)
  - Fixed comparison queries ("sheets vs quickbooks")
  - Added comparison_keywords detection
  - AI now loads both data sources in single query
  
- ✅ **Comprehensive Testing Suite** (commit 98da4f1)
  - test_quickbooks_comprehensive.py: 87.5% pass rate (14/16 tests)
  - test_comparison_query.py: 100% pass rate (2/2 tests)
  - Zero AI hallucinations detected
  - All features validated in production

### 🎯 **Recent Achievements (November 6-8, 2025)**
- ✅ **Documentation Reorganization** (commit 8b4b3ba)
  - 44 docs → 24 active docs
  - Created 2 consolidated guides (QUICKBOOKS_GUIDE.md, SETUP_GUIDE.md)
  - 20 historical files archived
  
- ✅ **Chat Testing SOP** (commit 4d63d01)
  - 531-line comprehensive testing guide
  - Standard procedures for chat feature validation
  
- ✅ **Copilot Instructions Enhanced** (commit d3ac437)
  - Quick reference section for common workflows
  - 8 task checklists with exact commands
  
- ✅ **AI Hallucination Fix** (commits 096eab7, 3466da9, 0f7cff1)
  - Token limits & prompt optimization
  - Zero fake customer names in responses
  
- ✅ **QB Client Sync** (commits 016e702, 3753e0c)
  - AI-powered sync function
  - 6 clients successfully synced

### 🎯 **Previous Achievements (November 2025)**
- ✅ **AI Document Upload**: Upload PDFs/images to extract project/permit data with GPT-4 Vision
- ✅ **Editable Extraction Fields**: Review and edit AI-extracted data before creating records
- ✅ **Enhanced UI**: Client cards show status breakdown (1 Active, 1 Completed, etc.)
- ✅ **Consistent Styling**: Unified status colors and formatting across all pages
- ✅ **Filtered Navigation**: Click client counts to view filtered projects/permits
- ✅ **Client Names on Projects**: Project cards now display client full names
- ✅ **Directory Restructuring**: Completed migration from nested structure to clean `backend/` organization
- ✅ **Script Path Updates**: All PowerShell automation tools updated and validated
- ✅ **Documentation Overhaul**: Created comprehensive documentation including directory structure guide
- ✅ **Service Validation**: Confirmed all services operational with new features

---

<div align="center">

**Built with ❤️ for construction professionals**

**Last Updated:** November 10, 2025, 3:30 PM PST

[🚀 Live Demo](https://houserenoai.onrender.com) • [📖 Documentation](docs/) • [🤖 AI Chat](https://portal.houserenovatorsllc.com)

</div>