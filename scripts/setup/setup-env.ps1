# HouseRenovators-API Environment Setup Script
# Automates setup on new machines

param(
    [string]$Mode = "local",  # "local" or "help"
    [string]$CredentialsPath = ""
)

Write-Host "🏗️  HouseRenovators-API Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "app/main.py")) {
    Write-Host "❌ Error: Must run from project root directory" -ForegroundColor Red
    Write-Host "   Current: $PWD" -ForegroundColor Yellow
    Write-Host "   Expected: HouseRenovators-api/" -ForegroundColor Yellow
    exit 1
}

if ($Mode -eq "help") {
    Write-Host "Usage: .\scripts\setup\setup-env.ps1 [-Mode local] [-CredentialsPath path]"
    Write-Host ""
    Write-Host "Modes:"
    Write-Host "  local          - Setup for local development (default)"
    Write-Host "  help           - Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\scripts\setup\setup-env.ps1"
    Write-Host "  .\scripts\setup\setup-env.ps1 -CredentialsPath C:\Backup\credentials.json"
    exit 0
}

# Step 1: Check Python
Write-Host "📋 Step 1: Checking Python installation..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.13+ from python.org" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Found: $pythonVersion" -ForegroundColor Gray

# Step 2: Create virtual environment
Write-Host ""
Write-Host "📋 Step 2: Creating virtual environment..." -ForegroundColor Green
if (Test-Path ".venv") {
    Write-Host "   ⚠️  Virtual environment already exists" -ForegroundColor Yellow
    $response = Read-Host "   Recreate? (y/N)"
    if ($response -eq "y") {
        Remove-Item -Recurse -Force .venv
        python -m venv .venv
        Write-Host "   ✅ Virtual environment recreated" -ForegroundColor Gray
    }
} else {
    python -m venv .venv
    Write-Host "   ✅ Virtual environment created" -ForegroundColor Gray
}

# Step 3: Install dependencies
Write-Host ""
Write-Host "📋 Step 3: Installing Python dependencies..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 4: Setup .env file
Write-Host ""
Write-Host "📋 Step 4: Setting up environment variables..." -ForegroundColor Green
if (Test-Path ".env") {
    Write-Host "   ⚠️  .env file already exists" -ForegroundColor Yellow
    $response = Read-Host "   Overwrite? (y/N)"
    if ($response -ne "y") {
        Write-Host "   ⏭️  Skipping .env creation" -ForegroundColor Gray
        $skipEnv = $true
    }
}

if (!$skipEnv) {
    Write-Host ""
    Write-Host "   Please provide the following credentials:" -ForegroundColor Cyan
    Write-Host "   (Press Enter to skip and fill in .env manually later)" -ForegroundColor Gray
    Write-Host ""
    
    # Prompt for each secret
    $sheetId = Read-Host "   Google Sheet ID"
    $openaiKey = Read-Host "   OpenAI API Key (sk-proj-...)"
    $qbClientId = Read-Host "   QuickBooks Client ID"
    $qbClientSecret = Read-Host "   QuickBooks Client Secret"
    
    # Generate JWT secret
    $jwtSecret = python -c "import secrets; print(secrets.token_urlsafe(32))" 2>$null
    Write-Host "   ✅ Generated JWT Secret: $jwtSecret" -ForegroundColor Gray
    
    # Create .env file
    $envContent = @"
# Google Sheets API
SHEET_ID=$sheetId
GOOGLE_SERVICE_ACCOUNT_FILE=config/house-renovators-credentials.json

# OpenAI API
OPENAI_API_KEY=$openaiKey

# QuickBooks OAuth2
QUICKBOOKS_CLIENT_ID=$qbClientId
QUICKBOOKS_CLIENT_SECRET=$qbClientSecret
QUICKBOOKS_REDIRECT_URI=http://localhost:8000/v1/quickbooks/callback
QUICKBOOKS_ENVIRONMENT=sandbox

# Security
JWT_SECRET_KEY=$jwtSecret
JWT_ALGORITHM=HS256

# API Settings
API_VERSION=v1
"@
    
    $envContent | Out-File -FilePath .env -Encoding utf8
    Write-Host "   ✅ .env file created" -ForegroundColor Gray
}

# Step 5: Setup Google Service Account
Write-Host ""
Write-Host "📋 Step 5: Setting up Google Service Account..." -ForegroundColor Green
if (!(Test-Path "config")) {
    New-Item -ItemType Directory -Path "config" | Out-Null
    Write-Host "   ✅ Created config/ directory" -ForegroundColor Gray
}

$credentialFile = "config/house-renovators-credentials.json"
if (Test-Path $credentialFile) {
    Write-Host "   ⚠️  Service account file already exists" -ForegroundColor Yellow
} elseif ($CredentialsPath -and (Test-Path $CredentialsPath)) {
    Copy-Item $CredentialsPath $credentialFile
    Write-Host "   ✅ Copied service account credentials" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️  Service account JSON not found" -ForegroundColor Yellow
    Write-Host "   📝 Please manually place house-renovators-credentials.json in config/" -ForegroundColor Yellow
    Write-Host "      Get it from: https://console.cloud.google.com" -ForegroundColor Gray
}

# Step 6: Verify .gitignore
Write-Host ""
Write-Host "📋 Step 6: Verifying security..." -ForegroundColor Green
$gitignoreContent = Get-Content .gitignore -Raw
$securityChecks = @(
    @{Pattern = ".env"; Name = "Environment variables"},
    @{Pattern = "*.json"; Name = "Credential files"},
    @{Pattern = "__pycache__"; Name = "Python cache"}
)

$allSecure = $true
foreach ($check in $securityChecks) {
    if ($gitignoreContent -like "*$($check.Pattern)*") {
        Write-Host "   ✅ $($check.Name) protected" -ForegroundColor Gray
    } else {
        Write-Host "   ❌ $($check.Name) NOT protected" -ForegroundColor Red
        $allSecure = $false
    }
}

if (!$allSecure) {
    Write-Host "   ⚠️  WARNING: Update .gitignore to protect secrets!" -ForegroundColor Red
}

# Step 7: Test setup
Write-Host ""
Write-Host "📋 Step 7: Testing setup..." -ForegroundColor Green
Write-Host "   Testing imports..." -ForegroundColor Gray

$testScript = @"
import sys
try:
    from app.services.google_service import google_service
    from app.services.openai_service import openai_service
    from app.services.quickbooks_service import quickbooks_service
    print('✅ All services import successfully')
    sys.exit(0)
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"@

$testScript | python 2>&1 | ForEach-Object {
    Write-Host "   $_" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review .env file and add any missing credentials"
Write-Host "2. Ensure config/house-renovators-credentials.json exists"
Write-Host "3. Start backend: python -m uvicorn app.main:app --reload"
Write-Host "4. Setup frontend: cd frontend && npm install && npm run dev"
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "- Setup Guide: docs/SETUP_NEW_MACHINE.md"
Write-Host "- Troubleshooting: docs/TROUBLESHOOTING.md"
Write-Host "- API Docs: docs/API_DOCUMENTATION.md"
Write-Host ""

# Check if credentials still needed
if (!(Test-Path $credentialFile)) {
    Write-Host "⚠️  IMPORTANT: Place Google Service Account JSON in config/" -ForegroundColor Yellow
    Write-Host "   File: config/house-renovators-credentials.json" -ForegroundColor Yellow
}

if ((Get-Content .env -Raw) -match "OPENAI_API_KEY=\s*$") {
    Write-Host "⚠️  IMPORTANT: Add OpenAI API key to .env" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
