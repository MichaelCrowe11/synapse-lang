"""Quantum namespace.

Exports:
Semantic layer (always available):
 - QuantumSemanticError
 - validate_circuit / validate_gate_call
 - BackendConfig / NoiseConfig

Execution layer (current in-core reference simulator):
 - QuantumCircuitBuilder
 - SimulatorBackend
 - QuantumGate / QuantumAlgorithms
"""
from .semantics import (
    QuantumSemanticError,
    GateSpec,
    GATE_REGISTRY,
    normalize_gate_name,
    validate_gate_call,
    validate_circuit,
    NoiseConfig,
    BackendConfig,
    parse_noise_model,
    validate_backend_config,
)
from .core import QuantumCircuitBuilder, SimulatorBackend, QuantumGate
from .algorithms import QuantumAlgorithms

__all__ = [
    # semantics
    "QuantumSemanticError",
    "GateSpec",
    "GATE_REGISTRY",
    "normalize_gate_name",
    "validate_gate_call",
    "validate_circuit",
    "NoiseConfig",
    "BackendConfig",
    "parse_noise_model",
    "validate_backend_config",
    # execution
    "QuantumCircuitBuilder",
    "SimulatorBackend",
    "QuantumGate",
    "QuantumAlgorithms",
]
