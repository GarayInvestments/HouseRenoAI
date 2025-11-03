# 🐙 House Renovators AI Portal - GitHub API Utilities
# Comprehensive GitHub repository and workflow management

param(
    [Parameter(Position=0)]
    [ValidateSet("status", "repo", "workflows", "releases", "issues", "pr", "metrics", "help")]
    [string]$Action = "status",
    
    [string]$Owner = $env:GITHUB_OWNER,
    [string]$Repository = $env:GITHUB_REPOSITORY,
    [string]$Token = $env:GITHUB_TOKEN,
    [string]$Branch = "main",
    [string]$WorkflowId,
    [string]$TagName,
    [string]$ReleaseBody,
    [string]$IssueTitle,
    [string]$IssueBody,
    [string]$PullRequestTitle,
    [string]$PullRequestBody,
    [string]$BaseBranch = "main",
    [string]$HeadBranch,
    [int]$Days = 7,
    [switch]$Json,
    [switch]$Verbose,
    [string]$OutputFile
)

# Configuration
$BaseUrl = "https://api.github.com"
$DefaultOwner = "your-username"  # Update with actual GitHub username/org
$DefaultRepo = "HouseRenovators-api"

# Validation
if (-not $Token) {
    Write-Error "GitHub token required. Set GITHUB_TOKEN environment variable or use -Token parameter."
    exit 1
}

if (-not $Owner) {
    $Owner = $DefaultOwner
    if ($Verbose) { Write-Host "Using default owner: $Owner" -ForegroundColor Yellow }
}

if (-not $Repository) {
    $Repository = $DefaultRepo
    if ($Verbose) { Write-Host "Using default repository: $Repository" -ForegroundColor Yellow }
}

function Write-Output($message, $color = "White") {
    if ($Json -and $Action -ne "help") { return }
    Write-Host $message -ForegroundColor $color
}

function Invoke-GitHubAPI($endpoint, $method = "GET", $body = $null) {
    try {
        $headers = @{
            "Authorization" = "Bearer $Token"
            "Accept" = "application/vnd.github.v3+json"
            "User-Agent" = "HouseRenovators-PowerShell-Client/1.0"
        }
        
        $uri = "$BaseUrl$endpoint"
        if ($Verbose) { Write-Output "API Call: $method $uri" "Gray" }
        
        $params = @{
            Uri = $uri
            Method = $method
            Headers = $headers
            TimeoutSec = 60
        }
        
        if ($body) {
            $params.Body = $body | ConvertTo-Json -Depth 10
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        return $response
    } catch {
        $errorDetails = $_.Exception.Message
        if ($_.Exception.Response) {
            try {
                $errorStream = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($errorStream)
                $errorBody = $reader.ReadToEnd()
                $errorJson = $errorBody | ConvertFrom-Json
                if ($errorJson.message) {
                    $errorDetails = $errorJson.message
                }
            } catch {
                # Ignore stream reading errors
            }
        }
        throw "GitHub API error: $errorDetails"
    }
}

function Get-RepositoryStatus {
    Write-Output "`n🐙 GitHub Repository Status" "Cyan"
    Write-Output "=" * 30
    
    try {
        # Get repository information
        $repo = Invoke-GitHubAPI "/repos/$Owner/$Repository"
        
        if ($Json) {
            return $repo | ConvertTo-Json -Depth 10
        }
        
        Write-Output "Repository: $($repo.full_name)" "White"
        Write-Output "Description: $($repo.description)" "Gray"
        Write-Output "Language: $($repo.language)" "White"
        Write-Output "Stars: $($repo.stargazers_count) ⭐" "Yellow"
        Write-Output "Forks: $($repo.forks_count) 🍴" "White"
        Write-Output "Issues: $($repo.open_issues_count) 🐛" "White"
        Write-Output "Size: $([math]::Round($repo.size / 1024, 2)) MB" "Gray"
        Write-Output "Created: $(([DateTime]$repo.created_at).ToString('yyyy-MM-dd'))" "Gray"
        Write-Output "Updated: $(([DateTime]$repo.updated_at).ToString('yyyy-MM-dd HH:mm:ss'))" "Gray"
        Write-Output "Default Branch: $($repo.default_branch)" "Cyan"
        Write-Output "Private: $(if ($repo.private) { 'Yes 🔒' } else { 'No 🔓' })" "White"
        
        # Get branch information
        Write-Output "`nBranch Information:" "Cyan"
        $branches = Invoke-GitHubAPI "/repos/$Owner/$Repository/branches"
        
        foreach ($branch in $branches | Select-Object -First 5) {
            $isDefault = if ($branch.name -eq $repo.default_branch) { " (default)" } else { "" }
            $protection = if ($branch.protected) { " 🛡️" } else { "" }
            Write-Output "  • $($branch.name)$isDefault$protection" "White"
        }
        
        if ($branches.Count -gt 5) {
            Write-Output "  ... and $($branches.Count - 5) more branches" "Gray"
        }
        
        # Get recent commits
        Write-Output "`nRecent Commits:" "Cyan"
        $commits = Invoke-GitHubAPI "/repos/$Owner/$Repository/commits?per_page=5"
        
        foreach ($commit in $commits) {
            $shortSha = $commit.sha.Substring(0, 7)
            $message = $commit.commit.message.Split("`n")[0]
            if ($message.Length -gt 60) {
                $message = $message.Substring(0, 57) + "..."
            }
            $author = $commit.commit.author.name
            $date = ([DateTime]$commit.commit.author.date).ToString('MM-dd HH:mm')
            
            Write-Output "  • $shortSha $message ($author, $date)" "White"
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get repository status: $_"
        return $false
    }
}

function Get-WorkflowStatus {
    Write-Output "`n⚙️ GitHub Actions Workflows" "Green"
    Write-Output "=" * 35
    
    try {
        # Get workflows
        $workflows = Invoke-GitHubAPI "/repos/$Owner/$Repository/actions/workflows"
        
        if ($Json) {
            return $workflows | ConvertTo-Json -Depth 10
        }
        
        if ($workflows.workflows.Count -eq 0) {
            Write-Output "No workflows found" "Yellow"
            return $true
        }
        
        Write-Output "Active Workflows:" "Cyan"
        foreach ($workflow in $workflows.workflows) {
            $status = switch ($workflow.state) {
                "active" { "✅ Active" }
                "disabled_manually" { "⏸️ Disabled" }
                "disabled_inactivity" { "😴 Inactive" }
                default { "❓ $($workflow.state)" }
            }
            
            Write-Output "  $status $($workflow.name)" "White"
            Write-Output "    File: $($workflow.path)" "Gray"
            if ($workflow.badge_url) {
                Write-Output "    Badge: $($workflow.badge_url)" "Gray"
            }
        }
        
        # Get recent workflow runs
        Write-Output "`nRecent Workflow Runs:" "Cyan"
        $runs = Invoke-GitHubAPI "/repos/$Owner/$Repository/actions/runs?per_page=10"
        
        foreach ($run in $runs.workflow_runs | Select-Object -First 10) {
            $status = switch ($run.status) {
                "completed" {
                    switch ($run.conclusion) {
                        "success" { "✅" }
                        "failure" { "❌" }
                        "cancelled" { "⏹️" }
                        "skipped" { "⏭️" }
                        default { "❓" }
                    }
                }
                "in_progress" { "🔄" }
                "queued" { "⏳" }
                default { "❓" }
            }
            
            $workflow = $workflows.workflows | Where-Object { $_.id -eq $run.workflow_id } | Select-Object -First 1
            $workflowName = if ($workflow) { $workflow.name } else { "Unknown" }
            $runTime = ([DateTime]$run.created_at).ToString('MM-dd HH:mm')
            
            Write-Output "  $status $workflowName - $runTime ($($run.event))" "White"
            
            if ($run.status -eq "completed" -and $run.conclusion -eq "failure") {
                Write-Output "    🔗 $($run.html_url)" "Red"
            }
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get workflow status: $_"
        return $false
    }
}

function Get-RepoMetrics {
    Write-Output "`n📊 Repository Metrics" "Blue"
    Write-Output "=" * 25
    
    try {
        # Get repository stats
        $repo = Invoke-GitHubAPI "/repos/$Owner/$Repository"
        
        # Get contributors
        $contributors = Invoke-GitHubAPI "/repos/$Owner/$Repository/contributors"
        
        # Get languages
        $languages = Invoke-GitHubAPI "/repos/$Owner/$Repository/languages"
        
        # Get traffic (requires push access)
        $traffic = $null
        try {
            $traffic = Invoke-GitHubAPI "/repos/$Owner/$Repository/traffic/views"
        } catch {
            if ($Verbose) { Write-Output "Traffic data not accessible (requires push access)" "Yellow" }
        }
        
        if ($Json) {
            $metrics = @{
                repository = $repo
                contributors = $contributors
                languages = $languages
                traffic = $traffic
            }
            return $metrics | ConvertTo-Json -Depth 10
        }
        
        # Display metrics
        Write-Output "Repository Health:" "Cyan"
        Write-Output "  Stars: $($repo.stargazers_count)" "White"
        Write-Output "  Watchers: $($repo.watchers_count)" "White"
        Write-Output "  Forks: $($repo.forks_count)" "White"
        Write-Output "  Open Issues: $($repo.open_issues_count)" "White"
        Write-Output "  Network Count: $($repo.network_count)" "White"
        
        Write-Output "`nContributors ($($contributors.Count)):" "Cyan"
        foreach ($contributor in $contributors | Select-Object -First 5) {
            Write-Output "  • $($contributor.login): $($contributor.contributions) commits" "White"
        }
        
        if ($contributors.Count -gt 5) {
            Write-Output "  ... and $($contributors.Count - 5) more contributors" "Gray"
        }
        
        Write-Output "`nLanguages:" "Cyan"
        $totalBytes = ($languages.PSObject.Properties.Value | Measure-Object -Sum).Sum
        foreach ($lang in $languages.PSObject.Properties) {
            $percentage = [math]::Round(($lang.Value / $totalBytes) * 100, 1)
            Write-Output "  • $($lang.Name): $percentage%" "White"
        }
        
        if ($traffic) {
            Write-Output "`nTraffic (Last 14 days):" "Cyan"
            Write-Output "  Views: $($traffic.count)" "White"
            Write-Output "  Unique Visitors: $($traffic.uniques)" "White"
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get repository metrics: $_"
        return $false
    }
}

function Get-Issues {
    Write-Output "`n🐛 Repository Issues" "Red"
    Write-Output "=" * 20
    
    try {
        # Get open issues
        $issues = Invoke-GitHubAPI "/repos/$Owner/$Repository/issues?state=open&per_page=20"
        
        if ($Json) {
            return $issues | ConvertTo-Json -Depth 10
        }
        
        if ($issues.Count -eq 0) {
            Write-Output "✅ No open issues" "Green"
            return $true
        }
        
        Write-Output "Open Issues ($($issues.Count)):" "Cyan"
        foreach ($issue in $issues | Select-Object -First 10) {
            $labels = if ($issue.labels.Count -gt 0) { 
                " [" + (($issue.labels | ForEach-Object { $_.name }) -join ", ") + "]"
            } else { 
                "" 
            }
            
            $assignee = if ($issue.assignee) { " (@$($issue.assignee.login))" } else { "" }
            $created = ([DateTime]$issue.created_at).ToString('MM-dd')
            
            Write-Output "  #$($issue.number) $($issue.title)$labels$assignee ($created)" "White"
            
            if ($issue.body -and $issue.body.Length -gt 0) {
                $preview = $issue.body.Substring(0, [Math]::Min(100, $issue.body.Length)).Replace("`n", " ")
                Write-Output "    $preview..." "Gray"
            }
        }
        
        if ($issues.Count -gt 10) {
            Write-Output "  ... and $($issues.Count - 10) more issues" "Gray"
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get issues: $_"
        return $false
    }
}

function Get-PullRequests {
    Write-Output "`n🔀 Pull Requests" "Magenta"
    Write-Output "=" * 20
    
    try {
        # Get open pull requests
        $prs = Invoke-GitHubAPI "/repos/$Owner/$Repository/pulls?state=open&per_page=20"
        
        if ($Json) {
            return $prs | ConvertTo-Json -Depth 10
        }
        
        if ($prs.Count -eq 0) {
            Write-Output "✅ No open pull requests" "Green"
            return $true
        }
        
        Write-Output "Open Pull Requests ($($prs.Count)):" "Cyan"
        foreach ($pr in $prs | Select-Object -First 10) {
            $status = if ($pr.draft) { "📝 Draft" } else { "🔍 Ready" }
            $author = $pr.user.login
            $created = ([DateTime]$pr.created_at).ToString('MM-dd')
            $checks = ""
            
            # Get PR status
            try {
                $statuses = Invoke-GitHubAPI "/repos/$Owner/$Repository/commits/$($pr.head.sha)/status"
                $checks = switch ($statuses.state) {
                    "success" { " ✅" }
                    "failure" { " ❌" }
                    "pending" { " ⏳" }
                    default { "" }
                }
            } catch {
                # Ignore status check errors
            }
            
            Write-Output "  #$($pr.number) $($pr.title) ($status, @$author, $created)$checks" "White"
            Write-Output "    $($pr.head.ref) → $($pr.base.ref)" "Gray"
            
            if ($pr.body -and $pr.body.Length -gt 0) {
                $preview = $pr.body.Substring(0, [Math]::Min(100, $pr.body.Length)).Replace("`n", " ")
                Write-Output "    $preview..." "Gray"
            }
        }
        
        if ($prs.Count -gt 10) {
            Write-Output "  ... and $($prs.Count - 10) more pull requests" "Gray"
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get pull requests: $_"
        return $false
    }
}

function Get-Releases {
    Write-Output "`n🚀 Releases" "DarkYellow"
    Write-Output "=" * 15
    
    try {
        # Get releases
        $releases = Invoke-GitHubAPI "/repos/$Owner/$Repository/releases?per_page=10"
        
        if ($Json) {
            return $releases | ConvertTo-Json -Depth 10
        }
        
        if ($releases.Count -eq 0) {
            Write-Output "No releases found" "Yellow"
            return $true
        }
        
        Write-Output "Recent Releases:" "Cyan"
        foreach ($release in $releases | Select-Object -First 5) {
            $prerelease = if ($release.prerelease) { " (pre-release)" } else { "" }
            $draft = if ($release.draft) { " (draft)" } else { "" }
            $published = ([DateTime]$release.published_at).ToString('yyyy-MM-dd')
            
            Write-Output "  🏷️ $($release.tag_name)$prerelease$draft - $published" "White"
            Write-Output "    $($release.name)" "Gray"
            
            if ($release.assets.Count -gt 0) {
                Write-Output "    Assets: $($release.assets.Count) files" "Gray"
                Write-Output "    Downloads: $(($release.assets | Measure-Object download_count -Sum).Sum)" "Gray"
            }
        }
        
        return $true
        
    } catch {
        Write-Error "Failed to get releases: $_"
        return $false
    }
}

function Show-Help {
    Write-Host @"
🐙 House Renovators AI Portal - GitHub API Utilities

USAGE:
    .\github-api.ps1 [ACTION] [OPTIONS]

ACTIONS:
    status      Show repository status and basic information
    repo        Show detailed repository information
    workflows   Show GitHub Actions workflows and runs
    releases    Show releases and tags
    issues      Show open issues
    pr          Show open pull requests
    metrics     Show repository metrics and statistics
    help        Show this help message

OPTIONS:
    -Owner              Repository owner/organization (or GITHUB_OWNER env var)
    -Repository         Repository name (or GITHUB_REPOSITORY env var)
    -Token              GitHub personal access token (or GITHUB_TOKEN env var)
    -Branch             Branch name (default: main)
    -WorkflowId         Specific workflow ID for workflow operations
    -TagName            Tag name for release operations
    -ReleaseBody        Release description
    -IssueTitle         Issue title for creation
    -IssueBody          Issue description
    -PullRequestTitle   PR title for creation
    -PullRequestBody    PR description
    -BaseBranch         Base branch for PR (default: main)
    -HeadBranch         Head branch for PR
    -Days               Number of days for historical data (default: 7)
    -Json               Output in JSON format
    -Verbose            Enable verbose output
    -OutputFile         Save output to file

EXAMPLES:
    # Check repository status
    .\github-api.ps1 status

    # Show workflow status
    .\github-api.ps1 workflows -Owner "username" -Repository "repo-name"

    # Get repository metrics in JSON
    .\github-api.ps1 metrics -Json

    # Show open issues
    .\github-api.ps1 issues

    # Show pull requests
    .\github-api.ps1 pr

ENVIRONMENT VARIABLES:
    GITHUB_TOKEN       GitHub personal access token
    GITHUB_OWNER       Repository owner/organization
    GITHUB_REPOSITORY  Repository name

TOKEN PERMISSIONS:
    The GitHub token should have the following scopes:
    • repo (for private repositories)
    • public_repo (for public repositories)
    • workflow (for GitHub Actions)
    • read:org (for organization data)

For more information, visit: https://docs.github.com/en/rest
"@ -ForegroundColor Cyan
}

# Main execution
try {
    switch ($Action.ToLower()) {
        "status" { 
            Get-RepositoryStatus 
        }
        "repo" { 
            Get-RepositoryStatus 
        }
        "workflows" { 
            Get-WorkflowStatus 
        }
        "releases" { 
            Get-Releases 
        }
        "issues" { 
            Get-Issues 
        }
        "pr" { 
            Get-PullRequests 
        }
        "metrics" { 
            Get-RepoMetrics 
        }
        "help" { 
            Show-Help 
        }
        default { 
            Write-Error "Unknown action: $Action. Use 'help' for usage information."
            exit 1
        }
    }
    
    if ($OutputFile -and -not $Json) {
        Write-Output "`n💾 Results saved to: $OutputFile" "Green"
    }
    
} catch {
    Write-Error "Script execution failed: $_"
    exit 1
}