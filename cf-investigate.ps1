# Cloudflare Pages Investigation Script
# Check the current configuration for house-renovators-ai

param(
    [string]$ApiToken = "",
    [string]$AccountId = "",
    [string]$ProjectName = "house-renovators-ai"
)

if (-not $ApiToken) {
    Write-Host "❌ Cloudflare API Token required" -ForegroundColor Red
    Write-Host "Get your token from: https://dash.cloudflare.com/profile/api-tokens" -ForegroundColor Yellow
    Write-Host "Usage: .\cf-investigate.ps1 -ApiToken 'your_token' -AccountId 'your_account_id'" -ForegroundColor Green
    exit 1
}

$Headers = @{
    "Authorization" = "Bearer $ApiToken"
    "Content-Type" = "application/json"
}

Write-Host "🔍 Investigating Cloudflare Pages Configuration" -ForegroundColor Cyan
Write-Host "=" * 50

try {
    # Get account info
    if (-not $AccountId) {
        Write-Host "📋 Getting account information..." -ForegroundColor Blue
        $accountsResponse = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/accounts" -Headers $Headers
        if ($accountsResponse.success) {
            $AccountId = $accountsResponse.result[0].id
            Write-Host "✅ Account ID: $AccountId" -ForegroundColor Green
        }
    }

    # List all Pages projects
    Write-Host "`n📂 Listing Cloudflare Pages projects..." -ForegroundColor Blue
    $projectsResponse = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/accounts/$AccountId/pages/projects" -Headers $Headers
    
    if ($projectsResponse.success) {
        Write-Host "✅ Found $($projectsResponse.result.Count) Pages projects:" -ForegroundColor Green
        foreach ($project in $projectsResponse.result) {
            Write-Host "  📁 $($project.name)" -ForegroundColor White
            Write-Host "     URL: $($project.canonical_deployment.url)" -ForegroundColor Gray
            Write-Host "     Environment: $($project.canonical_deployment.environment)" -ForegroundColor Gray
            Write-Host ""
        }
        
        # Check specific project
        $targetProject = $projectsResponse.result | Where-Object { $_.name -eq $ProjectName }
        if ($targetProject) {
            Write-Host "🎯 Found target project: $ProjectName" -ForegroundColor Green
            Write-Host "   Production URL: $($targetProject.canonical_deployment.url)" -ForegroundColor White
            
            # Get project details
            $projectDetailResponse = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/accounts/$AccountId/pages/projects/$ProjectName" -Headers $Headers
            if ($projectDetailResponse.success) {
                $project = $projectDetailResponse.result
                Write-Host "`n📋 Project Details:" -ForegroundColor Blue
                Write-Host "   Repository: $($project.source.config.repo_name)" -ForegroundColor White
                Write-Host "   Branch: $($project.source.config.production_branch)" -ForegroundColor White
                Write-Host "   Build Command: $($project.build_config.build_command)" -ForegroundColor White
                Write-Host "   Output Directory: $($project.build_config.destination_dir)" -ForegroundColor White
                
                # Get environment variables
                Write-Host "`n🔧 Environment Variables:" -ForegroundColor Blue
                try {
                    $envResponse = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/accounts/$AccountId/pages/projects/$ProjectName/env_vars" -Headers $Headers
                    if ($envResponse.success -and $envResponse.result.Count -gt 0) {
                        foreach ($env in $envResponse.result) {
                            Write-Host "   $($env.name): $($env.value)" -ForegroundColor White
                        }
                    } else {
                        Write-Host "   No environment variables configured" -ForegroundColor Gray
                    }
                } catch {
                    Write-Host "   ⚠️ Could not fetch environment variables" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Host "❌ Project '$ProjectName' not found" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Failed to list projects: $($projectsResponse.errors)" -ForegroundColor Red
    }

} catch {
    Write-Host "❌ API Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Verify the VITE_API_URL environment variable points to: https://houserenoai.onrender.com" -ForegroundColor White
Write-Host "2. Check if Pages project is connected to the correct GitHub repository" -ForegroundColor White
Write-Host "3. Ensure build settings are correct for React/Vite application" -ForegroundColor White