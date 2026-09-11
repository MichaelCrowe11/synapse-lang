@echo off
echo Testing local Docker build...
echo.

echo Building with production Dockerfile...
docker build -f Dockerfile.production -t synapse-docs-v2-test .

if %errorlevel% equ 0 (
    echo.
    echo ✓ Docker build successful!
    echo.
    echo Testing the container locally...
    docker run -d -p 8080:8080 --name synapse-test synapse-docs-v2-test

    echo.
    echo Container started. Opening http://localhost:8080 in 5 seconds...
    timeout /t 5
    start http://localhost:8080

    echo.
    echo To stop the test container:
    echo   docker stop synapse-test
    echo   docker rm synapse-test
) else (
    echo.
    echo ✗ Docker build failed!
    echo.
    echo Check the error messages above.
    echo Common issues:
    echo - Missing files
    echo - Syntax errors in Python
    echo - Invalid Dockerfile commands
)

pause