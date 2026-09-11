@echo off
REM Synapse Language v2 Documentation - Fixed Deployment Script

echo ================================================
echo SYNAPSE v2 DOCS - PRODUCTION DEPLOYMENT
echo ================================================
echo.

REM Check Fly CLI
where fly >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Fly CLI is not installed.
    pause
    exit /b 1
)

echo [1/5] Checking authentication...
fly auth whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo Not logged in. Running fly auth login...
    fly auth login
)

echo [2/5] Checking app existence...
fly apps list | findstr synapse-lang-docs >nul 2>&1
if %errorlevel% neq 0 (
    echo App does not exist. Creating synapse-lang-docs...
    fly apps create synapse-lang-docs --machines
    if %errorlevel% neq 0 (
        echo.
        echo App name might be taken. Trying alternative name...
        set /p APP_NAME="Enter a unique app name (e.g., synapse-docs-michael): "
        fly apps create %APP_NAME% --machines
        echo Please update fly.toml with your app name: %APP_NAME%
        pause
    )
)

echo [3/5] Setting up configuration...
if exist fly.toml.v2 (
    copy fly.toml.v2 fly.toml >nul
) else if exist fly.toml.simple (
    copy fly.toml.simple fly.toml >nul
)

echo [4/5] Setting secrets...
fly secrets set SECRET_KEY=prod_%RANDOM%%RANDOM%%RANDOM% --app synapse-lang-docs 2>nul

echo [5/5] Deploying application...
echo.
echo This will take a few minutes...
echo.

fly deploy --dockerfile Dockerfile.production

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo DEPLOYMENT SUCCESSFUL!
    echo ================================================
    echo.
    echo Your site is now live!
    echo.
    fly open --app synapse-lang-docs
) else (
    echo.
    echo ================================================
    echo DEPLOYMENT ENCOUNTERED AN ERROR
    echo ================================================
    echo.
    echo Checking deployment logs...
    fly logs --app synapse-lang-docs -n 50
    echo.
    echo For more details, run:
    echo   fly logs --app synapse-lang-docs
    echo   fly status --app synapse-lang-docs
)

pause