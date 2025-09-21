@echo off
echo ================================================
echo SETTING UP CUSTOM DOMAIN: synapse-lang.com
echo ================================================
echo.

echo Step 1: Adding certificates for custom domain...
fly certs add synapse-lang.com -a synapse-lang-docs
fly certs add www.synapse-lang.com -a synapse-lang-docs
fly certs add docs.synapse-lang.com -a synapse-lang-docs

echo.
echo Step 2: Checking certificate status...
fly certs list -a synapse-lang-docs

echo.
echo Step 3: Getting IP addresses for DNS configuration...
fly ips list -a synapse-lang-docs

echo.
echo ================================================
echo DNS CONFIGURATION REQUIRED
echo ================================================
echo.
echo Please add these DNS records at your domain registrar:
echo.
echo For root domain (synapse-lang.com):
echo   Type: A
echo   Name: @ or blank
echo   Value: [Use the IPv4 address shown above]
echo.
echo For www subdomain:
echo   Type: CNAME
echo   Name: www
echo   Value: synapse-lang-docs.fly.dev
echo.
echo For docs subdomain:
echo   Type: CNAME
echo   Name: docs
echo   Value: synapse-lang-docs.fly.dev
echo.
echo ================================================
echo.
echo After adding DNS records, it may take up to 48 hours to propagate.
echo.
echo To check status:
echo   fly certs check synapse-lang.com -a synapse-lang-docs
echo.
echo Your site will be available at:
echo   https://synapse-lang.com
echo   https://www.synapse-lang.com
echo   https://docs.synapse-lang.com
echo.
pause
