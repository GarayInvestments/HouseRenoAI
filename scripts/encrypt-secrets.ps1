# Simple Secret Encryption Script
# Encrypts .env and credentials for safe Git commit
# No GPG required - uses Windows Data Protection API (DPAPI)

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("encrypt", "decrypt", "help")]
    [string]$Action = "help"
)

$secretFiles = @(
    ".env",
    "config/house-renovators-credentials.json"
)

function Show-Help {
    Write-Host "🔒 Secret Encryption Tool" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Encrypts secrets for safe Git commit"
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\scripts\encrypt-secrets.ps1 -Action encrypt"
    Write-Host "  .\scripts\encrypt-secrets.ps1 -Action decrypt"
    Write-Host ""
    Write-Host "Files encrypted:" -ForegroundColor Yellow
    foreach ($file in $secretFiles) {
        Write-Host "  - $file"
    }
    Write-Host ""
    Write-Host "Encrypted files (safe to commit):" -ForegroundColor Green
    foreach ($file in $secretFiles) {
        Write-Host "  - $file.encrypted"
    }
}

function Encrypt-Secrets {
    Write-Host "🔒 Encrypting secrets..." -ForegroundColor Cyan
    Write-Host ""
    
    $password = Read-Host "Enter encryption password" -AsSecureString
    $confirmPassword = Read-Host "Confirm password" -AsSecureString
    
    # Convert SecureStrings to plain text for comparison
    $pwd1 = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
    $pwd2 = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($confirmPassword))
    
    if ($pwd1 -ne $pwd2) {
        Write-Host "❌ Passwords don't match!" -ForegroundColor Red
        return
    }
    
    $encryptedCount = 0
    
    foreach ($file in $secretFiles) {
        if (Test-Path $file) {
            try {
                # Read file content
                $content = Get-Content $file -Raw
                
                # Encrypt using AES
                $aes = [System.Security.Cryptography.Aes]::Create()
                $aes.Key = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
                    [System.Text.Encoding]::UTF8.GetBytes($pwd1))
                $aes.GenerateIV()
                
                $encryptor = $aes.CreateEncryptor()
                $plainBytes = [System.Text.Encoding]::UTF8.GetBytes($content)
                $encryptedBytes = $encryptor.TransformFinalBlock($plainBytes, 0, $plainBytes.Length)
                
                # Combine IV + encrypted data
                $result = $aes.IV + $encryptedBytes
                $base64 = [Convert]::ToBase64String($result)
                
                # Save encrypted version
                $encryptedFile = "$file.encrypted"
                Set-Content $encryptedFile $base64
                
                Write-Host "✅ Encrypted: $file → $encryptedFile" -ForegroundColor Green
                $encryptedCount++
                
                # Clean up
                $aes.Dispose()
            }
            catch {
                Write-Host "❌ Failed to encrypt $file : $_" -ForegroundColor Red
            }
        }
        else {
            Write-Host "⚠️  File not found: $file" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "📋 Summary: $encryptedCount files encrypted" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. git add *.encrypted"
    Write-Host "2. git commit -m 'Add encrypted secrets'"
    Write-Host "3. git push"
    Write-Host ""
    Write-Host "⚠️  Remember your password - you'll need it to decrypt!" -ForegroundColor Yellow
}

function Decrypt-Secrets {
    Write-Host "🔓 Decrypting secrets..." -ForegroundColor Cyan
    Write-Host ""
    
    $password = Read-Host "Enter decryption password" -AsSecureString
    $pwd = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
    
    $decryptedCount = 0
    
    foreach ($file in $secretFiles) {
        $encryptedFile = "$file.encrypted"
        
        if (Test-Path $encryptedFile) {
            try {
                # Read encrypted content
                $base64 = Get-Content $encryptedFile -Raw
                $encryptedData = [Convert]::FromBase64String($base64)
                
                # Extract IV (first 16 bytes) and encrypted content
                $aes = [System.Security.Cryptography.Aes]::Create()
                $aes.Key = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
                    [System.Text.Encoding]::UTF8.GetBytes($pwd))
                $aes.IV = $encryptedData[0..15]
                
                $decryptor = $aes.CreateDecryptor()
                $encryptedBytes = $encryptedData[16..($encryptedData.Length - 1)]
                $decryptedBytes = $decryptor.TransformFinalBlock($encryptedBytes, 0, $encryptedBytes.Length)
                $content = [System.Text.Encoding]::UTF8.GetString($decryptedBytes)
                
                # Ensure directory exists
                $dir = Split-Path $file -Parent
                if ($dir -and !(Test-Path $dir)) {
                    New-Item -ItemType Directory -Path $dir -Force | Out-Null
                }
                
                # Save decrypted content
                Set-Content $file $content
                
                Write-Host "✅ Decrypted: $encryptedFile → $file" -ForegroundColor Green
                $decryptedCount++
                
                # Clean up
                $aes.Dispose()
            }
            catch {
                Write-Host "❌ Failed to decrypt $encryptedFile : $_" -ForegroundColor Red
                Write-Host "   (Wrong password or corrupted file)" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "⚠️  Encrypted file not found: $encryptedFile" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "📋 Summary: $decryptedCount files decrypted" -ForegroundColor Cyan
    Write-Host ""
    if ($decryptedCount -gt 0) {
        Write-Host "✅ Secrets ready! You can now:" -ForegroundColor Green
        Write-Host "   - Run backend: python -m uvicorn app.main:app --reload"
        Write-Host "   - Run frontend: cd frontend && npm run dev"
    }
}

# Main execution
switch ($Action) {
    "encrypt" { Encrypt-Secrets }
    "decrypt" { Decrypt-Secrets }
    "help" { Show-Help }
    default { Show-Help }
}
