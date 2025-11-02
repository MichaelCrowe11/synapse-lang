#!/usr/bin/env python3
"""
Demonstration of Synapse Backend Infrastructure
Shows CG solver, GPU operations, and quantum simulation capabilities
"""
import os
import sys

import numpy as np

# Add synapse_lang to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synapse_lang.backends import auto, cg_solve, get_backend_info, gpu_matmul, vqe_minimize
from synapse_lang.backends.quant_orchestrator import EXAMPLE_HAMILTONIANS, VQEProblem


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def demo_backend_detection():
    """Demonstrate backend auto-detection"""
    print_header("Backend Detection and Configuration")

    # Auto-detect best backend
    detected = auto()
    print(f"✓ Auto-detected backend: {detected}")

    # Get detailed backend info
    info = get_backend_info()
    print("\n📊 Available backends:")
    for backend, available in info["available"].items():
        status = "✅" if available else "❌"
        print(f"  {status} {backend}")

    if "versions" in info:
        print("\n📦 Package versions:")
        for package, version in info["versions"].items():
            print(f"  • {package}: {version}")


def demo_cg_solver():
    """Demonstrate Conjugate Gradient solver"""
    print_header("Conjugate Gradient Solver")

    # Create a symmetric positive-definite system
    n = 50
    print(f"🔧 Creating {n}x{n} SPD system...")

    # Generate SPD matrix
    Q = np.random.randn(n, n)
    A = Q.T @ Q + np.eye(n) * 0.1  # Ensure positive definite
    b = np.random.randn(n)

    print("📐 Solving Ax = b using Conjugate Gradient...")

    # Solve using CG
    x = cg_solve(A, b, tol=1e-8)

    # Verify solution
    residual = np.linalg.norm(A @ x - b)
    print("✓ Solution found!")
    print(f"  • Residual norm: {residual:.2e}")
    print(f"  • Solution norm: {np.linalg.norm(x):.4f}")

    # Compare with direct solver
    x_direct = np.linalg.solve(A, b)
    diff = np.linalg.norm(x - x_direct)
    print(f"  • Difference from direct solve: {diff:.2e}")


def demo_gpu_operations():
    """Demonstrate GPU-accelerated operations"""
    print_header("GPU/CPU Matrix Operations")

    sizes = [100, 500, 1000]

    for n in sizes:
        print(f"\n📊 Matrix size: {n}x{n}")

        # Create random matrices
        A = np.random.randn(n, n)
        B = np.random.randn(n, n)

        # Matrix multiplication
        import time
        start = time.time()
        C = gpu_matmul(A, B)
        elapsed = time.time() - start

        print(f"  • Matrix multiply time: {elapsed:.4f}s")
        print(f"  • Result shape: {C.shape}")
        print(f"  • Result norm: {np.linalg.norm(C):.4f}")


def demo_quantum_vqe():
    """Demonstrate Variational Quantum Eigensolver"""
    print_header("Variational Quantum Eigensolver (VQE)")

    print("\n🔬 Testing on molecular Hamiltonians:")

    for name, hamiltonian in EXAMPLE_HAMILTONIANS.items():
        print(f"\n📌 {name.upper()} Hamiltonian ({hamiltonian.shape[0]}x{hamiltonian.shape[0]})")

        # Create VQE problem
        problem = VQEProblem(hamiltonian)
        print(f"  • Number of qubits: {problem.n_qubits}")
        print(f"  • Number of parameters: {problem.n_params}")

        # Get exact ground state energy
        eigenvalues = np.linalg.eigvalsh(hamiltonian)
        exact_ground = eigenvalues[0]
        print(f"  • Exact ground state energy: {exact_ground:.6f}")

        # Run VQE optimization
        print("  • Running VQE optimization...")
        initial_params = problem.random_initial_params(seed=42)
        result = problem.solve(initial_params, maxiter=20)

        print(f"  • Optimized energy: {result['fun']:.6f}")
        print(f"  • Energy error: {abs(result['fun'] - exact_ground):.6f}")
        print(f"  • Optimization iterations: {result['nit']}")
        print(f"  • Success: {result['success']}")


def demo_integrated_workflow():
    """Demonstrate an integrated scientific computing workflow"""
    print_header("Integrated Scientific Workflow")

    print("\n🔬 Simulating quantum-inspired optimization problem:")

    # Step 1: Generate problem data
    n = 10
    print(f"\n1️⃣ Generating {n}-dimensional optimization problem...")
    Q = np.random.randn(n, n)
    H = Q.T @ Q  # Quadratic form (positive definite)

    # Step 2: Solve linear system as preprocessing
    print("\n2️⃣ Preprocessing with linear solver...")
    b = np.ones(n)
    x_init = cg_solve(H, b, tol=1e-6)
    print(f"   Initial solution norm: {np.linalg.norm(x_init):.4f}")

    # Step 3: Reduce dimension using eigendecomposition
    print("\n3️⃣ Dimension reduction via eigendecomposition...")
    from synapse_lang.backends.gpu_fallback import eigh
    eigenvalues, eigenvectors = eigh(H)

    # Keep top 4 eigenvectors for quantum simulation
    n_qubits = 2
    reduced_dim = 2**n_qubits
    V = eigenvectors[:, :reduced_dim]
    H_reduced = V.T @ H @ V
    print(f"   Reduced from {n}x{n} to {reduced_dim}x{reduced_dim}")

    # Step 4: Quantum optimization on reduced problem
    print("\n4️⃣ Quantum optimization on reduced problem...")
    problem = VQEProblem(H_reduced, n_qubits)
    initial = problem.random_initial_params(seed=42)

    result = vqe_minimize(initial, H_reduced, maxiter=10)
    print(f"   Optimized energy: {result['fun']:.6f}")

    # Step 5: Map back to original space
    print("\n5️⃣ Mapping solution back to original space...")
    # This is simplified - in practice would involve more sophisticated mapping
    final_energy = result["fun"] * n / reduced_dim
    print(f"   Final objective value: {final_energy:.6f}")

    print("\n✅ Workflow completed successfully!")


def demo_performance_comparison():
    """Compare performance of different backend operations"""
    print_header("Performance Comparison")

    import time

    sizes = [50, 100, 200]

    print("\n📊 Comparing solver performance:")
    print("\nSize | Direct (NumPy) | CG Solver | Speedup")
    print("-" * 50)

    for n in sizes:
        # Generate SPD system
        Q = np.random.randn(n, n)
        A = Q.T @ Q + np.eye(n)
        b = np.random.randn(n)

        # Direct solve
        start = time.time()
        x_direct = np.linalg.solve(A, b)
        direct_time = time.time() - start

        # CG solve
        start = time.time()
        x_cg = cg_solve(A, b)
        cg_time = time.time() - start

        speedup = direct_time / cg_time
        print(f"{n:4d} | {direct_time:12.6f}s | {cg_time:9.6f}s | {speedup:7.2f}x")

        # Verify accuracy
        assert np.allclose(x_direct, x_cg, atol=1e-6)


def main():
    """Run all demonstrations"""
    print("\n" + "🚀 SYNAPSE BACKEND INFRASTRUCTURE DEMO 🚀".center(60))
    print("="*60)

    try:
        # Run demonstrations
        demo_backend_detection()
        demo_cg_solver()
        demo_gpu_operations()
        demo_quantum_vqe()
        demo_integrated_workflow()
        demo_performance_comparison()

        print("\n" + "="*60)
        print("✅ All demonstrations completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
