#!/usr/bin/env python3
"""
Optimized Synapse Language Interpreter
High-performance version with caching, lazy evaluation, and optimizations
"""

import sys
import time
import asyncio
import numpy as np
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import lru_cache, cached_property
import threading
from collections import deque

# Import cache system
from synapse_cache import (
    get_ast_cache, get_computation_cache, get_result_cache, 
    get_tensor_cache, memoize, ComputationCache
)

# Import existing modules
from synapse_ast_complete import *
from synapse_parser_enhanced import parse_synapse_code
from synapse_tensor_ops import SynapseTensor, TensorOperations
from synapse_symbolic import SymbolicEngine, SymbolicExpression
from synapse_interpreter import UncertainValue

@dataclass
class OptimizedExecutionContext:
    """Optimized execution context with fast lookups"""
    variables: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Any] = field(default_factory=dict)
    parent: Optional['OptimizedExecutionContext'] = None
    
    # Cache for variable lookups
    _lookup_cache: Dict[str, Any] = field(default_factory=dict)
    _cache_valid: bool = field(default=True)
    
    def get(self, name: str) -> Any:
        """Get variable with caching"""
        if name in self._lookup_cache and self._cache_valid:
            return self._lookup_cache[name]
        
        if name in self.variables:
            value = self.variables[name]
        elif self.parent:
            value = self.parent.get(name)
        else:
            raise NameError(f"Variable '{name}' not defined")
        
        self._lookup_cache[name] = value
        return value
    
    def set(self, name: str, value: Any):
        """Set variable and invalidate cache"""
        self.variables[name] = value
        self._cache_valid = False
        self._lookup_cache.clear()
    
    def get_function(self, name: str) -> Any:
        """Get function from context"""
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        return None

class LazyValue:
    """Lazy evaluation wrapper"""
    
    def __init__(self, compute_func, *args, **kwargs):
        self.compute_func = compute_func
        self.args = args
        self.kwargs = kwargs
        self._computed = False
        self._value = None
    
    def get(self):
        """Compute value if needed"""
        if not self._computed:
            self._value = self.compute_func(*self.args, **self.kwargs)
            self._computed = True
        return self._value
    
    def is_computed(self):
        return self._computed

class OptimizedSynapseInterpreter:
    """Optimized interpreter with caching and performance improvements"""
    
    def __init__(self, enable_jit: bool = True, cache_size: int = 1000):
        self.global_context = OptimizedExecutionContext()
        self.current_context = self.global_context
        self.symbolic_engine = SymbolicEngine()
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=16)
        
        # Caches
        self.ast_cache = get_ast_cache()
        self.computation_cache = get_computation_cache()
        self.result_cache = get_result_cache()
        self.tensor_cache = get_tensor_cache()
        
        # JIT compilation flag
        self.enable_jit = enable_jit
        self.jit_cache = {} if enable_jit else None
        
        # Expression optimization
        self.optimize_expressions = True
        
        # Initialize built-in functions
        self._init_optimized_builtins()
    
    def _init_optimized_builtins(self):
        """Initialize optimized built-in functions"""
        # Vectorized math operations
        self.global_context.functions.update({
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'exp': np.exp,
            'log': np.log,
            'sqrt': np.sqrt,
            'abs': np.abs,
            'min': np.minimum,
            'max': np.maximum,
            'sum': np.sum,
            'mean': np.mean,
            'std': np.std,
            
            # Optimized tensor operations
            'zeros': lambda *shape: self._cached_zeros(shape),
            'ones': lambda *shape: self._cached_ones(shape),
            'eye': lambda n: self._cached_eye(n),
            'random': lambda *shape: np.random.random(shape),
            
            # Lazy evaluation
            'lazy': lambda func, *args, **kwargs: LazyValue(func, *args, **kwargs),
            'force': lambda lazy_val: lazy_val.get() if isinstance(lazy_val, LazyValue) else lazy_val,
        })
    
    @lru_cache(maxsize=100)
    def _cached_zeros(self, shape: tuple) -> np.ndarray:
        """Cached zero tensor creation"""
        return np.zeros(shape if len(shape) > 1 else shape[0])
    
    @lru_cache(maxsize=100)
    def _cached_ones(self, shape: tuple) -> np.ndarray:
        """Cached ones tensor creation"""
        return np.ones(shape if len(shape) > 1 else shape[0])
    
    @lru_cache(maxsize=50)
    def _cached_eye(self, n: int) -> np.ndarray:
        """Cached identity matrix creation"""
        return np.eye(n)
    
    def interpret(self, source: str) -> Any:
        """Interpret source code with caching"""
        # Check AST cache
        ast = self.ast_cache.get_ast(source)
        if ast is None:
            # Parse and cache
            ast = parse_synapse_code(source)
            self.ast_cache.put_ast(source, ast)
        
        # Execute AST
        return self.execute(ast)
    
    def execute(self, node: ASTNode) -> Any:
        """Execute AST node with optimizations"""
        # Try to get from JIT cache if enabled
        if self.enable_jit and isinstance(node, (BinaryOpNode, UnaryOpNode, FunctionCallNode)):
            jit_key = self._get_jit_key(node)
            if jit_key in self.jit_cache:
                return self._execute_jit(self.jit_cache[jit_key], node)
        
        # Route to specific execution method
        method_name = f'_execute_{node.__class__.__name__}'
        method = getattr(self, method_name, self._execute_generic)
        
        # Time execution for cache decision
        start_time = time.perf_counter()
        result = method(node)
        execution_time = time.perf_counter() - start_time
        
        # Cache if execution was expensive
        if execution_time > 0.01:  # 10ms threshold
            self._maybe_cache_result(node, result, execution_time)
        
        return result
    
    def _execute_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        """Optimized binary operation execution"""
        # Check if we can use vectorized operations
        left = self.execute(node.left)
        right = self.execute(node.right)
        
        # Handle numpy arrays efficiently
        if isinstance(left, np.ndarray) or isinstance(right, np.ndarray):
            return self._execute_vectorized_binop(node.op, left, right)
        
        # Handle uncertain values
        if isinstance(left, UncertainValue) or isinstance(right, UncertainValue):
            return self._execute_uncertain_binop(node.op, left, right)
        
        # Regular execution
        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
            '**': lambda a, b: a ** b,
            '%': lambda a, b: a % b,
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '<': lambda a, b: a < b,
            '>': lambda a, b: a > b,
            '<=': lambda a, b: a <= b,
            '>=': lambda a, b: a >= b,
            '&&': lambda a, b: a and b,
            '||': lambda a, b: a or b,
        }
        
        if node.op in ops:
            return ops[node.op](left, right)
        else:
            raise ValueError(f"Unknown operator: {node.op}")
    
    def _execute_vectorized_binop(self, op: str, left: Any, right: Any) -> Any:
        """Execute binary operation using numpy vectorization"""
        # Convert to numpy if needed
        if not isinstance(left, np.ndarray):
            left = np.array(left)
        if not isinstance(right, np.ndarray):
            right = np.array(right)
        
        # Use numpy operations
        numpy_ops = {
            '+': np.add,
            '-': np.subtract,
            '*': np.multiply,
            '/': np.divide,
            '**': np.power,
            '%': np.mod,
            '==': np.equal,
            '!=': np.not_equal,
            '<': np.less,
            '>': np.greater,
            '<=': np.less_equal,
            '>=': np.greater_equal,
        }
        
        if op in numpy_ops:
            # Check tensor cache
            cache_key = (op, id(left), id(right))
            result = self.tensor_cache.get_operation(op, (left, right))
            if result is not None:
                return result
            
            # Compute and cache
            result = numpy_ops[op](left, right)
            self.tensor_cache.cache_operation(op, (left, right), result)
            return result
        
        # Fallback to element-wise
        return self._execute_binop_elementwise(op, left, right)
    
    def _execute_uncertain_binop(self, op: str, left: Any, right: Any) -> Any:
        """Execute binary operation with uncertainty propagation"""
        # Ensure both are UncertainValue
        if not isinstance(left, UncertainValue):
            left = UncertainValue(left, 0)
        if not isinstance(right, UncertainValue):
            right = UncertainValue(right, 0)
        
        # Propagate uncertainty
        if op == '+':
            return UncertainValue(
                left.value + right.value,
                np.sqrt(left.uncertainty**2 + right.uncertainty**2)
            )
        elif op == '-':
            return UncertainValue(
                left.value - right.value,
                np.sqrt(left.uncertainty**2 + right.uncertainty**2)
            )
        elif op == '*':
            value = left.value * right.value
            rel_unc = np.sqrt(
                (left.uncertainty/left.value)**2 + 
                (right.uncertainty/right.value)**2
            ) if left.value != 0 and right.value != 0 else 0
            return UncertainValue(value, abs(value * rel_unc))
        elif op == '/':
            if right.value == 0:
                raise ZeroDivisionError("Division by zero")
            value = left.value / right.value
            rel_unc = np.sqrt(
                (left.uncertainty/left.value)**2 + 
                (right.uncertainty/right.value)**2
            ) if left.value != 0 else 0
            return UncertainValue(value, abs(value * rel_unc))
        else:
            # For comparison operators, return the comparison of values
            return eval(f"{left.value} {op} {right.value}")
    
    def _execute_ParallelBlockNode(self, node: ParallelBlockNode) -> Dict[str, Any]:
        """Optimized parallel execution with result caching"""
        results = {}
        
        # Check if we have cached synthesis
        branch_names = tuple(branch.name for branch in node.branches)
        cached_synthesis = self.result_cache.get_synthesis(branch_names)
        if cached_synthesis is not None:
            return cached_synthesis
        
        # Create futures for parallel execution
        futures = {}
        for branch in node.branches:
            # Check if branch result is cached
            cached_result = self.result_cache.get_branch_result(branch.name)
            if cached_result is not None:
                results[branch.name] = cached_result
            else:
                # Submit for execution
                future = self.executor.submit(self._execute_branch, branch)
                futures[branch.name] = future
        
        # Collect results
        for name, future in futures.items():
            result = future.result()
            results[name] = result
            self.result_cache.store_branch_result(name, result)
        
        # Cache synthesis
        self.result_cache.store_synthesis(branch_names, results)
        
        return results
    
    def _execute_branch(self, branch: BranchNode) -> Any:
        """Execute a single branch"""
        # Create new context for branch
        branch_context = OptimizedExecutionContext(parent=self.current_context)
        old_context = self.current_context
        self.current_context = branch_context
        
        try:
            result = self.execute(branch.body)
            return result
        finally:
            self.current_context = old_context
    
    def _execute_FunctionCallNode(self, node: FunctionCallNode) -> Any:
        """Optimized function call execution"""
        # Check computation cache
        cache_result = self.computation_cache.get(
            node.name, 
            tuple(self.execute(arg) for arg in node.args),
            {}
        )
        if cache_result is not None:
            return cache_result[0]
        
        # Look up function
        func = self.current_context.get_function(node.name)
        if func is None:
            raise NameError(f"Function '{node.name}' not defined")
        
        # Evaluate arguments
        args = [self.execute(arg) for arg in node.args]
        
        # Time execution
        start_time = time.perf_counter()
        result = func(*args)
        execution_time = time.perf_counter() - start_time
        
        # Cache if expensive
        if execution_time > 0.001:  # 1ms threshold
            self.computation_cache.put(
                node.name,
                tuple(args),
                {},
                result,
                execution_time
            )
        
        return result
    
    def _execute_TensorNode(self, node: TensorNode) -> SynapseTensor:
        """Optimized tensor creation"""
        # Try to reuse cached tensors for common shapes
        if node.values:
            values = [self.execute(v) for v in node.values]
            return SynapseTensor(np.array(values))
        else:
            shape = tuple(self.execute(d) for d in node.dimensions)
            # Check cache for zeros/ones
            return SynapseTensor(self._cached_zeros(shape))
    
    def _execute_VariableNode(self, node: VariableNode) -> Any:
        """Optimized variable lookup"""
        return self.current_context.get(node.name)
    
    def _execute_AssignmentNode(self, node: AssignmentNode) -> Any:
        """Optimized assignment"""
        value = self.execute(node.value)
        self.current_context.set(node.name, value)
        return value
    
    def _execute_generic(self, node: ASTNode) -> Any:
        """Generic execution for unoptimized nodes"""
        # Fallback to basic execution
        if hasattr(node, 'statements'):
            results = []
            for stmt in node.statements:
                results.append(self.execute(stmt))
            return results[-1] if results else None
        return None
    
    def _get_jit_key(self, node: ASTNode) -> str:
        """Generate JIT cache key for node"""
        # Simple key generation - could be improved
        return f"{node.__class__.__name__}_{id(node)}"
    
    def _execute_jit(self, compiled_func, node: ASTNode) -> Any:
        """Execute JIT-compiled function"""
        # This would contain actual JIT execution
        # For now, just call the compiled function
        return compiled_func(self, node)
    
    def _maybe_cache_result(self, node: ASTNode, result: Any, execution_time: float):
        """Decide whether to cache result based on execution time"""
        if execution_time > 0.1:  # 100ms threshold for heavy caching
            # This would implement smart caching logic
            pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get interpreter statistics"""
        from synapse_cache import get_cache_stats
        return {
            'cache_stats': get_cache_stats(),
            'context_vars': len(self.global_context.variables),
            'jit_entries': len(self.jit_cache) if self.jit_cache else 0,
        }

def benchmark_interpreter():
    """Benchmark optimized vs regular interpreter"""
    import time
    
    # Test code
    test_code = """
    uncertain x = 10.0 ± 0.1
    uncertain y = 20.0 ± 0.2
    
    parallel {
        branch calc1: x * y + x
        branch calc2: y * x - y
        branch calc3: (x + y) * 2
    }
    
    tensor T[3, 3] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    result = T * 2 + T
    """
    
    # Create interpreters
    opt_interpreter = OptimizedSynapseInterpreter(enable_jit=True)
    
    # Warm up
    for _ in range(5):
        opt_interpreter.interpret(test_code)
    
    # Benchmark
    iterations = 100
    start = time.perf_counter()
    for _ in range(iterations):
        opt_interpreter.interpret(test_code)
    optimized_time = time.perf_counter() - start
    
    print(f"Optimized Interpreter: {optimized_time:.3f}s for {iterations} iterations")
    print(f"Average: {optimized_time/iterations*1000:.2f}ms per iteration")
    print("\nCache Statistics:")
    stats = opt_interpreter.get_stats()
    for key, value in stats['cache_stats'].items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    benchmark_interpreter()