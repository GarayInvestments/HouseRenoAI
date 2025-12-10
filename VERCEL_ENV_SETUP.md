# Vercel Environment Variables Setup Guide

After deploying to Vercel, add these environment variables in the Vercel dashboard:
https://vercel.com/your-project/settings/environment-variables

## Required Variables:

```bash
# Google Sheets
SHEET_ID=1Wp1MZFTA2rCm55IMAkNmh6z_2-vEa0mdhEkcufQVnnI
GOOGLE_SERVICE_ACCOUNT_BASE64=<base64 encoded credentials>

# OpenAI
OPENAI_API_KEY=sk-proj-...

# QuickBooks
QB_CLIENT_ID=ABFDraKIQB1PnJAX1c7yjoEln1XYV7qP74D3r84ivPNLlAG9US
QB_CLIENT_SECRET=eXJ7tbgoiKbqYzQMEjmTIMAH0gNaWJMy4mKVKPTq
QB_REDIRECT_URI=https://your-app.vercel.app/v1/quickbooks/callback
QB_ENVIRONMENT=production

# Database (Supabase)
DATABASE_URL=postgresql+asyncpg://postgres:***REMOVED***@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres

# Environment
ENVIRONMENT=production
DEBUG=false
```

## To encode service account:
```powershell
$content = Get-Content config/house-renovators-credentials.json -Raw
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($content))
```
