# House Renovators AI Portal - Documentation

Welcome to the House Renovators AI documentation. This guide will help you navigate all available documentation resources.

## 🚀 Quick Start

**New to the project?** Start here:
1. **[Setup Guide](setup/SETUP_GUIDE.md)** - Complete environment setup instructions
2. **[Setup New Machine](setup/SETUP_NEW_MACHINE.md)** - Streamlined setup for new developers
3. **[Setup Quick Reference](setup/SETUP_QUICK_REFERENCE.md)** - Environment variables and quick commands

**Already set up?** Jump to:
- **[API Documentation](guides/API_DOCUMENTATION.md)** - Complete API reference
- **[QuickBooks Guide](guides/QUICKBOOKS_GUIDE.md)** - OAuth2, API usage, sync features
- **[Workflow Guide](guides/WORKFLOW_GUIDE.md)** - Daily development workflow and git patterns

## 📁 Documentation Structure

### 📖 [Guides](guides/)
Comprehensive guides for using and maintaining the platform:
- **[API_DOCUMENTATION.md](guides/API_DOCUMENTATION.md)** - Complete API reference with examples
- **[QUICKBOOKS_GUIDE.md](guides/QUICKBOOKS_GUIDE.md)** - QuickBooks OAuth2, API, sync, troubleshooting
- **[TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)** - Common issues and solutions
- **[CHAT_TESTING_SOP.md](guides/CHAT_TESTING_SOP.md)** - Testing chat features, log monitoring
- **[FIELD_MAPPING.md](guides/FIELD_MAPPING.md)** - Google Sheets column mappings
- **[WORKFLOW_GUIDE.md](guides/WORKFLOW_GUIDE.md)** - Daily development workflow and git patterns

### ⚙️ [Setup](setup/)
Environment setup and configuration:
- **[SETUP_GUIDE.md](setup/SETUP_GUIDE.md)** - Comprehensive dev environment setup
- **[SETUP_NEW_MACHINE.md](setup/SETUP_NEW_MACHINE.md)** - Quick setup for new developers
- **[SETUP_QUICK_REFERENCE.md](setup/SETUP_QUICK_REFERENCE.md)** - Environment variables and quick commands
- **[GIT_SECRET_SETUP.md](setup/GIT_SECRET_SETUP.md)** - GPG-based secrets encryption

### 🚀 [Deployment](deployment/)
Deployment guides and operations:
- **[DEPLOYMENT.md](deployment/DEPLOYMENT.md)** - Render and Cloudflare deployment process
- **[RENDER_API_DEPLOYMENT_GUIDE.md](deployment/RENDER_API_DEPLOYMENT_GUIDE.md)** - Programmatic deployments via Render API
- **[RENDER_LOGS_GUIDE.md](deployment/RENDER_LOGS_GUIDE.md)** - Log access and monitoring

### 🔧 [Technical](technical/)
Technical specifications and design documents:
- **[GOOGLE_SHEETS_STRUCTURE.md](technical/GOOGLE_SHEETS_STRUCTURE.md)** - Sheets structure and field definitions
- **[GOOGLE_SHEETS_API_ACCESS.md](technical/GOOGLE_SHEETS_API_ACCESS.md)** - API access patterns and best practices
- **[PAYMENTS_FEATURE_DESIGN.md](technical/PAYMENTS_FEATURE_DESIGN.md)** - Payments feature implementation details
- **[CONTEXT_ENHANCEMENT_PROGRESS.md](technical/CONTEXT_ENHANCEMENT_PROGRESS.md)** - Context loading optimization progress
- **[LOGGING_SECURITY.md](technical/LOGGING_SECURITY.md)** - Security logging patterns and monitoring
- **[BASELINE_METRICS.md](technical/BASELINE_METRICS.md)** - Performance benchmarks
- **[metrics/](technical/metrics/)** - Performance metrics and baselines

### 📝 [Session Logs](session-logs/)
Development session summaries and progress reports:
- **[SESSION_SUMMARY_NOV_10_2025.md](session-logs/SESSION_SUMMARY_NOV_10_2025.md)** - Latest session summary

### 📦 [Archive](archive/)
Historical documentation and deprecated guides (17 files):
- Old implementation summaries, completed phase docs, deprecated test results

## 🎯 Common Tasks

### Setting Up a New Development Environment
1. Read [SETUP_GUIDE.md](setup/SETUP_GUIDE.md) for comprehensive instructions
2. Configure secrets with [GIT_SECRET_SETUP.md](setup/GIT_SECRET_SETUP.md)
3. Reference [SETUP_QUICK_REFERENCE.md](setup/SETUP_QUICK_REFERENCE.md) for environment variables

### Testing the Chat Feature
1. Follow procedures in [CHAT_TESTING_SOP.md](guides/CHAT_TESTING_SOP.md)
2. Use test scripts from `scripts/testing/chat-tests/`
3. Monitor logs with [RENDER_LOGS_GUIDE.md](deployment/RENDER_LOGS_GUIDE.md)

### Working with QuickBooks
1. Complete reference in [QUICKBOOKS_GUIDE.md](guides/QUICKBOOKS_GUIDE.md)
2. Check auth status: `GET /v1/quickbooks/status`
3. Connect if needed: Navigate to `/v1/quickbooks/connect`

### Deploying Changes
1. Follow [WORKFLOW_GUIDE.md](guides/WORKFLOW_GUIDE.md) for git patterns
2. Push to `main` branch (triggers auto-deploy)
3. Monitor with [RENDER_API_DEPLOYMENT_GUIDE.md](deployment/RENDER_API_DEPLOYMENT_GUIDE.md)

### Troubleshooting Issues
1. Check [TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md) for common issues
2. Review [RENDER_LOGS_GUIDE.md](deployment/RENDER_LOGS_GUIDE.md) for log access
3. Verify field mappings in [FIELD_MAPPING.md](guides/FIELD_MAPPING.md)

## 🏗️ Architecture Overview

**Multi-Cloud Full-Stack App:**
- **Backend**: FastAPI on Render (auto-deploy from `main`)
- **Frontend**: React 19 + Vite on Cloudflare Pages (auto-deploy from `main`)
- **Data Layer**: Google Sheets API (all data operations are async API calls)
- **Integration**: QuickBooks OAuth2 for invoice/payment sync

**Key Services:**
- `google_service` - Sheets API operations
- `quickbooks_service` - QB OAuth2 and API
- `openai_service` - AI chat with smart context loading
- `auth_service` - JWT authentication

## 📚 Additional Resources

- **API Routes**: `/v1/auth/*`, `/v1/chat`, `/v1/clients`, `/v1/projects`, `/v1/permits`, `/v1/documents`, `/v1/quickbooks/*`, `/v1/payments`
- **Test Scripts**: `scripts/testing/chat-tests/`
- **Setup Scripts**: `scripts/setup/`
- **Metrics Collection**: `scripts/collect_metrics.py`

## 🤝 Contributing

When adding new documentation:
1. Place in appropriate category directory (guides/, setup/, deployment/, technical/, session-logs/)
2. Update this README.md with a link to your new document
3. Follow existing documentation patterns and formatting
4. Keep session summaries in `session-logs/` for historical tracking

---

**Last Updated**: November 10, 2025
**Documentation Version**: 2.0 (Organized Structure)
