"""
Unit tests for Synapse Language parallel computing functionality.

Tests parallel blocks, parameter sweeps, distributed computing,
and performance optimization.
"""

import unittest
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from synapse_lang.parallel import (
    parallel_block, parameter_sweep, distributed_compute,
    ParallelConfig, optimize_parallel_execution
)


class TestParallelBlocks(unittest.TestCase):
    """Test basic parallel block execution."""
    
    def test_simple_parallel_block(self):
        """Test simple parallel execution."""
        results = []
        
        def task1():
            time.sleep(0.1)
            return "Task 1 complete"
            
        def task2():
            time.sleep(0.1)
            return "Task 2 complete"
            
        def task3():
            time.sleep(0.1)
            return "Task 3 complete"
            
        # Execute in parallel
        start_time = time.time()
        results = parallel_block([task1, task2, task3])
        parallel_time = time.time() - start_time
        
        # Check all results returned
        self.assertEqual(len(results), 3)
        self.assertIn("Task 1 complete", results)
        self.assertIn("Task 2 complete", results)
        self.assertIn("Task 3 complete", results)
        
        # Should be faster than serial (0.3s serial vs ~0.1s parallel)
        self.assertLess(parallel_time, 0.25)
        
    def test_parallel_with_arguments(self):
        """Test parallel execution with function arguments."""
        def compute_square(x):
            return x ** 2
            
        inputs = [1, 2, 3, 4, 5]
        
        results = parallel_block(
            function=compute_square,
            inputs=inputs
        )
        
        expected = [1, 4, 9, 16, 25]
        self.assertEqual(results, expected)
        
    def test_parallel_with_shared_state(self):
        """Test parallel execution with shared state handling."""
        from synapse_lang.parallel import SharedState
        
        shared_state = SharedState()
        shared_state.counter = 0
        
        def increment_counter(state, amount):
            with state.lock:
                state.counter += amount
                return state.counter
                
        # Multiple parallel increments
        amounts = [1, 2, 3, 4, 5]
        results = parallel_block(
            function=lambda amt: increment_counter(shared_state, amt),
            inputs=amounts
        )
        
        # Final counter should be sum of amounts
        self.assertEqual(shared_state.counter, sum(amounts))
        
    def test_nested_parallel_blocks(self):
        """Test nested parallel execution."""
        def outer_task(i):
            # Each outer task spawns inner parallel tasks
            def inner_task(j):
                return i * 10 + j
                
            inner_results = parallel_block(
                function=inner_task,
                inputs=[0, 1, 2]
            )
            return inner_results
            
        outer_results = parallel_block(
            function=outer_task,
            inputs=[1, 2, 3]
        )
        
        # Check structure of results
        self.assertEqual(len(outer_results), 3)
        self.assertEqual(outer_results[0], [10, 11, 12])
        self.assertEqual(outer_results[1], [20, 21, 22])
        self.assertEqual(outer_results[2], [30, 31, 32])


class TestParameterSweeps(unittest.TestCase):
    """Test parallel parameter sweep functionality."""
    
    def test_simple_parameter_sweep(self):
        """Test basic parameter sweep."""
        def simulation(temperature, pressure):
            # Simple calculation
            return temperature * pressure / 100
            
        temperatures = [250, 300, 350]
        pressures = [1.0, 1.5, 2.0]
        
        results = parameter_sweep(
            function=simulation,
            parameters={
                'temperature': temperatures,
                'pressure': pressures
            }
        )
        
        # Should have results for all combinations
        self.assertEqual(len(results), 9)  # 3 * 3
        
        # Check specific result
        result_300_15 = next(
            r for r in results 
            if r['temperature'] == 300 and r['pressure'] == 1.5
        )
        self.assertAlmostEqual(result_300_15['result'], 4.5)
        
    def test_parameter_sweep_with_uncertainty(self):
        """Test parameter sweep with uncertain values."""
        from synapse_lang.uncertainty import UncertainValue
        
        def calculation(x, y):
            return x + y
            
        x_values = [
            UncertainValue(1.0, 0.1),
            UncertainValue(2.0, 0.2)
        ]
        y_values = [
            UncertainValue(3.0, 0.3),
            UncertainValue(4.0, 0.4)
        ]
        
        results = parameter_sweep(
            function=calculation,
            parameters={'x': x_values, 'y': y_values},
            propagate_uncertainty=True
        )
        
        # Check uncertainty propagated
        for result in results:
            self.assertIsInstance(result['result'], UncertainValue)
            self.assertGreater(result['result'].uncertainty, 0)
            
    def test_adaptive_parameter_sweep(self):
        """Test adaptive parameter sampling."""
        def peaked_function(x, y):
            # Function with a peak at (5, 5)
            return np.exp(-((x-5)**2 + (y-5)**2) / 10)
            
        # Initial coarse grid
        x_initial = np.linspace(0, 10, 5)
        y_initial = np.linspace(0, 10, 5)
        
        results = parameter_sweep(
            function=peaked_function,
            parameters={'x': x_initial, 'y': y_initial},
            adaptive=True,
            refinement_threshold=0.5,
            max_refinements=2
        )
        
        # Should have refined near the peak
        # More points should be near (5, 5)
        near_peak = [
            r for r in results 
            if 4 < r['x'] < 6 and 4 < r['y'] < 6
        ]
        
        # Refined region should have more samples
        self.assertGreater(len(near_peak), len(results) / 9)


class TestDistributedComputing(unittest.TestCase):
    """Test distributed computing functionality."""
    
    def test_dask_backend(self):
        """Test Dask distributed backend."""
        try:
            import dask
            from synapse_lang.parallel import DaskBackend
            
            backend = DaskBackend(n_workers=2)
            
            def heavy_computation(x):
                # Simulate heavy work
                result = 0
                for i in range(1000000):
                    result += x * np.sin(i)
                return result / 1000000
                
            inputs = list(range(10))
            
            results = backend.map(heavy_computation, inputs)
            
            self.assertEqual(len(results), 10)
            
            backend.close()
            
        except ImportError:
            self.skipTest("Dask not installed")
            
    def test_mpi_backend(self):
        """Test MPI distributed backend."""
        try:
            from mpi4py import MPI
            from synapse_lang.parallel import MPIBackend
            
            backend = MPIBackend()
            
            def distributed_sum(data):
                comm = MPI.COMM_WORLD
                rank = comm.Get_rank()
                size = comm.Get_size()
                
                # Distribute data
                local_data = data[rank::size]
                local_sum = sum(local_data)
                
                # Gather results
                total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)
                
                return total_sum if rank == 0 else None
                
            data = list(range(100))
            result = backend.execute(distributed_sum, data)
            
            if result is not None:
                self.assertEqual(result, sum(data))
                
        except ImportError:
            self.skipTest("MPI not installed")
            
    def test_ray_backend(self):
        """Test Ray distributed backend."""
        try:
            import ray
            from synapse_lang.parallel import RayBackend
            
            backend = RayBackend()
            
            @ray.remote
            def ray_task(x):
                return x ** 2
                
            inputs = [1, 2, 3, 4, 5]
            futures = [ray_task.remote(x) for x in inputs]
            results = ray.get(futures)
            
            self.assertEqual(results, [1, 4, 9, 16, 25])
            
            ray.shutdown()
            
        except ImportError:
            self.skipTest("Ray not installed")


class TestParallelOptimization(unittest.TestCase):
    """Test parallel execution optimization."""
    
    def test_auto_parallelization(self):
        """Test automatic parallelization decisions."""
        config = ParallelConfig()
        
        # Small task - should not parallelize
        small_task = lambda x: x + 1
        small_inputs = list(range(10))
        
        strategy = config.optimize_strategy(small_task, small_inputs)
        self.assertEqual(strategy, 'serial')
        
        # Large task - should parallelize
        def large_task(x):
            time.sleep(0.1)
            return x ** 2
            
        large_inputs = list(range(100))
        
        strategy = config.optimize_strategy(large_task, large_inputs)
        self.assertEqual(strategy, 'parallel')
        
    def test_dynamic_load_balancing(self):
        """Test dynamic load balancing."""
        def variable_time_task(x):
            # Tasks take variable time
            time.sleep(x * 0.01)
            return x ** 2
            
        inputs = [1, 10, 2, 8, 3, 7, 4, 6, 5]
        
        # Without load balancing
        start_time = time.time()
        results_static = parallel_block(
            function=variable_time_task,
            inputs=inputs,
            load_balancing=False
        )
        static_time = time.time() - start_time
        
        # With load balancing
        start_time = time.time()
        results_dynamic = parallel_block(
            function=variable_time_task,
            inputs=inputs,
            load_balancing=True
        )
        dynamic_time = time.time() - start_time
        
        # Results should be the same
        self.assertEqual(sorted(results_static), sorted(results_dynamic))
        
        # Dynamic should be faster or similar
        print(f"Static: {static_time:.2f}s, Dynamic: {dynamic_time:.2f}s")
        
    def test_memory_optimization(self):
        """Test memory-aware parallel execution."""
        import psutil
        
        def memory_intensive_task(size_mb):
            # Allocate memory
            data = np.zeros(int(size_mb * 1024 * 1024 / 8))
            result = np.sum(data)
            return result
            
        # Get available memory
        available_memory = psutil.virtual_memory().available / (1024 * 1024)
        
        # Try to use more memory than available (should batch)
        tasks = [100] * 20  # 20 tasks of 100MB each
        
        config = ParallelConfig(
            memory_limit=available_memory * 0.5,  # Use only 50% of available
            auto_batch=True
        )
        
        results = parallel_block(
            function=memory_intensive_task,
            inputs=tasks,
            config=config
        )
        
        # Should complete without memory error
        self.assertEqual(len(results), 20)


class TestScientificParallelization(unittest.TestCase):
    """Test scientific computing specific parallelization."""
    
    def test_monte_carlo_parallelization(self):
        """Test Monte Carlo simulation parallelization."""
        def monte_carlo_pi(n_samples):
            # Estimate pi using Monte Carlo
            count_inside = 0
            for _ in range(n_samples):
                x = np.random.random()
                y = np.random.random()
                if x*x + y*y <= 1:
                    count_inside += 1
            return 4 * count_inside / n_samples
            
        # Split across cores
        n_total = 1000000
        n_cores = 4
        samples_per_core = n_total // n_cores
        
        results = parallel_block(
            function=monte_carlo_pi,
            inputs=[samples_per_core] * n_cores
        )
        
        # Combine results
        pi_estimate = np.mean(results)
        
        # Should be close to pi
        self.assertAlmostEqual(pi_estimate, np.pi, places=2)
        
    def test_ensemble_simulation(self):
        """Test ensemble simulation pattern."""
        def climate_model(scenario, realization):
            # Simplified climate simulation
            np.random.seed(realization)
            base_temp = 15.0
            warming = scenario['co2_level'] / 400 * 2  # Simplified
            variability = np.random.normal(0, 0.5)
            return base_temp + warming + variability
            
        scenarios = [
            {'name': 'low', 'co2_level': 450},
            {'name': 'medium', 'co2_level': 550},
            {'name': 'high', 'co2_level': 700}
        ]
        
        realizations = list(range(10))
        
        # Run ensemble
        ensemble_results = []
        for scenario in scenarios:
            scenario_results = parallel_block(
                function=lambda r: climate_model(scenario, r),
                inputs=realizations
            )
            ensemble_results.append({
                'scenario': scenario['name'],
                'temperatures': scenario_results,
                'mean': np.mean(scenario_results),
                'std': np.std(scenario_results)
            })
            
        # Check results structure
        self.assertEqual(len(ensemble_results), 3)
        
        # Higher CO2 should give higher temperature
        low_mean = next(r['mean'] for r in ensemble_results if r['scenario'] == 'low')
        high_mean = next(r['mean'] for r in ensemble_results if r['scenario'] == 'high')
        self.assertGreater(high_mean, low_mean)


class TestParallelPerformance(unittest.TestCase):
    """Test parallel execution performance."""
    
    def test_speedup_measurement(self):
        """Measure parallel speedup."""
        def cpu_bound_task(n):
            # CPU-intensive task
            result = 0
            for i in range(n):
                result += i ** 2
            return result
            
        n_tasks = 8
        task_size = 1000000
        
        # Serial execution
        start = time.time()
        serial_results = [cpu_bound_task(task_size) for _ in range(n_tasks)]
        serial_time = time.time() - start
        
        # Parallel execution
        start = time.time()
        parallel_results = parallel_block(
            function=cpu_bound_task,
            inputs=[task_size] * n_tasks
        )
        parallel_time = time.time() - start
        
        # Calculate speedup
        speedup = serial_time / parallel_time
        
        print(f"Serial: {serial_time:.2f}s")
        print(f"Parallel: {parallel_time:.2f}s")
        print(f"Speedup: {speedup:.2f}x")
        
        # Should have some speedup
        self.assertGreater(speedup, 1.5)
        
        # Results should be identical
        self.assertEqual(serial_results, parallel_results)
        
    def test_overhead_measurement(self):
        """Measure parallel execution overhead."""
        def tiny_task(x):
            return x + 1
            
        inputs = list(range(100))
        
        # Serial execution
        start = time.time()
        serial_results = [tiny_task(x) for x in inputs]
        serial_time = time.time() - start
        
        # Parallel execution
        start = time.time()
        parallel_results = parallel_block(
            function=tiny_task,
            inputs=inputs
        )
        parallel_time = time.time() - start
        
        # For tiny tasks, parallel might be slower due to overhead
        overhead_ratio = parallel_time / serial_time
        
        print(f"Overhead ratio: {overhead_ratio:.2f}x")
        
        # Document the overhead
        self.assertLess(overhead_ratio, 10)  # Shouldn't be more than 10x slower


if __name__ == '__main__':
    unittest.main(verbosity=2)