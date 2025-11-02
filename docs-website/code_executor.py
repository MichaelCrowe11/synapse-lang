#!/usr/bin/env python3
"""
Secure code execution engine for Synapse Language playground
"""

import ast
import contextlib
import io
import json

# Add synapse_lang to path
import os
import signal
import sys
import time
import traceback
from typing import Any

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)  # Add parent directory containing synapse_lang
sys.path.insert(0, "/app")  # For production environment

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Code execution timed out")

class SecureExecutor:
    """Secure code execution with sandboxing"""

    def __init__(self, max_time: int = 5, max_memory: int = 50 * 1024 * 1024):
        self.max_time = max_time
        self.max_memory = max_memory
        self.safe_builtins = {
            "abs": abs, "all": all, "any": any, "ascii": ascii,
            "bin": bin, "bool": bool, "bytes": bytes, "chr": chr,
            "complex": complex, "dict": dict, "divmod": divmod,
            "enumerate": enumerate, "filter": filter, "float": float,
            "format": format, "frozenset": frozenset, "hex": hex,
            "int": int, "isinstance": isinstance, "issubclass": issubclass,
            "iter": iter, "len": len, "list": list, "map": map,
            "max": max, "min": min, "next": next, "oct": oct,
            "ord": ord, "pow": pow, "print": print, "range": range,
            "repr": repr, "reversed": reversed, "round": round,
            "set": set, "slice": slice, "sorted": sorted, "str": str,
            "sum": sum, "tuple": tuple, "type": type, "zip": zip,
            # Import function for safe modules only
            "__import__": lambda name, *args, **kwargs: (
                __import__(name, *args, **kwargs)
                if name in ["math", "random", "datetime", "json", "synapse_lang", "numpy", "scipy"]
                else (_ for _ in ()).throw(ImportError(f"Module '{name}' is not allowed"))
            ),
            # Standard exceptions
            "Exception": Exception,
            "ImportError": ImportError,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "KeyError": KeyError,
            "IndexError": IndexError,
            "AttributeError": AttributeError,
        }

        # Blocked functions/modules for security
        self.blocked = {
            "__import__", "eval", "exec", "open", "input", "compile",
            "globals", "locals", "vars", "dir", "help", "quit", "exit",
            "os", "sys", "subprocess", "socket", "requests", "urllib",
            "pickle", "marshal", "importlib", "__builtins__"
        }

    def validate_code(self, code: str) -> bool:
        """Validate code for security issues"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Check for import statements
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in ["math", "random", "datetime", "json",
                                             "synapse_lang", "numpy", "scipy"]:
                            return False

                # Check for dangerous attribute access
                if isinstance(node, ast.Attribute):
                    if node.attr in ["__class__", "__bases__", "__globals__",
                                    "__code__", "__closure__", "__subclasses__"]:
                        return False

                # Check for exec/eval
                if isinstance(node, ast.Name):
                    if node.id in self.blocked:
                        return False

            return True
        except SyntaxError:
            return False

    def execute_synapse_code(self, code: str) -> dict[str, Any]:
        """Execute Synapse Language code safely"""
        start_time = time.time()

        # Validate code first
        if not self.validate_code(code):
            return {
                "success": False,
                "error": "Code contains restricted operations",
                "output": "",
                "execution_time": 0
            }

        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.max_time)

        # Capture output
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()

        # Create safe namespace
        safe_namespace = {"__builtins__": self.safe_builtins}

        # Import Synapse modules safely
        try:
            import synapse_lang
            safe_namespace["synapse_lang"] = synapse_lang
            safe_namespace["UncertainValue"] = synapse_lang.UncertainValue
            safe_namespace["QuantumCircuit"] = synapse_lang.QuantumCircuit
            safe_namespace["TypeInference"] = synapse_lang.TypeInference
            safe_namespace["ParallelCompute"] = synapse_lang.ParallelCompute
            safe_namespace["BlockchainVerifier"] = synapse_lang.BlockchainVerifier

            # Import numpy/scipy if available
            try:
                import numpy as np
                safe_namespace["np"] = np
                safe_namespace["numpy"] = np
            except ImportError:
                pass

            try:
                import scipy
                safe_namespace["scipy"] = scipy
            except ImportError:
                pass

        except ImportError:
            pass

        result = {
            "success": False,
            "output": "",
            "error": "",
            "execution_time": 0,
            "memory_used": "0 MB"
        }

        try:
            # Execute code with output capture
            with contextlib.redirect_stdout(output_buffer):
                with contextlib.redirect_stderr(error_buffer):
                    exec(code, safe_namespace)

            # Cancel timeout
            signal.alarm(0)

            execution_time = time.time() - start_time

            result["success"] = True
            result["output"] = output_buffer.getvalue()
            result["execution_time"] = round(execution_time, 3)

            # Get memory usage (approximate)
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                result["memory_used"] = f"{memory_mb:.1f} MB"
            except ImportError:
                # Fallback if psutil not available
                import resource
                memory_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
                result["memory_used"] = f"{memory_mb:.1f} MB"

        except TimeoutException:
            signal.alarm(0)
            result["error"] = "Execution timed out (5 second limit)"

        except Exception as e:
            signal.alarm(0)
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()

        finally:
            # Ensure timeout is cancelled
            signal.alarm(0)

        return result

def execute_python_code(code: str) -> dict[str, Any]:
    """Execute regular Python code safely"""
    executor = SecureExecutor()
    return executor.execute_synapse_code(code)

def execute_synapse_specific(code: str) -> dict[str, Any]:
    """Execute Synapse-specific code with special features"""
    # Preprocess Synapse syntax if needed
    processed_code = preprocess_synapse_syntax(code)
    executor = SecureExecutor()
    return executor.execute_synapse_code(processed_code)

def preprocess_synapse_syntax(code: str) -> str:
    """Convert Synapse-specific syntax to Python"""
    # Handle uncertainty operator ±
    code = code.replace("±", ", uncertainty=")

    # Handle quantum operators
    code = code.replace("|0⟩", "QuantumCircuit.zero_state()")
    code = code.replace("|1⟩", "QuantumCircuit.one_state()")

    # Handle special Synapse keywords
    code = code.replace("uncertain ", "UncertainValue(")
    code = code.replace("quantum ", "QuantumCircuit(")
    code = code.replace("verify ", "BlockchainVerifier.verify(")

    return code

if __name__ == "__main__":
    # Test the executor
    test_code = """
from synapse_lang import UncertainValue, QuantumCircuit

# Create uncertain value
value = UncertainValue(10.0, uncertainty=0.5)
print(f"Value: {value}")

# Create quantum circuit
qc = QuantumCircuit(2)
qc.hadamard(0)
qc.cnot(0, 1)
print(f"Quantum circuit created with {qc.num_qubits} qubits")

# Math operations
import math
print(f"Sin(π/2) = {math.sin(math.pi/2)}")
"""

    result = execute_python_code(test_code)
    print(json.dumps(result, indent=2))
