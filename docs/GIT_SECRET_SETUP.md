# Git-Secret Setup Guide for HouseRenovators-API

## What is git-secret?

Git-secret encrypts your `.env` and credential files so they can be safely committed to Git. Only authorized users with the correct GPG key can decrypt them.

---

## Installation

### Prerequisites: Install GPG (Gpg4win)

1. **Download Gpg4win**:
   - Visit: https://www.gpg4win.org/download.html
   - Download the installer
   - Run installer (default options are fine)

2. **Verify installation**:
   ```powershell
   gpg --version
   # Should show: gpg (GnuPG) 2.x.x
   ```

### Install git-secret

**Option 1: Direct Download (Recommended for Windows)**
```powershell
# Download latest release
$url = "https://github.com/sobolevn/git-secret/releases/latest/download/git-secret.tar.gz"
Invoke-WebRequest -Uri $url -OutFile "$env:TEMP\git-secret.tar.gz"

# Extract (requires 7-Zip or WSL)
# Then add to PATH
```

**Option 2: Using WSL (Ubuntu/Debian)**
```bash
sudo apt-get update
sudo apt-get install git-secret
```

**Option 3: Using Scoop (if installed)**
```powershell
scoop install git-secret
```

---

## Setup for This Project

### 1. Generate GPG Key (One-time)

```powershell
# Generate your GPG key
gpg --full-generate-key

# Choose:
# - Key type: (1) RSA and RSA
# - Key size: 4096
# - Expiration: 0 (never expires) or 2y (2 years)
# - Your name: Steve Garay
# - Your email: your@email.com
# - Passphrase: (create a strong one - remember it!)

# List your keys
gpg --list-keys
# Note your key ID (looks like: 1A2B3C4D5E6F7G8H)
```

### 2. Initialize git-secret in Repo

```powershell
# In project root
git secret init

# Tell git-secret about yourself
git secret tell your@email.com  # Use email from GPG key

# Verify
git secret whoknows
# Should show your email
```

### 3. Add Files to Encrypt

```powershell
# Add secrets
git secret add .env
git secret add config/house-renovators-credentials.json

# Check what's tracked
git secret list
```

### 4. Encrypt and Commit

```powershell
# Encrypt files (creates .env.secret, etc.)
git secret hide

# Add encrypted files to Git
git add .env.secret
git add config/house-renovators-credentials.json.secret
git add .gitsecret

# Commit
git commit -m "Add encrypted secrets with git-secret"
git push
```

### 5. On New Machine

```powershell
# Clone repo
git clone https://github.com/GarayInvestments/HouseRenoAI.git
cd HouseRenoAI

# Import your GPG key (if not already on new machine)
# Export from old machine:
gpg --export-secret-keys your@email.com > private-key.asc

# Import on new machine:
gpg --import private-key.asc
# Delete private-key.asc after import!

# Decrypt secrets
git secret reveal
# Enter your GPG passphrase

# Files decrypted: .env, config/house-renovators-credentials.json
```

---

## Daily Workflow

### After Modifying Secrets

```powershell
# 1. Edit .env or credentials
notepad .env

# 2. Re-encrypt
git secret hide

# 3. Commit encrypted version
git add .env.secret
git commit -m "Update secrets"
git push

# NOTE: Never commit unencrypted .env!
```

### Pulling Updates

```powershell
git pull

# If encrypted files changed, re-decrypt
git secret reveal
```

---

## .gitignore Updates

Add these to ensure only encrypted files are committed:

```gitignore
# Unencrypted secrets (never commit)
.env
config/house-renovators-credentials.json
config/*.json
!config/.gitkeep

# Allow encrypted versions
!.env.secret
!config/*.json.secret

# git-secret files
.gitsecret/keys/random_seed
!.gitsecret/paths/
```

---

## Team Collaboration

### Adding Team Members

```powershell
# On any machine with git-secret initialized:

# 1. Get teammate's GPG public key
# They export: gpg --export --armor their@email.com > their-public-key.asc
# They send you the file

# 2. Import their key
gpg --import their-public-key.asc

# 3. Tell git-secret about them
git secret tell their@email.com

# 4. Re-encrypt for all authorized users
git secret hide -d  # -d deletes old encrypted files first

# 5. Commit
git add .gitsecret .env.secret config/*.secret
git commit -m "Add teammate to git-secret"
git push
```

### Removing Access

```powershell
# Remove user
git secret removeperson their@email.com

# Re-encrypt without them
git secret hide -d

# They can no longer decrypt future changes
```

---

## Common Commands

```powershell
# Initialize
git secret init

# Add yourself
git secret tell your@email.com

# Add files to encrypt
git secret add FILE

# List encrypted files
git secret list

# Show who can decrypt
git secret whoknows

# Encrypt all tracked files
git secret hide

# Decrypt all encrypted files
git secret reveal

# Decrypt but keep encrypted versions
git secret reveal -f

# Clean decrypted files
git secret clean

# Remove file from tracking
git secret remove FILE
```

---

## Troubleshooting

### "gpg: decryption failed: No secret key"
**Fix**: Import your private GPG key
```powershell
gpg --import private-key.asc
```

### "git-secret: command not found"
**Fix**: Add git-secret to PATH or use full path to git-secret.bat

### "gpg: signing failed: Inappropriate ioctl for device"
**Fix**: Set GPG TTY
```powershell
$env:GPG_TTY = (tty)
```

### Encrypted files out of sync with source
**Fix**: Always run `git secret hide` after editing secrets
```powershell
git secret hide -d  # -d deletes old encrypted files
```

---

## Security Best Practices

1. **Never commit unencrypted secrets**
   - Verify `.env` is in `.gitignore`
   - Check: `git status` before committing

2. **Backup your GPG key securely**
   ```powershell
   gpg --export-secret-keys your@email.com > backup-private-key.asc
   # Store in password manager or encrypted USB
   ```

3. **Use strong GPG passphrase**
   - Protects your private key
   - Required to decrypt secrets

4. **Rotate secrets periodically**
   - Change API keys annually
   - Update if teammate leaves

5. **Audit access regularly**
   ```powershell
   git secret whoknows
   ```

---

## Alternative: Simpler Encrypted Backup Script

If git-secret is too complex, use this PowerShell script:

```powershell
# encrypt-secrets.ps1
$password = Read-Host "Enter encryption password" -AsSecureString
$files = @(".env", "config/house-renovators-credentials.json")

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        $encrypted = $content | ConvertTo-SecureString -AsPlainText -Force | 
                     ConvertFrom-SecureString -SecureKey $password
        Set-Content "$file.encrypted" $encrypted
        Write-Host "✅ Encrypted: $file → $file.encrypted"
    }
}

# Commit *.encrypted files to Git
```

```powershell
# decrypt-secrets.ps1
$password = Read-Host "Enter decryption password" -AsSecureString

Get-ChildItem "*.encrypted" | ForEach-Object {
    $encrypted = Get-Content $_.FullName
    $decrypted = $encrypted | ConvertTo-SecureString -SecureKey $password | 
                 ConvertFrom-SecureString -AsPlainText
    $original = $_.FullName -replace ".encrypted$", ""
    Set-Content $original $decrypted
    Write-Host "✅ Decrypted: $_.Name → $original"
}
```

---

## Quick Decision Guide

**Use git-secret if**:
- ✅ Working in a team
- ✅ Want granular access control
- ✅ Comfortable with GPG
- ✅ Need audit trail

**Use 1Password/BitWarden if**:
- ✅ Solo developer or small team
- ✅ Want simple solution
- ✅ Already using password manager
- ✅ Don't want to learn GPG

**Use encrypted backup script if**:
- ✅ Just need basic encryption
- ✅ Single-user project
- ✅ Don't want external dependencies

---

## Status for This Project

Current state:
- ❌ GPG not installed
- ❌ git-secret not installed
- ✅ Documentation ready
- ✅ .gitignore protects secrets
- ✅ Setup scripts created

Next steps if you want to proceed:
1. Install Gpg4win: https://www.gpg4win.org/download.html
2. Follow "Setup for This Project" section above
3. I can help automate the rest

Or stick with current approach (1Password + manual transfer) which is perfectly valid!

---

## Resources

- git-secret GitHub: https://github.com/sobolevn/git-secret
- git-secret docs: https://git-secret.io/
- Gpg4win: https://www.gpg4win.org/
- GPG Guide: https://gnupg.org/documentation/
