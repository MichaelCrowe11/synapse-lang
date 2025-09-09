"""Relocated quantum core previously in synapse_quantum_core.py.
Adds minimal noise model stub + validation utilities.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Union
import numpy as np

class QuantumGate(Enum):
    I = "I"; X = "X"; Y = "Y"; Z = "Z"; H = "H"; S = "S"; T = "T"; RX = "RX"; RY = "RY"; RZ = "RZ"
    CNOT = "CNOT"; CZ = "CZ"; SWAP = "SWAP"; TOFFOLI = "TOFFOLI"; FREDKIN = "FREDKIN"

@dataclass
class QuantumOperation:
    gate: QuantumGate
    qubits: List[int]
    parameters: List[float] | None = None
    label: str = ""
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []

class QuantumCircuitBuilder:
    def __init__(self, num_qubits: int, name: str = "circuit"):
        self.num_qubits = num_qubits
        self.name = name
        self.operations: List[QuantumOperation] = []
        self.measurements: Dict[int, int] = {}
        self.classical_bits = 0

    # --- gate helpers ---
    def add_gate(self, gate: QuantumGate, qubits: Union[int, List[int]], parameters: Optional[List[float]] = None):
        if isinstance(qubits, int):
            qubits = [qubits]
        for q in qubits:
            if q < 0 or q >= self.num_qubits:
                raise ValueError(f"Qubit index {q} out of range")
        self._validate_gate(gate, qubits, parameters or [])
        self.operations.append(QuantumOperation(gate, qubits, parameters or []))
        return self
    def x(self, q:int): return self.add_gate(QuantumGate.X, q)
    def y(self, q:int): return self.add_gate(QuantumGate.Y, q)
    def z(self, q:int): return self.add_gate(QuantumGate.Z, q)
    def h(self, q:int): return self.add_gate(QuantumGate.H, q)
    def cnot(self, c:int, t:int): return self.add_gate(QuantumGate.CNOT, [c,t])
    def rx(self, q:int, a:float): return self.add_gate(QuantumGate.RX, q, [a])
    def ry(self, q:int, a:float): return self.add_gate(QuantumGate.RY, q, [a])
    def rz(self, q:int, a:float): return self.add_gate(QuantumGate.RZ, q, [a])

    def measure(self, qubit:int, classical_bit:int|None=None):
        if classical_bit is None:
            classical_bit = self.classical_bits
            self.classical_bits += 1
        self.measurements[qubit] = classical_bit
        return self
    def measure_all(self):
        for i in range(self.num_qubits):
            self.measure(i)
        return self

    def _validate_gate(self, gate: QuantumGate, qubits: List[int], params: List[float]):
        single={QuantumGate.I,QuantumGate.X,QuantumGate.Y,QuantumGate.Z,QuantumGate.H,QuantumGate.S,QuantumGate.T,QuantumGate.RX,QuantumGate.RY,QuantumGate.RZ}
        two={QuantumGate.CNOT,QuantumGate.CZ,QuantumGate.SWAP}
        three={QuantumGate.TOFFOLI,QuantumGate.FREDKIN}
        if gate in single and len(qubits)!=1: raise ValueError(f"Gate {gate.value} needs 1 qubit")
        if gate in two and len(qubits)!=2: raise ValueError(f"Gate {gate.value} needs 2 qubits")
        if gate in three and len(qubits)!=3: raise ValueError(f"Gate {gate.value} needs 3 qubits")
        if gate in {QuantumGate.RX,QuantumGate.RY,QuantumGate.RZ} and len(params)!=1:
            raise ValueError(f"Rotation {gate.value} needs 1 parameter")

class SimulatorBackend:
    def __init__(self, name: str = "synapse_simulator"):
        self.name = name
        self.max_qubits = 24

    def execute(self, circuit: QuantumCircuitBuilder, shots: int = 1000, noise: Optional[Dict[str, Any]] = None) -> Dict[str,int]:
        if circuit.num_qubits > self.max_qubits:
            raise ValueError("Too many qubits for simulator")
        state = np.zeros(2**circuit.num_qubits, dtype=complex)
        state[0] = 1.0
        for op in circuit.operations:
            state = self._apply(state, op, circuit.num_qubits)
        results: Dict[str,int] = {}
        probs = np.abs(state)**2
        for _ in range(shots):
            outcome = np.random.choice(len(probs), p=probs)
            bit_string = format(outcome, f'0{circuit.num_qubits}b')
            # Apply simple depolarizing noise post-measure if requested
            if noise and noise.get("model") == "depolarizing":
                p = float(noise.get("p", 0.0))
                if p>0:
                    # with probability p, flip a random bit in the string
                    if np.random.rand() < p:
                        idx = np.random.randint(0, circuit.num_qubits)
                        b_list = list(bit_string)
                        b_list[idx] = '1' if b_list[idx]=='0' else '0'
                        bit_string = ''.join(b_list)
            results[bit_string] = results.get(bit_string,0)+1
        return results

    # simplified gate applications
    def _apply(self, state, op: QuantumOperation, n: int):
        # Dispatch on gate type
        if op.gate == QuantumGate.X:
            return self._x(state, op.qubits[0], n)
        if op.gate == QuantumGate.Y:
            return self._single_unitary(state, op.qubits[0], n, np.array([[0,-1j],[1j,0]]))
        if op.gate == QuantumGate.Z:
            return self._single_unitary(state, op.qubits[0], n, np.array([[1,0],[0,-1]]))
        if op.gate == QuantumGate.H:
            return self._h(state, op.qubits[0], n)
        if op.gate == QuantumGate.S:
            return self._single_unitary(state, op.qubits[0], n, np.array([[1,0],[0,1j]]))
        if op.gate == QuantumGate.T:
            return self._single_unitary(state, op.qubits[0], n, np.array([[1,0],[0,np.exp(1j*np.pi/4)]]))
        if op.gate == QuantumGate.CNOT:
            return self._cnot(state, op.qubits[0], op.qubits[1], n)
        if op.gate == QuantumGate.CZ:
            return self._cz(state, op.qubits[0], op.qubits[1], n)
        if op.gate == QuantumGate.SWAP:
            return self._swap(state, op.qubits[0], op.qubits[1], n)
        if op.gate == QuantumGate.TOFFOLI:
            return self._toffoli(state, op.qubits[0], op.qubits[1], op.qubits[2], n)
        if op.gate == QuantumGate.FREDKIN:
            return self._fredkin(state, op.qubits[0], op.qubits[1], op.qubits[2], n)
        if op.gate == QuantumGate.RX:
            return self._rotation(state, op.qubits[0], n, axis='X', theta=op.parameters[0])
        if op.gate == QuantumGate.RY:
            return self._rotation(state, op.qubits[0], n, axis='Y', theta=op.parameters[0])
        if op.gate == QuantumGate.RZ:
            return self._rotation(state, op.qubits[0], n, axis='Z', theta=op.parameters[0])
        return state
    def _x(self, state, q, n):
        new = np.copy(state); mask = 1 << (n-1-q)
        for i in range(len(state)):
            j = i ^ mask
            new[i] = state[j]
        return new
    def _h(self, state, q, n):
        new = np.zeros_like(state); mask = 1 << (n-1-q)
        for i in range(len(state)):
            j = i ^ mask
            if i & mask:
                new[i] = (state[j]-state[i])/np.sqrt(2)
                new[j] = (state[j]+state[i])/np.sqrt(2)
            elif not new[i]:
                new[i] = (state[i]+state[j])/np.sqrt(2)
                new[j] = (state[i]-state[j])/np.sqrt(2)
        return new
    def _cnot(self, state, c, t, n):
        new = np.copy(state); cm=1 << (n-1-c); tm=1 << (n-1-t)
        for i in range(len(state)):
            if i & cm:
                j = i ^ tm
                if j > i:  # swap only once per pair
                    new[i], new[j] = state[j], state[i]
        return new
    def _single_unitary(self, state, q, n, U: np.ndarray):
        new = np.copy(state); mask = 1 << (n-1-q)
        for i in range(len(state)):
            j = i ^ mask
            if i & mask:
                a = state[j]; b = state[i]
                new[j] = U[0,0]*a + U[0,1]*b
                new[i] = U[1,0]*a + U[1,1]*b
        return new
    def _rotation(self, state, q, n, axis: str, theta: float):
        ct = np.cos(theta/2); st = np.sin(theta/2)
        if axis=='X': U = np.array([[ct, -1j*st],[-1j*st, ct]])
        elif axis=='Y': U = np.array([[ct, -st],[st, ct]])
        else: # Z
            U = np.array([[np.exp(-1j*theta/2),0],[0,np.exp(1j*theta/2)]])
        return self._single_unitary(state, q, n, U)
    def _cz(self, state, c, t, n):
        new = np.copy(state); cm=1 << (n-1-c); tm=1 << (n-1-t)
        for i in range(len(state)):
            if (i & cm) and (i & tm):
                new[i] = -state[i]
        return new
    def _swap(self, state, a, b, n):
        if a==b: return state
        new = np.copy(state); am=1 << (n-1-a); bm=1 << (n-1-b)
        for i in range(len(state)):
            has_a = i & am; has_b = i & bm
            if (has_a and not has_b) or (has_b and not has_a):
                j = i ^ (am | bm)
                if j>i:
                    new[i], new[j] = state[j], state[i]
        return new
    def _toffoli(self, state, a, b, t, n):
        new = np.copy(state); am=1 << (n-1-a); bm=1 << (n-1-b); tm=1 << (n-1-t)
        for i in range(len(state)):
            if (i & am) and (i & bm):
                j = i ^ tm
                if j > i:
                    new[i], new[j] = state[j], state[i]
        return new
    def _fredkin(self, state, c, a, b, n):
        # controlled swap of a,b with control c
        if a==b: return state
        new = np.copy(state); cm=1 << (n-1-c); am=1 << (n-1-a); bm=1 << (n-1-b)
        for i in range(len(state)):
            if i & cm:
                has_a = i & am; has_b = i & bm
                if (has_a and not has_b) or (has_b and not has_a):
                    j = i ^ (am | bm)
                    if j>i:
                        new[i], new[j] = state[j], state[i]
        return new

class QuantumAlgorithms:
    @staticmethod
    def bell_pair() -> QuantumCircuitBuilder:
        c = QuantumCircuitBuilder(2, "bell")
        c.h(0).cnot(0,1).measure_all()
        return c

__all__ = [
    "QuantumCircuitBuilder",
    "SimulatorBackend",
    "QuantumGate",
    "QuantumAlgorithms",
]
