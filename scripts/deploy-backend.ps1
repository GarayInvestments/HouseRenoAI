# House Renovators AI Portal - Deployment Scripts
# PowerShell scripts for easy deployment to Render and Cloudflare Pages

Write-Host "🏗️ House Renovators AI Portal - Backend Deployment" -ForegroundColor Blue
Write-Host "=================================================" -ForegroundColor Blue

# Configuration
$BackendPath = "house-renovators-ai"
# Configuration
$BackendPath = "house-renovators-ai"
$RepoName = "HouseRenoAI"
$GitRemote = "https://github.com/GarayInvestments/HouseRenoAI.git"
$GitRemote = "https://github.com/GarayInvestments/HouseRenoAI.git"

# Check if we're in the right directory
if (-not (Test-Path $BackendPath)) {
    Write-Host "❌ Backend directory not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

Set-Location $BackendPath

Write-Host "📋 Pre-deployment Checklist:" -ForegroundColor Yellow
Write-Host "1. ✅ Verify .env.template is complete"
Write-Host "2. ✅ Check requirements.txt is updated"
Write-Host "3. ✅ Ensure service-account.json is ready for upload"
Write-Host "4. ✅ Test API endpoints locally"

# Verify required files
$RequiredFiles = @(
    ".env.template",
    "requirements.txt", 
    "Dockerfile",
    "README.md",
    "app/main.py"
)

foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file missing!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n🚀 Deployment Steps:" -ForegroundColor Cyan

Write-Host "1. Initialize Git repository (if not already done)..."
if (-not (Test-Path ".git")) {
    git init
    Write-Host "   ✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "   ✅ Git repository exists" -ForegroundColor Green
}

Write-Host "`n2. Add and commit files..."
git add .
git commit -m "FastAPI backend ready for deployment - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

Write-Host "`n3. Add remote repository..."
try {
    git remote add origin $GitRemote
    Write-Host "   ✅ Remote added: $GitRemote" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Remote might already exist" -ForegroundColor Yellow
}

Write-Host "`n4. Push to GitHub..."
try {
    git push -u origin main
    Write-Host "   ✅ Code pushed to GitHub" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to push. Check your Git configuration." -ForegroundColor Red
    Write-Host "   Manual steps needed:" -ForegroundColor Yellow
    Write-Host "   - Create repository on GitHub: $RepoName" -ForegroundColor Yellow
    Write-Host "   - Run: git push -u origin main" -ForegroundColor Yellow
}

Write-Host "`n🌐 Render Deployment Instructions:" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta
Write-Host "1. Go to https://render.com and sign in"
Write-Host "2. Click 'New +' → 'Web Service'"
Write-Host "3. Connect your GitHub repository: $RepoName"
Write-Host "4. Configure build settings:"
Write-Host "   - Build Command: pip install -r requirements.txt"
Write-Host "   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port 10000"
Write-Host "   - Python Version: 3.11"
Write-Host "`n5. Add Environment Variables:"
Write-Host "   - OPENAI_API_KEY=sk-your-key"
Write-Host "   - SHEET_ID=your-sheet-id"
Write-Host "   - CHAT_WEBHOOK_URL=your-webhook-url"
Write-Host "   - DEBUG=false"
Write-Host "   - PORT=10000"
Write-Host "`n6. Upload Secret Files:"
Write-Host "   - Upload your service-account.json file"
Write-Host "`n7. Deploy and note your API URL"

Write-Host "`n✅ Backend deployment preparation complete!" -ForegroundColor Green
Write-Host "Your API will be available at: https://your-service-name.onrender.com" -ForegroundColor Cyan

# Return to original directory
Set-Location ..

Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Complete Render deployment using the instructions above"
Write-Host "2. Update frontend .env.production with your Render API URL"
Write-Host "3. Run deploy-frontend.ps1 to deploy the PWA"