#!/usr/bin/env python
"""
Simple Synapse Language Demo
Shows basic functionality without complex parsing
"""

import numpy as np

from synapse_lang import TensorEngine, UncertaintyEngine


def demo_uncertainty():
    """Demonstrate uncertainty quantification"""
    print("Uncertainty Quantification Demo")
    print("=" * 40)

    # Create uncertainty engine
    engine = UncertaintyEngine()

    # Create uncertain values
    measurement1 = engine.create_uncertain(42.3, 0.5)
    measurement2 = engine.create_uncertain(15.7, 0.3)

    print(f"Measurement 1: {measurement1.nominal:.2f} +/- {measurement1.uncertainty:.2f}")
    print(f"Measurement 2: {measurement2.nominal:.2f} +/- {measurement2.uncertainty:.2f}")

    # Propagate uncertainties through calculations
    sum_result = measurement1.nominal + measurement2.nominal
    sum_uncertainty = np.sqrt(measurement1.uncertainty**2 + measurement2.uncertainty**2)

    print(f"\nSum: {sum_result:.2f} +/- {sum_uncertainty:.2f}")

    # Monte Carlo simulation
    samples1 = np.random.normal(measurement1.nominal, measurement1.uncertainty, 1000)
    samples2 = np.random.normal(measurement2.nominal, measurement2.uncertainty, 1000)
    sum_samples = samples1 + samples2

    print(f"Monte Carlo mean: {sum_samples.mean():.2f}")
    print(f"Monte Carlo std: {sum_samples.std():.2f}")
    print(f"95% CI: [{np.percentile(sum_samples, 2.5):.2f}, {np.percentile(sum_samples, 97.5):.2f}]")

def demo_tensors():
    """Demonstrate tensor operations"""
    print("\n\nTensor Operations Demo")
    print("=" * 40)

    # Create tensor engine
    engine = TensorEngine()

    # Create tensors
    tensor1 = engine.tensor([[1, 2], [3, 4]])
    tensor2 = engine.tensor([[5, 6], [7, 8]])

    print("Tensor 1:")
    print(tensor1.data)
    print("\nTensor 2:")
    print(tensor2.data)

    # Operations
    result = engine.matmul(tensor1, tensor2)
    print("\nMatrix multiplication result:")
    print(result.data)

    # Element-wise operations
    sum_result = engine.add(tensor1, tensor2)
    print("\nElement-wise addition:")
    print(sum_result.data)

def demo_parallel_simulation():
    """Demonstrate parallel simulation concept"""
    print("\n\nParallel Simulation Demo")
    print("=" * 40)

    # Simulate parallel branches
    branches = {
        "scenario_A": lambda: np.random.normal(100, 10),
        "scenario_B": lambda: np.random.normal(150, 15),
        "scenario_C": lambda: np.random.normal(80, 8)
    }

    print("Running parallel scenarios...")
    results = {}
    for name, func in branches.items():
        result = func()
        results[name] = result
        print(f"  {name}: {result:.2f}")

    # Merge results
    weighted_avg = sum(results.values()) / len(results)
    print(f"\nMerged result (average): {weighted_avg:.2f}")

    # Determine best scenario
    best = min(results.items(), key=lambda x: x[1])
    print(f"Best scenario: {best[0]} with value {best[1]:.2f}")

def main():
    """Run all demos"""
    print("\n*** SYNAPSE LANGUAGE DEMO ***\n")

    demo_uncertainty()
    demo_tensors()
    demo_parallel_simulation()

    print("\n" + "="*40)
    print("Installation: pip install synapse-lang")
    print("Website: https://synapse-lang.com")
    print("GitHub: https://github.com/MichaelCrowe11/synapse-lang")

if __name__ == "__main__":
    main()
