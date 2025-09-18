#!/bin/bash
# SYNAPSE ESSENTIAL PUBLISHING SCRIPT
# Publishes to PyPI, GitHub, and npm

echo "=================================================="
echo "    SYNAPSE LANGUAGE - ESSENTIAL PUBLISHING"
echo "=================================================="

VERSION="2.2.0"
PACKAGE="synapse-lang"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}Package: $PACKAGE v$VERSION${NC}"
echo "Date: $(date -Iseconds)"

# ===========================================
# 1. VALIDATE PACKAGE
# ===========================================
echo -e "\n${BLUE}[1/6] VALIDATING PACKAGE${NC}"
echo "================================"

# Check required files
for file in setup.py README.md LICENSE pyproject.toml; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file exists"
    else
        echo -e "  ${RED}✗${NC} $file missing"
        exit 1
    fi
done

# Check package directory
if [ -d "synapse_lang" ]; then
    echo -e "  ${GREEN}✓${NC} synapse_lang/ directory exists"
else
    echo -e "  ${RED}✗${NC} synapse_lang/ directory missing"
    exit 1
fi

# ===========================================
# 2. CLEAN PREVIOUS BUILDS
# ===========================================
echo -e "\n${BLUE}[2/6] CLEANING OLD BUILDS${NC}"
echo "================================"

rm -rf dist/ build/ *.egg-info/
echo -e "  ${GREEN}✓${NC} Cleaned old builds"

# ===========================================
# 3. BUILD DISTRIBUTIONS
# ===========================================
echo -e "\n${BLUE}[3/6] BUILDING DISTRIBUTIONS${NC}"
echo "================================"

# Build source distribution
echo "  Building source distribution..."
python3 setup.py sdist --quiet
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Source distribution built"
else
    echo -e "  ${RED}✗${NC} Failed to build source distribution"
fi

# Build wheel
echo "  Building wheel..."
python3 setup.py bdist_wheel --quiet 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Wheel built"
else
    echo -e "  ${RED}✗${NC} Failed to build wheel (optional)"
fi

# List built files
echo -e "\n  Built packages:"
for file in dist/*; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo "    • $(basename $file) ($size)"
    fi
done

# ===========================================
# 4. CREATE CHECKSUMS
# ===========================================
echo -e "\n${BLUE}[4/6] GENERATING CHECKSUMS${NC}"
echo "================================"

cd dist/
for file in *; do
    if [ -f "$file" ]; then
        sha256sum "$file" > "$file.sha256"
        echo -e "  ${GREEN}✓${NC} $file.sha256"
    fi
done
cd ..

# ===========================================
# 5. PYPI CONFIGURATION
# ===========================================
echo -e "\n${BLUE}[5/6] PYPI CONFIGURATION${NC}"
echo "================================"

# Create .pypirc if it doesn't exist
if [ ! -f ~/.pypirc ]; then
    echo "Creating .pypirc template..."
    cat > ~/.pypirc.template << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = # Add your PyPI token here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = # Add your TestPyPI token here
EOF
    echo -e "  ${GREEN}✓${NC} Created ~/.pypirc.template"
    echo "  ⚠️  Add your PyPI tokens to ~/.pypirc before publishing"
else
    echo -e "  ${GREEN}✓${NC} .pypirc exists"
fi

# ===========================================
# 6. PUBLISHING COMMANDS
# ===========================================
echo -e "\n${BLUE}[6/6] PUBLISHING COMMANDS${NC}"
echo "================================"

echo -e "\n${GREEN}Ready to publish!${NC} Use these commands:"
echo ""
echo "# 1. PYPI TEST (recommended first)"
echo "twine upload --repository testpypi dist/*"
echo ""
echo "# 2. PYPI PRODUCTION"
echo "twine upload dist/*"
echo ""
echo "# 3. GITHUB"
echo "git add ."
echo "git commit -m \"Release v$VERSION - Enhanced backend support\""
echo "git tag -a v$VERSION -m \"Version $VERSION\""
echo "git push origin main --tags"
echo ""
echo "# 4. CREATE GITHUB RELEASE"
echo "gh release create v$VERSION dist/* --title \"v$VERSION\" --notes \"Enhanced backend support\""
echo ""
echo "# 5. NPM (after creating package.json)"
echo "npm publish --access public"
echo ""
echo "# 6. DOCKER HUB"
echo "docker build -t $PACKAGE:$VERSION ."
echo "docker tag $PACKAGE:$VERSION $PACKAGE:latest"
echo "docker push $PACKAGE:$VERSION"
echo "docker push $PACKAGE:latest"

# ===========================================
# CREATE INSTALLATION GUIDE
# ===========================================
cat > INSTALL.md << EOF
# Synapse Language Installation Guide

## Quick Install

### From PyPI (Recommended)
\`\`\`bash
pip install synapse-lang
\`\`\`

### From TestPyPI (Beta)
\`\`\`bash
pip install -i https://test.pypi.org/simple/ synapse-lang
\`\`\`

### From Source
\`\`\`bash
git clone https://github.com/synapse-lang/synapse-lang.git
cd synapse-lang
pip install -e .
\`\`\`

## Platform-Specific Installation

### macOS (Homebrew)
\`\`\`bash
brew tap synapse-lang/tap
brew install synapse-lang
\`\`\`

### Conda
\`\`\`bash
conda install -c conda-forge synapse-lang
\`\`\`

### Docker
\`\`\`bash
docker pull synapse-lang:latest
docker run -it synapse-lang:latest
\`\`\`

### npm (Node.js wrapper)
\`\`\`bash
npm install -g @synapse-lang/cli
\`\`\`

## Verify Installation

\`\`\`bash
python -c "import synapse_lang; print(synapse_lang.__version__)"
\`\`\`

## Optional Dependencies

For full functionality:
\`\`\`bash
pip install synapse-lang[all]
\`\`\`

For specific features:
\`\`\`bash
pip install synapse-lang[quantum]  # Quantum computing
pip install synapse-lang[gpu]      # GPU acceleration
pip install synapse-lang[ml]       # Machine learning
\`\`\`

## Troubleshooting

If you encounter issues:
1. Ensure Python 3.8+ is installed
2. Update pip: \`pip install --upgrade pip\`
3. Clear pip cache: \`pip cache purge\`
4. Report issues: https://github.com/synapse-lang/synapse-lang/issues

## Links

- PyPI: https://pypi.org/project/synapse-lang/
- GitHub: https://github.com/synapse-lang/synapse-lang
- Documentation: https://docs.synapse-lang.org
- Discord: https://discord.gg/synapse-lang
EOF

echo -e "\n${GREEN}✓${NC} Created INSTALL.md"

# ===========================================
# SUMMARY
# ===========================================
echo -e "\n=================================================="
echo -e "${GREEN}BUILD COMPLETE!${NC}"
echo "=================================================="
echo ""
echo "Package: $PACKAGE v$VERSION"
echo "Files built: $(ls -1 dist/ 2>/dev/null | wc -l)"
echo ""
echo "Next steps:"
echo "1. Install twine: pip install twine"
echo "2. Configure ~/.pypirc with your API tokens"
echo "3. Run the publishing commands shown above"
echo ""
echo "For automated publishing, run:"
echo "  python3 validate_and_publish.py --production"
echo ""
echo "=================================================="