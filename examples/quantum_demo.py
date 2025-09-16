#!/usr/bin/env python3
"""
Synapse Language - Quantum Computing Demo
Demonstrates quantum-inspired features using the Synapse language Python implementation
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

import numpy as np

from synapse_lang import UncertainValue, monte_carlo, parallel_block, parameter_sweep
from synapse_lang.parallel import synthesize, thought_streams


def demo_uncertainty_propagation():
    """Demonstrate uncertainty-aware computation."""
    print("\n" + "="*60)
    print("DEMO 1: Uncertainty-Aware Computation")
    print("="*60)

    # Create measurements with uncertainty
    temperature = UncertainValue(273.15, 0.5)  # Kelvin
    pressure = UncertainValue(101.325, 0.1)    # kPa
    volume = UncertainValue(22.414, 0.01)      # Liters

    print(f"Temperature: {temperature.value:.2f} +/- {temperature.uncertainty:.2f} K")
    print(f"Pressure: {pressure.value:.3f} +/- {pressure.uncertainty:.3f} kPa")
    print(f"Volume: {volume.value:.3f} +/- {volume.uncertainty:.3f} L")

    # Ideal gas calculation with automatic uncertainty propagation
    R = 8.314  # Gas constant
    n_moles = (pressure * volume) / (R * temperature)

    print(f"\nCalculated moles of gas: {n_moles.value:.4f} +/- {n_moles.uncertainty:.4f} mol")
    print(f"Relative uncertainty: {(n_moles.uncertainty/n_moles.value)*100:.2f}%")


def demo_monte_carlo():
    """Demonstrate Monte Carlo simulation with uncertainty."""
    print("\n" + "="*60)
    print("DEMO 2: Monte Carlo Simulation")
    print("="*60)

    def reaction_rate(T, Ea):
        """Arrhenius equation for reaction rate."""
        A = 1e10  # Pre-exponential factor
        R = 8.314  # Gas constant
        return A * np.exp(-Ea / (R * T))

    # Parameters with uncertainty
    params = {
        "T": {"mean": 300, "std": 5},      # Temperature in K
        "Ea": {"mean": 50000, "std": 1000}  # Activation energy in J/mol
    }

    print("Running Monte Carlo simulation...")
    print(f"Temperature: {params['T']['mean']} +/- {params['T']['std']} K")
    print(f"Activation Energy: {params['Ea']['mean']} +/- {params['Ea']['std']} J/mol")

    # Run simulation
    results = monte_carlo(
        lambda p: reaction_rate(p["T"], p["Ea"]),
        params,
        n_samples=10000
    )

    rates = results["results"]
    print("\nReaction Rate Statistics:")
    print(f"  Mean: {np.mean(rates):.2e} s^-1")
    print(f"  Std Dev: {np.std(rates):.2e} s^-1")
    print(f"  Median: {np.median(rates):.2e} s^-1")

    # Calculate confidence interval
    ci_lower = np.percentile(rates, 2.5)
    ci_upper = np.percentile(rates, 97.5)
    print(f"  95% CI: [{ci_lower:.2e}, {ci_upper:.2e}] s^-1")


def demo_parallel_computation():
    """Demonstrate parallel computation capabilities."""
    print("\n" + "="*60)
    print("DEMO 3: Parallel Computation")
    print("="*60)

    # Define computational tasks
    def compute_factorial(n):
        """Compute factorial of n."""
        import math
        return math.factorial(n)

    def compute_fibonacci(n):
        """Compute nth Fibonacci number."""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def compute_prime(n):
        """Check if n is prime."""
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    # Run tasks in parallel
    print("Running parallel computations...")

    tasks = {
        "factorial_10": lambda: compute_factorial(10),
        "fibonacci_20": lambda: compute_fibonacci(20),
        "is_prime_97": lambda: compute_prime(97),
        "is_prime_100": lambda: compute_prime(100)
    }

    results = parallel_block(tasks)

    print("Results:")
    for name, result in results.items():
        print(f"  {name}: {result}")


def demo_parameter_sweep():
    """Demonstrate parameter sweep for optimization."""
    print("\n" + "="*60)
    print("DEMO 4: Parameter Sweep Optimization")
    print("="*60)

    def experiment(pH, temp, conc):
        """Model experimental yield based on parameters."""
        optimal_pH = 7.0
        optimal_temp = 298

        pH_factor = np.exp(-0.5 * ((pH - optimal_pH) / 0.5)**2)
        temp_factor = np.exp(-0.01 * abs(temp - optimal_temp))
        conc_factor = conc / (conc + 0.1)

        return pH_factor * temp_factor * conc_factor

    print("Performing parameter sweep...")

    # Define parameter ranges
    param_ranges = {
        "pH": np.linspace(5.0, 9.0, 10),
        "temp": np.linspace(280, 320, 10),
        "conc": np.logspace(-2, 0, 5)  # 0.01 to 1.0
    }

    # Perform sweep
    results = parameter_sweep(experiment, param_ranges, parallel=True)

    # Find optimal conditions
    best_params = max(results.items(), key=lambda x: x[1])
    optimal_conditions, optimal_yield = best_params

    print("\nOptimal Conditions Found:")
    print(f"  pH: {optimal_conditions[0]:.2f}")
    print(f"  Temperature: {optimal_conditions[1]:.1f} K")
    print(f"  Concentration: {optimal_conditions[2]:.3f} M")
    print(f"  Expected Yield: {optimal_yield:.3f} ({optimal_yield*100:.1f}%)")


async def demo_thought_streams():
    """Demonstrate parallel thought streams for hypothesis testing."""
    print("\n" + "="*60)
    print("DEMO 5: Parallel Thought Streams")
    print("="*60)

    # Define hypothesis functions
    async def hypothesis_water(temp):
        """Test if water is liquid at given temperature."""
        await asyncio.sleep(0.1)  # Simulate computation
        return temp > 273.15

    async def hypothesis_ice(temp):
        """Test if water is solid at given temperature."""
        await asyncio.sleep(0.1)  # Simulate computation
        return temp <= 273.15

    async def hypothesis_steam(temp):
        """Test if water is gas at given temperature."""
        await asyncio.sleep(0.1)  # Simulate computation
        return temp > 373.15

    print("Testing water phase hypotheses in parallel...")

    test_temp = 280  # K
    print(f"Test temperature: {test_temp} K")

    hypotheses = {
        "is_liquid": lambda: hypothesis_water(test_temp),
        "is_solid": lambda: hypothesis_ice(test_temp),
        "is_gas": lambda: hypothesis_steam(test_temp)
    }

    results = await thought_streams(hypotheses)

    print("Hypothesis Results:")
    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status} ({result})")

    # Synthesize consensus
    consensus = synthesize(list(results.values()), strategy="vote")
    print(f"\nConsensus state: {'Liquid' if consensus else 'Not determined'}")


def demo_quantum_inspired():
    """Demonstrate quantum-inspired superposition and measurement."""
    print("\n" + "="*60)
    print("DEMO 6: Quantum-Inspired Computing")
    print("="*60)

    class QuantumBit:
        """Simple quantum bit simulation."""
        def __init__(self, alpha=1/np.sqrt(2), beta=1/np.sqrt(2)):
            # Normalize coefficients
            norm = np.sqrt(abs(alpha)**2 + abs(beta)**2)
            self.alpha = alpha / norm
            self.beta = beta / norm

        def measure(self):
            """Measure the qubit, collapsing to |0⟩ or |1⟩."""
            prob_zero = abs(self.alpha)**2
            return 0 if np.random.random() < prob_zero else 1

        def __str__(self):
            return f"{self.alpha:.3f}|0> + {self.beta:.3f}|1>"

    print("Creating quantum superposition state...")
    qubit = QuantumBit()
    print(f"Initial state: {qubit}")

    print("\nPerforming 1000 measurements...")
    measurements = [qubit.measure() for _ in range(1000)]

    zeros = measurements.count(0)
    ones = measurements.count(1)

    print("Results:")
    print(f"  |0>: {zeros} ({zeros/10:.1f}%)")
    print(f"  |1>: {ones} ({ones/10:.1f}%)")
    print(f"  Ratio: {zeros/ones:.3f}")

    # Quantum interference simulation
    print("\nQuantum Interference Pattern:")
    phases = np.linspace(0, 2*np.pi, 20)
    amplitudes = []

    for phase in phases:
        # Create superposition with phase
        q = QuantumBit(1/np.sqrt(2), np.exp(1j*phase)/np.sqrt(2))
        # Measure probability
        probs = [q.measure() for _ in range(100)]
        amplitudes.append(sum(probs)/100)

    # Display interference pattern
    for i, amp in enumerate(amplitudes):
        bar = "#" * int(amp * 50)
        print(f"  phi={phases[i]:.2f}: {bar} {amp:.2f}")


def main():
    """Run all demonstrations."""
    print("\n" + "="*80)
    print(" "*20 + "SYNAPSE LANGUAGE - QUANTUM COMPUTING DEMO")
    print("="*80)

    # Run demonstrations
    demo_uncertainty_propagation()
    demo_monte_carlo()
    demo_parallel_computation()
    demo_parameter_sweep()

    # Run async demonstration
    asyncio.run(demo_thought_streams())

    demo_quantum_inspired()

    print("\n" + "="*80)
    print("[SUCCESS] All demonstrations completed successfully!")
    print("="*80)


if __name__ == "__main__":
    main()
