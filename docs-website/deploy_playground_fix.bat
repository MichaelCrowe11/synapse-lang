@echo off
echo ================================================
echo DEPLOYING FIXED PLAYGROUND TO PRODUCTION
echo ================================================
echo.

echo Deploying with real code execution support...
fly deploy --dockerfile Dockerfile.production --app synapse-lang-docs

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo DEPLOYMENT SUCCESSFUL!
    echo ================================================
    echo.
    echo The playground now supports REAL code execution:
    echo.
    echo - Python code execution with sandboxing
    echo - Synapse Language support
    echo - Import restrictions for security
    echo - 5-second timeout protection
    echo - Memory usage tracking
    echo.
    echo Test it at: https://synapse-lang-docs.fly.dev/playground
    echo.
    echo Opening in browser...
    start https://synapse-lang-docs.fly.dev/playground
) else (
    echo.
    echo Deployment failed. Please check errors above.
)

pause
