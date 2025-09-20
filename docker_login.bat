@echo off
REM Docker Hub Login and Push Script for Synapse v2.3.0

echo ======================================================
echo   Docker Hub Publishing for Synapse Language v2.3.0
echo ======================================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo Docker is running!
echo.

echo Please log in to Docker Hub:
echo Username: synapselang
echo.
docker login -u synapselang

if %errorlevel% neq 0 (
    echo ERROR: Docker login failed.
    pause
    exit /b 1
)

echo.
echo Login successful! Now pushing images to Docker Hub...
echo.

echo Pushing synapselang/synapse-lang:2.3.0...
docker push synapselang/synapse-lang:2.3.0

if %errorlevel% neq 0 (
    echo ERROR: Failed to push version 2.3.0
    pause
    exit /b 1
)

echo Pushing synapselang/synapse-lang:latest...
docker push synapselang/synapse-lang:latest

if %errorlevel% neq 0 (
    echo ERROR: Failed to push latest tag
    pause
    exit /b 1
)

echo.
echo ======================================================
echo   SUCCESS! Docker images published to Docker Hub!
echo ======================================================
echo.
echo View your images at:
echo   https://hub.docker.com/r/synapselang/synapse-lang
echo.
echo Users can now pull with:
echo   docker pull synapselang/synapse-lang:2.3.0
echo   docker pull synapselang/synapse-lang:latest
echo.
pause