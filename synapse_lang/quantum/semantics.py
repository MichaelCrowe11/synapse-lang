"""Quantum semantic validation: gate registry, backend + noise configuration.

Error Codes Implemented:
    E1001 unknown gate name
    E1002 qubit index out of range
    E1003 duplicate qubit where distinct required
    E1004 gate arity mismatch
    E1005 gate parameter count mismatch
    E1010 measurement index out of range
    E1011 duplicate measurement of same qubit
    E1101 non-integer qubit/measurement index
    E1200 malformed noise model / noise object
    E1201 unknown / incomplete noise model spec
    E1202 noise model probability outside [0,1]
    E1301 invalid shots count in backend config
    E1302 invalid total circuit qubit count

NOTE: Keep this list in sync with `QUANTUM_SYNTAX.md` error code table.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

class QuantumSemanticError(ValueError):
    """Raised for static/semantic quantum errors (pre-execution)."""

@dataclass(frozen=True)
class GateSpec:
    name: str
    arity: int
    n_params: Union[int, Tuple[int, ...]]
    aliases: Tuple[str, ...] = ()
    distinct_qubits: bool = True

def _canon(name: str) -> str:
    return name.strip().lower()

def normalize_gate_name(name: str) -> str:
    n = _canon(name)
    for g in GATE_REGISTRY.values():
        if n == g.name or n in g.aliases:
            return g.name
    return n

_GATES: List[GateSpec] = [
    GateSpec("h", 1, 0),
    GateSpec("x", 1, 0),
    GateSpec("y", 1, 0),
    GateSpec("z", 1, 0),
    GateSpec("s", 1, 0),
    GateSpec("sdg", 1, 0),
    GateSpec("t", 1, 0),
    GateSpec("tdg", 1, 0),
    GateSpec("rx", 1, 1),
    GateSpec("ry", 1, 1),
    GateSpec("rz", 1, 1),
    GateSpec("u", 1, 3),
    GateSpec("cx", 2, 0, aliases=("cnot",)),
    GateSpec("cz", 2, 0),
    GateSpec("swap", 2, 0, distinct_qubits=True),
    GateSpec("iswap", 2, 0, distinct_qubits=True),
    GateSpec("ccx", 3, 0, aliases=("toffoli",)),
    GateSpec("cswap", 3, 0),
]

GATE_REGISTRY: Dict[str, GateSpec] = {g.name: g for g in _GATES}
for g in _GATES:
    for a in g.aliases:
        GATE_REGISTRY[a] = g

@dataclass(frozen=True)
class NoiseConfig:
    kind: str  # 'ideal' or 'depolarizing'
    p1q: Optional[float] = None
    p2q: Optional[float] = None
    readout: Optional[float] = None

@dataclass(frozen=True)
class BackendConfig:
    shots: int = 1
    seed: Optional[int] = None
    noise: NoiseConfig = NoiseConfig(kind="ideal")

def parse_noise_model(model: Union[str, dict]) -> NoiseConfig:
    if isinstance(model, str):
        kind = _canon(model)
        if kind != "ideal":
            raise QuantumSemanticError(f"E1201 unknown noise_model '{model}' (expected 'ideal' or depolarizing dict)")
        return NoiseConfig(kind="ideal")
    if isinstance(model, dict):
        kind = _canon(str(model.get("type", "depolarizing")))
        if kind != "depolarizing":
            raise QuantumSemanticError(f"E1201 unknown noise_model type '{kind}'")
        try:
            p1q = float(model["p1q"])
            p2q = float(model["p2q"])
            readout = float(model["readout"])
        except (KeyError, TypeError, ValueError):
            raise QuantumSemanticError("E1201 depolarizing requires numeric p1q, p2q, readout")
        for k, v in (("p1q", p1q), ("p2q", p2q), ("readout", readout)):
            if not (0.0 <= v <= 1.0):
                raise QuantumSemanticError(f"E1202 noise_model parameter {k}={v} out of [0,1]")
        return NoiseConfig(kind="depolarizing", p1q=p1q, p2q=p2q, readout=readout)
    raise QuantumSemanticError("E1200 noise_model must be 'ideal' or a dict")

def validate_backend_config(cfg: BackendConfig) -> None:
    if not isinstance(cfg.shots, int) or cfg.shots < 1:
        raise QuantumSemanticError(f"E1301 shots must be positive int, got {cfg.shots!r}")
    if not isinstance(cfg.noise, NoiseConfig):
        raise QuantumSemanticError("E1200 invalid noise config object")

def _ensure_int(i, label: str):
    if not isinstance(i, int):
        raise QuantumSemanticError(f"E1101 Non-integer qubit index for {label}: {i!r}")
    return i

def validate_gate_call(gate_name: str, qubits: Sequence[int], params: Sequence[float], n_qubits_total: int, span: Optional[Tuple[int,int]] = None) -> None:
    nname = normalize_gate_name(gate_name)
    spec = GATE_REGISTRY.get(nname)
    loc = "" if span is None else f" (line {span[0]}, col {span[1]})"
    if spec is None:
        raise QuantumSemanticError(f"E1001 Unknown gate '{gate_name}'{loc}")
    if len(qubits) != spec.arity:
        raise QuantumSemanticError(f"E1004 Gate '{spec.name}' expects {spec.arity} qubit(s), got {len(qubits)}{loc}")
    allowed = (spec.n_params,) if isinstance(spec.n_params, int) else spec.n_params
    if len(params) not in allowed:
        allowed_str = "|".join(map(str, allowed))
        raise QuantumSemanticError(f"E1005 Gate '{spec.name}' expects {allowed_str} param(s), got {len(params)}{loc}")
    qints = [_ensure_int(q, f"gate '{spec.name}'") for q in qubits]
    for q in qints:
        if q < 0 or q >= n_qubits_total:
            raise QuantumSemanticError(f"E1002 Qubit index {q} out of range for circuit size {n_qubits_total}{loc}")
    if spec.distinct_qubits and len(set(qints)) != len(qints):
        raise QuantumSemanticError(f"E1003 Gate '{spec.name}' requires distinct qubits{loc}")

def validate_circuit(*, n_qubits: int, ops: Iterable[Dict[str, object]], measurements: Optional[List[Sequence[int]]] = None, backend: Optional[BackendConfig] = None) -> None:
    if not isinstance(n_qubits, int) or n_qubits <= 0:
        raise QuantumSemanticError(f"E1302 circuit qubit count must be positive int, got {n_qubits!r}")
    for op in ops:
        g = str(op.get("gate"))
        qubits = list(op.get("qubits", []))  # type: ignore
        params = list(op.get("params", []))  # type: ignore
        span = op.get("span")
        span_t = tuple(span) if isinstance(span, (list, tuple)) and len(span)==2 else None
        validate_gate_call(g, qubits, params, n_qubits, span_t)
    if measurements:
        seen = set()
        for group in measurements:
            for q in group:
                _ensure_int(q, "measurement")
                if q < 0 or q >= n_qubits:
                    raise QuantumSemanticError(f"E1010 measurement index {q} out of range for {n_qubits}")
                if q in seen:
                    raise QuantumSemanticError(f"E1011 duplicate measurement for qubit {q}")
                seen.add(q)
    if backend is not None:
        validate_backend_config(backend)

__all__ = [
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
]