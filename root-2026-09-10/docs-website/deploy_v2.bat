@echo off
REM Synapse Language v2 Documentation - Production Deployment Script
REM This script deploys the modern v2 design with WebSocket support to Fly.io

echo ================================================
echo SYNAPSE v2 DOCS - PRODUCTION DEPLOYMENT
echo ================================================
echo.
echo Modern UI with Real-time Features
echo.

REM Check if fly is installed
where fly >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Fly CLI is not installed.
    echo.
    echo Please install Fly CLI first:
    echo PowerShell: iwr https://fly.io/install.ps1 -useb ^| iex
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Fly authentication...
fly auth whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo You need to login to Fly.io first
    fly auth login
)

echo [2/5] Setting up environment...

REM Check if secrets need to be set
echo.
echo Setting production secrets...
fly secrets set SECRET_KEY=%RANDOM%%RANDOM%%RANDOM% --app synapse-lang-docs >nul 2>&1

echo [3/5] Building production image...
echo.

REM Use the production configuration
copy fly.toml.v2 fly.toml >nul 2>&1

echo [4/5] Deploying to Fly.io...
echo.
echo This may take a few minutes...
echo.

fly deploy --dockerfile Dockerfile.production

if %errorlevel% equ 0 (
    echo.
    echo [5/5] Deployment successful! Verifying...
    echo.

    REM Wait a moment for deployment to stabilize
    timeout /t 5 /nobreak >nul

    REM Check deployment status
    fly status --app synapse-lang-docs

    echo.
    echo ================================================
    echo DEPLOYMENT SUCCESSFUL!
    echo ================================================
    echo.
    echo Your v2 documentation site is now live at:
    echo https://synapse-lang-docs.fly.dev
    echo.
    echo Features enabled:
    echo   ✓ Modern Vercel/npm-inspired design
    echo   ✓ Real-time collaboration with WebSocket
    echo   ✓ Interactive code playground
    echo   ✓ Package explorer with syntax highlighting
    echo   ✓ API documentation with try-it-now
    echo   ✓ Dark/light theme system
    echo   ✓ Analytics dashboard
    echo.
    echo Commands:
    echo   View logs:    fly logs --app synapse-lang-docs
    echo   Check status: fly status --app synapse-lang-docs
    echo   Open site:    fly open --app synapse-lang-docs
    echo   SSH console:  fly ssh console --app synapse-lang-docs
    echo.
    echo Opening in browser...
    timeout /t 3 /nobreak >nul
    fly open --app synapse-lang-docs
) else (
    echo.
    echo ================================================
    echo DEPLOYMENT FAILED
    echo ================================================
    echo.
    echo Please check the error messages above.
    echo.
    echo Troubleshooting:
    echo   1. Check logs: fly logs --app synapse-lang-docs
    echo   2. Verify Docker build: docker build -f Dockerfile.production .
    echo   3. Check app status: fly status --app synapse-lang-docs
    echo   4. Review configuration: fly config show --app synapse-lang-docs
    echo.
)

pause