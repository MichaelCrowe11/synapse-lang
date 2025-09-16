"""
Synapse Language - Optimized JIT Compiler
Just-In-Time compilation for performance-critical code paths
"""

import ast
import hashlib
from collections.abc import Callable
from typing import Any

import numpy as np
from numba import njit, prange, vectorize

# Import Synapse AST
from synapse_ast_complete import *


class JITCompiler:
    """JIT compiler for Synapse expressions"""

    def __init__(self, cache_compiled: bool = True):
        self.cache_compiled = cache_compiled
        self.compiled_functions = {}
        self.compilation_stats = {
            "compiled": 0,
            "cache_hits": 0,
            "failures": 0
        }

    def compile_expression(self, node: ASTNode) -> Callable | None:
        """Compile AST node to native code"""
        # Generate cache key
        cache_key = self._get_cache_key(node)

        # Check cache
        if self.cache_compiled and cache_key in self.compiled_functions:
            self.compilation_stats["cache_hits"] += 1
            return self.compiled_functions[cache_key]

        try:
            # Convert to Python AST
            py_ast = self._synapse_to_python_ast(node)

            # Generate function
            func = self._create_function_from_ast(py_ast)

            # JIT compile
            compiled = self._jit_compile(func)

            # Cache
            if self.cache_compiled:
                self.compiled_functions[cache_key] = compiled

            self.compilation_stats["compiled"] += 1
            return compiled

        except Exception:
            self.compilation_stats["failures"] += 1
            return None

    def _get_cache_key(self, node: ASTNode) -> str:
        """Generate cache key for AST node"""
        # Simple serialization for caching
        node_repr = self._serialize_node(node)
        return hashlib.sha256(node_repr.encode()).hexdigest()

    def _serialize_node(self, node: ASTNode) -> str:
        """Serialize AST node for caching"""
        if isinstance(node, BinaryOpNode):
            return f"binop:{node.op}:{self._serialize_node(node.left)}:{self._serialize_node(node.right)}"
        elif isinstance(node, UnaryOpNode):
            return f"unary:{node.op}:{self._serialize_node(node.operand)}"
        elif isinstance(node, NumberNode):
            return f"num:{node.value}"
        elif isinstance(node, VariableNode):
            return f"var:{node.name}"
        elif isinstance(node, FunctionCallNode):
            args = ",".join(self._serialize_node(arg) for arg in node.args)
            return f"call:{node.name}:{args}"
        else:
            return f"unknown:{type(node).__name__}"

    def _synapse_to_python_ast(self, node: ASTNode) -> ast.AST:
        """Convert Synapse AST to Python AST"""
        if isinstance(node, BinaryOpNode):
            left = self._synapse_to_python_ast(node.left)
            right = self._synapse_to_python_ast(node.right)

            op_map = {
                "+": ast.Add(),
                "-": ast.Sub(),
                "*": ast.Mult(),
                "/": ast.Div(),
                "**": ast.Pow(),
                "%": ast.Mod(),
                "==": ast.Eq(),
                "!=": ast.NotEq(),
                "<": ast.Lt(),
                ">": ast.Gt(),
                "<=": ast.LtE(),
                ">=": ast.GtE(),
            }

            if node.op in op_map:
                return ast.BinOp(left=left, op=op_map[node.op], right=right)
            else:
                # Logical operators
                if node.op == "&&":
                    return ast.BoolOp(op=ast.And(), values=[left, right])
                elif node.op == "||":
                    return ast.BoolOp(op=ast.Or(), values=[left, right])

        elif isinstance(node, UnaryOpNode):
            operand = self._synapse_to_python_ast(node.operand)

            op_map = {
                "-": ast.USub(),
                "+": ast.UAdd(),
                "!": ast.Not(),
            }

            if node.op in op_map:
                return ast.UnaryOp(op=op_map[node.op], operand=operand)

        elif isinstance(node, NumberNode):
            return ast.Constant(value=node.value)

        elif isinstance(node, VariableNode):
            return ast.Name(id=node.name, ctx=ast.Load())

        elif isinstance(node, FunctionCallNode):
            # Map to numpy functions
            func_map = {
                "sin": "np.sin",
                "cos": "np.cos",
                "tan": "np.tan",
                "exp": "np.exp",
                "log": "np.log",
                "sqrt": "np.sqrt",
                "abs": "np.abs",
            }

            if node.name in func_map:
                func_name = func_map[node.name]
                if "." in func_name:
                    module, name = func_name.split(".")
                    func = ast.Attribute(
                        value=ast.Name(id=module, ctx=ast.Load()),
                        attr=name,
                        ctx=ast.Load()
                    )
                else:
                    func = ast.Name(id=func_name, ctx=ast.Load())

                args = [self._synapse_to_python_ast(arg) for arg in node.args]
                return ast.Call(func=func, args=args, keywords=[])

        # Default: return a constant None
        return ast.Constant(value=None)

    def _create_function_from_ast(self, py_ast: ast.AST) -> Callable:
        """Create Python function from AST"""
        # Wrap in function definition
        func_ast = ast.FunctionDef(
            name="compiled_func",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="x"), ast.arg(arg="y")],  # Default args
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ),
            body=[ast.Return(value=py_ast)],
            decorator_list=[]
        )

        # Create module
        module = ast.Module(body=[func_ast], type_ignores=[])
        ast.fix_missing_locations(module)

        # Compile and execute
        code = compile(module, "<jit>", "exec")
        namespace = {"np": np}
        exec(code, namespace)

        return namespace["compiled_func"]

    def _jit_compile(self, func: Callable) -> Callable:
        """Apply Numba JIT compilation"""
        return njit(cache=True)(func)

class VectorizedOps:
    """Vectorized operations for array processing"""

    @staticmethod
    @vectorize(["float64(float64, float64)"], target="parallel")
    def vadd(x, y):
        return x + y

    @staticmethod
    @vectorize(["float64(float64, float64)"], target="parallel")
    def vmul(x, y):
        return x * y

    @staticmethod
    @vectorize(["float64(float64)"], target="parallel")
    def vsin(x):
        return np.sin(x)

    @staticmethod
    @vectorize(["float64(float64)"], target="parallel")
    def vcos(x):
        return np.cos(x)

    @staticmethod
    @vectorize(["float64(float64)"], target="parallel")
    def vexp(x):
        return np.exp(x)

class ParallelExecutor:
    """Parallel execution engine using Numba"""

    @staticmethod
    @njit(parallel=True)
    def parallel_sum(arr):
        """Parallel sum reduction"""
        n = arr.shape[0]
        total = 0.0
        for i in prange(n):
            total += arr[i]
        return total

    @staticmethod
    @njit(parallel=True)
    def parallel_dot(a, b):
        """Parallel dot product"""
        n = a.shape[0]
        total = 0.0
        for i in prange(n):
            total += a[i] * b[i]
        return total

    @staticmethod
    @njit(parallel=True)
    def parallel_matmul(A, B):
        """Parallel matrix multiplication"""
        m, n = A.shape
        n2, p = B.shape
        C = np.zeros((m, p))

        for i in prange(m):
            for j in range(p):
                total = 0.0
                for k in range(n):
                    total += A[i, k] * B[k, j]
                C[i, j] = total
        return C

    @staticmethod
    @njit(parallel=True)
    def parallel_map(func_id, arr):
        """Parallel map operation"""
        n = arr.shape[0]
        result = np.zeros_like(arr)

        for i in prange(n):
            if func_id == 0:  # sin
                result[i] = np.sin(arr[i])
            elif func_id == 1:  # cos
                result[i] = np.cos(arr[i])
            elif func_id == 2:  # exp
                result[i] = np.exp(arr[i])
            elif func_id == 3:  # sqrt
                result[i] = np.sqrt(abs(arr[i]))
            else:
                result[i] = arr[i]

        return result

class JITCache:
    """Advanced caching for JIT-compiled functions"""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
        self.compile_time = {}

    def get(self, key: str) -> Callable | None:
        """Get compiled function from cache"""
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        return None

    def put(self, key: str, func: Callable, compile_time: float):
        """Store compiled function in cache"""
        if len(self.cache) >= self.max_size:
            # Evict least frequently used
            lfu_key = min(self.access_count, key=self.access_count.get)
            del self.cache[lfu_key]
            del self.access_count[lfu_key]
            if lfu_key in self.compile_time:
                del self.compile_time[lfu_key]

        self.cache[key] = func
        self.access_count[key] = 1
        self.compile_time[key] = compile_time

    def stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total_accesses = sum(self.access_count.values())
        total_compile_time = sum(self.compile_time.values())

        return {
            "size": len(self.cache),
            "total_accesses": total_accesses,
            "total_compile_time": total_compile_time,
            "avg_access_count": total_accesses / len(self.cache) if self.cache else 0,
            "most_used": max(self.access_count, key=self.access_count.get) if self.access_count else None
        }

def create_optimized_kernel(expression: str) -> Callable:
    """Create optimized kernel from expression string"""
    # Parse expression

    # Simple expression parser for common patterns
    if "+" in expression:
        @njit
        def kernel(x, y):
            return x + y
    elif "*" in expression:
        @njit
        def kernel(x, y):
            return x * y
    elif "sin" in expression:
        @njit
        def kernel(x):
            return np.sin(x)
    elif "exp" in expression:
        @njit
        def kernel(x):
            return np.exp(x)
    else:
        @njit
        def kernel(x):
            return x

    return kernel

def benchmark_jit():
    """Benchmark JIT compilation performance"""
    import time

    print("JIT Compilation Benchmark")
    print("=" * 50)

    # Test data
    n = 1000000
    x = np.random.random(n)
    y = np.random.random(n)

    # Python function
    def python_func(x, y):
        return np.sin(x) * np.cos(y) + np.exp(x * y)

    # JIT compiled function
    @njit
    def jit_func(x, y):
        return np.sin(x) * np.cos(y) + np.exp(x * y)

    # Vectorized function
    @vectorize(["float64(float64, float64)"], target="parallel")
    def vec_func(x, y):
        return np.sin(x) * np.cos(y) + np.exp(x * y)

    # Warmup
    _ = jit_func(x[:100], y[:100])
    _ = vec_func(x[:100], y[:100])

    # Benchmark Python
    start = time.perf_counter()
    python_func(x, y)
    py_time = time.perf_counter() - start

    # Benchmark JIT
    start = time.perf_counter()
    jit_func(x, y)
    jit_time = time.perf_counter() - start

    # Benchmark Vectorized
    start = time.perf_counter()
    vec_func(x, y)
    vec_time = time.perf_counter() - start

    print(f"Array size: {n:,}")
    print(f"Python:     {py_time:.3f}s")
    print(f"JIT:        {jit_time:.3f}s (speedup: {py_time/jit_time:.2f}x)")
    print(f"Vectorized: {vec_time:.3f}s (speedup: {py_time/vec_time:.2f}x)")

    # Test parallel operations
    print("\nParallel Operations:")

    A = np.random.random((1000, 1000))
    B = np.random.random((1000, 1000))

    # Standard matmul
    start = time.perf_counter()
    A @ B
    std_time = time.perf_counter() - start

    # Parallel matmul
    start = time.perf_counter()
    ParallelExecutor.parallel_matmul(A, B)
    par_time = time.perf_counter() - start

    print(f"Standard matmul: {std_time:.3f}s")
    print(f"Parallel matmul: {par_time:.3f}s (speedup: {std_time/par_time:.2f}x)")

if __name__ == "__main__":
    # Run benchmark
    benchmark_jit()

    # Test JIT compiler
    print("\nTesting JIT Compiler:")
    compiler = JITCompiler()

    # Create sample AST node
    from synapse_ast_complete import BinaryOpNode, NumberNode

    # Expression: 2 + 3
    ast_node = BinaryOpNode(
        left=NumberNode(2),
        op="+",
        right=NumberNode(3)
    )

    # Compile
    compiled = compiler.compile_expression(ast_node)
    if compiled:
        result = compiled(2, 3)
        print(f"Compiled result: {result}")

    print(f"Compilation stats: {compiler.compilation_stats}")
