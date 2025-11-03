# House Renovators AI Portal - FastAPI Backend

![FastAPI](https://img.shields.io/badge/FastAPI-0.103.0-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Google Sheets](https://img.shields.io/badge/Google_Sheets-API-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-purple)
![Render](https://img.shields.io/badge/Hosting-Render-orange)

This is the FastAPI backend for the House Renovators AI Portal, providing AI-powered permit management, project tracking, and team communication capabilities with **full Google Sheets integration**.

## ✅ **STATUS: PRODUCTION READY**
- ✅ Google Sheets integration **WORKING**
- ✅ AI chat with permit data access **WORKING**  
- ✅ Permit CRUD operations **WORKING**
- ✅ Real-time analysis and insights **WORKING**
- ✅ Deployed at: https://houserenoai.onrender.com

## 🚀 Quick Start

### Local Development

1. **Clone and Setup**
```bash
cd house-renovators-ai
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.template .env
# Edit .env with your actual API keys and configuration
```

3. **Add Google Service Account**
```bash
# Place your service-account.json file in the root directory
```

4. **Run the Application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 🔧 Automation Scripts (Available in Root Project)
For streamlined setup and deployment, reference these automation scripts:
- **[setup-portal.ps1](../../setup-portal.ps1)** - Complete portal setup and environment configuration
- **[deploy-backend.ps1](../../deploy-backend.ps1)** - Automated backend deployment to Render
- **[deploy-frontend.ps1](../../deploy-frontend.ps1)** - Automated frontend deployment to Cloudflare Pages

5. **Access API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🌐 Deployment to Render

### Automatic Deployment

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial FastAPI backend"
git remote add origin https://github.com/yourusername/house-renovators-ai.git
git push -u origin main
```

2. **Deploy on Render**
- Go to [Render.com](https://render.com)
- Create New → Web Service
- Connect your GitHub repository
- Configure build settings:
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`

3. **Environment Variables**
Add these in Render's Environment tab:
```
OPENAI_API_KEY=sk-your-key
SHEET_ID=your-sheet-id
CHAT_WEBHOOK_URL=your-webhook-url
DEBUG=false
PORT=10000
```

4. **Upload Service Account**
- Use Render's "Secret Files" feature
- Upload your `service-account.json`

## 📋 API Endpoints - **ALL WORKING ✅**

### **Permit Management** 
- ✅ `GET /v1/permits/` - Get all permits from Google Sheets *(6+ permits loaded)*
- ✅ `GET /v1/permits/{permit_id}` - Get specific permit details
- ✅ `PUT /v1/permits/{permit_id}` - Update permit with team notifications
- ✅ `GET /v1/permits/search/?query=approved` - Search permits with filters
- ✅ `POST /v1/permits/analyze` - AI analysis with insights and recommendations

### **AI Chat Integration**
- ✅ `POST /v1/chat/` - Process natural language queries with permit data access
- ✅ `GET /v1/chat/status` - Service health: OpenAI + Google Sheets connectivity

### **System Health**
- ✅ `GET /` - Basic API health check
- ✅ `GET /health` - Comprehensive service status
- ✅ `GET /debug/` - Google service initialization status

## 🔥 **Live API Examples**

### Chat with Permit Data
```bash
curl -X POST "https://houserenoai.onrender.com/v1/chat/" \
     -H "Content-Type: application/json" \
     -d '{"message": "How many permits are currently approved?"}'

# Response: "Out of the recent permits, four are currently approved..."
```

### Get All Permits  
```bash
curl "https://houserenoai.onrender.com/v1/permits/"
# Returns: Real permit data from Google Sheets
```

### AI Analysis
```bash
curl -X POST "https://houserenoai.onrender.com/v1/permits/analyze"
# Returns: Detailed analysis with missing approvals, timeline insights, next steps
```

## 🔧 Configuration - **FULLY CONFIGURED ✅**

### Required Environment Variables *(All Set)*

| Variable | Description | Status | Example |
|----------|-------------|--------|---------|
| `GOOGLE_CREDENTIALS_B64` | Base64 encoded service account | ✅ SET | `eyJ0eXBlI...` |
| `OPENAI_API_KEY` | OpenAI API key | ✅ SET | `sk-...` |
| `SHEET_ID` | Google Sheet ID | ✅ SET | `1AbCdEf...` |
| `CHAT_WEBHOOK_URL` | Google Chat webhook | ✅ SET | `https://chat.googleapis.com/...` |
| `DEBUG` | Enable debug mode | ✅ SET | `false` |
| `PORT` | Server port | ✅ SET | `10000` |

### Google Service Account Setup ✅ **COMPLETE**

1. **✅ Service Account Created**
   - Service account: `house-renovators-service@house-renovators-ai.iam.gserviceaccount.com`
   - JSON key file converted to base64 for Render deployment

2. **✅ APIs Enabled**
   - Google Sheets API - **WORKING**
   - Google Drive API - **WORKING**  

3. **✅ Google Sheet Shared**
   - Google Sheet shared with service account email
   - Editor permissions granted
   - **Real permit data being read successfully**

### **Authentication Status: WORKING** ✅
- Credentials properly created at startup
- Google services initialize after FastAPI startup event
- All API endpoints accessing Google Sheets successfully

## 🏗️ Architecture - **PRODUCTION READY**

### 📁 Project Structure

```
FastAPI Backend (✅ WORKING)
├── app/
│   ├── main.py              # FastAPI app with startup events ✅
│   ├── config.py            # Environment configuration ✅
│   ├── routes/
│   │   ├── chat.py          # AI chat + Google Sheets access ✅
│   │   └── permits.py       # Full permit CRUD operations ✅
│   └── services/
│       ├── openai_service.py    # OpenAI GPT integration ✅
│       └── google_service.py    # Google Sheets/Drive APIs ✅
├── requirements.txt         # Dependencies installed ✅
├── Dockerfile              # Container ready ✅
└── .env.template           # Environment template ✅
```

### 📚 Documentation Navigation
- 📘 [API Documentation](./API_DOCUMENTATION.md) - Complete endpoint reference with examples
- 🧰 [Troubleshooting Guide](./TROUBLESHOOTING.md) - Debug procedures and solutions
- 🚀 [Deployment Guide](./DEPLOYMENT.md) - Production deployment procedures
- 📋 [Project Setup](./PROJECT_SETUP.md) - Development environment setup

### **Key Architecture Decisions**
- **FastAPI Startup Events**: Google service initializes after credentials creation
- **Dynamic Import Pattern**: Routes access `google_service_module.google_service` to avoid stale references
- **Base64 Credential Transport**: Prevents JSON corruption in environment variables
- **Async/Await**: Non-blocking Google API operations
- **Error Handling**: Comprehensive exception handling with helpful error messages

## ⚡ Command-Line Tools

This project leverages multiple CLI tools for development and deployment automation:

### **Render CLI** - Backend Deployment
```bash
# Install Render CLI
npm install -g @render-api/cli

# Deploy backend service
render services create --name house-renovators-ai \
  --type web \
  --build-command "pip install -r requirements.txt" \
  --start-command "uvicorn app.main:app --host 0.0.0.0 --port 10000"

# Monitor deployments
render deploys list --service house-renovators-ai
render logs --service house-renovators-ai
```

### **Wrangler CLI** - Frontend Deployment (if using Cloudflare Pages)
```bash
# Install Wrangler CLI
npm install -g wrangler

# Deploy frontend to Cloudflare Pages
wrangler pages deploy dist --project-name house-renovators-pwa

# Monitor Pages deployments
wrangler pages deployment list
```

### **Google Cloud CLI** - Service Account Management
```bash
# Install Google Cloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# Authenticate and manage service accounts
gcloud auth login
gcloud iam service-accounts create house-renovators-service
gcloud iam service-accounts keys create service-account.json \
  --iam-account=house-renovators-service@PROJECT_ID.iam.gserviceaccount.com
```

## 🤖 AI Features - **FULLY OPERATIONAL ✅**

### **Chat Processing** ✅
- ✅ Natural language permit queries: *"How many permits are approved?"*
- ✅ Context-aware responses with real permit data
- ✅ Automatic data lookup when permit keywords detected  
- ✅ AI analysis with actionable insights

### **Permit Analysis** ✅  
- ✅ Automated status analysis: *4 approved, 1 under review, 1 pending*
- ✅ Missing data detection: *approval dates, file uploads*
- ✅ Timeline assessment: *average 1-day approval time*
- ✅ Next steps recommendations: *follow up on specific permits*

### **Real-Time Integration** ✅
- ✅ Live Google Sheets data access
- ✅ Google Chat webhook notifications 
- ✅ Team coordination messages
- ✅ Instant permit status updates

### **Sample AI Responses**
```json
{
  "summary": {
    "total_permits": 6,
    "approved_permits": 4,
    "under_review_permits": 1
  },
  "issues": {
    "missing_approval_dates": ["7f4f969c"],
    "missing_file_uploads": ["7f4f969c"]
  },
  "next_steps": {
    "for_under_review": "Follow up on permit 'cd7193a0'",
    "for_missing_uploads": "Complete file uploads for '7f4f969c'"
  }
}
```

## 🔒 Security - **PRODUCTION SECURE ✅**

- ✅ Base64 encoded credential transport (prevents JSON corruption)
- ✅ Google OAuth2 service account authentication
- ✅ Environment-based configuration (no hardcoded secrets)
- ✅ CORS protection configured
- ✅ Input validation with Pydantic models
- ✅ Comprehensive error handling and logging
- ✅ Service availability checks before API calls

## 📊 Monitoring

### Health Checks
- API endpoint health monitoring
- External service connectivity checks
- Performance metrics

### Logging
- Structured logging with Python logging
- Error tracking and debugging
- API request/response logging

## 🚀 Production Considerations

### Performance
- Async/await for non-blocking operations
- Connection pooling for external APIs
- Efficient data processing

### Scalability
- Stateless design
- Horizontal scaling capability
- Database connection management

### Reliability
- Comprehensive error handling
- Graceful degradation
- Health monitoring

## 📞 Support & Maintenance

### 📚 Documentation Resources
- 📘 **[API Documentation](./API_DOCUMENTATION.md)** - Complete endpoint reference with request/response examples
- 🧰 **[Troubleshooting Guide](./TROUBLESHOOTING.md)** - Debug procedures and common issue solutions  
- 🚀 **[Deployment Guide](./DEPLOYMENT.md)** - Production deployment and monitoring procedures
- 📋 **[Project Setup](./PROJECT_SETUP.md)** - Development environment configuration
- 🤖 **[AI Agent Instructions](./.github/copilot-instructions.md)** - Comprehensive guide for AI-assisted development

### 🔧 Support Channels
For issues or questions:
- Check logs in Render dashboard
- Review API documentation at `/docs`
- Verify environment variable configuration
- Test Google Sheets connectivity with `/debug/` endpoint

### 🔍 Health Monitoring
- **Service Status**: https://houserenoai.onrender.com/health
- **Google Integration**: https://houserenoai.onrender.com/debug/  
- **API Documentation**: https://houserenoai.onrender.com/docs
- **Render Dashboard**: Monitor deployment logs and performance metrics

## 🔄 Development Workflow - **TESTED & WORKING**

1. **Local Testing** ✅
```bash
uvicorn app.main:app --reload
# All endpoints tested and working locally
```

2. **API Testing Examples** ✅
```bash
# Test chat with permit data
curl -X POST "https://houserenoai.onrender.com/v1/chat/" \
     -H "Content-Type: application/json" \
     --data-binary '{"message": "Show me recent permits"}'

# Test permit retrieval  
curl "https://houserenoai.onrender.com/v1/permits/"

# Test AI analysis
curl -X POST "https://houserenoai.onrender.com/v1/permits/analyze"
```

3. **Deploy to Render** ✅
```bash
git add .
git commit -m "Update API with Google Sheets integration"
git push origin main
# Automatic deployment triggered
```

## 🌟 **COMPLETED FEATURES** ✅

- ✅ **Google Sheets Integration**: Service account authentication working
- ✅ **Real Permit Data**: 6+ permits loading from actual Google Sheet  
- ✅ **AI Chat**: Natural language queries with permit context
- ✅ **CRUD Operations**: Create, read, update permit data
- ✅ **Analysis Engine**: AI-powered insights and recommendations
- ✅ **Error Handling**: Comprehensive exception management
- ✅ **Production Deployment**: Live at https://houserenoai.onrender.com
- ✅ **Documentation**: API docs at /docs endpoint
- ✅ **Health Monitoring**: Status endpoints for service monitoring

## 🚀 **NEXT PHASE ROADMAP**

- [ ] Rate limiting and authentication middleware
- [ ] Webhook endpoints for Google Sheets changes
- [ ] Advanced permit workflow automation  
- [ ] Mobile app API extensions
- [ ] Advanced analytics dashboard
- [ ] Multi-project support
- [ ] Client portal integration

---

## 📝 License & Ownership

© 2025 House Renovators LLC — All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited. For licensing inquiries or partnership opportunities, please contact House Renovators LLC.

**Development Team**: AI-Powered Construction Management Solutions  
**Production Environment**: https://houserenoai.onrender.com  
**Last Updated**: November 3, 2025