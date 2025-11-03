# 🏗️ House Renovators AI Portal

> **Complete AI-powered permit management and project tracking system for House Renovators LLC**

A comprehensive solution combining **FastAPI backend** with **React PWA frontend**, featuring OpenAI integration, Google Sheets data management, and real-time team notifications.

---

## 🌟 Overview

The House Renovators AI Portal is a production-ready system designed for North Carolina licensed General Contractors to:

- **Automate permit management** with AI-powered processing
- **Track projects** from inception to completion
- **Ensure compliance** with NC building codes and regulations
- **Coordinate teams** through intelligent notifications
- **Generate reports** automatically using natural language queries

### 🏛️ Architecture

| Component | Technology | Deployment | Purpose |
|-----------|------------|------------|---------|
| **Backend API** | FastAPI + Python | Render.com | AI processing, data management |
| **Frontend PWA** | React + Vite | Cloudflare Pages | User interface, chat, dashboard |
| **Data Layer** | Google Sheets | Google Cloud | Permits, projects, clients data |
| **AI Engine** | OpenAI GPT-4 | API Integration | Natural language processing |
| **Notifications** | Google Chat | Webhook | Team communication |

---

## 🚀 Quick Start

### One-Click Setup

```powershell
# Clone and run the complete setup
.\setup-portal.ps1
```

### Manual Setup

1. **Backend Setup**
```bash
cd house-renovators-ai
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your API keys
uvicorn app.main:app --reload
```

2. **Frontend Setup**
```bash
cd house-renovators-pwa
npm install
npm run dev
```

### Access Points
- **Frontend PWA**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📁 Project Structure

```
house-renovators-portal/
├── house-renovators-ai/          # FastAPI Backend
│   ├── app/
│   │   ├── main.py               # FastAPI application
│   │   ├── config.py             # Configuration
│   │   ├── routes/               # API endpoints
│   │   │   ├── chat.py          # AI chat processing
│   │   │   └── permits.py       # Permit management
│   │   └── services/            # Core services
│   │       ├── openai_service.py # AI integration
│   │       └── google_service.py # Google APIs
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile               # Container config
│   └── README.md                # Backend documentation
│
├── house-renovators-pwa/         # React PWA Frontend
│   ├── src/
│   │   ├── components/          # UI components
│   │   │   ├── ChatBox.jsx      # AI chat interface
│   │   │   ├── Header.jsx       # Navigation
│   │   │   └── StatusIndicator.jsx # System status
│   │   ├── pages/
│   │   │   └── Dashboard.jsx    # Main dashboard
│   │   ├── utils/
│   │   │   └── api.js           # API client
│   │   └── App.jsx              # Main app
│   ├── public/
│   │   └── manifest.json        # PWA manifest
│   └── README.md                # Frontend documentation
│
├── deploy-backend.ps1            # Backend deployment script
├── deploy-frontend.ps1           # Frontend deployment script
├── setup-portal.ps1              # Complete setup script
└── README.md                     # This file
```

---

## 🔧 Configuration

### Required API Keys and Services

| Service | Required For | Configuration |
|---------|--------------|---------------|
| **OpenAI API** | AI chat processing | `OPENAI_API_KEY` |
| **Google Sheets API** | Data storage | Service account JSON |
| **Google Chat Webhook** | Team notifications | `CHAT_WEBHOOK_URL` |

### Environment Files

**Backend (.env)**
```bash
OPENAI_API_KEY=sk-your-openai-api-key
SHEET_ID=your-google-sheet-id
GOOGLE_SERVICE_ACCOUNT_FILE=service-account.json
CHAT_WEBHOOK_URL=your-google-chat-webhook
DEBUG=false
```

**Frontend (.env.production)**
```bash
VITE_API_URL=https://your-backend.onrender.com
VITE_ENV=production
VITE_ENABLE_DEBUG=false
```

---

## 🌐 Deployment

### Automated Deployment

```powershell
# Deploy backend to Render
.\deploy-backend.ps1

# Deploy frontend to Cloudflare Pages
.\deploy-frontend.ps1
```

### Production URLs

- **Frontend PWA**: `https://portal.houserenovatorsllc.com`
- **Backend API**: `https://house-renovators-ai.onrender.com`

### Deployment Targets

| Component | Platform | Features |
|-----------|----------|----------|
| **Backend** | Render.com | Auto-scaling, SSL, monitoring |
| **Frontend** | Cloudflare Pages | Global CDN, auto-builds, SSL |

---

## 🤖 AI Features

### Chat Interface
- **Natural Language Queries**: "Show me permits expiring this month"
- **Action Processing**: Automatic data updates based on conversation
- **Context Awareness**: Remembers conversation history
- **Error Handling**: Graceful degradation and helpful error messages

### Automated Processing
- **Permit Analysis**: AI-powered status assessment
- **Report Generation**: Natural language report creation
- **Data Validation**: Intelligent error detection
- **Compliance Checking**: NC building code verification

---

## 📊 Features

### Dashboard
- **Project Statistics**: Real-time metrics and KPIs
- **Recent Activity**: Latest permits and project updates
- **Quick Actions**: Common tasks and shortcuts
- **System Status**: Health monitoring and connectivity

### Permit Management
- **CRUD Operations**: Complete permit lifecycle management
- **Search & Filter**: Advanced querying capabilities
- **Status Tracking**: Real-time permit status updates
- **Compliance Monitoring**: Automated regulatory checks

### Team Coordination
- **Real-time Notifications**: Google Chat integration
- **Status Updates**: Automatic team alerts
- **Progress Tracking**: Project milestone monitoring
- **Communication Logs**: Complete audit trail

---

## 🔒 Security & Compliance

### Data Protection
- **Environment Variables**: Secure API key management
- **HTTPS Enforcement**: SSL/TLS encryption
- **CORS Configuration**: Cross-origin request protection
- **Input Validation**: SQL injection and XSS prevention

### Compliance Features
- **Audit Trails**: Complete activity logging
- **Data Retention**: Configurable retention policies
- **Access Controls**: Role-based permissions (planned)
- **Regulatory Alignment**: NC General Contractor standards

---

## 📱 PWA Features

### Mobile-First Design
- **Responsive Layout**: Works on all device sizes
- **Touch Optimized**: Mobile-friendly interactions
- **Offline Support**: Service worker caching
- **App Installation**: Native app-like experience

### Performance
- **Code Splitting**: Optimized bundle loading
- **Lazy Loading**: On-demand component loading
- **Caching Strategy**: Intelligent offline support
- **Fast Loading**: Sub-second initial loads

---

## 🛠️ Development

### Local Development

```bash
# Start development servers
.\setup-portal.ps1
# Select option 4 for development environment
```

### Testing

```bash
# Backend testing
cd house-renovators-ai
python -m pytest

# Frontend testing
cd house-renovators-pwa
npm test
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Chat API
curl -X POST http://localhost:8000/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me recent permits"}'
```

---

## 📈 Monitoring & Analytics

### Health Monitoring
- **API Uptime**: Continuous health checks
- **Response Times**: Performance monitoring
- **Error Tracking**: Automated error reporting
- **Usage Analytics**: User interaction metrics

### Business Intelligence
- **Project Metrics**: Completion rates and timelines
- **Permit Analytics**: Processing efficiency
- **Team Performance**: Communication and response metrics
- **Compliance Reports**: Regulatory adherence tracking

---

## 🔄 Roadmap

### Phase 1 (Current)
- ✅ Core AI chat functionality
- ✅ Permit management system
- ✅ Google Sheets integration
- ✅ PWA deployment

### Phase 2 (Planned)
- [ ] Advanced reporting dashboard
- [ ] Mobile app (React Native)
- [ ] Client portal access
- [ ] Document management

### Phase 3 (Future)
- [ ] Voice commands
- [ ] Advanced analytics
- [ ] Third-party integrations
- [ ] Multi-tenant support

---

## 💰 Cost Estimation

| Service | Monthly Cost | Notes |
|---------|--------------|--------|
| **Render (Backend)** | $7-15 | Based on usage |
| **Cloudflare Pages** | Free | With custom domain |
| **OpenAI API** | $10-40 | Based on usage |
| **Google Workspace** | Free | For Sheets/Chat APIs |
| **Total** | **$17-55** | Scales with usage |

---

## 📞 Support & Maintenance

### Troubleshooting
- Check API connectivity: `/health` endpoint
- Verify environment variables
- Review browser console logs
- Test Google Sheets permissions

### Updates
- Backend: Redeploy through Render dashboard
- Frontend: Auto-deploy through Cloudflare Pages
- Dependencies: Regular security updates

### Monitoring
- **Uptime**: Render and Cloudflare dashboards
- **Performance**: Lighthouse PWA audits
- **Errors**: Console logs and error tracking
- **Usage**: Analytics and API metrics

---

## 🎯 Mission Alignment

> "To uphold integrity, compliance, and excellence in every build — ensuring that every structure reflects skill, honesty, and responsibility before both clients and state standards."

The House Renovators AI Portal embodies this mission by:
- **Automating compliance** to prevent regulatory oversights
- **Ensuring transparency** through comprehensive logging
- **Improving efficiency** to focus on quality craftsmanship
- **Maintaining standards** through intelligent monitoring

---

## 🌟 Getting Started

1. **Run Setup**: `.\setup-portal.ps1`
2. **Configure APIs**: Update environment files
3. **Test Locally**: Verify all features work
4. **Deploy**: Use deployment scripts
5. **Monitor**: Set up health checks

**Questions?** Check the individual README files in each component directory for detailed instructions.

---

**House Renovators LLC** - Building Excellence Through Innovation