# DNS Configuration for synapse-lang.com

## GitHub Pages Setup Status
✅ **Website deployed**: The documentation site is now live
✅ **CNAME configured**: Custom domain file created
✅ **Workflow created**: Automatic deployment on push

## Required DNS Settings for Namecheap

To point synapse-lang.com to GitHub Pages, configure these DNS records in your Namecheap account:

### Option 1: Using A Records (Recommended)
Add these A records to point to GitHub Pages:
```
Type: A Record
Host: @
Value: 185.199.108.153
TTL: Automatic

Type: A Record
Host: @
Value: 185.199.109.153
TTL: Automatic

Type: A Record
Host: @
Value: 185.199.110.153
TTL: Automatic

Type: A Record
Host: @
Value: 185.199.111.153
TTL: Automatic
```

### Option 2: Using CNAME (for www subdomain)
```
Type: CNAME Record
Host: www
Value: michaelcrowe11.github.io
TTL: Automatic
```

## Steps to Configure in Namecheap:

1. **Log in to Namecheap**
   - Go to https://www.namecheap.com
   - Sign in to your account

2. **Navigate to Domain Settings**
   - Dashboard → Domain List
   - Click "Manage" next to synapse-lang.com

3. **Configure DNS**
   - Go to "Advanced DNS" tab
   - Remove any existing A records for @ host
   - Add the A records listed above

4. **Enable GitHub Pages**
   - Go to https://github.com/MichaelCrowe11/synapse-lang/settings/pages
   - Under "Custom domain", it should show: synapse-lang.com
   - Check "Enforce HTTPS" once DNS propagates

## Verification Steps:

After DNS propagation (can take up to 48 hours, usually faster):

1. **Check DNS propagation**: 
   ```bash
   nslookup synapse-lang.com
   dig synapse-lang.com
   ```

2. **Test the website**:
   - https://synapse-lang.com
   - https://www.synapse-lang.com

3. **GitHub Pages Status**:
   - Check: https://github.com/MichaelCrowe11/synapse-lang/settings/pages
   - Should show "✅ Your site is published at https://synapse-lang.com"

## Current Status URLs:

- **GitHub Repository**: https://github.com/MichaelCrowe11/synapse-lang
- **GitHub Pages (temp)**: https://michaelcrowe11.github.io/synapse-lang/
- **PyPI Package**: https://pypi.org/project/synapse-lang/2.0.0/
- **Target Domain**: https://synapse-lang.com (pending DNS)

## Package Installation:
```bash
pip install synapse-lang
```

## Troubleshooting:

If the site doesn't load after DNS configuration:
1. Clear browser cache
2. Try incognito/private browsing
3. Check GitHub Pages settings
4. Verify CNAME file exists in docs/
5. Check DNS propagation status at https://www.whatsmydns.net/

## Support:
- GitHub Issues: https://github.com/MichaelCrowe11/synapse-lang/issues
- PyPI Page: https://pypi.org/project/synapse-lang/