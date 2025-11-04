# Git Push Script - Prevents terminal hanging
# Use this instead of running git push directly in Copilot Chat

param(
    [string]$branch = "main",
    [switch]$force
)

Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Cyan

try {
    if ($force) {
        git push --force origin $branch 2>&1 | Out-String | Write-Host
    } else {
        git push origin $branch 2>&1 | Out-String | Write-Host
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Push successful!" -ForegroundColor Green
    } else {
        Write-Host "❌ Push failed with exit code $LASTEXITCODE" -ForegroundColor Red
        Write-Host "💡 Try: git pull --rebase origin $branch" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}
