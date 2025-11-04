#!/usr/bin/env pwsh
# Start the frontend development server

Write-Host "Starting House Renovators Frontend..." -ForegroundColor Green

# Navigate to frontend directory
Set-Location -Path ".\frontend"

# Start Vite dev server
Write-Host "Starting Vite dev server..." -ForegroundColor Cyan
npm run dev
