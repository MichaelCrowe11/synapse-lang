# 🚀 LAUNCH: Deploy Crowe Code & Synapse-Code

**Status:** ✅ Production Ready
**Time to Deploy:** ⏱️ 2 minutes
**Difficulty:** ⭐ Easy

---

## 🎯 ONE-CLICK DEPLOY

Click this button to deploy to Vercel instantly:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/MichaelCrowe11/synapse-lang&project-name=crowe-synapse-code&repository-name=synapse-lang&root-directory=dashboard&build-command=npm%20run%20build&install-command=npm%20install%20--legacy-peer-deps&framework=nextjs)

**This will:**
1. Clone your repository
2. Configure the project automatically
3. Deploy to production
4. Give you a live URL

---

## 📋 MANUAL DEPLOYMENT (Vercel Dashboard)

### Step 1: Go to Vercel
Visit: **https://vercel.com/new**

### Step 2: Import Repository
- Click "Import Git Repository"
- Select: `MichaelCrowe11/synapse-lang`
- Click "Import"

### Step 3: Configure Project

**Copy these settings exactly:**

```
Project Name:       crowe-synapse-code
Framework Preset:   Next.js
Root Directory:     dashboard

Build Settings:
  Build Command:    npm run build
  Output Directory: .next
  Install Command:  npm install --legacy-peer-deps
  Development Command: npm run dev

Git Configuration:
  Production Branch: claude/crowe-synapse-design-implementation-011CV1Giih4dDDD7XY39HKkS
  (or use main branch if you've merged)
```

### Step 4: Deploy
Click the big **"Deploy"** button

---

## 💻 CLI DEPLOYMENT (Advanced)

### Prerequisites
```bash
npm install -g vercel
```

### Option A: With Browser Login
```bash
cd /home/user/synapse-lang/dashboard

# Login (opens browser)
vercel login

# Deploy to production
vercel --prod
```

### Option B: With Token
```bash
# Get token from: https://vercel.com/account/tokens
export VERCEL_TOKEN='your-token-here'

cd /home/user/synapse-lang/dashboard

# Deploy
vercel --prod --yes --token $VERCEL_TOKEN
```

### Option C: Use the Launch Script
```bash
cd /home/user/synapse-lang/dashboard
./launch.sh
```

---

## 📺 What Happens During Deployment

```
[1/6] 📦 Installing dependencies...     (~30 seconds)
[2/6] 🔨 Building Next.js app...        (~60 seconds)
[3/6] ⚡ Optimizing bundle...           (~20 seconds)
[4/6] 📤 Uploading to edge network...   (~15 seconds)
[5/6] 🌐 Configuring routes...          (~10 seconds)
[6/6] ✅ Going live!                    (~5 seconds)

Total time: ~2-3 minutes
```

---

## 🎉 After Deployment

You'll receive a production URL like:
```
https://crowe-synapse-code.vercel.app
```

### Available Routes:
- **Home**: `https://your-url.vercel.app/`
  - Brand selection page with Crowe Code and Synapse-Code cards

- **Crowe Code**: `https://your-url.vercel.app/crowe-code`
  - Neural network visualization (150 nodes, 6 layers)
  - Obsidian glass spheres with circuit patterns
  - Electric blue & plasma purple theme
  - Interactive 3D controls

- **Synapse-Code**: `https://your-url.vercel.app/synapse-code`
  - L-System mycelial growth (5 iterations)
  - Organic glass spheres with flow patterns
  - Bioluminescent teal & amber theme
  - Anastomosis (hyphal fusion) visualization

---

## ✅ Post-Deployment Checklist

After deployment, verify:

- [ ] Home page loads and displays both brand cards
- [ ] Crowe Code page renders neural network
- [ ] Neural network animates and responds to mouse
- [ ] Obsidian glass spheres visible and reflective
- [ ] Synapse-Code page shows mycelial growth
- [ ] Mycelial network grows and branches
- [ ] Organic glass spheres have internal flow
- [ ] Anastomosis connections visible
- [ ] All pages work on mobile
- [ ] No console errors
- [ ] HTTPS enabled (automatic)
- [ ] Share links work correctly

---

## 🔧 Troubleshooting

### Build Fails
**Error:** `Failed to compile`
**Solution:** Check that `Install Command` is set to `npm install --legacy-peer-deps`

### 3D Scenes Don't Render
**Error:** Black screen on /crowe-code or /synapse-code
**Solution:**
- Check browser console for WebGL errors
- Verify browser supports WebGL 2.0
- Try in Chrome/Edge (best support)

### Slow Loading
**Issue:** Pages take long to load
**Solution:**
- This is normal for first visit (3D assets)
- Subsequent visits are cached
- Consider enabling Vercel's Edge Cache

### 404 Errors
**Error:** "404 This page could not be found"
**Solution:**
- Verify `Root Directory` is set to `dashboard`
- Check deployment logs for build errors

---

## 📊 Performance Expectations

**First Load:**
- Home: ~1.5s
- Crowe Code: ~3.0s (Three.js bundle)
- Synapse-Code: ~3.0s (Three.js bundle)

**Cached Load:**
- All pages: <0.5s

**Frame Rate:**
- Target: 60 FPS
- Typical: 45-60 FPS (depends on GPU)
- Mobile: 30-45 FPS

**Bundle Sizes:**
- Home: 130 KB
- Crowe Code: 88.8 KB (+ shared 87.5 KB)
- Synapse-Code: 88.8 KB (+ shared 87.5 KB)

---

## 🎨 Custom Domain (Optional)

### Add Custom Domain
1. Go to project settings in Vercel
2. Click "Domains"
3. Add: `crowe.yourdomain.com`
4. Update DNS with provided CNAME records
5. Wait for SSL certificate (automatic)

### Recommended Setup:
```
Main site:    synapse-lang.com (existing Flask on Fly.io)
3D Experience: crowe.synapse-lang.com (Next.js on Vercel)
```

---

## 🔐 Environment Variables (Optional)

If you need environment variables:

1. Go to project settings in Vercel
2. Click "Environment Variables"
3. Add:
   ```
   NEXT_PUBLIC_API_GATEWAY_URL=your-api-url
   ```
4. Redeploy for changes to take effect

---

## 📈 Monitoring

### View Analytics
- Visit: https://vercel.com/dashboard
- Select your project
- Click "Analytics" tab

### Metrics Available:
- Page views
- Unique visitors
- Average load time
- Error rate
- Top pages
- Device breakdown
- Geographic distribution

---

## 🚀 READY TO LAUNCH?

**Easiest Method:** Click the Deploy to Vercel button at the top ☝️

**Manual Method:** Follow the Vercel Dashboard steps above

**CLI Method:** Use the launch script or manual commands

---

**Questions?** Check the [PRODUCTION_READINESS.md](./PRODUCTION_READINESS.md) for detailed analysis.

**Need Help?** All the code is ready to go - just click deploy! 🎉
