# Set environment variables for Cloudflare Pages project
$AccountId = "3d1f227f6cbdb1108d2abd277f1726c0"
$ProjectName = "house-renovators-ai-portal"

# You'll need to get an API token from Cloudflare Dashboard
# Go to: https://dash.cloudflare.com/profile/api-tokens
# Create token with Zone:Read, Page:Edit permissions

$ApiToken = Read-Host "Enter your Cloudflare API Token" -AsSecureString
$ApiTokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($ApiToken))

$Headers = @{
    "Authorization" = "Bearer $ApiTokenPlain"
    "Content-Type" = "application/json"
}

# Set environment variables
$EnvVars = @(
    @{
        name = "VITE_API_URL"
        value = "https://houserenoai.onrender.com"
        type = "plain_text"
    },
    @{
        name = "VITE_ENV"
        value = "production"
        type = "plain_text"
    },
    @{
        name = "VITE_ENABLE_DEBUG"
        value = "false"
        type = "plain_text"
    }
)

Write-Host "🔧 Setting environment variables for $ProjectName..." -ForegroundColor Blue

foreach ($env in $EnvVars) {
    try {
        $body = $env | ConvertTo-Json -Depth 10
        $uri = "https://api.cloudflare.com/client/v4/accounts/$AccountId/pages/projects/$ProjectName/env_vars"
        
        $response = Invoke-RestMethod -Uri $uri -Method POST -Headers $Headers -Body $body
        
        if ($response.success) {
            Write-Host "✅ Set $($env.name) = $($env.value)" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to set $($env.name): $($response.errors)" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error setting $($env.name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n🚀 Environment variables configured!" -ForegroundColor Cyan
Write-Host "Now redeploy your Pages project to use the new environment variables." -ForegroundColor Yellow