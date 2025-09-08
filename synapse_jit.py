"""
JIT Compilation for Synapse Language
Compiles Synapse AST to optimized Python bytecode and native code
"""

import ast as py_ast
import types
import dis
from typing import Any, Dict, Optional
import numpy as np

try:
    import numba
    from numba import jit, njit, prange
except ImportError as e:
    raise ImportError(
        "The 'numba' package is required for JIT compilation but was not found. "
        "Please install it with 'pip install numba'."
    ) from e

import inspect
from synapse_ast import *
from synapse_parser import parse

class SynapseToPythonTranspiler(ASTVisitor):
    """Transpile Synapse AST to Python AST for JIT compilation"""
    
    def __init__(self):
        self.imports = set()
        self.parallel_imports = False
    
    def transpile(self, node: ASTNode) -> py_ast.Module:
        """Convert Synapse AST to Python AST"""
        body = []
        
        # Add necessary imports
        if self.parallel_imports:
            body.append(py_ast.Import(names=[py_ast.alias(name='numpy', asname='np')]))
            body.append(py_ast.ImportFrom(
                module='numba',
                names=[py_ast.alias(name='prange', asname=None)],
                level=0
            ))
        
        # Visit the Synapse AST
        if isinstance(node, ProgramNode):
            for stmt in node.body:
                py_stmt = self.visit(stmt)
                if py_stmt:
                    if isinstance(py_stmt, list):
                        body.extend(py_stmt)
                    else:
                        body.append(py_stmt)
        else:
            py_stmt = self.visit(node)
            if py_stmt:
                body.append(py_stmt)
        
        return py_ast.Module(body=body, type_ignores=[])
    
    def visit_program(self, node: ProgramNode):
        """Visit program node"""
        body = []
        for stmt in node.body:
            py_stmt = self.visit(stmt)
            if py_stmt:
                if isinstance(py_stmt, list):
                    body.extend(py_stmt)
                else:
                    body.append(py_stmt)
        return body
    
    def visit_number(self, node: NumberNode):
        """Convert number to Python AST"""
        return py_ast.Constant(value=node.value)
    
    def visit_string(self, node: StringNode):
        """Convert string to Python AST"""
        return py_ast.Constant(value=node.value)
    
    def visit_identifier(self, node: IdentifierNode):
        """Convert identifier to Python AST"""
        return py_ast.Name(id=node.name, ctx=py_ast.Load())
    
    def visit_uncertain(self, node: UncertainNode):
        """Convert uncertain value to Python AST"""
        # Create a tuple (value, uncertainty)
        return py_ast.Tuple(
            elts=[
                py_ast.Constant(value=node.value),
                py_ast.Constant(value=node.uncertainty)
            ],
            ctx=py_ast.Load()
        )
    
    def visit_binary_op(self, node: BinaryOpNode):
        """Convert binary operation to Python AST"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        op_map = {
            '+': py_ast.Add(),
            '-': py_ast.Sub(),
            '*': py_ast.Mult(),
            '/': py_ast.Div(),
            '^': py_ast.Pow(),
            '==': py_ast.Eq(),
            '!=': py_ast.NotEq(),
            '<': py_ast.Lt(),
            '>': py_ast.Gt(),
            '&&': py_ast.And(),
            '||': py_ast.Or()
        }
        
        if node.operator in ['&&', '||']:
            return py_ast.BoolOp(op=op_map[node.operator], values=[left, right])
        else:
            return py_ast.BinOp(left=left, op=op_map.get(node.operator, py_ast.Add()), right=right)
    
    def visit_unary_op(self, node: UnaryOpNode):
        """Convert unary operation to Python AST"""
        operand = self.visit(node.operand)
        
        op_map = {
            '-': py_ast.USub(),
            '!': py_ast.Not()
        }
        
        if node.operator == '!':
            return py_ast.UnaryOp(op=py_ast.Not(), operand=operand)
        else:
            return py_ast.UnaryOp(op=op_map.get(node.operator, py_ast.USub()), operand=operand)
    
    def visit_assignment(self, node: AssignmentNode):
        """Convert assignment to Python AST"""
        target = py_ast.Name(id=node.target.name, ctx=py_ast.Store())
        value = self.visit(node.value)
        
        return py_ast.Assign(targets=[target], value=value)
    
    def visit_function_call(self, node: FunctionCallNode):
        """Convert function call to Python AST"""
        func = py_ast.Name(id=node.function.name, ctx=py_ast.Load())
        args = [self.visit(arg) for arg in node.arguments]
        
        return py_ast.Call(func=func, args=args, keywords=[])
    
    def visit_parallel(self, node: ParallelNode):
        """Convert parallel block to Python AST with numba prange"""
        self.parallel_imports = True
        
        # Create a parallel loop using numba's prange
        # This is a simplified version - real implementation would be more complex
        
        body = []
        for i, branch in enumerate(node.branches):
            # Create a function for each branch
            func_name = f"branch_{branch.name}"
            branch_func = py_ast.FunctionDef(
                name=func_name,
                args=py_ast.arguments(
                    posonlyargs=[],
                    args=[],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[]
                ),
                body=[self.visit(branch.body)] if branch.body else [py_ast.Pass()],
                decorator_list=[py_ast.Name(id='njit', ctx=py_ast.Load())],
                returns=None
            )
            body.append(branch_func)
            
            # Call the function
            body.append(py_ast.Expr(value=py_ast.Call(
                func=py_ast.Name(id=func_name, ctx=py_ast.Load()),
                args=[],
                keywords=[]
            )))
        
        return body
    
    def visit_block(self, node: BlockNode):
        """Convert block to Python AST"""
        body = []
        for stmt in node.statements:
            py_stmt = self.visit(stmt)
            if py_stmt:
                if isinstance(py_stmt, list):
                    body.extend(py_stmt)
                else:
                    body.append(py_stmt)
        return body

class JITCompiler:
    """JIT compiler for Synapse using Numba"""
    
    def __init__(self):
        self.transpiler = SynapseToPythonTranspiler()
        self.compiled_functions = {}
        self.cache = {}
    
    def compile_function(self, synapse_code: str, function_name: str = "synapse_func"):
        """Compile Synapse code to optimized function"""
        
        # Check cache
        if synapse_code in self.cache:
            return self.cache[synapse_code]
        
        # Parse Synapse code to AST
        synapse_ast = parse(synapse_code)
        
        # Transpile to Python AST
        py_ast_module = self.transpiler.transpile(synapse_ast)
        
        # Add function wrapper
        func_ast = py_ast.FunctionDef(
            name=function_name,
            args=py_ast.arguments(
                posonlyargs=[],
                args=[py_ast.arg(arg='args', annotation=None)],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ),
            body=py_ast_module.body if py_ast_module.body else [py_ast.Pass()],
            decorator_list=[],
            returns=None
        )
        
        # Create module with function
        module_ast = py_ast.Module(body=[func_ast], type_ignores=[])
        
        # Compile to bytecode
        py_ast.fix_missing_locations(module_ast)
        code = compile(module_ast, '<synapse>', 'exec')
        
        # Execute to get function
        namespace = {'np': np, 'numba': numba, 'njit': njit, 'prange': prange}
        exec(code, namespace)
        func = namespace[function_name]
        
        # Apply Numba JIT compilation for numerical functions
        try:
            jit_func = njit(func)
            self.cache[synapse_code] = jit_func
            return jit_func
        except:
            # Fall back to regular Python if Numba fails
            self.cache[synapse_code] = func
            return func
    
    def compile_numerical(self, func, signature=None):
        """Compile a numerical function with Numba"""
        if signature:
            return njit(signature)(func)
        return njit(func)
    
    def compile_parallel(self, func, signature=None):
        """Compile a parallel function with Numba"""
        if signature:
            return njit(signature, parallel=True)(func)
        return njit(parallel=True)(func)
    
    def optimize_uncertain_arithmetic(self, func):
        """Optimize uncertain value arithmetic"""
        
        @njit
        def propagate_uncertainty(val1, unc1, val2, unc2, operation):
            if operation == 0:  # Addition
                result = val1 + val2
                uncertainty = np.sqrt(unc1**2 + unc2**2)
            elif operation == 1:  # Subtraction
                result = val1 - val2
                uncertainty = np.sqrt(unc1**2 + unc2**2)
            elif operation == 2:  # Multiplication
                result = val1 * val2
                rel_unc1 = unc1 / val1 if val1 != 0 else 0
                rel_unc2 = unc2 / val2 if val2 != 0 else 0
                uncertainty = result * np.sqrt(rel_unc1**2 + rel_unc2**2)
            elif operation == 3:  # Division
                result = val1 / val2 if val2 != 0 else 0
                rel_unc1 = unc1 / val1 if val1 != 0 else 0
                rel_unc2 = unc2 / val2 if val2 != 0 else 0
                uncertainty = result * np.sqrt(rel_unc1**2 + rel_unc2**2)
            else:
                result = val1
                uncertainty = unc1
            
            return result, uncertainty
        
        return propagate_uncertainty
    
    def compile_tensor_operation(self, operation: str):
        """Compile tensor operations for performance"""
        
        if operation == "matmul":
            @njit(parallel=True)
            def matmul(A, B):
                m, k = A.shape
                k2, n = B.shape
                assert k == k2, "Matrix dimensions don't match"
                C = np.zeros((m, n))
                for i in prange(m):
                    for j in range(n):
                        for l in range(k):
                            C[i, j] += A[i, l] * B[l, j]
                return C
            return matmul
        
        elif operation == "conv2d":
            @njit(parallel=True)
            def conv2d(image, kernel):
                ih, iw = image.shape
                kh, kw = kernel.shape
                oh = ih - kh + 1
                ow = iw - kw + 1
                output = np.zeros((oh, ow))
                
                for i in prange(oh):
                    for j in range(ow):
                        for ki in range(kh):
                            for kj in range(kw):
                                output[i, j] += image[i + ki, j + kj] * kernel[ki, kj]
                return output
            return conv2d
        
        elif operation == "reduce_sum":
            @njit(parallel=True)
            def reduce_sum(tensor, axis=None):
                if axis is None:
                    return np.sum(tensor)
                return np.sum(tensor, axis=axis)
            return reduce_sum
        
        return None

class ParallelExecutor:
    """Execute Synapse parallel blocks efficiently"""
    
    def __init__(self, n_workers=None):
        import multiprocessing
        self.n_workers = n_workers or multiprocessing.cpu_count()
        try:
            from numba import njit, prange
            self.njit = njit
            self.prange = prange
        except ImportError as e:
            raise ImportError(
                "The 'numba' package is required for parallel execution but was not found. "
                "Please install it with 'pip install numba'."
            ) from e
    
    @staticmethod
    def parallel_map_numba(func, data):
        """Parallel map using Numba"""
        try:
            from numba import njit, prange
        except ImportError as e:
            raise ImportError(
                "The 'numba' package is required for parallel execution but was not found. "
                "Please install it with 'pip install numba'."
            ) from e
        n = len(data)
        results = np.empty(n, dtype=data.dtype)
        @njit(parallel=True)
        def _map(func, data, results):
            for i in prange(n):
                results[i] = func(data[i])
        _map(func, data, results)
        return results

    @staticmethod
    def parallel_reduce(func, data, initial=0):
        """Parallel reduction operation"""
        from functools import reduce
        import concurrent.futures
        
        def chunk_reduce(chunk):
            return reduce(func, chunk, initial)
        
        # Split data into chunks
        n = len(data)
        chunk_size = max(1, n // 8)
        chunks = [data[i:i+chunk_size] for i in range(0, n, chunk_size)]
        
        # Process chunks in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            chunk_results = list(executor.map(chunk_reduce, chunks))
        
        # Final reduction
        return reduce(func, chunk_results, initial)

# Example usage functions
def create_jit_example():
    """Example of JIT compilation"""
    
    compiler = JITCompiler()
    
    # Example 1: Compile uncertain arithmetic
    uncertain_add = compiler.optimize_uncertain_arithmetic(None)
    
    # Example 2: Compile matrix multiplication
    matmul = compiler.compile_tensor_operation("matmul")
    
    # Example 3: Compile convolution
    conv2d = compiler.compile_tensor_operation("conv2d")
    
    return {
        'uncertain_add': uncertain_add,
        'matmul': matmul,
        'conv2d': conv2d
    }

# Benchmark utilities
def benchmark_jit():
    """Benchmark JIT compilation performance"""
    import time
    
    # Create test data
    size = 1000
    A = np.random.randn(size, size)
    B = np.random.randn(size, size)
    
    # Python version
    start = time.time()
    C_python = np.dot(A, B)
    python_time = time.time() - start
    
    # JIT version
    compiler = JITCompiler()
    matmul_jit = compiler.compile_tensor_operation("matmul")
    
    # Warm up JIT
    matmul_jit(A[:10, :10], B[:10, :10])
    
    start = time.time()
    C_jit = matmul_jit(A, B)
    jit_time = time.time() - start
    
    return {
        'python_time': python_time,
        'jit_time': jit_time,
        'speedup': python_time / jit_time,
        'results_match': np.allclose(C_python, C_jit)
    }