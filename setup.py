"""
Setup configuration for Synapse Language
Created by Michael Benjamin Crowe
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Synapse - A language for deep scientific reasoning and parallel thought processing"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "numba>=0.54.0",
        "matplotlib>=3.4.0",
        "colorama>=0.4.4"
    ]

setup(
    name="synapse-lang",
    version="0.2.0",
    author="Michael Benjamin Crowe",
    author_email="",
    description="A language for deep scientific reasoning and parallel thought processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichaelCrowe11/synapse-lang",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    py_modules=[
        "synapse_interpreter",
        "synapse_parser",
        "synapse_ast",
        "synapse_repl",
        "synapse_scientific",
        "synapse_jit",
        "synapse"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pre-commit>=2.19.0",
        ],
        "docs": [
            "sphinx>=4.5.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "jupyter": [
            "jupyterlab>=3.4.0",
            "ipykernel>=6.15.0",
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
        "": ["*.syn", "*.md", "examples/*.syn", "vscode-extension/*"],
    },
    project_urls={
        "Bug Reports": "https://github.com/MichaelCrowe11/synapse-lang/issues",
        "Source": "https://github.com/MichaelCrowe11/synapse-lang",
        "Documentation": "https://github.com/MichaelCrowe11/synapse-lang/blob/master/LANGUAGE_SPEC.md",
    },
    keywords=[
        "scientific-computing",
        "parallel-processing",
        "uncertainty-quantification",
        "programming-language",
        "interpreter",
        "scientific-reasoning",
        "quantum-computing",
        "climate-modeling",
        "drug-discovery",
    ],
)