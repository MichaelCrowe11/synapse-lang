"""
Advanced Uncertainty Propagation for Synapse Language
Implements sophisticated uncertainty quantification and error propagation
"""

import numpy as np
from scipy import stats
from typing import Union, Tuple, List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
import sympy as sym
from numba import jit, vectorize
import warnings


@dataclass
class UncertainValue:
    """
    Represents a value with associated uncertainty
    Supports multiple uncertainty representations and propagation methods
    """
    value: float
    uncertainty: float
    distribution: str = "normal"  # normal, uniform, triangular, beta
    confidence: float = 0.68  # 1-sigma by default
    samples: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.samples is None:
            self.samples = self._generate_samples(10000)
    
    def _generate_samples(self, n_samples: int = 10000) -> np.ndarray:
        """Generate Monte Carlo samples from the uncertainty distribution"""
        np.random.seed(42)  # Reproducible for testing
        
        if self.distribution == "normal":
            return np.random.normal(self.value, self.uncertainty, n_samples)
        elif self.distribution == "uniform":
            half_width = self.uncertainty * np.sqrt(3)  # Convert to uniform half-width
            return np.random.uniform(self.value - half_width, self.value + half_width, n_samples)
        elif self.distribution == "triangular":
            return np.random.triangular(self.value - self.uncertainty, 
                                       self.value, 
                                       self.value + self.uncertainty, n_samples)
        elif self.distribution == "beta":
            # Beta distribution centered on value with spread uncertainty
            alpha, beta = 2, 2  # Default shape parameters
            return stats.beta.rvs(alpha, beta, loc=self.value-self.uncertainty, 
                                scale=2*self.uncertainty, size=n_samples)
        else:
            raise ValueError(f"Unsupported distribution: {self.distribution}")
    
    def __str__(self) -> str:
        return f"{self.value:.6g} ± {self.uncertainty:.6g}"
    
    def __repr__(self) -> str:
        return f"UncertainValue({self.value}, {self.uncertainty}, '{self.distribution}')"
    
    # Arithmetic operations with uncertainty propagation
    def __add__(self, other):
        if isinstance(other, UncertainValue):
            # Quadrature addition for independent uncertainties
            new_value = self.value + other.value
            new_uncertainty = np.sqrt(self.uncertainty**2 + other.uncertainty**2)
            new_samples = self.samples + other.samples
            return UncertainValue(new_value, new_uncertainty, samples=new_samples)
        else:
            # Adding constant
            return UncertainValue(self.value + other, self.uncertainty, samples=self.samples + other)
    
    def __sub__(self, other):
        if isinstance(other, UncertainValue):
            new_value = self.value - other.value
            new_uncertainty = np.sqrt(self.uncertainty**2 + other.uncertainty**2)
            new_samples = self.samples - other.samples
            return UncertainValue(new_value, new_uncertainty, samples=new_samples)
        else:
            return UncertainValue(self.value - other, self.uncertainty, samples=self.samples - other)
    
    def __mul__(self, other):
        if isinstance(other, UncertainValue):
            # Relative uncertainty propagation for multiplication
            new_value = self.value * other.value
            rel_unc_self = self.uncertainty / abs(self.value) if self.value != 0 else 0
            rel_unc_other = other.uncertainty / abs(other.value) if other.value != 0 else 0
            new_rel_uncertainty = np.sqrt(rel_unc_self**2 + rel_unc_other**2)
            new_uncertainty = abs(new_value) * new_rel_uncertainty
            new_samples = self.samples * other.samples
            return UncertainValue(new_value, new_uncertainty, samples=new_samples)
        else:
            return UncertainValue(self.value * other, abs(other) * self.uncertainty, 
                                samples=self.samples * other)
    
    def __truediv__(self, other):
        if isinstance(other, UncertainValue):
            new_value = self.value / other.value
            rel_unc_self = self.uncertainty / abs(self.value) if self.value != 0 else 0
            rel_unc_other = other.uncertainty / abs(other.value) if other.value != 0 else 0
            new_rel_uncertainty = np.sqrt(rel_unc_self**2 + rel_unc_other**2)
            new_uncertainty = abs(new_value) * new_rel_uncertainty
            new_samples = self.samples / other.samples
            return UncertainValue(new_value, new_uncertainty, samples=new_samples)
        else:
            return UncertainValue(self.value / other, self.uncertainty / abs(other),
                                samples=self.samples / other)
    
    def __pow__(self, power):
        """Power operation with uncertainty propagation"""
        new_value = self.value ** power
        if self.value != 0:
            new_rel_uncertainty = abs(power) * (self.uncertainty / abs(self.value))
            new_uncertainty = abs(new_value) * new_rel_uncertainty
        else:
            new_uncertainty = 0
        new_samples = self.samples ** power
        return UncertainValue(new_value, new_uncertainty, samples=new_samples)
    
    # Reverse operations
    __radd__ = __add__
    __rsub__ = lambda self, other: UncertainValue(other - self.value, self.uncertainty)
    __rmul__ = __mul__
    __rtruediv__ = lambda self, other: UncertainValue(other / self.value, 
                                                     abs(other) * self.uncertainty / (self.value**2))


class UncertaintyPropagator:
    """
    Advanced uncertainty propagation using multiple methods:
    1. Linear approximation (first-order Taylor expansion)
    2. Monte Carlo sampling
    3. Symbolic differentiation
    4. Bayesian inference
    """
    
    def __init__(self, method: str = "monte_carlo"):
        self.method = method
        self.symbolic_cache: Dict[str, sym.Expr] = {}
    
    @jit(nopython=True)
    def _linear_propagation(self, func: Callable, values: np.ndarray, 
                          uncertainties: np.ndarray, derivatives: np.ndarray) -> float:
        """First-order linear uncertainty propagation"""
        variance = np.sum((derivatives * uncertainties) ** 2)
        return np.sqrt(variance)
    
    def monte_carlo_propagation(self, func: Callable, *uncertain_values: UncertainValue,
                               n_samples: int = 100000) -> UncertainValue:
        """Monte Carlo uncertainty propagation"""
        # Stack all samples
        samples_list = [uv.samples[:n_samples] for uv in uncertain_values]
        
        # Apply function to all sample combinations
        try:
            result_samples = func(*samples_list)
            
            # Calculate statistics
            mean_result = np.mean(result_samples)
            std_result = np.std(result_samples)
            
            return UncertainValue(mean_result, std_result, samples=result_samples)
        except Exception as e:
            raise RuntimeError(f"Monte Carlo propagation failed: {e}")
    
    def symbolic_propagation(self, expression: str, variables: Dict[str, UncertainValue]) -> UncertainValue:
        """Symbolic differentiation for uncertainty propagation"""
        try:
            # Parse symbolic expression
            expr = sym.sympify(expression)
            symbols = list(expr.free_symbols)
            
            # Calculate partial derivatives
            partials = {}
            for symbol in symbols:
                partials[symbol] = sym.diff(expr, symbol)
            
            # Evaluate at mean values
            var_values = {sym.Symbol(name): uv.value for name, uv in variables.items()}
            result_value = float(expr.subs(var_values))
            
            # Calculate uncertainty using partial derivatives
            variance = 0
            for symbol in symbols:
                var_name = str(symbol)
                if var_name in variables:
                    partial_value = float(partials[symbol].subs(var_values))
                    variance += (partial_value * variables[var_name].uncertainty) ** 2
            
            uncertainty = np.sqrt(variance)
            
            return UncertainValue(result_value, uncertainty)
        
        except Exception as e:
            raise RuntimeError(f"Symbolic propagation failed: {e}")
    
    def bayesian_update(self, prior: UncertainValue, likelihood_data: np.ndarray, 
                       likelihood_uncertainty: float) -> UncertainValue:
        """Bayesian uncertainty update with new measurements"""
        # Simplified Bayesian update assuming normal distributions
        prior_precision = 1 / (prior.uncertainty ** 2)
        likelihood_precision = 1 / (likelihood_uncertainty ** 2)
        
        # Posterior precision and mean
        posterior_precision = prior_precision + len(likelihood_data) * likelihood_precision
        posterior_variance = 1 / posterior_precision
        
        posterior_mean = (prior_precision * prior.value + 
                         likelihood_precision * np.sum(likelihood_data)) / posterior_precision
        
        posterior_uncertainty = np.sqrt(posterior_variance)
        
        return UncertainValue(posterior_mean, posterior_uncertainty, distribution="normal")


class CorrelatedUncertainty:
    """Handle correlated uncertainties between variables"""
    
    def __init__(self):
        self.correlation_matrix: Dict[Tuple[str, str], float] = {}
        self.variables: Dict[str, UncertainValue] = {}
    
    def add_variable(self, name: str, uncertain_value: UncertainValue):
        """Add a variable to the correlation tracking"""
        self.variables[name] = uncertain_value
    
    def set_correlation(self, var1: str, var2: str, correlation: float):
        """Set correlation coefficient between two variables (-1 to 1)"""
        if not (-1 <= correlation <= 1):
            raise ValueError("Correlation must be between -1 and 1")
        
        self.correlation_matrix[(var1, var2)] = correlation
        self.correlation_matrix[(var2, var1)] = correlation  # Symmetric
    
    def propagate_correlated(self, func: Callable, var_names: List[str]) -> UncertainValue:
        """Propagate uncertainty accounting for correlations"""
        values = [self.variables[name].value for name in var_names]
        uncertainties = [self.variables[name].uncertainty for name in var_names]
        
        # Create correlated samples using Cholesky decomposition
        n_vars = len(var_names)
        correlation_matrix = np.eye(n_vars)
        
        for i, var1 in enumerate(var_names):
            for j, var2 in enumerate(var_names):
                if i != j:
                    corr = self.correlation_matrix.get((var1, var2), 0.0)
                    correlation_matrix[i, j] = corr
        
        # Generate correlated samples
        n_samples = 10000
        uncorrelated_samples = np.random.standard_normal((n_samples, n_vars))
        
        try:
            cholesky = np.linalg.cholesky(correlation_matrix)
            correlated_samples = uncorrelated_samples @ cholesky.T
            
            # Scale and shift samples
            scaled_samples = []
            for i, (value, uncertainty) in enumerate(zip(values, uncertainties)):
                scaled_samples.append(value + uncertainty * correlated_samples[:, i])
            
            # Apply function
            result_samples = func(*scaled_samples)
            
            return UncertainValue(np.mean(result_samples), np.std(result_samples), 
                                samples=result_samples)
        
        except np.linalg.LinAlgError:
            warnings.warn("Correlation matrix is not positive definite, using uncorrelated propagation")
            return self.propagate_uncorrelated(func, var_names)
    
    def propagate_uncorrelated(self, func: Callable, var_names: List[str]) -> UncertainValue:
        """Fallback to uncorrelated propagation"""
        uncertain_values = [self.variables[name] for name in var_names]
        propagator = UncertaintyPropagator("monte_carlo")
        return propagator.monte_carlo_propagation(func, *uncertain_values)


# Mathematical functions with uncertainty support
class UncertainMath:
    """Mathematical functions that preserve uncertainty"""
    
    @staticmethod
    def sin(x: UncertainValue) -> UncertainValue:
        """Sine with uncertainty propagation"""
        new_value = np.sin(x.value)
        # Derivative of sin is cos
        derivative = np.cos(x.value)
        new_uncertainty = abs(derivative) * x.uncertainty
        new_samples = np.sin(x.samples)
        return UncertainValue(new_value, new_uncertainty, samples=new_samples)
    
    @staticmethod
    def cos(x: UncertainValue) -> UncertainValue:
        """Cosine with uncertainty propagation"""
        new_value = np.cos(x.value)
        derivative = -np.sin(x.value)  # Derivative of cos is -sin
        new_uncertainty = abs(derivative) * x.uncertainty
        new_samples = np.cos(x.samples)
        return UncertainValue(new_value, new_uncertainty, samples=new_samples)
    
    @staticmethod
    def exp(x: UncertainValue) -> UncertainValue:
        """Exponential with uncertainty propagation"""
        new_value = np.exp(x.value)
        derivative = new_value  # Derivative of exp is exp
        new_uncertainty = derivative * x.uncertainty
        new_samples = np.exp(x.samples)
        return UncertainValue(new_value, new_uncertainty, samples=new_samples)
    
    @staticmethod
    def log(x: UncertainValue) -> UncertainValue:
        """Natural logarithm with uncertainty propagation"""
        if x.value <= 0:
            raise ValueError("Cannot take logarithm of non-positive value")
        
        new_value = np.log(x.value)
        derivative = 1 / x.value  # Derivative of ln is 1/x
        new_uncertainty = abs(derivative) * x.uncertainty
        new_samples = np.log(np.clip(x.samples, 1e-10, None))  # Avoid log(0)
        return UncertainValue(new_value, new_uncertainty, samples=new_samples)
    
    @staticmethod
    def sqrt(x: UncertainValue) -> UncertainValue:
        """Square root with uncertainty propagation"""
        if x.value < 0:
            raise ValueError("Cannot take square root of negative value")
        
        new_value = np.sqrt(x.value)
        derivative = 1 / (2 * new_value) if new_value != 0 else 0
        new_uncertainty = abs(derivative) * x.uncertainty
        new_samples = np.sqrt(np.clip(x.samples, 0, None))
        return UncertainValue(new_value, new_uncertainty, samples=new_samples)


# Integration with Synapse language constructs
class UncertaintyIntegration:
    """Integration layer for Synapse language uncertainty features"""
    
    @staticmethod
    def create_uncertain(value: float, uncertainty: float, 
                        distribution: str = "normal") -> UncertainValue:
        """Create uncertain value from Synapse syntax: uncertain x = 5.0 ± 0.1"""
        return UncertainValue(value, uncertainty, distribution)
    
    @staticmethod
    def measure_with_uncertainty(measurement_func: Callable, 
                               repetitions: int = 100) -> UncertainValue:
        """Perform repeated measurements to estimate uncertainty"""
        measurements = []
        for _ in range(repetitions):
            measurements.append(measurement_func())
        
        measurements = np.array(measurements)
        mean_value = np.mean(measurements)
        uncertainty = np.std(measurements, ddof=1)  # Sample standard deviation
        
        return UncertainValue(mean_value, uncertainty, samples=measurements)
    
    @staticmethod
    def combine_measurements(*measurements: UncertainValue) -> UncertainValue:
        """Optimally combine multiple measurements of the same quantity"""
        weights = [1 / (m.uncertainty ** 2) for m in measurements]
        total_weight = sum(weights)
        
        weighted_mean = sum(w * m.value for w, m in zip(weights, measurements)) / total_weight
        combined_uncertainty = 1 / np.sqrt(total_weight)
        
        return UncertainValue(weighted_mean, combined_uncertainty)