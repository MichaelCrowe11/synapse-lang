"""TensorEngine - High-performance tensor operations for Synapse language."""

import numpy as np
import numba
from numba import cuda, jit, njit, prange, vectorize
from typing import Union, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass
import functools
from enum import Enum
import warnings

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class Backend(Enum):
    """Supported tensor backends."""
    NUMPY = "numpy"
    NUMBA = "numba"
    TORCH = "torch"
    TENSORFLOW = "tensorflow"
    CUDA = "cuda"


@dataclass
class TensorConfig:
    """Tensor engine configuration."""
    backend: Backend = Backend.NUMPY
    device: str = "cpu"  # cpu, cuda, tpu
    precision: str = "float32"  # float16, float32, float64
    parallel: bool = True
    lazy_eval: bool = False
    cache_ops: bool = True
    max_memory_gb: float = 8.0
    
    
class Tensor:
    """Tensor wrapper for consistent interface."""
    
    def __init__(self, data: np.ndarray):
        self._data = data
        
    @property 
    def data(self) -> np.ndarray:
        """Get the tensor data."""
        return self._data
    
    @property
    def shape(self) -> Tuple[int, ...]:
        """Get tensor shape."""
        return self._data.shape
        
    @property
    def dtype(self) -> np.dtype:
        """Get tensor dtype.""" 
        return self._data.dtype
    
    def __str__(self) -> str:
        """String representation."""
        return str(self._data)
        
    def __repr__(self) -> str:
        """Representation."""
        return f"Tensor(shape={self.shape}, dtype={self.dtype})"


class LazyTensor:
    """Lazy evaluation tensor wrapper."""
    
    def __init__(self, shape: Tuple[int, ...], dtype: np.dtype, 
                 compute_fn: Optional[Callable] = None):
        self.shape = shape
        self.dtype = dtype
        self.compute_fn = compute_fn
        self._materialized = False
        self._data = None
        self._operations = []
        
    def materialize(self) -> np.ndarray:
        """Materialize the tensor by executing operations."""
        if self._materialized:
            return self._data
            
        if self.compute_fn:
            self._data = self.compute_fn()
        else:
            self._data = np.zeros(self.shape, dtype=self.dtype)
            
        # Apply queued operations
        for op, args, kwargs in self._operations:
            self._data = op(self._data, *args, **kwargs)
            
        self._materialized = True
        self._operations.clear()
        return self._data
        
    def add_operation(self, op: Callable, *args, **kwargs):
        """Queue an operation for lazy evaluation."""
        self._operations.append((op, args, kwargs))
        self._materialized = False
        
    @property
    def data(self) -> np.ndarray:
        """Get the materialized tensor data."""
        return self.materialize()
        
    def __str__(self) -> str:
        """String representation of the tensor."""
        data = self.materialize()
        return f"LazyTensor(shape={self.shape}, dtype={self.dtype}):\n{data}"
        
    def __repr__(self) -> str:
        """Representation of the tensor."""
        return f"LazyTensor(shape={self.shape}, dtype={self.dtype})"


class TensorEngine:
    """High-performance tensor operations engine."""
    
    def __init__(self, config: Optional[TensorConfig] = None):
        self.config = config or TensorConfig()
        self._cache = {}
        self._init_backend()
        
    def _init_backend(self):
        """Initialize the selected backend."""
        if self.config.backend == Backend.TORCH and not TORCH_AVAILABLE:
            warnings.warn("PyTorch not available, falling back to NumPy")
            self.config.backend = Backend.NUMPY
            
        if self.config.backend == Backend.TENSORFLOW and not TF_AVAILABLE:
            warnings.warn("TensorFlow not available, falling back to NumPy")
            self.config.backend = Backend.NUMPY
            
        if self.config.backend == Backend.CUDA and not cuda.is_available():
            warnings.warn("CUDA not available, falling back to Numba")
            self.config.backend = Backend.NUMBA
            
    def tensor(self, data: Union[list, np.ndarray], 
               shape: Optional[Tuple[int, ...]] = None,
               dtype: Optional[str] = None) -> Union[Tensor, LazyTensor]:
        """Create a tensor with the specified backend."""
        dtype = dtype or self.config.precision
        
        if self.config.lazy_eval:
            if shape is None:
                shape = np.array(data).shape
            return LazyTensor(shape, np.dtype(dtype), 
                            lambda: self._create_tensor(data, dtype))
        
        return self._create_tensor(data, dtype)
        
    def _create_tensor(self, data: Union[list, np.ndarray], dtype: str) -> Tensor:
        """Create tensor with backend-specific implementation."""
        if self.config.backend == Backend.TORCH:
            import torch
            device = self.config.device
            torch_tensor = torch.tensor(data, dtype=getattr(torch, dtype), device=device)
            return Tensor(torch_tensor.numpy())
            
        elif self.config.backend == Backend.TENSORFLOW:
            import tensorflow as tf
            tf_tensor = tf.constant(data, dtype=getattr(tf, dtype))
            return Tensor(tf_tensor.numpy())
            
        else:  # NumPy or Numba
            return Tensor(np.array(data, dtype=dtype))
            
    def zeros(self, shape: Tuple[int, ...], dtype: Optional[str] = None) -> Any:
        """Create zero tensor."""
        dtype = dtype or self.config.precision
        
        if self.config.lazy_eval:
            return LazyTensor(shape, np.dtype(dtype))
            
        if self.config.backend == Backend.TORCH:
            import torch
            return torch.zeros(shape, dtype=getattr(torch, dtype), 
                             device=self.config.device)
        elif self.config.backend == Backend.TENSORFLOW:
            import tensorflow as tf
            return tf.zeros(shape, dtype=getattr(tf, dtype))
        else:
            return np.zeros(shape, dtype=dtype)
            
    def ones(self, shape: Tuple[int, ...], dtype: Optional[str] = None) -> Any:
        """Create ones tensor."""
        dtype = dtype or self.config.precision
        
        if self.config.lazy_eval:
            return LazyTensor(shape, np.dtype(dtype), 
                            lambda: np.ones(shape, dtype=dtype))
            
        if self.config.backend == Backend.TORCH:
            import torch
            return torch.ones(shape, dtype=getattr(torch, dtype),
                            device=self.config.device)
        elif self.config.backend == Backend.TENSORFLOW:
            import tensorflow as tf
            return tf.ones(shape, dtype=getattr(tf, dtype))
        else:
            return np.ones(shape, dtype=dtype)
            
    def random(self, shape: Tuple[int, ...], dtype: Optional[str] = None) -> Any:
        """Create random tensor."""
        dtype = dtype or self.config.precision
        
        if self.config.lazy_eval:
            return LazyTensor(shape, np.dtype(dtype),
                            lambda: np.random.random(shape).astype(dtype))
            
        if self.config.backend == Backend.TORCH:
            import torch
            return torch.rand(shape, dtype=getattr(torch, dtype),
                            device=self.config.device)
        elif self.config.backend == Backend.TENSORFLOW:
            import tensorflow as tf
            return tf.random.uniform(shape, dtype=getattr(tf, dtype))
        else:
            return np.random.random(shape).astype(dtype)
            
    # Mathematical operations
    @njit(parallel=True, fastmath=True)
    def _numba_add(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Numba-accelerated addition."""
        result = np.empty_like(a)
        for i in prange(a.size):
            result.flat[i] = a.flat[i] + b.flat[i]
        return result
        
    def add(self, a: Any, b: Any) -> Any:
        """Element-wise addition."""
        if isinstance(a, LazyTensor) or isinstance(b, LazyTensor):
            result = LazyTensor(a.shape, a.dtype)
            result.add_operation(lambda x, y: x + y, b)
            return result
        
        # Extract data from Tensor objects
        a_data = a.data if isinstance(a, Tensor) else a
        b_data = b.data if isinstance(b, Tensor) else b
            
        if self.config.backend == Backend.NUMBA:
            result = self._numba_add(a_data, b_data)
        else:
            result = a_data + b_data
            
        return Tensor(result)
            
    @njit(parallel=True, fastmath=True)
    def _numba_multiply(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Numba-accelerated multiplication."""
        result = np.empty_like(a)
        for i in prange(a.size):
            result.flat[i] = a.flat[i] * b.flat[i]
        return result
        
    def multiply(self, a: Any, b: Any) -> Any:
        """Element-wise multiplication."""
        if isinstance(a, LazyTensor) or isinstance(b, LazyTensor):
            result = LazyTensor(a.shape, a.dtype)
            result.add_operation(lambda x, y: x * y, b)
            return result
            
        if self.config.backend == Backend.NUMBA:
            return self._numba_multiply(a, b)
        else:
            return a * b
            
    @njit(parallel=True, fastmath=True)
    def _numba_matmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Numba-accelerated matrix multiplication."""
        m, k = a.shape
        k2, n = b.shape
        assert k == k2, "Matrix dimensions must match"
        
        result = np.zeros((m, n), dtype=a.dtype)
        for i in prange(m):
            for j in range(n):
                for l in range(k):
                    result[i, j] += a[i, l] * b[l, j]
        return result
        
    def matmul(self, a: Any, b: Any) -> Any:
        """Matrix multiplication."""
        if isinstance(a, LazyTensor) or isinstance(b, LazyTensor):
            shape = (a.shape[0], b.shape[1])
            result = LazyTensor(shape, a.dtype)
            result.add_operation(lambda x, y: x @ y, b)
            return result
        
        # Extract data from Tensor objects
        a_data = a.data if isinstance(a, Tensor) else a
        b_data = b.data if isinstance(b, Tensor) else b
            
        if self.config.backend == Backend.NUMBA:
            result = self._numba_matmul(a_data, b_data)
        elif self.config.backend == Backend.TORCH:
            result = torch.matmul(a_data, b_data)
        elif self.config.backend == Backend.TENSORFLOW:
            result = tf.matmul(a_data, b_data)
        else:
            result = np.matmul(a_data, b_data)
            
        return Tensor(result)
            
    def transpose(self, tensor: Any, axes: Optional[Tuple[int, ...]] = None) -> Any:
        """Transpose tensor."""
        if isinstance(tensor, LazyTensor):
            if axes is None:
                axes = tuple(reversed(range(len(tensor.shape))))
            new_shape = tuple(tensor.shape[i] for i in axes)
            result = LazyTensor(new_shape, tensor.dtype)
            result.add_operation(lambda x: np.transpose(x, axes))
            return result
            
        if self.config.backend == Backend.TORCH:
            if axes:
                return tensor.permute(axes)
            return tensor.T
        elif self.config.backend == Backend.TENSORFLOW:
            return tf.transpose(tensor, axes)
        else:
            return np.transpose(tensor, axes)
            
    def reshape(self, tensor: Any, shape: Tuple[int, ...]) -> Any:
        """Reshape tensor."""
        if isinstance(tensor, LazyTensor):
            result = LazyTensor(shape, tensor.dtype)
            result.add_operation(lambda x: x.reshape(shape))
            return result
            
        if self.config.backend == Backend.TORCH:
            return tensor.reshape(shape)
        elif self.config.backend == Backend.TENSORFLOW:
            return tf.reshape(tensor, shape)
        else:
            return np.reshape(tensor, shape)
            
    # Reduction operations
    def sum(self, tensor: Any, axis: Optional[Union[int, Tuple[int, ...]]] = None) -> Any:
        """Sum reduction."""
        if isinstance(tensor, LazyTensor):
            tensor = tensor.materialize()
            
        if self.config.backend == Backend.TORCH:
            return torch.sum(tensor, dim=axis)
        elif self.config.backend == Backend.TENSORFLOW:
            return tf.reduce_sum(tensor, axis=axis)
        else:
            return np.sum(tensor, axis=axis)
            
    def mean(self, tensor: Any, axis: Optional[Union[int, Tuple[int, ...]]] = None) -> Any:
        """Mean reduction."""
        if isinstance(tensor, LazyTensor):
            tensor = tensor.materialize()
            
        if self.config.backend == Backend.TORCH:
            return torch.mean(tensor, dim=axis)
        elif self.config.backend == Backend.TENSORFLOW:
            return tf.reduce_mean(tensor, axis=axis)
        else:
            return np.mean(tensor, axis=axis)
            
    def max(self, tensor: Any, axis: Optional[Union[int, Tuple[int, ...]]] = None) -> Any:
        """Max reduction."""
        if isinstance(tensor, LazyTensor):
            tensor = tensor.materialize()
            
        if self.config.backend == Backend.TORCH:
            if axis is not None:
                return torch.max(tensor, dim=axis)[0]
            return torch.max(tensor)
        elif self.config.backend == Backend.TENSORFLOW:
            return tf.reduce_max(tensor, axis=axis)
        else:
            return np.max(tensor, axis=axis)
            
    def min(self, tensor: Any, axis: Optional[Union[int, Tuple[int, ...]]] = None) -> Any:
        """Min reduction."""
        if isinstance(tensor, LazyTensor):
            tensor = tensor.materialize()
            
        if self.config.backend == Backend.TORCH:
            if axis is not None:
                return torch.min(tensor, dim=axis)[0]
            return torch.min(tensor)
        elif self.config.backend == Backend.TENSORFLOW:
            return tf.reduce_min(tensor, axis=axis)
        else:
            return np.min(tensor, axis=axis)
            
    # Advanced operations
    def einsum(self, equation: str, *tensors) -> Any:
        """Einstein summation."""
        # Materialize lazy tensors
        tensors = [t.materialize() if isinstance(t, LazyTensor) else t 
                  for t in tensors]
                  
        if self.config.backend == Backend.TORCH:
            return torch.einsum(equation, *tensors)
        elif self.config.backend == Backend.TENSORFLOW:
            return tf.einsum(equation, *tensors)
        else:
            return np.einsum(equation, *tensors)
            
    def conv2d(self, input: Any, kernel: Any, stride: int = 1, 
               padding: str = "valid") -> Any:
        """2D convolution."""
        if isinstance(input, LazyTensor) or isinstance(kernel, LazyTensor):
            if isinstance(input, LazyTensor):
                input = input.materialize()
            if isinstance(kernel, LazyTensor):
                kernel = kernel.materialize()
                
        if self.config.backend == Backend.TORCH:
            import torch.nn.functional as F
            return F.conv2d(input, kernel, stride=stride, 
                          padding=padding if padding != "valid" else 0)
        elif self.config.backend == Backend.TENSORFLOW:
            return tf.nn.conv2d(input, kernel, strides=stride, padding=padding.upper())
        else:
            # NumPy implementation
            from scipy import signal
            return signal.convolve2d(input, kernel, mode=padding)
            
    def gradient(self, tensor: Any, axis: Optional[int] = None) -> Any:
        """Compute gradient."""
        if isinstance(tensor, LazyTensor):
            tensor = tensor.materialize()
            
        if self.config.backend == Backend.TORCH:
            if tensor.requires_grad:
                return tensor.grad
            else:
                return torch.gradient(tensor, dim=axis)
        elif self.config.backend == Backend.TENSORFLOW:
            return tf.gradients(tensor, axis)
        else:
            return np.gradient(tensor, axis=axis)
            
    # GPU operations
    @cuda.jit
    def _cuda_add_kernel(a, b, result):
        """CUDA kernel for addition."""
        i, j = cuda.grid(2)
        if i < result.shape[0] and j < result.shape[1]:
            result[i, j] = a[i, j] + b[i, j]
            
    def cuda_add(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """GPU-accelerated addition."""
        if not cuda.is_available():
            return self.add(a, b)
            
        # Transfer to GPU
        d_a = cuda.to_device(a)
        d_b = cuda.to_device(b)
        d_result = cuda.device_array_like(a)
        
        # Configure kernel
        threadsperblock = (16, 16)
        blockspergrid_x = (a.shape[0] + threadsperblock[0] - 1) // threadsperblock[0]
        blockspergrid_y = (a.shape[1] + threadsperblock[1] - 1) // threadsperblock[1]
        blockspergrid = (blockspergrid_x, blockspergrid_y)
        
        # Launch kernel
        self._cuda_add_kernel[blockspergrid, threadsperblock](d_a, d_b, d_result)
        
        # Transfer back
        return d_result.copy_to_host()
        
    # Utility methods
    def to_numpy(self, tensor: Any) -> np.ndarray:
        """Convert tensor to NumPy array."""
        if isinstance(tensor, LazyTensor):
            return tensor.materialize()
        elif self.config.backend == Backend.TORCH:
            return tensor.detach().cpu().numpy()
        elif self.config.backend == Backend.TENSORFLOW:
            return tensor.numpy()
        else:
            return np.array(tensor)
            
    def shape(self, tensor: Any) -> Tuple[int, ...]:
        """Get tensor shape."""
        if isinstance(tensor, LazyTensor):
            return tensor.shape
        elif hasattr(tensor, 'shape'):
            return tuple(tensor.shape)
        else:
            return np.array(tensor).shape
            
    def dtype(self, tensor: Any) -> str:
        """Get tensor dtype."""
        if isinstance(tensor, LazyTensor):
            return str(tensor.dtype)
        elif hasattr(tensor, 'dtype'):
            return str(tensor.dtype)
        else:
            return str(np.array(tensor).dtype)
            
    def memory_usage(self, tensor: Any) -> int:
        """Get tensor memory usage in bytes."""
        if isinstance(tensor, LazyTensor):
            if tensor._materialized:
                tensor = tensor._data
            else:
                # Estimate based on shape and dtype
                return np.prod(tensor.shape) * np.dtype(tensor.dtype).itemsize
                
        if self.config.backend == Backend.TORCH:
            return tensor.element_size() * tensor.nelement()
        elif self.config.backend == Backend.TENSORFLOW:
            return tf.size(tensor).numpy() * tensor.dtype.size
        else:
            return tensor.nbytes
            
    def optimize_memory(self):
        """Optimize memory usage."""
        if self.config.backend == Backend.TORCH:
            import torch
            torch.cuda.empty_cache()
        elif self.config.backend == Backend.TENSORFLOW:
            import tensorflow as tf
            tf.keras.backend.clear_session()
        # Clear cache
        self._cache.clear()
        
        
# High-level API functions
def create_tensor_engine(backend: str = "numpy", **kwargs) -> TensorEngine:
    """Create tensor engine with specified backend."""
    backend_map = {
        "numpy": Backend.NUMPY,
        "numba": Backend.NUMBA,
        "torch": Backend.TORCH,
        "pytorch": Backend.TORCH,
        "tensorflow": Backend.TENSORFLOW,
        "tf": Backend.TENSORFLOW,
        "cuda": Backend.CUDA
    }
    
    config = TensorConfig(backend=backend_map.get(backend.lower(), Backend.NUMPY))
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
            
    return TensorEngine(config)
    

# Decorator for tensor operations
def tensor_op(backend: str = "numpy", parallel: bool = True):
    """Decorator for tensor operations."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            engine = create_tensor_engine(backend, parallel=parallel)
            # Inject engine into function namespace
            func.__globals__['engine'] = engine
            return func(*args, **kwargs)
        return wrapper
    return decorator