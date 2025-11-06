# cleanup-structure.ps1
# Directory Structure Cleanup Script
# Removes duplicate directories, old backups, and obsolete credential files

Write-Host "🧹 Starting directory structure cleanup..." -ForegroundColor Cyan
Write-Host ""

# Safety check - confirm we're in the right directory
$currentDir = Get-Location
if ($currentDir.Path -notlike "*HouseRenovators-api*") {
    Write-Host "❌ Error: Not in HouseRenovators-api directory" -ForegroundColor Red
    Write-Host "Current directory: $currentDir" -ForegroundColor Yellow
    exit 1
}

Write-Host "Current directory: $currentDir" -ForegroundColor Green
Write-Host ""

# Track what will be deleted
$itemsToDelete = @()

# 1. Check for duplicate backend directory
if (Test-Path "backend") {
    Write-Host "📁 Found duplicate /backend/ directory" -ForegroundColor Yellow
    $itemsToDelete += @{Path="backend/"; Reason="Duplicate of /app/ (root app/ is deployed to Render)"}
}

# 2. Check for old credentials in config/
if (Test-Path "config") {
    $credFiles = Get-ChildItem config/ -Filter "*.json" | Where-Object {$_.Name -ne "house-renovators-credentials.json"}
    if ($credFiles.Count -gt 0) {
        Write-Host "🔐 Found $($credFiles.Count) old credential files in /config/" -ForegroundColor Yellow
        foreach ($file in $credFiles) {
            $itemsToDelete += @{Path="config/$($file.Name)"; Reason="Old credential file (keeping only house-renovators-credentials.json)"}
        }
    }
}

# 3. Check for backup directories
$backupDirs = @(
    "organization-backup-2025-11-04_000329",
    "workspace-backup-2025-11-04_000046",
    "frontend-archive"
)

foreach ($dir in $backupDirs) {
    if (Test-Path $dir) {
        Write-Host "📦 Found backup directory: /$dir/" -ForegroundColor Yellow
        $itemsToDelete += @{Path="$dir/"; Reason="Old backup directory"}
    }
}

# 4. Check for obsolete files at root
$obsoleteFiles = @(
    @{Path="FRONTEND_FIX_SUMMARY.md"; Reason="Moved to docs/archive/"},
    @{Path="start-backend.ps1"; Reason="Should be in scripts/ if still needed"},
    @{Path="start-frontend.ps1"; Reason="Should be in scripts/ if still needed"}
)

foreach ($file in $obsoleteFiles) {
    if (Test-Path $file.Path) {
        Write-Host "📄 Found obsolete file: $($file.Path)" -ForegroundColor Yellow
        $itemsToDelete += $file
    }
}

# Display summary
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "CLEANUP SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($itemsToDelete.Count -eq 0) {
    Write-Host "✓ Directory structure is already clean! No items to delete." -ForegroundColor Green
    exit 0
}

Write-Host "The following $($itemsToDelete.Count) item(s) will be deleted:" -ForegroundColor Yellow
Write-Host ""

$counter = 1
foreach ($item in $itemsToDelete) {
    Write-Host "  $counter. " -NoNewline -ForegroundColor White
    Write-Host "$($item.Path)" -NoNewline -ForegroundColor Red
    Write-Host " → " -NoNewline -ForegroundColor DarkGray
    Write-Host "$($item.Reason)" -ForegroundColor DarkGray
    $counter++
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Confirmation prompt
$confirmation = Read-Host "Do you want to proceed with cleanup? (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host "❌ Cleanup cancelled by user" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🗑️  Starting deletion..." -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$errorCount = 0

foreach ($item in $itemsToDelete) {
    try {
        if (Test-Path $item.Path) {
            $fullPath = Join-Path $currentDir $item.Path
            
            # Check if it's a directory or file
            if ((Get-Item $fullPath) -is [System.IO.DirectoryInfo]) {
                Remove-Item -Path $fullPath -Recurse -Force -ErrorAction Stop
                Write-Host "  ✓ Deleted directory: $($item.Path)" -ForegroundColor Green
            } else {
                Remove-Item -Path $fullPath -Force -ErrorAction Stop
                Write-Host "  ✓ Deleted file: $($item.Path)" -ForegroundColor Green
            }
            $successCount++
        } else {
            Write-Host "  ⚠ Already deleted: $($item.Path)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  ✗ Failed to delete $($item.Path): $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "CLEANUP COMPLETE" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Successfully deleted: $successCount item(s)" -ForegroundColor Green
if ($errorCount -gt 0) {
    Write-Host "✗ Failed to delete: $errorCount item(s)" -ForegroundColor Red
}
Write-Host ""

# Optional: Show remaining structure
Write-Host "📂 Updated directory structure:" -ForegroundColor Cyan
Write-Host ""
Get-ChildItem -Directory | Where-Object {$_.Name -notlike ".*"} | ForEach-Object {
    Write-Host "  ├── $($_.Name)/" -ForegroundColor White
}
Get-ChildItem -File | Where-Object {$_.Name -notlike ".*"} | Select-Object -First 5 | ForEach-Object {
    Write-Host "  ├── $($_.Name)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "✅ Cleanup script completed!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review changes with: git status" -ForegroundColor White
Write-Host "  2. Commit deletions: git add -A && git commit -m 'chore: Clean up directory structure'" -ForegroundColor White
Write-Host "  3. Push changes: git push origin main" -ForegroundColor White
Write-Host ""
