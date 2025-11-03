# 🚀 House Renovators AI Portal - CLI Tools Installation
# This script installs all required CLI tools for managing the multi-cloud deployment

param(
    [switch]$SkipNodeJS,
    [switch]$SkipPython,
    [switch]$Verbose
)

Write-Host "🚀 Installing House Renovators AI Portal CLI Tools..." -ForegroundColor Cyan
Write-Host "=" * 60

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to install with error handling
function Install-Tool($name, $command, $checkCommand = $null) {
    $check = if ($checkCommand) { $checkCommand } else { $name }
    
    if (Test-Command $check) {
        Write-Host "✅ $name is already installed" -ForegroundColor Green
        return
    }
    
    Write-Host "📦 Installing $name..." -ForegroundColor Yellow
    try {
        Invoke-Expression $command
        if (Test-Command $check) {
            Write-Host "✅ $name installed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ $name installation may have failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Failed to install $name`: $_" -ForegroundColor Red
    }
}

# Check for PowerShell prerequisites
Write-Host "`n🔧 Checking Prerequisites..." -ForegroundColor Cyan

# Check if running as Administrator for some installations
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  Some installations may require Administrator privileges" -ForegroundColor Yellow
}

# Install Winget if not available
if (-not (Test-Command "winget")) {
    Write-Host "❌ Windows Package Manager (winget) is required but not found" -ForegroundColor Red
    Write-Host "Please install winget from Microsoft Store or GitHub releases" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n📦 Installing Platform CLI Tools..." -ForegroundColor Cyan

# 1. GitHub CLI
Install-Tool "GitHub CLI" "winget install --id GitHub.cli" "gh"

# 2. Google Cloud CLI
Install-Tool "Google Cloud CLI" "winget install --id Google.CloudSDK" "gcloud"

# 3. jq (JSON processor)
Install-Tool "jq" "winget install --id jqlang.jq" "jq"

# 4. Node.js (required for npm-based tools)
if (-not $SkipNodeJS) {
    Install-Tool "Node.js" "winget install --id OpenJS.NodeJS" "node"
    
    # Wait for Node.js PATH update
    Start-Sleep 3
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

# 5. Python (if needed for OpenAI CLI)
if (-not $SkipPython) {
    Install-Tool "Python" "winget install --id Python.Python.3.11" "python"
}

Write-Host "`n📦 Installing npm-based CLI Tools..." -ForegroundColor Cyan

# Refresh PATH for npm
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

if (Test-Command "npm") {
    # 6. Render CLI
    Install-Tool "Render CLI" "npm install -g @render-api/cli" "render"
    
    # 7. Wrangler (Cloudflare)
    Install-Tool "Wrangler CLI" "npm install -g wrangler" "wrangler"
    
    # 8. Google Apps Script CLI (optional)
    Install-Tool "clasp CLI" "npm install -g @google/clasp" "clasp"
} else {
    Write-Host "❌ npm not available, skipping npm-based tools" -ForegroundColor Red
    Write-Host "Please install Node.js and run this script again" -ForegroundColor Yellow
}

Write-Host "`n📦 Installing Python-based CLI Tools..." -ForegroundColor Cyan

if (Test-Command "pip") {
    # 9. OpenAI CLI
    Install-Tool "OpenAI CLI" "pip install openai" "openai"
    
    # 10. Development tools
    Install-Tool "uvicorn" "pip install uvicorn" "uvicorn"
    Install-Tool "pytest" "pip install pytest" "pytest"
} else {
    Write-Host "❌ pip not available, skipping Python-based tools" -ForegroundColor Red
}

Write-Host "`n🔧 Verifying Installations..." -ForegroundColor Cyan

$tools = @(
    @{Name="GitHub CLI"; Command="gh"; TestArgs="--version"},
    @{Name="Google Cloud CLI"; Command="gcloud"; TestArgs="--version"},
    @{Name="jq"; Command="jq"; TestArgs="--version"},
    @{Name="Node.js"; Command="node"; TestArgs="--version"},
    @{Name="npm"; Command="npm"; TestArgs="--version"},
    @{Name="Render CLI"; Command="render"; TestArgs="--version"},
    @{Name="Wrangler CLI"; Command="wrangler"; TestArgs="--version"},
    @{Name="Python"; Command="python"; TestArgs="--version"},
    @{Name="OpenAI CLI"; Command="openai"; TestArgs="--version"}
)

$installed = 0
$total = $tools.Count

foreach ($tool in $tools) {
    if (Test-Command $tool.Command) {
        try {
            $version = & $tool.Command $tool.TestArgs 2>$null
            Write-Host "✅ $($tool.Name): $($version.Split("`n")[0])" -ForegroundColor Green
            $installed++
        } catch {
            Write-Host "⚠️  $($tool.Name): Installed but version check failed" -ForegroundColor Yellow
            $installed++
        }
    } else {
        Write-Host "❌ $($tool.Name): Not found" -ForegroundColor Red
    }
}

Write-Host "`n📊 Installation Summary" -ForegroundColor Cyan
Write-Host "=" * 30
Write-Host "Installed: $installed/$total tools" -ForegroundColor $(if ($installed -eq $total) { "Green" } else { "Yellow" })

if ($installed -eq $total) {
    Write-Host "`n🎉 All CLI tools installed successfully!" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run authentication setup scripts in cli-tools/ directory" -ForegroundColor White
    Write-Host "2. Configure environment variables in automation/config/" -ForegroundColor White
    Write-Host "3. Test the deployment pipeline with deploy-all.ps1" -ForegroundColor White
} else {
    Write-Host "`n⚠️  Some tools failed to install. Check error messages above." -ForegroundColor Yellow
    Write-Host "You may need to:" -ForegroundColor Cyan
    Write-Host "- Run as Administrator for some installations" -ForegroundColor White
    Write-Host "- Manually install missing tools" -ForegroundColor White
    Write-Host "- Restart PowerShell to refresh PATH" -ForegroundColor White
}

Write-Host "`n🔗 Useful Commands:" -ForegroundColor Cyan
Write-Host "- Check tool versions: Get-Command gh, render, wrangler, gcloud" -ForegroundColor White
Write-Host "- Setup authentication: .\automation\cli-tools\setup-*.ps1" -ForegroundColor White
Write-Host "- Deploy stack: .\automation\workflows\deploy-all.ps1" -ForegroundColor White

Write-Host "`n✅ CLI installation complete!" -ForegroundColor Green