"""
Backend adapter for Synapse - lightweight POC
Provides: auto() detection, solve(), matmul(), vqe_minimize() stubs
"""
from .cg_solver import cg_solve
from .gpu_fallback import matmul as gpu_matmul
from .quant_orchestrator import vqe_energy, vqe_minimize

__all__ = [
    'cg_solve',
    'gpu_matmul',
    'vqe_energy',
    'vqe_minimize',
    'auto',
    'get_backend_info',
    'set_default_backend',
]

# Global default backend
_default_backend = None


def auto():
    """Probe environment and return a suggested backend string"""
    backends = {"cpu.numpy": True}
    try:
        import scipy  # type: ignore
        backends['cpu.scipy'] = True
    except Exception:
        backends['cpu.scipy'] = False
    try:
        import cupy as cp  # type: ignore
        backends['gpu.cupy'] = True
    except Exception:
        backends['gpu.cupy'] = False
    try:
        import quant_hpc_lite  # type: ignore
        backends['quant.hpc'] = True
    except Exception:
        backends['quant.hpc'] = False

    # Priority: GPU > SciPy > NumPy > quant (explicit)
    if backends['gpu.cupy']:
        return 'gpu.cupy'
    if backends['cpu.scipy']:
        return 'cpu.scipy'
    if backends['quant.hpc']:
        return 'quant.hpc'
    return 'cpu.numpy'


def get_backend_info():
    """Get detailed information about available backends"""
    info = {
        'default': _default_backend or auto(),
        'available': {},
        'versions': {}
    }

    # Check NumPy
    try:
        import numpy as np
        info['available']['cpu.numpy'] = True
        info['versions']['numpy'] = np.__version__
    except:
        info['available']['cpu.numpy'] = False

    # Check SciPy
    try:
        import scipy
        info['available']['cpu.scipy'] = True
        info['versions']['scipy'] = scipy.__version__
    except:
        info['available']['cpu.scipy'] = False

    # Check CuPy
    try:
        import cupy as cp
        info['available']['gpu.cupy'] = True
        info['versions']['cupy'] = cp.__version__
        # Check CUDA availability
        try:
            _ = cp.cuda.Device()
            info['cuda_available'] = True
        except:
            info['cuda_available'] = False
    except:
        info['available']['gpu.cupy'] = False

    # Check quantum backend
    try:
        import quant_hpc_lite
        info['available']['quant.hpc'] = True
        if hasattr(quant_hpc_lite, '__version__'):
            info['versions']['quant_hpc_lite'] = quant_hpc_lite.__version__
    except:
        info['available']['quant.hpc'] = False

    return info


def set_default_backend(backend: str):
    """Set the default backend for operations"""
    global _default_backend
    _default_backend = backend
    return backend