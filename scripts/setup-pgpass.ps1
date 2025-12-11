# Setup pgpass.conf for PostgreSQL password-less authentication
# This eliminates interactive password prompts for psql

Write-Host "Setting up pgpass.conf for Supabase PostgreSQL..." -ForegroundColor Cyan

# Read DATABASE_URL from .env file
$envFile = Join-Path $PSScriptRoot '..\' '.env'
if (-not (Test-Path $envFile)) {
    Write-Host "❌ Error: .env file not found at $envFile" -ForegroundColor Red
    exit 1
}

$databaseUrl = Get-Content $envFile | Where-Object { $_ -match '^DATABASE_URL=' } | ForEach-Object { $_ -replace '^DATABASE_URL=', '' }

if (-not $databaseUrl) {
    Write-Host "❌ Error: DATABASE_URL not found in .env file" -ForegroundColor Red
    exit 1
}

# Parse DATABASE_URL: postgresql+asyncpg://user:pass@host:port/db
if ($databaseUrl -match 'postgresql\+?asyncpg?://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+)') {
    $pgUser = $matches[1]
    $pgPass = $matches[2]
    $pgHost = $matches[3]
    $pgPort = $matches[4]
    $pgDb = $matches[5]
} else {
    Write-Host "❌ Error: Could not parse DATABASE_URL format" -ForegroundColor Red
    exit 1
}

# Create pgpass directory and file
$pgpassDir = Join-Path $env:APPDATA 'postgresql'
Write-Host "Creating directory: $pgpassDir"
New-Item -ItemType Directory -Path $pgpassDir -Force | Out-Null

$pgpassFile = Join-Path $pgpassDir 'pgpass.conf'
Write-Host "Writing password to: $pgpassFile"

# Write the single-line entry: hostname:port:database:username:password
# Use $() to prevent PowerShell from treating ':' as scope separator
$entry = "$($pgHost):$($pgPort):$($pgDb):$($pgUser):$($pgPass)"
Set-Content -Path $pgpassFile -Value $entry -NoNewline

# Restrict file access to the current user (remove inheritance then grant read to user)
Write-Host "Restricting file permissions to current user only..."
icacls $pgpassFile /inheritance:r | Out-Null
icacls $pgpassFile /grant:r "$($env:USERNAME):R" | Out-Null

Write-Host ""
Write-Host "✅ pgpass.conf created successfully!" -ForegroundColor Green
Write-Host "   File: $pgpassFile" -ForegroundColor Gray
Write-Host "   Permissions: Read-only for $($env:USERNAME)" -ForegroundColor Gray
Write-Host ""
Write-Host "Now you can run psql without password prompts:" -ForegroundColor Yellow
Write-Host '   $clean = $env:DATABASE_URL -replace "\\+asyncpg", ""' -ForegroundColor Gray
Write-Host '   psql $clean -c "\d permits"' -ForegroundColor Gray
Write-Host ""
