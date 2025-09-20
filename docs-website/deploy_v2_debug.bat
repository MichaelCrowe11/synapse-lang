@echo off
REM Synapse Language v2 Documentation - Debug Deployment Script
REM This script provides verbose output for troubleshooting

echo ================================================
echo SYNAPSE v2 DOCS - DEPLOYMENT DIAGNOSTIC
echo ================================================
echo.

REM Check if fly is installed
echo Checking Fly CLI installation...
where fly
if %errorlevel% neq 0 (
    echo ERROR: Fly CLI is not installed.
    echo.
    echo Please install Fly CLI first:
    echo PowerShell: iwr https://fly.io/install.ps1 -useb ^| iex
    echo.
    pause
    exit /b 1
)

echo.
echo Fly CLI found at above location
echo.

REM Check authentication
echo Checking Fly authentication...
fly auth whoami
if %errorlevel% neq 0 (
    echo.
    echo You are not logged in to Fly.io
    echo Please run: fly auth login
    echo.
    pause
    exit /b 1
)

echo.
echo Checking current directory...
echo Current directory: %cd%
echo.

echo Checking for required files...
if exist "app_v2_socket.py" (
    echo ✓ app_v2_socket.py found
) else (
    echo ✗ app_v2_socket.py NOT FOUND
)

if exist "Dockerfile.production" (
    echo ✓ Dockerfile.production found
) else (
    echo ✗ Dockerfile.production NOT FOUND
)

if exist "requirements_v2.txt" (
    echo ✓ requirements_v2.txt found
) else (
    echo ✗ requirements_v2.txt NOT FOUND
)

if exist "fly.toml.v2" (
    echo ✓ fly.toml.v2 found
) else (
    echo ✗ fly.toml.v2 NOT FOUND
)

if exist "templates_v2" (
    echo ✓ templates_v2 directory found
) else (
    echo ✗ templates_v2 directory NOT FOUND
)

echo.
echo Checking app status...
fly apps list | findstr synapse-lang-docs
if %errorlevel% neq 0 (
    echo.
    echo App 'synapse-lang-docs' does not exist yet.
    echo.
    echo Would you like to create it? (This is normal for first deployment)
    echo.
    pause

    echo Creating app...
    fly apps create synapse-lang-docs
    if %errorlevel% neq 0 (
        echo.
        echo Failed to create app. The name might be taken.
        echo Try with a different name:
        echo fly apps create synapse-docs-v2
        pause
        exit /b 1
    )
)

echo.
echo Copying configuration files...
copy fly.toml.v2 fly.toml
echo Configuration copied.

echo.
echo Ready to deploy. Press any key to start deployment...
pause

echo.
echo Starting deployment...
fly deploy --dockerfile Dockerfile.production --verbose

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo DEPLOYMENT SUCCESSFUL!
    echo ================================================
    echo.
    echo Your site is live at:
    echo https://synapse-lang-docs.fly.dev
    echo.
    fly open
) else (
    echo.
    echo ================================================
    echo DEPLOYMENT FAILED
    echo ================================================
    echo.
    echo Common issues:
    echo 1. App name already taken - try a different name
    echo 2. Missing files - check file list above
    echo 3. Docker build error - check Dockerfile
    echo 4. Port mismatch - ensure PORT=8080
    echo.
    echo Run these commands for more info:
    echo   fly logs
    echo   fly doctor
    echo.
)

pause