@echo off
echo ================================================
echo DEPLOYING WEBSITE FIX
echo ================================================
echo.
echo This deployment fixes:
echo - Homepage rendering issues
echo - Static file paths
echo - Simplified template for stability
echo.

cd docs-website
fly deploy --dockerfile Dockerfile.production --app synapse-lang-docs

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo FIX DEPLOYED SUCCESSFULLY
    echo ================================================
    echo.
    echo The website should now work properly with:
    echo - Clean, simple homepage
    echo - Working navigation links
    echo - Proper static file serving
    echo - All routes functioning
    echo.
    echo Opening site...
    start https://synapse-lang-docs.fly.dev
) else (
    echo.
    echo Deployment failed. Check errors above.
)

cd ..
pause