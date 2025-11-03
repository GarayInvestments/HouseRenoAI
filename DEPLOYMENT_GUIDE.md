# 🚀 House Renovators AI - Deployment Guide

**Last Updated:** November 3, 2025  
**Status:** Ready for Production Deployment

---

## Quick Deployment Summary

### ✅ Backend - ALREADY DEPLOYED
- **Platform:** Render.com
- **URL:** https://houserenoai.onrender.com
- **Status:** Live and operational
- **Auto-deploy:** Configured from GitHub

### 🚀 Frontend - READY TO DEPLOY
- **Build:** Complete (257KB, 73KB gzipped)
- **Platform:** Cloudflare Pages (recommended)
- **Status:** Built and tested locally
- **Next:** Deploy to production

---

## Frontend Deployment - Cloudflare Pages

### Method 1: GitHub Integration (Recommended)

#### Step 1: Push to GitHub
```powershell
cd frontend
git add .
git commit -m "Complete UI redesign - production ready"
git push origin main
```

#### Step 2: Create Cloudflare Pages Project
1. Go to https://dash.cloudflare.com
2. Navigate to **Workers & Pages**
3. Click **Create application** → **Pages** → **Connect to Git**
4. Select repository: **GarayInvestments/HouseRenoAI**
5. Configure build settings:

**Build Configuration:**
```
Production branch: main
Build command: cd frontend && npm run build
Build output directory: frontend/dist
Root directory: (leave empty or set to /)
```

**Environment Variables:**
```
NODE_VERSION=18
VITE_API_URL=https://houserenoai.onrender.com
```

#### Step 3: Deploy
- Click **Save and Deploy**
- Wait for build to complete (~2-3 minutes)
- Your site will be live at: `https://your-project.pages.dev`

#### Step 4: Custom Domain (Optional)
1. Go to Pages project → **Custom domains**
2. Add domain: `portal.houserenovatorsllc.com`
3. Update DNS records as instructed by Cloudflare
4. Wait for SSL certificate provisioning (~15 minutes)

---

### Method 2: Wrangler CLI

#### Install Wrangler
```powershell
npm install -g wrangler
wrangler login
```

#### Deploy
```powershell
cd frontend
npm run build
wrangler pages deploy dist --project-name=house-renovators-ai
```

---

### Method 3: Direct Upload

#### Step 1: Build
```powershell
cd frontend
npm run build
```

#### Step 2: Upload
1. Go to Cloudflare Pages dashboard
2. Click **Upload assets**
3. Upload the entire `dist` folder
4. Configure environment variables
5. Deploy

---

## Alternative Platforms

### Render Static Site

#### Step 1: Create Static Site
1. Go to https://render.com/dashboard
2. Click **New** → **Static Site**
3. Connect GitHub repository

#### Step 2: Configure
```
Build Command: cd frontend && npm install && npm run build
Publish Directory: frontend/dist
```

#### Step 3: Environment Variables
```
VITE_API_URL=https://houserenoai.onrender.com
```

### Vercel

#### Via CLI
```powershell
cd frontend
npm install -g vercel
vercel --prod
```

#### Via Dashboard
1. Go to https://vercel.com/new
2. Import `GarayInvestments/HouseRenoAI`
3. Configure:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Environment Variables:
   ```
   VITE_API_URL=https://houserenoai.onrender.com
   ```

### Netlify

#### Via CLI
```powershell
cd frontend
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

#### Via Dashboard
1. Go to https://app.netlify.com
2. Drag and drop the `frontend/dist` folder
3. Configure environment variables in Site settings

---

## Post-Deployment Checklist

### ✅ Functionality Tests
- [ ] Frontend loads correctly
- [ ] All 6 pages render (Dashboard, AI Assistant, Permits, Projects, Documents, Settings)
- [ ] Navigation works (sidebar on desktop, drawer on mobile)
- [ ] Responsive design works at different screen sizes
- [ ] API connection to backend works
- [ ] No console errors

### ✅ Responsive Tests
- [ ] Desktop (>= 1024px): Sidebar visible, hamburger hidden
- [ ] Tablet (768px - 1023px): Mobile view
- [ ] Mobile (< 768px): Drawer navigation works

### ✅ Performance Tests
- [ ] Page load time < 3 seconds
- [ ] Lighthouse score > 90
- [ ] No broken images or assets
- [ ] HTTPS working correctly

### ✅ Browser Tests
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

---

## Environment Variables

### Required
```env
VITE_API_URL=https://houserenoai.onrender.com
```

### Optional
```env
NODE_VERSION=18
VITE_ENV=production
```

---

## Monitoring & Analytics

### Cloudflare Analytics
- Automatically enabled on Cloudflare Pages
- Access via Pages project dashboard
- View traffic, performance metrics, and errors

### Google Analytics (Optional)
Add to `index.html` before deployment:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

---

## Troubleshooting

### Build Fails
**Error:** `Cannot find module`
**Solution:** Ensure all dependencies are in `package.json`:
```powershell
cd frontend
npm install
npm run build
```

### API Connection Issues
**Error:** CORS or connection refused
**Solution:** 
1. Verify `VITE_API_URL` environment variable is set
2. Check backend is running: https://houserenoai.onrender.com/health
3. Verify backend CORS settings allow your frontend domain

### Routing Issues
**Error:** 404 on page refresh
**Solution:** Add `_redirects` file to `public` folder:
```
/*    /index.html   200
```

### CSS Not Loading
**Error:** Styles not applied
**Solution:** 
1. Check `index.css` is imported in `main.jsx`
2. Verify build process completes successfully
3. Check browser console for errors

---

## Rollback Procedure

### Cloudflare Pages
1. Go to Pages project → **Deployments**
2. Find previous working deployment
3. Click **...** → **Rollback to this deployment**

### Render
1. Go to Static Site dashboard
2. Select previous deployment from dropdown
3. Click **Deploy**

---

## Custom Domain Setup

### DNS Configuration for Cloudflare
1. **Add CNAME record:**
   ```
   Type: CNAME
   Name: portal (or @)
   Content: your-project.pages.dev
   Proxy status: Proxied (orange cloud)
   ```

2. **Wait for propagation** (~15-30 minutes)

3. **SSL Certificate:** Automatically provisioned by Cloudflare

### Verify Domain
```powershell
nslookup portal.houserenovatorsllc.com
```

---

## Maintenance

### Update Frontend
```powershell
cd frontend
git pull origin main
npm install  # if package.json changed
npm run build
# Redeploy via chosen method
```

### Monitor Uptime
- Cloudflare: Built-in analytics
- External: UptimeRobot (free tier available)
- Set up alerts for downtime

---

## Performance Optimization

### Already Implemented
- ✅ Code splitting
- ✅ Minification (Vite)
- ✅ Gzip compression (Cloudflare)
- ✅ Optimized bundle size (257KB → 73KB gzipped)

### Future Improvements
- [ ] Image optimization (if adding images)
- [ ] Service worker for offline support
- [ ] CDN caching strategies
- [ ] Lazy loading for heavy components

---

## Support & Resources

### Documentation
- **Frontend Design:** `frontend/DESIGN_DOCUMENTATION.md`
- **UI Redesign:** `frontend/UI_REDESIGN_COMPLETE.md`
- **Status Summary:** `docs/STATUS_SUMMARY.md`

### Platform Documentation
- Cloudflare Pages: https://developers.cloudflare.com/pages
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs
- Netlify: https://docs.netlify.com

### Contact
For deployment issues:
1. Check platform status pages
2. Review build logs
3. Check environment variables
4. Verify backend connectivity

---

## Success Criteria

### ✅ Deployment Complete When:
- [ ] Frontend accessible via HTTPS
- [ ] All pages load correctly
- [ ] Responsive design works
- [ ] API calls successful
- [ ] No console errors
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate active
- [ ] Monitoring set up

---

**🎯 Recommended Next Step:**  
Deploy to Cloudflare Pages using Method 1 (GitHub Integration) for automatic deployments on future updates.

**Estimated Deployment Time:** 10-15 minutes  
**Difficulty:** Easy (well documented, automated process)
