# 🚀 Synapse v2 Documentation - Deployment Guide

## Production Deployment to Fly.io

This guide covers deploying the modern v2 documentation site with all real-time features.

## 📋 Prerequisites

1. **Fly CLI installed**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex

   # Mac
   brew install flyctl

   # Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Fly.io account**
   ```bash
   fly auth signup
   # or
   fly auth login
   ```

## 🎯 Quick Deploy

### Windows
```powershell
cd C:\Users\micha\synapse-lang\docs-website
.\deploy_v2.bat
```

### Mac/Linux
```bash
cd /path/to/synapse-lang/docs-website
./deploy_v2.sh
```

## 🔧 Manual Deployment Steps

### 1. Set Configuration
```bash
# Use v2 configuration
cp fly.toml.v2 fly.toml
```

### 2. Set Secrets
```bash
# Generate and set secret key
fly secrets set SECRET_KEY=$(openssl rand -hex 32) --app synapse-lang-docs

# Optional: Set other secrets
fly secrets set GITHUB_TOKEN=your-token --app synapse-lang-docs
fly secrets set NPM_TOKEN=your-token --app synapse-lang-docs
```

### 3. Deploy
```bash
fly deploy --dockerfile Dockerfile.production
```

### 4. Verify Deployment
```bash
# Check status
fly status --app synapse-lang-docs

# View logs
fly logs --app synapse-lang-docs

# Open site
fly open --app synapse-lang-docs
```

## 🌟 Features Included

### Modern UI/UX
- ✅ Vercel/npm-inspired design
- ✅ Dark/light theme system
- ✅ Responsive layouts
- ✅ Smooth animations

### Interactive Features
- ✅ **Real-time Collaboration** - WebSocket-powered collaborative editing
- ✅ **Live Code Playground** - Execute code with visualization
- ✅ **Package Explorer** - VS Code-style file browser
- ✅ **API Documentation** - Interactive with try-it-now
- ✅ **Analytics Dashboard** - Real-time metrics and charts

### Technical Stack
- **Backend**: Flask + SocketIO
- **Real-time**: WebSocket with eventlet
- **Frontend**: Modern JavaScript, CodeMirror
- **Deployment**: Fly.io with auto-scaling
- **Monitoring**: Health checks, metrics

## 📊 Monitoring

### Health Check
```bash
curl https://synapse-lang-docs.fly.dev/health
```

### Status Endpoint
```bash
curl https://synapse-lang-docs.fly.dev/api/v2/status
```

### Real-time Analytics
```bash
curl https://synapse-lang-docs.fly.dev/api/v2/analytics
```

## 🔄 Updating

### Deploy Updates
```bash
# Make changes to code
# Then deploy
fly deploy --dockerfile Dockerfile.production
```

### Scale Application
```bash
# Scale to 2 instances
fly scale count 2 --app synapse-lang-docs

# Scale machine size
fly scale vm shared-cpu-1x --memory 1024 --app synapse-lang-docs
```

### Update Secrets
```bash
fly secrets set SECRET_KEY=new-secret --app synapse-lang-docs
```

## 🐛 Troubleshooting

### Check Logs
```bash
# Live logs
fly logs --app synapse-lang-docs

# Last 100 lines
fly logs -n 100 --app synapse-lang-docs
```

### SSH into Container
```bash
fly ssh console --app synapse-lang-docs
```

### Restart Application
```bash
fly apps restart synapse-lang-docs
```

### Check Configuration
```bash
fly config show --app synapse-lang-docs
```

## 🔒 Security

### Environment Variables
All sensitive data should be set as secrets:
```bash
fly secrets list --app synapse-lang-docs
```

### HTTPS
Fly.io automatically provides SSL certificates and forces HTTPS.

### Rate Limiting
Configured in the application with default limits.

## 📈 Performance

### Current Setup
- **Memory**: 512MB
- **CPU**: 1 shared CPU
- **Regions**: iad (US East)
- **Auto-scaling**: Enabled
- **WebSocket**: Supported

### Scaling Options
```bash
# Add more regions
fly regions add ord --app synapse-lang-docs

# Increase resources
fly scale vm dedicated-cpu-1x --memory 2048 --app synapse-lang-docs
```

## 🔗 URLs

- **Production**: https://synapse-lang-docs.fly.dev
- **Health**: https://synapse-lang-docs.fly.dev/health
- **Status**: https://synapse-lang-docs.fly.dev/api/v2/status
- **Metrics**: https://synapse-lang-docs.fly.dev/api/v2/analytics

## 📝 Maintenance

### Backup Data
```bash
fly volumes list --app synapse-lang-docs
fly volumes snapshots list <volume-id>
```

### Database (if using)
```bash
fly postgres connect -a synapse-lang-docs-db
```

## 🎯 Post-Deployment Checklist

- [ ] Verify site loads at https://synapse-lang-docs.fly.dev
- [ ] Test dark/light theme toggle
- [ ] Check WebSocket connection (Workspace page)
- [ ] Test code playground execution
- [ ] Verify package explorer functionality
- [ ] Check API documentation interactivity
- [ ] Test responsive design on mobile
- [ ] Monitor initial performance metrics
- [ ] Set up uptime monitoring (optional)
- [ ] Configure custom domain (optional)

## 🆘 Support

- **Fly.io Status**: https://status.fly.io
- **Fly.io Community**: https://community.fly.io
- **Documentation**: https://fly.io/docs

---

**Ready to deploy!** Run `deploy_v2.bat` (Windows) or `deploy_v2.sh` (Mac/Linux) to deploy the modern v2 documentation site with all features enabled.