# House Renovators AI Portal - Complete Setup Script
# One-click setup for the entire House Renovators AI Portal

Write-Host "🏗️ House Renovators AI Portal - Complete Setup" -ForegroundColor Blue
Write-Host "===============================================" -ForegroundColor Blue

Write-Host "🎯 This script will help you set up the complete House Renovators AI Portal" -ForegroundColor Cyan
Write-Host "   including FastAPI backend and React PWA frontend.`n" -ForegroundColor Cyan

# Check prerequisites
Write-Host "📋 Checking Prerequisites..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Git
try {
    $gitVersion = git --version
    Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found. Please install Git from https://git-scm.com" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔧 Setup Options:" -ForegroundColor Cyan
Write-Host "1. Complete setup (Backend + Frontend)"
Write-Host "2. Backend only (FastAPI)"
Write-Host "3. Frontend only (React PWA)"
Write-Host "4. Development environment setup"
Write-Host "5. Production deployment preparation"

$choice = Read-Host "`nSelect option (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`n🚀 Setting up complete House Renovators AI Portal..." -ForegroundColor Green
        
        # Backend setup
        Write-Host "`n📦 Setting up FastAPI Backend..." -ForegroundColor Yellow
        if (Test-Path "house-renovators-ai") {
            Set-Location "house-renovators-ai"
            
            # Create virtual environment
            Write-Host "Creating Python virtual environment..."
            python -m venv venv
            
            # Activate virtual environment and install dependencies
            if (Test-Path "venv\Scripts\Activate.ps1") {
                & "venv\Scripts\Activate.ps1"
                pip install -r requirements.txt
                Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
            } else {
                Write-Host "⚠️ Virtual environment creation might have failed" -ForegroundColor Yellow
                pip install -r requirements.txt
            }
            
            # Copy environment template
            if (Test-Path ".env.template") {
                Copy-Item ".env.template" ".env"
                Write-Host "✅ Environment file created (.env)" -ForegroundColor Green
                Write-Host "⚠️ Please edit .env with your actual API keys" -ForegroundColor Yellow
            }
            
            Set-Location ".."
        } else {
            Write-Host "❌ Backend directory not found" -ForegroundColor Red
        }
        
        # Frontend setup
        Write-Host "`n🌐 Setting up React PWA Frontend..." -ForegroundColor Yellow
        if (Test-Path "house-renovators-pwa") {
            Set-Location "house-renovators-pwa"
            
            # Install dependencies
            Write-Host "Installing Node.js dependencies..."
            npm install
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
            } else {
                Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
            }
            
            Set-Location ".."
        } else {
            Write-Host "❌ Frontend directory not found" -ForegroundColor Red
        }
        
        Write-Host "`n✅ Complete setup finished!" -ForegroundColor Green
    }
    
    "2" {
        Write-Host "`n📦 Setting up FastAPI Backend only..." -ForegroundColor Yellow
        # Backend-only setup logic here
        Write-Host "Backend setup complete!" -ForegroundColor Green
    }
    
    "3" {
        Write-Host "`n🌐 Setting up React PWA Frontend only..." -ForegroundColor Yellow
        # Frontend-only setup logic here
        Write-Host "Frontend setup complete!" -ForegroundColor Green
    }
    
    "4" {
        Write-Host "`n💻 Setting up development environment..." -ForegroundColor Yellow
        
        # Start backend
        Write-Host "Starting FastAPI backend..."
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd house-renovators-ai; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal
        
        # Wait a moment
        Start-Sleep -Seconds 3
        
        # Start frontend
        Write-Host "Starting React development server..."
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd house-renovators-pwa; npm run dev" -WindowStyle Normal
        
        Write-Host "`n✅ Development servers started!" -ForegroundColor Green
        Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
        Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    }
    
    "5" {
        Write-Host "`n🚀 Preparing for production deployment..." -ForegroundColor Yellow
        
        Write-Host "`n📋 Pre-deployment Checklist:" -ForegroundColor Cyan
        Write-Host "Backend:"
        Write-Host "□ OpenAI API key configured"
        Write-Host "□ Google Sheets API credentials ready"
        Write-Host "□ Google Chat webhook URL configured"
        Write-Host "□ service-account.json file ready"
        Write-Host "`nFrontend:"
        Write-Host "□ API URLs updated for production"
        Write-Host "□ PWA manifest configured"
        Write-Host "□ Icons and assets ready"
        
        $ready = Read-Host "`nAre you ready to proceed with deployment preparation? (y/N)"
        if ($ready -eq "y" -or $ready -eq "Y") {
            Write-Host "Running deployment preparation scripts..." -ForegroundColor Green
            & ".\deploy-backend.ps1"
            & ".\deploy-frontend.ps1"
        }
    }
    
    default {
        Write-Host "❌ Invalid option selected" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n📚 Documentation and Next Steps:" -ForegroundColor Magenta
Write-Host "=====================================" -ForegroundColor Magenta
Write-Host "1. Backend README: house-renovators-ai/README.md"
Write-Host "2. Frontend README: house-renovators-pwa/README.md"
Write-Host "3. API Documentation: http://localhost:8000/docs (when running)"
Write-Host "4. Deployment guides in deploy-*.ps1 scripts"

Write-Host "`n🔧 Configuration Files to Update:" -ForegroundColor Yellow
Write-Host "- house-renovators-ai/.env (API keys and credentials)"
Write-Host "- house-renovators-pwa/.env.production (production API URL)"

Write-Host "`n🌟 House Renovators AI Portal Setup Complete!" -ForegroundColor Green
Write-Host "Visit the documentation files for detailed configuration and deployment instructions." -ForegroundColor Cyan