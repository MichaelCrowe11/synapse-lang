#!/bin/bash
#
# Synapse Language - Production Publication Script
# Publishes to PyPI with all commercial features enabled
#

set -e  # Exit on error

echo "========================================"
echo "Synapse Language - Production Publisher"
echo "========================================"

# Check Python version
python --version

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Install required packages
echo "Installing build requirements..."
pip install --upgrade pip setuptools wheel twine build

# Run tests
echo "Running test suite..."
python -m pytest tests/ -v || {
    echo "Tests failed! Fix issues before publishing."
    exit 1
}

# Update version if needed
echo "Current version:"
grep "__version__" synapse_lang/__version__.py

read -p "Enter new version (or press Enter to keep current): " NEW_VERSION
if [ ! -z "$NEW_VERSION" ]; then
    sed -i "s/__version__ = .*/__version__ = \"$NEW_VERSION\"/" synapse_lang/__version__.py
    sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    echo "Version updated to $NEW_VERSION"
fi

# Build the package
echo "Building package..."
python -m build

# Check the build
echo "Checking package..."
twine check dist/*

# Display package contents
echo "Package contents:"
ls -la dist/

# Confirm publication
echo ""
echo "WARNING: You are about to publish to PyPI!"
echo "This will make the package publicly available."
echo ""
read -p "Publish to TEST PyPI first? (y/n): " TEST_FIRST

if [ "$TEST_FIRST" = "y" ]; then
    echo "Publishing to TEST PyPI..."
    twine upload --repository testpypi dist/* || {
        echo "Test PyPI upload failed!"
        exit 1
    }
    
    echo ""
    echo "Package uploaded to TEST PyPI!"
    echo "Test with: pip install -i https://test.pypi.org/simple/ synapse-lang"
    echo ""
    read -p "Continue to production PyPI? (y/n): " CONTINUE
    
    if [ "$CONTINUE" != "y" ]; then
        echo "Aborted."
        exit 0
    fi
fi

# Final confirmation
echo ""
echo "FINAL CONFIRMATION"
echo "=================="
echo "You are about to publish Synapse Language to PyPI."
echo "This action cannot be undone for this version."
echo ""
read -p "Type 'PUBLISH' to confirm: " CONFIRM

if [ "$CONFIRM" != "PUBLISH" ]; then
    echo "Publication cancelled."
    exit 0
fi

# Publish to PyPI
echo "Publishing to PyPI..."
twine upload dist/*

# Create git tag
VERSION=$(grep "__version__" synapse_lang/__version__.py | cut -d'"' -f2)
git tag -a "v$VERSION" -m "Release version $VERSION"
git push origin "v$VERSION"

echo ""
echo "========================================"
echo "🎉 Publication Complete!"
echo "========================================"
echo ""
echo "Package: synapse-lang"
echo "Version: $VERSION"
echo ""
echo "Install with: pip install synapse-lang"
echo ""
echo "Next steps:"
echo "1. Update website with new version"
echo "2. Announce on social media"
echo "3. Send newsletter to subscribers"
echo "4. Update documentation"
echo ""
echo "Commercial licenses available at:"
echo "https://synapse-lang.com/pricing"
echo ""