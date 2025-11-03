# 🚀 House Renovators AI Portal - DevOps Automation Toolkit

This directory contains the complete automation infrastructure for managing the multi-cloud House Renovators AI Portal deployment across **Render**, **Cloudflare Pages**, **Google Cloud**, **OpenAI**, and **GitHub**.

## 📁 Directory Structure

```
automation/
├── README.md                     # This file - automation overview
├── cli-tools/                    # CLI installation and configuration
│   ├── install-all-clis.ps1     # One-click CLI tool installation
│   ├── setup-render-cli.ps1     # Render CLI authentication
│   ├── setup-wrangler-cli.ps1   # Cloudflare Wrangler setup
│   ├── setup-gcloud-cli.ps1     # Google Cloud CLI setup
│   └── setup-github-cli.ps1     # GitHub CLI authentication
├── api-scripts/                  # Programmatic API integrations
│   ├── render-api.ps1           # Render REST API utilities
│   ├── cloudflare-api.ps1       # Cloudflare API utilities
│   ├── google-apis.ps1          # Google Sheets/Drive/Chat APIs
│   └── health-check.ps1         # Automated health verification
├── workflows/                    # Complete automation workflows
│   ├── deploy-all.ps1           # Full stack deployment
│   ├── test-all.ps1             # End-to-end testing
│   ├── monitor-health.ps1       # Continuous health monitoring
│   └── notify-team.ps1          # Team notification system
└── config/
    ├── .env.automation          # Automation-specific environment variables
    └── cli-config.json          # CLI tool configurations
```

## 🛠️ **CLI Tools Overview**

### **Platform Management**
| Platform | CLI Tool | Purpose | Installation |
|----------|----------|---------|--------------|
| **Render** | `@render-api/cli` | Backend deployment, logs, env vars | `npm install -g @render-api/cli` |
| **Cloudflare** | `wrangler` | Frontend PWA deployment, Workers | `npm install -g wrangler` |
| **Google Cloud** | `gcloud` | Service accounts, APIs, IAM | Download from Google |
| **GitHub** | `gh` | Repos, actions, CI/CD integration | `winget install GitHub.cli` |
| **OpenAI** | `openai` | GPT-4o testing, usage monitoring | `pip install openai` |

### **Development Tools**
| Tool | Purpose | Installation |
|------|---------|--------------|
| **Python** | FastAPI backend management | `uvicorn`, `pytest`, `pip` |
| **Node.js** | React PWA development | `npm`, `vite`, `npx` |
| **PowerShell** | Windows automation scripts | Built-in |
| **jq** | JSON parsing for API responses | `winget install jqlang.jq` |

## 🚀 **Quick Start**

### **1. Install All CLI Tools**
```powershell
.\automation\cli-tools\install-all-clis.ps1
```

### **2. Configure Authentication**
```powershell
# Set up all platform authentications
.\automation\cli-tools\setup-render-cli.ps1
.\automation\cli-tools\setup-wrangler-cli.ps1
.\automation\cli-tools\setup-gcloud-cli.ps1
.\automation\cli-tools\setup-github-cli.ps1
```

### **3. Deploy Complete Stack**
```powershell
# Deploy backend + frontend + notifications
.\automation\workflows\deploy-all.ps1
```

### **4. Monitor Health**
```powershell
# Continuous health monitoring
.\automation\workflows\monitor-health.ps1
```

## ⚙️ **API Integration Overview**

### **Backend Management (Render)**
```powershell
# Deploy backend via REST API
POST https://api.render.com/v1/services/{serviceId}/deploys

# Monitor deployment status
GET https://api.render.com/v1/services/{serviceId}/deploys

# Stream logs
GET https://api.render.com/v1/services/{serviceId}/logs
```

### **Frontend Management (Cloudflare)**
```powershell
# Deploy PWA via API
POST https://api.cloudflare.com/client/v4/accounts/{id}/pages/projects/{name}/deployments

# Manage environment variables
PATCH https://api.cloudflare.com/client/v4/accounts/{id}/pages/projects/{name}
```

### **Data Management (Google Cloud)**
```powershell
# Read permit data
GET https://sheets.googleapis.com/v4/spreadsheets/{sheetId}/values/{range}

# Send team notifications
POST https://chat.googleapis.com/v1/spaces/{spaceId}/messages
```

## 🔄 **Automation Workflows**

### **Complete Deployment Pipeline**
1. **Pre-Deploy Tests** - Lint code, verify environment variables
2. **Backend Deploy** - Render API deployment with health checks
3. **Frontend Deploy** - Cloudflare Pages deployment
4. **Post-Deploy Verification** - API health checks, data connectivity
5. **Team Notification** - Google Chat success/failure notifications

### **Continuous Monitoring**
1. **Health Checks** - `/health`, `/debug/`, permit data access
2. **Performance Monitoring** - Response times, error rates
3. **Uptime Tracking** - Service availability monitoring
4. **Alert System** - Automatic notifications for issues

### **Development Workflows**
1. **Local Testing** - Backend + frontend development servers
2. **API Testing** - Automated endpoint verification
3. **Integration Testing** - End-to-end workflow validation
4. **Performance Testing** - Load testing and optimization

## 📊 **Integration Examples**

### **Full Stack Deployment**
```powershell
# Complete deployment with verification
render deploys create srv-d44ak76uk2gs73a3psig --confirm
wrangler pages deploy dist --project-name=house-renovators-pwa
curl https://houserenoai.onrender.com/health | jq '.status'
curl -X POST $CHAT_WEBHOOK_URL -d '{"text": "✅ Deployment completed"}'
```

### **Health Monitoring**
```powershell
# Comprehensive health verification
$backendHealth = curl https://houserenoai.onrender.com/health | ConvertFrom-Json
$googleService = curl https://houserenoai.onrender.com/debug/ | ConvertFrom-Json
$permitData = curl https://houserenoai.onrender.com/v1/permits/ | ConvertFrom-Json

# Notify if any issues detected
if ($backendHealth.status -ne "healthy") {
    # Send alert to Google Chat
}
```

### **API Testing Automation**
```powershell
# Automated endpoint testing
$testResults = @()
$testResults += Test-Endpoint "https://houserenoai.onrender.com/health"
$testResults += Test-Endpoint "https://houserenoai.onrender.com/v1/permits/"
$testResults += Test-ChatEndpoint "How many permits are approved?"

# Generate test report
Generate-TestReport $testResults
```

## 🔐 **Security & Configuration**

### **Environment Variables**
- `RENDER_API_TOKEN` - Render API authentication
- `CLOUDFLARE_API_TOKEN` - Cloudflare API access
- `GOOGLE_APPLICATION_CREDENTIALS` - Google Cloud service account
- `GITHUB_TOKEN` - GitHub API access
- `OPENAI_API_KEY` - OpenAI API access

### **Authentication Setup**
Each CLI tool requires proper authentication:
- **Render CLI**: `render auth login`
- **Wrangler**: `wrangler auth login`
- **gcloud**: `gcloud auth login`
- **GitHub CLI**: `gh auth login`

## 📈 **Monitoring & Alerts**

### **Key Metrics**
- Backend uptime and response times
- Frontend deployment success rates
- Google Sheets API quota usage
- OpenAI API usage and costs
- Error rates and performance trends

### **Alert Conditions**
- Service downtime > 1 minute
- API response time > 5 seconds
- Google service initialization failures
- Deployment failures
- High error rates (>5%)

## 🎯 **Usage Examples**

### **Daily Operations**
```powershell
# Morning health check
.\automation\workflows\monitor-health.ps1

# Deploy updates
.\automation\workflows\deploy-all.ps1

# Evening performance report
.\automation\api-scripts\health-check.ps1 -GenerateReport
```

### **Troubleshooting**
```powershell
# Check all service statuses
.\automation\api-scripts\render-api.ps1 -GetServiceStatus
.\automation\api-scripts\cloudflare-api.ps1 -GetPagesStatus
.\automation\api-scripts\google-apis.ps1 -TestConnection

# Stream live logs
render logs srv-d44ak76uk2gs73a3psig --tail 100
```

### **Performance Optimization**
```powershell
# Test response times
.\automation\workflows\test-all.ps1 -PerformanceTest

# Monitor resource usage
.\automation\api-scripts\render-api.ps1 -GetMetrics
```

## 🚀 **Future Enhancements**

- **GitHub Actions Integration** - Automated CI/CD pipelines
- **Slack Notifications** - Alternative to Google Chat
- **Terraform Integration** - Infrastructure as Code
- **Docker Automation** - Container management
- **Load Testing** - Performance validation
- **Blue-Green Deployments** - Zero-downtime updates

---

**🎯 Quick Commands:**
- Install tools: `.\automation\cli-tools\install-all-clis.ps1`
- Deploy all: `.\automation\workflows\deploy-all.ps1`
- Monitor health: `.\automation\workflows\monitor-health.ps1`
- Check status: `.\automation\api-scripts\health-check.ps1`

**📞 Support:** See individual script files for detailed usage and troubleshooting.