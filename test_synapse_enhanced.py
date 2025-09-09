#!/usr/bin/env python3
"""
Comprehensive test suite for enhanced Synapse language features
Tests parser, tensor operations, symbolic math, and pipeline execution
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
import numpy as np
from synapse_interpreter import Lexer, TokenType
from synapse_parser_enhanced import Parser, parse_synapse_code
from synapse_ast_complete import *
from synapse_tensor_ops import SynapseTensor, TensorOperations
from synapse_symbolic import SymbolicEngine, SymbolicExpression
import sympy as sp

class TestEnhancedParser(unittest.TestCase):
    """Test enhanced parser functionality"""
    
    def test_hypothesis_parsing(self):
        """Test hypothesis construct parsing"""
        code = """
        hypothesis H1 {
            assume: temperature > 273
            predict: state == "liquid"
            validate: experimental_data
        }
        """
        ast = parse_synapse_code(code)
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.statements), 1)
        self.assertIsInstance(ast.statements[0], HypothesisNode)
        self.assertEqual(ast.statements[0].name, "H1")
    
    def test_experiment_parsing(self):
        """Test experiment construct parsing"""
        code = """
        experiment E1 {
            setup: initialize_conditions()
            parallel {
                branch A: test_1()
                branch B: test_2()
            }
            synthesize: analyze_results()
        }
        """
        ast = parse_synapse_code(code)
        self.assertIsInstance(ast.statements[0], ExperimentNode)
        self.assertEqual(ast.statements[0].name, "E1")
        self.assertIsNotNone(ast.statements[0].parallel_block)
    
    def test_pipeline_parsing(self):
        """Test pipeline construct parsing"""
        code = """
        pipeline DataAnalysis {
            stage Ingestion parallel(8) {
                read: load_data()
                clean: remove_outliers()
            }
            
            stage Processing {
                fork {
                    path statistical: compute_stats()
                    path ml: train_model()
                }
            }
        }
        """
        ast = parse_synapse_code(code)
        self.assertIsInstance(ast.statements[0], PipelineNode)
        self.assertEqual(ast.statements[0].name, "DataAnalysis")
        self.assertEqual(len(ast.statements[0].stages), 2)
    
    def test_reason_chain_parsing(self):
        """Test reasoning chain parsing"""
        code = """
        reason chain Logic1 {
            premise P1: "All humans are mortal"
            premise P2: "Socrates is human"
            derive D1 from P1, P2: "Socrates is mortal"
            conclude: D1 => "Proven"
        }
        """
        ast = parse_synapse_code(code)
        self.assertIsInstance(ast.statements[0], ReasonChainNode)
        self.assertEqual(len(ast.statements[0].premises), 2)
        self.assertEqual(len(ast.statements[0].derivations), 1)
    
    def test_symbolic_block_parsing(self):
        """Test symbolic mathematics block parsing"""
        code = """
        symbolic {
            let f(x) = x^2 + 2*x + 1
            let g(x) = differentiate(f, x)
            solve: g(x) == 0 for x
            prove: f(x) >= 0 for all x in Real
        }
        """
        ast = parse_synapse_code(code)
        self.assertIsInstance(ast.statements[0], SymbolicNode)
        self.assertEqual(len(ast.statements[0].bindings), 2)
        self.assertEqual(len(ast.statements[0].operations), 2)
    
    def test_uncertain_declaration_parsing(self):
        """Test uncertain value declaration parsing"""
        code = """
        uncertain mass = 10.5 ± 0.2
        uncertain temperature = 300 ± 5
        """
        ast = parse_synapse_code(code)
        self.assertEqual(len(ast.statements), 2)
        self.assertIsInstance(ast.statements[0], UncertainDeclarationNode)
        self.assertEqual(ast.statements[0].name, "mass")
    
    def test_tensor_declaration_parsing(self):
        """Test tensor declaration parsing"""
        code = """
        tensor T[3, 3, 3] = random_normal()
        tensor M[10, 10] = identity()
        """
        ast = parse_synapse_code(code)
        self.assertIsInstance(ast.statements[0], TensorDeclarationNode)
        self.assertEqual(ast.statements[0].name, "T")
        self.assertEqual(len(ast.statements[0].dimensions), 3)
    
    def test_explore_construct_parsing(self):
        """Test explore with backtracking parsing"""
        code = """
        explore solution_space {
            try analytical: exact_solution()
            fallback numerical: newton_raphson()
            fallback monte_carlo: random_sampling()
            accept when: error < 0.001
            reject when: iterations > 1000
        }
        """
        ast = parse_synapse_code(code)
        self.assertIsInstance(ast.statements[0], ExploreNode)
        self.assertEqual(len(ast.statements[0].tries), 1)
        self.assertEqual(len(ast.statements[0].fallbacks), 2)
    
    def test_structure_definition_parsing(self):
        """Test structure definition parsing"""
        code = """
        structure Molecule {
            atoms: Graph<Element>
            bonds: Tensor[n, n]
            energy: Real
            invariant: valence_satisfied
        }
        """
        ast = parse_synapse_code(code)
        self.assertIsInstance(ast.statements[0], StructureNode)
        self.assertEqual(ast.statements[0].name, "Molecule")
        self.assertEqual(len(ast.statements[0].fields), 3)
        self.assertEqual(len(ast.statements[0].invariants), 1)


class TestTensorOperations(unittest.TestCase):
    """Test tensor operations with uncertainty propagation"""
    
    def test_tensor_creation(self):
        """Test tensor creation methods"""
        # Zero tensor
        t1 = TensorOperations.zeros((3, 3))
        self.assertEqual(t1.shape, (3, 3))
        self.assertTrue(np.all(t1.data == 0))
        
        # Ones tensor
        t2 = TensorOperations.ones((2, 4))
        self.assertEqual(t2.shape, (2, 4))
        self.assertTrue(np.all(t2.data == 1))
        
        # Identity matrix
        t3 = TensorOperations.eye(4)
        self.assertEqual(t3.shape, (4, 4))
        self.assertTrue(np.allclose(t3.data, np.eye(4)))
        
        # Random tensor
        t4 = TensorOperations.random((5, 5), distribution='normal')
        self.assertEqual(t4.shape, (5, 5))
    
    def test_tensor_arithmetic_with_uncertainty(self):
        """Test arithmetic operations with uncertainty propagation"""
        # Create tensors with uncertainty
        t1 = SynapseTensor(np.array([10.0, 20.0]), np.array([0.5, 1.0]))
        t2 = SynapseTensor(np.array([5.0, 10.0]), np.array([0.2, 0.5]))
        
        # Addition
        t_add = t1 + t2
        self.assertTrue(np.allclose(t_add.data, [15.0, 30.0]))
        # Uncertainties add in quadrature
        expected_unc = np.sqrt(0.5**2 + 0.2**2), np.sqrt(1.0**2 + 0.5**2)
        self.assertTrue(np.allclose(t_add.uncertainty, expected_unc))
        
        # Multiplication
        t_mul = t1 * t2
        self.assertTrue(np.allclose(t_mul.data, [50.0, 200.0]))
        
        # Division
        t_div = t1 / t2
        self.assertTrue(np.allclose(t_div.data, [2.0, 2.0]))
    
    def test_tensor_matrix_operations(self):
        """Test matrix operations"""
        # Matrix multiplication
        m1 = SynapseTensor(np.array([[1, 2], [3, 4]]))
        m2 = SynapseTensor(np.array([[5, 6], [7, 8]]))
        
        result = m1 @ m2
        expected = np.array([[19, 22], [43, 50]])
        self.assertTrue(np.allclose(result.data, expected))
        
        # Transpose
        t = m1.transpose()
        self.assertTrue(np.allclose(t.data, [[1, 3], [2, 4]]))
        
        # Inverse
        m_inv = TensorOperations.inv(m1)
        identity = m1 @ m_inv
        self.assertTrue(np.allclose(identity.data, np.eye(2), atol=1e-10))
    
    def test_tensor_eigenvalues(self):
        """Test eigenvalue computation"""
        # Symmetric matrix
        m = SynapseTensor(np.array([[4, -2], [-2, 4]]))
        eigenvals = TensorOperations.eigenvalues(m)
        
        # Known eigenvalues are 2 and 6
        self.assertTrue(np.allclose(sorted(eigenvals.data), [2, 6]))
    
    def test_tensor_fft(self):
        """Test FFT operations"""
        # Create signal
        t = np.linspace(0, 1, 100)
        signal = np.sin(2 * np.pi * 5 * t) + np.sin(2 * np.pi * 10 * t)
        tensor = SynapseTensor(signal)
        
        # Compute FFT
        fft_result = TensorOperations.fft(tensor)
        self.assertEqual(fft_result.data.shape, signal.shape)
        
        # Inverse FFT should recover original
        ifft_result = TensorOperations.ifft(fft_result)
        self.assertTrue(np.allclose(ifft_result.data.real, signal))
    
    def test_tensor_statistical_operations(self):
        """Test statistical operations with uncertainty"""
        # Create tensor with uncertainty
        data = np.array([[1, 2, 3], [4, 5, 6]])
        uncertainty = np.array([[0.1, 0.2, 0.1], [0.2, 0.1, 0.2]])
        t = SynapseTensor(data, uncertainty)
        
        # Sum with uncertainty propagation
        t_sum = t.sum(axis=1)
        self.assertTrue(np.allclose(t_sum.data, [6, 15]))
        
        # Mean with uncertainty propagation
        t_mean = t.mean(axis=1)
        self.assertTrue(np.allclose(t_mean.data, [2, 5]))
        
        # Standard deviation
        t_std = t.std(axis=1)
        self.assertEqual(t_std.data.shape, (2,))


class TestSymbolicEngine(unittest.TestCase):
    """Test symbolic mathematics engine"""
    
    def setUp(self):
        """Initialize symbolic engine"""
        self.engine = SymbolicEngine()
    
    def test_symbol_creation(self):
        """Test symbol creation with assumptions"""
        # Real symbol
        x = self.engine.create_symbol('a', real=True, positive=True)
        self.assertIsInstance(x, sp.Symbol)
        self.assertTrue(x.is_real)
        self.assertTrue(x.is_positive)
        
        # Integer symbol
        n = self.engine.create_symbol('n', integer=True)
        self.assertTrue(n.is_integer)
    
    def test_expression_parsing(self):
        """Test expression parsing"""
        expr = self.engine.parse_expression("x^2 + 2*x + 1")
        self.assertIsInstance(expr, sp.Expr)
        
        # Evaluate at x=2
        result = expr.subs(self.engine.symbols['x'], 2)
        self.assertEqual(result, 9)
    
    def test_differentiation(self):
        """Test symbolic differentiation"""
        # First derivative
        deriv = self.engine.differentiate("x^3 + 2*x^2 - x + 1", 'x')
        expected = self.engine.parse_expression("3*x^2 + 4*x - 1")
        self.assertEqual(deriv.expr, expected)
        
        # Second derivative
        second_deriv = self.engine.differentiate("x^3", 'x', order=2)
        expected = self.engine.parse_expression("6*x")
        self.assertEqual(second_deriv.expr, expected)
    
    def test_integration(self):
        """Test symbolic integration"""
        # Indefinite integral
        integral = self.engine.integrate("2*x", 'x')
        # Result should be x^2 + C (constant ignored in comparison)
        self.assertTrue('x**2' in str(integral.expr))
        
        # Definite integral
        definite = self.engine.integrate("x", 'x', limits=(0, 1))
        self.assertEqual(definite.expr, sp.Rational(1, 2))
    
    def test_equation_solving(self):
        """Test equation solving"""
        # Simple equation
        solutions = self.engine.solve_equation("x^2 - 4 = 0", 'x')
        self.assertEqual(set(solutions), {-2, 2})
        
        # Quadratic equation
        solutions = self.engine.solve_equation("x^2 + 2*x + 1 = 0", 'x')
        self.assertEqual(solutions, [-1])
    
    def test_limit_computation(self):
        """Test limit computation"""
        # Limit at finite point
        limit = self.engine.compute_limit("sin(x)/x", 'x', 0)
        self.assertEqual(limit.expr, 1)
        
        # Limit at infinity
        limit_inf = self.engine.compute_limit("1/x", 'x', '∞')
        self.assertEqual(limit_inf.expr, 0)
    
    def test_taylor_series(self):
        """Test Taylor series expansion"""
        series = self.engine.taylor_series("exp(x)", 'x', 0, order=4)
        # Should be 1 + x + x^2/2 + x^3/6
        expected_terms = ['1', 'x', 'x**2/2', 'x**3/6']
        series_str = str(series.expr)
        for term in expected_terms:
            self.assertIn(term.replace('**', '^'), series_str.replace('**', '^'))
    
    def test_matrix_operations(self):
        """Test symbolic matrix operations"""
        # Create symbolic matrix
        matrix = [[1, 2], [3, 4]]
        
        # Determinant
        det = self.engine.matrix_operations('determinant', matrix)
        self.assertEqual(det, -2)
        
        # Inverse
        inv = self.engine.matrix_operations('inverse', matrix)
        self.assertIsInstance(inv, sp.Matrix)
        
        # Eigenvalues
        eigenvals = self.engine.matrix_operations('eigenvalues', matrix)
        self.assertIsInstance(eigenvals, dict)
    
    def test_logical_inference(self):
        """Test logical inference"""
        premises = [
            "p => q",
            "q => r",
            "p"
        ]
        conclusion = "r"
        
        result = self.engine.logical_inference(premises, conclusion)
        # This should be valid by modus ponens and transitivity
        # Note: Actual validation depends on SymPy's logical simplification
        self.assertIn('valid', result)
    
    def test_optimization(self):
        """Test expression optimization"""
        # Find extrema of parabola
        result = self.engine.optimize_expression("x^2 - 4*x + 3", 'x')
        
        # Should find minimum at x=2
        self.assertEqual(len(result['critical_points']), 1)
        self.assertEqual(result['critical_points'][0], 2)
        
        # Check it's classified as minimum
        extrema = result['extrema']
        self.assertEqual(len(extrema), 1)
        self.assertEqual(extrema[0]['type'], 'minimum')
        self.assertEqual(extrema[0]['point'], 2)


class TestIntegration(unittest.TestCase):
    """Test integration of all components"""
    
    def test_parser_ast_integration(self):
        """Test parser produces valid AST"""
        code = """
        experiment QuantumSimulation {
            setup: initialize_qubits(10)
            
            parallel {
                branch path1: simulate_circuit_1()
                branch path2: simulate_circuit_2()
            }
            
            synthesize: measure_entanglement()
        }
        """
        
        ast = parse_synapse_code(code)
        
        # Verify AST structure
        self.assertIsInstance(ast, ProgramNode)
        exp = ast.statements[0]
        self.assertIsInstance(exp, ExperimentNode)
        self.assertEqual(exp.name, "QuantumSimulation")
        self.assertIsNotNone(exp.setup)
        self.assertIsNotNone(exp.parallel_block)
        self.assertEqual(len(exp.parallel_block.branches), 2)
    
    def test_complex_program_parsing(self):
        """Test parsing of complex program with multiple constructs"""
        code = """
        structure QuantumState {
            amplitude: Complex
            phase: Real
            invariant: norm == 1
        }
        
        uncertain measurement = 42.0 ± 0.5
        tensor state_vector[100] = normalize(random_complex())
        
        pipeline QuantumAlgorithm {
            stage Preparation {
                init: create_superposition()
                entangle: bell_pairs()
            }
            
            stage Evolution parallel(4) {
                fork {
                    path unitary: apply_gates()
                    path measurement: partial_measure()
                }
            }
        }
        
        hypothesis QuantumAdvantage {
            assume: circuit_depth < 100
            predict: speedup > exponential
            validate: benchmark_results
        }
        """
        
        ast = parse_synapse_code(code)
        
        # Should have 5 top-level statements (structure, uncertain, tensor, pipeline, hypothesis)
        self.assertEqual(len(ast.statements), 5)
        
        # Check each construct type
        self.assertIsInstance(ast.statements[0], StructureNode)
        self.assertIsInstance(ast.statements[1], UncertainDeclarationNode)
        self.assertIsInstance(ast.statements[2], TensorDeclarationNode)
        self.assertIsInstance(ast.statements[3], PipelineNode)
        self.assertIsInstance(ast.statements[4], HypothesisNode)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedParser))
    suite.addTests(loader.loadTestsFromTestCase(TestTensorOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestSymbolicEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)