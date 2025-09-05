# Synapse Language - GitHub Codespaces Production Setup

## Instructions for AI Coding Agents

This document provides step-by-step instructions for AI coding agents (Claude, GPT-4, Copilot, etc.) to finalize the Synapse language production environment in GitHub Codespaces.

---

## 🎯 Objective
Transform Synapse from a prototype to a production-ready scientific computing language with full CI/CD, documentation, and deployment infrastructure.

---

## 📋 Prerequisites Check
```bash
# Verify you're in GitHub Codespaces
echo $CODESPACES
echo $GITHUB_REPOSITORY

# Check Python version (need 3.8+)
python --version

# Check git configuration
git config --get user.name
git config --get user.email
```

---

## 🚀 Phase 1: Environment Setup

### 1.1 Create Codespaces Configuration
```bash
# Create .devcontainer directory
mkdir -p .devcontainer

# Create devcontainer.json
cat > .devcontainer/devcontainer.json << 'EOF'
{
  "name": "Synapse Development Environment",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "18"
    },
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-toolsai.jupyter",
        "github.copilot",
        "synapse-lang.synapse-language"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "python.formatting.provider": "black",
        "python.testing.pytestEnabled": true,
        "files.associations": {
          "*.syn": "synapse",
          "*.synapse": "synapse"
        }
      }
    }
  },
  "postCreateCommand": "pip install -e . && pip install -r requirements-dev.txt",
  "forwardPorts": [8000, 8888, 5000],
  "remoteUser": "vscode"
}
EOF
```

### 1.2 Create Development Dependencies
```bash
cat > requirements-dev.txt << 'EOF'
# Development dependencies
pytest>=7.0.0
pytest-cov>=3.0.0
pytest-asyncio>=0.20.0
pytest-benchmark>=3.4.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.950
pylint>=2.13.0
sphinx>=4.5.0
sphinx-rtd-theme>=1.0.0
twine>=4.0.0
wheel>=0.37.0
setuptools>=60.0.0
jupyterlab>=3.4.0
ipykernel>=6.15.0
notebook>=6.4.0
pre-commit>=2.19.0
tox>=3.25.0
coverage>=6.4
hypothesis>=6.50.0
EOF
```

---

## 🧪 Phase 2: Testing Infrastructure

### 2.1 Create Test Suite
```bash
# Create test directory structure
mkdir -p tests/{unit,integration,performance,examples}

# Create pytest configuration
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --benchmark-disable
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    benchmark: marks tests as performance benchmarks
EOF

# Create main test file
cat > tests/test_core.py << 'EOF'
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse_interpreter import SynapseInterpreter, Lexer, UncertainValue
from synapse_parser import parse
from synapse_ast import *

class TestLexer:
    def test_tokenize_numbers(self):
        lexer = Lexer("42 3.14 2.5e-3")
        tokens = lexer.tokenize()
        assert len(tokens) == 4  # 3 numbers + EOF
        
    def test_tokenize_keywords(self):
        lexer = Lexer("hypothesis experiment parallel")
        tokens = lexer.tokenize()
        assert len([t for t in tokens if t.type.name in ['HYPOTHESIS', 'EXPERIMENT', 'PARALLEL']]) == 3
    
    def test_tokenize_uncertain(self):
        lexer = Lexer("uncertain x = 10 ± 0.5")
        tokens = lexer.tokenize()
        assert any(t.type.name == 'UNCERTAIN' for t in tokens)
        assert any(t.type.name == 'UNCERTAINTY' for t in tokens)

class TestParser:
    def test_parse_assignment(self):
        ast = parse("x = 42")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
    
    def test_parse_parallel(self):
        code = """
        parallel {
            branch A: compute_1
            branch B: compute_2
        }
        """
        ast = parse(code)
        assert any(isinstance(node, ParallelNode) for node in ast.body)
    
    def test_parse_hypothesis(self):
        code = """
        hypothesis TestHyp {
            assume: condition
            predict: outcome
            validate: experiment
        }
        """
        ast = parse(code)
        assert any(isinstance(node, HypothesisNode) for node in ast.body)

class TestInterpreter:
    def test_uncertain_arithmetic(self):
        interp = SynapseInterpreter()
        interp.execute("uncertain x = 10 ± 0.5")
        interp.execute("uncertain y = 20 ± 1.0")
        
        x = interp.variables['x']
        y = interp.variables['y']
        
        assert isinstance(x, UncertainValue)
        assert x.value == 10
        assert x.uncertainty == 0.5
        
        result = x + y
        assert result.value == 30
        assert result.uncertainty > 0
    
    def test_parallel_execution(self):
        interp = SynapseInterpreter()
        code = """
        parallel {
            branch A: task_1
            branch B: task_2
        }
        """
        results = interp.execute(code)
        assert len(results) > 0
        assert 'parallel_execution' in results[0]

@pytest.mark.integration
class TestIntegration:
    def test_scientific_functions(self):
        from synapse_scientific import integrate_scientific_functions
        interp = SynapseInterpreter()
        integrate_scientific_functions(interp)
        
        assert 'np' in interp.variables
        assert 'tensor' in interp.variables
        assert 'monte_carlo' in interp.variables
    
    def test_jit_compilation(self):
        from synapse_jit import JITCompiler
        compiler = JITCompiler()
        
        code = "x = 42"
        func = compiler.compile_function(code)
        assert callable(func)

@pytest.mark.benchmark
class TestPerformance:
    def test_parallel_speedup(self, benchmark):
        from synapse_jit import ParallelExecutor
        import numpy as np
        
        executor = ParallelExecutor()
        data = np.random.randn(10000)
        
        def square(x):
            return x * x
        
        result = benchmark(executor.parallel_map_numba, square, data)
        assert len(result) == len(data)
EOF
```

### 2.2 Create GitHub Actions CI/CD
```bash
mkdir -p .github/workflows

cat > .github/workflows/ci.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [ master, main, develop ]
  pull_request:
    branches: [ master, main ]
  release:
    types: [created]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=15 --max-line-length=127 --statistics
    
    - name: Type check with mypy
      run: |
        mypy --ignore-missing-imports .
    
    - name: Test with pytest
      run: |
        pytest -v --cov=. --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Build package
      run: |
        pip install wheel setuptools
        python setup.py sdist bdist_wheel
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        pip install twine
        twine upload dist/*

  docker:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: synapselang/synapse:latest
EOF
```

---

## 📦 Phase 3: Package Setup

### 3.1 Create setup.py
```bash
cat > setup.py << 'EOF'
from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="synapse-lang",
    version="0.2.0",
    author="Synapse Team",
    author_email="contact@synapse-lang.org",
    description="A language for deep scientific reasoning and parallel thought processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichaelCrowe11/synapse-lang",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "docs": [
            "sphinx>=4.5.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "synapse=synapse:main",
            "synapse-repl=synapse_repl:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.syn", "*.md", "examples/*.syn"],
    },
)
EOF
```

### 3.2 Create Dockerfile
```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install Synapse
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 synapse && chown -R synapse:synapse /app
USER synapse

# Expose Jupyter port if needed
EXPOSE 8888

# Default command starts REPL
CMD ["synapse"]
EOF
```

---

## 📚 Phase 4: Documentation

### 4.1 Create Documentation Structure
```bash
mkdir -p docs/{source,_static,_templates}

cat > docs/source/conf.py << 'EOF'
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'Synapse Language'
copyright = '2024, Synapse Team'
author = 'Synapse Team'
release = '0.2.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.mathjax',
]

templates_path = ['_templates']
exclude_patterns = []
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
EOF

cat > docs/source/index.rst << 'EOF'
Synapse Language Documentation
==============================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   language_guide
   api_reference
   examples
   contributing

Welcome to Synapse
------------------

Synapse is a proprietary programming language designed for deep scientific 
reasoning and enhanced parallel thought processing pipelines.

Key Features
------------

* **Uncertainty-aware computing** - Built-in error propagation
* **Parallel execution** - Native support for concurrent computation
* **Scientific computing** - Integrated NumPy/SciPy functionality
* **JIT compilation** - Optimized performance with Numba
* **Interactive REPL** - Exploratory programming environment

Quick Example
-------------

.. code-block:: synapse

    uncertain mass = 10.5 ± 0.2
    uncertain velocity = 25.3 ± 0.5
    
    parallel {
        branch kinetic: calculate_kinetic_energy(mass, velocity)
        branch momentum: calculate_momentum(mass, velocity)
    }

Installation
------------

.. code-block:: bash

    pip install synapse-lang
    
    # Or from source
    git clone https://github.com/MichaelCrowe11/synapse-lang
    cd synapse-lang
    pip install -e .

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
EOF
```

### 4.2 Create Makefile for Documentation
```bash
cat > docs/Makefile << 'EOF'
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
EOF
```

---

## 🎨 Phase 5: VS Code Extension Publishing

### 5.1 Prepare VS Code Extension
```bash
cd vscode-extension

# Create extension manifest
cat > extension.js << 'EOF'
const vscode = require('vscode');

function activate(context) {
    console.log('Synapse language extension activated');
    
    // Register commands
    let runCommand = vscode.commands.registerCommand('synapse.run', () => {
        const terminal = vscode.window.createTerminal('Synapse');
        const file = vscode.window.activeTextEditor?.document.fileName;
        if (file && file.endsWith('.syn')) {
            terminal.sendText(`synapse ${file}`);
            terminal.show();
        }
    });
    
    let replCommand = vscode.commands.registerCommand('synapse.repl', () => {
        const terminal = vscode.window.createTerminal('Synapse REPL');
        terminal.sendText('synapse');
        terminal.show();
    });
    
    context.subscriptions.push(runCommand, replCommand);
}

function deactivate() {}

module.exports = { activate, deactivate };
EOF

# Update package.json with commands
cat >> package.json << 'EOF'
  ,
  "activationEvents": [
    "onLanguage:synapse"
  ],
  "commands": [
    {
      "command": "synapse.run",
      "title": "Run Synapse File"
    },
    {
      "command": "synapse.repl",
      "title": "Start Synapse REPL"
    }
  ]
EOF

# Create README for extension
cat > README.md << 'EOF'
# Synapse Language Support for VS Code

Official VS Code extension for the Synapse programming language.

## Features

- Syntax highlighting for `.syn` files
- Code snippets for common patterns
- Run Synapse files directly from VS Code
- Integrated REPL support

## Installation

1. Install from VS Code Marketplace: Search for "Synapse Language"
2. Or install manually: `code --install-extension synapse-language-0.1.0.vsix`

## Usage

- Open any `.syn` file for automatic syntax highlighting
- Use `Ctrl+Shift+P` → "Run Synapse File" to execute current file
- Use `Ctrl+Shift+P` → "Start Synapse REPL" for interactive mode
EOF

cd ..
```

---

## 🚢 Phase 6: Deployment & Release

### 6.1 Create Release Script
```bash
cat > scripts/release.sh << 'EOF'
#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh <version>"
    exit 1
fi

echo "Releasing Synapse v$VERSION..."

# Update version in files
sed -i "s/version=\".*\"/version=\"$VERSION\"/" setup.py
sed -i "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" vscode-extension/package.json
sed -i "s/release = '.*'/release = '$VERSION'/" docs/source/conf.py

# Run tests
pytest

# Build documentation
cd docs && make html && cd ..

# Build package
python setup.py sdist bdist_wheel

# Create git tag
git add -A
git commit -m "Release v$VERSION"
git tag -a "v$VERSION" -m "Release version $VERSION"
git push origin master --tags

echo "Release v$VERSION completed!"
EOF

chmod +x scripts/release.sh
```

### 6.2 Create Docker Compose for Development
```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  synapse:
    build: .
    image: synapselang/synapse:latest
    volumes:
      - .:/app
      - synapse-data:/data
    ports:
      - "8888:8888"  # Jupyter
      - "5000:5000"  # API if needed
    environment:
      - PYTHONPATH=/app
    command: jupyter lab --ip=0.0.0.0 --no-browser --allow-root

  docs:
    image: nginx:alpine
    volumes:
      - ./docs/build/html:/usr/share/nginx/html:ro
    ports:
      - "8080:80"

volumes:
  synapse-data:
EOF
```

---

## 🔧 Phase 7: Final Configuration

### 7.1 Create Pre-commit Hooks
```bash
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=127', '--extend-ignore=E203']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF

# Install pre-commit
pip install pre-commit
pre-commit install
```

### 7.2 Create Jupyter Kernel
```bash
cat > install_kernel.py << 'EOF'
#!/usr/bin/env python3
"""Install Synapse Jupyter kernel"""

import json
import os
import sys
from pathlib import Path
from jupyter_client.kernelspec import KernelSpecManager

kernel_json = {
    "argv": [sys.executable, "-m", "synapse_kernel", "-f", "{connection_file}"],
    "display_name": "Synapse",
    "language": "synapse",
    "metadata": {
        "debugger": False
    }
}

def install_kernel():
    kernel_dir = Path.home() / ".local/share/jupyter/kernels/synapse"
    kernel_dir.mkdir(parents=True, exist_ok=True)
    
    with open(kernel_dir / "kernel.json", "w") as f:
        json.dump(kernel_json, f, indent=2)
    
    print(f"Synapse kernel installed at {kernel_dir}")

if __name__ == "__main__":
    install_kernel()
EOF

python install_kernel.py
```

---

## ✅ Phase 8: Validation Checklist

Run these commands to validate the setup:

```bash
# 1. Run tests
pytest -v

# 2. Check code quality
black --check .
flake8 .
mypy .

# 3. Build documentation
cd docs && make html && cd ..

# 4. Test Docker build
docker build -t synapse-test .
docker run -it synapse-test synapse -c "print('Hello from Synapse')"

# 5. Test installation
pip install -e .
synapse --help

# 6. Run example programs
synapse examples/quantum_simulation.syn
synapse examples/climate_model.syn
synapse examples/drug_discovery.syn

# 7. Start REPL
synapse

# 8. Test VS Code extension
cd vscode-extension
npm install
npm run compile
vsce package
```

---

## 🎯 Success Criteria

The production setup is complete when:

1. ✅ All tests pass on multiple Python versions
2. ✅ CI/CD pipeline runs successfully
3. ✅ Documentation builds without errors
4. ✅ Docker image builds and runs
5. ✅ VS Code extension installs and highlights syntax
6. ✅ REPL starts and executes code
7. ✅ Example programs run without errors
8. ✅ Package installs from PyPI (after publishing)

---

## 📝 Notes for AI Agents

- **Always run tests** after making changes
- **Use pre-commit hooks** to maintain code quality
- **Document all new features** in both code and docs
- **Follow semantic versioning** for releases
- **Keep dependencies updated** with `pip-compile`
- **Monitor CI/CD status** on GitHub Actions
- **Test on multiple platforms** before releasing

---

## 🚀 Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/MichaelCrowe11/synapse-lang
cd synapse-lang

# Install everything
pip install -e .
pip install -r requirements-dev.txt
pre-commit install

# Run tests
pytest

# Start developing
code .  # Opens in VS Code with Synapse support
```

---

This completes the production setup for Synapse in GitHub Codespaces!
EOF