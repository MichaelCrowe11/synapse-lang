"""
Setup configuration for Quantum-Net Language
Part of the Quantum Trinity alongside Synapse and Qubit-Flow
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Quantum-Net - A distributed quantum computing and networking language"

setup(
    name="synapse-quantum-net",
    version="1.0.0",
    author="Michael Benjamin Crowe",
    author_email="michaelcrowe11@users.noreply.github.com",
    description="Distributed quantum computing and networking language - part of the Quantum Trinity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichaelCrowe11/synapse-lang",
    packages=find_packages(include=[
        "qnet_lang",
        "qnet_lang.*",
        "qnet_runtime",
        "qnet_runtime.*",
        "qnet_bridge",
        "qnet_bridge.*"
    ]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research", 
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Networking",
        "Topic :: System :: Distributed Computing",
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
        "networkx>=2.6.0",
        "matplotlib>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "ruff>=0.5.0",
        ],
        "quantum": [
            "qiskit>=0.34.0",
            "pennylane>=0.20.0",
            "cirq>=0.13.0",
        ],
        "visualization": [
            "plotly>=5.0.0",
            "dash>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "synapse-qnet=qnet_lang.cli:main",
            "synapse-quantum-net=qnet_lang.repl:main",
        ],
    },
    include_package_data=True,
    package_data={
        "qnet_lang": ["*.qnet", "examples/*.qnet"],
    },
    zip_safe=False,
)