@echo off
echo ================================================
echo DEPLOYING CONTINUOUS ENHANCEMENTS
echo ================================================
echo.
echo NEW FEATURES BEING DEPLOYED:
echo.
echo [1] PARTICLE SYSTEM
echo    - Quantum particles with mouse interaction
echo    - Dynamic connections between particles
echo    - WebGL accelerated rendering
echo.
echo [2] ADVANCED ANIMATIONS
echo    - Scroll-triggered reveals
echo    - Parallax effects
echo    - Morphing shapes
echo    - Holographic text
echo    - Matrix rain background
echo.
echo [3] INTERACTION PATTERNS
echo    - Command palette (Ctrl+K)
echo    - Quick actions (Ctrl+/)
echo    - Swipe gestures
echo    - Keyboard shortcuts
echo.
echo [4] 3D VISUALIZATIONS
echo    - WebGL quantum sphere
echo    - Real-time rotation
echo    - Shader effects
echo.
echo [5] PERFORMANCE MONITOR
echo    - FPS counter
echo    - Memory usage
echo    - DOM node count
echo    - Toggle with Ctrl+Shift+P
echo.
echo [6] LIVE FEATURES
echo    - Real-time metric updates
echo    - Typewriter effects
echo    - Dynamic data charts
echo.

cd docs-website
fly deploy --dockerfile Dockerfile.production --app synapse-lang-docs

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo ENHANCEMENTS DEPLOYED SUCCESSFULLY
    echo ================================================
    echo.
    echo Try these features:
    echo - Press Ctrl+K for command palette
    echo - Hover over page to see particle interactions
    echo - Scroll to see reveal animations
    echo - Press Ctrl+Shift+P for performance monitor
    echo.
    echo Live at: https://synapse-lang-docs.fly.dev
    echo.
    start https://synapse-lang-docs.fly.dev
) else (
    echo.
    echo Deployment failed. Check errors above.
)

cd ..
pause