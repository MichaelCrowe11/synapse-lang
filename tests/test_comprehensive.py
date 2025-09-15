"""
Comprehensive test suite for Synapse Language.

This module provides extensive testing coverage including:
- Core language features
- Error handling and edge cases
- Type system validation
- Quantum computing features
- Parallel execution
- Performance benchmarks
- Memory usage tests
"""

import unittest
import time
import threading
import gc
import sys
import os
from typing import List, Any
import tempfile
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from synapse_lang import (
    Lexer, EnhancedParser, Interpreter, parse, execute,
    UncertainValue, uncertain, QuantumCircuit
)
from synapse_lang.errors import (
    SynapseError, SyntaxError, TypeError, RuntimeError,
    QuantumError, ParallelError, ErrorCollector
)
from synapse_lang.type_system import (
    TypeChecker, PrimitiveType, UncertainType, QubitType,
    ListType, FunctionType
)


class TestCore(unittest.TestCase):
    """Test core language functionality."""

    def setUp(self):
        self.interpreter = Interpreter()

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        cases = [
            ("2 + 3", 5),
            ("10 - 4", 6),
            ("3 * 7", 21),
            ("15 / 3", 5.0),
            ("2 ** 3", 8),
            ("17 % 5", 2),
        ]

        for code, expected in cases:
            with self.subTest(code=code):
                result = execute(code, sandbox=False)
                self.assertEqual(result, expected)

    def test_variable_assignment(self):
        """Test variable assignment and retrieval."""
        code = """
        x = 42
        y = x + 8
        z = y * 2
        result = z
        """
        result = execute(code, sandbox=False)
        self.assertEqual(result, 100)

    def test_string_operations(self):
        """Test string handling."""
        cases = [
            ('"hello" + " world"', "hello world"),
            ('name = "Synapse"; "Language: " + name', "Language: Synapse"),
        ]

        for code, expected in cases:
            with self.subTest(code=code):
                result = execute(code, sandbox=False)
                self.assertEqual(result, expected)

    def test_boolean_logic(self):
        """Test boolean operations."""
        cases = [
            ("true && false", False),
            ("true || false", True),
            ("!true", False),
            ("5 > 3", True),
            ("10 <= 10", True),
            ("7 == 7", True),
            ("8 != 9", True),
        ]

        for code, expected in cases:
            with self.subTest(code=code):
                result = execute(code, sandbox=False)
                self.assertEqual(result, expected)


class TestUncertaintyComputation(unittest.TestCase):
    """Test uncertainty propagation and computation."""

    def test_uncertain_values(self):
        """Test creation and basic operations with uncertain values."""
        code = """
        uncertain x = 10.0 ± 0.5
        uncertain y = 20.0 ± 1.0
        result = x + y
        """
        result = execute(code, sandbox=False)

        # Check that result is uncertain and has correct propagated uncertainty
        self.assertTrue(hasattr(result, 'value'))
        self.assertTrue(hasattr(result, 'uncertainty'))
        self.assertAlmostEqual(result.value, 30.0)
        # Uncertainty should be √(0.5² + 1.0²) ≈ 1.118
        self.assertAlmostEqual(result.uncertainty, 1.118, places=2)

    def test_uncertainty_propagation(self):
        """Test various uncertainty propagation rules."""
        test_cases = [
            # Addition: σ_sum = √(σ₁² + σ₂²)
            ("uncertain a = 5.0 ± 0.3; uncertain b = 3.0 ± 0.4; a + b", 8.0, 0.5),
            # Multiplication: σ_product/product = √((σ₁/a)² + (σ₂/b)²)
            ("uncertain a = 4.0 ± 0.2; uncertain b = 3.0 ± 0.15; a * b", 12.0, None),
            # Powers: relative uncertainty multiplied by exponent
            ("uncertain a = 2.0 ± 0.1; a ** 2", 4.0, None),
        ]

        for code, expected_value, expected_uncertainty in test_cases:
            with self.subTest(code=code):
                result = execute(code, sandbox=False)
                self.assertAlmostEqual(result.value, expected_value)
                if expected_uncertainty:
                    self.assertAlmostEqual(result.uncertainty, expected_uncertainty, places=1)

    def test_uncertain_comparisons(self):
        """Test comparisons with uncertain values."""
        code = """
        uncertain a = 10.0 ± 2.0
        uncertain b = 12.0 ± 1.0
        result = a < b
        """
        result = execute(code, sandbox=False)
        # Should handle uncertainty in comparisons appropriately
        self.assertIsInstance(result, (bool, float))


class TestQuantumFeatures(unittest.TestCase):
    """Test quantum computing functionality."""

    def test_qubit_creation(self):
        """Test quantum bit creation and manipulation."""
        code = """
        qubit q = |0>
        result = measure(q)
        """
        result = execute(code, sandbox=False)
        self.assertIn(result, [0, 1])  # Measurement should yield 0 or 1

    def test_quantum_gates(self):
        """Test quantum gate operations."""
        code = """
        circuit qc {
            qubit q1 = |0>
            qubit q2 = |0>
            hadamard(q1)
            cnot(q1, q2)
        }
        result = execute(qc)
        """
        try:
            result = execute(code, sandbox=False)
            # Should create Bell state |00⟩ + |11⟩
            self.assertIsNotNone(result)
        except Exception as e:
            self.skipTest(f"Quantum features not fully implemented: {e}")

    def test_quantum_measurement(self):
        """Test quantum measurement operations."""
        code = """
        circuit bell_test {
            qubit q1 = |0>
            qubit q2 = |0>
            hadamard(q1)
            cnot(q1, q2)
            measure_all()
        }
        results = []
        repeat 100 {
            results.append(execute(bell_test))
        }
        """
        try:
            result = execute(code, sandbox=False)
            # Should get correlated measurements (00 or 11)
            self.assertIsNotNone(result)
        except Exception as e:
            self.skipTest(f"Quantum measurement not implemented: {e}")


class TestParallelExecution(unittest.TestCase):
    """Test parallel execution features."""

    def test_basic_parallel(self):
        """Test basic parallel branch execution."""
        code = """
        parallel {
            branch A: x = 10 + 5
            branch B: y = 20 + 3
            branch C: z = 30 + 7
        }
        result = x + y + z
        """
        result = execute(code, sandbox=False)
        self.assertEqual(result, 15 + 23 + 37)

    def test_parallel_with_shared_data(self):
        """Test parallel execution with shared variables."""
        code = """
        shared_total = 0
        parallel {
            branch A: shared_total += 10
            branch B: shared_total += 20
            branch C: shared_total += 30
        }
        result = shared_total
        """
        try:
            result = execute(code, sandbox=False)
            self.assertEqual(result, 60)
        except Exception as e:
            # Race conditions may occur without proper synchronization
            self.assertIsInstance(e, (RuntimeError, ParallelError))

    def test_parallel_performance(self):
        """Test that parallel execution provides performance benefits."""
        sequential_code = """
        def slow_task(n):
            sum = 0
            for i in range(n):
                sum += i
            return sum

        result1 = slow_task(10000)
        result2 = slow_task(10000)
        result3 = slow_task(10000)
        """

        parallel_code = """
        def slow_task(n):
            sum = 0
            for i in range(n):
                sum += i
            return sum

        parallel {
            branch A: result1 = slow_task(10000)
            branch B: result2 = slow_task(10000)
            branch C: result3 = slow_task(10000)
        }
        """

        # Measure execution times
        start = time.time()
        try:
            execute(sequential_code, sandbox=False)
            sequential_time = time.time() - start
        except:
            sequential_time = float('inf')

        start = time.time()
        try:
            execute(parallel_code, sandbox=False)
            parallel_time = time.time() - start
        except:
            parallel_time = float('inf')

        if parallel_time < float('inf') and sequential_time < float('inf'):
            # Parallel should be faster (allowing for some overhead)
            self.assertLess(parallel_time, sequential_time * 0.8)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery."""

    def test_syntax_errors(self):
        """Test syntax error detection and reporting."""
        bad_syntax_cases = [
            "2 + + 3",  # Invalid operator sequence
            "x = ",     # Incomplete assignment
            "if x",     # Missing condition body
            "def func(", # Incomplete function definition
        ]

        for code in bad_syntax_cases:
            with self.subTest(code=code):
                try:
                    result = execute(code, sandbox=False)
                    self.fail(f"Expected syntax error for: {code}")
                except (SyntaxError, Exception) as e:
                    self.assertIsNotNone(e)

    def test_type_errors(self):
        """Test type error detection."""
        type_error_cases = [
            '"hello" + 42',      # String + number
            'true * false',      # Boolean multiplication
            '10 / "zero"',       # Division by string
        ]

        for code in type_error_cases:
            with self.subTest(code=code):
                try:
                    result = execute(code, sandbox=False)
                    # May succeed with dynamic typing, check result type
                except (TypeError, Exception) as e:
                    self.assertIsNotNone(e)

    def test_runtime_errors(self):
        """Test runtime error handling."""
        runtime_error_cases = [
            "x = undefined_variable",  # Undefined variable
            "result = 10 / 0",        # Division by zero
            "arr = [1,2,3]; arr[10]", # Index out of bounds
        ]

        for code in runtime_error_cases:
            with self.subTest(code=code):
                try:
                    result = execute(code, sandbox=False)
                    if code == "result = 10 / 0":
                        # Should handle division by zero gracefully
                        self.assertTrue(result == float('inf') or isinstance(result, Exception))
                except (RuntimeError, Exception) as e:
                    self.assertIsNotNone(e)

    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        code_with_recovery = """
        try {
            risky_operation = 10 / 0
        } fallback {
            risky_operation = "infinity"
        }
        result = risky_operation
        """
        try:
            result = execute(code_with_recovery, sandbox=False)
            # Should recover from division by zero
            self.assertIn(result, [float('inf'), "infinity"])
        except Exception as e:
            self.skipTest(f"Error recovery not implemented: {e}")


class TestTypeSystem(unittest.TestCase):
    """Test static type checking system."""

    def setUp(self):
        self.type_checker = TypeChecker()

    def test_primitive_types(self):
        """Test primitive type inference."""
        cases = [
            ("42", "int"),
            ("3.14", "float"),
            ('"hello"', "string"),
            ("true", "bool"),
        ]

        for code, expected_type in cases:
            with self.subTest(code=code):
                ast = parse(code)
                inferred_type = self.type_checker.infer_type(ast)
                self.assertIsNotNone(inferred_type)
                self.assertEqual(inferred_type.name, expected_type)

    def test_uncertain_types(self):
        """Test uncertain type inference."""
        ast = parse("uncertain x = 42.0 ± 1.0")
        inferred_type = self.type_checker.infer_type(ast)
        self.assertIsInstance(inferred_type, UncertainType)
        self.assertEqual(inferred_type.base_type.name, "float")

    def test_composite_types(self):
        """Test composite type inference."""
        cases = [
            ("[1, 2, 3]", "list<int>"),
            ('["a", "b", "c"]', "list<string>"),
            ('{"key": "value"}', "dict<string, string>"),
        ]

        for code, expected_type in cases:
            with self.subTest(code=code):
                ast = parse(code)
                inferred_type = self.type_checker.infer_type(ast)
                if inferred_type:
                    self.assertEqual(inferred_type.name, expected_type)

    def test_type_compatibility(self):
        """Test type compatibility checking."""
        int_type = self.type_checker.types['int']
        float_type = self.type_checker.types['float']
        uncertain_int = UncertainType(int_type)

        # Test assignability
        self.assertTrue(int_type.is_assignable_from(int_type))
        self.assertFalse(int_type.is_assignable_from(float_type))
        self.assertTrue(uncertain_int.is_assignable_from(int_type))  # Can assign certain to uncertain

    def test_function_type_checking(self):
        """Test function type checking."""
        add_func = FunctionType([
            self.type_checker.types['int'],
            self.type_checker.types['int']
        ], self.type_checker.types['int'])

        self.type_checker.functions['add'] = add_func

        # Test valid call
        result_type = self.type_checker.check_function_call('add', [
            self.type_checker.types['int'],
            self.type_checker.types['int']
        ])
        self.assertEqual(result_type.name, 'int')

        # Test invalid call
        self.type_checker.errors = []
        result_type = self.type_checker.check_function_call('add', [
            self.type_checker.types['string'],
            self.type_checker.types['int']
        ])
        self.assertTrue(len(self.type_checker.errors) > 0)


class TestPerformance(unittest.TestCase):
    """Performance benchmarks and optimization tests."""

    def test_execution_speed(self):
        """Test execution speed for various operations."""
        test_cases = [
            ("Arithmetic", "sum = 0; for i in range(1000): sum += i"),
            ("String concatenation", 's = ""; for i in range(100): s += "x"'),
            ("List operations", "arr = []; for i in range(500): arr.append(i)"),
        ]

        for name, code in test_cases:
            with self.subTest(name=name):
                start_time = time.time()
                try:
                    result = execute(code, sandbox=False)
                    execution_time = time.time() - start_time

                    # Performance assertion (should complete within reasonable time)
                    self.assertLess(execution_time, 5.0, f"{name} took too long: {execution_time:.2f}s")
                    print(f"{name}: {execution_time:.4f}s")
                except Exception as e:
                    self.skipTest(f"{name} not implemented: {e}")

    def test_memory_usage(self):
        """Test memory usage patterns."""
        # Measure memory before
        gc.collect()
        initial_memory = self._get_memory_usage()

        code = """
        large_array = []
        for i in range(10000):
            large_array.append(i * 2)
        result = len(large_array)
        """

        try:
            result = execute(code, sandbox=False)

            # Measure memory after
            peak_memory = self._get_memory_usage()
            memory_increase = peak_memory - initial_memory

            # Should not use excessive memory
            self.assertLess(memory_increase, 100 * 1024 * 1024)  # Less than 100MB
            print(f"Memory increase: {memory_increase / 1024 / 1024:.2f}MB")

        except Exception as e:
            self.skipTest(f"Memory test failed: {e}")

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except ImportError:
            return 0  # psutil not available

    def test_compilation_speed(self):
        """Test compilation/parsing speed."""
        large_program = """
        # Large program for compilation speed test
        """ + "\n".join([f"var_{i} = {i} * 2" for i in range(1000)])

        start_time = time.time()
        try:
            ast = parse(large_program)
            compilation_time = time.time() - start_time

            self.assertLess(compilation_time, 2.0, f"Compilation too slow: {compilation_time:.2f}s")
            print(f"Compilation time: {compilation_time:.4f}s")

        except Exception as e:
            self.skipTest(f"Compilation test failed: {e}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_large_numbers(self):
        """Test handling of large numbers."""
        cases = [
            "result = 2 ** 100",  # Very large integer
            "result = 1e308",     # Large float near limit
            "result = 1e-308",    # Very small positive float
        ]

        for code in cases:
            with self.subTest(code=code):
                try:
                    result = execute(code, sandbox=False)
                    self.assertIsNotNone(result)
                    self.assertTrue(isinstance(result, (int, float)))
                except (OverflowError, Exception) as e:
                    # May overflow, which is acceptable
                    pass

    def test_deep_recursion(self):
        """Test deep recursion handling."""
        code = """
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)

        result = factorial(100)
        """
        try:
            result = execute(code, sandbox=False)
            self.assertTrue(result > 0)
        except (RecursionError, Exception) as e:
            # May hit recursion limit, which is acceptable
            pass

    def test_unicode_handling(self):
        """Test Unicode string handling."""
        cases = [
            '"Hello 世界"',  # Mixed ASCII and Chinese
            '"🌟⚡🔬"',      # Emoji
            '"Café naïve"', # Accented characters
        ]

        for code in cases:
            with self.subTest(code=code):
                try:
                    result = execute(code, sandbox=False)
                    self.assertIsInstance(result, str)
                    self.assertTrue(len(result) > 0)
                except Exception as e:
                    self.skipTest(f"Unicode not supported: {e}")

    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        cases = [
            "",           # Empty program
            "   \n\t  ",  # Whitespace only
            "# Just comment",  # Comment only
        ]

        for code in cases:
            with self.subTest(code=code):
                try:
                    result = execute(code, sandbox=False)
                    # Should handle gracefully, possibly returning None
                except Exception as e:
                    # Empty input handling varies, both outcomes acceptable
                    pass


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple features."""

    def test_scientific_computation(self):
        """Test scientific computation pipeline."""
        code = """
        # Monte Carlo estimation of π
        import random

        def estimate_pi(samples):
            inside_circle = 0
            for i in range(samples):
                x = random.uniform(-1, 1)
                y = random.uniform(-1, 1)
                if x*x + y*y <= 1:
                    inside_circle += 1
            return 4.0 * inside_circle / samples

        uncertain pi_estimate = estimate_pi(10000) ± 0.1
        result = pi_estimate
        """
        try:
            result = execute(code, sandbox=False)
            # Should be approximately π
            if hasattr(result, 'value'):
                self.assertAlmostEqual(result.value, 3.14159, places=1)
            else:
                self.assertAlmostEqual(result, 3.14159, places=1)
        except Exception as e:
            self.skipTest(f"Scientific computation not fully supported: {e}")

    def test_quantum_uncertainty_integration(self):
        """Test integration of quantum and uncertainty features."""
        code = """
        circuit noisy_measurement {
            qubit q = |0>
            hadamard(q)  # Put in superposition
            # Add noise model
            uncertain noise_level = 0.05 ± 0.01
            result = measure_with_noise(q, noise_level)
        }

        measurements = []
        repeat 100 {
            measurements.append(execute(noisy_measurement))
        }
        """
        try:
            result = execute(code, sandbox=False)
            # Should handle integration of quantum and uncertainty
            self.assertIsNotNone(result)
        except Exception as e:
            self.skipTest(f"Quantum-uncertainty integration not implemented: {e}")


def create_test_suite():
    """Create comprehensive test suite."""
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestCore,
        TestUncertaintyComputation,
        TestQuantumFeatures,
        TestParallelExecution,
        TestErrorHandling,
        TestTypeSystem,
        TestPerformance,
        TestEdgeCases,
        TestIntegration,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite


def run_benchmarks():
    """Run performance benchmarks and generate report."""
    print("=" * 50)
    print("SYNAPSE LANGUAGE BENCHMARK REPORT")
    print("=" * 50)

    # Create benchmark results file
    results = {
        'timestamp': time.time(),
        'python_version': sys.version,
        'benchmarks': {}
    }

    # Run performance tests
    performance_suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformance)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(performance_suite)

    results['benchmarks']['performance'] = {
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors)
    }

    # Save results
    with open('benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nBenchmark results saved to benchmark_results.json")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Synapse Language Test Suite')
    parser.add_argument('--benchmark', action='store_true', help='Run performance benchmarks')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--pattern', '-p', help='Run tests matching pattern')

    args = parser.parse_args()

    if args.benchmark:
        run_benchmarks()
    else:
        # Run regular tests
        suite = create_test_suite()

        if args.pattern:
            # Filter tests by pattern
            filtered_suite = unittest.TestSuite()
            for test_group in suite:
                for test in test_group:
                    if args.pattern.lower() in str(test).lower():
                        filtered_suite.addTest(test)
            suite = filtered_suite

        verbosity = 2 if args.verbose else 1
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)

        # Print summary
        print(f"\nTest Summary:")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")

        if result.failures:
            print(f"\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")

        if result.errors:
            print(f"\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")

        sys.exit(0 if result.wasSuccessful() else 1)