@echo off
REM Synapse Language Documentation - Deploy to Fly.io
REM This script deploys the documentation website to Fly.io

echo ================================================
echo SYNAPSE DOCS DEPLOYMENT TO FLY.IO
echo ================================================
echo.

REM Check if fly is installed
where fly >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Fly CLI is not installed.
    echo.
    echo Please install Fly CLI first:
    echo PowerShell: iwr https://fly.io/install.ps1 -useb ^| iex
    echo.
    echo Or download from: https://fly.io/docs/getting-started/installing-flyctl/
    pause
    exit /b 1
)

echo Fly CLI found. Proceeding with deployment...
echo.

REM Navigate to docs-website directory
cd /d "%~dp0docs-website"

REM Check if already initialized
if exist fly.toml (
    echo Fly app already configured. Deploying...
    fly deploy
) else (
    echo Initializing new Fly app...
    echo.
    echo IMPORTANT: When prompted:
    echo   - App name: synapse-lang-docs (or your choice)
    echo   - Region: iad (US East) or your nearest region
    echo   - Database: NO
    echo   - Redis: NO
    echo   - Deploy now: YES
    echo.
    fly launch
)

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo DEPLOYMENT SUCCESSFUL!
    echo ================================================
    echo.
    echo Your documentation is now live!
    echo.
    echo Opening in browser...
    fly open
    echo.
    echo Useful commands:
    echo   fly logs       - View application logs
    echo   fly status     - Check deployment status
    echo   fly deploy     - Deploy updates
    echo.
) else (
    echo.
    echo ================================================
    echo DEPLOYMENT FAILED
    echo ================================================
    echo.
    echo Please check the error messages above.
    echo You may need to:
    echo   1. Run 'fly auth login' to authenticate
    echo   2. Check your internet connection
    echo   3. Verify the app name is unique
    echo.
)

pause