"""
Setup configuration for Synapse Language - PyPI Ready
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from package
version_file = Path(__file__).parent / "synapse_lang" / "__version__.py"
version = "1.0.0"
if version_file.exists():
    with open(version_file) as f:
        exec(f.read())
        version = locals().get("__version__", "1.0.0")

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="synapse-lang",
    version=version,
    author="Michael Benjamin Crowe",
    author_email="michael@synapse-lang.com",
    description="A revolutionary programming language for scientific computing with parallel execution and uncertainty quantification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michaelcrowe/synapse-lang",
    project_urls={
        "Bug Reports": "https://github.com/michaelcrowe/synapse-lang/issues",
        "Documentation": "https://synapse-lang.readthedocs.io",
        "Source Code": "https://github.com/michaelcrowe/synapse-lang",
        "Changelog": "https://github.com/michaelcrowe/synapse-lang/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests*", "docs*", "examples*", "benchmarks*"]),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "sympy>=1.9",
        "matplotlib>=3.4.0",
        "colorama>=0.4.4",
        "networkx>=2.6",
        "pandas>=1.3.0",
    ],
    extras_require={
        "gpu": [
            # Users should install ONE of these manually:
            # "cupy-cuda12x>=12.0",  # For CUDA 12.x
            # "torch>=2.0.0",  # Install with --index-url for CUDA
        ],
        "jit": [
            "numba>=0.58",
        ],
        "quantum": [
            "qiskit>=0.34.0",
            "pennylane>=0.20.0",
            "cirq>=0.13.0",
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-asyncio>=0.21",
            "black>=23.0",
            "ruff>=0.5",
            "mypy>=1.10",
            "pre-commit>=3.0",
            "tox>=4.0",
        ],
        "docs": [
            "sphinx>=6.0",
            "sphinx-rtd-theme>=1.3",
            "sphinx-autodoc-typehints>=1.23",
            "myst-parser>=2.0",
        ],
        "all": [
            "numba>=0.58",
            "qiskit>=0.34.0",
            "pennylane>=0.20.0",
            "cirq>=0.13.0",
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "sphinx>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "synapse=synapse_lang.cli:main",
            "synapse-repl=synapse_lang.repl:main",
            "synapse-bench=synapse_lang.benchmark:main",
        ],
    },
    package_data={
        "synapse_lang": [
            "*.syn",
            "examples/*.syn",
            "data/*.json",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    keywords=[
        "programming-language",
        "scientific-computing",
        "parallel-computing",
        "uncertainty-quantification",
        "quantum-computing",
        "tensor-operations",
        "symbolic-mathematics",
        "interpreter",
        "jit-compilation",
        "gpu-acceleration",
    ],
    zip_safe=False,
)