@echo off
REM Synapse Language v2.3.0 - Docker Publishing Script for Windows
REM This script builds and publishes the Docker image to Docker Hub

echo ================================================
echo SYNAPSE LANGUAGE DOCKER PUBLISHER (Windows)
echo ================================================
echo.
echo Image: michaelcrowe11/synapse-lang:2.3.2
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running or not installed.
    echo Please start Docker Desktop or install from:
    echo https://docs.docker.com/desktop/windows/install/
    pause
    exit /b 1
)

echo Docker is running...
echo.

REM Login to Docker Hub
echo Please login to Docker Hub:
docker login
if %errorlevel% neq 0 (
    echo ERROR: Docker login failed
    pause
    exit /b 1
)

echo.
echo Building Docker image...
echo ------------------------------

REM Build the image
docker build -t michaelcrowe11/synapse-lang:2.3.2 -t michaelcrowe11/synapse-lang:latest .
if %errorlevel% neq 0 (
    echo ERROR: Docker build failed
    pause
    exit /b 1
)

echo.
echo Build successful!
echo.

REM Test the image
echo Testing the image...
docker run --rm michaelcrowe11/synapse-lang:2.3.2 python -c "import synapse_lang; print(f'Synapse v{synapse_lang.__version__} working!')"
if %errorlevel% neq 0 (
    echo WARNING: Test failed, but continuing...
)

echo.
echo Pushing to Docker Hub...
echo ------------------------------

REM Push version tag
docker push michaelcrowe11/synapse-lang:2.3.2
if %errorlevel% neq 0 (
    echo ERROR: Failed to push version tag
    pause
    exit /b 1
)

REM Push latest tag
docker push michaelcrowe11/synapse-lang:latest
if %errorlevel% neq 0 (
    echo ERROR: Failed to push latest tag
    pause
    exit /b 1
)

echo.
echo ================================================
echo SUCCESS! Docker image published!
echo ================================================
echo.
echo Published to Docker Hub:
echo   https://hub.docker.com/r/michaelcrowe11/synapse-lang
echo.
echo Installation Commands:
echo   docker pull michaelcrowe11/synapse-lang:2.3.0
echo   docker pull michaelcrowe11/synapse-lang:latest
echo.
echo Run Commands:
echo   docker run -it michaelcrowe11/synapse-lang:2.3.2
echo   docker run -p 8888:8888 michaelcrowe11/synapse-lang:2.3.2 jupyter notebook --ip=0.0.0.0 --allow-root
echo.
pause