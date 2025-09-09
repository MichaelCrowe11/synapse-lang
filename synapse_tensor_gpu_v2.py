"""
Synapse Language - GPU-Accelerated Tensor Operations
Selects best available backend: CuPy > PyTorch > NumPy.
Unified API via SynapseTensor.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple, Union

# Backend detection
_backend = "numpy"
try:  # Prefer CuPy when present
    import cupy as xp  # type: ignore
    _backend = "cupy"
except Exception:
    try:
        import torch  # type: ignore
        import numpy as np
        xp = np  # type: ignore
        _backend = "torch"
    except Exception:
        import numpy as xp  # type: ignore
        import numpy as np
        _backend = "numpy"


ArrayLike = Union["SynapseTensor", "xp.ndarray", "np.ndarray", "torch.Tensor"]


@dataclass
class SynapseTensor:
    data: Any
    backend: str = _backend

    @staticmethod
    def from_array(x: Any) -> "SynapseTensor":
        if isinstance(x, SynapseTensor):
            return x
        return SynapseTensor(data=x)

    def to(self, device: str = "cpu") -> "SynapseTensor":
        if self.backend == "torch":
            import torch  # type: ignore
            t = self.data
            if not isinstance(t, torch.Tensor):
                t = torch.from_numpy(xp.asarray(self.data))
            if device == "cuda" and torch.cuda.is_available():
                t = t.to("cuda")
            else:
                t = t.to("cpu")
            return SynapseTensor(t, backend="torch")
        # CuPy implicitly uses GPU; NumPy stays on CPU
        return self

    # Basic ops
    def matmul(self, other: ArrayLike) -> "SynapseTensor":
        other = SynapseTensor.from_array(other)
        if self.backend == "torch":
            import torch  # type: ignore
            a = self.data if isinstance(self.data, torch.Tensor) else torch.as_tensor(self.data)
            b = other.data if isinstance(other.data, torch.Tensor) else torch.as_tensor(other.data)
            return SynapseTensor(a @ b, backend="torch")
        return SynapseTensor(xp.matmul(self.data, other.data), backend=self.backend)

    def dot(self, other: ArrayLike) -> "SynapseTensor":
        other = SynapseTensor.from_array(other)
        if self.backend == "torch":
            import torch  # type: ignore
            a = self.data if isinstance(self.data, torch.Tensor) else torch.as_tensor(self.data)
            b = other.data if isinstance(other.data, torch.Tensor) else torch.as_tensor(other.data)
            return SynapseTensor(torch.dot(a.flatten(), b.flatten()), backend="torch")
        return SynapseTensor(xp.dot(self.data, other.data), backend=self.backend)

    def einsum(self, subscripts: str, *operands: ArrayLike) -> "SynapseTensor":
        ops = [SynapseTensor.from_array(o).data for o in operands]
        if self.backend == "torch":
            import torch  # type: ignore
            return SynapseTensor(torch.einsum(subscripts, self.data, *ops), backend="torch")
        return SynapseTensor(xp.einsum(subscripts, self.data, *ops), backend=self.backend)

    def asnumpy(self):
        if self.backend == "cupy":
            return xp.asnumpy(self.data)
        if self.backend == "torch":
            import torch  # type: ignore
            if isinstance(self.data, torch.Tensor):
                return self.data.detach().cpu().numpy()
        return xp.asarray(self.data)


def available_backend() -> str:
    return _backend