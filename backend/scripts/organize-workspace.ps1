#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Organize documentation and Python scripts in HouseRenovators-api workspace

.DESCRIPTION
    This script organizes:
    - Documentation files into proper structure
    - Python utility scripts into organized folders
    - Removes deprecated/duplicate files
    - Creates a clean, maintainable structure

.EXAMPLE
    .\organize-workspace.ps1
    .\organize-workspace.ps1 -DryRun
#>

param(
    [switch]$DryRun,
    [switch]$SkipBackup
)

$ErrorActionPreference = "Stop"
$RootPath = Split-Path -Parent $PSScriptRoot

Write-Host "📚 House Renovators Workspace Organization Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Create backup unless skipped
if (-not $SkipBackup -and -not $DryRun) {
    $BackupTimestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
    $BackupPath = Join-Path $RootPath "organization-backup-$BackupTimestamp"
    
    Write-Host "📦 Creating backup at: $BackupPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    
    # Backup root level files we'll modify
    $rootFiles = Get-ChildItem -Path $RootPath -File | Where-Object { 
        $_.Extension -eq ".md" -or $_.Extension -eq ".py" -or $_.Name -eq "test_chat.json"
    }
    
    foreach ($file in $rootFiles) {
        Copy-Item -Path $file.FullName -Destination $BackupPath -Force
    }
    
    Write-Host "  ✅ Backed up $(($rootFiles | Measure-Object).Count) files" -ForegroundColor Green
    Write-Host ""
}

# Define organization plan
$OrganizationPlan = @{
    "Documentation" = @{
        "Keep" = @(
            @{ Source = "README.md"; Dest = "README.md"; Category = "Main" },
            @{ Source = "API_DOCUMENTATION.md"; Dest = "docs/API_DOCUMENTATION.md"; Category = "Core Docs" },
            @{ Source = "DEPLOYMENT.md"; Dest = "docs/DEPLOYMENT.md"; Category = "Core Docs" },
            @{ Source = "TROUBLESHOOTING.md"; Dest = "docs/TROUBLESHOOTING.md"; Category = "Core Docs" },
            @{ Source = "PROJECT_SETUP.md"; Dest = "docs/PROJECT_SETUP.md"; Category = "Core Docs" },
            @{ Source = "WORKFLOW_GUIDE.md"; Dest = "docs/WORKFLOW_GUIDE.md"; Category = "Core Docs" }
        )
        "Archive" = @(
            @{ Source = "SESSION_SUMMARY_NOV_3_2025.md"; Reason = "Historical session log" },
            @{ Source = "SHEETS_VERIFICATION_COMPLETE.md"; Reason = "Completed setup log" },
            @{ Source = "BACKEND_ACCESS_SETUP.md"; Reason = "Completed setup log" },
            @{ Source = "BACKEND_ACCESS_VERIFIED.md"; Reason = "Completed setup log" },
            @{ Source = "FRONTEND_REBUILD_SUMMARY.md"; Reason = "Completed rebuild log" },
            @{ Source = "FRONTEND_BACKEND_INTEGRATION.md"; Reason = "Integration already complete" },
            @{ Source = "SYSTEM_CHECK_REPORT.md"; Reason = "Old system check" }
        )
        "Delete" = @(
            @{ Source = "fdsdf.md"; Reason = "Random/test file" },
            @{ Source = "DEPLOY_NOW.md"; Reason = "Duplicate of DEPLOYMENT.md" },
            @{ Source = "DEPLOYMENT_GUIDE.md"; Reason = "Duplicate of DEPLOYMENT.md" }
        )
    }
    "PythonScripts" = @{
        "Organize" = @(
            @{ Source = "test_google_access.py"; Dest = "scripts/testing/test_google_access.py"; Category = "Testing" },
            @{ Source = "test_drive_access.py"; Dest = "scripts/testing/test_drive_access.py"; Category = "Testing" },
            @{ Source = "verify_sheets_schema.py"; Dest = "scripts/testing/verify_sheets_schema.py"; Category = "Testing" },
            @{ Source = "setup_sheet_access.py"; Dest = "scripts/setup/setup_sheet_access.py"; Category = "Setup" }
        )
        "Keep" = @(
            @{ Source = "scripts/create-perfect-base64.py"; Category = "Utility" },
            @{ Source = "scripts/simple-fix.py"; Category = "Utility" }
        )
        "Delete" = @(
            @{ Source = "app/main_updated.py"; Reason = "Backup/deprecated version" },
            @{ Source = "app/config_updated.py"; Reason = "Backup/deprecated version" }
        )
    }
    "OtherFiles" = @{
        "Archive" = @(
            @{ Source = "test_chat.json"; Reason = "Test file - archive" }
        )
        "Delete" = @(
            @{ Source = "cf-investigate.ps1"; Reason = "One-off investigation script" }
        )
    }
}

# Count items
$moveCount = ($OrganizationPlan.Documentation.Keep | Measure-Object).Count + 
             ($OrganizationPlan.PythonScripts.Organize | Measure-Object).Count
$archiveCount = ($OrganizationPlan.Documentation.Archive | Measure-Object).Count + 
                ($OrganizationPlan.OtherFiles.Archive | Measure-Object).Count
$deleteCount = ($OrganizationPlan.Documentation.Delete | Measure-Object).Count + 
               ($OrganizationPlan.PythonScripts.Delete | Measure-Object).Count + 
               ($OrganizationPlan.OtherFiles.Delete | Measure-Object).Count

Write-Host "🔍 Analysis Complete" -ForegroundColor Yellow
Write-Host "  📦 Files to move/organize: $moveCount" -ForegroundColor Cyan
Write-Host "  🗄️  Files to archive: $archiveCount" -ForegroundColor Yellow
Write-Host "  🗑️  Files to delete: $deleteCount" -ForegroundColor Red
Write-Host ""

# Show organization plan
Write-Host "📋 Organization Plan:" -ForegroundColor Cyan
Write-Host ""

Write-Host "📚 Documentation:" -ForegroundColor White
Write-Host ""
Write-Host "  ✅ Keep & Organize:" -ForegroundColor Green
foreach ($item in $OrganizationPlan.Documentation.Keep) {
    $sourcePath = Join-Path $RootPath $item.Source
    if (Test-Path $sourcePath) {
        Write-Host "    $($item.Source) → $($item.Dest)" -ForegroundColor Gray
    }
}
Write-Host ""

Write-Host "  🗄️  Archive (move to docs/archive/):" -ForegroundColor Yellow
foreach ($item in $OrganizationPlan.Documentation.Archive) {
    $sourcePath = Join-Path $RootPath $item.Source
    if (Test-Path $sourcePath) {
        Write-Host "    $($item.Source) - $($item.Reason)" -ForegroundColor Gray
    }
}
Write-Host ""

Write-Host "  🗑️  Delete:" -ForegroundColor Red
foreach ($item in $OrganizationPlan.Documentation.Delete) {
    $sourcePath = Join-Path $RootPath $item.Source
    if (Test-Path $sourcePath) {
        Write-Host "    $($item.Source) - $($item.Reason)" -ForegroundColor Gray
    }
}
Write-Host ""

Write-Host "🐍 Python Scripts:" -ForegroundColor White
Write-Host ""
Write-Host "  ✅ Organize:" -ForegroundColor Green
foreach ($item in $OrganizationPlan.PythonScripts.Organize) {
    $sourcePath = Join-Path $RootPath $item.Source
    if (Test-Path $sourcePath) {
        Write-Host "    $($item.Source) → $($item.Dest)" -ForegroundColor Gray
    }
}
Write-Host ""

Write-Host "  🗑️  Delete:" -ForegroundColor Red
foreach ($item in $OrganizationPlan.PythonScripts.Delete) {
    $sourcePath = Join-Path $RootPath $item.Source
    if (Test-Path $sourcePath) {
        Write-Host "    $($item.Source) - $($item.Reason)" -ForegroundColor Gray
    }
}
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run without -DryRun flag to perform organization" -ForegroundColor Cyan
    exit 0
}

# Confirm before proceeding
$totalChanges = $moveCount + $archiveCount + $deleteCount
Write-Host "⚠️  WARNING: This will modify $totalChanges files" -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Type 'YES' to proceed with organization"

if ($confirmation -ne "YES") {
    Write-Host "❌ Organization cancelled" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔨 Starting organization..." -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0

# Create necessary directories
$dirsToCreate = @(
    "docs/archive",
    "scripts/testing",
    "scripts/setup"
)

foreach ($dir in $dirsToCreate) {
    $fullPath = Join-Path $RootPath $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  📁 Created directory: $dir" -ForegroundColor Cyan
    }
}
Write-Host ""

# Move/organize documentation
Write-Host "📚 Organizing documentation..." -ForegroundColor Cyan
foreach ($item in $OrganizationPlan.Documentation.Keep) {
    $sourcePath = Join-Path $RootPath $item.Source
    $destPath = Join-Path $RootPath $item.Dest
    
    if (Test-Path $sourcePath) {
        # Skip if source and dest are the same
        if ($sourcePath -eq $destPath) {
            Write-Host "  ⏭️  Skipped: $($item.Source) (already in place)" -ForegroundColor Gray
            continue
        }
        
        try {
            $destDir = Split-Path -Parent $destPath
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            
            Move-Item -Path $sourcePath -Destination $destPath -Force
            Write-Host "  ✅ Moved: $($item.Source) → $($item.Dest)" -ForegroundColor Green
            $successCount++
        } catch {
            Write-Host "  ❌ Failed: $($item.Source) - $($_.Exception.Message)" -ForegroundColor Red
            $failCount++
        }
    }
}

# Archive documentation
foreach ($item in $OrganizationPlan.Documentation.Archive) {
    $sourcePath = Join-Path $RootPath $item.Source
    $destPath = Join-Path $RootPath "docs/archive/$($item.Source)"
    
    if (Test-Path $sourcePath) {
        try {
            Move-Item -Path $sourcePath -Destination $destPath -Force
            Write-Host "  🗄️  Archived: $($item.Source)" -ForegroundColor Yellow
            $successCount++
        } catch {
            Write-Host "  ❌ Failed: $($item.Source) - $($_.Exception.Message)" -ForegroundColor Red
            $failCount++
        }
    }
}

# Delete documentation
foreach ($item in $OrganizationPlan.Documentation.Delete) {
    $sourcePath = Join-Path $RootPath $item.Source
    
    if (Test-Path $sourcePath) {
        try {
            Remove-Item -Path $sourcePath -Force
            Write-Host "  🗑️  Deleted: $($item.Source)" -ForegroundColor Red
            $successCount++
        } catch {
            Write-Host "  ❌ Failed: $($item.Source) - $($_.Exception.Message)" -ForegroundColor Red
            $failCount++
        }
    }
}
Write-Host ""

# Organize Python scripts
Write-Host "🐍 Organizing Python scripts..." -ForegroundColor Cyan
foreach ($item in $OrganizationPlan.PythonScripts.Organize) {
    $sourcePath = Join-Path $RootPath $item.Source
    $destPath = Join-Path $RootPath $item.Dest
    
    if (Test-Path $sourcePath) {
        try {
            $destDir = Split-Path -Parent $destPath
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            
            Move-Item -Path $sourcePath -Destination $destPath -Force
            Write-Host "  ✅ Moved: $($item.Source) → $($item.Dest)" -ForegroundColor Green
            $successCount++
        } catch {
            Write-Host "  ❌ Failed: $($item.Source) - $($_.Exception.Message)" -ForegroundColor Red
            $failCount++
        }
    }
}

# Delete Python scripts
foreach ($item in $OrganizationPlan.PythonScripts.Delete) {
    $sourcePath = Join-Path $RootPath $item.Source
    
    if (Test-Path $sourcePath) {
        try {
            Remove-Item -Path $sourcePath -Force
            Write-Host "  🗑️  Deleted: $($item.Source)" -ForegroundColor Red
            $successCount++
        } catch {
            Write-Host "  ❌ Failed: $($item.Source) - $($_.Exception.Message)" -ForegroundColor Red
            $failCount++
        }
    }
}
Write-Host ""

# Archive other files
Write-Host "📦 Archiving other files..." -ForegroundColor Cyan
foreach ($item in $OrganizationPlan.OtherFiles.Archive) {
    $sourcePath = Join-Path $RootPath $item.Source
    $destPath = Join-Path $RootPath "docs/archive/$($item.Source)"
    
    if (Test-Path $sourcePath) {
        try {
            Move-Item -Path $sourcePath -Destination $destPath -Force
            Write-Host "  🗄️  Archived: $($item.Source)" -ForegroundColor Yellow
            $successCount++
        } catch {
            Write-Host "  ❌ Failed: $($item.Source) - $($_.Exception.Message)" -ForegroundColor Red
            $failCount++
        }
    }
}

# Delete other files
foreach ($item in $OrganizationPlan.OtherFiles.Delete) {
    $sourcePath = Join-Path $RootPath $item.Source
    
    if (Test-Path $sourcePath) {
        try {
            Remove-Item -Path $sourcePath -Force
            Write-Host "  🗑️  Deleted: $($item.Source)" -ForegroundColor Red
            $successCount++
        } catch {
            Write-Host "  ❌ Failed: $($item.Source) - $($_.Exception.Message)" -ForegroundColor Red
            $failCount++
        }
    }
}
Write-Host ""

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "✨ Organization Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Successfully organized: $successCount files" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "  ❌ Failed: $failCount files" -ForegroundColor Red
}
if (-not $SkipBackup) {
    Write-Host "  📦 Backup: $BackupPath" -ForegroundColor Yellow
}
Write-Host ""

# Show final structure
Write-Host "📁 Organized workspace structure:" -ForegroundColor Cyan
Write-Host ""
Write-Host "HouseRenovators-api/" -ForegroundColor White
Write-Host "├── README.md                      # Main documentation" -ForegroundColor Gray
Write-Host "├── docs/" -ForegroundColor White
Write-Host "│   ├── API_DOCUMENTATION.md       # API reference" -ForegroundColor Gray
Write-Host "│   ├── DEPLOYMENT.md              # Production deployment" -ForegroundColor Gray
Write-Host "│   ├── TROUBLESHOOTING.md         # Debug guide" -ForegroundColor Gray
Write-Host "│   ├── PROJECT_SETUP.md           # Development setup" -ForegroundColor Gray
Write-Host "│   ├── WORKFLOW_GUIDE.md          # Development workflow" -ForegroundColor Gray
Write-Host "│   └── archive/                   # Historical logs" -ForegroundColor Gray
Write-Host "├── scripts/" -ForegroundColor White
Write-Host "│   ├── setup/                     # Setup utilities" -ForegroundColor Gray
Write-Host "│   │   └── setup_sheet_access.py" -ForegroundColor Gray
Write-Host "│   ├── testing/                   # Test scripts" -ForegroundColor Gray
Write-Host "│   │   ├── test_google_access.py" -ForegroundColor Gray
Write-Host "│   │   ├── test_drive_access.py" -ForegroundColor Gray
Write-Host "│   │   └── verify_sheets_schema.py" -ForegroundColor Gray
Write-Host "│   └── *.ps1                      # PowerShell utilities" -ForegroundColor Gray
Write-Host "├── backend/                       # FastAPI backend" -ForegroundColor White
Write-Host "└── frontend/                      # React PWA" -ForegroundColor White
Write-Host ""

Write-Host "✅ Your workspace is now organized!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review docs/ folder for all documentation" -ForegroundColor White
Write-Host "  2. Check scripts/testing/ for test utilities" -ForegroundColor White
Write-Host "  3. Commit changes: git add . && git commit -m 'Organize documentation and scripts'" -ForegroundColor White
Write-Host ""
