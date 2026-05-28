"""Packaged interpreter with expression evaluation and quantum run support."""
from __future__ import annotations

import math
from typing import Any

from .parser_enhanced import EnhancedParser
from .synapse_ast import *  # includes RunNode alias
from .synapse_lexer import Lexer

try:
    from .quantum import (
        BackendConfig,
        NoiseConfig,
        QuantumCircuitBuilder,
        QuantumSemanticError,
        SimulatorBackend,
        validate_circuit,
    )
    QUANTUM_CORE_AVAILABLE = True
except Exception:  # fallback if quantum subpackage missing or partial
    QUANTUM_CORE_AVAILABLE = False

_BOOL_LITERALS = {"true": True, "false": False}


class SynapseInterpreter:
    def __init__(self):
        from .builtins import default_builtins

        self.variables: dict[str, Any] = default_builtins()
        self._active_backend_name = None
        self._current_backend_config: dict[str, Any] = {}

    def execute(self, source: str, context: dict[str, Any] | None = None) -> Any:
        if context:
            self.variables.update(context)
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        ast = EnhancedParser(tokens).parse()
        return self.interpret(ast)

    def _program_statements(self, node: ProgramNode) -> list[ASTNode]:
        return getattr(node, "body", None) or getattr(node, "statements", [])

    def _assignment_target(self, node: AssignmentNode) -> str:
        target = node.target
        if isinstance(target, IdentifierNode):
            return target.name
        if isinstance(target, str):
            return target
        return getattr(target, "name", str(target))

    def interpret(self, node: ASTNode) -> Any:
        if node is None:
            return None
        if isinstance(node, ProgramNode):
            result = None
            for stmt in self._program_statements(node):
                result = self.interpret(stmt)
            return result
        if isinstance(node, AssignmentNode):
            value = self.interpret(node.value)
            name = self._assignment_target(node)
            self.variables[name] = value
            return value
        if isinstance(node, BinaryOpNode):
            return self._eval_binary(node)
        if isinstance(node, UnaryOpNode):
            return self._eval_unary(node)
        if isinstance(node, FunctionCallNode):
            return self._eval_call(node)
        if isinstance(node, ListNode):
            return [self.interpret(e) for e in node.elements]
        if isinstance(node, UncertainNode):
            try:
                from .uncertainty import UncertainValue

                return UncertainValue(node.value, node.uncertainty)
            except ImportError:
                return (node.value, node.uncertainty)
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
            name = node.name.lower()
            if name in _BOOL_LITERALS:
                return _BOOL_LITERALS[name]
            if node.name not in self.variables:
                raise NameError(f"Variable '{node.name}' is not defined")
            return self.variables[node.name]
        if isinstance(node, BlockNode):
            results = []
            for stmt in node.statements:
                r = self.interpret(stmt)
                if r is not None:
                    results.append(r)
            return results[-1] if results else None
        if isinstance(node, ParallelNode):
            return self._run_parallel(node)
        if isinstance(node, BranchNode):
            body = node.body
            if isinstance(body, list):
                result = None
                for stmt in body:
                    result = self.interpret(stmt)
                return result
            return self.interpret(body)
        if isinstance(node, QuantumAlgorithmNode):
            self.variables[f"algorithm_{node.name}"] = node
            return f"Algorithm {node.name} registered"
        return None

    def _eval_binary(self, node: BinaryOpNode) -> Any:
        op = node.operator
        if op == "?:":
            cond = self.interpret(node.left)
            branches = node.right if isinstance(node.right, list) else [node.right]
            return self.interpret(branches[0] if cond else branches[1])

        left = self.interpret(node.left)
        right = self.interpret(node.right)

        try:
            from .uncertainty import UncertainValue
        except ImportError:
            UncertainValue = None  # type: ignore[misc, assignment]

        if UncertainValue and isinstance(left, UncertainValue) and isinstance(right, UncertainValue):
            if op in ("+", "PLUS"):
                return UncertainValue(
                    left.value + right.value,
                    math.sqrt(left.uncertainty ** 2 + right.uncertainty ** 2),
                )
            if op in ("*", "MULTIPLY"):
                rel = math.sqrt((left.uncertainty / left.value) ** 2 + (right.uncertainty / right.value) ** 2)
                product = left.value * right.value
                return UncertainValue(product, abs(product) * rel)
            if op in ("**", "POWER"):
                val = left.value ** right.value
                rel = abs(right.value) * (left.uncertainty / left.value) if left.value else 0.0
                return UncertainValue(val, abs(val) * rel)

        if op in ("+", "PLUS"):
            return left + right
        if op in ("-", "MINUS"):
            return left - right
        if op in ("*", "MULTIPLY"):
            return left * right
        if op in ("/", "DIVIDE"):
            return left / right
        if op in ("**", "POWER"):
            return left ** right
        if op in ("%", "MODULO"):
            return left % right
        if op in ("<", "LESS_THAN"):
            if UncertainValue and isinstance(left, UncertainValue) and isinstance(right, UncertainValue):
                return left.value < right.value
            return left < right
        if op in (">", "GREATER_THAN"):
            return left > right
        if op in ("<=", "LESS_EQUAL"):
            return left <= right
        if op in (">=", "GREATER_EQUAL"):
            return left >= right
        if op in ("==", "EQUALS"):
            return left == right
        if op in ("!=", "NOT_EQUALS"):
            return left != right
        if op in ("&&", "AND"):
            return bool(left) and bool(right)
        if op in ("||", "OR"):
            return bool(left) or bool(right)
        raise ValueError(f"Unknown operator: {op}")

    def _eval_unary(self, node: UnaryOpNode) -> Any:
        operand = self.interpret(node.operand)
        op = node.operator
        if op in ("-", "MINUS"):
            return -operand
        if op in ("!", "NOT"):
            return not operand
        if op in ("+", "PLUS"):
            return +operand
        raise ValueError(f"Unknown unary operator: {op}")

    def _eval_call(self, node: FunctionCallNode) -> Any:
        if isinstance(node.function, IdentifierNode):
            name = node.function.name
        elif isinstance(node.function, str):
            name = node.function
        else:
            name = str(node.function)
        func = self.variables.get(name)
        if func is None or not callable(func):
            raise NameError(f"Function '{name}' is not defined")
        args = [self.interpret(a) for a in node.arguments]
        return func(*args)

    def _run_parallel(self, node: ParallelNode) -> Any:
        """Execute parallel branches sequentially (shared interpreter state)."""
        result = None
        for branch in node.branches:
            result = self.interpret(branch)
        return result

    def _define_circuit(self, node: QuantumCircuitNode):
        self.variables[f"circuit_{node.name}"] = node
        return f"Circuit {node.name}({node.qubits}) defined"

    def _define_backend(self, node: QuantumBackendNode):
        cfg = {k: self.interpret(v) for k, v in node.config.items()}
        self.variables[f"backend_{node.name}"] = cfg
        self._active_backend_name = node.name
        self._current_backend_config = cfg
        return f"Backend {node.name} active"

    def _run(self, node: RunNode):
        circ_key = f"circuit_{node.circuit_name}"
        circuit_node: QuantumCircuitNode = self.variables.get(circ_key)
        if circuit_node is None:
            return f"Error: circuit '{node.circuit_name}' not defined"
        backend_name = node.backend_name or self._active_backend_name
        backend_cfg = self.variables.get(f"backend_{backend_name}", {}) if backend_name else {}
        opt = {k: self.interpret(v) for k, v in node.options.items()}
        shots = int(opt.get("shots", backend_cfg.get("shots", 512)))
        noise = opt.get("noise_model", backend_cfg.get("noise_model"))
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
            return {
                "circuit": node.circuit_name,
                "backend": backend_name,
                "shots": shots,
                "simulated": True,
                "noise": noise_cfg,
            }
        try:
            builder = QuantumCircuitBuilder(circuit_node.qubits)
            ops_meta = []
            for g in circuit_node.gates:
                name = g.gate_type
                qvals = [int(self.interpret(x)) for x in g.qubits]
                params = [self.interpret(p) for p in g.parameters]
                ops_meta.append({"gate": name, "qubits": qvals, "params": params})
            meas_groups = []
            if circuit_node.measurements:
                for m in circuit_node.measurements:
                    meas_groups.append([int(self.interpret(q)) for q in m.qubits])
            else:
                meas_groups = [list(range(circuit_node.qubits))]
            try:
                validate_circuit(
                    n_qubits=circuit_node.qubits,
                    ops=ops_meta,
                    measurements=meas_groups,
                    backend=BackendConfig(
                        shots=shots,
                        noise=NoiseConfig(kind=(noise_cfg or {}).get("model", "ideal")),
                    ),
                )
            except QuantumSemanticError as se:
                return f"Error: {se}"
            for meta in ops_meta:
                gname = meta["gate"].upper()
                err = self._apply_gate(
                    builder,
                    type(
                        "Tmp",
                        (),
                        {
                            "gate_type": gname,
                            "qubits": meta["qubits"],
                            "parameters": meta["params"],
                        },
                    )(),
                    circuit_node.qubits,
                )
                if err:
                    return f"Error: {err}"
            builder.measure_all()
            backend = SimulatorBackend()
            counts = backend.execute(builder, shots=shots, noise=noise_cfg)
            return {
                "circuit": node.circuit_name,
                "backend": backend_name,
                "shots": shots,
                "counts": counts,
                "noise": noise_cfg,
            }
        except Exception as e:
            return f"Run error: {e}"

    def _apply_gate(self, circuit, gate, total_qubits: int):
        name = gate.gate_type.upper()
        qvals = []
        for x in gate.qubits:
            v = x if isinstance(x, int) else self.interpret(x)
            if not isinstance(v, (int, float)):
                return f"invalid qubit ref {v}"
            qi = int(v)
            if qi < 0 or qi >= total_qubits:
                return f"qubit {qi} out of range 0..{total_qubits-1}"
            qvals.append(qi)
        params = gate.parameters
        try:
            if name == "H":
                circuit.h(qvals[0])
            elif name == "X":
                circuit.x(qvals[0])
            elif name == "Y":
                circuit.y(qvals[0])
            elif name == "Z":
                circuit.z(qvals[0])
            elif name in ("CNOT", "CX"):
                if len(qvals) != 2:
                    return "CNOT requires 2 qubits"
                circuit.cnot(qvals[0], qvals[1])
            elif name == "RX" and len(params) == 1:
                circuit.rx(qvals[0], float(params[0]))
            elif name == "RY" and len(params) == 1:
                circuit.ry(qvals[0], float(params[0]))
            elif name == "RZ" and len(params) == 1:
                circuit.rz(qvals[0], float(params[0]))
            else:
                return f"unsupported gate {name}"
        except Exception as e:
            return str(e)
        return None


def parse(source: str) -> ProgramNode:
    lexer = Lexer(source)
    return EnhancedParser(lexer.tokenize()).parse()


__all__ = ["SynapseInterpreter", "parse"]
