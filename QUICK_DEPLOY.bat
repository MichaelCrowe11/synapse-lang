@echo off
echo ================================================
echo CRITICAL FIX: WebSocket Connection for Playground
echo ================================================
echo.
echo This fixes the playground to actually execute code!
echo.

cd docs-website
fly deploy --dockerfile Dockerfile.production --app synapse-lang-docs

if %errorlevel% equ 0 (
    echo.
    echo ✅ DEPLOYMENT SUCCESSFUL!
    echo.
    echo The playground will now:
    echo - Connect via WebSocket
    echo - Execute REAL Python/Synapse code
    echo - Show actual output (not fake)
    echo.
    echo Test it in 30 seconds at:
    start https://synapse-lang-docs.fly.dev/playground
) else (
    echo.
    echo ❌ Deployment failed
)

cd ..
pause
