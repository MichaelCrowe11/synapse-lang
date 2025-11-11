#!/usr/bin/env python3
"""
SYNAPSE INTERPRETER - BACKEND INTEGRATION
Wires the backend POC into Synapse language runtime
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synapse_lang.backends import auto, cg_solve, get_backend_info, gpu_matmul, vqe_minimize


class SynapseBackendIntegration:
    """Integrates backend operations into Synapse interpreter"""

    def __init__(self, interpreter):
        """
        Args:
            interpreter: Synapse interpreter instance
        """
        self.interpreter = interpreter
        self.current_backend = auto()
        self.register_backend_functions()

    def register_backend_functions(self):
        """Register all backend functions as Synapse builtins"""

        # Backend namespace
        backend_ns = {
            "auto": self.backend_auto,
            "info": self.backend_info,
            "solve": self.backend_solve,
            "matmul": self.backend_matmul,
            "gpu_matmul": self.backend_gpu_matmul,
            "vqe": self.backend_vqe,
            "set": self.backend_set,
        }

        # Register under 'backend' namespace
        if hasattr(self.interpreter, "env"):
            self.interpreter.env["backend"] = backend_ns
        elif hasattr(self.interpreter, "builtins"):
            self.interpreter.builtins["backend"] = backend_ns
        else:
            # Fallback: add to global namespace
            self.interpreter.backend = backend_ns

    def backend_auto(self):
        """Auto-detect optimal backend"""
        self.current_backend = auto()
        return self.current_backend

    def backend_info(self):
        """Get detailed backend information"""
        info = get_backend_info()
        # Format for Synapse display
        return {
            "current": self.current_backend,
            "available": list(info["available"].keys()),
            "active": [k for k, v in info["available"].items() if v],
            "versions": info.get("versions", {})
        }

    def backend_solve(self, A, b, **kwargs):
        """Solve linear system with automatic backend selection"""
        # Convert Synapse types if needed
        import numpy as np

        # Handle uncertain values
        if hasattr(A, "nominal"):
            A = A.nominal
        if hasattr(b, "nominal"):
            b = b.nominal

        # Convert to numpy
        A = np.asarray(A)
        b = np.asarray(b)

        # Solve based on backend
        if "gpu" in self.current_backend:
            from synapse_lang.backends.gpu_fallback import solve_linear
            return solve_linear(A, b)
        else:
            return cg_solve(A, b, **kwargs)

    def backend_matmul(self, A, B):
        """Matrix multiplication with backend selection"""

        # Handle uncertain values
        if hasattr(A, "nominal"):
            A = A.nominal
        if hasattr(B, "nominal"):
            B = B.nominal

        # Use GPU if available
        return gpu_matmul(A, B)

    def backend_gpu_matmul(self, A, B):
        """Explicit GPU matrix multiplication"""
        return gpu_matmul(A, B, use_gpu=True)

    def backend_vqe(self, params, hamiltonian=None, **kwargs):
        """Quantum VQE optimization"""
        return vqe_minimize(params, hamiltonian, **kwargs)

    def backend_set(self, backend_name):
        """Set specific backend"""
        from synapse_lang.backends import set_default_backend
        self.current_backend = backend_name
        set_default_backend(backend_name)
        return backend_name


# ============================================================================
# SYNAPSE CODE EXAMPLES
# ============================================================================

SYNAPSE_BACKEND_EXAMPLES = """
// Example 1: Auto-detect backend
let best_backend = backend.auto()
print("Using backend:", best_backend)

// Example 2: Solve linear system
let A = [[4, 1], [1, 3]]
let b = [1, 2]
let x = backend.solve(A, b)
print("Solution:", x)

// Example 3: GPU matrix multiplication
let M1 = random_matrix(1000, 1000)
let M2 = random_matrix(1000, 1000)
let result = backend.gpu_matmul(M1, M2)

// Example 4: Quantum optimization
let H = [[−1, 0.4], [0.4, −0.5]]
let ground_state = backend.vqe([0.1, 0.2], H)
print("Ground state energy:", ground_state.fun)

// Example 5: With uncertainty propagation
uncertain temp = 298.15 ± 0.5
uncertain pressure = 101.325 ± 0.1

// System matrix with uncertainties
let K = build_matrix(temp, pressure)
let f = build_force(temp)

// Solve preserves uncertainties
let u = backend.solve(K, f)
print("Displacement:", u, "± ", u.uncertainty)
"""


# ============================================================================
# INTEGRATION HELPER
# ============================================================================

def integrate_with_synapse(interpreter_instance=None):
    """
    Integrate backend with existing Synapse interpreter

    Usage:
        from synapse_lang import Interpreter
        interp = Interpreter()
        integrate_with_synapse(interp)
    """
    if interpreter_instance is None:
        # Try to import default interpreter
        try:
            from synapse_lang import Interpreter
            interpreter_instance = Interpreter()
        except ImportError:
            print("Could not import Synapse interpreter")
            return None

    # Create integration
    integration = SynapseBackendIntegration(interpreter_instance)

    print("✅ Backend integration complete!")
    print(f"Current backend: {integration.current_backend}")
    print("\nAvailable functions:")
    print("  backend.auto()       - Auto-detect best backend")
    print("  backend.info()       - Get backend information")
    print("  backend.solve(A, b)  - Solve linear system")
    print("  backend.matmul(A, B) - Matrix multiplication")
    print("  backend.vqe(...)     - Quantum optimization")

    return integration


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    print("SYNAPSE BACKEND INTEGRATION TEST")
    print("="*60)

    # Create mock interpreter for testing
    class MockInterpreter:
        def __init__(self):
            self.env = {}

    # Test integration
    mock_interp = MockInterpreter()
    integration = SynapseBackendIntegration(mock_interp)

    print("\nRegistered functions in interpreter:")
    for name in mock_interp.env.get("backend", {}).keys():
        print(f"  backend.{name}")

    print("\n" + "="*60)
    print("SYNAPSE CODE EXAMPLES:")
    print("="*60)
    print(SYNAPSE_BACKEND_EXAMPLES)

    print("\nIntegration ready for use!")
