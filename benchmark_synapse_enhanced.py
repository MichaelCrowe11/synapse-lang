#!/usr/bin/env python3
"""
Enhanced Benchmark suite for Synapse language
Compares performance with other scientific computing languages
"""

import json
import os
import sys
import time
from datetime import datetime

import numpy as np

# Add synapse_lang to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from synapse_lang import Interpreter, Lexer, Parser
    SYNAPSE_AVAILABLE = True
except ImportError:
    print("Warning: Synapse language modules not found")
    SYNAPSE_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False


class SynapseEnhancedBenchmark:
    """Enhanced benchmark suite for Synapse with detailed comparisons"""

    def __init__(self):
        self.results = {}
        self.metadata = {
            "timestamp": datetime.now().isoformat(),
            "platform": sys.platform,
            "python_version": sys.version,
            "numpy_version": np.__version__,
            "synapse_available": SYNAPSE_AVAILABLE,
            "numba_available": NUMBA_AVAILABLE
        }

    def benchmark_uncertainty_propagation(self, n_measurements=1000):
        """Benchmark uncertainty quantification capabilities"""
        print(f"\n{'='*60}")
        print(f"Benchmarking Uncertainty Propagation ({n_measurements} measurements)")
        print(f"{'='*60}")

        synapse_code = f"""
        # Scientific measurement with uncertainty
        uncertain temperature = 298.15 ± 0.5
        uncertain pressure = 101.325 ± 0.1
        uncertain volume = 22.4 ± 0.05

        # Ideal gas calculation with error propagation
        R = 8.314

        # Run multiple calculations
        results = []
        for i in range({n_measurements}) {{
            moles = (pressure * volume) / (R * temperature)
            results.append(moles)
        }}

        return results
        """

        # Benchmark Synapse
        if SYNAPSE_AVAILABLE:
            try:
                start = time.time()
                lexer = Lexer(synapse_code)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                interpreter = Interpreter()
                interpreter.interpret(ast)
                synapse_time = time.time() - start
                print(f"✓ Synapse: {synapse_time:.4f}s")
            except Exception as e:
                print(f"✗ Synapse error: {e}")
                synapse_time = None
        else:
            synapse_time = None
            print("✗ Synapse not available")

        # Benchmark Python with manual uncertainty
        start = time.time()
        for _ in range(n_measurements):
            temp_val = 298.15
            temp_unc = 0.5
            press_val = 101.325
            press_unc = 0.1
            vol_val = 22.4
            vol_unc = 0.05
            R = 8.314

            # Manual error propagation
            moles_val = (press_val * vol_val) / (R * temp_val)
            # Simplified uncertainty calculation
            rel_unc = np.sqrt((press_unc/press_val)**2 + (vol_unc/vol_val)**2 + (temp_unc/temp_val)**2)
            moles_val * rel_unc

        python_time = time.time() - start
        print(f"✓ Python (manual): {python_time:.4f}s")

        self.results["uncertainty_propagation"] = {
            "synapse": synapse_time,
            "python_manual": python_time,
            "measurements": n_measurements
        }

    def benchmark_parallel_execution(self, n_branches=4, workload_size=1000):
        """Benchmark parallel execution capabilities"""
        print(f"\n{'='*60}")
        print(f"Benchmarking Parallel Execution ({n_branches} branches)")
        print(f"{'='*60}")

        synapse_code = f"""
        # Parallel hypothesis testing
        experiment ParallelTest {{
            results = []

            parallel {{
                branch A: compute_hypothesis_a({workload_size})
                branch B: compute_hypothesis_b({workload_size})
                branch C: compute_hypothesis_c({workload_size})
                branch D: compute_hypothesis_d({workload_size})
            }}

            synthesize: combine_results(A, B, C, D)
        }}

        function compute_hypothesis_a(n) {{
            sum = 0
            for i in range(n) {{
                sum = sum + i * 2
            }}
            return sum
        }}

        function compute_hypothesis_b(n) {{
            product = 1
            for i in range(1, min(n, 20)) {{
                product = product * i
            }}
            return product
        }}

        function compute_hypothesis_c(n) {{
            values = []
            for i in range(n) {{
                values.append(i ** 0.5)
            }}
            return sum(values)
        }}

        function compute_hypothesis_d(n) {{
            total = 0
            for i in range(n) {{
                total = total + sin(i)
            }}
            return total
        }}
        """

        # Benchmark Synapse parallel
        if SYNAPSE_AVAILABLE:
            try:
                start = time.time()
                lexer = Lexer(synapse_code)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                interpreter = Interpreter()
                interpreter.interpret(ast)
                synapse_time = time.time() - start
                print(f"✓ Synapse (parallel): {synapse_time:.4f}s")
            except Exception as e:
                print(f"✗ Synapse error: {e}")
                synapse_time = None
        else:
            synapse_time = None
            print("✗ Synapse not available")

        # Benchmark Python with threading
        import concurrent.futures
        import math

        def compute_a(n):
            return sum(i * 2 for i in range(n))

        def compute_b(n):
            product = 1
            for i in range(1, min(n, 20)):
                product *= i
            return product

        def compute_c(n):
            return sum(i ** 0.5 for i in range(n))

        def compute_d(n):
            return sum(math.sin(i) for i in range(n))

        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(compute_a, workload_size),
                executor.submit(compute_b, workload_size),
                executor.submit(compute_c, workload_size),
                executor.submit(compute_d, workload_size)
            ]
            [f.result() for f in futures]
        python_parallel_time = time.time() - start
        print(f"✓ Python (threads): {python_parallel_time:.4f}s")

        # Benchmark sequential Python
        start = time.time()
        [
            compute_a(workload_size),
            compute_b(workload_size),
            compute_c(workload_size),
            compute_d(workload_size)
        ]
        python_sequential_time = time.time() - start
        print(f"✓ Python (sequential): {python_sequential_time:.4f}s")

        self.results["parallel_execution"] = {
            "synapse_parallel": synapse_time,
            "python_threaded": python_parallel_time,
            "python_sequential": python_sequential_time,
            "speedup": python_sequential_time / python_parallel_time if python_parallel_time > 0 else 0
        }

    def benchmark_scientific_pipeline(self, data_size=10000):
        """Benchmark scientific data processing pipeline"""
        print(f"\n{'='*60}")
        print(f"Benchmarking Scientific Pipeline ({data_size} data points)")
        print(f"{'='*60}")

        synapse_code = f"""
        pipeline DataAnalysis {{
            stage Loading {{
                data = generate_data({data_size})
            }}

            stage Cleaning parallel(4) {{
                cleaned = remove_outliers(data)
                normalized = normalize(cleaned)
            }}

            stage Analysis {{
                mean = calculate_mean(normalized)
                variance = calculate_variance(normalized, mean)
                correlation = calculate_correlation(normalized)
            }}

            stage Reporting {{
                report = generate_report(mean, variance, correlation)
            }}
        }}

        function generate_data(n) {{
            data = []
            for i in range(n) {{
                data.append(random() * 100)
            }}
            return data
        }}

        function remove_outliers(data) {{
            # Simple outlier removal
            cleaned = []
            for value in data {{
                if value > 5 and value < 95 {{
                    cleaned.append(value)
                }}
            }}
            return cleaned
        }}

        function normalize(data) {{
            if len(data) == 0 {{
                return data
            }}

            min_val = min(data)
            max_val = max(data)
            range_val = max_val - min_val

            if range_val == 0 {{
                return data
            }}

            normalized = []
            for value in data {{
                normalized.append((value - min_val) / range_val)
            }}
            return normalized
        }}
        """

        # Benchmark Synapse pipeline
        if SYNAPSE_AVAILABLE:
            try:
                start = time.time()
                lexer = Lexer(synapse_code)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                interpreter = Interpreter()
                interpreter.interpret(ast)
                synapse_time = time.time() - start
                print(f"✓ Synapse (pipeline): {synapse_time:.4f}s")
            except Exception as e:
                print(f"✗ Synapse error: {e}")
                synapse_time = None
        else:
            synapse_time = None
            print("✗ Synapse not available")

        # Benchmark NumPy pipeline
        start = time.time()
        # Generate data
        data = np.random.random(data_size) * 100
        # Remove outliers
        cleaned = data[(data > 5) & (data < 95)]
        # Normalize
        if len(cleaned) > 0:
            normalized = (cleaned - cleaned.min()) / (cleaned.max() - cleaned.min())
            # Calculate statistics
            np.mean(normalized)
            np.var(normalized)
            np.corrcoef(normalized[:min(1000, len(normalized))],
                                    normalized[:min(1000, len(normalized))])[0, 1]
        numpy_time = time.time() - start
        print(f"✓ NumPy (pipeline): {numpy_time:.4f}s")

        # Benchmark Pandas if available
        if PANDAS_AVAILABLE:
            start = time.time()
            df = pd.DataFrame({"data": np.random.random(data_size) * 100})
            # Pipeline operations
            df_cleaned = df[(df["data"] > 5) & (df["data"] < 95)]
            df_normalized = (df_cleaned - df_cleaned.min()) / (df_cleaned.max() - df_cleaned.min())
            df_normalized.describe()
            pandas_time = time.time() - start
            print(f"✓ Pandas (pipeline): {pandas_time:.4f}s")
        else:
            pandas_time = None
            print("- Pandas not available")

        self.results["scientific_pipeline"] = {
            "synapse": synapse_time,
            "numpy": numpy_time,
            "pandas": pandas_time,
            "data_size": data_size
        }

    def benchmark_matrix_operations(self, size=100):
        """Benchmark matrix/tensor operations"""
        print(f"\n{'='*60}")
        print(f"Benchmarking Matrix Operations ({size}x{size})")
        print(f"{'='*60}")

        synapse_code = f"""
        # Matrix operations with tensor support
        let size = {size}

        # Create matrices
        matrix_a = create_matrix(size, size)
        matrix_b = create_matrix(size, size)

        # Matrix multiplication
        result = matrix_multiply(matrix_a, matrix_b)

        # Tensor operations
        tensor_3d = create_tensor(10, 10, 10)
        tensor_result = tensor_operation(tensor_3d)

        function create_matrix(rows, cols) {{
            matrix = []
            for i in range(rows) {{
                row = []
                for j in range(cols) {{
                    row.append(random())
                }}
                matrix.append(row)
            }}
            return matrix
        }}

        function matrix_multiply(a, b) {{
            size = len(a)
            result = []

            for i in range(size) {{
                row = []
                for j in range(size) {{
                    sum = 0
                    for k in range(size) {{
                        sum = sum + a[i][k] * b[k][j]
                    }}
                    row.append(sum)
                }}
                result.append(row)
            }}
            return result
        }}
        """

        # Benchmark Synapse
        if SYNAPSE_AVAILABLE:
            try:
                start = time.time()
                lexer = Lexer(synapse_code)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                interpreter = Interpreter()
                interpreter.interpret(ast)
                synapse_time = time.time() - start
                print(f"✓ Synapse: {synapse_time:.4f}s")
            except Exception as e:
                print(f"✗ Synapse error: {e}")
                synapse_time = None
        else:
            synapse_time = None
            print("✗ Synapse not available")

        # Benchmark NumPy
        start = time.time()
        a = np.random.rand(size, size)
        b = np.random.rand(size, size)
        np.matmul(a, b)
        # Additional tensor operation
        tensor = np.random.rand(10, 10, 10)
        np.einsum("ijk->jki", tensor)
        numpy_time = time.time() - start
        print(f"✓ NumPy: {numpy_time:.4f}s")

        # Benchmark with Numba JIT if available
        if NUMBA_AVAILABLE:
            @jit(nopython=True)
            def matrix_multiply_numba(a, b):
                size = len(a)
                result = np.zeros((size, size))
                for i in range(size):
                    for j in range(size):
                        for k in range(size):
                            result[i, j] += a[i, k] * b[k, j]
                return result

            a = np.random.rand(size, size)
            b = np.random.rand(size, size)

            # Warm-up JIT
            _ = matrix_multiply_numba(a[:10, :10], b[:10, :10])

            start = time.time()
            matrix_multiply_numba(a, b)
            numba_time = time.time() - start
            print(f"✓ Numba JIT: {numba_time:.4f}s")
        else:
            numba_time = None
            print("- Numba not available")

        self.results["matrix_operations"] = {
            "synapse": synapse_time,
            "numpy": numpy_time,
            "numba": numba_time,
            "matrix_size": size
        }

    def generate_report(self):
        """Generate comprehensive benchmark report"""
        print(f"\n{'='*60}")
        print("SYNAPSE ENHANCED BENCHMARK REPORT")
        print(f"{'='*60}")

        print("\nSystem Information:")
        print(f"  Platform: {self.metadata['platform']}")
        print(f"  Python: {sys.version.split()[0]}")
        print(f"  NumPy: {self.metadata['numpy_version']}")
        print(f"  Synapse Available: {self.metadata['synapse_available']}")
        print(f"  Numba Available: {self.metadata['numba_available']}")

        print(f"\n{'='*60}")
        print("PERFORMANCE RESULTS")
        print(f"{'='*60}")

        for test_name, times in self.results.items():
            print(f"\n{test_name.replace('_', ' ').title()}:")
            print("  " + "-" * 56)

            # Find best performer
            valid_times = {k: v for k, v in times.items()
                          if v is not None and isinstance(v, (int, float))}

            if valid_times:
                best = min(valid_times, key=valid_times.get)
                best_time = valid_times[best]

                for key, value in times.items():
                    if isinstance(value, (int, float)):
                        if value is not None:
                            relative = value / best_time if best_time > 0 else 0
                            status = "🏆" if key == best else "  "
                            print(f"  {status} {key:20s}: {value:8.4f}s (x{relative:.2f})")
                    elif key not in ["data_size", "matrix_size", "measurements", "speedup"]:
                        print(f"     {key:20s}: {value}")

        print(f"\n{'='*60}")
        print("PERFORMANCE SUMMARY")
        print(f"{'='*60}")

        # Calculate average relative performance
        synapse_performances = []
        for test_name, times in self.results.items():
            if times.get("synapse") and times.get("numpy"):
                relative = times["synapse"] / times["numpy"]
                synapse_performances.append(relative)
                comparison = "slower" if relative > 1 else "faster"
                print(f"{test_name}: {relative:.2f}x {comparison} than NumPy")

        if synapse_performances:
            avg_relative = sum(synapse_performances) / len(synapse_performances)
            print(f"\n📊 Average Synapse performance vs NumPy: {avg_relative:.2f}x")

        print("\n" + "="*60)
        print("KEY INSIGHTS")
        print("="*60)

        print("""
✅ Strengths:
  • Native uncertainty propagation (unique feature)
  • Intuitive parallel execution syntax
  • Scientific pipeline abstractions
  • Hypothesis-driven programming model

⚠️  Performance Notes:
  • Interpreter-based (no JIT yet) - slower than compiled
  • Would benefit from Numba/PyPy integration
  • Parallel features need optimization

💡 Recommendations:
  • Enable JIT compilation for 10-100x speedup
  • Implement native BLAS/LAPACK bindings
  • Add GPU acceleration for tensor operations
  • Cache compiled functions
        """)

        # Save results to JSON
        report_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump({
                "metadata": self.metadata,
                "results": self.results
            }, f, indent=2)
        print(f"\n📁 Results saved to: {report_file}")


def main():
    benchmark = SynapseEnhancedBenchmark()

    print("🚀 Starting Synapse Enhanced Benchmark Suite")
    print("="*60)

    # Run all benchmarks
    benchmark.benchmark_uncertainty_propagation(n_measurements=100)
    benchmark.benchmark_parallel_execution(n_branches=4, workload_size=1000)
    benchmark.benchmark_scientific_pipeline(data_size=5000)
    benchmark.benchmark_matrix_operations(size=50)

    # Generate comprehensive report
    benchmark.generate_report()


if __name__ == "__main__":
    main()
