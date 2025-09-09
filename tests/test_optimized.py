import pytest

from synapse_cache import TTLRUCache
from synapse_tensor_gpu_v2 import SynapseTensor, available_backend


def test_ttlru_cache_basic():
    c = TTLRUCache(maxsize=2)
    c.set("a", 1)
    c.set("b", 2)
    hit, v = c.get("a")
    assert hit and v == 1
    c.set("c", 3)  # evict LRU ("b")
    hit_b, _ = c.get("b")
    assert not hit_b


def test_tensor_backend_available():
    assert available_backend() in {"numpy", "torch", "cupy"}
    t = SynapseTensor.from_array([[1, 2], [3, 4]])
    out = t.matmul(t)
    assert hasattr(out, "data")