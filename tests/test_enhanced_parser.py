"""
Enhanced Parser Test Suite for Synapse Language
Phase 1, Week 1, Day 1-2
Tests the enhanced parser with proper syntax
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse_lang.synapse_lexer import Lexer, TokenType
from synapse_lang.synapse_parser_enhanced import EnhancedParser, ParserError
from synapse_lang.synapse_ast_enhanced import *


class TestParserFramework:
    """Base test framework for parser validation"""

    def parse_source(self, source: str):
        """Helper to parse source code"""
        # Remove leading indentation from test strings
        lines = source.strip().split('\n')
        source = '\n'.join(lines)

        lexer = Lexer(source)
        parser = EnhancedParser(lexer)
        return parser.parse()

    def assert_parse_error(self, source: str):
        """Assert that parsing fails with ParserError"""
        with pytest.raises(ParserError):
            self.parse_source(source)


class TestBasicParsing(TestParserFramework):
    """Test basic parsing functionality"""

    def test_empty_program(self):
        """Empty program should parse successfully"""
        ast = self.parse_source("")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 0

    def test_simple_number(self):
        """Parse simple number literal"""
        ast = self.parse_source("42")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], NumberNode)
        assert ast.body[0].value == 42

    def test_simple_string(self):
        """Parse simple string literal"""
        ast = self.parse_source('"hello world"')
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], StringNode)
        assert ast.body[0].value == "hello world"

    def test_simple_assignment(self):
        """Parse simple assignment"""
        ast = self.parse_source("x = 42")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert ast.body[0].target == "x"


class TestUncertainValues(TestParserFramework):
    """Test uncertainty value parsing"""

    def test_uncertain_value_basic(self):
        """Parse basic uncertain value"""
        source = "uncertain value = 42.3 ± 0.5"
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert ast.body[0].is_uncertain == True

    def test_uncertain_value_variable(self):
        """Parse uncertain value with variable"""
        source = "uncertain temperature = 300 ± 10"
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert ast.body[0].target == "temperature"


class TestQuantumConstructs(TestParserFramework):
    """Test quantum computing constructs"""

    def test_quantum_circuit_basic(self):
        """Parse basic quantum circuit"""
        source = """
quantum circuit bell_state:
    qubits: 2
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)
        assert ast.body[0].name == "bell_state"
        assert ast.body[0].qubits == 2

    def test_quantum_gates(self):
        """Parse quantum gates"""
        source = """
quantum circuit test:
    qubits: 2
    gates:
        H(0)
        CX(0, 1)
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        circuit = ast.body[0]
        assert isinstance(circuit, QuantumCircuitNode)
        assert len(circuit.gates) == 2
        assert circuit.gates[0].gate_type == "H"
        assert circuit.gates[1].gate_type == "CX"

    def test_quantum_measurement(self):
        """Parse quantum measurement"""
        source = """
quantum circuit measure_test:
    qubits: 2
    measure("all")
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        circuit = ast.body[0]
        assert isinstance(circuit, QuantumCircuitNode)
        assert len(circuit.measurements) == 1

    def test_run_circuit(self):
        """Parse run statement for circuit execution"""
        source = """
run bell_state on ibm_simulator with shots = 1000, noise = "thermal"
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], RunNode)
        assert ast.body[0].circuit == "bell_state"
        assert ast.body[0].backend == "ibm_simulator"


class TestParallelExecution(TestParserFramework):
    """Test parallel execution constructs"""

    def test_parallel_block_basic(self):
        """Parse basic parallel block"""
        source = """
parallel:
    branch A: compute_1()
    branch B: compute_2()
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], ParallelNode)
        assert len(ast.body[0].branches) == 2

    def test_parallel_with_synthesis(self):
        """Parse parallel block with synthesis"""
        source = """
parallel:
    branch slit_A: evolve_wavefunction("A")
    branch slit_B: evolve_wavefunction("B")
    synthesize: compute_interference(slit_A, slit_B)
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        parallel = ast.body[0]
        assert isinstance(parallel, ParallelNode)
        assert len(parallel.branches) == 2
        assert parallel.synthesize is not None


class TestHypothesisExperiment(TestParserFramework):
    """Test hypothesis and experiment constructs"""

    def test_hypothesis_basic(self):
        """Parse basic hypothesis"""
        source = """
hypothesis H1:
    assume: temperature > 273
    predict: state == "liquid"
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], HypothesisNode)
        assert ast.body[0].name == "H1"
        assert len(ast.body[0].assumptions) == 1
        assert len(ast.body[0].predictions) == 1

    def test_experiment_basic(self):
        """Parse basic experiment"""
        source = """
experiment E1:
    setup:
        initialize_conditions()
    analyze:
        process_results()
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], ExperimentNode)
        assert ast.body[0].name == "E1"

    def test_experiment_with_parallel(self):
        """Parse experiment with parallel branches"""
        source = """
experiment pressure_test:
    setup:
        initialize()

    parallel:
        branch A: test_at_pressure(1)
        branch B: test_at_pressure(2)
        branch C: test_at_pressure(0.5)
        synthesize: statistical_analysis(A, B, C)
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], ExperimentNode)


class TestReasoningChains(TestParserFramework):
    """Test reasoning chain constructs"""

    def test_reason_chain_basic(self):
        """Parse basic reasoning chain"""
        source = """
reason_chain ThermodynamicAnalysis:
    premise P1: "Energy cannot be created or destroyed"
    premise P2: "Entropy always increases"
    conclude: P1 && P2
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], ReasonChainNode)
        assert ast.body[0].name == "ThermodynamicAnalysis"
        assert len(ast.body[0].premises) == 2

    def test_reason_chain_with_derive(self):
        """Parse reasoning chain with derivations"""
        source = """
reason_chain ScientificMethod:
    premise P1: "Observable phenomenon exists"
    derive D1 from P1: "Hypothesis can be formed"
    conclude: D1
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        chain = ast.body[0]
        assert isinstance(chain, ReasonChainNode)
        assert len(chain.premises) == 1
        assert len(chain.derivations) == 1


class TestPipelines(TestParserFramework):
    """Test pipeline constructs"""

    def test_pipeline_basic(self):
        """Parse basic pipeline"""
        source = """
pipeline DataAnalysis:
    stage Ingestion:
        load_data()
        remove_outliers()

    stage Processing:
        compute_statistics()
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], PipelineNode)
        assert ast.body[0].name == "DataAnalysis"
        assert len(ast.body[0].stages) == 2

    def test_pipeline_with_parallel(self):
        """Parse pipeline with parallel processing"""
        source = """
pipeline Analysis:
    stage Ingestion[8]:
        load_dataset()
        remove_outliers()
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        pipeline = ast.body[0]
        assert isinstance(pipeline, PipelineNode)
        assert pipeline.stages[0].parallel_factor == 8

    def test_pipeline_with_fork(self):
        """Parse pipeline with fork"""
        source = """
pipeline ML:
    stage Processing:
        fork:
            path statistical:
                compute_stats()
            path ml:
                train_model()
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        pipeline = ast.body[0]
        assert isinstance(pipeline, PipelineNode)
        assert pipeline.stages[0].fork is not None
        assert len(pipeline.stages[0].fork.paths) == 2


class TestSymbolicMath(TestParserFramework):
    """Test symbolic mathematics constructs"""

    def test_symbolic_block_basic(self):
        """Parse basic symbolic block"""
        source = """
symbolic:
    let f(x) = x^2 + 2*x + 1
    let g(x) = differentiate(f, x)
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], SymbolicNode)
        assert len(ast.body[0].statements) == 2

    def test_symbolic_solve(self):
        """Parse symbolic solve statement"""
        source = """
symbolic:
    solve g(x) == 0 for x
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        symbolic = ast.body[0]
        assert isinstance(symbolic, SymbolicNode)
        assert len(symbolic.statements) == 1
        assert isinstance(symbolic.statements[0], SolveNode)

    def test_symbolic_prove(self):
        """Parse symbolic prove statement"""
        source = """
symbolic:
    prove f(x) >= 0 in Real
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        symbolic = ast.body[0]
        assert isinstance(symbolic, SymbolicNode)
        assert len(symbolic.statements) == 1
        assert isinstance(symbolic.statements[0], ProveNode)


class TestTensorOperations(TestParserFramework):
    """Test tensor and matrix operations"""

    def test_tensor_declaration(self):
        """Parse tensor declaration"""
        source = "tensor T[3,3,3] = quantum_state_space()"
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], TensorNode)
        assert ast.body[0].name == "T"
        assert ast.body[0].dimensions == [3, 3, 3]

    def test_matrix_literal(self):
        """Parse matrix literal"""
        source = """
M = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, MatrixNode)


class TestExpressions(TestParserFramework):
    """Test expression parsing"""

    def test_binary_operators(self):
        """Parse binary operators"""
        source = """
x = 1 + 2
y = 3 * 4
z = 5 / 2
w = 10 - 3
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 4
        for stmt in ast.body:
            assert isinstance(stmt, AssignmentNode)
            assert isinstance(stmt.value, BinaryOpNode)

    def test_comparison_operators(self):
        """Parse comparison operators"""
        source = """
a = x > 5
b = y <= 10
c = z == 3
d = w != 0
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 4

    def test_logical_operators(self):
        """Parse logical operators"""
        source = """
p = true && false
q = true || false
r = !true
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 3

    def test_operator_precedence(self):
        """Parse expressions with correct precedence"""
        source = """
result = 1 + 2 * 3
result2 = (1 + 2) * 3
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 2

    def test_function_calls(self):
        """Parse function calls"""
        source = """
result = compute(x, y, z)
value = sin(theta)
data = process(input, parallel=true)
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 3
        for stmt in ast.body:
            assert isinstance(stmt, AssignmentNode)
            assert isinstance(stmt.value, FunctionCallNode)


class TestControlFlow(TestParserFramework):
    """Test control flow constructs"""

    def test_if_statement(self):
        """Parse if statement"""
        source = """
if temperature > 100:
    state = "gas"
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], IfNode)

    def test_if_else_statement(self):
        """Parse if-else statement"""
        source = """
if temperature > 100:
    state = "gas"
else:
    state = "liquid"
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        if_node = ast.body[0]
        assert isinstance(if_node, IfNode)
        assert if_node.else_body is not None

    def test_while_loop(self):
        """Parse while loop"""
        source = """
while error > tolerance:
    iterate()
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], WhileNode)

    def test_for_loop(self):
        """Parse for loop"""
        source = """
for i in range(10):
    process(i)
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], ForNode)
        assert ast.body[0].variable == "i"


class TestAdvancedFeatures(TestParserFramework):
    """Test advanced language features"""

    def test_explore_block(self):
        """Parse explore block"""
        source = """
explore solution_space:
    try path1: analytical_approach()
    fallback path2: numerical_approach()
    accept if error < tolerance
"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], ExploreNode)
        assert ast.body[0].target == "solution_space"
        assert len(ast.body[0].attempts) == 1
        assert len(ast.body[0].fallbacks) == 1

    def test_constrain_variable(self):
        """Parse constrain statement"""
        source = "constrain x: Real where 0 < x"
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], ConstrainNode)
        assert ast.body[0].variable == "x"

    def test_evolve_variable(self):
        """Parse evolve statement"""
        source = "evolve y: Dynamic = initial_state"
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], EvolveNode)
        assert ast.body[0].variable == "y"

    def test_observe_quantum(self):
        """Parse observe statement"""
        source = "observe z: Quantum when collapsed"
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], ObserveNode)
        assert ast.body[0].variable == "z"


def run_tests():
    """Run all parser tests"""
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    run_tests()