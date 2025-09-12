"""Security sandboxing and resource management for Synapse execution."""

import ast
import sys
import time
import threading
import traceback
import multiprocessing
from typing import Any, Dict, Optional, Set, Callable, List
from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps
import signal
import os


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    # Resource limits
    max_memory_mb: int = 512
    max_cpu_seconds: int = 30
    max_file_size_mb: int = 10
    max_open_files: int = 100
    max_threads: int = 10
    max_processes: int = 5
    
    # Execution limits
    max_recursion_depth: int = 1000
    max_loop_iterations: int = 1000000
    max_quantum_qubits: int = 30
    max_tensor_size: int = 100000000  # 100M elements
    
    # Access controls
    allowed_modules: Set[str] = None
    forbidden_modules: Set[str] = None
    allowed_builtins: Set[str] = None
    forbidden_builtins: Set[str] = None
    
    # File system access
    allowed_read_paths: List[str] = None
    allowed_write_paths: List[str] = None
    sandbox_directory: Optional[str] = None
    
    # Network access
    allow_network: bool = False
    allowed_hosts: Set[str] = None
    
    def __post_init__(self):
        """Initialize default allowed/forbidden sets."""
        if self.allowed_modules is None:
            self.allowed_modules = {
                'math', 'numpy', 'scipy', 'sympy',
                'uncertainties', 'qiskit', 'cirq',
                'pandas', 'matplotlib', 'json', 'csv'
            }
        
        if self.forbidden_modules is None:
            self.forbidden_modules = {
                'os', 'sys', 'subprocess', 'socket',
                'urllib', 'requests', 'shutil', 'pickle',
                '__builtins__', 'eval', 'exec', 'compile'
            }
        
        if self.allowed_builtins is None:
            self.allowed_builtins = {
                'abs', 'all', 'any', 'ascii', 'bin', 'bool',
                'bytearray', 'bytes', 'callable', 'chr', 'complex',
                'dict', 'divmod', 'enumerate', 'filter', 'float',
                'format', 'frozenset', 'hex', 'id', 'int', 'isinstance',
                'issubclass', 'iter', 'len', 'list', 'map', 'max',
                'min', 'next', 'object', 'oct', 'ord', 'pow', 'print',
                'range', 'repr', 'reversed', 'round', 'set', 'slice',
                'sorted', 'str', 'sum', 'tuple', 'type', 'zip'
            }
        
        if self.forbidden_builtins is None:
            self.forbidden_builtins = {
                'eval', 'exec', 'compile', '__import__',
                'open', 'input', 'breakpoint', 'globals',
                'locals', 'vars', 'dir', 'help'
            }


class SecurityViolation(Exception):
    """Raised when security policy is violated."""
    pass


class ResourceExhausted(Exception):
    """Raised when resource limits are exceeded."""
    pass


class ExecutionTimeout(Exception):
    """Raised when execution time limit is exceeded."""
    pass


class SandboxedNamespace:
    """Sandboxed namespace for code execution."""
    
    def __init__(self, policy: SecurityPolicy):
        self.policy = policy
        self.namespace = {}
        self._setup_namespace()
    
    def _setup_namespace(self):
        """Setup safe namespace with restricted builtins."""
        # Create restricted builtins
        safe_builtins = {}
        
        for name in self.policy.allowed_builtins:
            if hasattr(__builtins__, name):
                safe_builtins[name] = getattr(__builtins__, name)
        
        # Add safe import function
        safe_builtins['__import__'] = self._safe_import
        
        self.namespace['__builtins__'] = safe_builtins
        self.namespace['__name__'] = '__sandboxed__'
        self.namespace['__doc__'] = None
    
    def _safe_import(self, name, *args, **kwargs):
        """Safe import that checks against policy."""
        # Check if module is forbidden
        if name in self.policy.forbidden_modules:
            raise SecurityViolation(f"Import of module '{name}' is forbidden")
        
        # Check if module is in allowed list
        if self.policy.allowed_modules and name not in self.policy.allowed_modules:
            raise SecurityViolation(f"Import of module '{name}' is not allowed")
        
        # Perform the import
        return __import__(name, *args, **kwargs)
    
    def update(self, items: Dict[str, Any]):
        """Update namespace with new items."""
        for key, value in items.items():
            if callable(value):
                # Wrap functions with security checks
                self.namespace[key] = self._wrap_function(value)
            else:
                self.namespace[key] = value
    
    def _wrap_function(self, func: Callable) -> Callable:
        """Wrap function with security checks."""
        @wraps(func)
        def wrapped(*args, **kwargs):
            # Check recursion depth
            if sys.getrecursionlimit() > self.policy.max_recursion_depth:
                raise ResourceExhausted("Maximum recursion depth exceeded")
            
            return func(*args, **kwargs)
        
        return wrapped


class CodeValidator:
    """Validates code against security policy."""
    
    def __init__(self, policy: SecurityPolicy):
        self.policy = policy
        self.loop_depth = 0
        self.function_calls = set()
    
    def validate(self, code: str) -> bool:
        """Validate code string against policy."""
        try:
            tree = ast.parse(code)
            self._validate_ast(tree)
            return True
        except SyntaxError as e:
            raise ValueError(f"Invalid syntax: {e}")
        except SecurityViolation:
            raise
    
    def _validate_ast(self, node: ast.AST):
        """Recursively validate AST nodes."""
        # Check for forbidden constructs
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split('.')[0]
                if module_name in self.policy.forbidden_modules:
                    raise SecurityViolation(f"Import of '{module_name}' is forbidden")
        
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module.split('.')[0] if node.module else ''
            if module_name in self.policy.forbidden_modules:
                raise SecurityViolation(f"Import from '{module_name}' is forbidden")
        
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check for dangerous function names
            if node.name.startswith('_'):
                raise SecurityViolation(f"Private function '{node.name}' not allowed")
        
        elif isinstance(node, ast.Call):
            # Check for dangerous function calls
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in self.policy.forbidden_builtins:
                    raise SecurityViolation(f"Call to '{func_name}' is forbidden")
                self.function_calls.add(func_name)
        
        elif isinstance(node, (ast.For, ast.While)):
            # Track loop depth for nested loop detection
            self.loop_depth += 1
            if self.loop_depth > 10:
                raise SecurityViolation("Excessive loop nesting depth")
        
        elif isinstance(node, ast.Exec):
            raise SecurityViolation("Use of 'exec' is forbidden")
        
        elif isinstance(node, ast.Eval):
            raise SecurityViolation("Use of 'eval' is forbidden")
        
        # Recursively validate child nodes
        for child in ast.iter_child_nodes(node):
            self._validate_ast(child)
        
        # Decrement loop depth when exiting loop
        if isinstance(node, (ast.For, ast.While)):
            self.loop_depth -= 1


class ResourceMonitor:
    """Monitors resource usage during execution."""
    
    def __init__(self, policy: SecurityPolicy):
        self.policy = policy
        self.start_time = None
        self.monitoring = False
        self.monitor_thread = None
    
    def start(self):
        """Start resource monitoring."""
        self.start_time = time.time()
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop(self):
        """Stop resource monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Monitor resource usage in background thread."""
        while self.monitoring:
            try:
                # Check execution time
                if self.start_time:
                    elapsed = time.time() - self.start_time
                    if elapsed > self.policy.max_cpu_seconds:
                        self.monitoring = False
                        raise ExecutionTimeout(f"Execution exceeded {self.policy.max_cpu_seconds} seconds")
                
                # Check memory usage (platform-specific)
                if sys.platform != 'win32':
                    import psutil
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    if memory_mb > self.policy.max_memory_mb:
                        self.monitoring = False
                        raise ResourceExhausted(f"Memory usage exceeded {self.policy.max_memory_mb} MB")
                
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                self.monitoring = False
                raise


class ExecutionSandbox:
    """Main sandbox for secure code execution."""
    
    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()
        self.namespace = SandboxedNamespace(self.policy)
        self.validator = CodeValidator(self.policy)
        self.monitor = ResourceMonitor(self.policy)
    
    @contextmanager
    def _resource_limits(self):
        """Context manager for resource limits."""
        # Save original limits
        original_recursion = sys.getrecursionlimit()
        
        try:
            # Set new limits
            sys.setrecursionlimit(min(original_recursion, self.policy.max_recursion_depth))
            
            # Platform-specific resource limits
            if sys.platform != 'win32':
                try:
                    import resource as res
                    
                    # Set memory limit
                    soft, hard = res.getrlimit(res.RLIMIT_AS)
                    res.setrlimit(res.RLIMIT_AS, 
                                (self.policy.max_memory_mb * 1024 * 1024, hard))
                    
                    # Set CPU time limit
                    res.setrlimit(res.RLIMIT_CPU,
                                (self.policy.max_cpu_seconds, self.policy.max_cpu_seconds + 5))
                    
                    # Set file size limit
                    res.setrlimit(res.RLIMIT_FSIZE,
                                (self.policy.max_file_size_mb * 1024 * 1024,
                                 self.policy.max_file_size_mb * 1024 * 1024))
                    
                    # Set max open files
                    res.setrlimit(res.RLIMIT_NOFILE,
                                (self.policy.max_open_files, self.policy.max_open_files))
                except ImportError:
                    # Resource module not available on this platform
                    pass
            
            yield
            
        finally:
            # Restore original limits
            sys.setrecursionlimit(original_recursion)
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None,
                timeout: Optional[int] = None) -> Any:
        """Execute code in sandboxed environment."""
        # Validate code
        self.validator.validate(code)
        
        # Update namespace with context
        if context:
            self.namespace.update(context)
        
        # Use provided timeout or policy default
        if timeout:
            self.policy.max_cpu_seconds = timeout
        
        # Execute with resource monitoring
        result = None
        exception = None
        
        def run_code():
            nonlocal result, exception
            try:
                with self._resource_limits():
                    self.monitor.start()
                    
                    # Compile and execute code
                    compiled = compile(code, '<sandboxed>', 'exec')
                    exec(compiled, self.namespace.namespace)
                    
                    # Get result if available
                    if '__result__' in self.namespace.namespace:
                        result = self.namespace.namespace['__result__']
                    
            except Exception as e:
                exception = e
            finally:
                self.monitor.stop()
        
        # Run in separate thread with timeout
        thread = threading.Thread(target=run_code)
        thread.start()
        thread.join(timeout=self.policy.max_cpu_seconds)
        
        if thread.is_alive():
            # Force stop if still running
            raise ExecutionTimeout(f"Execution exceeded timeout of {self.policy.max_cpu_seconds} seconds")
        
        if exception:
            raise exception
        
        return result
    
    def execute_function(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function in sandboxed environment."""
        # Wrap function execution in code string
        code = f"""
import inspect
__func__ = context['__func__']
__args__ = context['__args__']
__kwargs__ = context['__kwargs__']
__result__ = __func__(*__args__, **__kwargs__)
"""
        
        context = {
            '__func__': func,
            '__args__': args,
            '__kwargs__': kwargs
        }
        
        return self.execute(code, context)


class ProcessSandbox:
    """Process-based sandbox for complete isolation."""
    
    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None,
                timeout: Optional[int] = None) -> Any:
        """Execute code in separate process."""
        timeout = timeout or self.policy.max_cpu_seconds
        
        def run_in_process(queue, code, context):
            try:
                sandbox = ExecutionSandbox(self.policy)
                result = sandbox.execute(code, context)
                queue.put(('success', result))
            except Exception as e:
                queue.put(('error', str(e), traceback.format_exc()))
        
        # Create queue for communication
        queue = multiprocessing.Queue()
        
        # Create and start process
        process = multiprocessing.Process(
            target=run_in_process,
            args=(queue, code, context)
        )
        process.start()
        
        # Wait for completion with timeout
        process.join(timeout=timeout)
        
        if process.is_alive():
            # Terminate if still running
            process.terminate()
            process.join()
            raise ExecutionTimeout(f"Process execution exceeded {timeout} seconds")
        
        # Get result from queue
        if not queue.empty():
            result = queue.get()
            if result[0] == 'success':
                return result[1]
            else:
                raise RuntimeError(f"Process execution failed: {result[1]}\n{result[2]}")
        
        return None


# Decorator for sandboxed execution
def sandboxed(policy: Optional[SecurityPolicy] = None):
    """Decorator to run function in sandbox."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sandbox = ExecutionSandbox(policy)
            return sandbox.execute_function(func, *args, **kwargs)
        return wrapper
    return decorator


# Context manager for sandboxed execution
@contextmanager
def sandboxed_context(policy: Optional[SecurityPolicy] = None):
    """Context manager for sandboxed execution."""
    sandbox = ExecutionSandbox(policy)
    try:
        yield sandbox
    finally:
        sandbox.monitor.stop()


# Utility functions for common sandbox configurations
def create_strict_sandbox() -> ExecutionSandbox:
    """Create sandbox with strict security policy."""
    policy = SecurityPolicy(
        max_memory_mb=256,
        max_cpu_seconds=10,
        max_file_size_mb=1,
        max_open_files=10,
        allowed_modules={'math', 'numpy'},
        allow_network=False
    )
    return ExecutionSandbox(policy)


def create_scientific_sandbox() -> ExecutionSandbox:
    """Create sandbox for scientific computing."""
    policy = SecurityPolicy(
        max_memory_mb=2048,
        max_cpu_seconds=300,
        max_file_size_mb=100,
        allowed_modules={
            'math', 'numpy', 'scipy', 'sympy',
            'pandas', 'matplotlib', 'qiskit',
            'uncertainties', 'scikit-learn'
        },
        max_quantum_qubits=30,
        max_tensor_size=1000000000
    )
    return ExecutionSandbox(policy)


def create_quantum_sandbox() -> ExecutionSandbox:
    """Create sandbox for quantum computing."""
    policy = SecurityPolicy(
        max_memory_mb=4096,
        max_cpu_seconds=600,
        allowed_modules={
            'math', 'numpy', 'scipy', 'qiskit',
            'cirq', 'pennylane', 'pyquil'
        },
        max_quantum_qubits=30
    )
    return ExecutionSandbox(policy)