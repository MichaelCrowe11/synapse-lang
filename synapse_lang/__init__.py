"""Synapse language API. Optional scientific engines load on first access."""
from __future__ import annotations

from importlib import import_module
from importlib.util import find_spec

from .__version__ import __version__
from .ast_consolidated import *

__author__ = "Michael Benjamin Crowe"

_LAZY = {
    "Interpreter": ("synapse_interpreter", "SynapseInterpreter"),
    "EnhancedParser": ("parser_enhanced", "EnhancedParser"),
    "Lexer": ("synapse_lexer", "Lexer"),
    "Token": ("synapse_lexer", "Token"),
    "TokenType": ("synapse_lexer", "TokenType"),
    "QuantumCircuit": ("quantum.core", "QuantumCircuitBuilder"),
    "QuantumSimulator": ("quantum.core", "SimulatorBackend"),
    "QuantumSemanticError": ("quantum.semantics", "QuantumSemanticError"),
}
for _module, _names in {
    "jit_compiler": ("JITCompiler", "compile_synapse_code", "synapse_jit"),
    "security": ("ExecutionSandbox", "ProcessSandbox", "SecurityPolicy",
                 "create_quantum_sandbox", "create_scientific_sandbox",
                 "sandboxed", "sandboxed_context"),
    "uncertainty": ("UncertaintyEngine", "UncertainValue", "monte_carlo",
                    "propagate_uncertainty", "uncertain"),
    "parallel": ("parallel_block", "parameter_sweep"),
    "tensor_ops": ("TensorConfig", "TensorEngine", "create_tensor_engine"),
    "symbolic": ("SymbolicEngine", "SymbolicExpression", "symbolic_var"),
}.items():
    _LAZY.update({name: (_module, name) for name in _names})


def __getattr__(name):
    requirements = {
        "JIT_AVAILABLE": ("numba",),
        "UNCERTAINTY_AVAILABLE": ("numpy", "scipy"),
        "TENSOR_AVAILABLE": ("numpy", "numba"),
        "SYMBOLIC_AVAILABLE": ("numpy", "sympy"),
    }
    if name in requirements:
        return all(find_spec(package) is not None for package in requirements[name])
    if name not in _LAZY:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module, attribute = _LAZY[name]
    value = getattr(import_module(f".{module}", __name__), attribute)
    globals()[name] = value
    return value


def parse(code):
    """Parse once; reuse the returned AST with execute_program()."""
    from .synapse_interpreter import parse as parse_source

    return parse_source(code)


def compile(code, optimize=True):
    """Compile supported numeric programs with Numba; fastmath stays disabled."""
    from .jit_compiler import CompilationConfig, compile_synapse_code

    return compile_synapse_code(code, CompilationConfig(
        parallel=optimize, fastmath=False, optimize_level=3 if optimize else 0,
    ))


def execute_program(program, sandbox=False, context=None, *, parallel=False):
    """Execute a parsed program in fresh state. Not a security sandbox."""
    if sandbox:
        raise NotImplementedError(
            "Synapse runtime isolation is unavailable; sandbox=True is refused. "
            "Use sandbox=False only for trusted code and context."
        )
    from .synapse_interpreter import SynapseInterpreter

    return SynapseInterpreter(parallel=parallel).execute_program(program, context)


def execute(code, sandbox=False, context=None, *, parallel=False):
    """Execute trusted source. Explicit sandbox requests fail closed."""
    if sandbox:
        return execute_program(None, sandbox=True)
    return execute_program(parse(code), context=context, parallel=parallel)


def run_file(filepath, sandbox=False, *, parallel=False):
    with open(filepath, encoding="utf-8") as source:
        return execute(source.read(), sandbox=sandbox, parallel=parallel)


def main():
    from .cli import main as cli_main

    return cli_main()


__all__ = list(_LAZY) + [
    "ASTNode", "ProgramNode", "NumberNode", "StringNode", "IdentifierNode",
    "BinaryOpNode", "UnaryOpNode", "HypothesisNode", "ExperimentNode",
    "ParallelNode", "QuantumCircuitNode", "QuantumGateNode", "parse", "compile",
    "execute", "execute_program", "run_file", "__version__",
]
