"""Deprecated shim: original quantum core moved to `synapse_lang.quantum.core`.

Import from `synapse_lang.quantum` instead. This file will be removed in a future release.
"""
from .synapse_lang.quantum import (  # type: ignore
    QuantumAlgorithms,
    QuantumCircuitBuilder,
    QuantumGate,
    SimulatorBackend,
)

__all__ = [
    "QuantumCircuitBuilder",
    "SimulatorBackend",
    "QuantumGate",
    "QuantumAlgorithms",
]
