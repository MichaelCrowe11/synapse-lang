"""
Synapse Language - GPU-Accelerated Tensor Operations
High-performance tensor operations with GPU support via CuPy/PyTorch
"""

import warnings
from dataclasses import dataclass
from typing import Any, Union

import numpy as np

# Try to import GPU libraries
GPU_AVAILABLE = False
GPU_BACKEND = None

try:
    import cupy as cp
    GPU_AVAILABLE = True
    GPU_BACKEND = "cupy"
    print("GPU acceleration available via CuPy")
except ImportError:
    try:
        import torch
        if torch.cuda.is_available():
            GPU_AVAILABLE = True
            GPU_BACKEND = "pytorch"
            print("GPU acceleration available via PyTorch")
    except ImportError:
        pass

if not GPU_AVAILABLE:
    warnings.warn("No GPU backend available. Install CuPy or PyTorch with CUDA support for GPU acceleration.", stacklevel=2)

@dataclass
class GPUConfig:
    """Configuration for GPU operations"""
    enabled: bool = GPU_AVAILABLE
    backend: str | None = GPU_BACKEND
    device_id: int = 0
    memory_fraction: float = 0.8
    benchmark_mode: bool = True
    allow_tf32: bool = True  # For PyTorch

    def __post_init__(self):
        if self.enabled and GPU_BACKEND == "pytorch":
            import torch
            torch.backends.cudnn.benchmark = self.benchmark_mode
            torch.backends.cuda.matmul.allow_tf32 = self.allow_tf32

class GPUTensor:
    """GPU-accelerated tensor wrapper"""

    def __init__(self, data: Union[np.ndarray, "cp.ndarray", "torch.Tensor"],
                 uncertainty: float | None = None,
                 use_gpu: bool = True):
        self.use_gpu = use_gpu and GPU_AVAILABLE
        self.uncertainty = uncertainty

        if self.use_gpu:
            self.data = self._to_gpu(data)
        else:
            self.data = self._to_cpu(data)

    def _to_gpu(self, data: Any) -> Any:
        """Move data to GPU"""
        if GPU_BACKEND == "cupy":
            import cupy as cp
            if isinstance(data, np.ndarray):
                return cp.asarray(data)
            elif isinstance(data, cp.ndarray):
                return data
            else:
                return cp.asarray(np.array(data))
        elif GPU_BACKEND == "pytorch":
            import torch
            if isinstance(data, np.ndarray):
                return torch.from_numpy(data).cuda()
            elif isinstance(data, torch.Tensor):
                return data.cuda() if not data.is_cuda else data
            else:
                return torch.tensor(data).cuda()
        return np.array(data)

    def _to_cpu(self, data: Any) -> np.ndarray:
        """Move data to CPU"""
        if GPU_BACKEND == "cupy":
            import cupy as cp
            if isinstance(data, cp.ndarray):
                return cp.asnumpy(data)
        elif GPU_BACKEND == "pytorch":
            import torch
            if isinstance(data, torch.Tensor):
                return data.cpu().numpy()

        if isinstance(data, np.ndarray):
            return data
        return np.array(data)

    def to_numpy(self) -> np.ndarray:
        """Convert to numpy array"""
        return self._to_cpu(self.data)

    @property
    def shape(self) -> tuple:
        return tuple(self.data.shape)

    @property
    def ndim(self) -> int:
        return self.data.ndim

    @property
    def size(self) -> int:
        return int(np.prod(self.shape))

    def __repr__(self) -> str:
        device = "GPU" if self.use_gpu else "CPU"
        unc_str = f" ± {self.uncertainty}" if self.uncertainty else ""
        return f"GPUTensor({self.shape}, device={device}{unc_str})"

class GPUTensorOps:
    """GPU-accelerated tensor operations"""

    def __init__(self, config: GPUConfig | None = None):
        self.config = config or GPUConfig()
        self._op_cache = {}

    def _get_backend_module(self):
        """Get the appropriate backend module"""
        if self.config.backend == "cupy":
            import cupy as cp
            return cp
        elif self.config.backend == "pytorch":
            import torch
            return torch
        return np

    # Creation operations
    def zeros(self, shape: int | tuple, dtype=None) -> GPUTensor:
        """Create zero tensor on GPU"""
        if isinstance(shape, int):
            shape = (shape,)

        if self.config.enabled:
            backend = self._get_backend_module()
            if self.config.backend == "pytorch":
                data = backend.zeros(shape, dtype=dtype or backend.float32, device="cuda")
            else:
                data = backend.zeros(shape, dtype=dtype or backend.float32)
        else:
            data = np.zeros(shape, dtype=dtype or np.float32)

        return GPUTensor(data, use_gpu=self.config.enabled)

    def ones(self, shape: int | tuple, dtype=None) -> GPUTensor:
        """Create ones tensor on GPU"""
        if isinstance(shape, int):
            shape = (shape,)

        if self.config.enabled:
            backend = self._get_backend_module()
            if self.config.backend == "pytorch":
                data = backend.ones(shape, dtype=dtype or backend.float32, device="cuda")
            else:
                data = backend.ones(shape, dtype=dtype or backend.float32)
        else:
            data = np.ones(shape, dtype=dtype or np.float32)

        return GPUTensor(data, use_gpu=self.config.enabled)

    def eye(self, n: int, m: int | None = None, dtype=None) -> GPUTensor:
        """Create identity matrix on GPU"""
        m = m or n

        if self.config.enabled:
            backend = self._get_backend_module()
            if self.config.backend == "pytorch":
                data = backend.eye(n, m, dtype=dtype or backend.float32, device="cuda")
            else:
                data = backend.eye(n, m, dtype=dtype or backend.float32)
        else:
            data = np.eye(n, m, dtype=dtype or np.float32)

        return GPUTensor(data, use_gpu=self.config.enabled)

    def random(self, shape: int | tuple, dtype=None) -> GPUTensor:
        """Create random tensor on GPU"""
        if isinstance(shape, int):
            shape = (shape,)

        if self.config.enabled:
            backend = self._get_backend_module()
            if self.config.backend == "pytorch":
                data = backend.rand(shape, dtype=dtype or backend.float32, device="cuda")
            else:
                data = backend.random.random(shape).astype(dtype or backend.float32)
        else:
            data = np.random.random(shape).astype(dtype or np.float32)

        return GPUTensor(data, use_gpu=self.config.enabled)

    # Arithmetic operations
    def add(self, a: GPUTensor, b: GPUTensor | float) -> GPUTensor:
        """Add tensors on GPU"""
        if isinstance(b, GPUTensor):
            result_data = a.data + b.data
            # Propagate uncertainty
            if a.uncertainty or b.uncertainty:
                unc_a = a.uncertainty or 0
                unc_b = b.uncertainty or 0
                result_unc = np.sqrt(unc_a**2 + unc_b**2)
            else:
                result_unc = None
        else:
            result_data = a.data + b
            result_unc = a.uncertainty

        return GPUTensor(result_data, uncertainty=result_unc, use_gpu=a.use_gpu)

    def multiply(self, a: GPUTensor, b: GPUTensor | float) -> GPUTensor:
        """Multiply tensors on GPU"""
        if isinstance(b, GPUTensor):
            result_data = a.data * b.data
            # Propagate uncertainty
            if a.uncertainty or b.uncertainty:
                a_val = a.to_numpy()
                b_val = b.to_numpy()
                unc_a = a.uncertainty or 0
                unc_b = b.uncertainty or 0
                rel_unc = np.sqrt((unc_a/np.mean(a_val))**2 + (unc_b/np.mean(b_val))**2)
                result_unc = np.mean(np.abs(a_val * b_val)) * rel_unc
            else:
                result_unc = None
        else:
            result_data = a.data * b
            result_unc = a.uncertainty * abs(b) if a.uncertainty else None

        return GPUTensor(result_data, uncertainty=result_unc, use_gpu=a.use_gpu)

    def matmul(self, a: GPUTensor, b: GPUTensor) -> GPUTensor:
        """Matrix multiplication on GPU"""
        if self.config.backend == "pytorch":
            result_data = a.data @ b.data
        else:
            result_data = a.data @ b.data

        # Propagate uncertainty (simplified)
        result_unc = None
        if a.uncertainty or b.uncertainty:
            unc_a = a.uncertainty or 0
            unc_b = b.uncertainty or 0
            result_unc = np.sqrt(unc_a**2 + unc_b**2)

        return GPUTensor(result_data, uncertainty=result_unc, use_gpu=a.use_gpu)

    # Reduction operations
    def sum(self, tensor: GPUTensor, axis: int | None = None) -> GPUTensor | float:
        """Sum reduction on GPU"""
        backend = self._get_backend_module()

        if axis is None:
            result = backend.sum(tensor.data)
            if self.config.backend == "pytorch":
                result = result.item()
            else:
                result = float(result)
            return result
        else:
            result_data = backend.sum(tensor.data, axis=axis)
            return GPUTensor(result_data, use_gpu=tensor.use_gpu)

    def mean(self, tensor: GPUTensor, axis: int | None = None) -> GPUTensor | float:
        """Mean reduction on GPU"""
        backend = self._get_backend_module()

        if axis is None:
            result = backend.mean(tensor.data)
            if self.config.backend == "pytorch":
                result = result.item()
            else:
                result = float(result)
            return result
        else:
            result_data = backend.mean(tensor.data, axis=axis)
            return GPUTensor(result_data, uncertainty=tensor.uncertainty, use_gpu=tensor.use_gpu)

    def std(self, tensor: GPUTensor, axis: int | None = None) -> GPUTensor | float:
        """Standard deviation on GPU"""
        backend = self._get_backend_module()

        if axis is None:
            result = backend.std(tensor.data)
            if self.config.backend == "pytorch":
                result = result.item()
            else:
                result = float(result)
            return result
        else:
            result_data = backend.std(tensor.data, axis=axis)
            return GPUTensor(result_data, use_gpu=tensor.use_gpu)

    # Advanced operations
    def fft(self, tensor: GPUTensor) -> GPUTensor:
        """Fast Fourier Transform on GPU"""
        if self.config.backend == "cupy":
            import cupy as cp
            result_data = cp.fft.fft(tensor.data)
        elif self.config.backend == "pytorch":
            import torch
            result_data = torch.fft.fft(tensor.data)
        else:
            result_data = np.fft.fft(tensor.to_numpy())

        return GPUTensor(result_data, use_gpu=tensor.use_gpu)

    def conv2d(self, tensor: GPUTensor, kernel: GPUTensor,
               stride: int = 1, padding: int = 0) -> GPUTensor:
        """2D convolution on GPU"""
        if self.config.backend == "pytorch":
            import torch.nn.functional as F

            # Ensure 4D tensors (batch, channel, height, width)
            if tensor.data.ndim == 2:
                tensor_4d = tensor.data.unsqueeze(0).unsqueeze(0)
            elif tensor.data.ndim == 3:
                tensor_4d = tensor.data.unsqueeze(0)
            else:
                tensor_4d = tensor.data

            if kernel.data.ndim == 2:
                kernel_4d = kernel.data.unsqueeze(0).unsqueeze(0)
            elif kernel.data.ndim == 3:
                kernel_4d = kernel.data.unsqueeze(0)
            else:
                kernel_4d = kernel.data

            result = F.conv2d(tensor_4d, kernel_4d, stride=stride, padding=padding)
            return GPUTensor(result.squeeze(), use_gpu=True)
        elif self.config.backend == "cupy":
            import cupyx.scipy.signal
            result = cupyx.scipy.signal.convolve2d(
                tensor.data, kernel.data, mode="same" if padding else "valid"
            )
            return GPUTensor(result, use_gpu=True)
        else:
            from scipy import signal
            result = signal.convolve2d(
                tensor.to_numpy(), kernel.to_numpy(),
                mode="same" if padding else "valid"
            )
            return GPUTensor(result, use_gpu=False)

    def eigenvalues(self, tensor: GPUTensor) -> tuple[GPUTensor, GPUTensor]:
        """Compute eigenvalues and eigenvectors on GPU"""
        if self.config.backend == "cupy":
            import cupy as cp
            eigenvalues, eigenvectors = cp.linalg.eig(tensor.data)
        elif self.config.backend == "pytorch":
            import torch
            eigenvalues, eigenvectors = torch.linalg.eig(tensor.data)
        else:
            eigenvalues, eigenvectors = np.linalg.eig(tensor.to_numpy())

        return (GPUTensor(eigenvalues, use_gpu=tensor.use_gpu),
                GPUTensor(eigenvectors, use_gpu=tensor.use_gpu))

    def svd(self, tensor: GPUTensor) -> tuple[GPUTensor, GPUTensor, GPUTensor]:
        """Singular Value Decomposition on GPU"""
        if self.config.backend == "cupy":
            import cupy as cp
            u, s, vh = cp.linalg.svd(tensor.data)
        elif self.config.backend == "pytorch":
            import torch
            u, s, vh = torch.linalg.svd(tensor.data)
        else:
            u, s, vh = np.linalg.svd(tensor.to_numpy())

        return (GPUTensor(u, use_gpu=tensor.use_gpu),
                GPUTensor(s, use_gpu=tensor.use_gpu),
                GPUTensor(vh, use_gpu=tensor.use_gpu))

    # Memory management
    def clear_cache(self):
        """Clear GPU memory cache"""
        if self.config.backend == "cupy":
            import cupy as cp
            cp.get_default_memory_pool().free_all_blocks()
        elif self.config.backend == "pytorch":
            import torch
            torch.cuda.empty_cache()

    def memory_info(self) -> dict:
        """Get GPU memory information"""
        info = {"gpu_available": self.config.enabled}

        if self.config.enabled:
            if self.config.backend == "cupy":
                import cupy as cp
                mempool = cp.get_default_memory_pool()
                info["used_bytes"] = mempool.used_bytes()
                info["total_bytes"] = mempool.total_bytes()
            elif self.config.backend == "pytorch":
                import torch
                info["allocated"] = torch.cuda.memory_allocated()
                info["reserved"] = torch.cuda.memory_reserved()
                info["max_allocated"] = torch.cuda.max_memory_allocated()

        return info

# Global GPU operations instance
_gpu_ops = None

def get_gpu_ops(config: GPUConfig | None = None) -> GPUTensorOps:
    """Get global GPU operations instance"""
    global _gpu_ops
    if _gpu_ops is None:
        _gpu_ops = GPUTensorOps(config)
    return _gpu_ops

def benchmark_gpu_vs_cpu():
    """Benchmark GPU vs CPU performance"""
    import time

    sizes = [100, 500, 1000, 2000]

    print("GPU vs CPU Benchmark")
    print("=" * 50)

    for size in sizes:
        print(f"\nMatrix size: {size}x{size}")

        # CPU benchmark
        a_cpu = np.random.random((size, size)).astype(np.float32)
        b_cpu = np.random.random((size, size)).astype(np.float32)

        start = time.perf_counter()
        for _ in range(10):
            a_cpu @ b_cpu
        cpu_time = time.perf_counter() - start

        print(f"  CPU time: {cpu_time:.3f}s")

        # GPU benchmark (if available)
        if GPU_AVAILABLE:
            gpu_ops = get_gpu_ops()
            a_gpu = GPUTensor(a_cpu)
            b_gpu = GPUTensor(b_cpu)

            # Warmup
            _ = gpu_ops.matmul(a_gpu, b_gpu)

            start = time.perf_counter()
            for _ in range(10):
                gpu_ops.matmul(a_gpu, b_gpu)
            gpu_time = time.perf_counter() - start

            print(f"  GPU time: {gpu_time:.3f}s")
            print(f"  Speedup:  {cpu_time/gpu_time:.2f}x")
        else:
            print("  GPU not available")

if __name__ == "__main__":
    print(f"GPU Available: {GPU_AVAILABLE}")
    if GPU_AVAILABLE:
        print(f"GPU Backend: {GPU_BACKEND}")

        # Run benchmark
        benchmark_gpu_vs_cpu()

        # Test operations
        gpu_ops = get_gpu_ops()

        # Create tensors
        a = gpu_ops.random((1000, 1000))
        b = gpu_ops.random((1000, 1000))

        # Operations
        c = gpu_ops.add(a, b)
        d = gpu_ops.matmul(a, b)

        print(f"\nMemory info: {gpu_ops.memory_info()}")
        gpu_ops.clear_cache()
        print(f"After clear: {gpu_ops.memory_info()}")
