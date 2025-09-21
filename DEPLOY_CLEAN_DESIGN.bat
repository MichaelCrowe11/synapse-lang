@echo off
echo ================================================
echo DEPLOYING PROFESSIONAL REDESIGN
echo ================================================
echo.
echo Changes:
echo - Removed all emoji clutter
echo - Custom SVG icon system
echo - Clean, professional typography
echo - Minimalist design language
echo - Better visual hierarchy
echo.

cd docs-website
fly deploy --dockerfile Dockerfile.production --app synapse-lang-docs

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo DEPLOYMENT SUCCESSFUL
    echo ================================================
    echo.
    echo Professional design is now live at:
    echo https://synapse-lang-docs.fly.dev
    echo.
    echo Updates:
    echo [1] Homepage - Clean, emoji-free design
    echo [2] Playground - Professional code examples
    echo [3] Dashboard - SVG icons instead of emojis
    echo [4] Custom icon system in /static_v2/icons.svg
    echo.
    start https://synapse-lang-docs.fly.dev
) else (
    echo.
    echo Deployment failed. Check errors above.
)

cd ..
pause
