@echo off
echo ================================================
echo DEPLOYING REAL CODE EXECUTION TO PRODUCTION
echo ================================================
echo.
echo This deployment adds:
echo - Real Python/Synapse code execution
echo - Secure sandboxed environment
echo - Import restrictions for safety
echo - 5-second timeout protection
echo - Memory usage tracking
echo.
echo Starting deployment...
echo.

cd docs-website

fly deploy --dockerfile Dockerfile.production --app synapse-lang-docs

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo DEPLOYMENT SUCCESSFUL!
    echo ================================================
    echo.
    echo The playground now executes REAL code!
    echo.
    echo Test it here:
    echo https://synapse-lang-docs.fly.dev/playground
    echo.
    echo Try running this example code:
    echo   from synapse_lang import UncertainValue
    echo   value = UncertainValue(10.0, uncertainty=0.5)
    echo   print(value)
    echo.
    echo Opening playground...
    timeout /t 2 >nul
    start https://synapse-lang-docs.fly.dev/playground
) else (
    echo.
    echo ================================================
    echo DEPLOYMENT FAILED
    echo ================================================
    echo.
    echo Please check the error messages above.
    echo.
    echo Common issues:
    echo 1. Not logged in: Run 'fly auth login'
    echo 2. App doesn't exist: Run 'fly apps list'
    echo 3. Docker issues: Check Dockerfile.production
)

cd ..
pause
