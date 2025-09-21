@echo off
echo ================================================
echo DEPLOYING EMOJI REMOVAL FIX
echo ================================================
echo.
echo This deployment removes emojis from:
echo - Homepage install cards (Python, Node, Docker)
echo - Feature cards (Quantum, Distributed, Security)
echo - Dashboard metrics
echo - Playground examples
echo.

cd docs-website
fly deploy --dockerfile Dockerfile.production --app synapse-lang-docs

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo SUCCESS - EMOJIS REMOVED
    echo ================================================
    echo.
    echo The site now uses professional SVG icons.
    echo.
    echo View the clean design at:
    start https://synapse-lang-docs.fly.dev
) else (
    echo.
    echo Deployment failed.
)

cd ..
pause
