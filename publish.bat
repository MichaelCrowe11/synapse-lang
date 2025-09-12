@echo off
REM Synapse Language Publishing Script for Windows
REM Usage: publish.bat [all|pypi|vscode|npm|github] [--dry-run] [--test-pypi]

echo ================================================================================
echo Synapse Language Publisher
echo ================================================================================

REM Check Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    exit /b 1
)

REM Install required packages if missing
echo Checking dependencies...
pip show build >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing build...
    pip install build
)

pip show twine >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing twine...
    pip install twine
)

REM Run the publisher
python publish_all.py %*

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Publishing completed successfully!
) else (
    echo.
    echo [ERROR] Publishing failed. Check the output above for details.
)

pause