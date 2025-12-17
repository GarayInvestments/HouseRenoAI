# Enables repo-managed git hooks via core.hooksPath
# Usage:
#   .\scripts\setup\enable-githooks.ps1

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$hooksPath = Join-Path $repoRoot '.githooks'

if (-not (Test-Path $hooksPath)) {
  throw "Hooks directory not found: $hooksPath"
}

Push-Location $repoRoot
try {
  git config core.hooksPath .githooks

  $current = (git config --get core.hooksPath)
  Write-Host "✅ Git hooks enabled: core.hooksPath=$current"
  Write-Host "   Hook: .githooks/pre-commit (runs frontend build when frontend files are staged)"
  Write-Host "   Bypass: git commit --no-verify"
}
finally {
  Pop-Location
}
