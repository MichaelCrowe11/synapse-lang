# 🚀 Deploying Synapse Docs to Fly.io

## Prerequisites

1. Install Fly CLI:
```bash
# Windows (PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh
```

2. Sign up/Login to Fly.io:
```bash
fly auth signup
# or
fly auth login
```

## Deployment Steps

### 1. Navigate to docs website directory
```bash
cd C:\Users\micha\synapse-lang\docs-website
```

### 2. Initialize Fly app (first time only)
```bash
fly launch
```

When prompted:
- App name: `synapse-lang-docs` (or choose your own)
- Region: Choose nearest to you (e.g., `iad` for US East)
- PostgreSQL: No
- Redis: No
- Deploy now: Yes

### 3. Deploy updates
```bash
fly deploy
```

### 4. Open the deployed site
```bash
fly open
```

Your documentation will be live at: https://synapse-lang-docs.fly.dev

## Environment Variables

Set any required environment variables:
```bash
fly secrets set SECRET_KEY="your-production-secret-key"
```

## Monitoring

### View logs
```bash
fly logs
```

### Check status
```bash
fly status
```

### Scale if needed
```bash
# Scale to 2 instances
fly scale count 2

# Scale machine size
fly scale vm shared-cpu-1x
```

## Custom Domain (Optional)

1. Add custom domain:
```bash
fly ips allocate-v4
fly certs add yourdomain.com
```

2. Update DNS:
- Add A record pointing to the allocated IP
- Add CNAME for www subdomain

## Updating the Documentation

1. Make changes to the website code
2. Test locally:
```bash
cd docs-website
python app.py
# Visit http://localhost:8080
```

3. Deploy changes:
```bash
fly deploy
```

## Rollback if Needed

```bash
# List releases
fly releases

# Rollback to previous version
fly deploy --image <previous-image-ref>
```

## Useful Commands

```bash
# SSH into running app
fly ssh console

# View app info
fly info

# View configuration
fly config show

# Restart app
fly apps restart
```

## GitHub Actions Integration (Optional)

Create `.github/workflows/deploy-docs.yml`:
```yaml
name: Deploy Docs to Fly.io

on:
  push:
    branches: [main]
    paths:
      - 'docs-website/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        working-directory: ./docs-website
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Add your Fly API token to GitHub secrets:
```bash
fly tokens create
# Add the token to GitHub repo settings > Secrets
```

## Troubleshooting

### Build fails
- Check `Dockerfile` syntax
- Ensure all required files are present
- Check `requirements.txt` for correct versions

### App crashes
- Check logs: `fly logs`
- Verify port configuration (should be 8080)
- Check health endpoint: `/health`

### Deployment stuck
- Cancel: `Ctrl+C`
- Try again: `fly deploy`
- Force deploy: `fly deploy --strategy immediate`

## Support

- Fly.io Docs: https://fly.io/docs
- Fly.io Status: https://status.fly.io
- Community: https://community.fly.io

---

**Ready to deploy!** Run `fly launch` in the `docs-website` directory to get started.