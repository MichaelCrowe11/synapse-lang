# Custom Domain Setup for synapse-lang.com

## Domain: synapse-lang.com (Already Owned)

## DNS Configuration

Add these records to your DNS provider:

### Option 1: Root Domain (synapse-lang.com)
```
Type: A
Name: @
Value: [Fly.io IP - run 'fly ips list' to get this]
TTL: 3600
```

### Option 2: With www subdomain
```
Type: CNAME
Name: www
Value: synapse-lang-docs.fly.dev
TTL: 3600
```

### Option 3: Docs subdomain (docs.synapse-lang.com)
```
Type: CNAME
Name: docs
Value: synapse-lang-docs.fly.dev
TTL: 3600
```

## Fly.io Certificate Setup

1. Add the custom domain to Fly.io:
```bash
fly certs add synapse-lang.com -a synapse-lang-docs
fly certs add www.synapse-lang.com -a synapse-lang-docs
```

2. Check certificate status:
```bash
fly certs list -a synapse-lang-docs
fly certs show synapse-lang.com -a synapse-lang-docs
```

## Verification Steps

1. DNS Propagation (can take up to 48 hours):
   - Check with: https://dnschecker.org/#A/synapse-lang.com
   - Or use: `nslookup synapse-lang.com`

2. SSL Certificate:
   - Fly.io will automatically provision Let's Encrypt certificates
   - Check status: `fly certs check synapse-lang.com -a synapse-lang-docs`

## Update Application

1. Update your app to recognize the custom domain:
```python
# In app_v2_socket.py
ALLOWED_HOSTS = [
    'synapse-lang.com',
    'www.synapse-lang.com',
    'docs.synapse-lang.com',
    'synapse-lang-docs.fly.dev'
]
```

2. Update CORS settings for WebSocket:
```python
socketio = SocketIO(app, cors_allowed_origins=[
    'https://synapse-lang.com',
    'https://www.synapse-lang.com',
    'https://docs.synapse-lang.com',
    'https://synapse-lang-docs.fly.dev'
])
```

## Marketing URLs

Once configured, you'll have:
- Main site: https://synapse-lang.com
- Documentation: https://docs.synapse-lang.com
- API: https://synapse-lang.com/api/v2/
- Playground: https://synapse-lang.com/playground
- Dashboard: https://synapse-lang.com/dashboard

## Update All References

Update these locations with the new domain:
- README.md
- setup.py (project_urls)
- package.json (homepage)
- Docker labels
- PyPI description
- npm description
