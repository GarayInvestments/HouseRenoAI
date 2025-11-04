# GitHub Actions Setup for Cloudflare Pages Deployment

This document explains how to configure automatic deployments to Cloudflare Pages using GitHub Actions.

## Required GitHub Secrets

To enable automatic deployments, you need to add the following secrets to your GitHub repository:

### 1. CLOUDFLARE_API_TOKEN

**How to get it:**
1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Click "Create Token"
3. Use the "Edit Cloudflare Workers" template
4. Or create a custom token with these permissions:
   - Account > Cloudflare Pages > Edit
5. Copy the token

**Add to GitHub:**
1. Go to https://github.com/GarayInvestments/HouseRenoAI/settings/secrets/actions
2. Click "New repository secret"
3. Name: `CLOUDFLARE_API_TOKEN`
4. Value: Paste your token
5. Click "Add secret"

### 2. CLOUDFLARE_ACCOUNT_ID

**How to get it:**
1. Go to https://dash.cloudflare.com
2. Select your account (if you have multiple)
3. Look in the URL: `dash.cloudflare.com/[ACCOUNT_ID]/`
4. Or find it in the right sidebar of any Cloudflare dashboard page

**Current Account ID:** `3d1f227f6cbdb1108d2abd277f1726c0`

**Add to GitHub:**
1. Go to https://github.com/GarayInvestments/HouseRenoAI/settings/secrets/actions
2. Click "New repository secret"
3. Name: `CLOUDFLARE_ACCOUNT_ID`
4. Value: `3d1f227f6cbdb1108d2abd277f1726c0`
5. Click "Add secret"

### 3. VITE_API_URL (Optional)

**Add to GitHub:**
1. Go to https://github.com/GarayInvestments/HouseRenoAI/settings/secrets/actions
2. Click "New repository secret"
3. Name: `VITE_API_URL`
4. Value: `https://houserenoai.onrender.com`
5. Click "Add secret"

## How It Works

Once the secrets are configured:

1. ✅ **Automatic Deployment:** Every push to `main` branch that includes changes to `frontend/` will trigger a deployment
2. ✅ **Build Process:** GitHub Actions will install dependencies and build your frontend
3. ✅ **Deploy:** The built files are automatically deployed to Cloudflare Pages
4. ✅ **URL:** Your app will be available at https://house-renovators-ai-portal.pages.dev

## Manual Deployment

You can also trigger deployments manually:

1. Go to https://github.com/GarayInvestments/HouseRenoAI/actions
2. Select "Deploy Frontend to Cloudflare Pages"
3. Click "Run workflow"
4. Select branch and click "Run workflow"

## Monitoring Deployments

- **GitHub Actions:** https://github.com/GarayInvestments/HouseRenoAI/actions
- **Cloudflare Dashboard:** https://dash.cloudflare.com/pages/view/house-renovators-ai-portal

## Troubleshooting

### Deployment fails with "Unauthorized"
- Check that `CLOUDFLARE_API_TOKEN` is valid and has correct permissions

### Deployment fails with "Account not found"
- Verify `CLOUDFLARE_ACCOUNT_ID` is correct

### Build fails
- Check the GitHub Actions logs for specific error messages
- Ensure all dependencies are listed in `package.json`

## Next Steps

After setting up the secrets:

1. Commit and push the workflow file:
   ```bash
   git add .github/workflows/deploy-frontend.yml
   git commit -m "feat: Add GitHub Actions workflow for Cloudflare Pages deployment"
   git push origin main
   ```

2. Go to GitHub Actions to see your first automated deployment!

## Resources

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Wrangler Action Documentation](https://github.com/cloudflare/wrangler-action)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
