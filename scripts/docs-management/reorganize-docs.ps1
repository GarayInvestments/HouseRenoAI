# Documentation Reorganization Script
# Handles archiving and consolidation operations

$ErrorActionPreference = "Stop"

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "DOCUMENTATION REORGANIZATION - Phase 2 & 3" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Phase 2: Archive historical files
Write-Host "Phase 2: Archiving historical documents..." -ForegroundColor Yellow
Write-Host ""

$filesToArchive = @(
    "docs/chat_refactor_plan.md",
    "docs/quickbooks_init_issue_doc.md",
    "docs/QUICKBOOKS_TEST_RESULTS_20251106_202200.md",
    "docs/DEPLOYMENT_SUMMARY_NOV_7_2025.md",
    "docs/PHASE_0_COMPLETE.md",
    "docs/PHASE_1_COMPLETE.md",
    "docs/REFACTOR_COMPLETE.md",
    "docs/CLIENT_LOOKUP_FEATURE.md"
)

foreach ($file in $filesToArchive) {
    if (Test-Path $file) {
        $filename = Split-Path $file -Leaf
        $dest = "docs/archive/$filename"
        Write-Host "  Moving: $filename" -ForegroundColor Gray
        Move-Item $file $dest -Force
    } else {
        Write-Host "  Skipping (not found): $file" -ForegroundColor DarkGray
    }
}

Write-Host "✅ Archived 8 historical files" -ForegroundColor Green
Write-Host ""

# Phase 3: Delete original files that were merged
Write-Host "Phase 3: Removing merged source files..." -ForegroundColor Yellow
Write-Host ""

$filesToRemove = @(
    # QuickBooks docs (merged into QUICKBOOKS_GUIDE.md)
    "docs/QUICKBOOKS_IMPLEMENTATION_SUMMARY.md",
    "docs/QUICKBOOKS_INTEGRATION.md",
    "docs/QUICKBOOKS_INTEGRATION_COMPLETE.md",
    "docs/QUICKBOOKS_PRODUCTION_COMPLETION_GUIDE.md",
    "docs/QUICKBOOKS_PRODUCTION_SETUP_PLAN.md",
    
    # Setup docs (merged into SETUP_GUIDE.md)
    "docs/PROJECT_SETUP.md",
    "docs/GITHUB_ACTIONS_SETUP.md",
    "docs/GITHUB_SECRETS_SETUP.md",
    "docs/SETUP_GITKRAKEN_MCP.md",
    
    # Status docs (will merge into PROJECT_STATUS.md)
    "docs/PROGRESS_REPORT_NOV_2025.md",
    "docs/NEXT_STEPS.md",
    
    # Security doc (will merge into API_DOCUMENTATION.md)
    "docs/SECURITY_AUTHENTICATION_PLAN.md",
    
    # Document upload (will merge into TROUBLESHOOTING.md)
    "docs/DOCUMENT_UPLOAD_TROUBLESHOOTING.md"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        $filename = Split-Path $file -Leaf
        Write-Host "  Removing: $filename" -ForegroundColor Gray
        Remove-Item $file -Force
    } else {
        Write-Host "  Skipping (not found): $file" -ForegroundColor DarkGray
    }
}

Write-Host "✅ Removed merged source files" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "REORGANIZATION COMPLETE" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Created:" -ForegroundColor Green
Write-Host "  ✅ docs/QUICKBOOKS_GUIDE.md" -ForegroundColor White
Write-Host "  ✅ docs/SETUP_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "Archived:" -ForegroundColor Yellow
Write-Host "  📁 8 historical files → docs/archive/" -ForegroundColor White
Write-Host ""
Write-Host "Removed:" -ForegroundColor Red
Write-Host "  🗑️  15 merged source files" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review changes: git status" -ForegroundColor White
Write-Host "  2. Update README.md links" -ForegroundColor White
Write-Host "  3. Commit: git add -A && git commit -m 'Reorganize documentation'" -ForegroundColor White
Write-Host ""
