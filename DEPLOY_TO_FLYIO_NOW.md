# 🚀 Deploy Synapse Lang to Fly.io - Manual Instructions

**Issue:** Automated deployment encountered authentication issues with Fly.io CLI.
**Solution:** Complete the deployment manually with these steps.

---

## ✅ Prerequisites (Already Done)

- [x] Critical production fixes applied
- [x] Code pushed to GitHub
- [x] fly.toml configured correctly
- [x] Dockerfile.production ready
- [x] Health endpoint `/api/health` implemented
- [x] Local testing successful (running at http://localhost:8080)

---

## 🔧 Manual Deployment Steps

### Step 1: Re-authenticate with Fly.io

Open a new terminal and run:

```bash
# Clear any cached credentials
flyctl auth logout

# Login again
flyctl auth login
```

This will open your browser. Complete the authentication flow.

### Step 2: Verify Authentication

```bash
flyctl auth whoami
```

**Expected output:**
```
Email: michael@southwestmushrooms.online
```

### Step 3: Navigate to Project

```bash
cd C:\Users\micha\synapse-lang\docs-website
```

### Step 4: Check if App Exists

```bash
flyctl apps list | grep synapse-lang-docs
```

**If app exists:** Proceed to Step 6
**If app doesn't exist:** Continue to Step 5

### Step 5: Create Fly.io App (If Needed)

```bash
flyctl apps create synapse-lang-docs
```

Select organization when prompted.

### Step 6: Deploy to Fly.io

```bash
# Deploy (this will build and deploy)
flyctl deploy

# Watch the deployment progress
# This may take 3-5 minutes
```

**Expected output:**
```
==> Building image
...
==> Pushing image to registry
...
==> Deploying...
...
--> v0 deployed successfully
```

### Step 7: Set Production Secrets

```bash
# Generate a random secret key
flyctl secrets set SECRET_KEY=$(openssl rand -hex 32)
```

### Step 8: Verify Deployment

```bash
# Check app status
flyctl status

# View logs
flyctl logs

# Test health endpoint
curl https://synapse-lang-docs.fly.dev/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "2.3.2",
  "timestamp": "2025-11-09T...",
  "service": "synapse-lang-docs"
}
```

### Step 9: Open in Browser

```bash
flyctl open
```

Or visit: https://synapse-lang-docs.fly.dev

---

## 🐛 Troubleshooting

### Issue: "You must be authenticated to view this"

**Solution:**
```bash
# Remove config files
rm ~/.fly/config.yml

# Re-login
flyctl auth login
```

### Issue: "Failed to build image"

**Solution:**
```bash
# Check Dockerfile.production exists
ls -la Dockerfile.production

# Try local Docker build first
docker build -f Dockerfile.production -t synapse-test .

# Then deploy
flyctl deploy
```

### Issue: "App name already taken"

**Solution:**
```bash
# Use a different app name in fly.toml
# Change: app = 'synapse-lang-docs'
# To: app = 'synapse-lang-platform'

# Then deploy
flyctl deploy
```

### Issue: Health check failing

**Solution:**
```bash
# Check logs
flyctl logs --app synapse-lang-docs

# SSH into container
flyctl ssh console

# Test health endpoint internally
curl localhost:8080/api/health
```

---

## 🔄 Alternative: GitHub Actions Deployment

If manual deployment has issues, set up GitHub Actions:

### 1. Get Fly.io API Token

```bash
flyctl tokens create deploy
```

Copy the token.

### 2. Add to GitHub Secrets

1. Go to: https://github.com/MichaelCrowe11/synapse-lang/settings/secrets/actions
2. Click "New repository secret"
3. Name: `FLY_API_TOKEN`
4. Value: [paste token]
5. Click "Add secret"

### 3. Create GitHub Workflow

Create `.github/workflows/deploy-fly.yml`:

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [ master ]
    paths:
      - 'docs-website/**'
  workflow_dispatch:

jobs:
  deploy:
    name: Deploy to Fly.io
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy to Fly.io
        working-directory: ./docs-website
        run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

### 4. Trigger Deployment

```bash
git add .github/workflows/deploy-fly.yml
git commit -m "Add Fly.io auto-deployment"
git push origin master
```

GitHub Actions will automatically deploy!

---

## 📊 Post-Deployment Checklist

After successful deployment:

- [ ] Visit https://synapse-lang-docs.fly.dev
- [ ] Test /api/health endpoint
- [ ] Test /playground page
- [ ] Test /dashboard page
- [ ] Check fly.io dashboard: https://fly.io/dashboard
- [ ] Monitor logs: `flyctl logs`
- [ ] Set up monitoring (Sentry, LogDNA, etc.)
- [ ] Share the URL on social media!

---

## 🎉 Ready to Launch?

Once deployed successfully:

1. **Announce on Twitter/X** (use LAUNCH_NOW_PLAYBOOK.md)
2. **Submit to Hacker News** (Show HN post ready)
3. **Post on Reddit** (r/programming, r/QuantumComputing)
4. **Share on LinkedIn**
5. **Monitor metrics and engage with users**

---

## 🆘 Need Help?

**Fly.io Documentation:**
- Troubleshooting: https://fly.io/docs/getting-started/troubleshooting/
- Deployment Guide: https://fly.io/docs/languages-and-frameworks/dockerfile/
- Scaling: https://fly.io/docs/reference/scaling/

**Fly.io Community:**
- Forum: https://community.fly.io/
- Discord: https://fly.io/discord

**Check Status:**
- Fly.io Status: https://status.flyio.net/

---

## 📝 Current Authentication Status

**Last attempt:** Authentication succeeded but deployment commands failed
**Account:** michael@southwestmushrooms.online
**Issue:** Possible CLI cache or token expiry issue

**Recommended fix:** Fresh authentication in new terminal session

---

## 🚀 Quick Deploy Command (After Re-auth)

```bash
cd C:\Users\micha\synapse-lang\docs-website && flyctl deploy
```

**That's it!** 🎉

---

*Created: November 2025*
*Platform ready for deployment - all fixes applied and tested*
