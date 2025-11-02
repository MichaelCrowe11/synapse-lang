#!/usr/bin/env python3
"""
Setup GitHub repository structure for Synapse Language
Creates all necessary GitHub templates and documentation
"""

from pathlib import Path

# Base directory
base_dir = Path("/mnt/c/Users/micha/synapse-lang")

# Create directories
dirs_to_create = [
    ".github/ISSUE_TEMPLATE",
    ".github/workflows",
    "docs/tutorials",
    "docs/api",
    "scripts"
]

for dir_path in dirs_to_create:
    (base_dir / dir_path).mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directory: {dir_path}")

# Create PULL_REQUEST_TEMPLATE.md
pr_template = """## Description
Brief description of the changes in this PR.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Which areas does this PR affect?
- [ ] Core Language
- [ ] Quantum Computing
- [ ] AI/ML Integration
- [ ] Visual Programming
- [ ] Real-time Collaboration
- [ ] Blockchain Verification
- [ ] Distributed Computing
- [ ] Mobile Framework
- [ ] Documentation
- [ ] Tests

## How Has This Been Tested?
Describe the tests that you ran to verify your changes.

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Documentation updated

## Checklist:
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable):
Add screenshots to help explain your changes.

## Additional Notes:
Any additional information that reviewers should know.
"""

with open(base_dir / ".github/PULL_REQUEST_TEMPLATE.md", "w") as f:
    f.write(pr_template)
print("✅ Created PULL_REQUEST_TEMPLATE.md")

# Create FUNDING.yml
funding_yml = """# These are supported funding model platforms

github: [michaelcrowe11]
patreon: # Replace with a single Patreon username
open_collective: # Replace with a single Open Collective username
ko_fi: # Replace with a single Ko-fi username
tidelift: # Replace with a single Tidelift platform-name/package-name
community_bridge: # Replace with a single Community Bridge project-name
liberapay: # Replace with a single Liberapay username
issuehunt: # Replace with a single IssueHunt username
otechie: # Replace with a single Otechie username
lfx_crowdfunding: # Replace with a single LFX Crowdfunding project-name
custom: # Replace with up to 4 custom sponsorship URLs
"""

with open(base_dir / ".github/FUNDING.yml", "w") as f:
    f.write(funding_yml)
print("✅ Created FUNDING.yml")

# Create CODE_OF_CONDUCT.md
code_of_conduct = """# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, caste, color, religion, or sexual
identity and orientation.

## Our Standards

Examples of behavior that contributes to a positive environment:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior:

* The use of sexualized language or imagery, and sexual attention or advances
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information without explicit permission
* Other conduct which could reasonably be considered inappropriate

## Our Responsibilities

Project maintainers are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
synapse-lang@outlook.com.

All complaints will be reviewed and investigated promptly and fairly.

## Attribution

This Code of Conduct is adapted from the Contributor Covenant, version 2.1,
available at https://www.contributor-covenant.org/version/2/1/code_of_conduct.html
"""

with open(base_dir / ".github/CODE_OF_CONDUCT.md", "w") as f:
    f.write(code_of_conduct)
print("✅ Created CODE_OF_CONDUCT.md")

# Create SECURITY.md
security_md = """# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for
receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 2.3.x   | ✅ Current version |
| 2.2.x   | ⚠️ Security fixes only |
| 2.1.x   | ⚠️ Security fixes only |
| 2.0.x   | ❌ No longer supported |
| < 2.0   | ❌ No longer supported |

## Reporting a Vulnerability

Please report security vulnerabilities to: synapse-security@outlook.com

You should receive a response within 48 hours. If the issue is confirmed, we will
release a patch as soon as possible depending on complexity.

Please include:
- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the issue
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

## Disclosure Policy

When we receive a security bug report, we will:
1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported releases
4. Release new versions and announce the vulnerability

## Comments on this Policy

If you have suggestions on how this process could be improved, please submit a
pull request or open an issue to discuss.
"""

with open(base_dir / ".github/SECURITY.md", "w") as f:
    f.write(security_md)
print("✅ Created SECURITY.md")

# Create comprehensive test workflow
test_workflow = """name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]

    - name: Lint with ruff
      run: |
        ruff check synapse_lang/

    - name: Type check with mypy
      run: |
        mypy synapse_lang/

    - name: Test with pytest
      run: |
        pytest tests/ --cov=synapse_lang --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  docker:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Build Docker image
      run: |
        docker build -t synapse-lang:test .

    - name: Test Docker image
      run: |
        docker run --rm synapse-lang:test python -c "import synapse_lang; print(synapse_lang.__version__)"

  publish:
    needs: [test]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Build package
      run: |
        python -m pip install --upgrade pip build
        python -m build

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
"""

with open(base_dir / ".github/workflows/ci.yml", "w") as f:
    f.write(test_workflow)
print("✅ Created CI/CD workflow")

# Create Docker publish workflow
docker_workflow = """name: Docker Publish

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'
  workflow_dispatch:

env:
  REGISTRY: docker.io
  IMAGE_NAME: michaelcrowe11/synapse-lang

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Log in to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
"""

with open(base_dir / ".github/workflows/docker.yml", "w") as f:
    f.write(docker_workflow)
print("✅ Created Docker workflow")

# Create comprehensive CONTRIBUTING.md
contributing = """# Contributing to Synapse Language

First off, thank you for considering contributing to Synapse Language! It's people like you that make Synapse such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by the [Synapse Code of Conduct](.github/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, please include as many details as possible using our [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml).

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml) to provide:

- A clear and descriptive title
- A detailed description of the proposed feature
- Examples of how it would be used
- Why this enhancement would be useful

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:

- `good first issue` - Simple issues perfect for beginners
- `help wanted` - Issues where we need community help
- `documentation` - Help improve our docs

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows our style guidelines
5. Issue that pull request!

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/synapse-lang.git
cd synapse-lang

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
ruff check synapse_lang/

# Run type checking
mypy synapse_lang/
```

## Style Guidelines

### Python Style

We use:
- `black` for code formatting (line length: 100)
- `ruff` for linting
- `mypy` for type checking

Run formatting before committing:
```bash
black synapse_lang/
ruff check --fix synapse_lang/
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests liberally after the first line

Example:
```
Add quantum state visualization feature

- Implement Bloch sphere representation
- Add real-time state updates
- Include measurement probabilities

Fixes #123
```

### Documentation

- Use docstrings for all public functions and classes
- Follow NumPy docstring style
- Update README.md if adding new features
- Add examples for complex functionality

## Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage
- Test on multiple Python versions if possible

## Project Structure

```
synapse-lang/
├── synapse_lang/          # Main package
│   ├── quantum/           # Quantum computing modules
│   ├── backends/          # Computation backends
│   ├── pharmkit/          # Drug discovery toolkit
│   └── ...
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Example scripts
└── scripts/               # Utility scripts
```

## Community

- **Discord**: Join our [Discord server](https://discord.gg/synapse-lang)
- **Forums**: Visit [community.synapse-lang.org](https://community.synapse-lang.org)
- **Twitter**: Follow [@SynapseLang](https://twitter.com/SynapseLang)

## Recognition

Contributors are recognized in:
- AUTHORS.md file
- GitHub contributors page
- Release notes

## Questions?

Feel free to open an issue with the `question` label or reach out on Discord!

Thank you for contributing! 🚀
"""

# Update existing CONTRIBUTING.md
with open(base_dir / "CONTRIBUTING.md", "w") as f:
    f.write(contributing)
print("✅ Updated CONTRIBUTING.md")

print("\n✨ GitHub repository structure created successfully!")
print("Next steps:")
print("1. Initialize git repository: git init")
print("2. Add remote: git remote add origin https://github.com/michaelcrowe11/synapse-lang.git")
print("3. Push to GitHub: git push -u origin main")
