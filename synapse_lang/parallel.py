"""
Parallel computing module for Synapse language.
Provides parallel execution, distributed computing, and parameter sweep capabilities.
"""

import asyncio
import concurrent.futures
import multiprocessing as mp
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
from functools import partial
import itertools
from dataclasses import dataclass


@dataclass
class ParallelConfig:
    """Configuration for parallel execution."""
    max_workers: Optional[int] = None
    chunk_size: int = 1
    backend: str = "threading"  # "threading", "multiprocessing", or "asyncio"
    timeout: Optional[float] = None


class ParallelBlock:
    """Manages parallel execution of code blocks."""
    
    def __init__(self, config: Optional[ParallelConfig] = None):
        self.config = config or ParallelConfig()
        self.results = []
        
    def execute(self, tasks: List[Callable], *args, **kwargs) -> List[Any]:
        """Execute tasks in parallel."""
        if self.config.backend == "threading":
            return self._execute_threaded(tasks, *args, **kwargs)
        elif self.config.backend == "multiprocessing":
            return self._execute_multiprocess(tasks, *args, **kwargs)
        elif self.config.backend == "asyncio":
            return asyncio.run(self._execute_async(tasks, *args, **kwargs))
        else:
            raise ValueError(f"Unknown backend: {self.config.backend}")
    
    def _execute_threaded(self, tasks: List[Callable], *args, **kwargs) -> List[Any]:
        """Execute using ThreadPoolExecutor."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = [executor.submit(task, *args, **kwargs) for task in tasks]
            return [f.result(timeout=self.config.timeout) for f in futures]
    
    def _execute_multiprocess(self, tasks: List[Callable], *args, **kwargs) -> List[Any]:
        """Execute using ProcessPoolExecutor."""
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = [executor.submit(task, *args, **kwargs) for task in tasks]
            return [f.result(timeout=self.config.timeout) for f in futures]
    
    async def _execute_async(self, tasks: List[Callable], *args, **kwargs) -> List[Any]:
        """Execute using asyncio."""
        async_tasks = []
        for task in tasks:
            if asyncio.iscoroutinefunction(task):
                async_tasks.append(task(*args, **kwargs))
            else:
                # Wrap sync function in async
                async_tasks.append(asyncio.to_thread(task, *args, **kwargs))
        return await asyncio.gather(*async_tasks)


class ParameterSweep:
    """Performs parameter sweeps for scientific computing."""
    
    def __init__(self, function: Callable, parallel_config: Optional[ParallelConfig] = None):
        self.function = function
        self.parallel_config = parallel_config or ParallelConfig()
        
    def sweep(self, **param_ranges) -> Dict[Tuple, Any]:
        """
        Perform parameter sweep over given ranges.
        
        Args:
            **param_ranges: Keyword arguments with parameter names and their ranges
            
        Returns:
            Dictionary mapping parameter tuples to results
        """
        # Generate all parameter combinations
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        combinations = list(itertools.product(*param_values))
        
        # Create tasks for each combination
        tasks = []
        for combo in combinations:
            kwargs = dict(zip(param_names, combo))
            tasks.append(partial(self.function, **kwargs))
        
        # Execute in parallel
        block = ParallelBlock(self.parallel_config)
        results = block.execute(tasks)
        
        # Return results mapped to parameter combinations
        return dict(zip(combinations, results))
    
    def sweep_grid(self, param_grid: Dict[str, List]) -> np.ndarray:
        """
        Perform grid-based parameter sweep.
        
        Args:
            param_grid: Dictionary of parameter names to value lists
            
        Returns:
            N-dimensional array of results
        """
        results_dict = self.sweep(**param_grid)
        
        # Reshape results into grid
        shapes = [len(v) for v in param_grid.values()]
        results_array = np.zeros(shapes)
        
        for combo, result in results_dict.items():
            indices = combo
            results_array[indices] = result
            
        return results_array


class ThoughtStream:
    """Represents a parallel thought stream for hypothesis exploration."""
    
    def __init__(self, stream_id: str, hypothesis: Callable):
        self.stream_id = stream_id
        self.hypothesis = hypothesis
        self.result = None
        self.status = "pending"
        
    async def process(self, *args, **kwargs):
        """Process the hypothesis asynchronously."""
        self.status = "processing"
        try:
            if asyncio.iscoroutinefunction(self.hypothesis):
                self.result = await self.hypothesis(*args, **kwargs)
            else:
                self.result = await asyncio.to_thread(self.hypothesis, *args, **kwargs)
            self.status = "completed"
        except Exception as e:
            self.result = e
            self.status = "failed"
        return self.result


class ParallelSynthesizer:
    """Synthesizes results from parallel computations."""
    
    @staticmethod
    def consensus(results: List[Any], threshold: float = 0.95) -> bool:
        """Check if results reach consensus."""
        if not results:
            return False
            
        # For numeric results
        if all(isinstance(r, (int, float)) for r in results):
            mean = np.mean(results)
            std = np.std(results)
            if std == 0:
                return True
            cv = std / mean  # Coefficient of variation
            return cv < (1 - threshold)
        
        # For boolean results
        if all(isinstance(r, bool) for r in results):
            agreement = sum(results) / len(results)
            return agreement >= threshold or agreement <= (1 - threshold)
        
        # For other types, check equality
        return len(set(str(r) for r in results)) == 1
    
    @staticmethod
    def merge(results: List[Any], strategy: str = "mean") -> Any:
        """Merge parallel results using specified strategy."""
        if not results:
            return None
            
        if strategy == "mean" and all(isinstance(r, (int, float)) for r in results):
            return np.mean(results)
        elif strategy == "median" and all(isinstance(r, (int, float)) for r in results):
            return np.median(results)
        elif strategy == "vote":
            # Majority voting
            from collections import Counter
            counts = Counter(results)
            return counts.most_common(1)[0][0]
        elif strategy == "all":
            return results
        else:
            return results[0]  # Default to first result


# Public API functions

def parallel_block(tasks: Union[List[Callable], Dict[str, Callable], Callable] = None, 
                  config: Optional[Dict] = None,
                  function: Optional[Callable] = None,
                  inputs: Optional[List] = None,
                  **kwargs) -> Union[List, Dict]:
    """
    Execute tasks in parallel.
    
    Args:
        tasks: List of functions or dict of named functions
        config: Optional configuration dict
        function: Single function to apply to multiple inputs
        inputs: List of inputs for the function
        **kwargs: Additional keyword arguments
        
    Returns:
        List or dict of results matching input structure
    """
    cfg = ParallelConfig(**config) if config else ParallelConfig()
    block = ParallelBlock(cfg)
    
    # Handle function + inputs pattern (common use case)
    if function is not None and inputs is not None:
        from functools import partial
        task_list = [partial(function, inp) for inp in inputs]
        return block.execute(task_list)
    
    # Handle tasks argument
    if tasks is not None:
        if isinstance(tasks, dict):
            # Named tasks
            task_list = list(tasks.values())
            results = block.execute(task_list)
            return dict(zip(tasks.keys(), results))
        elif callable(tasks):
            # Single function
            return block.execute([tasks])[0]
        else:
            # List of tasks
            return block.execute(tasks)
    
    raise ValueError("Must provide either 'tasks' or both 'function' and 'inputs'")


def parameter_sweep(function: Callable, 
                   param_ranges: Dict[str, List] = None,
                   parameters: Dict[str, List] = None,
                   parallel: bool = True,
                   **kwargs) -> Dict[Tuple, Any]:
    """
    Perform parameter sweep over given ranges.
    
    Args:
        function: Function to evaluate
        param_ranges: Dictionary of parameter names to value ranges
        parameters: Alternative name for param_ranges
        parallel: Whether to run in parallel
        **kwargs: Additional parameter ranges
        
    Returns:
        Dictionary mapping parameter tuples to results
    """
    # Handle alternative parameter names
    if parameters is not None:
        param_ranges = parameters
    elif param_ranges is None and kwargs:
        param_ranges = kwargs
    
    if param_ranges is None:
        raise ValueError("Must provide parameter ranges")
    
    config = ParallelConfig() if parallel else ParallelConfig(max_workers=1)
    sweeper = ParameterSweep(function, config)
    return sweeper.sweep(**param_ranges)


async def thought_streams(hypotheses: Dict[str, Callable]) -> Dict[str, Any]:
    """
    Process multiple hypotheses as parallel thought streams.
    
    Args:
        hypotheses: Dictionary of stream names to hypothesis functions
        
    Returns:
        Dictionary of stream names to results
    """
    streams = [ThoughtStream(name, hyp) for name, hyp in hypotheses.items()]
    tasks = [stream.process() for stream in streams]
    await asyncio.gather(*tasks)
    return {stream.stream_id: stream.result for stream in streams}


def synthesize(results: List[Any], strategy: str = "consensus") -> Any:
    """
    Synthesize results from parallel computations.
    
    Args:
        results: List of results to synthesize
        strategy: Synthesis strategy ("consensus", "mean", "median", "vote", "all")
        
    Returns:
        Synthesized result
    """
    synthesizer = ParallelSynthesizer()
    
    if strategy == "consensus":
        return synthesizer.consensus(results)
    else:
        return synthesizer.merge(results, strategy)


# Additional features for compatibility

def optimize_parallel_execution(tasks: List[Callable], dependencies: Optional[Dict] = None) -> List:
    """Optimize parallel execution based on task dependencies."""
    # Simple implementation - just run tasks in parallel
    config = ParallelConfig(backend="threading")
    block = ParallelBlock(config)
    return block.execute(tasks)


def distributed_compute(func: Callable, data: List, workers: int = None) -> List:
    """Distributed computation across workers."""
    config = ParallelConfig(max_workers=workers, backend="multiprocessing")
    block = ParallelBlock(config)
    tasks = [partial(func, item) for item in data]
    return block.execute(tasks)


def parallel_map(func: Callable, iterable, workers: int = None) -> List:
    """Parallel map operation."""
    return distributed_compute(func, list(iterable), workers)


def parallel_reduce(func: Callable, iterable, initial=None) -> Any:
    """Parallel reduce operation."""
    from functools import reduce
    results = parallel_map(lambda x: x, iterable)
    return reduce(func, results, initial) if initial is not None else reduce(func, results)


class SharedState:
    """Thread-safe shared state for parallel computations."""
    
    def __init__(self, initial_value=None):
        import threading
        self._value = initial_value
        self._lock = threading.Lock()
    
    def get(self):
        with self._lock:
            return self._value
    
    def set(self, value):
        with self._lock:
            self._value = value
    
    def update(self, func):
        with self._lock:
            self._value = func(self._value)


# Backend stubs for testing
class DaskBackend:
    """Dask backend for distributed computing (stub)."""
    def __init__(self):
        raise NotImplementedError("Dask backend not yet implemented. Install dask to use.")


class MPIBackend:
    """MPI backend for HPC computing (stub)."""
    def __init__(self):
        raise NotImplementedError("MPI backend not yet implemented. Install mpi4py to use.")


class RayBackend:
    """Ray backend for distributed computing (stub)."""
    def __init__(self):
        raise NotImplementedError("Ray backend not yet implemented. Install ray to use.")


# Export public API
__all__ = [
    'ParallelConfig',
    'ParallelBlock', 
    'ParameterSweep',
    'ThoughtStream',
    'ParallelSynthesizer',
    'SharedState',
    'DaskBackend',
    'MPIBackend', 
    'RayBackend',
    'parallel_block',
    'parameter_sweep',
    'thought_streams',
    'synthesize',
    'distributed_compute',
    'parallel_map',
    'parallel_reduce',
    'optimize_parallel_execution'
]