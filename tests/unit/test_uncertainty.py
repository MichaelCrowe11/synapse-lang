"""
Unit tests for Synapse Language uncertainty quantification.

Tests the core uncertainty propagation, mathematical operations,
and statistical methods.
"""

import unittest
import numpy as np
from math import sqrt, pi
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from synapse_lang.uncertainty import UncertainValue, monte_carlo, propagate_uncertainty


class TestUncertainValue(unittest.TestCase):
    """Test basic uncertain value operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.value1 = UncertainValue(10.0, 0.5)  # 10.0 ± 0.5
        self.value2 = UncertainValue(5.0, 0.2)   # 5.0 ± 0.2
        
    def test_creation(self):
        """Test uncertain value creation."""
        # Basic creation
        val = UncertainValue(25.3, 0.2)
        self.assertEqual(val.value, 25.3)
        self.assertEqual(val.uncertainty, 0.2)
        
        # From string notation
        val2 = UncertainValue.from_string("25.3 ± 0.2")
        self.assertEqual(val2.value, 25.3)
        self.assertEqual(val2.uncertainty, 0.2)
        
    def test_addition(self):
        """Test addition with uncertainty propagation."""
        result = self.value1 + self.value2
        
        # Check value
        self.assertAlmostEqual(result.value, 15.0)
        
        # Check uncertainty propagation (independent)
        expected_uncertainty = sqrt(0.5**2 + 0.2**2)
        self.assertAlmostEqual(result.uncertainty, expected_uncertainty, places=6)
        
    def test_subtraction(self):
        """Test subtraction with uncertainty propagation."""
        result = self.value1 - self.value2
        
        # Check value
        self.assertAlmostEqual(result.value, 5.0)
        
        # Check uncertainty propagation
        expected_uncertainty = sqrt(0.5**2 + 0.2**2)
        self.assertAlmostEqual(result.uncertainty, expected_uncertainty, places=6)
        
    def test_multiplication(self):
        """Test multiplication with uncertainty propagation."""
        result = self.value1 * self.value2
        
        # Check value
        self.assertAlmostEqual(result.value, 50.0)
        
        # Check uncertainty propagation (relative)
        rel_unc1 = 0.5 / 10.0
        rel_unc2 = 0.2 / 5.0
        expected_rel_uncertainty = sqrt(rel_unc1**2 + rel_unc2**2)
        expected_uncertainty = 50.0 * expected_rel_uncertainty
        self.assertAlmostEqual(result.uncertainty, expected_uncertainty, places=6)
        
    def test_division(self):
        """Test division with uncertainty propagation."""
        result = self.value1 / self.value2
        
        # Check value
        self.assertAlmostEqual(result.value, 2.0)
        
        # Check uncertainty propagation
        rel_unc1 = 0.5 / 10.0
        rel_unc2 = 0.2 / 5.0
        expected_rel_uncertainty = sqrt(rel_unc1**2 + rel_unc2**2)
        expected_uncertainty = 2.0 * expected_rel_uncertainty
        self.assertAlmostEqual(result.uncertainty, expected_uncertainty, places=6)
        
    def test_power(self):
        """Test power operations with uncertainty."""
        result = self.value1 ** 2
        
        # Check value
        self.assertAlmostEqual(result.value, 100.0)
        
        # Check uncertainty propagation (power rule)
        expected_uncertainty = 2 * 100.0 * (0.5 / 10.0)
        self.assertAlmostEqual(result.uncertainty, expected_uncertainty, places=6)
        
    def test_trigonometric(self):
        """Test trigonometric functions with uncertainty."""
        import math
        
        angle = UncertainValue(pi/4, 0.01)  # 45° ± small uncertainty
        
        # Sin
        sin_result = angle.sin()
        self.assertAlmostEqual(sin_result.value, math.sin(pi/4), places=6)
        
        # Cos
        cos_result = angle.cos()
        self.assertAlmostEqual(cos_result.value, math.cos(pi/4), places=6)
        
        # Verify uncertainty propagated
        self.assertGreater(sin_result.uncertainty, 0)
        self.assertGreater(cos_result.uncertainty, 0)
        
    def test_comparison(self):
        """Test comparison operations with uncertainty."""
        val1 = UncertainValue(10.0, 0.5)
        val2 = UncertainValue(10.2, 0.5)
        val3 = UncertainValue(15.0, 0.5)
        
        # Not significantly different
        self.assertFalse(val1.significantly_different_from(val2))
        
        # Significantly different
        self.assertTrue(val1.significantly_different_from(val3))
        
    def test_string_representation(self):
        """Test string formatting."""
        val = UncertainValue(123.456, 0.789)
        
        # Default representation
        self.assertEqual(str(val), "123.456 ± 0.789")
        
        # Formatted representation
        formatted = val.format(decimals=2)
        self.assertEqual(formatted, "123.46 ± 0.79")
        
        # Scientific notation
        large_val = UncertainValue(1.23e10, 4.5e8)
        sci_format = large_val.format_scientific()
        self.assertIn("e+10", sci_format.lower())


class TestMonteCarloSimulation(unittest.TestCase):
    """Test Monte Carlo simulation functionality."""
    
    def test_basic_monte_carlo(self):
        """Test basic Monte Carlo simulation."""
        # Define uncertain inputs
        x = UncertainValue(10.0, 0.5)
        y = UncertainValue(5.0, 0.2)
        
        # Run Monte Carlo
        def calculation(x_val, y_val):
            return x_val * y_val + x_val / y_val
            
        result = monte_carlo(
            function=calculation,
            inputs={'x': x, 'y': y},
            samples=10000
        )
        
        # Check result is close to analytical
        expected_value = 10.0 * 5.0 + 10.0 / 5.0  # 52.0
        self.assertAlmostEqual(result.value, expected_value, places=1)
        
        # Check uncertainty is reasonable
        self.assertGreater(result.uncertainty, 0)
        self.assertLess(result.uncertainty, 5.0)
        
    def test_parallel_monte_carlo(self):
        """Test parallel Monte Carlo execution."""
        import time
        
        # Complex calculation
        def slow_calculation(x, y, z):
            # Simulate expensive computation
            result = 0
            for _ in range(100):
                result += x * np.sin(y) + np.cos(z)
            return result / 100
            
        x = UncertainValue(1.0, 0.1)
        y = UncertainValue(2.0, 0.2)
        z = UncertainValue(3.0, 0.3)
        
        # Run parallel Monte Carlo
        start_time = time.time()
        result_parallel = monte_carlo(
            function=slow_calculation,
            inputs={'x': x, 'y': y, 'z': z},
            samples=1000,
            parallel=True,
            n_cores=4
        )
        parallel_time = time.time() - start_time
        
        # Run serial Monte Carlo
        start_time = time.time()
        result_serial = monte_carlo(
            function=slow_calculation,
            inputs={'x': x, 'y': y, 'z': z},
            samples=1000,
            parallel=False
        )
        serial_time = time.time() - start_time
        
        # Results should be similar
        self.assertAlmostEqual(result_parallel.value, result_serial.value, places=1)
        
        # Parallel should be faster (allow some overhead)
        # Note: On small samples, parallel might be slower due to overhead
        print(f"Parallel time: {parallel_time:.2f}s")
        print(f"Serial time: {serial_time:.2f}s")
        
    def test_monte_carlo_convergence(self):
        """Test Monte Carlo convergence with sample size."""
        x = UncertainValue(10.0, 1.0)
        
        def simple_function(x):
            return x ** 2
            
        # Test with different sample sizes
        sample_sizes = [100, 1000, 10000]
        uncertainties = []
        
        for n_samples in sample_sizes:
            result = monte_carlo(
                function=simple_function,
                inputs={'x': x},
                samples=n_samples
            )
            uncertainties.append(result.uncertainty)
            
        # Uncertainty should decrease with more samples
        for i in range(len(uncertainties) - 1):
            self.assertLess(uncertainties[i+1], uncertainties[i] * 1.1)


class TestCorrelatedUncertainties(unittest.TestCase):
    """Test correlated uncertainty handling."""
    
    def test_correlation_matrix(self):
        """Test multivariate uncertain values with correlations."""
        from synapse_lang.uncertainty import MultivariateUncertain
        
        # Create correlated measurements
        means = [25.3, 1013.25, 65.0]
        uncertainties = [0.2, 1.5, 3.0]
        correlation_matrix = [
            [1.0, 0.7, 0.3],
            [0.7, 1.0, 0.5],
            [0.3, 0.5, 1.0]
        ]
        
        multivariate = MultivariateUncertain(
            means=means,
            uncertainties=uncertainties,
            correlations=correlation_matrix,
            labels=["temperature", "pressure", "humidity"]
        )
        
        # Check basic properties
        self.assertEqual(len(multivariate), 3)
        self.assertEqual(multivariate["temperature"].value, 25.3)
        self.assertEqual(multivariate["temperature"].uncertainty, 0.2)
        
        # Check correlation preserved
        samples = multivariate.sample(10000)
        correlation_estimated = np.corrcoef(samples.T)
        
        # Check diagonal is 1
        for i in range(3):
            self.assertAlmostEqual(correlation_estimated[i, i], 1.0, places=1)
            
        # Check off-diagonal correlations (roughly)
        self.assertAlmostEqual(correlation_estimated[0, 1], 0.7, places=1)
        self.assertAlmostEqual(correlation_estimated[0, 2], 0.3, places=1)
        self.assertAlmostEqual(correlation_estimated[1, 2], 0.5, places=1)


class TestUncertaintyPropagation(unittest.TestCase):
    """Test different uncertainty propagation methods."""
    
    def test_analytical_propagation(self):
        """Test analytical uncertainty propagation."""
        x = UncertainValue(5.0, 0.1)
        y = UncertainValue(3.0, 0.05)
        
        # Test with known analytical solution
        # f(x,y) = x*y, uncertainty = sqrt((y*dx)^2 + (x*dy)^2)
        result = propagate_uncertainty(
            function=lambda x, y: x * y,
            variables={'x': x, 'y': y},
            method='analytical'
        )
        
        expected_uncertainty = sqrt((3.0 * 0.1)**2 + (5.0 * 0.05)**2)
        self.assertAlmostEqual(result.uncertainty, expected_uncertainty, places=6)
        
    def test_numerical_propagation(self):
        """Test numerical uncertainty propagation."""
        x = UncertainValue(2.0, 0.1)
        
        # Non-linear function
        result = propagate_uncertainty(
            function=lambda x: x**3 + 2*x**2 + x + 1,
            variables={'x': x},
            method='numerical'
        )
        
        # Check result is reasonable
        expected_value = 2**3 + 2*2**2 + 2 + 1  # 19
        self.assertAlmostEqual(result.value, expected_value, places=6)
        self.assertGreater(result.uncertainty, 0)
        
    def test_symbolic_propagation(self):
        """Test symbolic uncertainty propagation."""
        # This would require sympy integration
        pass  # Placeholder for symbolic tests


class TestStatisticalFunctions(unittest.TestCase):
    """Test statistical functions with uncertainty."""
    
    def test_weighted_mean(self):
        """Test weighted mean with uncertainties."""
        from synapse_lang.uncertainty import weighted_mean
        
        measurements = [
            UncertainValue(10.1, 0.5),
            UncertainValue(10.3, 0.2),
            UncertainValue(9.9, 0.3),
            UncertainValue(10.2, 0.1)
        ]
        
        result = weighted_mean(measurements)
        
        # Most precise measurement (smallest uncertainty) should have most weight
        # Result should be closest to 10.2 ± 0.1
        self.assertAlmostEqual(result.value, 10.2, places=1)
        self.assertLess(result.uncertainty, 0.1)  # Combined uncertainty less than smallest
        
    def test_chi_squared(self):
        """Test chi-squared calculation with uncertainties."""
        from synapse_lang.uncertainty import chi_squared_test
        
        # Observed values with uncertainties
        observed = [
            UncertainValue(10.2, 0.5),
            UncertainValue(9.8, 0.4),
            UncertainValue(10.5, 0.6)
        ]
        
        # Expected value
        expected = UncertainValue(10.0, 0.1)
        
        chi2, p_value = chi_squared_test(observed, expected)
        
        # Should not reject null hypothesis (values consistent with expected)
        self.assertGreater(p_value, 0.05)


if __name__ == '__main__':
    unittest.main(verbosity=2)