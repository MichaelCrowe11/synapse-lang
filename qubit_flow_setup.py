"""
Setup configuration for Qubit-Flow Language
Part of the Quantum Trinity alongside Synapse and Quantum-Net
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "QUBIT_FLOW_README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Qubit-Flow - A quantum circuit design and execution language"

setup(
    name="qubit-flow",
    version="1.0.0",
    author="Michael Benjamin Crowe",
    author_email="michaelcrowe11@users.noreply.github.com",
    description="Quantum circuit design and algorithm execution language - part of the Quantum Trinity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichaelCrowe11/synapse-lang",
    packages=find_packages(include=[
        "qubit_flow_lang",
        "qubit_flow_lang.*"
    ]),
    py_modules=[
        "qubit_flow_ast",
        "qubit_flow_interpreter", 
        "qubit_flow_lexer",
        "qubit_flow_parser"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research", 
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
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
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "qiskit>=0.34.0",
        "pennylane>=0.20.0",
        "cirq>=0.13.0",
        "matplotlib>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "ruff>=0.5.0",
        ],
        "hardware": [
            "qiskit-ibm-provider>=0.6.0",
            "qiskit-aer>=0.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qflow=qubit_flow_lang.cli:main",
            "qubit-flow=qubit_flow_lang.repl:main",
        ],
    },
    include_package_data=True,
    package_data={
        "qubit_flow_lang": ["*.qflow", "examples/*.qflow"],
    },
    zip_safe=False,
)