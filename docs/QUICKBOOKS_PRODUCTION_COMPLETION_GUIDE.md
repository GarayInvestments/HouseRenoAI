# QuickBooks Production Checklist - Step by Step Guide

**Date**: November 6, 2025  
**Status**: Ready to complete all checklist items

---

## ✅ COMPLETED: Legal Pages Created

### Privacy Policy
- **URL**: `https://portal.houserenovatorsllc.com/privacy`
- **File**: `frontend/src/pages/PrivacyPolicy.jsx`
- **Status**: ✅ Created and ready to deploy

### Terms of Service
- **URL**: `https://portal.houserenovatorsllc.com/terms`
- **File**: `frontend/src/pages/TermsOfService.jsx`
- **Status**: ✅ Created and ready to deploy

---

## 📋 COMPLETE INTUIT DEVELOPER CHECKLIST

### Step 1: Add Redirect URIs ⏱️ (5 minutes)

1. **Go to Intuit Developer Dashboard**: https://developer.intuit.com/
2. Click your app → **Keys & credentials**
3. Scroll to **Redirect URIs** section
4. Click **Add URI**

**Add these URIs**:
```
https://api.houserenovatorsllc.com/v1/quickbooks/callback
```

**Optional (for enhanced functionality)**:
```
https://api.houserenovatorsllc.com/v1/quickbooks/disconnect
```

5. Click **Save**

---

### Step 2: Add Privacy Policy & Terms ⏱️ (2 minutes)

**IMPORTANT**: Deploy frontend first to make URLs live!

1. In Intuit Dashboard → Your App
2. Find "Add your app's end-user license agreement and privacy policy"
3. Click to expand

**Enter these URLs**:
```
Privacy Policy: https://portal.houserenovatorsllc.com/privacy
Terms of Service: https://portal.houserenovatorsllc.com/terms
```

4. Click **Save**

---

### Step 3: Add Host Domain & Launch URL ⏱️ (3 minutes)

1. Find "Add your app's host domain, launch URL, and disconnect URL"
2. Click to expand

**Enter**:
```
Host Domain: houserenovatorsllc.com
Launch URL: https://portal.houserenovatorsllc.com
Disconnect URL: https://api.houserenovatorsllc.com/v1/quickbooks/disconnect
```

3. Click **Save**

---

### Step 4: Select App Category ⏱️ (1 minute)

1. Find "Select at least one category for your app"
2. Click to expand

**Select**:
- Primary Category: **Construction**
- Secondary Category: **Accounting** or **Business Management**

3. Click **Save**

---

### Step 5: Regulated Industries ⏱️ (1 minute)

1. Find "Tell us about any regulated industries that use your app"
2. Click to expand

**Answer**: 
- ☐ No regulated industries (unless you handle healthcare/finance data)

3. Click **Save**

---

### Step 6: Where App is Hosted ⏱️ (2 minutes)

1. Find "Tell us where your app is hosted"
2. Click to expand

**Answer**:
```
Hosting Type: Cloud-based
Providers: 
- Backend: Render.com (https://api.houserenovatorsllc.com)
- Frontend: Cloudflare Pages (https://portal.houserenovatorsllc.com)

Security: 
- SSL/TLS encryption
- OAuth 2.0 authentication
- Secure token storage
```

3. Click **Save**

---

### Step 7: Compliance Section ⏱️ (30-40 minutes)

This section includes security and compliance questions. Answer honestly:

**Common Questions**:
1. **Data Security**:
   - Yes, we use HTTPS/TLS encryption
   - Yes, we implement OAuth 2.0
   - Yes, we store tokens securely (Google Sheets with encryption)

2. **Data Handling**:
   - We access: Customer data, invoices, estimates, company info
   - Data is used for: Syncing with project management, generating reports
   - Data is stored in: Google Sheets (encrypted at rest)

3. **Third-Party Sharing**:
   - We share data with: OpenAI (for AI features), Google (for storage)
   - Purpose: AI analysis, data storage
   - Security: Encrypted transmission, secure APIs

4. **User Control**:
   - Users can disconnect QuickBooks anytime
   - Users can export their data
   - Users can delete their account

5. **Compliance Certifications**:
   - SOC 2 (if applicable)
   - GDPR compliance (data protection)
   - PCI DSS (if handling payments directly)

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Deploy Frontend to Cloudflare Pages

```bash
# In frontend directory
cd frontend
npm run build

# Deploy to Cloudflare Pages
# (This will make privacy & terms pages live)
```

**Verify URLs are live**:
- https://portal.houserenovatorsllc.com/privacy
- https://portal.houserenovatorsllc.com/terms

---

### Step 2: Update Backend Environment (Already Done ✅)

```bash
QB_REDIRECT_URI=https://api.houserenovatorsllc.com/v1/quickbooks/callback
```

**Status**: Already updated in Render ✅

---

### Step 3: Complete Intuit Checklist (Follow steps above)

**Estimated Time**: 40-60 minutes total
- App details: ~15 minutes
- Compliance: ~30-40 minutes

---

### Step 4: Get Production Credentials

Once checklist is 100% complete:

1. Go to **Production** tab in Intuit Dashboard
2. Copy **Production Client ID**
3. Copy **Production Client Secret**

---

### Step 5: Update Backend with Production Credentials

**In Render Dashboard**:

```bash
# Update these environment variables:
QB_CLIENT_ID=<production_client_id>
QB_CLIENT_SECRET=<production_client_secret>
QB_ENVIRONMENT=production
```

**Or via API**:
```powershell
# Use the Render API script we created earlier
# Update QB_CLIENT_ID, QB_CLIENT_SECRET, QB_ENVIRONMENT
```

---

### Step 6: Test Production OAuth

1. **Visit**: https://api.houserenovatorsllc.com/v1/quickbooks/auth
2. **Login** with real QuickBooks account
3. **Authorize** the app
4. **Verify** tokens saved to Google Sheets
5. **Test**: https://api.houserenovatorsllc.com/v1/quickbooks/status

---

## ✅ VERIFICATION CHECKLIST

After completing all steps:

- [ ] Privacy policy live at `/privacy`
- [ ] Terms of service live at `/terms`
- [ ] Redirect URI added in Intuit dashboard
- [ ] All app details completed (100%)
- [ ] Compliance section completed (100%)
- [ ] Production credentials obtained
- [ ] Backend updated with production credentials
- [ ] `QB_ENVIRONMENT=production` in Render
- [ ] OAuth flow tested with real account
- [ ] Tokens persisting to Google Sheets
- [ ] All API endpoints working
- [ ] Invoice creation tested
- [ ] Customer sync tested

---

## 📊 PROGRESS TRACKER

| Task | Time | Status |
|------|------|--------|
| ✅ Create privacy policy | 5 min | DONE |
| ✅ Create terms of service | 5 min | DONE |
| ✅ Update App.jsx routing | 2 min | DONE |
| ⏳ Deploy frontend | 5 min | PENDING |
| ⏳ Add redirect URIs | 5 min | PENDING |
| ⏳ Add privacy/terms URLs | 2 min | PENDING |
| ⏳ Add host domain | 3 min | PENDING |
| ⏳ Select categories | 1 min | PENDING |
| ⏳ Regulated industries | 1 min | PENDING |
| ⏳ Hosting information | 2 min | PENDING |
| ⏳ Compliance questions | 40 min | PENDING |
| ⏳ Get production credentials | 2 min | PENDING |
| ⏳ Update backend env vars | 5 min | PENDING |
| ⏳ Test production OAuth | 5 min | PENDING |

**Total Estimated Time**: ~80 minutes
**Time Saved by Copilot**: ~20 minutes (legal pages created automatically)

---

## 🎯 NEXT IMMEDIATE ACTIONS

1. **Commit legal pages to Git**:
```bash
git add frontend/src/pages/PrivacyPolicy.jsx
git add frontend/src/pages/TermsOfService.jsx
git add frontend/src/App.jsx
git commit -m "feat: Add privacy policy and terms of service pages for QuickBooks production"
git push origin main
```

2. **Deploy frontend to Cloudflare Pages**
   - Push triggers auto-deploy
   - Wait 2-3 minutes for build
   - Verify pages are live

3. **Open Intuit Dashboard**
   - https://developer.intuit.com/
   - Start completing checklist items
   - Work through each section systematically

4. **Complete compliance section**
   - Answer all security questions
   - Provide data handling details
   - Submit for review if required

5. **Get production credentials and deploy**

---

## 📞 SUPPORT

If you encounter issues:
- **Intuit Support**: https://help.developer.intuit.com/
- **QuickBooks API Docs**: https://developer.intuit.com/app/developer/qbo/docs/
- **Compliance Help**: Review Intuit's compliance guide

---

**Ready to proceed?** Let's commit these changes and deploy the frontend!
