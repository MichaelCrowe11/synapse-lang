"""Deprecated root interpreter wrapper. Use synapse_lang.synapse_interpreter."""
from __future__ import annotations
from synapse_lang.synapse_interpreter import *  # type: ignore
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor

# Quantum ML availability flag (set to False by default)
QUANTUM_ML_AVAILABLE = False

# Import TokenType if available, otherwise define a minimal placeholder for safety
try:
    from synapse_lang.tokens import TokenType
except ImportError:
    class TokenType:
        LEFT_BRACE = 'LEFT_BRACE'
        RIGHT_BRACE = 'RIGHT_BRACE'
        EOF = 'EOF'
        NEWLINE = 'NEWLINE'
        PARALLEL = 'PARALLEL'
        UNCERTAIN = 'UNCERTAIN'
        IDENTIFIER = 'IDENTIFIER'
        ASSIGN = 'ASSIGN'
        BRANCH = 'BRANCH'
        NUMBER = 'NUMBER'
        STRING = 'STRING'
        UNCERTAINTY = 'UNCERTAINTY'

@dataclass
class UncertainValue: ...  # kept for compatibility shadowing

class ParallelStream:
    def __init__(self, name: str, function):
        self.name = name
        self.function = function
        self.result = None
        self.lock = threading.Lock()
    
    def execute(self):
        self.result = self.function()
        return self.result

class SynapseInterpreter:
    def __init__(self):
        self.variables = {}
        self.hypotheses = {}
        self.experiments = {}
        self.streams = {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Initialize quantum ML components if available
        if QUANTUM_ML_AVAILABLE:
            self.quantum_nn = QuantumNeuralNetwork(input_size=10, hidden_size=64, output_size=1)
            self.quantum_ensemble = QuantumEnsemble(num_models=5)
            self.continuous_learner = ContinuousQuantumLearner()
        else:
            self.quantum_nn = None
            self.quantum_ensemble = None
            self.continuous_learner = None
        
    def execute(self, source: str):
        """Execute Synapse source code using AST parser"""
        try:
            ast = parse(source)
            return self.interpret_ast(ast)
        except Exception as e:
            error_msg = f"Parse/Execution Error: {e}"
            print(f"Error: {error_msg}")
            return [error_msg]
    
    def interpret_ast(self, node):
        """Interpret AST nodes with error handling"""
        try:
            if isinstance(node, ProgramNode):
                results = []
                for stmt in node.body:
                    result = self.interpret_ast(stmt)
                    if result is not None:
                        results.append(result)
                return results
            elif isinstance(node, UncertainNode):
                uncertain_val = UncertainValue(node.value, node.uncertainty)
                var_name = f"uncertain_{len(self.variables)}"
                self.variables[var_name] = uncertain_val
                return f"{var_name} = {uncertain_val}"
            elif isinstance(node, AssignmentNode):
                value = self.interpret_ast(node.value)
                var_name = node.target.name
                
                if node.is_uncertain:
                    uncertain_val = UncertainValue(float(value), 0.0)
                    self.variables[var_name] = uncertain_val
                    return f"{var_name} = {uncertain_val}"
                else:
                    self.variables[var_name] = value
                    return f"{var_name} = {value}"
            elif isinstance(node, ParallelNode):
                return self.execute_parallel_ast(node)
            elif isinstance(node, ReasonChainNode):
                return self.interpret_reason_chain(node)
            elif isinstance(node, HypothesisNode):
                return self.interpret_hypothesis(node)
            elif isinstance(node, PipelineNode):
                return self.interpret_pipeline(node)
            elif isinstance(node, StageNode):
                return self.interpret_stage(node)
            elif isinstance(node, ListNode):
                return [self.interpret_ast(e) for e in node.elements]
            elif isinstance(node, MatrixNode):
                return [[self.interpret_ast(e) for e in row] for row in node.rows]
            elif isinstance(node, TensorNode):
                values = [self.interpret_ast(v) for v in node.values]
                return {"tensor": True, "dims": node.dimensions, "values": values}
            elif isinstance(node, NumberNode):
                return node.value
            elif isinstance(node, StringNode):
                return node.value
            elif isinstance(node, IdentifierNode):
                if node.name not in self.variables:
                    raise NameError(f"Variable '{node.name}' is not defined")
                return self.variables.get(node.name, node.name)
            elif isinstance(node, BinaryOpNode):
                return self.interpret_binary_op(node)
            elif isinstance(node, ProveNode):
                return self.interpret_prove(node)
            elif isinstance(node, QuantumCircuitNode):
                return self.interpret_quantum_circuit(node)
            elif isinstance(node, QuantumGateNode):
                return self.interpret_quantum_gate(node)
            elif isinstance(node, QuantumMeasureNode):
                return self.interpret_quantum_measure(node)
            elif isinstance(node, QuantumAlgorithmNode):
                return self.interpret_quantum_algorithm(node)
            elif isinstance(node, QuantumBackendNode):
                return self.interpret_quantum_backend(node)
            else:
                return f"Unsupported AST node: {type(node).__name__}"
        except Exception as e:
            return f"Runtime Error in {type(node).__name__}: {e}"
    
    def execute_parallel_ast(self, node):
        """Execute parallel block with optimized worker count"""
        # Determine optimal worker count
        if node.num_workers is not None:
            max_workers = node.num_workers
        else:
            # Auto-determine based on branch count and system resources
            import os
            cpu_count = os.cpu_count() or 4
            max_workers = min(len(node.branches), cpu_count, 8)  # Cap at 8 for safety
        
        # Reuse existing executor if worker count matches, otherwise create new one
        if not hasattr(self, '_cached_executor') or self._cached_workers != max_workers:
            if hasattr(self, '_cached_executor'):
                self._cached_executor.shutdown(wait=False)
            
            from concurrent.futures import ThreadPoolExecutor
            self._cached_executor = ThreadPoolExecutor(max_workers=max_workers)
            self._cached_workers = max_workers
        
        futures = []
        for branch in node.branches:
            branch_name = branch.name
            # Capture branch context for parallel execution
            branch_vars = self.variables.copy()
            
            def execute_branch(name=branch_name, context=branch_vars):
                # Create isolated interpreter context for this branch
                branch_result = f"Executed branch {name}"
                # Here we could execute branch.body in isolated context
                return branch_result
            
            future = self._cached_executor.submit(execute_branch)
            futures.append((branch_name, future))
        
        results = {}
        for branch_name, future in futures:
            results[branch_name] = future.result()
        
        return {"parallel_execution": results, "workers_used": max_workers}
    
    def interpret_reason_chain(self, node):
        """Interpret reasoning chain with enhanced condition evaluation"""
        results = [f"Reasoning Chain: {node.name}"]
        premise_values = {}
        
        # Evaluate premises and store results
        for premise in node.premises:
            premise_value = self.interpret_ast(premise.statement)
            premise_values[premise.name] = premise_value
            results.append(f"Premise {premise.name}: {premise_value}")
        
        # Evaluate derivations with premise context
        derivation_values = {}
        for derivation in node.derivations:
            # Check if derivation references valid premise
            if derivation.from_premise in premise_values:
                derived_value = self.interpret_ast(derivation.conclusion)
                derivation_values[derivation.name] = derived_value
                results.append(f"Derivation {derivation.name} from {derivation.from_premise}: {derived_value}")
            else:
                results.append(f"Warning: Derivation {derivation.name} references unknown premise {derivation.from_premise}")
        
        # Enhanced conclusion evaluation
        if node.conclusion:
            # Evaluate condition with premise/derivation context
            condition_result = self.interpret_ast(node.conclusion.condition)
            
            # Apply logical evaluation of condition
            conclusion_valid = False
            if isinstance(condition_result, bool):
                conclusion_valid = condition_result
            elif isinstance(condition_result, (int, float)):
                conclusion_valid = condition_result != 0
            elif isinstance(condition_result, str):
                # Check if condition references a valid premise/derivation
                conclusion_valid = condition_result in premise_values or condition_result in derivation_values
            
            if conclusion_valid:
                conclusion_value = self.interpret_ast(node.conclusion.result)
                results.append(f"Conclusion (valid): {conclusion_value}")
            else:
                results.append(f"Conclusion (invalid): Condition {condition_result} not satisfied")
        
        return results
    
    def interpret_hypothesis(self, node):
        """Interpret hypothesis with quantum ML integration."""
        try:
            results = [f"Hypothesis: {node.name}"]
            
            # Import quantum ML if available
            try:
                from synapse_quantum_ml import QuantumNeuralNetwork, calculate_quantum_uncertainty
                quantum_available = True
            except ImportError:
                quantum_available = False
            
            # Evaluate assumptions with quantum uncertainty
            assumption_values = []
            for assumption in node.assumptions:
                assumption_value = self.interpret_ast(assumption)
                if quantum_available and isinstance(assumption_value, (int, float)):
                    # Add quantum uncertainty to numerical assumptions
                    uncertainty = calculate_quantum_uncertainty(np.array([assumption_value]))
                    assumption_value = UncertainValue(float(assumption_value), float(uncertainty))
                assumption_values.append(assumption_value)
                results.append(f"Assumption: {assumption_value}")
            
            # Evaluate predictions with quantum ML
            prediction_values = []
            for prediction in node.predictions:
                prediction_value = self.interpret_ast(prediction)
                if quantum_available and len(assumption_values) > 0:
                    # Use quantum neural network for prediction refinement
                    qnn = QuantumNeuralNetwork(
                        input_size=len(assumption_values),
                        hidden_size=32,
                        output_size=1
                    )
                    
                    # Prepare input data
                    input_data = np.array([float(str(v).split(' ')[0]) for v in assumption_values])
                    quantum_prediction = qnn.forward(input_data.reshape(1, -1))
                    
                    # Combine classical and quantum predictions
                    if isinstance(prediction_value, (int, float)):
                        combined_prediction = 0.7 * prediction_value + 0.3 * quantum_prediction[0][0]
                        uncertainty = calculate_quantum_uncertainty(quantum_prediction)
                        prediction_value = UncertainValue(combined_prediction, uncertainty)
                    
                prediction_values.append(prediction_value)
                results.append(f"Prediction: {prediction_value}")
            
            # Add quantum confidence assessment
            if quantum_available:
                results.append("Quantum-enhanced hypothesis evaluation completed")
            
            return results
            
        except Exception as e:
            return [f"Hypothesis interpretation error: {str(e)}"]
    
    def interpret_binary_op(self, node):
        """Interpret binary operations"""
        left = self.interpret_ast(node.left)
        right = self.interpret_ast(node.right)

        # Constant folding shortcut
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            try:
                if node.operator == "+":
                    return left + right
                if node.operator == "-":
                    return left - right
                if node.operator == "*":
                    return left * right
                if node.operator == "/":
                    return left / right
            except Exception as e:
                return f"Arithmetic error: {e}"
        
        if node.operator == "+":
            return left + right
        elif node.operator == "-":
            return left - right
        elif node.operator == "*":
            return left * right
        elif node.operator == "/":
            return left / right
        elif node.operator == "=>":
            # Arrow operator for implications
            return f"{left} => {right}"
        else:
            return f"Unsupported operator: {node.operator}"

    def interpret_pipeline(self, node: PipelineNode):
        """Execute pipeline with variable context propagation across stages"""
        results = {"pipeline": node.name, "stages": []}
        
        # Create pipeline-local variable context
        pipeline_context = self.variables.copy()
        
        for stage in node.stages:
            # Each stage inherits context from previous stages
            prev_vars = self.variables
            self.variables = pipeline_context.copy()
            
            stage_result = self.interpret_stage(stage)
            
            # Propagate new variables to pipeline context
            pipeline_context.update(self.variables)
            
            # Restore global context
            self.variables = prev_vars
            
            results["stages"].append(stage_result)
        
        # Merge pipeline results back to global context
        self.variables.update(pipeline_context)
        
        return results

    def interpret_stage(self, node: StageNode):
        """Execute pipeline stage with proper body interpretation"""
        if hasattr(node.body, 'statements'):
            # Block node - execute all statements
            stage_results = []
            for stmt in node.body.statements:
                result = self.interpret_ast(stmt)
                if result is not None:
                    stage_results.append(result)
            body_result = stage_results
        else:
            # Single expression
            body_result = self.interpret_ast(node.body)
            
        return {"stage": node.name, "result": body_result, "parallel": node.parallel_count}
    
    def parse_and_execute(self, tokens: List[Token]):
        results = []
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == TokenType.EOF:
                break
            
            if token.type == TokenType.NEWLINE:
                i += 1
                continue
            
            if token.type == TokenType.PARALLEL:
                result = self.execute_parallel_block(tokens, i)
                results.append(result)
                i = self.find_block_end(tokens, i) + 1
                
            elif token.type == TokenType.UNCERTAIN:
                result = self.parse_uncertain_value(tokens, i)
                results.append(result)
                while tokens[i].type != TokenType.NEWLINE and tokens[i].type != TokenType.EOF:
                    i += 1
                    
            elif token.type == TokenType.IDENTIFIER:
                if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.ASSIGN:
                    var_name = token.value
                    i += 2  # Skip identifier and =
                    value = self.parse_expression(tokens, i)
                    self.variables[var_name] = value
                    results.append(f"{var_name} = {value}")
                    while tokens[i].type != TokenType.NEWLINE and tokens[i].type != TokenType.EOF:
                        i += 1
                else:
                    i += 1
            else:
                i += 1
        
        return results
    
    def execute_parallel_block(self, tokens: List[Token], start_idx: int):
        i = start_idx + 1
        
        while tokens[i].type != TokenType.LEFT_BRACE:
            i += 1
        i += 1  # Skip {
        
        branches = []
        
        while tokens[i].type != TokenType.RIGHT_BRACE:
            if tokens[i].type == TokenType.BRANCH:
                i += 1
                branch_name = tokens[i].value
                i += 2  # Skip name and :
                
                # Simple expression parsing for demo
                expr_start = i
                while tokens[i].type != TokenType.NEWLINE and tokens[i].type != TokenType.RIGHT_BRACE:
                    i += 1
                
                branches.append((branch_name, lambda name=branch_name: f"Executed branch {name}"))
            
            if tokens[i].type == TokenType.NEWLINE:
                i += 1
            elif tokens[i].type != TokenType.RIGHT_BRACE:
                i += 1
        
        # Execute branches in parallel
        futures = []
        for branch_name, branch_func in branches:
            future = self.executor.submit(branch_func)
            futures.append((branch_name, future))
        
        results = {}
        for branch_name, future in futures:
            results[branch_name] = future.result()
        
        return {"parallel_execution": results}
    
    def parse_uncertain_value(self, tokens: List[Token], start_idx: int):
        i = start_idx + 1
        
        while tokens[i].type != TokenType.IDENTIFIER:
            i += 1
        
        var_name = tokens[i].value
        i += 1
        
        while tokens[i].type != TokenType.NUMBER:
            i += 1
        
        value = tokens[i].value
        i += 1
        
        if i < len(tokens) and tokens[i].type == TokenType.UNCERTAINTY:
            i += 1
            uncertainty = tokens[i].value
            uncertain_val = UncertainValue(value, uncertainty)
            self.variables[var_name] = uncertain_val
            return f"{var_name} = {uncertain_val}"
        
        return f"{var_name} = {value}"
    
    def parse_expression(self, tokens: List[Token], start_idx: int):
        # Simplified expression parsing
        i = start_idx
        
        if tokens[i].type == TokenType.NUMBER:
            return tokens[i].value
        elif tokens[i].type == TokenType.STRING:
            return tokens[i].value
        elif tokens[i].type == TokenType.IDENTIFIER:
            return self.variables.get(tokens[i].value, tokens[i].value)
        
        return None
    
    def find_block_end(self, tokens: List[Token], start_idx: int):
        i = start_idx
        brace_count = 0
        
        while i < len(tokens):
            if tokens[i].type == TokenType.LEFT_BRACE:
                brace_count += 1
            elif tokens[i].type == TokenType.RIGHT_BRACE:
                brace_count -= 1
                if brace_count == 0:
                    return i
            i += 1
        
        return len(tokens) - 1
    
    def interpret_prove(self, node):
        """Interpret prove statement"""
        statement = self.interpret_ast(node.statement)
        method = self.interpret_ast(node.method) if node.method else "direct"
        return f"Proof attempt: {statement} using {method}"
    
    def interpret_quantum_circuit(self, node):
        """Interpret quantum circuit definition"""
        if not QUANTUM_CORE_AVAILABLE:
            return f"Quantum core not available for circuit '{node.name}'"
        
        try:
            # Create quantum circuit
            circuit = QuantumCircuitBuilder(node.qubits)
            
            # Add gates
            for gate in node.gates:
                self.add_quantum_gate(circuit, gate)

            # Add measurements (measure all if any measurement nodes present but no explicit ones yet)
            if node.measurements:
                for m in node.measurements:
                    for q_ast in m.qubits:
                        q_index = self.interpret_ast(q_ast)
                        if isinstance(q_index, (int, float)):
                            circuit.measure(int(q_index))
            else:
                # Auto-measure if no explicit measurement but circuit ends a top-level block
                circuit.measure_all()
            
            # Create simulator backend
            backend = self._get_active_backend() or SimulatorBackend()
            
            # Execute circuit
            shots = self._current_backend_config.get('shots', 512) if hasattr(self, '_current_backend_config') else 512
            result = backend.execute(circuit, shots=shots)
            
            # Store circuit for later use
            self.variables[f"circuit_{node.name}"] = circuit
            
            return {
                "circuit_name": node.name,
                "qubits": node.qubits,
                "gates": len(node.gates),
                "shots": shots,
                "counts": result
            }
            
        except Exception as e:
            return f"Quantum circuit error in '{node.name}': {e}"
    
    def interpret_quantum_gate(self, node):
        """Interpret individual quantum gate"""
        if not QUANTUM_CORE_AVAILABLE:
            return f"Quantum core not available for gate '{node.gate_type}'"
        
        # This would typically be called from within circuit interpretation
        return f"Gate {node.gate_type} on qubits {node.qubits}"
    
    def add_quantum_gate(self, circuit, gate_node):
        """Add a quantum gate to the circuit with validation and parameter handling"""
        gate_type = gate_node.gate_type.lower()
        qubits = [self.interpret_ast(q) for q in gate_node.qubits]
        parameters = [self.interpret_ast(p) for p in gate_node.parameters]

        # Validate qubits are numeric
        if any(not isinstance(q, (int, float)) for q in qubits):
            print(f"Warning: Non-numeric qubit index in {gate_type}: {qubits}")
            return
        qi = [int(q) for q in qubits]

        try:
            if gate_type in ('h','hadamard'):
                circuit.h(qi[0])
            elif gate_type in ('cnot','cx'):
                if len(qi) < 2:
                    raise ValueError('cnot requires two qubits')
                circuit.cnot(qi[0], qi[1])
            elif gate_type in ('x','pauli_x'):
                circuit.x(qi[0])
            elif gate_type in ('y','pauli_y'):
                circuit.y(qi[0])
            elif gate_type in ('z','pauli_z'):
                circuit.z(qi[0])
            elif gate_type in ('rx','rotation_x'):
                circuit.rx(qi[0], float(parameters[0]) if parameters else 0.0)
            elif gate_type in ('ry','rotation_y'):
                circuit.ry(qi[0], float(parameters[0]) if parameters else 0.0)
            elif gate_type in ('rz','rotation_z'):
                circuit.rz(qi[0], float(parameters[0]) if parameters else 0.0)
            else:
                print(f"Warning: Unknown quantum gate '{gate_type}'")
        except Exception as e:
            print(f"Quantum gate error {gate_type}: {e}")
    
    def interpret_quantum_measure(self, node):
        """Interpret quantum measurement"""
        if not QUANTUM_CORE_AVAILABLE:
            return f"Quantum core not available for measurement"
        
        qubits = [self.interpret_ast(q) for q in node.qubits]
        return f"Measure qubits {qubits}"
    
    def interpret_quantum_algorithm(self, node):
        """Interpret quantum algorithm definition"""
        if not QUANTUM_CORE_AVAILABLE:
            return f"Quantum core not available for algorithm '{node.name}'"
        
        # Store algorithm for later execution
        self.variables[f"algorithm_{node.name}"] = {
            "name": node.name,
            "parameters": node.parameters,
            "ansatz": node.ansatz,
            "cost_function": node.cost_function,
            "optimizer": node.optimizer
        }
        
        return f"Quantum algorithm '{node.name}' defined"
    
    def interpret_quantum_backend(self, node):
        """Interpret quantum backend configuration"""
        if not QUANTUM_CORE_AVAILABLE:
            return f"Quantum core not available for backend '{node.name}'"
        
        # Store backend configuration
        cfg = {k: self.interpret_ast(v) for k, v in node.config.items()}
        self.variables[f"backend_{node.name}"] = {"name": node.name, "config": cfg}
        # Mark as active backend
        self._active_backend_name = node.name
        self._current_backend_config = cfg
        return f"Quantum backend '{node.name}' configured (active)"

    def _get_active_backend(self):
        if not QUANTUM_CORE_AVAILABLE:
            return None
        if hasattr(self, '_active_backend_name'):
            # For now always return a fresh SimulatorBackend; future: different types
            return SimulatorBackend()
        return None

def main(): ...