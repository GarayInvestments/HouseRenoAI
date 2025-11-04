#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Clean up duplicate files and folders in HouseRenovators-api workspace

.DESCRIPTION
    This script safely removes redundant nested folders and duplicate files
    while creating a backup before any changes.

.EXAMPLE
    .\cleanup-duplicates.ps1
#>

param(
    [switch]$DryRun,
    [switch]$SkipBackup
)

$ErrorActionPreference = "Stop"
$RootPath = Split-Path -Parent $PSScriptRoot

Write-Host "🧹 House Renovators Workspace Cleanup Script" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Create backup unless skipped
if (-not $SkipBackup -and -not $DryRun) {
    $BackupTimestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
    $BackupPath = Join-Path $RootPath "workspace-backup-$BackupTimestamp"
    
    Write-Host "📦 Creating backup at: $BackupPath" -ForegroundColor Yellow
    
    # Create backup folder
    New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    
    # Backup items we're about to modify
    $ItemsToBackup = @(
        "backend/backend",
        "backend/frontend",
        "backend/automation",
        "backend/config",
        "backend/docs",
        "backend/scripts",
        "backend/API_DOCUMENTATION.md",
        "backend/DEPLOYMENT.md",
        "backend/PROJECT_SETUP.md",
        "backend/TROUBLESHOOTING.md",
        "house-renovators-ai"
    )
    
    foreach ($item in $ItemsToBackup) {
        $sourcePath = Join-Path $RootPath $item
        if (Test-Path $sourcePath) {
            $destPath = Join-Path $BackupPath $item
            $destParent = Split-Path -Parent $destPath
            
            if (-not (Test-Path $destParent)) {
                New-Item -ItemType Directory -Path $destParent -Force | Out-Null
            }
            
            Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
            Write-Host "  ✅ Backed up: $item" -ForegroundColor Green
        }
    }
    
    Write-Host ""
}

# Define cleanup operations
$CleanupOperations = @(
    @{
        Path = "backend/backend"
        Reason = "Nested duplicate backend folder"
        Action = "DELETE"
    },
    @{
        Path = "house-renovators-ai"
        Reason = "Nested duplicate with only README"
        Action = "DELETE"
    },
    @{
        Path = "backend/frontend"
        Reason = "Frontend folder inside backend (root frontend/ is correct)"
        Action = "DELETE"
    },
    @{
        Path = "backend/automation"
        Reason = "Duplicate of root automation/"
        Action = "DELETE"
    },
    @{
        Path = "backend/config"
        Reason = "Duplicate of root config/"
        Action = "DELETE"
    },
    @{
        Path = "backend/docs"
        Reason = "Duplicate of root docs/"
        Action = "DELETE"
    },
    @{
        Path = "backend/scripts"
        Reason = "Duplicate of root scripts/"
        Action = "DELETE"
    },
    @{
        Path = "backend/API_DOCUMENTATION.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/DEPLOYMENT.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/PROJECT_SETUP.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/TROUBLESHOOTING.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/FRONTEND_BACKEND_INTEGRATION.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/FRONTEND_REBUILD_SUMMARY.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/SESSION_SUMMARY_NOV_3_2025.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/SHEETS_VERIFICATION_COMPLETE.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/BACKEND_ACCESS_SETUP.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/BACKEND_ACCESS_VERIFIED.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/DEPLOYMENT_GUIDE.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/DEPLOY_NOW.md"
        Reason = "Duplicate documentation"
        Action = "DELETE"
    },
    @{
        Path = "backend/cf-investigate.ps1"
        Reason = "Duplicate script"
        Action = "DELETE"
    },
    @{
        Path = "backend/frontend-archive"
        Reason = "Duplicate archive folder"
        Action = "DELETE"
    }
)

Write-Host "🔍 Analysis Complete - Found $(($CleanupOperations | Where-Object { Test-Path (Join-Path $RootPath $_.Path) }).Count) items to clean" -ForegroundColor Yellow
Write-Host ""

# Show what will be cleaned
Write-Host "📋 Items to be removed:" -ForegroundColor Cyan
Write-Host ""

$itemsFound = 0
foreach ($op in $CleanupOperations) {
    $fullPath = Join-Path $RootPath $op.Path
    if (Test-Path $fullPath) {
        $itemsFound++
        $size = if (Test-Path $fullPath -PathType Container) {
            $sizeBytes = (Get-ChildItem -Path $fullPath -Recurse -File | Measure-Object -Property Length -Sum).Sum
            if ($sizeBytes -gt 1MB) {
                "{0:N2} MB" -f ($sizeBytes / 1MB)
            } elseif ($sizeBytes -gt 1KB) {
                "{0:N2} KB" -f ($sizeBytes / 1KB)
            } else {
                "$sizeBytes bytes"
            }
        } else {
            $sizeBytes = (Get-Item $fullPath).Length
            if ($sizeBytes -gt 1KB) {
                "{0:N2} KB" -f ($sizeBytes / 1KB)
            } else {
                "$sizeBytes bytes"
            }
        }
        
        Write-Host "  ❌ $($op.Path)" -ForegroundColor Red
        Write-Host "     Reason: $($op.Reason)" -ForegroundColor Gray
        Write-Host "     Size: $size" -ForegroundColor Gray
        Write-Host ""
    }
}

if ($itemsFound -eq 0) {
    Write-Host "✅ No duplicate items found! Workspace is already clean." -ForegroundColor Green
    exit 0
}

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run without -DryRun flag to perform cleanup" -ForegroundColor Cyan
    exit 0
}

# Confirm before proceeding
Write-Host "⚠️  WARNING: This will permanently delete $itemsFound items" -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Type 'YES' to proceed with cleanup"

if ($confirmation -ne "YES") {
    Write-Host "❌ Cleanup cancelled" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🗑️  Starting cleanup..." -ForegroundColor Cyan
Write-Host ""

$removedCount = 0
$failedCount = 0

foreach ($op in $CleanupOperations) {
    $fullPath = Join-Path $RootPath $op.Path
    
    if (Test-Path $fullPath) {
        try {
            Remove-Item -Path $fullPath -Recurse -Force -ErrorAction Stop
            Write-Host "  ✅ Removed: $($op.Path)" -ForegroundColor Green
            $removedCount++
        } catch {
            Write-Host "  ❌ Failed to remove: $($op.Path)" -ForegroundColor Red
            Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Gray
            $failedCount++
        }
    }
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "✨ Cleanup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Removed: $removedCount items" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "  ❌ Failed: $failedCount items" -ForegroundColor Red
}
if (-not $SkipBackup) {
    Write-Host "  📦 Backup: $BackupPath" -ForegroundColor Yellow
}
Write-Host ""

# Show final clean structure
Write-Host "📁 Clean workspace structure:" -ForegroundColor Cyan
Write-Host ""
Write-Host "HouseRenovators-api/" -ForegroundColor White
Write-Host "├── backend/              # FastAPI backend code only" -ForegroundColor Gray
Write-Host "│   ├── app/" -ForegroundColor Gray
Write-Host "│   ├── requirements.txt" -ForegroundColor Gray
Write-Host "│   └── Dockerfile" -ForegroundColor Gray
Write-Host "├── frontend/            # React PWA code only" -ForegroundColor Gray
Write-Host "│   ├── src/" -ForegroundColor Gray
Write-Host "│   └── package.json" -ForegroundColor Gray
Write-Host "├── automation/          # DevOps scripts" -ForegroundColor Gray
Write-Host "├── config/              # Configuration files" -ForegroundColor Gray
Write-Host "├── docs/               # Documentation" -ForegroundColor Gray
Write-Host "├── scripts/            # Utility scripts" -ForegroundColor Gray
Write-Host "└── README.md" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ Your workspace is now clean and organized!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Test your backend: cd backend && uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "  2. Test your frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "  3. Commit changes: git add . && git commit -m 'Clean up duplicate files'" -ForegroundColor White
Write-Host ""
