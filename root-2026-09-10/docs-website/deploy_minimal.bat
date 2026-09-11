@echo off
echo ================================================
echo MINIMAL DEPLOYMENT TEST
echo ================================================
echo.

echo Step 1: Creating/checking app...
fly apps list | findstr synapse-lang-docs >nul 2>&1
if %errorlevel% neq 0 (
    echo Creating new app: synapse-lang-docs
    fly apps create synapse-lang-docs --machines
    if %errorlevel% neq 0 (
        echo.
        echo App name is taken. Please choose a different name.
        echo Suggestions:
        echo   - synapse-docs-v2
        echo   - synapse-lang-docs-2
        echo   - synapse-michael-docs
        echo.
        set /p NEW_NAME="Enter your app name: "
        fly apps create %NEW_NAME% --machines
        echo.
        echo IMPORTANT: Update the app name in fly.toml to: %NEW_NAME%
        echo.
        pause
    )
)

echo.
echo Step 2: Using minimal configuration...
echo # Minimal fly.toml > fly.toml
echo app = "synapse-lang-docs" >> fly.toml
echo primary_region = "iad" >> fly.toml
echo. >> fly.toml
echo [build] >> fly.toml
echo   dockerfile = "Dockerfile.minimal" >> fly.toml
echo. >> fly.toml
echo [env] >> fly.toml
echo   PORT = "8080" >> fly.toml
echo. >> fly.toml
echo [[services]] >> fly.toml
echo   internal_port = 8080 >> fly.toml
echo   protocol = "tcp" >> fly.toml
echo. >> fly.toml
echo   [[services.ports]] >> fly.toml
echo     port = 80 >> fly.toml
echo     handlers = ["http"] >> fly.toml
echo. >> fly.toml
echo   [[services.ports]] >> fly.toml
echo     port = 443 >> fly.toml
echo     handlers = ["tls", "http"] >> fly.toml

echo.
echo Step 3: Deploying minimal app...
fly deploy --dockerfile Dockerfile.minimal

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo MINIMAL DEPLOYMENT SUCCESSFUL!
    echo ================================================
    echo.
    echo Opening your site...
    fly open
    echo.
    echo Next steps:
    echo 1. If this works, we can deploy the full v2 app
    echo 2. Run: deploy_v2_fixed.bat
) else (
    echo.
    echo ================================================
    echo DEPLOYMENT FAILED
    echo ================================================
    echo.
    echo Let's check what went wrong:
    fly doctor
    echo.
    echo Also try:
    echo   fly deploy --dockerfile Dockerfile.minimal --verbose
)

pause