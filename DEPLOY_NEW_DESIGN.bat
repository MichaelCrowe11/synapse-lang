@echo off
echo ================================================
echo DEPLOYING MAJOR REDESIGN - BRUTALIST MINIMAL
echo ================================================
echo.
echo This is a COMPLETE visual overhaul:
echo.
echo [BLACK AND WHITE] No more purple gradients
echo [BOLD TYPOGRAPHY] Massive, impactful headlines  
echo [BRUTALIST] Sharp borders, no rounded corners
echo [MINIMAL] Clean, stark, professional
echo [NO EMOJIS] Zero decorative elements
echo.

cd docs-website
fly deploy --dockerfile Dockerfile.production --app synapse-lang-docs

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo MAJOR REDESIGN DEPLOYED SUCCESSFULLY
    echo ================================================
    echo.
    echo The site now has a completely new look:
    echo - Brutalist minimal design
    echo - Black and white color scheme
    echo - Bold typography (140px headlines)
    echo - No emojis or decorative elements
    echo.
    echo Opening new design...
    start https://synapse-lang-docs.fly.dev
) else (
    echo.
    echo Deployment failed. Check errors above.
)

cd ..
pause
