#!/usr/bin/env pwsh
# Start the backend API server

Write-Host "Starting House Renovators API Backend..." -ForegroundColor Green

# Activate virtual environment
& ".\backend\venv\Scripts\Activate.ps1"

# Start uvicorn server
Write-Host "Starting uvicorn server on http://0.0.0.0:8000" -ForegroundColor Cyan
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
