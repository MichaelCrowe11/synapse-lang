"""
Comprehensive tests for Synapse backend infrastructure.
Run: pytest tests/test_backends.py -v
"""
import pytest
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse_lang.backends import (
    cg_solve, gpu_matmul, vqe_energy, vqe_minimize,
    auto, get_backend_info, set_default_backend
)
from synapse_lang.backends.cg_solver import pcg_solve, bicgstab_solve
from synapse_lang.backends.gpu_fallback import (
    to_gpu, to_cpu, elementwise_op, solve_linear, eigh, svd,
    get_gpu_memory_info, GPUArray
)
from synapse_lang.backends.quant_orchestrator import (
    QuantumSimulator, VQEProblem, EXAMPLE_HAMILTONIANS
)


class TestCGSolver:
    """Test Conjugate Gradient solver implementations"""

    def test_cg_solve_small_spd(self):
        """Test CG solver on small SPD system"""
        # Create symmetric positive definite matrix
        A = np.array([[4.0, 1.0], [1.0, 3.0]])
        b = np.array([1.0, 2.0])

        x = cg_solve(A, b)

        # Verify solution
        expected = np.linalg.solve(A, b)
        assert np.allclose(x, expected, atol=1e-6)

    def test_cg_solve_larger_spd(self):
        """Test CG on larger SPD system"""
        n = 50
        # Generate random SPD matrix
        Q = np.random.randn(n, n)
        A = Q.T @ Q + np.eye(n)  # Ensure positive definite
        b = np.random.randn(n)

        x = cg_solve(A, b, tol=1e-8)

        # Verify solution
        residual = np.linalg.norm(A @ x - b)
        assert residual < 1e-6

    def test_pcg_solve_with_jacobi(self):
        """Test Preconditioned CG with Jacobi preconditioner"""
        n = 30
        # Diagonally dominant matrix
        A = np.random.randn(n, n)
        A = A.T @ A
        np.fill_diagonal(A, np.diag(A) + 5)
        b = np.random.randn(n)

        x = pcg_solve(A, b, M=None)  # Uses Jacobi by default

        # Verify solution
        residual = np.linalg.norm(A @ x - b)
        assert residual < 1e-6

    def test_bicgstab_nonsymmetric(self):
        """Test BiCGSTAB for non-symmetric system"""
        # Non-symmetric but well-conditioned matrix
        A = np.array([[3.0, 1.0], [2.0, 4.0]])
        b = np.array([1.0, 2.0])

        x = bicgstab_solve(A, b)

        # Verify solution
        expected = np.linalg.solve(A, b)
        assert np.allclose(x, expected, atol=1e-6)

    def test_cg_invalid_input(self):
        """Test CG with invalid inputs"""
        A = np.array([[1, 2, 3], [4, 5, 6]])  # Non-square
        b = np.array([1, 2])

        with pytest.raises(ValueError):
            cg_solve(A, b)


class TestGPUFallback:
    """Test GPU/CPU fallback functionality"""

    def test_matmul_fallback(self):
        """Test matrix multiplication with fallback"""
        A = np.random.rand(10, 8)
        B = np.random.rand(8, 6)

        C = gpu_matmul(A, B)

        # Verify result
        expected = A @ B
        assert np.allclose(C, expected, atol=1e-10)

    def test_gpu_array_wrapper(self):
        """Test GPUArray wrapper class"""
        data = np.random.rand(5, 5)
        arr = GPUArray(data, force_cpu=True)

        assert not arr.is_gpu
        assert arr.shape == (5, 5)
        assert np.allclose(arr.to_cpu(), data)

    def test_elementwise_operations(self):
        """Test elementwise operations"""
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])

        # Test various operations
        result_add = elementwise_op('add', a, b)
        assert np.allclose(result_add, a + b)

        result_mul = elementwise_op('multiply', a, b)
        assert np.allclose(result_mul, a * b)

        result_exp = elementwise_op('exp', a)
        assert np.allclose(result_exp, np.exp(a))

    def test_solve_linear_system(self):
        """Test linear system solver"""
        A = np.array([[3, 1], [1, 2]], dtype=float)
        b = np.array([9, 8], dtype=float)

        x = solve_linear(A, b)

        # Verify solution
        expected = np.linalg.solve(A, b)
        assert np.allclose(x, expected, atol=1e-10)

    def test_eigendecomposition(self):
        """Test eigenvalue decomposition"""
        # Create symmetric matrix
        A = np.array([[2, 1], [1, 2]], dtype=float)

        w, v = eigh(A)

        # Verify eigenvalues
        expected_w = np.array([1, 3])
        assert np.allclose(sorted(w), expected_w, atol=1e-10)

    def test_svd_decomposition(self):
        """Test singular value decomposition"""
        A = np.array([[1, 2], [3, 4], [5, 6]], dtype=float)

        U, S, Vt = svd(A)

        # Reconstruct and verify
        reconstructed = U @ np.diag(S) @ Vt[:2, :]
        assert np.allclose(reconstructed, A, atol=1e-10)

    def test_gpu_memory_info(self):
        """Test GPU memory information retrieval"""
        info = get_gpu_memory_info()
        assert 'available' in info
        # If GPU available, should have more keys
        if info['available']:
            assert 'used_bytes' in info


class TestQuantumOrchestrator:
    """Test quantum computing orchestrator"""

    def test_quantum_simulator_basic(self):
        """Test basic quantum simulator operations"""
        sim = QuantumSimulator(2)

        # Apply Hadamard to first qubit
        sim.apply_gate('H', 0)

        # State should be (|00⟩ + |01⟩)/√2
        expected = np.array([1, 1, 0, 0]) / np.sqrt(2)
        assert np.allclose(np.abs(sim.state), np.abs(expected), atol=1e-10)

    def test_quantum_simulator_rotation(self):
        """Test rotation gates"""
        sim = QuantumSimulator(1)

        # Apply Y rotation of π/2
        sim.apply_gate('RY', 0, np.pi/2)

        # State should be (|0⟩ + |1⟩)/√2
        expected = np.array([1/np.sqrt(2), 1/np.sqrt(2)])
        assert np.allclose(np.abs(sim.state), np.abs(expected), atol=1e-10)

    def test_vqe_energy_stub(self):
        """Test VQE energy calculation with stub"""
        params = [0.5, -0.3, 0.2]
        hamiltonian = np.eye(4)

        energy = vqe_energy(params, hamiltonian)

        assert isinstance(energy, float)
        assert energy >= 0  # For identity Hamiltonian

    def test_vqe_minimize_simple(self):
        """Test VQE optimization on simple problem"""
        # Simple diagonal Hamiltonian
        hamiltonian = np.diag([-1, 0, 0, 1])
        initial = [0.1, 0.2]

        result = vqe_minimize(initial, hamiltonian, maxiter=10)

        assert 'x' in result
        assert 'fun' in result
        assert 'success' in result
        assert result['fun'] <= vqe_energy(initial, hamiltonian)  # Should improve

    def test_vqe_problem_class(self):
        """Test VQEProblem helper class"""
        # Use H2 molecule Hamiltonian
        problem = VQEProblem(EXAMPLE_HAMILTONIANS['h2'])

        assert problem.n_qubits == 2
        assert problem.n_params == 4

        # Generate initial parameters
        params = problem.random_initial_params(seed=42)
        assert len(params) == problem.n_params

        # Solve problem
        result = problem.solve(initial_params=params, maxiter=5)
        assert result['success']

    def test_example_hamiltonians(self):
        """Test with provided example Hamiltonians"""
        for name, H in EXAMPLE_HAMILTONIANS.items():
            # Each should be a valid Hamiltonian
            assert H.shape[0] == H.shape[1]  # Square
            assert np.allclose(H, H.conj().T)  # Hermitian

            # Test energy calculation
            params = np.random.rand(4) * np.pi
            energy = vqe_energy(params, H)
            assert isinstance(energy, float)


class TestBackendDetection:
    """Test backend auto-detection and configuration"""

    def test_auto_backend_detection(self):
        """Test automatic backend detection"""
        backend = auto()
        assert backend in ['cpu.numpy', 'cpu.scipy', 'gpu.cupy', 'quant.hpc']

    def test_backend_info(self):
        """Test backend information retrieval"""
        info = get_backend_info()

        assert 'default' in info
        assert 'available' in info
        assert 'versions' in info

        # NumPy should always be available
        assert 'cpu.numpy' in info['available']

    def test_set_default_backend(self):
        """Test setting default backend"""
        original = auto()
        set_default_backend('cpu.numpy')
        info = get_backend_info()

        # Should be set to cpu.numpy now
        assert info['default'] == 'cpu.numpy'

        # Restore original
        set_default_backend(original)


class TestIntegration:
    """Integration tests combining multiple backends"""

    def test_combined_workflow(self):
        """Test a workflow using multiple backend features"""
        # Step 1: Solve linear system
        A = np.array([[4, 1], [1, 3]], dtype=float)
        b = np.array([1, 2], dtype=float)
        x = cg_solve(A, b)

        # Step 2: Matrix multiplication
        C = gpu_matmul(A, np.outer(x, x))

        # Step 3: Eigendecomposition
        w, v = eigh(C)

        # Step 4: Use in quantum simulation
        params = w[:2]  # Use eigenvalues as parameters
        energy = vqe_energy(params, hamiltonian=C)

        assert isinstance(energy, float)

    def test_large_scale_computation(self):
        """Test with larger matrices"""
        n = 100

        # Generate large SPD matrix
        Q = np.random.randn(n, n)
        A = Q.T @ Q + np.eye(n)

        # Large matrix multiplication
        B = np.random.randn(n, n)
        C = gpu_matmul(A, B)

        assert C.shape == (n, n)

        # Solve large system
        b = np.random.randn(n)
        x = cg_solve(A, b, maxiter=200)

        residual = np.linalg.norm(A @ x - b)
        assert residual < 1e-4


# Performance benchmarking tests
@pytest.mark.slow
class TestPerformance:
    """Performance benchmarking tests (marked as slow)"""

    def test_cg_performance(self):
        """Benchmark CG solver performance"""
        import time

        sizes = [50, 100, 200]
        times = []

        for n in sizes:
            Q = np.random.randn(n, n)
            A = Q.T @ Q + np.eye(n)
            b = np.random.randn(n)

            start = time.time()
            x = cg_solve(A, b)
            elapsed = time.time() - start
            times.append(elapsed)

            print(f"CG solve {n}x{n}: {elapsed:.4f}s")

        # Performance should scale reasonably
        assert all(t < 5.0 for t in times)  # All under 5 seconds

    def test_gpu_speedup(self):
        """Test GPU speedup if available"""
        import time

        n = 500
        A = np.random.randn(n, n)
        B = np.random.randn(n, n)

        # CPU timing
        start = time.time()
        C_cpu = np.matmul(A, B)
        cpu_time = time.time() - start

        # GPU timing (will fall back to CPU if not available)
        start = time.time()
        C_gpu = gpu_matmul(A, B)
        gpu_time = time.time() - start

        print(f"Matrix multiply {n}x{n}: CPU={cpu_time:.4f}s, GPU={gpu_time:.4f}s")

        # Results should match
        assert np.allclose(C_cpu, C_gpu, atol=1e-10)


if __name__ == "__main__":
    # Run tests directly
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    for test_class in [TestCGSolver, TestGPUFallback, TestQuantumOrchestrator,
                       TestBackendDetection, TestIntegration]:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)