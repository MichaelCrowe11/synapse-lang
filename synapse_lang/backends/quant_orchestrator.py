"""
Minimal quant-hpc-lite orchestrator POC.
Attempts to import local quant_hpc_lite controller from repo; if absent,
provides a simulator stub.

Provides vqe_energy(params, hamiltonian) and vqe_minimize(initial_params,...)
"""
from typing import Sequence, Callable, Optional, Dict, Any, Union
import numpy as np


# Try to import the provided quant-hpc-lite controller (uploaded into the project)
try:
    import quant_hpc_lite as qhl  # user-provided module (repo-in-a-file)
    HAS_QHL = True
except Exception:
    HAS_QHL = False


class QuantumSimulator:
    """Simple quantum circuit simulator for testing"""

    def __init__(self, n_qubits: int):
        self.n_qubits = n_qubits
        self.state = np.zeros(2**n_qubits, dtype=complex)
        self.state[0] = 1.0  # |00...0⟩ state

    def apply_gate(self, gate: str, qubit: int, param: float = 0.0):
        """Apply single-qubit gate"""
        if gate == 'H':  # Hadamard
            self._apply_hadamard(qubit)
        elif gate == 'RY':  # Y-rotation
            self._apply_ry(qubit, param)
        elif gate == 'RZ':  # Z-rotation
            self._apply_rz(qubit, param)

    def _apply_hadamard(self, qubit: int):
        """Apply Hadamard gate to qubit"""
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        self._apply_single_gate(H, qubit)

    def _apply_ry(self, qubit: int, theta: float):
        """Apply Y-rotation gate"""
        c = np.cos(theta / 2)
        s = np.sin(theta / 2)
        RY = np.array([[c, -s], [s, c]])
        self._apply_single_gate(RY, qubit)

    def _apply_rz(self, qubit: int, theta: float):
        """Apply Z-rotation gate"""
        RZ = np.diag([np.exp(-1j * theta / 2), np.exp(1j * theta / 2)])
        self._apply_single_gate(RZ, qubit)

    def _apply_single_gate(self, gate: np.ndarray, qubit: int):
        """Apply single-qubit gate to state vector"""
        n = self.n_qubits
        new_state = np.zeros_like(self.state)

        for i in range(2**n):
            # Get bit value at qubit position
            bit = (i >> qubit) & 1

            # Indices for 0 and 1 states
            i0 = i & ~(1 << qubit)  # Clear bit
            i1 = i | (1 << qubit)   # Set bit

            # Apply gate
            if bit == 0:
                new_state[i] += gate[0, 0] * self.state[i0] + gate[0, 1] * self.state[i1]
            else:
                new_state[i] += gate[1, 0] * self.state[i0] + gate[1, 1] * self.state[i1]

        self.state = new_state

    def expectation(self, operator: np.ndarray) -> float:
        """Calculate expectation value ⟨ψ|O|ψ⟩"""
        if operator.shape != (2**self.n_qubits, 2**self.n_qubits):
            # If operator is small, assume it acts on first qubits
            # and pad with identity
            n_op_qubits = int(np.log2(operator.shape[0]))
            I_rest = np.eye(2**(self.n_qubits - n_op_qubits))
            operator = np.kron(operator, I_rest)

        return np.real(self.state.conj() @ operator @ self.state)


def _stub_expectation(params, hamiltonian):
    """Simulator using simple quantum circuit model"""
    p = np.array(params)

    if hamiltonian is None:
        # Default: sum of squared parameters (optimization test)
        return float((p ** 2).sum())

    # Simulate a simple variational circuit
    n_params = len(params)
    n_qubits = max(2, int(np.ceil(np.log2(n_params + 1))))

    sim = QuantumSimulator(n_qubits)

    # Apply parameterized ansatz
    for i, param in enumerate(params):
        qubit = i % n_qubits
        # Layer of RY rotations
        sim.apply_gate('RY', qubit, param)

        # Entangling layer (simplified)
        if i > 0 and i % n_qubits == 0:
            for q in range(n_qubits - 1):
                # Simplified: apply phase based on parameter
                sim.apply_gate('RZ', q, params[i - 1] * 0.1)

    # Calculate expectation value
    if isinstance(hamiltonian, (list, np.ndarray)):
        H = np.array(hamiltonian)
        if H.ndim == 1:
            # Diagonal Hamiltonian
            H_full = np.diag(H[:2**n_qubits])
        elif H.ndim == 2:
            H_full = H
        else:
            H_full = np.eye(2**n_qubits)

        return sim.expectation(H_full)
    else:
        # Scalar Hamiltonian
        return float(hamiltonian) * np.linalg.norm(sim.state)**2


def vqe_energy(params: Sequence[float], hamiltonian=None,
               backend: str = 'sim', shots: int = 1024) -> float:
    """Run the parameterized circuit and return expected energy (POC).

    Args:
        params: Variational parameters
        hamiltonian: Hamiltonian operator (matrix, diagonal, or None)
        backend: Backend to use ('sim', 'qhl', 'ibm', etc.)
        shots: Number of measurement shots (for shot-based simulators)

    Returns:
        Expectation value of energy
    """
    if HAS_QHL and backend != 'sim':
        # Example usage of the controller (API may differ in real module)
        try:
            ctrl = qhl.QuantumController()
            qc = qhl.build_ansatz_from_params(params)
            job = ctrl.submit(qc, backend=backend, shots=shots)
            res = ctrl.get_expectation(job, hamiltonian)
            return float(res)
        except Exception as e:
            print(f"quant_hpc_lite call failed, falling back to simulator: {e}")
            return _stub_expectation(params, hamiltonian)
    else:
        return _stub_expectation(params, hamiltonian)


def vqe_minimize(initial_params, hamiltonian=None,
                 method: str = 'L-BFGS-B', backend: str = 'sim',
                 maxiter: int = 100, callback: Optional[Callable] = None) -> Dict[str, Any]:
    """Classical optimization wrapper minimizing vqe_energy.

    Args:
        initial_params: Initial variational parameters
        hamiltonian: Hamiltonian to minimize
        method: Optimization method
        backend: Quantum backend
        maxiter: Maximum iterations
        callback: Optional callback function

    Returns:
        dict with x (opt params), fun (energy), success, and other info
    """
    history = {'energies': [], 'params': []}

    def track_progress(x):
        energy = vqe_energy(x, hamiltonian, backend=backend)
        history['energies'].append(energy)
        history['params'].append(x.copy())
        if callback:
            callback(x, energy)
        return energy

    try:
        import scipy.optimize as opt

        # Wrapper for optimization
        def objective(x):
            return track_progress(x)

        # Perform optimization
        res = opt.minimize(
            objective,
            initial_params,
            method=method,
            options={'maxiter': maxiter}
        )

        return {
            'x': res.x,
            'fun': float(res.fun),
            'success': res.success,
            'nit': res.nit,
            'message': res.message,
            'history': history
        }

    except ImportError:
        # Fallback: simple coordinate descent
        print("SciPy not available, using simple optimization")
        x = np.array(initial_params, dtype=float)
        best = track_progress(x)
        improved = True
        iterations = 0

        while improved and iterations < maxiter:
            improved = False
            iterations += 1

            for i in range(len(x)):
                for delta in [-0.1, 0.1]:
                    x_trial = x.copy()
                    x_trial[i] += delta
                    energy = track_progress(x_trial)

                    if energy < best:
                        best = energy
                        x = x_trial
                        improved = True

        return {
            'x': x,
            'fun': best,
            'success': True,
            'nit': iterations,
            'message': 'Simple optimization completed',
            'history': history
        }


def get_quantum_backend_info() -> Dict[str, Any]:
    """Get information about available quantum backends"""
    info = {
        'simulator': True,  # Always available
        'quant_hpc_lite': HAS_QHL,
        'backends': ['sim']  # Simulator always available
    }

    if HAS_QHL:
        try:
            ctrl = qhl.QuantumController()
            info['backends'].extend(ctrl.list_backends())
            info['default_backend'] = ctrl.default_backend
        except:
            pass

    return info


class VQEProblem:
    """Helper class to set up VQE problems"""

    def __init__(self, hamiltonian: Union[np.ndarray, list],
                 n_qubits: Optional[int] = None):
        """Initialize VQE problem.

        Args:
            hamiltonian: Problem Hamiltonian
            n_qubits: Number of qubits (auto-detected if None)
        """
        self.hamiltonian = np.array(hamiltonian)

        if n_qubits is None:
            # Auto-detect from Hamiltonian size
            if self.hamiltonian.ndim == 2:
                n_qubits = int(np.log2(self.hamiltonian.shape[0]))
            else:
                n_qubits = 2  # Default

        self.n_qubits = n_qubits
        self.n_params = 2 * n_qubits  # Default ansatz parameters

    def random_initial_params(self, seed: Optional[int] = None) -> np.ndarray:
        """Generate random initial parameters"""
        if seed is not None:
            np.random.seed(seed)
        return np.random.uniform(-np.pi, np.pi, self.n_params)

    def solve(self, initial_params: Optional[np.ndarray] = None,
              **kwargs) -> Dict[str, Any]:
        """Solve the VQE problem"""
        if initial_params is None:
            initial_params = self.random_initial_params()

        return vqe_minimize(initial_params, self.hamiltonian, **kwargs)


# Example Hamiltonians for testing
EXAMPLE_HAMILTONIANS = {
    'h2': np.array([  # H2 molecule (simplified)
        [-1.0523, 0.3979, 0, 0],
        [0.3979, -0.4719, 0, 0],
        [0, 0, -0.4719, 0.3979],
        [0, 0, 0.3979, -1.0523]
    ]),
    'ising_2': np.array([  # 2-qubit Ising
        [-2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 2]
    ]),
    'xyz_2': np.array([  # 2-qubit XYZ model
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [1, 0, 0, 0]
    ])
}