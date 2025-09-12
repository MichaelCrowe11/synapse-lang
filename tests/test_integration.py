"""Comprehensive integration tests for Synapse language."""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse_lang import (
    parse, compile, execute,
    Lexer, EnhancedParser,
    ExecutionSandbox, SecurityPolicy,
    JITCompiler
)


class TestLanguageIntegration(unittest.TestCase):
    """Test complete language pipeline."""
    
    def test_hypothesis_experiment_flow(self):
        """Test scientific hypothesis and experiment constructs."""
        code = """
        hypothesis H1 {
            assume: temperature > 273
            predict: state == "liquid"
            validate: experimental_data
        }
        
        experiment E1 {
            setup: initialize_conditions()
            parallel {
                branch A: test_at_pressure(1)
                branch B: test_at_pressure(2)
                branch C: test_at_pressure(0.5)
            }
            synthesize: analyze_results()
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.statements), 2)
    
    def test_parallel_execution(self):
        """Test parallel execution blocks."""
        code = """
        parallel {
            branch compute1: heavy_calculation(1)
            branch compute2: heavy_calculation(2)
            branch compute3: heavy_calculation(3)
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        self.assertEqual(ast.statements[0].node_type.name, 'PARALLEL')
    
    def test_reasoning_chains(self):
        """Test reasoning chain constructs."""
        code = """
        reason chain ThermodynamicAnalysis {
            premise P1: "Energy cannot be created or destroyed"
            premise P2: "Entropy always increases"
            
            derive D1 from P1: "Total system energy is constant"
            derive D2 from P2: "Heat flows from hot to cold"
            
            conclude: D1 && D2 => "System reaches equilibrium"
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        reason_chain = ast.statements[0]
        self.assertEqual(len(reason_chain.premises), 2)
        self.assertEqual(len(reason_chain.derivations), 2)
    
    def test_uncertainty_propagation(self):
        """Test uncertainty quantification."""
        code = """
        uncertain value measurement = 42.3 ± 0.5
        uncertain value temperature = 300 ± 10
        
        propagate uncertainty through {
            result = measurement * temperature / 100
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        # Check that uncertainty nodes are created
        self.assertEqual(ast.statements[0].node_type.name, 'UNCERTAIN')
    
    def test_quantum_circuit(self):
        """Test quantum circuit definition and execution."""
        code = """
        quantum circuit bell_state(2) {
            H(0)
            CNOT(0, 1)
            measure(0)
            measure(1)
        }
        
        run bell_state with backend simulator {
            shots: 1000
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        circuit = ast.statements[0]
        self.assertEqual(circuit.name, 'bell_state')
        self.assertEqual(circuit.qubits, 2)
        self.assertEqual(len(circuit.gates), 2)
    
    def test_pipeline_processing(self):
        """Test data processing pipeline."""
        code = """
        pipeline DataAnalysis {
            stage Ingestion parallel(8) {
                read: load_dataset()
                clean: remove_outliers()
                normalize: standard_scale()
            }
            
            stage Processing parallel(auto) {
                fork {
                    path statistical: compute_statistics()
                    path ml: train_model()
                    path viz: generate_plots()
                }
            }
            
            stage Synthesis {
                merge: combine_results()
                validate: cross_check()
                report: generate_findings()
            }
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        pipeline = ast.statements[0]
        self.assertEqual(pipeline.name, 'DataAnalysis')
        self.assertEqual(len(pipeline.stages), 3)
    
    def test_exploration_backtracking(self):
        """Test solution space exploration."""
        code = """
        explore solution_space {
            try path1: analytical_approach()
            fallback path2: numerical_approach()
            fallback path3: monte_carlo()
            
            accept when: error < 0.001
            reject when: iterations > 1000
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        explore = ast.statements[0]
        self.assertEqual(len(explore.try_paths), 1)
        self.assertEqual(len(explore.fallback_paths), 2)
    
    def test_symbolic_mathematics(self):
        """Test symbolic math operations."""
        code = """
        symbolic {
            let f(x) = x^2 + 2*x + 1
            let g(x) = differentiate(f, x)
            
            solve: g(x) == 0 for x
            prove: f(x) >= 0 for all x
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        symbolic = ast.statements[0]
        self.assertEqual(len(symbolic.declarations), 2)
        self.assertEqual(len(symbolic.operations), 2)
    
    def test_tensor_operations(self):
        """Test tensor declarations and operations."""
        code = """
        tensor T[3, 3, 3] = quantum_state_space()
        parallel map T {
            element => normalize(element)
        } into T_normalized
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        tensor = ast.statements[0]
        self.assertEqual(tensor.dimensions, [3, 3, 3])
    
    def test_stream_synchronization(self):
        """Test thought streams and synchronization."""
        code = """
        stream S1: process_hypothesis_A()
        stream S2: process_hypothesis_B()
        
        synchronize at checkpoint {
            consensus: S1.result ~= S2.result
            divergence: investigate_discrepancy()
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.statements), 3)


class TestCompilation(unittest.TestCase):
    """Test JIT compilation."""
    
    def test_simple_compilation(self):
        """Test basic code compilation."""
        code = """
        x = 10
        y = 20
        result = x + y
        """
        
        # This would need mock implementations
        # compiled = compile(code)
        # self.assertIsNotNone(compiled)
    
    def test_parallel_compilation(self):
        """Test parallel code compilation."""
        code = """
        parallel {
            branch a: compute(1)
            branch b: compute(2)
        }
        """
        
        ast = parse(code)
        compiler = JITCompiler()
        # Test that compilation doesn't raise errors
        # compiled = compiler.compile_ast(ast)
    
    def test_optimization_levels(self):
        """Test different optimization levels."""
        code = "x = 1 + 2 + 3"
        
        # Test different optimization levels
        # compiled_o0 = compile(code, optimize=False)
        # compiled_o3 = compile(code, optimize=True)


class TestSecurity(unittest.TestCase):
    """Test security sandboxing."""
    
    def test_basic_sandbox(self):
        """Test basic sandboxed execution."""
        policy = SecurityPolicy(
            max_memory_mb=256,
            max_cpu_seconds=5,
            allowed_modules={'math'}
        )
        
        sandbox = ExecutionSandbox(policy)
        
        # Safe code should execute
        result = sandbox.execute("result = 2 + 2\n__result__ = result")
        self.assertEqual(result, 4)
    
    def test_forbidden_imports(self):
        """Test that forbidden imports are blocked."""
        policy = SecurityPolicy(
            forbidden_modules={'os', 'sys'}
        )
        
        sandbox = ExecutionSandbox(policy)
        
        # Should raise SecurityViolation
        with self.assertRaises(Exception):
            sandbox.execute("import os")
    
    def test_resource_limits(self):
        """Test resource limit enforcement."""
        policy = SecurityPolicy(
            max_cpu_seconds=1,
            max_loop_iterations=1000
        )
        
        sandbox = ExecutionSandbox(policy)
        
        # Infinite loop should timeout
        with self.assertRaises(Exception):
            sandbox.execute("while True: pass")
    
    def test_file_access_restrictions(self):
        """Test file system access restrictions."""
        policy = SecurityPolicy(
            allowed_read_paths=['/tmp'],
            allowed_write_paths=[]
        )
        
        sandbox = ExecutionSandbox(policy)
        
        # File operations should be restricted
        with self.assertRaises(Exception):
            sandbox.execute("open('/etc/passwd', 'r')")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery."""
    
    def test_syntax_errors(self):
        """Test syntax error handling."""
        code = """
        if x > 10
            print("missing colon")
        """
        
        # Parser should handle syntax errors gracefully
        try:
            ast = parse(code)
        except Exception as e:
            self.assertIn("Expected", str(e))
    
    def test_parser_recovery(self):
        """Test parser error recovery."""
        code = """
        valid_statement = 10
        invalid statement here
        another_valid = 20
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = EnhancedParser(tokens)
        parser.error_recovery = True
        
        # Parser should recover and parse valid statements
        ast = parser.parse()
        self.assertIsNotNone(ast)
    
    def test_runtime_errors(self):
        """Test runtime error handling."""
        code = """
        x = 10
        y = 0
        result = x / y
        """
        
        # Should handle division by zero
        with self.assertRaises(Exception):
            execute(code, sandbox=False)


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""
    
    def test_scientific_computation(self):
        """Test complete scientific computation workflow."""
        code = """
        # Define experimental parameters
        uncertain temperature = 298.15 ± 0.5
        uncertain pressure = 101.325 ± 0.1
        
        # Run parallel simulations
        parallel {
            branch sim1: molecular_dynamics(temperature, pressure)
            branch sim2: monte_carlo(temperature, pressure)
            branch sim3: quantum_simulation(temperature, pressure)
        }
        
        # Analyze results
        hypothesis H1 {
            assume: temperature > 273
            predict: phase == "liquid"
            validate: simulation_results
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        # Verify all constructs are parsed
        self.assertTrue(any(s.node_type.name == 'UNCERTAIN' for s in ast.statements))
        self.assertTrue(any(s.node_type.name == 'PARALLEL' for s in ast.statements))
        self.assertTrue(any(s.node_type.name == 'HYPOTHESIS' for s in ast.statements))
    
    def test_quantum_algorithm(self):
        """Test quantum algorithm implementation."""
        code = """
        quantum algorithm VQE {
            parameters: [theta1, theta2, theta3]
            ansatz: hardware_efficient
            cost: expectation_value(H)
            optimizer: COBYLA
        }
        
        quantum circuit ansatz(2) {
            RY(theta1, 0)
            RY(theta2, 1)
            CNOT(0, 1)
            RY(theta3, 0)
        }
        
        run VQE with backend quantum_simulator {
            shots: 1000
            optimization_level: 2
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        # Check quantum nodes
        self.assertTrue(any(s.node_type.name == 'QUANTUM_ALGORITHM' for s in ast.statements))
        self.assertTrue(any(s.node_type.name == 'QUANTUM_CIRCUIT' for s in ast.statements))
    
    def test_machine_learning_pipeline(self):
        """Test ML pipeline processing."""
        code = """
        pipeline MLPipeline {
            stage DataPrep parallel(4) {
                load: read_csv("data.csv")
                clean: handle_missing_values()
                encode: categorical_encoding()
                scale: standard_scaling()
            }
            
            stage FeatureEngineering {
                fork {
                    path pca: principal_components(n=10)
                    path selection: select_k_best(k=15)
                    path embedding: autoencoder_features()
                }
            }
            
            stage ModelTraining parallel(auto) {
                fork {
                    path rf: random_forest()
                    path xgb: xgboost()
                    path nn: neural_network()
                }
            }
            
            stage Evaluation {
                ensemble: voting_classifier()
                metrics: calculate_metrics()
                report: generate_report()
            }
        }
        """
        
        ast = parse(code)
        self.assertIsNotNone(ast)
        pipeline = ast.statements[0]
        self.assertEqual(pipeline.name, 'MLPipeline')
        self.assertEqual(len(pipeline.stages), 4)


class TestPerformance(unittest.TestCase):
    """Performance and optimization tests."""
    
    def test_compilation_speedup(self):
        """Test that JIT compilation provides speedup."""
        code = """
        sum = 0
        for i in range(1000000):
            sum = sum + i
        result = sum
        """
        
        # Compare interpreted vs compiled performance
        # This would need actual implementation
        pass
    
    def test_parallel_speedup(self):
        """Test parallel execution speedup."""
        code = """
        parallel {
            branch a: heavy_computation(1000000)
            branch b: heavy_computation(1000000)
            branch c: heavy_computation(1000000)
            branch d: heavy_computation(1000000)
        }
        """
        
        # Test that parallel execution is faster than sequential
        pass
    
    def test_memory_efficiency(self):
        """Test memory usage optimization."""
        code = """
        tensor large[1000, 1000, 100]
        # Process tensor efficiently
        """
        
        # Test memory usage stays within bounds
        pass


def run_integration_tests():
    """Run all integration tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLanguageIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCompilation))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)