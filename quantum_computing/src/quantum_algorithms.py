"""
Quantum Algorithms for Synapse Language

Implements fundamental quantum algorithms including Deutsch-Jozsa,
Grover's search, Shor's factoring, and quantum machine learning algorithms.
"""

import numpy as np
from typing import List, Dict, Callable, Optional, Tuple, Union
import math
from .quantum_circuit import QuantumCircuit, QuantumRegister, ClassicalRegister

class QuantumAlgorithms:
    """Collection of quantum algorithms implemented in Synapse Language."""
    
    @staticmethod
    def deutsch_jozsa(oracle_function: Callable[[List[int]], int], n_qubits: int) -> QuantumCircuit:
        """
        Implement Deutsch-Jozsa algorithm to determine if function is constant or balanced.
        
        Args:
            oracle_function: Function that takes list of bits and returns 0 or 1
            n_qubits: Number of input qubits
            
        Returns:
            QuantumCircuit implementing the algorithm
        """
        # Create circuit with n input qubits + 1 ancilla qubit
        qreg = QuantumRegister(n_qubits + 1)
        creg = ClassicalRegister(n_qubits)
        circuit = QuantumCircuit(qreg, creg)
        
        # Initialize ancilla qubit in |1⟩ state
        circuit.x(n_qubits)
        
        # Apply Hadamard to all qubits
        for i in range(n_qubits + 1):
            circuit.h(i)
        
        # Apply oracle function
        circuit = QuantumAlgorithms._apply_deutsch_oracle(circuit, oracle_function, n_qubits)
        
        # Apply Hadamard to input qubits
        for i in range(n_qubits):
            circuit.h(i)
        
        # Measure input qubits
        for i in range(n_qubits):
            circuit.measure(i, i)
        
        circuit.name = "Deutsch-Jozsa Algorithm"
        return circuit
    
    @staticmethod
    def _apply_deutsch_oracle(circuit: QuantumCircuit, oracle_func: Callable, n_qubits: int) -> QuantumCircuit:
        """Apply oracle function to quantum circuit."""
        # This is a simplified implementation
        # In practice, oracle would be implemented as quantum gates
        
        # For demonstration, we'll implement a simple balanced function oracle
        # Real implementation would depend on the specific oracle function
        
        # Example: f(x) = x₀ ⊕ x₁ (balanced function)
        if n_qubits >= 2:
            circuit.cnot(0, n_qubits)  # Apply to ancilla
            circuit.cnot(1, n_qubits)  # Apply to ancilla
        
        return circuit
    
    @staticmethod
    def grovers_search(marked_items: List[int], n_qubits: int, iterations: int = None) -> QuantumCircuit:
        """
        Implement Grover's quantum search algorithm.
        
        Args:
            marked_items: List of marked item indices
            n_qubits: Number of qubits (2^n_qubits total items)
            iterations: Number of Grover iterations (optimal if None)
            
        Returns:
            QuantumCircuit implementing Grover's algorithm
        """
        if iterations is None:
            # Optimal number of iterations: π/4 * √(N/M)
            N = 2 ** n_qubits
            M = len(marked_items)
            iterations = int(math.pi / 4 * math.sqrt(N / M))
        
        # Create circuit
        qreg = QuantumRegister(n_qubits)
        creg = ClassicalRegister(n_qubits)
        circuit = QuantumCircuit(qreg, creg)
        
        # Initialize superposition state
        for i in range(n_qubits):
            circuit.h(i)
        
        # Apply Grover iterations
        for _ in range(iterations):
            # Oracle: mark target items
            circuit = QuantumAlgorithms._apply_grover_oracle(circuit, marked_items, n_qubits)
            
            # Diffuser: inversion about average
            circuit = QuantumAlgorithms._apply_grover_diffuser(circuit, n_qubits)
        
        # Measure all qubits
        circuit.measure_all()
        
        circuit.name = f"Grover's Search ({iterations} iterations)"
        return circuit
    
    @staticmethod
    def _apply_grover_oracle(circuit: QuantumCircuit, marked_items: List[int], n_qubits: int) -> QuantumCircuit:
        """Apply Grover oracle to mark target items."""
        for item in marked_items:
            # Convert item index to binary representation
            binary_str = format(item, f'0{n_qubits}b')
            
            # Apply X gates to qubits that should be 0
            for i, bit in enumerate(binary_str):
                if bit == '0':
                    circuit.x(i)
            
            # Apply controlled-Z gate (marks the state with -1 phase)
            if n_qubits == 1:
                circuit.z(0)
            elif n_qubits == 2:
                circuit.cz(0, 1)
            else:
                # Multi-controlled Z gate (simplified implementation)
                circuit.h(n_qubits - 1)
                for i in range(n_qubits - 2):
                    circuit.cnot(i, n_qubits - 1)
                circuit.h(n_qubits - 1)
            
            # Undo X gates
            for i, bit in enumerate(binary_str):
                if bit == '0':
                    circuit.x(i)
        
        return circuit
    
    @staticmethod
    def _apply_grover_diffuser(circuit: QuantumCircuit, n_qubits: int) -> QuantumCircuit:
        """Apply Grover diffuser (inversion about average)."""
        # Apply Hadamard gates
        for i in range(n_qubits):
            circuit.h(i)
        
        # Apply X gates
        for i in range(n_qubits):
            circuit.x(i)
        
        # Apply controlled-Z gate
        if n_qubits == 1:
            circuit.z(0)
        elif n_qubits == 2:
            circuit.cz(0, 1)
        else:
            # Multi-controlled Z (simplified)
            circuit.h(n_qubits - 1)
            for i in range(n_qubits - 2):
                circuit.cnot(i, n_qubits - 1)
            circuit.h(n_qubits - 1)
        
        # Undo X gates
        for i in range(n_qubits):
            circuit.x(i)
        
        # Undo Hadamard gates
        for i in range(n_qubits):
            circuit.h(i)
        
        return circuit
    
    @staticmethod
    def quantum_fourier_transform(n_qubits: int, inverse: bool = False) -> QuantumCircuit:
        """
        Implement Quantum Fourier Transform.
        
        Args:
            n_qubits: Number of qubits
            inverse: If True, implement inverse QFT
            
        Returns:
            QuantumCircuit implementing QFT
        """
        qreg = QuantumRegister(n_qubits)
        circuit = QuantumCircuit(qreg)
        
        def qft_rotations(circuit, n):
            """Apply QFT rotations."""
            if n == 0:
                return circuit
            
            n -= 1
            circuit.h(n)
            
            for qubit in range(n):
                angle = math.pi / (2 ** (n - qubit))
                circuit.rz(angle, n)  # Controlled rotation would be better
            
            qft_rotations(circuit, n)
        
        if inverse:
            # Inverse QFT: reverse the order of operations
            qft_rotations(circuit, n_qubits)
            # Reverse qubit order
            for i in range(n_qubits // 2):
                circuit.swap(i, n_qubits - 1 - i)
        else:
            qft_rotations(circuit, n_qubits)
        
        circuit.name = f"QFT{'†' if inverse else ''} ({n_qubits} qubits)"
        return circuit
    
    @staticmethod
    def quantum_phase_estimation(unitary_matrix: np.ndarray, eigenstate: np.ndarray, 
                                n_counting_qubits: int) -> QuantumCircuit:
        """
        Implement Quantum Phase Estimation algorithm.
        
        Args:
            unitary_matrix: Unitary operator U
            eigenstate: Eigenstate |ψ⟩ of U
            n_counting_qubits: Number of counting qubits for precision
            
        Returns:
            QuantumCircuit implementing QPE
        """
        n_state_qubits = int(math.log2(len(eigenstate)))
        total_qubits = n_counting_qubits + n_state_qubits
        
        qreg = QuantumRegister(total_qubits)
        creg = ClassicalRegister(n_counting_qubits)
        circuit = QuantumCircuit(qreg, creg)
        
        # Initialize counting qubits in superposition
        for i in range(n_counting_qubits):
            circuit.h(i)
        
        # Initialize state qubits in eigenstate (simplified)
        # In practice, this would require state preparation
        
        # Apply controlled unitary operations
        for i in range(n_counting_qubits):
            # Apply controlled-U^(2^i)
            repetitions = 2 ** i
            for _ in range(repetitions):
                # Apply controlled unitary (simplified implementation)
                pass  # Would implement controlled unitary gates
        
        # Apply inverse QFT to counting qubits
        qft_circuit = QuantumAlgorithms.quantum_fourier_transform(n_counting_qubits, inverse=True)
        
        # Measure counting qubits
        for i in range(n_counting_qubits):
            circuit.measure(i, i)
        
        circuit.name = f"Quantum Phase Estimation ({n_counting_qubits} counting qubits)"
        return circuit
    
    @staticmethod
    def shors_algorithm(N: int, a: int = None) -> QuantumCircuit:
        """
        Implement Shor's algorithm for integer factorization (simplified version).
        
        Args:
            N: Number to factor
            a: Random integer coprime to N
            
        Returns:
            QuantumCircuit implementing period finding part of Shor's algorithm
        """
        if a is None:
            a = 2  # Simplified choice
        
        # Number of qubits needed
        n_qubits = 2 * int(math.ceil(math.log2(N)))
        
        qreg = QuantumRegister(n_qubits)
        creg = ClassicalRegister(n_qubits // 2)
        circuit = QuantumCircuit(qreg, creg)
        
        # Initialize counting register in superposition
        for i in range(n_qubits // 2):
            circuit.h(i)
        
        # Initialize work register to |1⟩
        circuit.x(n_qubits // 2)
        
        # Apply controlled modular exponentiation: |x⟩|1⟩ → |x⟩|a^x mod N⟩
        # This is the most complex part and requires quantum arithmetic circuits
        # Simplified implementation placeholder
        
        # Apply QFT to counting register
        for i in range(n_qubits // 2):
            circuit.h(i)
            for j in range(i + 1, n_qubits // 2):
                angle = math.pi / (2 ** (j - i))
                # Would apply controlled rotation
        
        # Measure counting register
        for i in range(n_qubits // 2):
            circuit.measure(i, i)
        
        circuit.name = f"Shor's Algorithm (N={N}, a={a})"
        return circuit
    
    @staticmethod
    def quantum_walk(n_steps: int, n_positions: int) -> QuantumCircuit:
        """
        Implement quantum walk algorithm.
        
        Args:
            n_steps: Number of walk steps
            n_positions: Number of possible positions
            
        Returns:
            QuantumCircuit implementing quantum walk
        """
        # Need qubits for position and coin (direction)
        position_qubits = int(math.ceil(math.log2(n_positions)))
        coin_qubits = 1
        total_qubits = position_qubits + coin_qubits
        
        qreg = QuantumRegister(total_qubits)
        creg = ClassicalRegister(total_qubits)
        circuit = QuantumCircuit(qreg, creg)
        
        # Initialize in center position
        center = n_positions // 2
        center_binary = format(center, f'0{position_qubits}b')
        for i, bit in enumerate(center_binary):
            if bit == '1':
                circuit.x(i)
        
        # Perform quantum walk steps
        for step in range(n_steps):
            # Coin flip: Hadamard on coin qubit
            circuit.h(position_qubits)
            
            # Conditional move: if coin is |0⟩ move left, if |1⟩ move right
            # This requires quantum arithmetic circuits
            # Simplified implementation
            for i in range(position_qubits):
                circuit.cnot(position_qubits, i)  # Conditional operation
        
        # Measure all qubits
        circuit.measure_all()
        
        circuit.name = f"Quantum Walk ({n_steps} steps, {n_positions} positions)"
        return circuit
    
    @staticmethod
    def simon_algorithm(oracle_function: Callable[[List[int]], List[int]], n_qubits: int) -> QuantumCircuit:
        """
        Implement Simon's algorithm for finding hidden period.
        
        Args:
            oracle_function: Function with hidden period s
            n_qubits: Number of input qubits
            
        Returns:
            QuantumCircuit implementing Simon's algorithm
        """
        # Need n qubits for input and n qubits for output
        qreg = QuantumRegister(2 * n_qubits)
        creg = ClassicalRegister(n_qubits)
        circuit = QuantumCircuit(qreg, creg)
        
        # Initialize input qubits in superposition
        for i in range(n_qubits):
            circuit.h(i)
        
        # Apply oracle function
        # This would require implementing the specific oracle
        # Simplified placeholder
        
        # Apply Hadamard to input qubits
        for i in range(n_qubits):
            circuit.h(i)
        
        # Measure input qubits
        for i in range(n_qubits):
            circuit.measure(i, i)
        
        circuit.name = f"Simon's Algorithm ({n_qubits} qubits)"
        return circuit
    
    @staticmethod
    def bernstein_vazirani(secret_string: str) -> QuantumCircuit:
        """
        Implement Bernstein-Vazirani algorithm to find hidden bit string.
        
        Args:
            secret_string: Hidden bit string to find
            
        Returns:
            QuantumCircuit implementing the algorithm
        """
        n_qubits = len(secret_string)
        
        qreg = QuantumRegister(n_qubits + 1)
        creg = ClassicalRegister(n_qubits)
        circuit = QuantumCircuit(qreg, creg)
        
        # Initialize ancilla qubit in |1⟩
        circuit.x(n_qubits)
        
        # Apply Hadamard to all qubits
        for i in range(n_qubits + 1):
            circuit.h(i)
        
        # Apply oracle based on secret string
        for i, bit in enumerate(secret_string):
            if bit == '1':
                circuit.cnot(i, n_qubits)  # Apply CNOT if bit is 1
        
        # Apply Hadamard to input qubits
        for i in range(n_qubits):
            circuit.h(i)
        
        # Measure input qubits
        for i in range(n_qubits):
            circuit.measure(i, i)
        
        circuit.name = f"Bernstein-Vazirani (secret: {secret_string})"
        return circuit

# Export algorithms class
__all__ = ['QuantumAlgorithms']