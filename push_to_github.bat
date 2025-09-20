@echo off
echo ================================================
echo PUSHING SYNAPSE v2.3.2 TO GITHUB
echo ================================================
echo.

echo Checking git status...
git status

echo.
echo Initializing git repository (if needed)...
git init

echo.
echo Adding all files...
git add -A

echo.
echo Creating commit...
git commit -m "🚀 Release v2.3.2 - Modern documentation with real-time features

Major Updates:
- ✨ Launched modern documentation site (https://synapse-lang-docs.fly.dev)
- 🎨 Vercel/npm-inspired UI/UX design
- 👥 Real-time collaboration with WebSocket
- 🚀 Interactive code playground
- 📁 VS Code-style package explorer
- 📚 Interactive API documentation
- 🌓 Dark/light theme system
- 📊 Analytics dashboard

Technical Stack:
- Backend: Flask + SocketIO
- Frontend: Modern JavaScript, CodeMirror
- Deployment: Fly.io with auto-scaling
- WebSocket: Real-time collaboration
- Docker: Production-ready containers

Package Availability:
- PyPI: pip install synapse_lang
- npm: npm install synapse-lang-core
- Docker: docker pull michaelcrowe11/synapse-lang:2.3.2

Author: Michael Benjamin Crowe (michael@crowelogic.com)
"

echo.
echo Setting up remote repository...
echo.
echo Choose your GitHub setup:
echo 1. Create new repository (recommended for first push)
echo 2. Use existing repository
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Creating new GitHub repository...
    echo.
    echo IMPORTANT: First, go to GitHub and create a new repository:
    echo.
    echo 1. Go to: https://github.com/new
    echo 2. Repository name: synapse-lang
    echo 3. Description: Revolutionary scientific programming language with quantum computing, AI, and blockchain
    echo 4. Make it PUBLIC
    echo 5. DON'T initialize with README (we already have one)
    echo 6. Click 'Create repository'
    echo.
    pause
    echo.
    echo Now adding remote...
    git remote add origin https://github.com/michaelcrowe11/synapse-lang.git
) else (
    echo.
    echo Using existing repository...
    git remote -v
    echo.
    echo Is this correct? Press Ctrl+C to cancel, or
    pause
)

echo.
echo Pushing to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo Creating version tag...
    git tag -a v2.3.2 -m "Version 2.3.2 - Modern documentation and real-time features"
    git push origin v2.3.2

    echo.
    echo ================================================
    echo SUCCESS! CODE PUSHED TO GITHUB
    echo ================================================
    echo.
    echo Repository: https://github.com/michaelcrowe11/synapse-lang
    echo.
    echo Next steps:
    echo 1. Add README badges
    echo 2. Create GitHub Pages
    echo 3. Set up GitHub Actions
    echo 4. Add contributors guide
    echo.
    echo Opening GitHub repository...
    start https://github.com/michaelcrowe11/synapse-lang
) else (
    echo.
    echo ================================================
    echo PUSH FAILED
    echo ================================================
    echo.
    echo Common issues:
    echo 1. Not authenticated - run: git config --global user.name "Your Name"
    echo 2. Not authenticated - run: git config --global user.email "your-email@example.com"
    echo 3. Repository doesn't exist - create it on GitHub first
    echo 4. Wrong URL - check remote with: git remote -v
    echo.
    echo To authenticate with GitHub:
    echo 1. Create a personal access token: https://github.com/settings/tokens
    echo 2. Use the token as your password when prompted
    echo.
)

pause