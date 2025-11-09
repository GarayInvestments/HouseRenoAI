# Setting Up HouseRenovators-API on a New Machine

## Prerequisites
- Python 3.13+
- Node.js 18+ (for frontend)
- Git
- PowerShell (Windows) or Bash (Mac/Linux)

## Quick Setup

### 1. Clone Repository
```powershell
git clone https://github.com/GarayInvestments/HouseRenoAI.git
cd HouseRenoAI
```

### 2. Backend Setup

#### Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Mac/Linux
```

#### Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Setup Environment Variables
Create `.env` file in project root:

```env
# Google Sheets API
SHEET_ID=your_google_sheet_id_here
GOOGLE_SERVICE_ACCOUNT_FILE=config/house-renovators-credentials.json

# OpenAI API
OPENAI_API_KEY=sk-proj-your_key_here

# QuickBooks OAuth2
QUICKBOOKS_CLIENT_ID=your_qb_client_id_here
QUICKBOOKS_CLIENT_SECRET=your_qb_client_secret_here
QUICKBOOKS_REDIRECT_URI=https://houserenoai.onrender.com/v1/quickbooks/callback
QUICKBOOKS_ENVIRONMENT=production  # or 'sandbox'

# Security
JWT_SECRET_KEY=your_random_secret_key_here
JWT_ALGORITHM=HS256

# API Settings
API_VERSION=v1
```

#### Add Google Service Account Credentials
Place your `house-renovators-credentials.json` in `config/` folder:
```powershell
# Copy from secure location (1Password, encrypted USB, etc.)
cp /path/to/secure/house-renovators-credentials.json config/
```

### 3. Frontend Setup
```powershell
cd frontend
npm install

# Create frontend/.env
@"
VITE_API_URL=http://localhost:8000
"@ | Out-File -FilePath .env -Encoding utf8
```

### 4. Test Installation
```powershell
# Terminal 1 - Backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Visit: http://localhost:5173

---

## Detailed Instructions

### Option 1: Manual Transfer (Most Secure)

**From OLD machine:**
1. Export environment variables to encrypted file:
   ```powershell
   # Export .env securely
   $content = Get-Content .env
   $content | Out-File -FilePath secrets-backup.txt -Encoding utf8
   
   # Encrypt file (Windows)
   Compress-Archive -Path secrets-backup.txt, config/house-renovators-credentials.json -DestinationPath secrets-encrypted.zip
   # Add password to zip manually
   ```

2. Transfer `secrets-encrypted.zip` via:
   - Encrypted USB drive
   - Secure cloud (1Password, BitWarden, LastPass)
   - Direct cable transfer
   - **NOT email or unencrypted cloud**

**On NEW machine:**
1. Extract encrypted zip
2. Place `.env` in project root
3. Place `house-renovators-credentials.json` in `config/`
4. Delete extracted files after setup
5. Delete `secrets-encrypted.zip` from old machine

### Option 2: Password Manager (Recommended)

**Using 1Password/BitWarden:**

1. **OLD Machine**: Store secrets in password manager:
   - Create "HouseRenovators Env Vars" entry
   - Add each `.env` variable as a field
   - Attach `house-renovators-credentials.json` as document
   - Tag as "development", "server-credentials"

2. **NEW Machine**: 
   - Install password manager
   - Retrieve credentials
   - Recreate `.env` file
   - Download service account JSON

### Option 3: Secure Cloud Storage

**Using Encrypted Cloud (Tresorit, Cryptomator, etc.):**

1. Upload encrypted backup to secure cloud
2. Download on new machine
3. Decrypt and place files
4. Delete from cloud after setup (optional)

---

## Environment Variables Reference

### Critical Secrets (Never Commit!)
- `OPENAI_API_KEY` - Get from OpenAI dashboard
- `JWT_SECRET_KEY` - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `QUICKBOOKS_CLIENT_SECRET` - From QuickBooks Developer Portal
- `GOOGLE_SERVICE_ACCOUNT_FILE` - JSON file path (file itself in `config/`)

### Semi-Public (OK in Render dashboard, not in Git)
- `SHEET_ID` - Google Sheet ID from URL
- `QUICKBOOKS_CLIENT_ID` - From QB Developer Portal
- `QUICKBOOKS_REDIRECT_URI` - Your production callback URL

### Public (Can be in Git if needed)
- `API_VERSION` - Usually "v1"
- `JWT_ALGORITHM` - Usually "HS256"
- `QUICKBOOKS_ENVIRONMENT` - "production" or "sandbox"

---

## Security Checklist

### ✅ Before Leaving Old Machine:
- [ ] Backup `.env` to secure location
- [ ] Backup `config/house-renovators-credentials.json`
- [ ] Export any local SQLite databases (if any)
- [ ] Note installed VS Code extensions
- [ ] Commit all uncommitted code changes

### ✅ On New Machine:
- [ ] Clone repo
- [ ] Create `.env` from secure backup
- [ ] Add service account JSON to `config/`
- [ ] Verify `.gitignore` excludes secrets
- [ ] Test backend startup (no errors about missing env vars)
- [ ] Test frontend connection to backend
- [ ] Delete temporary credential files
- [ ] Lock password manager

### ✅ Verify Secrets Are Protected:
```powershell
# Check what Git would commit
git status
git add --dry-run .

# These should be listed in .gitignore:
# - .env
# - config/*.json
# - *.pem
# - *.key
```

---

## Common Issues

### "GOOGLE_SERVICE_ACCOUNT_FILE not found"
**Fix**: Ensure `config/house-renovators-credentials.json` exists and path in `.env` is correct.

### "Invalid OPENAI_API_KEY"
**Fix**: Check key starts with `sk-proj-` or `sk-` and has no extra spaces/newlines.

### "JWT_SECRET_KEY not set"
**Fix**: Generate new key:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### QuickBooks OAuth Fails
**Fix**: 
1. Verify `QUICKBOOKS_REDIRECT_URI` matches QB Developer Portal exactly
2. Check `QUICKBOOKS_CLIENT_ID` and `QUICKBOOKS_CLIENT_SECRET`
3. Ensure correct environment (production vs sandbox)

---

## Automated Setup Script

See `scripts/setup/setup-env.ps1` for automated environment setup.

---

## Production Deployment

After local setup works, deploy to Render:

### Backend (Render)
1. Push code to GitHub
2. Render auto-deploys from `main` branch
3. Set environment variables in Render Dashboard:
   - All variables from `.env`
   - Add `GOOGLE_SERVICE_ACCOUNT_BASE64` (see deployment docs)

### Frontend (Cloudflare Pages)
1. Linked to GitHub repo
2. Auto-deploys on push to `main`
3. Set `VITE_API_URL=https://houserenoai.onrender.com` in Cloudflare settings

---

## Security Best Practices

1. **Never commit secrets to Git**
   - Use `.gitignore`
   - Check with `git status` before every commit

2. **Rotate credentials periodically**
   - QuickBooks tokens: Refresh every 100 days
   - JWT secret: Change if compromised
   - Service account: Rotate annually

3. **Use different credentials per environment**
   - Development: Separate QB sandbox app
   - Production: Production QB app
   - Testing: Mock credentials

4. **Backup securely**
   - Use password manager
   - Encrypted backups only
   - Test restoration process

5. **Access control**
   - Limit who has production credentials
   - Use separate service accounts per developer
   - Enable 2FA on all accounts

---

## Getting Credentials

### Google Service Account JSON
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. IAM & Admin → Service Accounts
4. Find "house-renovators" service account
5. Keys → Add Key → Create New Key → JSON
6. Download and rename to `house-renovators-credentials.json`

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new secret key
3. Copy immediately (shown only once)
4. Add to `.env` as `OPENAI_API_KEY`

### QuickBooks Credentials
1. Go to [QuickBooks Developer Portal](https://developer.intuit.com)
2. My Apps → Select your app
3. Keys & credentials
4. Copy Client ID and Client Secret
5. Add to `.env`

### JWT Secret Key
Generate locally (never retrieve from external source):
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Quick Copy-Paste Commands

### Complete Backend Setup (Windows)
```powershell
# Clone and setup
git clone https://github.com/GarayInvestments/HouseRenoAI.git
cd HouseRenoAI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Copy credentials (adjust paths)
cp "C:\SecureBackup\.env" .
cp "C:\SecureBackup\house-renovators-credentials.json" config\

# Test
python -m uvicorn app.main:app --reload
```

### Complete Frontend Setup
```powershell
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

---

## Need Help?

- Check `docs/TROUBLESHOOTING.md`
- Review Render logs: `render logs -r srv-d44ak76uk2gs73a3psig --limit 100 --confirm`
- Test OpenAI connection: `python -c "from app.services.openai_service import openai_service; print('OK')"`
