# Quantum Drug Discovery Platform
# A comprehensive application framework using the Quantum Trinity

"""
Quantum Drug Discovery Platform (QDD)
=====================================

A production-ready platform for drug discovery using quantum computing.
Integrates all three quantum languages:
- Synapse-Lang: Molecular uncertainty modeling
- Qubit-Flow: VQE and quantum chemistry circuits
- Quantum-Net: Distributed computation across quantum nodes

Key Features:
- Molecular structure optimization
- Protein-drug interaction simulation
- Lead compound screening
- Pharmacokinetic property prediction
- Distributed quantum simulation
"""

__version__ = "1.0.0"
__author__ = "Quantum Trinity Team"

from .distributed_compute import DistributedQuantumCompute
from .drug_screener import DrugScreener
from .molecular_simulator import MolecularSimulator
from .protein_folder import ProteinFolder
from .vqe_optimizer import VQEOptimizer

__all__ = [
    "MolecularSimulator",
    "DrugScreener",
    "ProteinFolder",
    "VQEOptimizer",
    "DistributedQuantumCompute"
]
