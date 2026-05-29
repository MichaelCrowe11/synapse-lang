"""Synapse Language - Complete Implementation Package."""

from .__version__ import __version__
__author__ = "Michael Benjamin Crowe"

from .ast_consolidated import *

try:
    from .jit_compiler import JITCompiler, compile_synapse_code, synapse_jit

    JIT_AVAILABLE = True
except ImportError:
    JIT_AVAILABLE = False
    JITCompiler = None  # type: ignore[misc, assignment]
    compile_synapse_code = None  # type: ignore[misc, assignment]
    synapse_jit = None  # type: ignore[misc, assignment]

from .security import (
    ExecutionSandbox,
    ProcessSandbox,
    SecurityPolicy,
    create_quantum_sandbox,
    create_scientific_sandbox,
    sandboxed,
    sandboxed_context,
)
from .synapse_interpreter import SynapseInterpreter as Interpreter
from .synapse_lexer import Lexer, Token, TokenType

try:
    from .quantum.core import QuantumCircuitBuilder as QuantumCircuit
    from .quantum.core import SimulatorBackend as QuantumSimulator
    from .quantum.semantics import QuantumSemanticError
except ImportError:
    pass

try:
    from .uncertainty import (
        UncertaintyEngine,
        UncertainValue,
        monte_carlo,
        propagate_uncertainty,
        uncertain,
    )
    from .parallel import parallel_block, parameter_sweep

    UNCERTAINTY_AVAILABLE = True
except ImportError:
    UNCERTAINTY_AVAILABLE = False

    class UncertaintyEngine:
        def __init__(self, *args, **kwargs):
            pass

    class UncertainValue:
        def __init__(self, *args, **kwargs):
            pass

    def uncertain(*args, **kwargs):
        return None

    def monte_carlo(*args, **kwargs):
        raise ImportError("uncertainty module unavailable")

    def propagate_uncertainty(*args, **kwargs):
        raise ImportError("uncertainty module unavailable")

    def parallel_block(*args, **kwargs):
        raise ImportError("parallel module unavailable")

    def parameter_sweep(*args, **kwargs):
        raise ImportError("parallel module unavailable")

try:
    from .tensor_ops import TensorConfig, TensorEngine, create_tensor_engine

    TENSOR_AVAILABLE = True
except ImportError:
    TENSOR_AVAILABLE = False

    class TensorEngine:
        def __init__(self, *args, **kwargs):
            pass

    class TensorConfig:
        def __init__(self, *args, **kwargs):
            pass

    def create_tensor_engine(*args, **kwargs):
        return None

try:
    from .symbolic import SymbolicEngine, SymbolicExpression, symbolic_var

    SYMBOLIC_AVAILABLE = True
except ImportError:
    SYMBOLIC_AVAILABLE = False

    class SymbolicEngine:
        def __init__(self, *args, **kwargs):
            pass

    class SymbolicExpression:
        def __init__(self, *args, **kwargs):
            pass

    def symbolic_var(*args, **kwargs):
        return None


def __getattr__(name: str):
    if name == "EnhancedParser":
        from .parser_enhanced import EnhancedParser

        return EnhancedParser
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def parse(code: str) -> ASTNode:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    from .parser_enhanced import EnhancedParser

    return EnhancedParser(tokens).parse()


def compile(code: str, optimize: bool = True) -> callable:
    if not JIT_AVAILABLE:
        raise ImportError(
            "numba is required for compilation. Install with: pip install synapse-lang[jit]"
        )
    from .jit_compiler import CompilationConfig

    config = CompilationConfig(
        parallel=optimize,
        fastmath=optimize,
        optimize_level=3 if optimize else 0,
    )
    return compile_synapse_code(code, config)


def execute(code: str, sandbox: bool = True, context: dict | None = None) -> any:
    interpreter = Interpreter()
    if context:
        interpreter.variables.update(context)
    return interpreter.execute(code)


def run_file(filepath: str, sandbox: bool = True) -> any:
    with open(filepath) as f:
        code = f.read()
    return execute(code, sandbox)


def main():
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Synapse Language Interpreter")
    parser.add_argument("file", nargs="?", help="Synapse source file to run")
    parser.add_argument("--compile", action="store_true", help="Compile to optimized code")
    parser.add_argument("--no-sandbox", action="store_true", help="Disable security sandbox")
    parser.add_argument("--repl", action="store_true", help="Start interactive REPL")
    parser.add_argument("--version", action="version", version=f"Synapse {__version__}")

    args = parser.parse_args()

    if args.repl or not args.file:
        root = Path(__file__).resolve().parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from synapse_repl import REPL

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


__all__ = [
    "Lexer",
    "Token",
    "TokenType",
    "Interpreter",
    "EnhancedParser",
    "ASTNode",
    "ProgramNode",
    "NumberNode",
    "StringNode",
    "IdentifierNode",
    "BinaryOpNode",
    "UnaryOpNode",
    "HypothesisNode",
    "ExperimentNode",
    "ParallelNode",
    "QuantumCircuitNode",
    "QuantumGateNode",
    "JITCompiler",
    "compile_synapse_code",
    "synapse_jit",
    "ExecutionSandbox",
    "SecurityPolicy",
    "sandboxed",
    "parse",
    "compile",
    "execute",
    "run_file",
    "monte_carlo",
    "parallel_block",
    "parameter_sweep",
    "__version__",
]
