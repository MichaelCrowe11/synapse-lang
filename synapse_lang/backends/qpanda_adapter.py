"""QPanda3 backend adapter for Synapse Lang.

Translates between Synapse's QuantumCircuitBuilder representation and
pyqpanda3's QProg / CPUQVM execution model.

Gate-level operations from QuantumCircuitBuilder are mapped through GATE_MAP
to their pyqpanda3 equivalents, composed into a QProg, measured, and executed
on a CPUQVM instance.

Algorithm wrappers (run_grover, run_qaoa, run_qae, run_qubo) provide
high-level access to pyqpanda_alg search and optimization algorithms,
returning unified SynapseQuantumResult objects.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Union

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
from synapse_lang.results import SynapseQuantumResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gate mapping: Synapse gate names (lowercase) -> pyqpanda3 gate constructors
# ---------------------------------------------------------------------------
# Single-qubit gates take (qubit_index) or (qubit_index, parameter).
# Multi-qubit gates take (qubit1, qubit2, ...).
# The mapping stores the raw callable; the _translate_circuit method handles
# dispatching with the correct arguments based on QuantumOperation metadata.

GATE_MAP: Dict[str, Any] = {
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
_SYNAPSE_GATE_TO_KEY: Dict[QuantumGate, str] = {
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

    _instance: Optional[QPandaBackend] = None

    def __init__(self, config: Dict[str, Any]) -> None:
        self.shots: int = config.get("shots", 1024)
        self._config = config
        logger.info("QPandaBackend initialised (shots=%d)", self.shots)

    @classmethod
    def get_or_create(cls, config: Dict[str, Any]) -> QPandaBackend:
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
        shots: Optional[int] = None,
        noise: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
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
    # Search & Optimization Algorithm Wrappers
    # ------------------------------------------------------------------

    def run_grover(
        self,
        n_qubits: int,
        marked_states: List[str],
        iterations: Optional[int] = None,
        shots: Optional[int] = None,
    ) -> SynapseQuantumResult:
        """Run Grover's search algorithm to find marked states.

        Uses pyqpanda_alg's Grover class with mark_data_reflection to
        build a phase-flip oracle from a list of marked bit-strings.

        Parameters
        ----------
        n_qubits:
            Number of qubits in the search space (search space = 2^n_qubits).
        marked_states:
            List of bit-string targets to search for, e.g. ``["101", "001"]``.
        iterations:
            Number of Grover iterations (amplitude amplification rounds).
            If ``None``, uses the optimal count from ``iter_num(n_qubits, len(marked_states))``.
        shots:
            Number of measurement shots for sampling.  Falls back to
            ``self.shots`` if not provided.  Pass 0 for probability-only.

        Returns
        -------
        SynapseQuantumResult
            With ``probabilities`` (always), ``counts`` (if shots > 0),
            and ``metadata`` containing algorithm details.
        """
        shots = shots if shots is not None else self.shots

        try:
            from pyqpanda_alg.Grover import Grover, mark_data_reflection, iter_num

            # Build the oracle from marked states
            oracle = self._build_grover_oracle(marked_states)

            # Determine iteration count
            if iterations is None:
                iterations = iter_num(n_qubits, len(marked_states))

            # Construct Grover search with the oracle
            grover = Grover(flip_operator=oracle)

            # Build circuit and run
            q_state = list(range(n_qubits))
            prog = QProg()
            prog << grover.cir(q_input=q_state, iternum=iterations)

            machine = CPUQVM()
            machine.run(prog, max(shots, 1))
            result = machine.result()
            prob_dict = result.get_prob_dict(q_state)

            probabilities = self._normalize_probabilities(prob_dict)
            counts = self._prob_to_counts(probabilities, shots) if shots > 0 else None

            return SynapseQuantumResult(
                counts=counts,
                probabilities=probabilities,
                metadata={
                    "algorithm": "grover",
                    "n_qubits": n_qubits,
                    "marked_states": marked_states,
                    "iterations": iterations,
                    "shots": shots,
                },
            )
        except Exception as exc:
            logger.error("Grover search failed: %s", exc)
            return SynapseQuantumResult(
                metadata={
                    "algorithm": "grover",
                    "n_qubits": n_qubits,
                    "marked_states": marked_states,
                    "iterations": iterations,
                    "error": str(exc),
                },
            )

    def run_qaoa(
        self,
        problem: Any,
        layers: int = 1,
        optimizer: str = "COBYLA",
        shots: int = -1,
        optimizer_option: Optional[Dict[str, Any]] = None,
    ) -> SynapseQuantumResult:
        """Run the Quantum Approximate Optimization Algorithm (QAOA).

        Finds approximate solutions to combinatorial optimization problems
        expressed as sympy polynomial expressions over binary variables.

        Parameters
        ----------
        problem:
            A sympy expression with binary variables (e.g. ``x0 + x1 - 2*x0*x1``)
            or a ``PauliOperator``.
        layers:
            Number of QAOA circuit layers (p-value).
        optimizer:
            Classical optimizer name (e.g. ``"COBYLA"``, ``"SLSQP"``, ``"SPSA"``).
        shots:
            Circuit measurement shots.  ``-1`` uses state-vector probabilities.
        optimizer_option:
            Extra options passed to the optimizer.

        Returns
        -------
        SynapseQuantumResult
            With ``probabilities``, ``value`` (best energy), and ``metadata``
            containing the full energy dictionary and problem dimension.
        """
        try:
            from pyqpanda_alg.QAOA.qaoa import QAOA

            qaoa = QAOA(problem)
            run_result = qaoa.run(
                layer=layers,
                shots=shots,
                optimizer=optimizer,
                optimizer_option=optimizer_option,
            )

            energy_dict = dict(qaoa.energy_dict) if qaoa.energy_dict else {}
            problem_dim = qaoa.problem_dimension

            # QAOA.run() returns a tuple: (prob_dict, optimized_params, loss)
            prob_dict = None
            if isinstance(run_result, tuple) and len(run_result) >= 1:
                prob_dict = run_result[0]
            elif isinstance(run_result, dict):
                prob_dict = run_result

            if isinstance(prob_dict, dict):
                probabilities = self._normalize_probabilities(prob_dict)
            else:
                probabilities = None

            # Find the best (minimum) energy value
            best_value = None
            if energy_dict:
                best_value = min(energy_dict.values())

            return SynapseQuantumResult(
                probabilities=probabilities,
                value=best_value,
                metadata={
                    "algorithm": "qaoa",
                    "layers": layers,
                    "optimizer": optimizer,
                    "problem_dimension": problem_dim,
                    "energy_dict": energy_dict,
                },
            )
        except Exception as exc:
            logger.error("QAOA failed: %s", exc)
            return SynapseQuantumResult(
                metadata={
                    "algorithm": "qaoa",
                    "layers": layers,
                    "optimizer": optimizer,
                    "error": str(exc),
                },
            )

    def run_qae(
        self,
        operator: Callable,
        n_qubits: int,
        res_index: Union[int, List[int]] = -1,
        target_state: str = "1",
        epsilon: float = 0.001,
    ) -> SynapseQuantumResult:
        """Run Quantum Amplitude Estimation (QAE).

        Estimates the amplitude (probability) of a target state produced
        by a given quantum operator/circuit.

        Parameters
        ----------
        operator:
            A callable ``f(qubits) -> QCircuit`` that prepares the state
            whose amplitude is to be estimated.
        n_qubits:
            Number of qubits used by the operator.
        res_index:
            Index (or list of indices) of the qubit(s) to estimate.
        target_state:
            The bit-string target state to estimate probability for.
        epsilon:
            Estimation precision (minimum error bound).

        Returns
        -------
        SynapseQuantumResult
            With ``value`` containing the estimated amplitude (probability)
            and ``metadata`` with algorithm parameters.
        """
        try:
            from pyqpanda_alg.QAE.QAE import QAE

            estimator = QAE(
                operator_in=operator,
                qnumber=n_qubits,
                res_index=res_index,
                epsilon=epsilon,
                target_state=target_state,
            )
            estimated_value = estimator.run()

            return SynapseQuantumResult(
                value=float(estimated_value),
                metadata={
                    "algorithm": "qae",
                    "n_qubits": n_qubits,
                    "res_index": res_index,
                    "target_state": target_state,
                    "epsilon": epsilon,
                },
            )
        except Exception as exc:
            logger.error("QAE failed: %s", exc)
            return SynapseQuantumResult(
                metadata={
                    "algorithm": "qae",
                    "n_qubits": n_qubits,
                    "epsilon": epsilon,
                    "error": str(exc),
                },
            )

    def run_qubo(
        self,
        problem: Any,
        layers: Optional[int] = None,
        optimizer: str = "SLSQP",
        optimizer_option: Optional[Dict[str, Any]] = None,
    ) -> SynapseQuantumResult:
        """Run QUBO (Quadratic Unconstrained Binary Optimization) via QAOA.

        Solves QUBO problems using pyqpanda_alg's QUBO_QAOA solver.
        The problem can be specified as a sympy expression or a dict with
        ``quadratic``, ``linear``, and ``constant`` keys.

        Parameters
        ----------
        problem:
            A sympy expression with binary variables, or a dict with keys:
            ``"quadratic"`` (matrix A), ``"linear"`` (vector b),
            ``"constant"`` (scalar c) defining Q(x) = x^T A x + b^T x + c.
        layers:
            Number of QAOA layers.
        optimizer:
            Classical optimizer (default ``"SLSQP"``).
        optimizer_option:
            Extra options for the optimizer.

        Returns
        -------
        SynapseQuantumResult
            With ``probabilities``, ``value`` (best objective), and ``metadata``.
        """
        try:
            from pyqpanda_alg.QUBO import QUBO_QAOA

            qubo_solver = QUBO_QAOA(problem)
            result_probs = qubo_solver.run(
                layer=layers,
                optimizer=optimizer,
                optimizer_option=optimizer_option,
            )

            if isinstance(result_probs, dict):
                probabilities = self._normalize_probabilities(result_probs)
            else:
                probabilities = None

            # Determine best solution and its objective value
            best_value = None
            best_solution = None
            if probabilities:
                best_solution = max(probabilities, key=probabilities.get)
                # Evaluate objective at best solution using the solver
                try:
                    best_bits = [int(b) for b in best_solution]
                    best_value = float(qubo_solver.calculate_energy(best_bits))
                except Exception:
                    # Fall back: no value if evaluation fails
                    pass

            return SynapseQuantumResult(
                probabilities=probabilities,
                value=best_value,
                metadata={
                    "algorithm": "qubo",
                    "layers": layers,
                    "optimizer": optimizer,
                    "best_solution": best_solution,
                },
            )
        except Exception as exc:
            logger.error("QUBO failed: %s", exc)
            return SynapseQuantumResult(
                metadata={
                    "algorithm": "qubo",
                    "layers": layers,
                    "optimizer": optimizer,
                    "error": str(exc),
                },
            )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _build_grover_oracle(
        self, marked_states: List[str]
    ) -> Callable:
        """Build a Grover oracle (phase-flip operator) for the given marked states.

        Returns a callable ``f(qubits) -> QCircuit`` that applies a phase
        flip to the specified computational basis states using
        ``mark_data_reflection``.

        Parameters
        ----------
        marked_states:
            List of bit-string targets, e.g. ``["101", "001"]``.

        Returns
        -------
        Callable
            A function ``f(qubits) -> QCircuit`` suitable for the
            ``flip_operator`` parameter of pyqpanda_alg's Grover class.
        """
        from pyqpanda_alg.Grover import mark_data_reflection

        def oracle(qubits):
            return mark_data_reflection(qubits=qubits, mark_data=marked_states)

        return oracle

    def _normalize_probabilities(
        self, prob_dict: Dict[str, float]
    ) -> Dict[str, float]:
        """Normalize a probability dictionary so values sum to 1.0.

        Handles edge cases where raw output may not be perfectly normalized.
        Zero-probability entries are preserved (unlike ``_prob_to_counts``).

        Parameters
        ----------
        prob_dict:
            Raw probability dictionary from a quantum execution.

        Returns
        -------
        Dict[str, float]
            Normalized probabilities summing to 1.0.
        """
        total = sum(prob_dict.values())
        if total == 0 or abs(total - 1.0) < 1e-12:
            return dict(prob_dict)
        return {state: prob / total for state, prob in prob_dict.items()}

    def _prob_to_counts(self, prob_dict: Dict[str, float], shots: int) -> Dict[str, int]:
        """Convert a probability distribution to shot counts.

        Useful when working with probability-based results rather than
        shot-sampled counts.
        """
        counts: Dict[str, int] = {}
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
