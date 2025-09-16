#!/usr/bin/env python3
"""
Synapse Language - Performance Benchmarking Suite
Comprehensive benchmarks for interpreter optimization validation
"""

import json
import os
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synapse_cache import clear_all_caches
from synapse_interpreter_enhanced import SynapseInterpreterEnhanced
from synapse_interpreter_optimized import OptimizedSynapseInterpreter


@dataclass
class BenchmarkResult:
    """Result of a single benchmark"""
    name: str
    category: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    cache_stats: dict[str, Any] = None

    def to_dict(self):
        return asdict(self)

class BenchmarkSuite:
    """Comprehensive benchmark suite for Synapse"""

    def __init__(self, iterations: int = 100, warmup: int = 10):
        self.iterations = iterations
        self.warmup = warmup
        self.results: list[BenchmarkResult] = []

    def run_benchmark(self, name: str, category: str, code: str,
                      interpreter: Any) -> BenchmarkResult:
        """Run a single benchmark"""
        print(f"Running benchmark: {name}")

        # Clear caches
        clear_all_caches()

        # Warmup
        for _ in range(self.warmup):
            try:
                interpreter.interpret(code)
            except Exception as e:
                print(f"  Warmup error: {e}")

        # Actual benchmark
        times = []
        for i in range(self.iterations):
            start = time.perf_counter()
            try:
                interpreter.interpret(code)
            except Exception as e:
                print(f"  Iteration {i} error: {e}")
                continue
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        if not times:
            print(f"  No successful iterations for {name}")
            return None

        # Get cache statistics if available
        cache_stats = None
        if hasattr(interpreter, "get_stats"):
            cache_stats = interpreter.get_stats()

        result = BenchmarkResult(
            name=name,
            category=category,
            iterations=len(times),
            total_time=sum(times),
            avg_time=statistics.mean(times),
            min_time=min(times),
            max_time=max(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            cache_stats=cache_stats
        )

        self.results.append(result)
        return result

    def run_all_benchmarks(self):
        """Run all benchmark categories"""
        print("=" * 60)
        print("SYNAPSE LANGUAGE BENCHMARK SUITE")
        print("=" * 60)

        # Create interpreters
        opt_interpreter = OptimizedSynapseInterpreter(enable_jit=True)
        SynapseInterpreterEnhanced()

        # Run benchmarks for each category
        self.benchmark_basic_operations(opt_interpreter)
        self.benchmark_uncertain_values(opt_interpreter)
        self.benchmark_parallel_execution(opt_interpreter)
        self.benchmark_tensor_operations(opt_interpreter)
        self.benchmark_symbolic_math(opt_interpreter)
        self.benchmark_complex_programs(opt_interpreter)

        # Print results
        self.print_results()

        # Save results to file
        self.save_results()

    def benchmark_basic_operations(self, interpreter):
        """Benchmark basic arithmetic and variable operations"""
        print("\n--- Basic Operations ---")

        # Simple arithmetic
        code = """
        x = 10
        y = 20
        z = x + y * 2 - x / 2
        result = z ** 2
        """
        self.run_benchmark("Basic Arithmetic", "basic", code, interpreter)

        # Variable assignments
        code = """
        a = 1
        b = a + 1
        c = b + 1
        d = c + 1
        e = d + 1
        f = e + 1
        g = f + 1
        h = g + 1
        i = h + 1
        j = i + 1
        """
        self.run_benchmark("Variable Chain", "basic", code, interpreter)

        # Function calls
        code = """
        x = sin(0.5)
        y = cos(0.5)
        z = exp(1.0)
        w = log(10.0)
        result = sqrt(x*x + y*y + z*z + w*w)
        """
        self.run_benchmark("Math Functions", "basic", code, interpreter)

    def benchmark_uncertain_values(self, interpreter):
        """Benchmark uncertainty propagation"""
        print("\n--- Uncertainty Propagation ---")

        # Basic uncertainty
        code = """
        uncertain x = 10.0 ± 0.1
        uncertain y = 20.0 ± 0.2
        z = x + y
        w = x * y
        v = x / y
        result = sqrt(z*z + w*w + v*v)
        """
        self.run_benchmark("Uncertain Arithmetic", "uncertainty", code, interpreter)

        # Complex uncertainty propagation
        code = """
        uncertain mass = 10.5 ± 0.1
        uncertain velocity = 25.3 ± 0.3
        uncertain time = 2.0 ± 0.05

        momentum = mass * velocity
        acceleration = velocity / time
        force = mass * acceleration
        energy = 0.5 * mass * velocity * velocity
        """
        self.run_benchmark("Physics with Uncertainty", "uncertainty", code, interpreter)

    def benchmark_parallel_execution(self, interpreter):
        """Benchmark parallel branch execution"""
        print("\n--- Parallel Execution ---")

        # Simple parallel
        code = """
        x = 10
        y = 20

        parallel {
            branch a: x + y
            branch b: x * y
            branch c: x - y
            branch d: x / y
        }
        """
        self.run_benchmark("Simple Parallel", "parallel", code, interpreter)

        # Nested parallel
        code = """
        parallel {
            branch outer1: {
                parallel {
                    branch inner1: 1 + 1
                    branch inner2: 2 + 2
                }
            }
            branch outer2: {
                parallel {
                    branch inner3: 3 + 3
                    branch inner4: 4 + 4
                }
            }
        }
        """
        self.run_benchmark("Nested Parallel", "parallel", code, interpreter)

        # Heavy parallel computation
        code = """
        parallel {
            branch calc1: {
                sum = 0
                for i in range(100) {
                    sum = sum + sin(i) * cos(i)
                }
            }
            branch calc2: {
                prod = 1
                for i in range(50) {
                    prod = prod * (1 + i/100)
                }
            }
            branch calc3: {
                values = []
                for i in range(75) {
                    values = values + [sqrt(i)]
                }
            }
        }
        """
        self.run_benchmark("Heavy Parallel", "parallel", code, interpreter)

    def benchmark_tensor_operations(self, interpreter):
        """Benchmark tensor and matrix operations"""
        print("\n--- Tensor Operations ---")

        # Tensor creation
        code = """
        T1 = zeros(10, 10)
        T2 = ones(10, 10)
        T3 = eye(10)
        T4 = random(10, 10)
        """
        self.run_benchmark("Tensor Creation", "tensor", code, interpreter)

        # Tensor arithmetic
        code = """
        tensor A[3, 3] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        tensor B[3, 3] = [[9, 8, 7], [6, 5, 4], [3, 2, 1]]

        C = A + B
        D = A * B
        E = A - B
        F = A / 2
        """
        self.run_benchmark("Tensor Arithmetic", "tensor", code, interpreter)

        # Large tensor operations
        code = """
        M1 = zeros(100, 100)
        M2 = ones(100, 100)
        M3 = M1 + M2
        M4 = M3 * 2
        M5 = M4 - M2
        """
        self.run_benchmark("Large Tensor Ops", "tensor", code, interpreter)

    def benchmark_symbolic_math(self, interpreter):
        """Benchmark symbolic mathematics"""
        print("\n--- Symbolic Mathematics ---")

        # Basic symbolic
        code = """
        symbolic {
            let f(x) = x^2 + 2*x + 1
            let g(x) = differentiate(f, x)
            solve: g(x) == 0 for x
        }
        """
        self.run_benchmark("Symbolic Differentiation", "symbolic", code, interpreter)

        # Complex symbolic
        code = """
        symbolic {
            let h(x, y) = x^2 + y^2 - 1
            let grad_x = differentiate(h, x)
            let grad_y = differentiate(h, y)
            prove: grad_x^2 + grad_y^2 > 0
        }
        """
        self.run_benchmark("Symbolic Gradient", "symbolic", code, interpreter)

    def benchmark_complex_programs(self, interpreter):
        """Benchmark complete programs"""
        print("\n--- Complex Programs ---")

        # Scientific simulation
        code = """
        experiment SimulateOscillator {
            uncertain frequency = 1.0 ± 0.01
            uncertain amplitude = 10.0 ± 0.1
            uncertain phase = 0.0 ± 0.05

            parallel {
                branch wave1: amplitude * sin(frequency * 1 + phase)
                branch wave2: amplitude * sin(frequency * 2 + phase)
                branch wave3: amplitude * sin(frequency * 3 + phase)
            }

            synthesize: (wave1 + wave2 + wave3) / 3
        }
        """
        self.run_benchmark("Oscillator Simulation", "complex", code, interpreter)

        # Pipeline execution
        code = """
        pipeline DataProcessing {
            stage LoadData {
                data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            }

            stage Transform parallel(4) {
                normalized = data / 10
                squared = data * data
                logged = log(data + 1)
            }

            stage Aggregate {
                mean_val = mean(normalized)
                sum_val = sum(squared)
                max_val = max(logged)
            }
        }
        """
        self.run_benchmark("Data Pipeline", "complex", code, interpreter)

    def print_results(self):
        """Print benchmark results"""
        print("\n" + "=" * 60)
        print("BENCHMARK RESULTS")
        print("=" * 60)

        # Group by category
        categories = {}
        for result in self.results:
            if result is None:
                continue
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)

        for category, results in categories.items():
            print(f"\n{category.upper()} BENCHMARKS:")
            print("-" * 40)

            for result in results:
                print(f"\n{result.name}:")
                print(f"  Iterations: {result.iterations}")
                print(f"  Average:    {result.avg_time*1000:.3f} ms")
                print(f"  Min:        {result.min_time*1000:.3f} ms")
                print(f"  Max:        {result.max_time*1000:.3f} ms")
                print(f"  Std Dev:    {result.std_dev*1000:.3f} ms")

                if result.cache_stats:
                    cache = result.cache_stats.get("cache_stats", {})
                    if cache:
                        ast_cache = cache.get("ast_cache", {})
                        if ast_cache and ast_cache.get("hits", 0) + ast_cache.get("misses", 0) > 0:
                            print(f"  Cache Hit Rate: {ast_cache.get('hit_rate', 0)*100:.1f}%")

        # Overall statistics
        print("\n" + "=" * 60)
        print("OVERALL STATISTICS")
        print("=" * 60)

        all_times = [r.avg_time for r in self.results if r is not None]
        if all_times:
            print(f"Total benchmarks:     {len(all_times)}")
            print(f"Average time:         {statistics.mean(all_times)*1000:.3f} ms")
            print(f"Fastest benchmark:    {min(all_times)*1000:.3f} ms")
            print(f"Slowest benchmark:    {max(all_times)*1000:.3f} ms")

    def save_results(self, filename: str = "benchmark_results.json"):
        """Save results to JSON file"""
        timestamp = datetime.now().isoformat()
        data = {
            "timestamp": timestamp,
            "iterations": self.iterations,
            "warmup": self.warmup,
            "results": [r.to_dict() for r in self.results if r is not None]
        }

        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\nResults saved to: {filepath}")

def compare_interpreters():
    """Compare optimized vs enhanced interpreter performance"""
    print("=" * 60)
    print("INTERPRETER COMPARISON")
    print("=" * 60)

    # Test code
    test_code = """
    uncertain x = 10.0 ± 0.1
    uncertain y = 20.0 ± 0.2

    parallel {
        branch calc1: x * y + x
        branch calc2: y * x - y
        branch calc3: (x + y) * 2
    }

    tensor T[3, 3] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    result = T * 2 + T
    """

    # Create interpreters
    opt_interpreter = OptimizedSynapseInterpreter(enable_jit=True)
    enhanced_interpreter = SynapseInterpreterEnhanced()

    # Benchmark each
    iterations = 100

    # Optimized version
    opt_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        try:
            opt_interpreter.interpret(test_code)
        except:
            pass
        opt_times.append(time.perf_counter() - start)

    # Enhanced version
    enh_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        try:
            enhanced_interpreter.interpret(test_code)
        except:
            pass
        enh_times.append(time.perf_counter() - start)

    # Results
    opt_avg = statistics.mean(opt_times) * 1000
    enh_avg = statistics.mean(enh_times) * 1000
    speedup = enh_avg / opt_avg if opt_avg > 0 else 0

    print(f"\nOptimized Interpreter: {opt_avg:.3f} ms average")
    print(f"Enhanced Interpreter:  {enh_avg:.3f} ms average")
    print(f"Speedup:              {speedup:.2f}x")

    # Cache effectiveness
    stats = opt_interpreter.get_stats()
    cache_stats = stats.get("cache_stats", {})
    ast_cache = cache_stats.get("ast_cache", {})
    if ast_cache:
        print("\nCache Statistics:")
        print(f"  AST Cache Hits:    {ast_cache.get('hits', 0)}")
        print(f"  AST Cache Misses:  {ast_cache.get('misses', 0)}")
        print(f"  Hit Rate:          {ast_cache.get('hit_rate', 0)*100:.1f}%")

if __name__ == "__main__":
    # Run full benchmark suite
    suite = BenchmarkSuite(iterations=50, warmup=5)
    suite.run_all_benchmarks()

    # Compare interpreters
    print("\n")
    compare_interpreters()
