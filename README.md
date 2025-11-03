# House Renovators AI Portal - FastAPI Backend

This is the FastAPI backend for the House Renovators AI Portal, providing AI-powered permit management, project tracking, and team communication capabilities.

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

## 📋 API Endpoints

### Chat Endpoints
- `POST /v1/chat/` - Process chat messages with AI
- `GET /v1/chat/status` - Get chat system status

### Permit Endpoints
- `GET /v1/permits/` - Get all permits
- `GET /v1/permits/{permit_id}` - Get specific permit
- `PUT /v1/permits/{permit_id}` - Update permit
- `GET /v1/permits/search/` - Search permits
- `POST /v1/permits/analyze` - AI analysis of permits

### Health Endpoints
- `GET /` - Basic health check
- `GET /health` - Detailed health status

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `SHEET_ID` | Google Sheet ID | `1AbCdEf...` |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Service account file path | `service-account.json` |
| `CHAT_WEBHOOK_URL` | Google Chat webhook | `https://chat.googleapis.com/...` |
| `DEBUG` | Enable debug mode | `false` |
| `PORT` | Server port | `10000` |

### Google Service Account Setup

1. **Create Service Account**
   - Go to Google Cloud Console
   - Create new service account
   - Download JSON key file

2. **Enable APIs**
   - Google Sheets API
   - Google Drive API

3. **Share Google Sheet**
   - Share your Google Sheet with service account email
   - Grant Editor permissions

## 🏗️ Architecture

```
FastAPI Backend
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── routes/
│   │   ├── chat.py          # Chat endpoints
│   │   └── permits.py       # Permit management
│   └── services/
│       ├── openai_service.py    # OpenAI integration
│       └── google_service.py    # Google APIs
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── .env.template           # Environment template
```

## 🤖 AI Features

### Chat Processing
- Natural language query processing
- Context-aware responses
- Action detection and execution
- Integration with Google Sheets data

### Permit Analysis
- Automated permit status analysis
- Compliance checking
- Timeline assessment
- Report generation

### Notifications
- Automated Google Chat notifications
- Real-time status updates
- Team coordination messages

## 🔒 Security

- Environment-based configuration
- Google OAuth2 service account authentication
- CORS protection
- Input validation with Pydantic
- Error handling and logging

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

## 📞 Support

For issues or questions:
- Check logs in Render dashboard
- Review API documentation at `/docs`
- Verify environment variable configuration
- Test Google Sheets connectivity

## 🔄 Development Workflow

1. **Local Testing**
```bash
uvicorn app.main:app --reload
```

2. **API Testing**
```bash
curl -X POST "http://localhost:8000/v1/chat/" \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me recent permits"}'
```

3. **Deploy to Render**
```bash
git add .
git commit -m "Update API"
git push origin main
```

## 🌟 Next Steps

- [ ] Set up monitoring and alerting
- [ ] Implement rate limiting
- [ ] Add authentication middleware
- [ ] Create client SDK
- [ ] Set up CI/CD pipeline