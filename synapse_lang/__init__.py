"""Synapse Language - Complete Implementation Package."""

__version__ = "2.0.0"
__author__ = "Synapse Development Team"

# Core language components
from .synapse_lexer import Lexer, Token, TokenType
from .parser_enhanced import EnhancedParser
from .ast_consolidated import *
from .synapse_interpreter import SynapseInterpreter as Interpreter

# Advanced features
from .jit_compiler import JITCompiler, compile_synapse_code, synapse_jit
from .security import (
    ExecutionSandbox, 
    ProcessSandbox,
    SecurityPolicy,
    sandboxed,
    sandboxed_context,
    create_scientific_sandbox,
    create_quantum_sandbox
)

# Quantum computing - import only what exists
try:
    from .quantum.core import QuantumCircuitBuilder as QuantumCircuit, SimulatorBackend as QuantumSimulator
    from .quantum.semantics import QuantumSemanticError
except ImportError:
    # Quantum modules may not be fully available
    pass

# Scientific computing - import with fallbacks
try:
    from .uncertainty import UncertaintyEngine, UncertainValue, uncertain
    UNCERTAINTY_AVAILABLE = True
except ImportError:
    UNCERTAINTY_AVAILABLE = False
    # Create fallback classes
    class UncertaintyEngine:
        def __init__(self, *args, **kwargs): pass
    class UncertainValue:
        def __init__(self, *args, **kwargs): pass
    def uncertain(*args, **kwargs): return None

try:
    from .tensor_ops import TensorEngine, TensorConfig, create_tensor_engine
    TENSOR_AVAILABLE = True
except ImportError:
    TENSOR_AVAILABLE = False
    class TensorEngine:
        def __init__(self, *args, **kwargs): pass
    class TensorConfig:
        def __init__(self, *args, **kwargs): pass
    def create_tensor_engine(*args, **kwargs): return None

try:
    from .symbolic import SymbolicEngine, SymbolicExpression, symbolic_var
    SYMBOLIC_AVAILABLE = True
except ImportError:
    SYMBOLIC_AVAILABLE = False
    class SymbolicEngine:
        def __init__(self, *args, **kwargs): pass
    class SymbolicExpression:
        def __init__(self, *args, **kwargs): pass
    def symbolic_var(*args, **kwargs): return None

# High-level API
def parse(code: str) -> ASTNode:
    """Parse Synapse code into AST."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = EnhancedParser(tokens)
    return parser.parse()


def compile(code: str, optimize: bool = True) -> callable:
    """Compile Synapse code to optimized machine code."""
    from .jit_compiler import CompilationConfig
    
    config = CompilationConfig(
        parallel=optimize,
        fastmath=optimize,
        optimize_level=3 if optimize else 0
    )
    
    return compile_synapse_code(code, config)


def execute(code: str, sandbox: bool = True, context: dict = None) -> any:
    """Execute Synapse code with optional sandboxing."""
    if sandbox:
        sandbox_exec = create_scientific_sandbox()
        return sandbox_exec.execute(code, context)
    else:
        ast = parse(code)
        interpreter = Interpreter()
        return interpreter.execute(ast, context or {})


def run_file(filepath: str, sandbox: bool = True) -> any:
    """Run a Synapse source file."""
    with open(filepath, 'r') as f:
        code = f.read()
    return execute(code, sandbox)


# CLI entry point
def main():
    """Main CLI entry point."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Synapse Language Interpreter')
    parser.add_argument('file', nargs='?', help='Synapse source file to run')
    parser.add_argument('--compile', action='store_true', help='Compile to optimized code')
    parser.add_argument('--no-sandbox', action='store_true', help='Disable security sandbox')
    parser.add_argument('--repl', action='store_true', help='Start interactive REPL')
    parser.add_argument('--version', action='version', version=f'Synapse {__version__}')
    
    args = parser.parse_args()
    
    if args.repl or not args.file:
        from .synapse_repl import REPL
        repl = REPL(sandbox=not args.no_sandbox)
        repl.run()
    elif args.file:
        try:
            if args.compile:
                compiled = compile(open(args.file).read())
                result = compiled()
            else:
                result = run_file(args.file, sandbox=not args.no_sandbox)
            
            if result is not None:
                print(result)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


# Export main components
__all__ = [
    # Core
    'Lexer', 'Token', 'TokenType',
    'EnhancedParser', 'Interpreter',
    
    # AST Nodes
    'ASTNode', 'ProgramNode', 'NumberNode', 'StringNode',
    'IdentifierNode', 'BinaryOpNode', 'UnaryOpNode',
    'HypothesisNode', 'ExperimentNode', 'ParallelNode',
    'QuantumCircuitNode', 'QuantumGateNode',
    
    # Compilation
    'JITCompiler', 'compile_synapse_code', 'synapse_jit',
    
    # Security
    'ExecutionSandbox', 'SecurityPolicy', 'sandboxed',
    
    # High-level API
    'parse', 'compile', 'execute', 'run_file',
    
    # Version
    '__version__'
]