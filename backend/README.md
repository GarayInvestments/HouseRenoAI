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
- 🤖 **AI Integration**: OpenAI GPT-4o with permit data context *(Connected and responding)*
- 📊 **Data Source**: Google Sheets real-time integration *(6 permits loaded)*
- 🔧 **DevOps**: Complete automation toolkit *(Validated and operational)*
- ✨ **Directory Structure**: Recently restructured for optimal organization *(Nov 2025)*

---

## 📁 Project Structure *(Recently Restructured - November 2025)*

```
HouseRenovators-api/
├── 📂 backend/                 # FastAPI Backend (Python) - Moved from nested structure
├── 📂 frontend/                # React PWA (JavaScript) - Moved from house-renovators-pwa/
├── 📂 automation/              # DevOps Automation Toolkit - Complete PowerShell suite
├── 📂 docs/                    # Project Documentation - Centralized and comprehensive
├── 📂 scripts/                 # Utility Scripts - Deployment and maintenance
├── 📂 config/                  # Configuration Files - API payloads and settings
└── 📄 README.md                # This file - Updated with restructuring progress
```

> **✅ Restructuring Complete**: Successfully moved from redundant nested directories to clean, organized structure. All automation tools tested and validated working with new paths.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (for backend)
- Node.js 18+ (for frontend)
- Git
- Visual Studio Code (recommended)

### 1. Clone Repository
```bash
git clone https://github.com/GarayInvestments/HouseRenoAI.git
cd HouseRenovators-api
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Automation Setup (Optional)
```bash
cd automation
.\cli-tools\install-all-clis.ps1  # Windows PowerShell
```

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
```bash
# Backend (.env)
OPENAI_API_KEY=your_openai_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
SHEET_ID=your_google_sheet_id

# Frontend (.env.local)
VITE_API_URL=https://houserenoai.onrender.com
```

---

## 🤖 AI Features

### **Intelligent Permit Assistant**
- **Contextual Responses**: AI has access to complete permit database
- **Smart Analysis**: Automatic permit status insights and recommendations
- **Natural Language**: Conversational interface for permit inquiries
- **Real-time Data**: Always current with Google Sheets integration

### **Advanced Capabilities**
- Permit status tracking and notifications
- Project timeline analysis and predictions
- Compliance checking and recommendations
- Team communication and coordination

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
- **Backend Health**: https://houserenoai.onrender.com/health
- **Debug Info**: https://houserenoai.onrender.com/debug/
- **API Docs**: https://houserenoai.onrender.com/docs

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
| **Backend API** | ✅ Production | https://houserenoai.onrender.com | Nov 3, 2025 *(Healthy - 360ms response)*|
| **Frontend PWA** | ✅ Production | https://portal.houserenovatorsllc.com | Nov 3, 2025 *(200 OK response)* |
| **Google Sheets** | ✅ Integrated | Connected | Nov 3, 2025 *(6 permits loaded - 1251ms)* |
| **AI Chat** | ✅ Working | GPT-4o | Nov 3, 2025 *(Responding - 2560ms)* |
| **Automation** | ✅ Complete | Multi-cloud | Nov 3, 2025 *(All scripts validated)* |
| **Monitoring** | ✅ Active | Real-time | Nov 3, 2025 *(Health check operational)* |

### 🎯 **Recent Achievements (November 2025)**
- ✅ **Directory Restructuring**: Completed migration from nested `house-renovators-ai/house-renovators-ai/` to clean `backend/` structure
- ✅ **Script Path Updates**: All PowerShell automation tools updated and validated with new directory structure
- ✅ **Documentation Overhaul**: Created comprehensive documentation including directory structure guide
- ✅ **Syntax Fixes**: Resolved PowerShell parameter issues in health check scripts
- ✅ **Service Validation**: Confirmed all services operational after restructuring
- ✅ **Performance Verification**: All endpoints responding within acceptable timeframes

---

<div align="center">

**Built with ❤️ for construction professionals**

[🚀 Live Demo](https://houserenoai.onrender.com) • [📖 Documentation](docs/) • [🤖 AI Chat](https://houserenoai.onrender.com/docs)

</div>