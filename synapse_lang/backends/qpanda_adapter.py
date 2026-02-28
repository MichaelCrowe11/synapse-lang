"""QPanda3 backend adapter for Synapse Lang.

Translates between Synapse's QuantumCircuitBuilder representation and
pyqpanda3's QProg / CPUQVM execution model.

Gate-level operations from QuantumCircuitBuilder are mapped through GATE_MAP
to their pyqpanda3 equivalents, composed into a QProg, measured, and executed
on a CPUQVM instance.
"""
from __future__ import annotations

import logging
from typing import Any

from pyqpanda3.core import (
    CNOT,
    CPUQVM,
    CZ,
    H,
    I,
    QProg,
    RX,
    RY,
    RZ,
    S,
    SWAP,
    T,
    TOFFOLI,
    X,
    Y,
    Z,
    measure,
)

from synapse_lang.quantum.core import QuantumCircuitBuilder, QuantumGate

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gate mapping: Synapse gate names (lowercase) -> pyqpanda3 gate constructors
# ---------------------------------------------------------------------------
# Single-qubit gates take (qubit_index) or (qubit_index, parameter).
# Multi-qubit gates take (qubit1, qubit2, ...).
# The mapping stores the raw callable; the _translate_circuit method handles
# dispatching with the correct arguments based on QuantumOperation metadata.

GATE_MAP: dict[str, Any] = {
    # Single-qubit (no parameters)
    "i": I,
    "h": H,
    "x": X,
    "y": Y,
    "z": Z,
    "s": S,
    "t": T,
    # Single-qubit rotations (1 float parameter)
    "rx": RX,
    "ry": RY,
    "rz": RZ,
    # Two-qubit gates
    "cx": CNOT,
    "cnot": CNOT,
    "cz": CZ,
    "swap": SWAP,
    # Three-qubit gates
    "ccx": TOFFOLI,
    "toffoli": TOFFOLI,
}

# Gates that require rotation parameters
_ROTATION_GATES = {"rx", "ry", "rz"}

# Synapse QuantumGate enum -> lowercase lookup key in GATE_MAP
_SYNAPSE_GATE_TO_KEY: dict[QuantumGate, str] = {
    QuantumGate.I: "i",
    QuantumGate.X: "x",
    QuantumGate.Y: "y",
    QuantumGate.Z: "z",
    QuantumGate.H: "h",
    QuantumGate.S: "s",
    QuantumGate.T: "t",
    QuantumGate.RX: "rx",
    QuantumGate.RY: "ry",
    QuantumGate.RZ: "rz",
    QuantumGate.CNOT: "cnot",
    QuantumGate.CZ: "cz",
    QuantumGate.SWAP: "swap",
    QuantumGate.TOFFOLI: "toffoli",
}


class QPandaBackend:
    """Singleton backend that executes Synapse circuits on pyqpanda3 CPUQVM.

    Usage::

        backend = QPandaBackend.get_or_create({"shots": 1024})
        counts = backend.execute(circuit)
        backend.shutdown()
    """

    _instance: QPandaBackend | None = None

    def __init__(self, config: dict[str, Any]) -> None:
        self.shots: int = config.get("shots", 1024)
        self._config = config
        logger.info("QPandaBackend initialised (shots=%d)", self.shots)

    @classmethod
    def get_or_create(cls, config: dict[str, Any]) -> QPandaBackend:
        """Return the singleton instance, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(
        self,
        synapse_circuit: QuantumCircuitBuilder,
        shots: int | None = None,
        noise: dict[str, Any] | None = None,
    ) -> dict[str, int]:
        """Execute a gate-level Synapse circuit on QPanda3's CPUQVM.

        Parameters
        ----------
        synapse_circuit:
            A populated ``QuantumCircuitBuilder`` with operations and
            measurements already added.
        shots:
            Number of measurement shots.  Falls back to ``self.shots``
            if not provided.
        noise:
            Reserved for future noise-model support (currently unused).

        Returns
        -------
        dict[str, int]
            Measurement outcome counts, e.g. ``{"00": 512, "11": 512}``.
        """
        shots = shots if shots is not None else self.shots
        prog = self._translate_circuit(synapse_circuit)

        machine = CPUQVM()
        machine.run(prog, shots)
        result = machine.result()
        counts: dict[str, int] = result.get_counts()

        logger.debug("QPanda execution complete: %d unique outcomes", len(counts))
        return counts

    # ------------------------------------------------------------------
    # Translation
    # ------------------------------------------------------------------

    def _translate_circuit(self, synapse_circuit: QuantumCircuitBuilder) -> QProg:
        """Convert Synapse QuantumCircuitBuilder operations to a QPanda3 QProg.

        Each ``QuantumOperation`` in the builder is mapped through
        ``GATE_MAP`` using the qubit indices and optional rotation
        parameters.  Measurements are appended at the end for every
        qubit that has a measurement registered in the builder.
        """
        prog = QProg()

        # Apply gates
        for op in synapse_circuit.operations:
            key = _SYNAPSE_GATE_TO_KEY.get(op.gate)
            if key is None:
                logger.warning(
                    "Unsupported gate %s — skipping", op.gate.value
                )
                continue

            gate_fn = GATE_MAP[key]

            if key in _ROTATION_GATES:
                # Rotation gates: fn(qubit, angle)
                prog << gate_fn(op.qubits[0], op.parameters[0])
            elif len(op.qubits) == 1:
                # Single-qubit gate: fn(qubit)
                prog << gate_fn(op.qubits[0])
            elif len(op.qubits) == 2:
                # Two-qubit gate: fn(q0, q1)
                prog << gate_fn(op.qubits[0], op.qubits[1])
            elif len(op.qubits) == 3:
                # Three-qubit gate: fn(q0, q1, q2)
                prog << gate_fn(op.qubits[0], op.qubits[1], op.qubits[2])
            else:
                raise ValueError(
                    f"Gate '{key}' has unsupported qubit count: {len(op.qubits)}"
                )

        # Append measurements
        if synapse_circuit.measurements:
            qubit_indices = sorted(synapse_circuit.measurements.keys())
            cbit_indices = [synapse_circuit.measurements[q] for q in qubit_indices]
            prog << measure(qubit_indices, cbit_indices)
        else:
            # If no explicit measurements, measure all qubits
            all_qubits = list(range(synapse_circuit.num_qubits))
            prog << measure(all_qubits, all_qubits)

        return prog

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _prob_to_counts(self, prob_dict: dict[str, float], shots: int) -> dict[str, int]:
        """Convert a probability distribution to shot counts.

        Useful when working with probability-based results rather than
        shot-sampled counts.
        """
        counts: dict[str, int] = {}
        for state, prob in prob_dict.items():
            count = int(round(prob * shots))
            if count > 0:
                counts[state] = count
        return counts

    def shutdown(self) -> None:
        """Release resources and clear the singleton."""
        QPandaBackend._instance = None
        logger.info("QPandaBackend shut down")

    def __repr__(self) -> str:
        return f"QPandaBackend(shots={self.shots})"
