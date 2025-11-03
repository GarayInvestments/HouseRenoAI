# 📁 House Renovators AI Portal - Directory Structure Guide
# Updated structure after reorganization

## 🏗️ New Directory Structure

```
HouseRenovators-api/
├── 📂 backend/                 # FastAPI Backend Application
│   ├── 📁 .git/                # Git repository (moved from nested structure)
│   ├── 📁 .github/             # GitHub configuration and CI/CD
│   ├── 📁 app/                 # FastAPI application code
│   │   ├── 📁 routes/          # API route handlers
│   │   └── 📁 services/        # Business logic services
│   ├── 📄 .env                 # Environment variables (production)
│   ├── 📄 .env.template        # Environment template
│   ├── 📄 .gitignore          # Git ignore patterns
│   ├── 📄 requirements.txt    # Python dependencies
│   ├── 📄 Dockerfile          # Container configuration
│   ├── 📄 runtime.txt         # Python runtime specification
│   └── 📄 README.md           # Backend-specific documentation
│
├── 📂 frontend/                # PWA Frontend Application
│   ├── 📁 node_modules/        # Node.js dependencies
│   ├── 📁 public/              # Static assets
│   ├── 📁 src/                 # React/Vite source code
│   │   ├── 📁 components/      # React components
│   │   ├── 📁 pages/           # Page components
│   │   ├── 📁 utils/           # Utility functions
│   │   └── 📁 assets/          # Frontend assets
│   ├── 📄 package.json         # Node.js dependencies and scripts
│   ├── 📄 vite.config.js      # Vite configuration
│   └── 📄 index.html          # Entry HTML file
│
├── 📂 automation/              # DevOps Automation Toolkit
│   ├── 📁 cli-tools/           # CLI installation and setup scripts
│   │   ├── 📄 install-all-clis.ps1        # Install all CLI tools
│   │   ├── 📄 setup-render-cli.ps1        # Render CLI setup
│   │   ├── 📄 setup-cloudflare-cli.ps1    # Cloudflare CLI setup
│   │   ├── 📄 setup-google-cloud-cli.ps1  # Google Cloud CLI setup
│   │   └── 📄 setup-github-cli.ps1        # GitHub CLI setup
│   ├── 📁 api-scripts/         # API management utilities
│   │   ├── 📄 render-api.ps1              # Render service management
│   │   ├── 📄 cloudflare-api.ps1          # Cloudflare Pages management
│   │   ├── 📄 google-cloud-api.ps1        # Google Cloud operations
│   │   ├── 📄 github-api.ps1              # GitHub operations
│   │   ├── 📄 health-check.ps1            # Health monitoring
│   │   └── 📄 continuous-monitoring.ps1   # Continuous monitoring
│   ├── 📁 workflows/           # Deployment orchestration
│   │   ├── 📄 deploy-all.ps1              # Complete stack deployment
│   │   └── 📄 rollback.ps1               # Deployment rollback
│   └── 📄 README.md            # Automation documentation
│
├── 📂 docs/                    # Project Documentation
│   ├── 📄 API_DOCUMENTATION.md          # API reference
│   ├── 📄 DEPLOYMENT.md                 # Deployment guide
│   ├── 📄 TROUBLESHOOTING.md            # Troubleshooting guide
│   ├── 📄 PROJECT_SETUP.md              # Project setup instructions
│   ├── 📄 IMPLEMENTATION_PROGRESS.md    # Implementation status
│   ├── 📄 STATUS_SUMMARY.md             # Status summary
│   └── 📄 directory-structure.md        # This file
│
├── 📂 scripts/                 # Utility and deployment scripts
│   ├── 📄 deploy-backend.ps1            # Legacy backend deployment
│   ├── 📄 deploy-frontend.ps1           # Legacy frontend deployment
│   ├── 📄 setup-portal.ps1              # Portal setup script
│   └── 📄 simple-fix.py                 # Python utilities
│
├── 📂 config/                  # Configuration files
│   ├── 📄 cli-config.json               # CLI tool configuration
│   ├── 📄 base64_env_payload.json       # Environment payloads
│   ├── 📄 corrected-credentials.json    # Credential files
│   ├── 📄 GC_Permit_Compliance_Schema.json  # Data schema
│   └── 📄 house-renovators-credentials.json # Service credentials
│
├── 📄 README.md                # Main project documentation
├── 📄 .gitignore              # Git ignore patterns (project level)
└── 📄 house-renovators-ai_Workspace.code-workspace  # VS Code workspace
```

## 🔄 Migration Summary

### What Changed:
1. **Flattened Structure**: Removed redundant nested `house-renovators-ai/house-renovators-ai/` directory
2. **Clear Separation**: Backend and frontend now in separate top-level directories
3. **Organized Documentation**: All docs moved to dedicated `docs/` directory
4. **Configuration Centralized**: Config files moved to `config/` directory
5. **Scripts Organized**: Utility scripts moved to `scripts/` directory
6. **Automation Preserved**: DevOps toolkit remains in `automation/` with updated paths

### Benefits:
- **Clearer Structure**: Easier to navigate and understand
- **Better Separation**: Frontend and backend clearly separated
- **Improved Organization**: Documentation and configuration centralized
- **Maintained Functionality**: All automation tools updated for new paths
- **Git History Preserved**: Backend git history maintained in new location

## 🛠️ Updated Script References

### Automation Scripts Updated:
- ✅ `automation/workflows/deploy-all.ps1` - Updated config path references
- ✅ `automation/api-scripts/health-check.ps1` - No changes needed (external URLs)
- ✅ `automation/api-scripts/continuous-monitoring.ps1` - No changes needed
- ✅ `automation/cli-tools/install-all-clis.ps1` - No changes needed

### Documentation Updated:
- ✅ Path references in all automation README files
- ✅ Cross-references between documentation files
- ✅ Directory structure documentation (this file)

## 📋 Next Steps

1. **Update Git Ignore**: Update patterns for new structure
2. **Test All Scripts**: Verify all automation works with new paths
3. **Update Documentation Links**: Fix any remaining cross-references
4. **Commit Changes**: Save the new structure to version control

## 🚀 Quick Start with New Structure

```powershell
# Clone/navigate to project
cd HouseRenovators-api

# Backend development
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Frontend development  
cd frontend
npm install
npm run dev

# Automation tools
cd automation
.\cli-tools\install-all-clis.ps1
.\workflows\deploy-all.ps1

# Health monitoring
.\automation\api-scripts\health-check.ps1 -All
```

## 📞 Support

For questions about the new structure or migration issues:
- Check `docs/TROUBLESHOOTING.md` for common issues
- Review `automation/README.md` for tool documentation
- See individual component README files for specific guidance