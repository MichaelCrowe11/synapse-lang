"""
Synapse Language - Performance Optimization Cache
High-performance caching system for interpreter optimization (TTL + LRU).
"""
from __future__ import annotations

import hashlib
import pickle
import threading
import time
import weakref
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    sets: int = 0


class TTLRUCache:
    """Thread-safe TTL + LRU cache with size limit and metrics."""

    def __init__(self, maxsize: int = 2048, default_ttl: float = 0.0):
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self._data: OrderedDict[str, Tuple[float, Any]] = OrderedDict()
        self._lock = threading.RLock()
        self.stats = CacheStats()

    def _purge_expired(self):
        now = time.time()
        expired_keys = [k for k, (exp, _) in self._data.items() if exp and exp < now]
        for k in expired_keys:
            self._data.pop(k, None)
            self.stats.evictions += 1

    def _evict_lru_if_needed(self):
        while len(self._data) > self.maxsize:
            self._data.popitem(last=False)  # LRU
            self.stats.evictions += 1

    def get(self, key: str) -> Tuple[bool, Any]:
        with self._lock:
            self._purge_expired()
            if key in self._data:
                exp, val = self._data.pop(key)
                self._data[key] = (exp, val)  # move to MRU
                self.stats.hits += 1
                return True, val
            self.stats.misses += 1
            return False, None

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        with self._lock:
            exp = 0.0
            if ttl is None:
                ttl = self.default_ttl
            if ttl and ttl > 0:
                exp = time.time() + ttl
            if key in self._data:
                self._data.pop(key)
            self._data[key] = (exp, value)
            self.stats.sets += 1
            self._evict_lru_if_needed()

    def clear(self) -> None:
        """Clear the cache"""
        with self._lock:
            self._data.clear()
            self.stats = CacheStats()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'size': len(self._data),
            'hits': self.stats.hits,
            'misses': self.stats.misses,
            'evictions': self.stats.evictions,
            'sets': self.stats.sets,
            'hit_rate': self.stats.hits / (self.stats.hits + self.stats.misses) if (self.stats.hits + self.stats.misses) > 0 else 0
        }


# Backward compatibility aliases
class LRUCache(TTLRUCache):
    """Backward compatible LRU cache"""
    def __init__(self, max_size: int = 1000):
        super().__init__(maxsize=max_size, default_ttl=0.0)
    
    def get(self, key: str) -> Optional[Any]:
        hit, val = super().get(key)
        return val if hit else None
    
    def put(self, key: str, value: Any) -> None:
        super().set(key, value)
    
    def stats(self) -> Dict[str, Any]:
        return super().get_stats()

_global_caches: Dict[str, TTLRUCache] = {}


def get_cache(slot: str = "default") -> TTLRUCache:
    if slot not in _global_caches:
        _global_caches[slot] = TTLRUCache()
    return _global_caches[slot]


def _stable_hash(obj: Any) -> str:
    try:
        data = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        data = repr(obj).encode("utf8", errors="ignore")
    return hashlib.sha256(data).hexdigest()


def memoize_ast(slot: str = "default", ttl: float = 0.0):
    """Decorator to memoize expensive eval/compile steps.

    Key = hash(code_string) + hash(static_env_keys) + function identity.
    Expects decorated function signature like:
        fn(code: str, *args, **kwargs)
    """

    def deco(fn: Callable):
        cache = get_cache(slot)
        fid = _stable_hash(fn.__qualname__)

        def make_key(code: str, *args, **kwargs) -> str:
            return _stable_hash((fid, code, tuple(args), tuple(sorted(kwargs.items()))))

        def wrapper(code: str, *args, **kwargs):
            key = make_key(code, *args, **kwargs)
            hit, val = cache.get(key)
            if hit:
                return val
            val = fn(code, *args, **kwargs)
            cache.set(key, val, ttl=ttl)
            return val

        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        return wrapper

    return deco


class ComputationCache:
    """Cache for expensive computations with TTL support"""
    
    def __init__(self, max_size: int = 500, ttl: float = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.access_times = {}
        self.computation_times = {}
        self.lock = threading.Lock()
    
    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Create cache key from function call"""
        key_data = (func_name, args, tuple(sorted(kwargs.items())))
        return hashlib.sha256(pickle.dumps(key_data)).hexdigest()
    
    def get(self, func_name: str, args: tuple, kwargs: dict) -> Optional[Tuple[Any, float]]:
        """Get cached result if available and not expired"""
        key = self._make_key(func_name, args, kwargs)
        
        with self.lock:
            if key in self.cache:
                timestamp, result = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    self.access_times[key] = time.time()
                    return result, self.computation_times.get(key, 0)
                else:
                    # Expired
                    del self.cache[key]
                    if key in self.computation_times:
                        del self.computation_times[key]
        return None
    
    def put(self, func_name: str, args: tuple, kwargs: dict, result: Any, computation_time: float) -> None:
        """Cache computation result"""
        key = self._make_key(func_name, args, kwargs)
        
        with self.lock:
            # Evict oldest if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.access_times, key=self.access_times.get)
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
                if oldest_key in self.computation_times:
                    del self.computation_times[oldest_key]
            
            self.cache[key] = (time.time(), result)
            self.access_times[key] = time.time()
            self.computation_times[key] = computation_time

def memoize(cache: Optional[LRUCache] = None, key_func: Optional[Callable] = None):
    """Decorator for memoizing function results"""
    if cache is None:
        cache = LRUCache(max_size=100)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = str((func.__name__, args, tuple(sorted(kwargs.items()))))
            
            # Check cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache.put(cache_key, result)
            return result
        
        wrapper.cache = cache
        return wrapper
    return decorator

class ASTCache:
    """Specialized cache for parsed AST nodes"""
    
    def __init__(self, max_size: int = 100):
        self.cache = LRUCache(max_size)
        self.source_hashes = {}
    
    def get_ast(self, source: str) -> Optional[Any]:
        """Get cached AST for source code"""
        source_hash = hashlib.sha256(source.encode()).hexdigest()
        return self.cache.get(source_hash)
    
    def put_ast(self, source: str, ast: Any) -> None:
        """Cache AST for source code"""
        source_hash = hashlib.sha256(source.encode()).hexdigest()
        self.cache.put(source_hash, ast)
        self.source_hashes[source_hash] = len(source)
    
    def invalidate(self, source: str) -> None:
        """Invalidate cache for specific source"""
        source_hash = hashlib.sha256(source.encode()).hexdigest()
        if source_hash in self.source_hashes:
            del self.source_hashes[source_hash]

class ResultCache:
    """Cache for parallel computation results"""
    
    def __init__(self):
        self.branch_results = {}
        self.synthesis_results = {}
        self.lock = threading.Lock()
    
    def store_branch_result(self, branch_id: str, result: Any) -> None:
        """Store result from parallel branch"""
        with self.lock:
            self.branch_results[branch_id] = (time.time(), result)
    
    def get_branch_result(self, branch_id: str) -> Optional[Any]:
        """Get result from parallel branch"""
        with self.lock:
            if branch_id in self.branch_results:
                return self.branch_results[branch_id][1]
        return None
    
    def store_synthesis(self, branches: Tuple[str, ...], result: Any) -> None:
        """Store synthesis result from multiple branches"""
        key = tuple(sorted(branches))
        with self.lock:
            self.synthesis_results[key] = (time.time(), result)
    
    def get_synthesis(self, branches: Tuple[str, ...]) -> Optional[Any]:
        """Get cached synthesis result"""
        key = tuple(sorted(branches))
        with self.lock:
            if key in self.synthesis_results:
                return self.synthesis_results[key][1]
        return None
    
    def clear_old_results(self, max_age: float = 300) -> None:
        """Clear results older than max_age seconds"""
        current_time = time.time()
        with self.lock:
            # Clear old branch results
            self.branch_results = {
                k: v for k, v in self.branch_results.items()
                if current_time - v[0] < max_age
            }
            # Clear old synthesis results
            self.synthesis_results = {
                k: v for k, v in self.synthesis_results.items()
                if current_time - v[0] < max_age
            }

class TensorCache:
    """Specialized cache for tensor operations"""
    
    def __init__(self, max_memory_mb: int = 500):
        self.cache = {}
        self.memory_usage = 0
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.lock = threading.Lock()
        self.weak_refs = weakref.WeakValueDictionary()
    
    def _estimate_size(self, tensor: Any) -> int:
        """Estimate memory size of tensor"""
        try:
            import numpy as np
            if isinstance(tensor, np.ndarray):
                return tensor.nbytes
        except ImportError:
            pass
        # Rough estimate for other objects
        return len(pickle.dumps(tensor))
    
    def cache_operation(self, op_name: str, inputs: tuple, result: Any) -> None:
        """Cache tensor operation result"""
        key = (op_name, tuple(id(x) for x in inputs))
        size = self._estimate_size(result)
        
        with self.lock:
            # Check if we need to evict
            while self.memory_usage + size > self.max_memory and self.cache:
                # Evict least recently used
                oldest_key = next(iter(self.cache))
                evicted = self.cache.pop(oldest_key)
                self.memory_usage -= self._estimate_size(evicted)
            
            self.cache[key] = result
            self.memory_usage += size
            self.weak_refs[key] = result
    
    def get_operation(self, op_name: str, inputs: tuple) -> Optional[Any]:
        """Get cached tensor operation result"""
        key = (op_name, tuple(id(x) for x in inputs))
        
        with self.lock:
            # Try strong reference first
            if key in self.cache:
                return self.cache[key]
            # Try weak reference
            if key in self.weak_refs:
                result = self.weak_refs[key]
                # Promote to strong reference
                self.cache[key] = result
                self.memory_usage += self._estimate_size(result)
                return result
        return None

# Global cache instances
_ast_cache = ASTCache()
_computation_cache = ComputationCache()
_result_cache = ResultCache()
_tensor_cache = TensorCache()

def get_ast_cache() -> ASTCache:
    """Get global AST cache"""
    return _ast_cache

def get_computation_cache() -> ComputationCache:
    """Get global computation cache"""
    return _computation_cache

def get_result_cache() -> ResultCache:
    """Get global result cache"""
    return _result_cache

def get_tensor_cache() -> TensorCache:
    """Get global tensor cache"""
    return _tensor_cache

def clear_all_caches():
    """Clear all global caches"""
    _ast_cache.cache.clear()
    _computation_cache.cache.clear()
    _result_cache.branch_results.clear()
    _result_cache.synthesis_results.clear()
    _tensor_cache.cache.clear()
    _tensor_cache.memory_usage = 0

def get_cache_stats() -> Dict[str, Any]:
    """Get statistics for all caches"""
    return {
        'ast_cache': _ast_cache.cache.stats(),
        'computation_cache': {
            'size': len(_computation_cache.cache),
            'ttl': _computation_cache.ttl
        },
        'result_cache': {
            'branches': len(_result_cache.branch_results),
            'synthesis': len(_result_cache.synthesis_results)
        },
        'tensor_cache': {
            'size': len(_tensor_cache.cache),
            'memory_mb': _tensor_cache.memory_usage / (1024 * 1024)
        }
    }