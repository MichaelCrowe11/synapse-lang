@echo off
REM Synapse Language - Production Publication Script (Windows)
REM Publishes to PyPI with all commercial features enabled

echo ========================================
echo Synapse Language - Production Publisher
echo ========================================

REM Check Python version
python --version

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

REM Install required packages
echo Installing build requirements...
python -m pip install --upgrade pip setuptools wheel twine build

REM Run tests
echo Running test suite...
python -m pytest tests\ -v
if errorlevel 1 (
    echo Tests failed! Fix issues before publishing.
    exit /b 1
)

REM Display current version
echo Current version:
findstr "__version__" synapse_lang\__version__.py

REM Build the package
echo Building package...
python -m build

REM Check the build
echo Checking package...
python -m twine check dist\*

REM Display package contents
echo Package contents:
dir dist\

REM Confirm publication
echo.
echo WARNING: You are about to publish to PyPI!
echo This will make the package publicly available.
echo.
set /p TEST_FIRST="Publish to TEST PyPI first? (y/n): "

if "%TEST_FIRST%"=="y" (
    echo Publishing to TEST PyPI...
    python -m twine upload --repository testpypi dist\*
    
    echo.
    echo Package uploaded to TEST PyPI!
    echo Test with: pip install -i https://test.pypi.org/simple/ synapse-lang
    echo.
    set /p CONTINUE="Continue to production PyPI? (y/n): "
    
    if not "%CONTINUE%"=="y" (
        echo Aborted.
        exit /b 0
    )
)

REM Final confirmation
echo.
echo FINAL CONFIRMATION
echo ==================
echo You are about to publish Synapse Language to PyPI.
echo This action cannot be undone for this version.
echo.
set /p CONFIRM="Type 'PUBLISH' to confirm: "

if not "%CONFIRM%"=="PUBLISH" (
    echo Publication cancelled.
    exit /b 0
)

REM Publish to PyPI
echo Publishing to PyPI...
python -m twine upload dist\*

echo.
echo ========================================
echo Publication Complete!
echo ========================================
echo.
echo Package: synapse-lang
echo.
echo Install with: pip install synapse-lang
echo.
echo Next steps:
echo 1. Update website with new version
echo 2. Announce on social media
echo 3. Send newsletter to subscribers
echo 4. Update documentation
echo.
echo Commercial licenses available at:
echo https://synapse-lang.com/pricing
echo.