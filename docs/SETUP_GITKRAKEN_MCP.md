# How to Enable GitKraken MCP Tools in VS Code

This guide explains how to get the GitKraken Model Context Protocol (MCP) tools working in your VS Code workspace, so GitHub Copilot can use Git operations directly.

## What Are MCP Tools?

Model Context Protocol (MCP) tools allow GitHub Copilot to interact with external services like Git, GitHub, GitLab, and Jira. The GitKraken MCP server provides these capabilities:

- **Git Operations**: add, commit, push, pull, branch, checkout, stash, blame
- **Pull Requests**: Create, review, comment, list PRs
- **Issues**: List, view, comment on GitHub/GitLab/Jira issues
- **Repository Operations**: Get file contents, view diffs, logs

## Prerequisites

1. **VS Code** with **GitHub Copilot Chat** extension installed
2. **Node.js** (v18 or later)
3. **GitKraken Account** (free tier works)

## Installation Steps

### Step 1: Install GitKraken CLI

```powershell
# Using npm
npm install -g @gitkraken/cli

# Or using Chocolatey (Windows)
choco install gitkraken-cli

# Or download from https://www.gitkraken.com/cli
```

### Step 2: Authenticate GitKraken

```powershell
# Login to GitKraken
gk auth login

# This will open a browser window to authenticate
```

### Step 3: Install GitKraken MCP Server

```powershell
# Install the MCP server package
npm install -g @gitkraken/mcp-server

# Or via the VS Code extension marketplace
# Search for "GitKraken" and install the official extension
```

### Step 4: Configure VS Code Settings

Open your **User Settings** (JSON):
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Preferences: Open User Settings (JSON)"
3. Add this configuration:

```json
{
  "github.copilot.chat.mcp.enabled": true,
  "github.copilot.chat.mcp.servers": {
    "gitkraken": {
      "command": "node",
      "args": [
        "/path/to/gitkraken-mcp-server/index.js"
      ],
      "env": {
        "GITKRAKEN_TOKEN": "your-token-here"
      }
    }
  }
}
```

**To find the MCP server path:**

```powershell
# Find where npm global packages are installed
npm root -g

# The GitKraken MCP server should be at:
# Windows: C:\Users\YourName\AppData\Roaming\npm\node_modules\@gitkraken\mcp-server
# Mac/Linux: /usr/local/lib/node_modules/@gitkraken/mcp-server
```

### Step 5: Get Your GitKraken Token

```powershell
# Get your authentication token
gk auth token

# Copy the token and add it to the VS Code settings above
```

### Step 6: Restart VS Code

Close and reopen VS Code for the changes to take effect.

## Verify Installation

Open GitHub Copilot Chat and ask:

```
@workspace Can you show me git status using GitKraken MCP tools?
```

If configured correctly, Copilot will use `mcp_gitkraken_git_status` instead of running `git status` in the terminal.

## Alternative: VS Code Extension Method

The easiest way (if available):

1. Open VS Code Extensions (`Ctrl+Shift+X`)
2. Search for "GitKraken"
3. Install the official GitKraken extension
4. The extension should auto-configure MCP for you
5. Sign in when prompted

## Troubleshooting

### "MCP tools not available"

**Check if MCP is enabled:**
```json
"github.copilot.chat.mcp.enabled": true
```

**Check server path:**
```powershell
# Verify the file exists
Test-Path "C:\Users\YourName\AppData\Roaming\npm\node_modules\@gitkraken\mcp-server\index.js"
```

### "GitKraken authentication failed"

**Re-authenticate:**
```powershell
gk auth logout
gk auth login
```

### "Command not found: node"

**Install Node.js:**
- Download from https://nodejs.org/
- Or use `choco install nodejs` (Windows with Chocolatey)

### MCP server crashes

**Check logs:**
1. Open VS Code Developer Tools: `Help` → `Toggle Developer Tools`
2. Look for errors in the Console tab
3. Search for "MCP" or "gitkraken"

## Available MCP Tools

Once configured, Copilot can use these tools:

### Git Operations
- `mcp_gitkraken_git_status` - Show git status
- `mcp_gitkraken_git_add_or_commit` - Stage and commit files
- `mcp_gitkraken_git_push` - Push commits
- `mcp_gitkraken_git_branch` - List or create branches
- `mcp_gitkraken_git_checkout` - Switch branches
- `mcp_gitkraken_git_log_or_diff` - View history or diffs
- `mcp_gitkraken_git_stash` - Stash changes
- `mcp_gitkraken_git_blame` - Show file blame

### Pull Requests
- `mcp_gitkraken_pull_request_assigned_to_me` - List your PRs
- `mcp_gitkraken_pull_request_get_detail` - Get PR details
- `mcp_gitkraken_pull_request_create` - Create new PR
- `mcp_gitkraken_pull_request_create_review` - Review a PR
- `mcp_gitkraken_pull_request_get_comments` - Get PR comments

### Issues
- `mcp_gitkraken_issues_assigned_to_me` - List your issues
- `mcp_gitkraken_issues_get_detail` - Get issue details
- `mcp_gitkraken_issues_add_comment` - Comment on issues

### Repository
- `mcp_gitkraken_repository_get_file_content` - Read remote files

## Example Usage

Once set up, you can ask Copilot:

```
"Create a new branch called feature/client-lookup"
→ Uses mcp_gitkraken_git_branch

"Show me the last 10 commits"
→ Uses mcp_gitkraken_git_log_or_diff

"Create a PR for this branch"
→ Uses mcp_gitkraken_pull_request_create

"Who last modified this line in documents.py?"
→ Uses mcp_gitkraken_git_blame
```

## Benefits Over Terminal Commands

1. **Structured Output**: Returns JSON instead of text parsing
2. **Error Handling**: Better error messages and recovery
3. **GitHub Integration**: Direct PR/issue management
4. **Multi-Provider**: Works with GitHub, GitLab, Bitbucket, Azure DevOps
5. **Context Aware**: Copilot knows exactly what the tool does

## Notes

- MCP tools are still relatively new (as of 2025)
- Some features may require GitKraken Pro subscription
- Falls back to terminal commands if MCP unavailable
- Works best with GitHub Copilot Chat, not inline suggestions

## Resources

- [GitKraken CLI Docs](https://help.gitkraken.com/gitkraken-cli/gitkraken-cli-home/)
- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [VS Code Copilot Chat Docs](https://code.visualstudio.com/docs/copilot/copilot-chat)

---

**Once configured, you'll see Copilot using MCP tools in this workspace just like in the HouseRenovators-api workspace!** 🚀
