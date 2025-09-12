# Synapse Language Publishing Guide

## Quick Start

### Publish to All Platforms
```bash
# Unix/Linux/macOS
./publish.sh all

# Windows
publish.bat all
```

### Publish to Specific Platforms
```bash
# PyPI only
python publish_all.py pypi

# VS Code Marketplace only
python publish_all.py vscode

# npm registry only
python publish_all.py npm

# Multiple platforms
python publish_all.py pypi vscode npm
```

## Platform-Specific Instructions

### 1. PyPI (Python Package Index)

#### First-time Setup
1. Create account at https://pypi.org/account/register/
2. Generate API token: https://pypi.org/manage/account/token/
3. Configure `.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

#### Publishing
```bash
# Test on TestPyPI first
python publish_all.py pypi --test-pypi

# Publish to PyPI
python publish_all.py pypi

# Verify installation
pip install synapse-lang==1.0.3
```

### 2. VS Code Marketplace

#### First-time Setup
1. Create publisher account: https://marketplace.visualstudio.com/manage
2. Install vsce: `npm install -g vsce`
3. Login: `vsce login YOUR-PUBLISHER-NAME`

#### Publishing
```bash
# Build and publish extension
python publish_all.py vscode

# Verify in VS Code
# Extensions → Search "Synapse Language"
```

### 3. npm Registry

#### First-time Setup
1. Create account at https://www.npmjs.com/signup
2. Login: `npm login`
3. Enable 2FA (recommended)

#### Publishing
```bash
# Publish to npm
python publish_all.py npm

# Verify installation
npm install @synapse-lang/core@1.0.3
```

### 4. GitHub Releases

#### First-time Setup
1. Install GitHub CLI: https://cli.github.com/
2. Authenticate: `gh auth login`

#### Publishing
```bash
# Create release with assets
python publish_all.py github

# View release
gh release view v1.0.3
```

## Advanced Options

### Dry Run (Preview Changes)
```bash
# See what would be published without actually doing it
python publish_all.py all --dry-run
```

### Verbose Output
```bash
# Show detailed command execution
python publish_all.py all --verbose
```

### Skip Tests
```bash
# Skip test suite (not recommended)
python publish_all.py all --skip-tests
```

## Pre-Publishing Checklist

- [ ] Update version in `synapse_lang/__init__.py`
- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Run tests: `pytest tests/`
- [ ] Commit changes: `git commit -am "Release v1.0.3"`
- [ ] Tag release: `git tag v1.0.3`
- [ ] Push changes: `git push origin main --tags`

## Version Management

The version is centrally managed in `synapse_lang/__init__.py`. The publishing script automatically:
- Reads version from `__init__.py`
- Updates `package.json` for VS Code extension
- Updates npm package version
- Creates GitHub release with matching tag

## Troubleshooting

### PyPI Upload Fails
- Check `.pypirc` configuration
- Verify API token is valid
- Ensure you're not uploading duplicate version

### VS Code Extension Fails
- Run `npm install` in `vscode-extension/`
- Check `vsce` is installed: `npm install -g vsce`
- Verify publisher account: `vsce ls-publishers`

### npm Publish Fails
- Check login: `npm whoami`
- Verify package name is available
- Ensure version hasn't been published

### GitHub Release Fails
- Check GitHub CLI auth: `gh auth status`
- Verify repository permissions
- Ensure tag doesn't already exist

## Platform URLs

After successful publishing, your package will be available at:

- **PyPI**: https://pypi.org/project/synapse-lang/
- **VS Code**: https://marketplace.visualstudio.com/items?itemName=synapse-lang.synapse-lang
- **npm**: https://www.npmjs.com/package/@synapse-lang/core
- **GitHub**: https://github.com/MichaelCrowe11/synapse-lang/releases

## Automation with CI/CD

For automated publishing, you can use GitHub Actions:

```yaml
name: Publish Release

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          pip install build twine
          npm install -g vsce
      
      - name: Publish to all platforms
        env:
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
          VSCE_TOKEN: ${{ secrets.VSCE_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: |
          python publish_all.py all
```

## Support

For issues or questions about publishing:
- GitHub Issues: https://github.com/MichaelCrowe11/synapse-lang/issues
- Email: michaelcrowe11@users.noreply.github.com