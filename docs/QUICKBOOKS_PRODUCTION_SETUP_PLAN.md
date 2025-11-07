# QuickBooks Production Setup Checklist

**Date**: November 6, 2025  
**Current Status**: Development credentials active, Production locked

---

## 🎯 Immediate Action: Add Redirect URI

### Step 1: Navigate to Redirect URIs
1. In Intuit Developer Dashboard
2. Click "Add your app's host domain, launch URL, and disconnect URL"
3. Expand the dropdown

### Step 2: Add Production Redirect URI
```
Redirect URI: https://api.houserenovatorsllc.com/v1/quickbooks/callback
```

### Step 3: Save Changes
- Click "Save" or "Add"
- Verify it appears in the list

---

## 📝 Complete Checklist for Production

### App Details (17% complete - 8 min remaining)

#### ✅ 1. Review Developer Portal Profile
- Already completed

#### ⏳ 2. Add Privacy Policy & Terms
**Create these pages**:
- Privacy Policy URL: `https://portal.houserenovatorsllc.com/privacy`
- Terms of Service URL: `https://portal.houserenovatorsllc.com/terms`

**Quick Template Option**:
- Use free privacy policy generator: https://www.privacypolicygenerator.info/
- Customize for House Renovators LLC
- Upload to Cloudflare Pages

#### ⏳ 3. Add URLs
- **Host Domain**: `houserenovatorsllc.com`
- **Launch URL**: `https://portal.houserenovatorsllc.com`
- **Redirect URI**: `https://api.houserenovatorsllc.com/v1/quickbooks/callback`
- **Disconnect URL**: `https://api.houserenovatorsllc.com/v1/quickbooks/disconnect`

#### ⏳ 4. Select App Category
**Recommended**: 
- Primary: Construction
- Secondary: Business Management

#### ⏳ 5. Regulated Industries
**Answer**: No (unless dealing with HIPAA/PCI/etc.)

#### ⏳ 6. Where App is Hosted
**Answer**: 
- Cloud-based application
- Hosting: Render.com (backend) + Cloudflare Pages (frontend)

---

### Compliance (0% complete - 40 min remaining)

This section typically includes:
- Security questionnaire
- Data handling policies
- OAuth implementation review
- Compliance certifications

**Note**: Can complete later if just testing with sandbox

---

## 🚀 Recommended Approach

### Phase 1: Keep Using Sandbox (Now)
```bash
# Current configuration works perfectly
QB_ENVIRONMENT=sandbox
QB_REDIRECT_URI=https://api.houserenovatorsllc.com/v1/quickbooks/callback

# Test with:
# - Sandbox company
# - Test data
# - Development credentials
```

**Advantages**:
- ✅ Already working
- ✅ No production checklist needed
- ✅ Free unlimited testing
- ✅ Reset data anytime

### Phase 2: Production Later (When Ready)
```bash
# After completing checklist
QB_ENVIRONMENT=production
# Use production credentials from Intuit

# Deploy with:
# - Real QuickBooks companies
# - Live customer data
# - Production credentials
```

---

## ⚡ Quick Start: Add Redirect URI Only

**Minimum requirement to test with new domain**:

1. **Open Intuit Dashboard**: https://developer.intuit.com/
2. **Go to your app** → Keys & credentials
3. **Find "Redirect URIs"** section
4. **Click "Add URI"**
5. **Enter**: `https://api.houserenovatorsllc.com/v1/quickbooks/callback`
6. **Save**

**Then test**:
```bash
# Visit OAuth URL
https://api.houserenovatorsllc.com/v1/quickbooks/auth

# Should redirect to QuickBooks login
# Then back to your callback with tokens
```

---

## 📊 Current vs Production Comparison

| Feature | Sandbox (Current) | Production (Future) |
|---------|------------------|---------------------|
| **Cost** | Free | Free |
| **Data** | Test data | Real customer data |
| **Companies** | Test companies | Live QuickBooks accounts |
| **Setup Time** | 5 minutes | 40-60 minutes |
| **Credentials** | Development keys | Production keys |
| **Checklist** | Not required | Required |
| **Invoice Limits** | Unlimited | Unlimited |
| **Reset Data** | Anytime | Never (live data) |

---

## ✅ Decision Time

### Option 1: Stay in Sandbox (Recommended for Now)
**Pros**:
- Already working perfectly
- No checklist needed
- Test without risk
- Switch to production anytime

**Action**: Just add redirect URI, keep testing

### Option 2: Complete Production Checklist (60 min)
**Pros**:
- Access real QuickBooks data
- Production-ready credentials
- Professional setup

**Action**: Complete all checklist items

---

## 🔧 Files That Need Changes (If Going Production)

### Backend (.env on Render)
```bash
# Change this:
QB_ENVIRONMENT=sandbox

# To this:
QB_ENVIRONMENT=production
QB_CLIENT_ID=<production_client_id>
QB_CLIENT_SECRET=<production_client_secret>
```

### No Other Code Changes Needed
- ✅ Redirect URI already updated
- ✅ API endpoints work with both
- ✅ Token persistence works the same
- ✅ All 16 endpoints compatible

---

## 📞 Support Resources

- **Intuit Developer Docs**: https://developer.intuit.com/app/developer/qbo/docs/get-started
- **OAuth Guide**: https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0
- **Sandbox vs Production**: https://developer.intuit.com/app/developer/qbo/docs/learn/explore-the-quickbooks-online-api/sandbox

---

## 🎯 Next Actions (Your Choice)

**Immediate (5 minutes)**:
1. Add redirect URI in Intuit dashboard
2. Test OAuth with sandbox: `https://api.houserenovatorsllc.com/v1/quickbooks/auth`
3. Verify tokens save to Google Sheets
4. Continue development with sandbox

**Later (when needed)**:
1. Create privacy policy & terms pages
2. Complete production checklist (40-60 min)
3. Get production credentials
4. Switch `QB_ENVIRONMENT=production`
5. Test with real QuickBooks companies

---

**Recommendation**: Add redirect URI now, stay in sandbox for testing, switch to production when you're ready to onboard real customers.
