"""
Distributed Computing Support for Synapse Language
Enables parallel and distributed execution of scientific computations
"""

import asyncio
import concurrent.futures
import multiprocessing as mp
from multiprocessing import Pool, Process, Queue, Manager, Lock
import threading
import time
import pickle
import socket
import json
from typing import Any, List, Dict, Tuple, Callable, Union, Optional, Iterable
from dataclasses import dataclass, field
from enum import Enum
import warnings
import sys
import os
from pathlib import Path

# Distributed computing frameworks
try:
    import dask
    import dask.distributed as dd
    from dask.distributed import Client, as_completed
    from dask import delayed
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False

try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False

try:
    import mpi4py
    from mpi4py import MPI
    MPI_AVAILABLE = True
except ImportError:
    MPI_AVAILABLE = False

import numpy as np
from .uncertainty import UncertainValue, UncertaintyPropagator


class ComputeBackend(Enum):
    """Available distributed computing backends"""
    THREADING = "threading"
    MULTIPROCESSING = "multiprocessing"
    DASK = "dask"
    RAY = "ray"
    MPI = "mpi"
    ASYNCIO = "asyncio"


@dataclass
class ComputeTask:
    """Represents a computational task with metadata"""
    task_id: str
    function: Callable
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict = field(default_factory=dict)
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[float] = None


@dataclass
class ComputeResult:
    """Result of a distributed computation"""
    task_id: str
    result: Any
    execution_time: float
    worker_id: Optional[str] = None
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DistributedExecutor:
    """
    High-level interface for distributed computing in Synapse Language
    Supports multiple backends and execution patterns
    """
    
    def __init__(self, backend: Union[str, ComputeBackend] = ComputeBackend.THREADING,
                 n_workers: Optional[int] = None, **backend_config):
        
        self.backend = ComputeBackend(backend) if isinstance(backend, str) else backend
        self.n_workers = n_workers or mp.cpu_count()
        self.backend_config = backend_config
        
        # Backend-specific initialization
        self.client = None
        self.executor = None
        self.cluster = None
        
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the selected distributed computing backend"""
        
        if self.backend == ComputeBackend.THREADING:
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.n_workers
            )
            
        elif self.backend == ComputeBackend.MULTIPROCESSING:
            self.executor = concurrent.futures.ProcessPoolExecutor(
                max_workers=self.n_workers
            )
            
        elif self.backend == ComputeBackend.DASK:
            if not DASK_AVAILABLE:
                raise ImportError("Dask is required for distributed computing")
            
            # Initialize Dask client
            if 'address' in self.backend_config:
                self.client = Client(self.backend_config['address'])
            else:
                from dask.distributed import LocalCluster
                self.cluster = LocalCluster(n_workers=self.n_workers, 
                                          processes=True, **self.backend_config)
                self.client = Client(self.cluster)
                
        elif self.backend == ComputeBackend.RAY:
            if not RAY_AVAILABLE:
                raise ImportError("Ray is required for distributed computing")
            
            if not ray.is_initialized():
                ray.init(num_cpus=self.n_workers, **self.backend_config)
                
        elif self.backend == ComputeBackend.MPI:
            if not MPI_AVAILABLE:
                raise ImportError("MPI4Py is required for MPI computing")
            
            self.mpi_comm = MPI.COMM_WORLD
            self.mpi_rank = self.mpi_comm.Get_rank()
            self.mpi_size = self.mpi_comm.Get_size()
            
        elif self.backend == ComputeBackend.ASYNCIO:
            # AsyncIO executor will be created as needed
            pass
    
    def submit(self, function: Callable, *args, **kwargs) -> ComputeTask:
        """Submit a single task for execution"""
        task_id = f"task_{time.time()}_{np.random.randint(10000)}"
        
        task = ComputeTask(
            task_id=task_id,
            function=function,
            args=args,
            kwargs=kwargs
        )
        
        return task
    
    def execute_single(self, task: ComputeTask) -> ComputeResult:
        """Execute a single task"""
        start_time = time.time()
        
        try:
            if self.backend == ComputeBackend.THREADING:
                future = self.executor.submit(task.function, *task.args, **task.kwargs)
                result = future.result(timeout=task.timeout)
                
            elif self.backend == ComputeBackend.MULTIPROCESSING:
                future = self.executor.submit(task.function, *task.args, **task.kwargs)
                result = future.result(timeout=task.timeout)
                
            elif self.backend == ComputeBackend.DASK:
                future = self.client.submit(task.function, *task.args, **task.kwargs)
                result = future.result(timeout=task.timeout)
                
            elif self.backend == ComputeBackend.RAY:
                @ray.remote
                def ray_wrapper(func, args, kwargs):
                    return func(*args, **kwargs)
                
                future = ray_wrapper.remote(task.function, task.args, task.kwargs)
                result = ray.get(future)
                
            else:
                # Fallback to direct execution
                result = task.function(*task.args, **task.kwargs)
            
            execution_time = time.time() - start_time
            
            return ComputeResult(
                task_id=task.task_id,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ComputeResult(
                task_id=task.task_id,
                result=None,
                execution_time=execution_time,
                error=e
            )
    
    def execute_parallel(self, tasks: List[ComputeTask]) -> List[ComputeResult]:
        """Execute multiple tasks in parallel"""
        
        if self.backend == ComputeBackend.DASK:
            return self._execute_dask_parallel(tasks)
        elif self.backend == ComputeBackend.RAY:
            return self._execute_ray_parallel(tasks)
        elif self.backend == ComputeBackend.MPI:
            return self._execute_mpi_parallel(tasks)
        elif self.backend == ComputeBackend.ASYNCIO:
            return asyncio.run(self._execute_async_parallel(tasks))
        else:
            return self._execute_concurrent_parallel(tasks)
    
    def _execute_concurrent_parallel(self, tasks: List[ComputeTask]) -> List[ComputeResult]:
        """Execute tasks using concurrent.futures"""
        futures = {}
        
        for task in tasks:
            future = self.executor.submit(task.function, *task.args, **task.kwargs)
            futures[future] = task
        
        results = []
        for future in concurrent.futures.as_completed(futures, timeout=300):
            task = futures[future]
            start_time = time.time()
            
            try:
                result = future.result()
                execution_time = time.time() - start_time
                
                results.append(ComputeResult(
                    task_id=task.task_id,
                    result=result,
                    execution_time=execution_time
                ))
            except Exception as e:
                execution_time = time.time() - start_time
                results.append(ComputeResult(
                    task_id=task.task_id,
                    result=None,
                    execution_time=execution_time,
                    error=e
                ))
        
        return results
    
    def _execute_dask_parallel(self, tasks: List[ComputeTask]) -> List[ComputeResult]:
        """Execute tasks using Dask"""
        futures = []
        
        for task in tasks:
            future = self.client.submit(task.function, *task.args, **task.kwargs)
            futures.append((future, task))
        
        results = []
        for future, task in futures:
            start_time = time.time()
            
            try:
                result = future.result()
                execution_time = time.time() - start_time
                
                results.append(ComputeResult(
                    task_id=task.task_id,
                    result=result,
                    execution_time=execution_time,
                    worker_id=str(future.key)
                ))
            except Exception as e:
                execution_time = time.time() - start_time
                results.append(ComputeResult(
                    task_id=task.task_id,
                    result=None,
                    execution_time=execution_time,
                    error=e
                ))
        
        return results
    
    def _execute_ray_parallel(self, tasks: List[ComputeTask]) -> List[ComputeResult]:
        """Execute tasks using Ray"""
        @ray.remote
        def ray_task_wrapper(func, args, kwargs):
            return func(*args, **kwargs)
        
        futures = []
        for task in tasks:
            future = ray_task_wrapper.remote(task.function, task.args, task.kwargs)
            futures.append((future, task))
        
        results = []
        for future, task in futures:
            start_time = time.time()
            
            try:
                result = ray.get(future)
                execution_time = time.time() - start_time
                
                results.append(ComputeResult(
                    task_id=task.task_id,
                    result=result,
                    execution_time=execution_time
                ))
            except Exception as e:
                execution_time = time.time() - start_time
                results.append(ComputeResult(
                    task_id=task.task_id,
                    result=None,
                    execution_time=execution_time,
                    error=e
                ))
        
        return results
    
    def _execute_mpi_parallel(self, tasks: List[ComputeTask]) -> List[ComputeResult]:
        """Execute tasks using MPI"""
        results = []
        
        # Simple task distribution: divide tasks among MPI processes
        tasks_per_process = len(tasks) // self.mpi_size
        start_idx = self.mpi_rank * tasks_per_process
        end_idx = start_idx + tasks_per_process
        
        # Last process gets remaining tasks
        if self.mpi_rank == self.mpi_size - 1:
            end_idx = len(tasks)
        
        local_tasks = tasks[start_idx:end_idx]
        local_results = []
        
        for task in local_tasks:
            result = self.execute_single(task)
            local_results.append(result)
        
        # Gather results from all processes
        all_results = self.mpi_comm.gather(local_results, root=0)
        
        if self.mpi_rank == 0:
            # Flatten results from all processes
            for process_results in all_results:
                results.extend(process_results)
        
        # Broadcast final results to all processes
        results = self.mpi_comm.bcast(results, root=0)
        
        return results
    
    async def _execute_async_parallel(self, tasks: List[ComputeTask]) -> List[ComputeResult]:
        """Execute tasks using AsyncIO"""
        async def async_task_wrapper(task: ComputeTask):
            loop = asyncio.get_event_loop()
            start_time = time.time()
            
            try:
                # Run CPU-bound task in thread pool
                result = await loop.run_in_executor(
                    None, task.function, *task.args
                )
                execution_time = time.time() - start_time
                
                return ComputeResult(
                    task_id=task.task_id,
                    result=result,
                    execution_time=execution_time
                )
            except Exception as e:
                execution_time = time.time() - start_time
                return ComputeResult(
                    task_id=task.task_id,
                    result=None,
                    execution_time=execution_time,
                    error=e
                )
        
        # Execute all tasks concurrently
        coroutines = [async_task_wrapper(task) for task in tasks]
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        return [r for r in results if isinstance(r, ComputeResult)]
    
    def map(self, function: Callable, iterable: Iterable, chunksize: Optional[int] = None) -> List[Any]:
        """Map function over iterable in parallel"""
        
        if self.backend == ComputeBackend.DASK:
            if chunksize:
                # Use Dask bag for chunked processing
                import dask.bag as db
                bag = db.from_sequence(iterable, partition_size=chunksize)
                return bag.map(function).compute()
            else:
                futures = self.client.map(function, iterable)
                return self.client.gather(futures)
        
        elif self.backend == ComputeBackend.RAY:
            @ray.remote
            def ray_map_func(item):
                return function(item)
            
            futures = [ray_map_func.remote(item) for item in iterable]
            return ray.get(futures)
        
        else:
            # Use standard executor map
            if hasattr(self.executor, 'map'):
                return list(self.executor.map(function, iterable, chunksize=chunksize))
            else:
                # Fallback
                return [function(item) for item in iterable]
    
    def close(self):
        """Clean up resources"""
        if self.executor:
            self.executor.shutdown(wait=True)
        
        if self.client:
            self.client.close()
        
        if self.cluster:
            self.cluster.close()
        
        if self.backend == ComputeBackend.RAY and ray.is_initialized():
            ray.shutdown()


class ScientificParallelization:
    """
    Scientific computing patterns for parallel execution
    Handles common patterns like parameter sweeps, Monte Carlo simulations
    """
    
    def __init__(self, executor: DistributedExecutor):
        self.executor = executor
    
    def parameter_sweep(self, function: Callable, 
                       parameter_grid: Dict[str, List[Any]]) -> Dict[Tuple, ComputeResult]:
        """Parallel parameter sweep across parameter combinations"""
        import itertools
        
        # Generate all parameter combinations
        param_names = list(parameter_grid.keys())
        param_values = list(parameter_grid.values())
        param_combinations = list(itertools.product(*param_values))
        
        # Create tasks
        tasks = []
        for i, param_combo in enumerate(param_combinations):
            kwargs = dict(zip(param_names, param_combo))
            task = ComputeTask(
                task_id=f"param_sweep_{i}",
                function=function,
                kwargs=kwargs
            )
            tasks.append(task)
        
        # Execute in parallel
        results = self.executor.execute_parallel(tasks)
        
        # Return results indexed by parameter combination
        result_dict = {}
        for result, param_combo in zip(results, param_combinations):
            result_dict[param_combo] = result
        
        return result_dict
    
    def monte_carlo_simulation(self, simulation_func: Callable, 
                              n_simulations: int, 
                              batch_size: Optional[int] = None,
                              **sim_kwargs) -> List[ComputeResult]:
        """Parallel Monte Carlo simulation"""
        
        batch_size = batch_size or min(1000, max(1, n_simulations // self.executor.n_workers))
        
        tasks = []
        for batch_start in range(0, n_simulations, batch_size):
            batch_end = min(batch_start + batch_size, n_simulations)
            batch_size_actual = batch_end - batch_start
            
            def batch_simulation(n_runs, **kwargs):
                """Run multiple simulations in a batch"""
                results = []
                for _ in range(n_runs):
                    results.append(simulation_func(**kwargs))
                return results
            
            task = ComputeTask(
                task_id=f"mc_batch_{batch_start}_{batch_end}",
                function=batch_simulation,
                args=(batch_size_actual,),
                kwargs=sim_kwargs
            )
            tasks.append(task)
        
        return self.executor.execute_parallel(tasks)
    
    def uncertainty_propagation_parallel(self, function: Callable,
                                       uncertain_inputs: List[UncertainValue],
                                       n_samples: int = 10000,
                                       batch_size: Optional[int] = None) -> UncertainValue:
        """Parallel uncertainty propagation using Monte Carlo"""
        
        batch_size = batch_size or min(1000, max(1, n_samples // self.executor.n_workers))
        
        def batch_uncertainty_calc(n_batch_samples: int, uncertain_vals: List[UncertainValue]):
            """Calculate uncertainty for a batch of samples"""
            results = []
            for _ in range(n_batch_samples):
                # Sample from each uncertain input
                sample_values = []
                for uval in uncertain_vals:
                    sample_values.append(np.random.choice(uval.samples))
                
                # Apply function to samples
                try:
                    result = function(*sample_values)
                    results.append(result)
                except:
                    pass  # Skip failed evaluations
            
            return results
        
        # Create batch tasks
        tasks = []
        for batch_start in range(0, n_samples, batch_size):
            batch_end = min(batch_start + batch_size, n_samples)
            batch_size_actual = batch_end - batch_start
            
            task = ComputeTask(
                task_id=f"uncertainty_batch_{batch_start}",
                function=batch_uncertainty_calc,
                args=(batch_size_actual, uncertain_inputs)
            )
            tasks.append(task)
        
        # Execute parallel uncertainty propagation
        results = self.executor.execute_parallel(tasks)
        
        # Combine results from all batches
        all_samples = []
        for result in results:
            if result.error is None and result.result:
                all_samples.extend(result.result)
        
        if not all_samples:
            raise RuntimeError("All uncertainty propagation samples failed")
        
        all_samples = np.array(all_samples)
        mean_result = np.mean(all_samples)
        std_result = np.std(all_samples)
        
        return UncertainValue(mean_result, std_result, samples=all_samples)


# Integration with Synapse language constructs
class DistributedIntegration:
    """Integration layer for distributed computing in Synapse language"""
    
    @staticmethod
    def create_parallel_context(backend: str = "threading", 
                               n_workers: Optional[int] = None) -> DistributedExecutor:
        """Create distributed execution context from Synapse syntax"""
        return DistributedExecutor(backend, n_workers)
    
    @staticmethod
    def parallel_branches(executor: DistributedExecutor, 
                         branch_functions: Dict[str, Callable]) -> Dict[str, ComputeResult]:
        """Execute parallel branches from Synapse parallel construct"""
        tasks = []
        
        for branch_name, branch_func in branch_functions.items():
            task = ComputeTask(
                task_id=f"branch_{branch_name}",
                function=branch_func
            )
            tasks.append(task)
        
        results = executor.execute_parallel(tasks)
        
        # Return results indexed by branch name
        branch_results = {}
        for result, (branch_name, _) in zip(results, branch_functions.items()):
            branch_results[branch_name] = result
        
        return branch_results
    
    @staticmethod
    def distributed_hypothesis_testing(executor: DistributedExecutor,
                                     hypothesis_tests: List[Callable]) -> List[ComputeResult]:
        """Execute hypothesis tests in parallel"""
        tasks = []
        
        for i, test_func in enumerate(hypothesis_tests):
            task = ComputeTask(
                task_id=f"hypothesis_{i}",
                function=test_func
            )
            tasks.append(task)
        
        return executor.execute_parallel(tasks)
    
    @staticmethod
    def parallel_pipeline_stages(executor: DistributedExecutor,
                               pipeline_stages: List[Tuple[str, Callable, Any]]) -> Dict[str, ComputeResult]:
        """Execute pipeline stages with dependency handling"""
        results = {}
        
        # Simple sequential execution for now (could be enhanced with dependency graph)
        for stage_name, stage_func, stage_input in pipeline_stages:
            # Use results from previous stages as input if needed
            if isinstance(stage_input, str) and stage_input in results:
                stage_input = results[stage_input].result
            
            task = ComputeTask(
                task_id=f"pipeline_{stage_name}",
                function=stage_func,
                args=(stage_input,) if stage_input is not None else ()
            )
            
            result = executor.execute_single(task)
            results[stage_name] = result
        
        return results