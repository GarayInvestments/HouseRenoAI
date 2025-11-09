# Backup Script - Run BEFORE starting Phase 1 refactor
# Creates backup branch and tag for rollback safety

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupBranch = "backup/pre-refactor-$timestamp"
$backupTag = "backup-$timestamp"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  CHAT REFACTOR BACKUP PROCEDURE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Ensure we're in the right directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "Project Root: $projectRoot" -ForegroundColor Yellow
Write-Host ""

# Check for uncommitted changes
Write-Host "Checking for uncommitted changes..." -ForegroundColor Yellow
$gitStatus = git status --porcelain

if ($gitStatus) {
    Write-Host "ERROR: You have uncommitted changes!" -ForegroundColor Red
    Write-Host "Please commit or stash your changes before running backup." -ForegroundColor Red
    Write-Host ""
    git status
    exit 1
}

Write-Host "✓ No uncommitted changes found" -ForegroundColor Green
Write-Host ""

# Get current branch
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "Current branch: $currentBranch" -ForegroundColor Yellow
Write-Host ""

# Create backup branch
Write-Host "Creating backup branch: $backupBranch" -ForegroundColor Yellow
git checkout -b $backupBranch

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create backup branch" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Backup branch created" -ForegroundColor Green
Write-Host ""

# Create tag
Write-Host "Creating backup tag: $backupTag" -ForegroundColor Yellow
git tag $backupTag -m "Backup before chat.py refactor - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create backup tag" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Backup tag created" -ForegroundColor Green
Write-Host ""

# Push backup branch to remote
Write-Host "Pushing backup branch to remote..." -ForegroundColor Yellow
git push origin $backupBranch

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to push backup branch" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Backup branch pushed to remote" -ForegroundColor Green
Write-Host ""

# Push tag to remote
Write-Host "Pushing backup tag to remote..." -ForegroundColor Yellow
git push origin $backupTag

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to push backup tag" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Backup tag pushed to remote" -ForegroundColor Green
Write-Host ""

# Return to original branch
Write-Host "Returning to branch: $currentBranch" -ForegroundColor Yellow
git checkout $currentBranch

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to return to original branch" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Returned to original branch" -ForegroundColor Green
Write-Host ""

# Verify backup
Write-Host "Verifying backup..." -ForegroundColor Yellow
$verifyBranch = git branch -r | Select-String "origin/$backupBranch"
$verifyTag = git tag -l $backupTag

if (-not $verifyBranch) {
    Write-Host "ERROR: Backup branch not found in remote" -ForegroundColor Red
    exit 1
}

if (-not $verifyTag) {
    Write-Host "ERROR: Backup tag not found" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Backup verified successfully" -ForegroundColor Green
Write-Host ""

# Success summary
Write-Host "============================================" -ForegroundColor Green
Write-Host "  BACKUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backup Details:" -ForegroundColor Cyan
Write-Host "  Branch: $backupBranch" -ForegroundColor White
Write-Host "  Tag:    $backupTag" -ForegroundColor White
Write-Host "  Time:   $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
Write-Host ""
Write-Host "Rollback Commands (if needed):" -ForegroundColor Yellow
Write-Host "  git checkout $backupBranch" -ForegroundColor White
Write-Host "  git checkout -b hotfix/revert-refactor" -ForegroundColor White
Write-Host "  # Test, then merge to main if stable" -ForegroundColor White
Write-Host ""
Write-Host "You can now safely proceed with Phase 1!" -ForegroundColor Green
Write-Host ""
