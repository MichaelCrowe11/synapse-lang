@echo off
echo ========================================
echo Synapse Language - PyPI Upload Script
echo ========================================
echo.
echo This script will upload Synapse v1.0.2 to PyPI
echo.
echo IMPORTANT: You need a PyPI API token!
echo If you don't have one:
echo   1. Go to https://pypi.org/manage/account/token/
echo   2. Create a new API token
echo   3. Copy the token (starts with pypi-)
echo.
echo ========================================
echo.

set /p UPLOAD_TYPE="Upload to [T]est PyPI or [P]roduction PyPI? (T/P): "

if /i "%UPLOAD_TYPE%"=="T" (
    echo.
    echo Uploading to Test PyPI...
    python -m twine upload --repository testpypi dist/* -u __token__
    echo.
    echo If successful, test with:
    echo   pip install -i https://test.pypi.org/simple/ synapse-lang
) else if /i "%UPLOAD_TYPE%"=="P" (
    echo.
    echo Uploading to Production PyPI...
    python -m twine upload dist/* -u __token__
    echo.
    echo If successful, install with:
    echo   pip install synapse-lang
) else (
    echo Invalid choice. Please run again and choose T or P.
)

echo.
echo ========================================
echo Upload complete!
echo ========================================
pause