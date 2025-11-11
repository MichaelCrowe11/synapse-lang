
import functools
from typing import Any


def memoize_parser(func):
    '''Memoization decorator for parser methods to cache repeated parsing patterns'''
    cache = {}

    @functools.wraps(func)
    def wrapper(self, *args):
        # Create cache key from position and args
        key = (self.position, args)
        if key not in cache:
            cache[key] = func(self, *args)
        return cache[key]

    wrapper.cache = cache
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper


def cache_lookup(max_size=128):
    '''LRU cache for variable/symbol lookups'''
    return functools.lru_cache(maxsize=max_size)
