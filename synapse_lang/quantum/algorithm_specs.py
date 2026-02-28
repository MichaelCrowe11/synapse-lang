"""Parameter specifications for all QPanda3-backed quantum algorithms."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AlgorithmSpec:
    """Defines required/optional parameters and constraints for one algorithm."""

    name: str
    required: set[str]
    optional: dict[str, object]  # param_name -> default_value
    min_qubits: int
    result_fields: list[str]  # which SynapseQuantumResult fields this populates


ALGORITHM_SPECS: dict[str, AlgorithmSpec] = {
    "grover_search": AlgorithmSpec(
        name="grover_search",
        required=set(),  # oracle OR marked — validated separately
        optional={"oracle": None, "marked": None, "iterations": "auto"},
        min_qubits=2,
        result_fields=["counts", "probabilities", "value"],
    ),
    "qaoa_solve": AlgorithmSpec(
        name="qaoa_solve",
        required={"problem"},
        optional={"layers": 1, "optimizer": "spsa"},
        min_qubits=2,
        result_fields=["value", "counts"],
    ),
    "qae": AlgorithmSpec(
        name="qae",
        required={"oracle"},
        optional={"precision": 5, "method": "iterative"},
        min_qubits=2,
        result_fields=["value"],
    ),
    "qarm": AlgorithmSpec(
        name="qarm",
        required={"data"},
        optional={"min_support": 0.3, "min_confidence": 0.7},
        min_qubits=2,
        result_fields=["data"],
    ),
    "qcmp": AlgorithmSpec(
        name="qcmp",
        required={"value"},
        optional={"function": "geq", "method": "standard"},
        min_qubits=2,
        result_fields=["counts", "probabilities"],
    ),
    "qkmeans": AlgorithmSpec(
        name="qkmeans",
        required={"data"},
        optional={"clusters": 2},
        min_qubits=2,
        result_fields=["classification"],
    ),
    "qpca": AlgorithmSpec(
        name="qpca",
        required={"data"},
        optional={"components": 2},
        min_qubits=2,
        result_fields=["data"],
    ),
    "qsencode": AlgorithmSpec(
        name="qsencode",
        required={"data"},
        optional={"encoding": "amplitude"},
        min_qubits=1,
        result_fields=["probabilities"],
    ),
    "qsvd": AlgorithmSpec(
        name="qsvd",
        required={"matrix"},
        optional={"rank": None},
        min_qubits=2,
        result_fields=["data"],
    ),
    "qsvm": AlgorithmSpec(
        name="qsvm",
        required={"train_data", "train_labels"},
        optional={"test_data": None, "kernel": "quantum"},
        min_qubits=2,
        result_fields=["classification"],
    ),
    "qsvr": AlgorithmSpec(
        name="qsvr",
        required={"train_data", "train_labels"},
        optional={"test_data": None, "kernel": "quantum"},
        min_qubits=2,
        result_fields=["classification", "value"],
    ),
    "qubo": AlgorithmSpec(
        name="qubo",
        required={"problem"},
        optional={"method": "qaoa"},
        min_qubits=2,
        result_fields=["value", "counts"],
    ),
    "qmrmr": AlgorithmSpec(
        name="qmrmr",
        required={"data", "labels"},
        optional={"features": 3},
        min_qubits=2,
        result_fields=["data"],
    ),
}
