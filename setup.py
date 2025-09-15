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
    version="2.2.0",
    author="Michael Benjamin Crowe",
    author_email="michaelcrowe11@users.noreply.github.com",
    description="Enterprise quantum computing platform with cloud-native architecture, distributed execution, and comprehensive quantum algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichaelCrowe11/synapse-lang",
    packages=find_packages(include=[
        "synapse_lang",
        "synapse_lang.*",
        "qubit_flow_lang",
        "quantum_net_lang"
    ]),
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
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
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
            "ruff>=0.5.0",
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
        "quantum": [
            "qiskit>=0.44.0",
            "cirq>=1.2.0",
            "pennylane>=0.32.0",
        ],
        "cloud": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "aioredis>=2.0.1",
            "asyncpg>=0.29.0",
            "docker>=6.1.0",
            "kubernetes>=27.2.0",
        ],
        "enterprise": [
            "stripe>=7.0.0",
            "boto3>=1.29.0",
            "motor>=3.3.0",
            "prometheus-client>=0.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "synapse=synapse_lang.cli:main",
            "synapse-repl=synapse_lang.repl:main",
            "synapse-quantum=synapse_lang.quantum.runner:main",
            "qflow=qubit_flow_lang:placeholder",
            "qnet=quantum_net_lang:placeholder",
        ],
    },
    include_package_data=True,
    package_data={
        "synapse_lang": ["*.syn", "examples/*.syn"],
    },
    zip_safe=False,
)