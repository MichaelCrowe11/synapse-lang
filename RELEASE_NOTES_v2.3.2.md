# Release Notes - Synapse Language v2.3.2

**Release Date**: September 18, 2025
**Type**: Patch Release (Naming Compliance)

## 🔧 Changes in v2.3.2

### Package Naming Compliance
- **Fixed**: PyPI package name now uses underscore (`synapse_lang`) instead of hyphen (`synapse-lang`) to comply with PEP 625
- **Impact**: Future uploads will meet PyPI's upcoming requirements for normalized package names
- **Backward Compatibility**: Users can still install using `pip install synapse-lang` (PyPI handles the redirect)

### Technical Updates
- Updated `setup.py` to use `synapse_lang` as package name
- Updated `pyproject.toml` with PEP 625 compliant naming
- Version bumped to 2.3.2 across all configuration files

## 📦 Installation

The package can still be installed using the familiar command:
```bash
pip install synapse-lang
```

PyPI automatically handles the normalization, so this change is transparent to users.

## 🔄 Migration

**No action required for existing users!** This is a naming compliance update only. All functionality remains the same as v2.3.1.

## 📊 Version Comparison

| Version | Package Name (Internal) | Install Command | Status |
|---------|------------------------|-----------------|--------|
| 2.3.1 | synapse-lang | `pip install synapse-lang` | Deprecated naming |
| 2.3.2 | synapse_lang | `pip install synapse-lang` | PEP 625 compliant ✅ |

## ✅ All Features Still Included

All 8 major enhancements from v2.3.0/2.3.1 remain:
1. Advanced Type Inference System
2. Real-time Collaboration
3. Visual Programming Interface
4. Distributed Computing Framework
5. AI-Powered Code Suggestions
6. Quantum Circuit Designer
7. Mobile App Framework
8. Blockchain Verification System

## 🔗 Links

- **PyPI**: https://pypi.org/project/synapse-lang/
- **NPM**: https://www.npmjs.com/package/synapse-lang-core
- **Docker Hub**: https://hub.docker.com/r/michaelcrowe11/synapse-lang
- **GitHub**: https://github.com/michaelcrowe11/synapse-lang

## 📝 Note from PyPI

This update addresses the following PyPI deprecation warning:
> "In the future, PyPI will require all newly uploaded source distribution filenames to comply with PEP 625."

By making this change now, we ensure continued smooth releases in the future.

---

**No functional changes in this release. This is purely a compliance update for future PyPI requirements.**