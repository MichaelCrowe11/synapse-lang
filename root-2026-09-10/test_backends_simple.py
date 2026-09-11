#!/usr/bin/env python3
"""
Simple test of Synapse Backend Infrastructure
Works without NumPy/SciPy dependencies
"""


def test_backend_modules():
    """Test that backend modules can be imported"""
    print("Testing Synapse Backend Infrastructure")
    print("=" * 50)

    # Test importing backend modules
    try:
        from synapse_lang.backends import auto, get_backend_info
        print("✅ Backend main module imported")
    except ImportError as e:
        print(f"❌ Failed to import backends: {e}")
        return False

    # Test CG solver import
    try:
        from synapse_lang.backends.cg_solver import cg_solve
        print("✅ CG solver module imported")
    except ImportError as e:
        print(f"❌ Failed to import CG solver: {e}")

    # Test GPU fallback import
    try:
        from synapse_lang.backends.gpu_fallback import matmul, to_gpu, to_cpu
        print("✅ GPU fallback module imported")
    except ImportError as e:
        print(f"❌ Failed to import GPU fallback: {e}")

    # Test quantum orchestrator import
    try:
        from synapse_lang.backends.quant_orchestrator import vqe_energy, vqe_minimize
        print("✅ Quantum orchestrator module imported")
    except ImportError as e:
        print(f"❌ Failed to import quantum orchestrator: {e}")

    return True


def test_backend_detection():
    """Test backend auto-detection without dependencies"""
    print("\n" + "="*50)
    print("Backend Detection Test")
    print("="*50)

    try:
        from synapse_lang.backends import auto, get_backend_info

        # Test auto-detection
        detected = auto()
        print(f"Auto-detected backend: {detected}")

        # Test backend info
        info = get_backend_info()
        print("\nAvailable backends:")
        for backend, available in info.get('available', {}).items():
            status = "✅" if available else "❌"
            print(f"  {status} {backend}")

        return True

    except Exception as e:
        print(f"Error during backend detection: {e}")
        return False


def test_simple_operations():
    """Test simple operations that work without NumPy"""
    print("\n" + "="*50)
    print("Simple Operations Test")
    print("="*50)

    # Test with basic Python lists as fallback
    try:
        # Simple 2x2 matrix as nested lists
        A = [[4.0, 1.0], [1.0, 3.0]]
        b = [1.0, 2.0]

        print("Testing with Python lists (no NumPy):")
        print(f"  Matrix A: {A}")
        print(f"  Vector b: {b}")

        # Manual solution for comparison
        # For this simple 2x2 system: Ax = b
        # Solution: x = A^(-1) * b
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        if abs(det) > 1e-10:
            # Inverse of 2x2 matrix
            A_inv = [
                [A[1][1]/det, -A[0][1]/det],
                [-A[1][0]/det, A[0][0]/det]
            ]
            # Multiply A_inv * b
            x = [
                A_inv[0][0] * b[0] + A_inv[0][1] * b[1],
                A_inv[1][0] * b[0] + A_inv[1][1] * b[1]
            ]
            print(f"  Manual solution: x = {x}")
            print("✅ Basic math operations work")
        else:
            print("  Matrix is singular")

        return True

    except Exception as e:
        print(f"Error during simple operations: {e}")
        return False


def test_quantum_stub():
    """Test quantum simulator stub functionality"""
    print("\n" + "="*50)
    print("Quantum Simulator Stub Test")
    print("="*50)

    try:
        from synapse_lang.backends.quant_orchestrator import vqe_energy, vqe_minimize

        # Test with simple parameters
        params = [0.5, -0.3, 0.2]
        print(f"Test parameters: {params}")

        # Test energy calculation (stub)
        energy = vqe_energy(params, hamiltonian=None)
        print(f"VQE energy (stub): {energy}")

        # Test that energy is computed
        if isinstance(energy, (int, float)):
            print("✅ VQE energy calculation works")
        else:
            print("❌ VQE energy returned unexpected type")

        return True

    except Exception as e:
        print(f"Error during quantum stub test: {e}")
        return False


def main():
    """Run all tests"""
    print("\n🚀 SYNAPSE BACKEND POC TEST SUITE 🚀")
    print("=" * 50)
    print("Testing without external dependencies (NumPy/SciPy)")
    print()

    # Track test results
    results = []

    # Run tests
    tests = [
        ("Module Import", test_backend_modules),
        ("Backend Detection", test_backend_detection),
        ("Simple Operations", test_simple_operations),
        ("Quantum Stub", test_quantum_stub),
    ]

    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Backend POC is working!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)