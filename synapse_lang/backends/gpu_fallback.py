"""
GPU matmul fallback: use CuPy if available, else NumPy.
Provides transparent API: to_gpu(array) and matmul(A,B)
"""
from typing import Any, Union, Optional, Tuple
import numpy as np


def _has_cupy():
    try:
        import cupy as cp  # type: ignore
        # Also check if CUDA is actually available
        try:
            _ = cp.cuda.Device()
            return True
        except:
            return False
    except Exception:
        return False


HAS_CUPY = _has_cupy()

if HAS_CUPY:
    import cupy as cp  # type: ignore


class GPUArray:
    """Wrapper for transparent GPU/CPU array operations"""

    def __init__(self, data, force_cpu: bool = False):
        self.force_cpu = force_cpu or not HAS_CUPY

        if self.force_cpu:
            self.data = np.asarray(data)
            self.is_gpu = False
        else:
            self.data = cp.asarray(data)
            self.is_gpu = True

    def to_cpu(self):
        """Convert to CPU array"""
        if self.is_gpu:
            return cp.asnumpy(self.data)
        return self.data

    def to_gpu(self):
        """Convert to GPU array if available"""
        if not self.is_gpu and HAS_CUPY:
            return cp.asarray(self.data)
        return self.data

    @property
    def shape(self):
        return self.data.shape

    @property
    def dtype(self):
        return self.data.dtype

    def __repr__(self):
        return f"GPUArray(shape={self.shape}, gpu={self.is_gpu})"


def to_gpu(x: Any, force: bool = False):
    """Move array to GPU if available.

    Args:
        x: Input array (numpy, list, or cupy)
        force: Force GPU transfer even if already on GPU

    Returns:
        GPU array if available, otherwise input
    """
    if HAS_CUPY:
        if hasattr(x, '__cuda_array_interface__') and not force:
            return x  # Already on GPU
        return cp.asarray(x)
    else:
        return np.asarray(x)


def to_cpu(x: Any):
    """Move array to CPU.

    Args:
        x: Input array (numpy, list, or cupy)

    Returns:
        NumPy array on CPU
    """
    if HAS_CUPY and hasattr(x, '__cuda_array_interface__'):
        return cp.asnumpy(x)
    else:
        return np.asarray(x)


def is_gpu_array(x: Any) -> bool:
    """Check if array is on GPU"""
    return HAS_CUPY and hasattr(x, '__cuda_array_interface__')


def matmul(A, B, use_gpu: Optional[bool] = None):
    """Matrix multiply using GPU if available, else CPU.

    Args:
        A: First matrix
        B: Second matrix
        use_gpu: Force GPU usage (True), CPU usage (False), or auto (None)

    Returns:
        numpy array on CPU
    """
    if use_gpu is None:
        use_gpu = HAS_CUPY

    if use_gpu and HAS_CUPY:
        A_gpu = cp.asarray(A)
        B_gpu = cp.asarray(B)
        C_gpu = cp.matmul(A_gpu, B_gpu)
        return cp.asnumpy(C_gpu)
    else:
        A_cpu = np.asarray(A)
        B_cpu = np.asarray(B)
        return np.matmul(A_cpu, B_cpu)


def elementwise_op(op_name: str, *arrays, use_gpu: Optional[bool] = None):
    """Perform elementwise operations on GPU if available.

    Args:
        op_name: Operation name ('add', 'multiply', 'exp', 'sin', etc.)
        arrays: Input arrays
        use_gpu: Force GPU/CPU or auto

    Returns:
        Result array on CPU
    """
    if use_gpu is None:
        use_gpu = HAS_CUPY

    if use_gpu and HAS_CUPY:
        module = cp
        gpu_arrays = [cp.asarray(a) for a in arrays]
    else:
        module = np
        gpu_arrays = [np.asarray(a) for a in arrays]

    # Map operation names to functions
    ops = {
        'add': module.add,
        'subtract': module.subtract,
        'multiply': module.multiply,
        'divide': module.divide,
        'power': module.power,
        'exp': module.exp,
        'log': module.log,
        'sin': module.sin,
        'cos': module.cos,
        'sqrt': module.sqrt,
    }

    if op_name not in ops:
        raise ValueError(f"Unknown operation: {op_name}")

    result = ops[op_name](*gpu_arrays)

    if use_gpu and HAS_CUPY:
        return cp.asnumpy(result)
    return result


def solve_linear(A, b, use_gpu: Optional[bool] = None):
    """Solve linear system Ax = b using GPU if available.

    Args:
        A: Coefficient matrix
        b: Right-hand side
        use_gpu: Force GPU/CPU or auto

    Returns:
        Solution vector x on CPU
    """
    if use_gpu is None:
        use_gpu = HAS_CUPY

    if use_gpu and HAS_CUPY:
        A_gpu = cp.asarray(A)
        b_gpu = cp.asarray(b)
        x_gpu = cp.linalg.solve(A_gpu, b_gpu)
        return cp.asnumpy(x_gpu)
    else:
        A_cpu = np.asarray(A)
        b_cpu = np.asarray(b)
        return np.linalg.solve(A_cpu, b_cpu)


def eigh(A, use_gpu: Optional[bool] = None):
    """Compute eigenvalues and eigenvectors of Hermitian matrix.

    Args:
        A: Hermitian matrix
        use_gpu: Force GPU/CPU or auto

    Returns:
        (eigenvalues, eigenvectors) both on CPU
    """
    if use_gpu is None:
        use_gpu = HAS_CUPY

    if use_gpu and HAS_CUPY:
        A_gpu = cp.asarray(A)
        w_gpu, v_gpu = cp.linalg.eigh(A_gpu)
        return cp.asnumpy(w_gpu), cp.asnumpy(v_gpu)
    else:
        A_cpu = np.asarray(A)
        return np.linalg.eigh(A_cpu)


def svd(A, use_gpu: Optional[bool] = None):
    """Compute Singular Value Decomposition.

    Args:
        A: Input matrix
        use_gpu: Force GPU/CPU or auto

    Returns:
        (U, S, Vt) all on CPU
    """
    if use_gpu is None:
        use_gpu = HAS_CUPY

    if use_gpu and HAS_CUPY:
        A_gpu = cp.asarray(A)
        u_gpu, s_gpu, vt_gpu = cp.linalg.svd(A_gpu)
        return cp.asnumpy(u_gpu), cp.asnumpy(s_gpu), cp.asnumpy(vt_gpu)
    else:
        A_cpu = np.asarray(A)
        return np.linalg.svd(A_cpu)


def get_gpu_memory_info() -> dict:
    """Get GPU memory usage information"""
    if not HAS_CUPY:
        return {"available": False}

    try:
        mempool = cp.get_default_memory_pool()
        pinned_mempool = cp.get_default_pinned_memory_pool()

        return {
            "available": True,
            "used_bytes": mempool.used_bytes(),
            "total_bytes": mempool.total_bytes(),
            "pinned_used_bytes": pinned_mempool.used_bytes(),
            "pinned_total_bytes": pinned_mempool.total_bytes(),
        }
    except:
        return {"available": False}


def clear_gpu_memory():
    """Clear GPU memory cache"""
    if HAS_CUPY:
        try:
            mempool = cp.get_default_memory_pool()
            pinned_mempool = cp.get_default_pinned_memory_pool()
            mempool.free_all_blocks()
            pinned_mempool.free_all_blocks()
        except:
            pass