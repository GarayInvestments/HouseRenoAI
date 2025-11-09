# 🏠 House Renovators AI Portal

![FastAPI](https://img.shields.io/badge/Backend-FastAPI-blue)
![React](https://img.shields.io/badge/Frontend-React_PWA-cyan)
![Google Sheets](https://img.shields.io/badge/Data-Google_Sheets-green)
![OpenAI](https://img.shields.io/badge/AI-GPT--4o-purple)
![Multi-Cloud](https://img.shields.io/badge/Platform-Multi--Cloud-orange)

> **Complete AI-powered permit management and project tracking solution for construction professionals.**

## ✅ **STATUS: PRODUCTION READY & RESTRUCTURED**
- 🚀 **Live Backend**: https://houserenoai.onrender.com *(Healthy - All systems operational)*
- 📱 **Frontend PWA**: https://portal.houserenovatorsllc.com *(Accessible and responsive)*
- 🤖 **AI Integration**: OpenAI GPT-4o with full data context *(Connected and responding)*
- 📊 **Data Source**: Google Sheets real-time integration *(Active permit/project data)*
- 💼 **QuickBooks**: OAuth2 production integration *(24 customers, 52 invoices)*
- 🔧 **DevOps**: Complete automation toolkit *(Validated and operational)*
- ✨ **Recent Updates**: Invoice DocNumber updates, Phase 0 refactor prep complete *(Nov 8, 2025)*
- 🧪 **Testing**: 9 integration tests (99% coverage), CI automation active
- 📊 **Metrics**: Baseline collection in progress (Nov 8-10)

---

## 📁 Project Structure

```
HouseRenovators-api/
├── 📂 app/                     # FastAPI Backend Application (ACTIVE)
│   ├── config.py               # Configuration and environment variables
│   ├── main.py                 # FastAPI application entry point
│   ├── routes/                 # API endpoint routes
│   │   ├── chat.py            # AI chat endpoints
│   │   ├── clients.py         # Client management endpoints
│   │   ├── documents.py       # Document upload & AI extraction (NEW)
│   │   ├── permits.py         # Permit management endpoints
│   │   └── projects.py        # Project management endpoints
│   └── services/               # Core business logic
│       ├── google_service.py  # Google Sheets integration
│       └── openai_service.py  # OpenAI GPT-4 integration
├── 📂 frontend/                # React PWA Frontend Application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── lib/               # Utilities and API client
│   │   ├── pages/             # Main application pages
│   │   │   ├── AIAssistant.jsx  # Chat interface with document upload
│   │   │   ├── Clients.jsx      # Client list with status breakdown
│   │   │   ├── Projects.jsx     # Project list with filters
│   │   │   └── ...
│   │   └── stores/            # Zustand state management
│   ├── package.json
│   └── vite.config.js
├── 📂 backend/                 # Legacy backend directory (for reference)
├── 📂 docs/                    # Project Documentation
│   ├── API_DOCUMENTATION.md   # Complete API reference (UPDATED)
│   ├── DEPLOYMENT.md          # Production deployment guide
│   ├── PROJECT_SETUP.md       # Development setup (UPDATED)
│   ├── PROGRESS_REPORT_NOV_2025.md  # Latest progress report (NEW)
│   └── TROUBLESHOOTING.md     # Debug and solutions guide
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

### **Core Documentation**
- 📖 [**API Documentation**](docs/API_DOCUMENTATION.md) - Complete API reference
- 🚀 [**Deployment Guide**](docs/DEPLOYMENT.md) - Production deployment
- 🔧 [**Project Setup**](docs/PROJECT_SETUP.md) - Development environment
- 🩺 [**Troubleshooting**](docs/TROUBLESHOOTING.md) - Common issues and solutions

### **Architecture & Development**
- 📁 [**Directory Structure**](docs/directory-structure.md) - Project organization
- 🤖 [**AI Instructions**](backend/.github/copilot-instructions.md) - AI development guide
- 🔄 [**Implementation Progress**](docs/IMPLEMENTATION_PROGRESS.md) - Development status

### **DevOps & Automation**
- 🛠️ [**Automation Toolkit**](automation/README.md) - DevOps tools overview
- 📊 [**Monitoring Guide**](automation/api-scripts/health-check.ps1) - Health monitoring
- 🚀 [**Deployment Workflows**](automation/workflows/deploy-all.ps1) - Automated deployment

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
| **Backend API** | ✅ Production | https://houserenoai.onrender.com | Nov 8, 2025 *(Healthy)*|
| **Frontend PWA** | ✅ Production | https://portal.houserenovatorsllc.com | Nov 8, 2025 *(200 OK)* |
| **Google Sheets** | ✅ Integrated | Connected | Nov 8, 2025 *(Permits & Projects loaded)* |
| **QuickBooks** | ✅ Integrated | OAuth2 Production | Nov 8, 2025 *(24 customers, 52 invoices)* |
| **AI Chat** | ✅ Working | GPT-4o | Nov 8, 2025 *(QB context active)* |
| **Session Management** | ✅ Active | Google Sheets | Nov 8, 2025 *(EST timestamps)* |
| **Automation** | ✅ Complete | Multi-cloud | Nov 3, 2025 *(All scripts validated)* |
| **Monitoring** | ✅ Active | Real-time | Nov 3, 2025 *(Health check operational)* |

### 🎯 **Recent Achievements (November 8, 2025)**
- ✅ **Invoice DocNumber Updates**: Added support for updating QuickBooks invoice DocNumber field
- ✅ **Phase 0 Refactor Complete**: Comprehensive pre-refactor safety measures in place
  - 9 integration tests (99% coverage) validating all current chat handlers
  - GitHub Actions CI with automated testing and 95% coverage threshold
  - Backup script ready for pre-refactor snapshot (PowerShell automation)
  - Baseline metrics collection started (3-day production data gathering Nov 8-10)
  - Performance logging added to chat endpoint ([METRICS] prefix for Render logs)
- ✅ **Test Infrastructure**: Complete test suite with mock fixtures for Google Sheets, QuickBooks, and memory manager
- ✅ **Documentation**: PHASE_0_COMPLETE.md, NEXT_STEPS.md, BASELINE_METRICS.md, chat_refactor_plan.md
- ✅ **Regression Protection**: Critical test for today's DocNumber feature ensuring no future breaks
- ✅ **QuickBooks Integration**: Full OAuth2 production integration with customer and invoice access
- ✅ **QB Context Loading**: AI can access QB data (24 customers, 52 invoices) in chat responses
- ✅ **Invoice Creation**: Create QuickBooks invoices directly from AI chat interface
- ✅ **Session Management**: Persistent chat sessions with EST timestamps stored in Google Sheets
- ✅ **Session Deletion Fix**: Resolved race condition in concurrent session deletions
- ✅ **Dynamic Column Creation**: AI can add new columns to Google Sheets on user request
- ✅ **Mobile Responsive**: Collapsible sidebar, compact header, floating history button (<768px)
- ✅ **Variable Scope Fix**: Resolved QuickBooks service scope error for reliable data loading

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

[🚀 Live Demo](https://api.houserenovatorsllc.com) • [📖 Documentation](docs/) • [🤖 AI Chat](https://api.houserenovatorsllc.com/docs)

</div>