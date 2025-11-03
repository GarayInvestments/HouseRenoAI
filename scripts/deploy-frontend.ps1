# House Renovators AI Portal - Frontend Deployment Scripts
# PowerShell script for easy deployment to Cloudflare Pages

Write-Host "🌐 House Renovators AI Portal - Frontend Deployment" -ForegroundColor Blue
Write-Host "===================================================" -ForegroundColor Blue

# Configuration
$FrontendPath = "house-renovators-pwa"
$RepoName = "HouseRenoAI"
$GitRemote = "https://github.com/GarayInvestments/HouseRenoAI.git"

# Check if we're in the right directory
if (-not (Test-Path $FrontendPath)) {
    Write-Host "❌ Frontend directory not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

Set-Location $FrontendPath

Write-Host "📋 Pre-deployment Checklist:" -ForegroundColor Yellow
Write-Host "1. ✅ Verify .env.production has correct API URL"
Write-Host "2. ✅ Check all dependencies are installed"
Write-Host "3. ✅ Test build process locally"
Write-Host "4. ✅ Verify PWA manifest configuration"

# Check if API URL is configured
if (Test-Path ".env.production") {
    $envContent = Get-Content ".env.production" | Where-Object { $_ -like "VITE_API_URL=*" }
    if ($envContent -like "*localhost*") {
        Write-Host "⚠️ WARNING: API URL still points to localhost in .env.production" -ForegroundColor Yellow
        Write-Host "   Please update VITE_API_URL to your Render deployment URL" -ForegroundColor Yellow
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    } else {
        Write-Host "✅ Production API URL configured" -ForegroundColor Green
    }
} else {
    Write-Host "❌ .env.production file not found!" -ForegroundColor Red
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
}

# Test build
Write-Host "`n🔨 Testing build process..."
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed! Please fix errors before deploying." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build successful" -ForegroundColor Green

# Clean up dist folder for fresh deployment
if (Test-Path "dist") {
    Remove-Item "dist" -Recurse -Force
    Write-Host "✅ Cleaned previous build" -ForegroundColor Green
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
git commit -m "PWA frontend ready for deployment - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

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

Write-Host "`n🌩️ Cloudflare Pages Deployment Instructions:" -ForegroundColor Magenta
Write-Host "===============================================" -ForegroundColor Magenta
Write-Host "1. Go to https://dash.cloudflare.com and sign in"
Write-Host "2. Go to 'Workers & Pages' → 'Create application' → 'Pages'"
Write-Host "3. Connect to Git and select your repository: $RepoName"
Write-Host "4. Configure build settings:"
Write-Host "   - Production branch: main"
Write-Host "   - Build command: npm run build"
Write-Host "   - Build output directory: dist"
Write-Host "   - Node.js version: 18 or higher"
Write-Host "`n5. Add Environment Variables:"
Write-Host "   - VITE_API_URL=https://your-render-app.onrender.com"
Write-Host "   - VITE_ENV=production"
Write-Host "   - VITE_ENABLE_DEBUG=false"
Write-Host "`n6. Configure Custom Domain (optional):"
Write-Host "   - Add custom domain: portal.houserenovatorsllc.com"
Write-Host "   - Configure DNS records as instructed"

Write-Host "`n📊 Build and Test Locally:" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "1. Build for production:"
Write-Host "   npm run build"
Write-Host "`n2. Preview production build:"
Write-Host "   npm run preview"
Write-Host "`n3. Test PWA features:"
Write-Host "   - Open browser dev tools"
Write-Host "   - Go to Application/PWA tab"
Write-Host "   - Check manifest and service worker"
Write-Host "   - Test install prompt"

Write-Host "`n✅ Frontend deployment preparation complete!" -ForegroundColor Green
Write-Host "Your PWA will be available at: https://your-project.pages.dev" -ForegroundColor Cyan

# Return to original directory
Set-Location ..

Write-Host "`n🎯 Final Steps:" -ForegroundColor Yellow
Write-Host "1. Complete Cloudflare Pages deployment using the instructions above"
Write-Host "2. Test the deployed application thoroughly"
Write-Host "3. Configure custom domain if desired"
Write-Host "4. Set up monitoring and analytics"

Write-Host "`n🔗 Useful Links:" -ForegroundColor Cyan
Write-Host "- Cloudflare Pages: https://dash.cloudflare.com"
Write-Host "- PWA Testing: Use Lighthouse in Chrome DevTools"
Write-Host "- Domain Setup: Cloudflare DNS management"