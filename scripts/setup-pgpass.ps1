# Setup pgpass.conf for PostgreSQL password-less authentication
# This eliminates interactive password prompts for psql

Write-Host "Setting up pgpass.conf for Supabase PostgreSQL..." -ForegroundColor Cyan

# Database connection details from .env
$pgHost = 'db.dtfjzjhxtojkgfofrmrr.supabase.co'
$pgPort = '5432'
$pgDb = 'postgres'
$pgUser = 'postgres'
$pgPass = '***REMOVED***'  # From DATABASE_URL

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
