"""Packaged interpreter with run/noise layer."""
from typing import List, Dict, Any
from .synapse_parser import parse
from .synapse_ast import *  # includes RunNode alias

try:
    from .quantum import (
        QuantumCircuitBuilder,
        SimulatorBackend,
        QuantumGate,
        validate_circuit,
        BackendConfig,
        NoiseConfig,
        QuantumSemanticError,
    )
    QUANTUM_CORE_AVAILABLE = True
except Exception:  # fallback if quantum subpackage missing or partial
    QUANTUM_CORE_AVAILABLE = False


class SynapseInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self._active_backend_name = None
        self._current_backend_config: Dict[str, Any] = {}

    def execute(self, source: str):
        ast = parse(source)
        return self.interpret(ast)

    # --- dispatch ---
    def interpret(self, node: ASTNode):
        if isinstance(node, ProgramNode):
            out = []
            for stmt in node.body:
                r = self.interpret(stmt)
                if r is not None:
                    out.append(r)
            return out
        if isinstance(node, QuantumCircuitNode):
            return self._define_circuit(node)
        if isinstance(node, QuantumBackendNode):
            return self._define_backend(node)
        if isinstance(node, RunNode):
            return self._run(node)
        if isinstance(node, NumberNode):
            return node.value
        if isinstance(node, StringNode):
            return node.value
        if isinstance(node, IdentifierNode):
            return self.variables.get(node.name, node.name)
        if isinstance(node, BlockNode):
            return [self.interpret(s) for s in node.statements]
        if isinstance(node, QuantumAlgorithmNode):
            self.variables[f"algorithm_{node.name}"] = node
            return f"Algorithm {node.name} registered"
        return None

    # --- definitions ---
    def _define_circuit(self, node: QuantumCircuitNode):
        self.variables[f"circuit_{node.name}"] = node
        return f"Circuit {node.name}({node.qubits}) defined"

    def _define_backend(self, node: QuantumBackendNode):
        cfg = {k: self.interpret(v) for k, v in node.config.items()}
        self.variables[f"backend_{node.name}"] = cfg
        self._active_backend_name = node.name
        self._current_backend_config = cfg
        return f"Backend {node.name} active"

    # --- run ---
    def _run(self, node: RunNode):
        circ_key = f"circuit_{node.circuit_name}"
        circuit_node: QuantumCircuitNode = self.variables.get(circ_key)
        if circuit_node is None:
            return f"Error: circuit '{node.circuit_name}' not defined"
        backend_name = node.backend_name or self._active_backend_name
        backend_cfg = self.variables.get(f"backend_{backend_name}", {}) if backend_name else {}
        # extract options
        opt = {k: self.interpret(v) for k, v in node.options.items()}
        shots = int(opt.get("shots", backend_cfg.get("shots", 512)))
        noise = opt.get("noise_model", backend_cfg.get("noise_model"))
        # basic noise schema (string or dict{'model':name,'p':float})
        noise_cfg = None
        if noise:
            if isinstance(noise, str):
                noise_cfg = {"model": noise}
            elif isinstance(noise, dict):
                noise_cfg = noise
            else:
                return f"Error: unsupported noise model type {type(noise).__name__}"
            if noise_cfg.get("model") == "depolarizing":
                p = float(noise_cfg.get("p", noise_cfg.get("p1q", 0.0)))
                if not (0.0 <= p <= 1.0):
                    return "Error: depolarizing noise parameter p must be in [0,1]"
                noise_cfg["p"] = p
        if not QUANTUM_CORE_AVAILABLE:
            return {"circuit": node.circuit_name, "backend": backend_name, "shots": shots, "simulated": True, "noise": noise_cfg}
        try:
            builder = QuantumCircuitBuilder(circuit_node.qubits)
            ops_meta = []
            for g in circuit_node.gates:
                # build meta op record first for semantic validation
                name = g.gate_type
                qvals = []
                for x in g.qubits:
                    v = self.interpret(x)
                    qvals.append(int(v))
                params = [self.interpret(p) for p in g.parameters]
                ops_meta.append({"gate": name, "qubits": qvals, "params": params})
            meas_groups = []
            if circuit_node.measurements:
                for m in circuit_node.measurements:
                    grp = []
                    for q in m.qubits:
                        grp.append(int(self.interpret(q)))
                    meas_groups.append(grp)
            else:
                # auto-measure all qubits
                meas_groups = [list(range(circuit_node.qubits))]
            # semantic validation pass
            try:
                validate_circuit(
                    n_qubits=circuit_node.qubits,
                    ops=ops_meta,
                    measurements=meas_groups,
                    backend=BackendConfig(shots=shots, noise=NoiseConfig(kind=(noise_cfg or {}).get("model","ideal")))
                )
            except QuantumSemanticError as se:
                return f"Error: {se}"
            # If valid, apply to builder
            for meta in ops_meta:
                gname = meta["gate"].upper()
                qvals = meta["qubits"]
                params = meta["params"]
                err = self._apply_gate(builder, type("Tmp",(),{"gate_type":gname,"qubits":qvals,"parameters":params})(), circuit_node.qubits)
                if err:
                    return f"Error: {err}"
            # measurements
            builder.measure_all()
            backend = SimulatorBackend()
            counts = backend.execute(builder, shots=shots, noise=noise_cfg)
            return {"circuit": node.circuit_name, "backend": backend_name, "shots": shots, "counts": counts, "noise": noise_cfg}
        except Exception as e:
            return f"Run error: {e}"
    def _apply_gate(self, circuit, gate: QuantumGateNode, total_qubits: int):
        name = gate.gate_type.upper()
        qvals = []
        for x in gate.qubits:
            v = self.interpret(x)
            if not isinstance(v, (int, float)):
                return f"invalid qubit ref {v}"
            qi = int(v)
            if qi < 0 or qi >= total_qubits:
                return f"qubit {qi} out of range 0..{total_qubits-1}"
            qvals.append(qi)
        params = [self.interpret(p) for p in gate.parameters]
        try:
            if name == "H": circuit.h(qvals[0])
            elif name == "X": circuit.x(qvals[0])
            elif name == "Y": circuit.y(qvals[0])
            elif name == "Z": circuit.z(qvals[0])
            elif name in ("CNOT","CX"):
                if len(qvals)!=2: return "CNOT requires 2 qubits"
                circuit.cnot(qvals[0], qvals[1])
            elif name == "RX":
                if len(params)!=1: return "RX requires 1 parameter"
                circuit.rx(qvals[0], float(params[0]))
            elif name == "RY":
                if len(params)!=1: return "RY requires 1 parameter"
                circuit.ry(qvals[0], float(params[0]))
            elif name == "RZ":
                if len(params)!=1: return "RZ requires 1 parameter"
                circuit.rz(qvals[0], float(params[0]))
            else:
                return f"unsupported gate {name}"
        except Exception as e:
            return str(e)
        return None


def main():
    import sys
    code = sys.stdin.read()
    print(SynapseInterpreter().execute(code))


__all__ = [
    "SynapseInterpreter",
    "parse",
]
