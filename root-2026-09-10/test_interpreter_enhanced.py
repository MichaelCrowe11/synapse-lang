#!/usr/bin/env python3
"""
Test suite for the enhanced Synapse interpreter
Tests execution of AST nodes and runtime behavior
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest

import numpy as np

from synapse_interpreter import UncertainValue
from synapse_interpreter_enhanced import SynapseInterpreterEnhanced
from synapse_tensor_ops import SynapseTensor


class TestEnhancedInterpreter(unittest.TestCase):
    """Test enhanced interpreter execution"""

    def setUp(self):
        """Set up test interpreter"""
        self.interpreter = SynapseInterpreterEnhanced()

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations"""
        code = """
        x = 10
        y = 20
        z = x + y * 2
        """

        self.interpreter.execute(code)
        self.assertEqual(self.interpreter.current_context.get("x"), 10)
        self.assertEqual(self.interpreter.current_context.get("y"), 20)
        self.assertEqual(self.interpreter.current_context.get("z"), 50)

    def test_uncertain_values(self):
        """Test uncertain value operations"""
        code = """
        uncertain mass = 10.5 ± 0.2
        uncertain velocity = 25.0 ± 0.5
        momentum = mass * velocity
        """

        self.interpreter.execute(code)

        mass = self.interpreter.current_context.get("mass")
        self.assertIsInstance(mass, UncertainValue)
        self.assertAlmostEqual(mass.value, 10.5)
        self.assertAlmostEqual(mass.uncertainty, 0.2)

        momentum = self.interpreter.current_context.get("momentum")
        self.assertIsInstance(momentum, UncertainValue)
        self.assertAlmostEqual(momentum.value, 262.5)

    def test_tensor_operations(self):
        """Test tensor declaration and operations"""
        code = """
        tensor A[2, 2] = eye(2)
        tensor B[2, 2] = ones(2, 2)
        C = A + B
        """

        self.interpreter.execute(code)

        A = self.interpreter.current_context.get("A")
        self.assertIsInstance(A, SynapseTensor)
        self.assertEqual(A.shape, (2, 2))

        C = self.interpreter.current_context.get("C")
        self.assertIsInstance(C, SynapseTensor)
        # eye(2) + ones(2,2) should give [[2,1],[1,2]]
        expected = np.array([[2, 1], [1, 2]])
        np.testing.assert_array_almost_equal(C.data, expected)

    def test_parallel_execution(self):
        """Test parallel branch execution"""
        code = """
        parallel {
            branch path1: 1 + 1
            branch path2: 2 * 2
            branch path3: 3 ** 2
        }
        """

        results = self.interpreter.execute(code)

        # Should return parallel results
        self.assertIn("path1", results[0])
        self.assertIn("path2", results[0])
        self.assertIn("path3", results[0])
        self.assertEqual(results[0]["path1"], 2)
        self.assertEqual(results[0]["path2"], 4)
        self.assertEqual(results[0]["path3"], 9)

    def test_experiment_execution(self):
        """Test experiment construct execution"""
        code = """
        experiment TestExp {
            setup: 100

            parallel {
                branch control: 100 * 1.0
                branch test: 100 * 1.5
            }

            synthesize: "Analysis complete"
        }
        """

        self.interpreter.execute(code)

        exp = self.interpreter.experiments.get("TestExp")
        self.assertIsNotNone(exp)
        self.assertEqual(exp["setup"], 100)
        self.assertEqual(exp["parallel_results"]["control"], 100.0)
        self.assertEqual(exp["parallel_results"]["test"], 150.0)
        self.assertEqual(exp["synthesis"], "Analysis complete")

    def test_pipeline_execution(self):
        """Test pipeline execution with stages"""
        code = """
        pipeline DataPipeline {
            stage Load {
                data: 100
                status: "loaded"
            }

            stage Process {
                transformed: 200
                validated: 1
            }

            stage Save {
                result: "completed"
            }
        }
        """

        self.interpreter.execute(code)

        pipeline = self.interpreter.pipelines.get("DataPipeline")
        self.assertIsNotNone(pipeline)
        self.assertEqual(len(pipeline["stages"]), 3)

        # Check stage outputs
        self.assertEqual(pipeline["stages"][0].outputs["data"], 100)
        self.assertEqual(pipeline["stages"][1].outputs["transformed"], 200)
        self.assertEqual(pipeline["stages"][2].outputs["result"], "completed")

    def test_hypothesis_execution(self):
        """Test hypothesis construct"""
        code = """
        hypothesis H1 {
            assume: 10 > 5
            predict: "valid"
            validate: 1
        }
        """

        self.interpreter.execute(code)

        hyp = self.interpreter.current_context.get("hypothesis_H1")
        self.assertIsNotNone(hyp)
        self.assertTrue(hyp["assume"])
        self.assertEqual(hyp["predict"], "valid")
        self.assertEqual(hyp["result"], "validated")

    def test_reasoning_chain(self):
        """Test reasoning chain execution"""
        code = """
        reason chain TestLogic {
            premise P1: 1
            premise P2: 1
            derive D1 from P1, P2: 1
            conclude: 1
        }
        """

        self.interpreter.execute(code)

        chain = self.interpreter.reasoning_chains.get("TestLogic")
        self.assertIsNotNone(chain)
        self.assertEqual(chain["premises"]["P1"], 1)
        self.assertEqual(chain["premises"]["P2"], 1)
        self.assertEqual(chain["derivations"]["D1"], 1)
        self.assertTrue(chain["valid"])

    def test_explore_with_backtracking(self):
        """Test explore construct with fallbacks"""
        code = """
        x = 100

        explore Search {
            try primary: 0
            fallback secondary: 1
            accept when: result > 0
        }
        """

        results = self.interpreter.execute(code)

        # Should try primary (0), fail accept condition, then try secondary (1)
        explore_result = results[-1]  # Last result
        self.assertTrue(explore_result["accepted"])
        self.assertEqual(explore_result["solution"], 1)
        self.assertEqual(len(explore_result["tried"]), 2)

    def test_symbolic_operations(self):
        """Test symbolic mathematics"""
        code = """
        symbolic {
            let f(x) = x * 2
            let g(x) = x + 10
        }
        """

        self.interpreter.execute(code)

        # Test that functions were defined
        f = self.interpreter.current_context.get_function("f")
        g = self.interpreter.current_context.get_function("g")

        self.assertIsNotNone(f)
        self.assertIsNotNone(g)

        # Test function execution
        self.assertEqual(f(5), 10)
        self.assertEqual(g(5), 15)

    def test_fork_in_pipeline(self):
        """Test fork within pipeline stage"""
        code = """
        pipeline ForkTest {
            stage Parallel {
                fork {
                    path a: 10
                    path b: 20
                    path c: 30
                }
            }
        }
        """

        self.interpreter.execute(code)

        pipeline = self.interpreter.pipelines.get("ForkTest")
        self.assertIsNotNone(pipeline)

        # Check fork results
        stage_output = pipeline["stages"][0].outputs
        self.assertEqual(stage_output["a"], 10)
        self.assertEqual(stage_output["b"], 20)
        self.assertEqual(stage_output["c"], 30)

    def test_nested_blocks(self):
        """Test nested block scoping"""
        code = """
        x = 10
        result = {
            y = 20
            z = x + y
            z
        }
        """

        self.interpreter.execute(code)

        # x should be in global scope
        self.assertEqual(self.interpreter.current_context.get("x"), 10)

        # result should be the last value in block (z = 30)
        self.assertEqual(self.interpreter.current_context.get("result"), 30)

        # y should not be in global scope (was in block scope)
        with self.assertRaises(NameError):
            self.interpreter.current_context.get("y")

    def test_function_calls(self):
        """Test built-in function calls"""
        code = """
        x = sqrt(16)
        y = sin(0)
        z = max(10, 20, 15)
        """

        self.interpreter.execute(code)

        self.assertAlmostEqual(self.interpreter.current_context.get("x"), 4.0)
        self.assertAlmostEqual(self.interpreter.current_context.get("y"), 0.0)
        self.assertEqual(self.interpreter.current_context.get("z"), 20)

    def test_structure_definition(self):
        """Test structure type definition"""
        code = """
        structure Point {
            x: Real
            y: Real
            invariant: x >= 0
        }
        """

        self.interpreter.execute(code)

        # Check structure was registered
        struct_def = self.interpreter.current_context.get("_struct_Point")
        self.assertIsNotNone(struct_def)
        self.assertIn("x", struct_def["fields"])
        self.assertIn("y", struct_def["fields"])

    def test_constrain_declaration(self):
        """Test constrain variable declaration"""
        code = """
        constrain x: Real where x > 0
        constrain n: Integer where n < 100
        """

        self.interpreter.execute(code)

        # Variables should be initialized
        self.assertEqual(self.interpreter.current_context.get("x"), 0.0)
        self.assertEqual(self.interpreter.current_context.get("n"), 0)

        # Constraints should be registered
        x_constraint = self.interpreter.current_context.get("_constraint_x")
        self.assertIsNotNone(x_constraint)
        self.assertEqual(x_constraint["type"], "Real")


def run_tests():
    """Run all interpreter tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEnhancedInterpreter)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*60)
    print("INTERPRETER TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
