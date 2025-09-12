"""UncertaintyEngine - Complete uncertainty quantification for Synapse language."""

import numpy as np
import numba
from numba import jit, njit, prange
from typing import Union, List, Tuple, Optional, Callable, Any, Dict
from dataclasses import dataclass
import functools
from enum import Enum
import warnings
from scipy import stats
import math

try:
    from uncertainties import ufloat, unumpy
    UNCERTAINTIES_AVAILABLE = True
except ImportError:
    UNCERTAINTIES_AVAILABLE = False


class PropagationMethod(Enum):
    """Uncertainty propagation methods."""
    LINEAR = "linear"  # First-order Taylor approximation
    MONTE_CARLO = "monte_carlo"  # Monte Carlo sampling
    BAYESIAN = "bayesian"  # Bayesian inference
    INTERVAL = "interval"  # Interval arithmetic
    POLYNOMIAL = "polynomial"  # Polynomial chaos expansion


@dataclass
class UncertaintyConfig:
    """Uncertainty engine configuration."""
    method: PropagationMethod = PropagationMethod.LINEAR
    samples: int = 10000  # For Monte Carlo
    confidence_level: float = 0.95
    correlation_threshold: float = 1e-10
    max_order: int = 2  # For polynomial methods
    parallel: bool = True
    cache_results: bool = True


class UncertainValue:
    """Represents a value with uncertainty."""
    
    def __init__(self, nominal: float, uncertainty: float = 0.0, 
                 distribution: str = "normal", correlation_id: Optional[str] = None):
        self.nominal = float(nominal)
        self.uncertainty = float(abs(uncertainty))
        self.distribution = distribution.lower()
        self.correlation_id = correlation_id
        self._samples_cache = None
        
    @property 
    def relative_uncertainty(self) -> float:
        """Relative uncertainty as fraction."""
        if self.nominal == 0:
            return float('inf') if self.uncertainty > 0 else 0.0
        return abs(self.uncertainty / self.nominal)
    
    @property
    def confidence_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """Confidence interval bounds."""
        if self.distribution == "normal":
            z_score = stats.norm.ppf((1 + confidence) / 2)
            margin = z_score * self.uncertainty
            return (self.nominal - margin, self.nominal + margin)
        elif self.distribution == "uniform":
            half_width = self.uncertainty * math.sqrt(3)
            return (self.nominal - half_width, self.nominal + half_width)
        else:
            # Fallback to normal approximation
            margin = 1.96 * self.uncertainty  # 95% CI
            return (self.nominal - margin, self.nominal + margin)
    
    def sample(self, n_samples: int = 1000) -> np.ndarray:
        """Generate random samples from the distribution."""
        if self._samples_cache is not None and len(self._samples_cache) >= n_samples:
            return self._samples_cache[:n_samples]
            
        if self.distribution == "normal":
            samples = np.random.normal(self.nominal, self.uncertainty, n_samples)
        elif self.distribution == "uniform":
            half_width = self.uncertainty * math.sqrt(3)
            samples = np.random.uniform(
                self.nominal - half_width, 
                self.nominal + half_width, 
                n_samples
            )
        elif self.distribution == "lognormal":
            # For lognormal, uncertainty is the geometric standard deviation
            mu = np.log(self.nominal)
            sigma = np.log(1 + self.uncertainty / self.nominal)
            samples = np.random.lognormal(mu, sigma, n_samples)
        elif self.distribution == "triangular":
            # Symmetric triangular around nominal
            half_width = self.uncertainty * math.sqrt(6)
            samples = np.random.triangular(
                self.nominal - half_width,
                self.nominal,
                self.nominal + half_width,
                n_samples
            )
        else:
            # Default to normal
            samples = np.random.normal(self.nominal, self.uncertainty, n_samples)
            
        self._samples_cache = samples
        return samples
    
    def __add__(self, other) -> 'UncertainValue':
        if isinstance(other, UncertainValue):
            # Check for correlation
            if (self.correlation_id and other.correlation_id and 
                self.correlation_id == other.correlation_id):
                # Perfect positive correlation
                new_uncertainty = self.uncertainty + other.uncertainty
            else:
                # Uncorrelated - add in quadrature
                new_uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
            return UncertainValue(self.nominal + other.nominal, new_uncertainty)
        else:
            return UncertainValue(self.nominal + other, self.uncertainty)
    
    def __radd__(self, other) -> 'UncertainValue':
        return self.__add__(other)
    
    def __sub__(self, other) -> 'UncertainValue':
        if isinstance(other, UncertainValue):
            if (self.correlation_id and other.correlation_id and 
                self.correlation_id == other.correlation_id):
                # Perfect correlation - uncertainties cancel for subtraction
                new_uncertainty = abs(self.uncertainty - other.uncertainty)
            else:
                new_uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
            return UncertainValue(self.nominal - other.nominal, new_uncertainty)
        else:
            return UncertainValue(self.nominal - other, self.uncertainty)
    
    def __rsub__(self, other) -> 'UncertainValue':
        return UncertainValue(other, 0) - self
    
    def __mul__(self, other) -> 'UncertainValue':
        if isinstance(other, UncertainValue):
            # For multiplication: σ_z/z = √((σ_x/x)² + (σ_y/y)²)
            if self.nominal == 0 or other.nominal == 0:
                return UncertainValue(0, 0)
            
            rel_unc1 = self.relative_uncertainty
            rel_unc2 = other.relative_uncertainty
            
            if (self.correlation_id and other.correlation_id and 
                self.correlation_id == other.correlation_id):
                # Correlated case
                new_rel_unc = rel_unc1 + rel_unc2
            else:
                new_rel_unc = math.sqrt(rel_unc1**2 + rel_unc2**2)
                
            new_nominal = self.nominal * other.nominal
            new_uncertainty = abs(new_nominal * new_rel_unc)
            return UncertainValue(new_nominal, new_uncertainty)
        else:
            return UncertainValue(self.nominal * other, abs(self.uncertainty * other))
    
    def __rmul__(self, other) -> 'UncertainValue':
        return self.__mul__(other)
    
    def __truediv__(self, other) -> 'UncertainValue':
        if isinstance(other, UncertainValue):
            if other.nominal == 0:
                raise ZeroDivisionError("Division by uncertain zero")
            
            rel_unc1 = self.relative_uncertainty
            rel_unc2 = other.relative_uncertainty
            
            if (self.correlation_id and other.correlation_id and 
                self.correlation_id == other.correlation_id):
                new_rel_unc = abs(rel_unc1 - rel_unc2)
            else:
                new_rel_unc = math.sqrt(rel_unc1**2 + rel_unc2**2)
                
            new_nominal = self.nominal / other.nominal
            new_uncertainty = abs(new_nominal * new_rel_unc)
            return UncertainValue(new_nominal, new_uncertainty)
        else:
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            return UncertainValue(self.nominal / other, self.uncertainty / abs(other))
    
    def __rtruediv__(self, other) -> 'UncertainValue':
        return UncertainValue(other, 0) / self
    
    def __pow__(self, exponent) -> 'UncertainValue':
        if isinstance(exponent, UncertainValue):
            # Use logarithmic differentiation for a^b
            if self.nominal <= 0:
                raise ValueError("Cannot raise non-positive uncertain number to uncertain power")
            
            # z = x^y, ln(z) = y*ln(x)
            # σ_z/z = √((y*σ_x/x)² + (ln(x)*σ_y)²)
            ln_x = math.log(self.nominal)
            rel_unc_x = self.relative_uncertainty
            
            term1 = (exponent.nominal * rel_unc_x) ** 2
            term2 = (ln_x * exponent.uncertainty) ** 2
            new_rel_unc = math.sqrt(term1 + term2)
            
            new_nominal = self.nominal ** exponent.nominal
            new_uncertainty = abs(new_nominal * new_rel_unc)
            return UncertainValue(new_nominal, new_uncertainty)
        else:
            # Simple power rule: z = x^n, σ_z = |n*x^(n-1)*σ_x|
            if self.nominal == 0 and exponent != 0:
                return UncertainValue(0, 0)
            
            new_nominal = self.nominal ** exponent
            derivative = exponent * (self.nominal ** (exponent - 1))
            new_uncertainty = abs(derivative * self.uncertainty)
            return UncertainValue(new_nominal, new_uncertainty)
    
    def sin(self) -> 'UncertainValue':
        """Sine function with uncertainty propagation."""
        new_nominal = math.sin(self.nominal)
        derivative = math.cos(self.nominal)
        new_uncertainty = abs(derivative * self.uncertainty)
        return UncertainValue(new_nominal, new_uncertainty)
    
    def cos(self) -> 'UncertainValue':
        """Cosine function with uncertainty propagation."""
        new_nominal = math.cos(self.nominal)
        derivative = -math.sin(self.nominal)
        new_uncertainty = abs(derivative * self.uncertainty)
        return UncertainValue(new_nominal, new_uncertainty)
    
    def exp(self) -> 'UncertainValue':
        """Exponential function with uncertainty propagation."""
        new_nominal = math.exp(self.nominal)
        new_uncertainty = new_nominal * self.uncertainty
        return UncertainValue(new_nominal, new_uncertainty)
    
    def log(self) -> 'UncertainValue':
        """Natural logarithm with uncertainty propagation."""
        if self.nominal <= 0:
            raise ValueError("Cannot take logarithm of non-positive uncertain number")
        new_nominal = math.log(self.nominal)
        new_uncertainty = self.uncertainty / self.nominal
        return UncertainValue(new_nominal, new_uncertainty)
    
    def sqrt(self) -> 'UncertainValue':
        """Square root with uncertainty propagation."""
        if self.nominal < 0:
            raise ValueError("Cannot take square root of negative uncertain number")
        if self.nominal == 0:
            return UncertainValue(0, 0)
        
        new_nominal = math.sqrt(self.nominal)
        derivative = 0.5 / new_nominal
        new_uncertainty = derivative * self.uncertainty
        return UncertainValue(new_nominal, new_uncertainty)
    
    def __repr__(self) -> str:
        return f"{self.nominal} ± {self.uncertainty}"
    
    def __str__(self) -> str:
        return self.__repr__()


class CorrelationMatrix:
    """Manages correlations between uncertain variables."""
    
    def __init__(self):
        self.correlations: Dict[Tuple[str, str], float] = {}
        self.variables: Dict[str, UncertainValue] = {}
    
    def add_variable(self, name: str, variable: UncertainValue):
        """Add a variable to the correlation matrix."""
        self.variables[name] = variable
        variable.correlation_id = name
    
    def set_correlation(self, var1: str, var2: str, correlation: float):
        """Set correlation coefficient between two variables."""
        if abs(correlation) > 1:
            raise ValueError("Correlation coefficient must be between -1 and 1")
        
        key = tuple(sorted([var1, var2]))
        self.correlations[key] = correlation
    
    def get_correlation(self, var1: str, var2: str) -> float:
        """Get correlation coefficient between two variables."""
        if var1 == var2:
            return 1.0
        
        key = tuple(sorted([var1, var2]))
        return self.correlations.get(key, 0.0)
    
    def propagate_correlated(self, expression: Callable, variables: List[str], 
                           samples: int = 10000) -> UncertainValue:
        """Propagate uncertainties through expression considering correlations."""
        # Generate correlated samples using Cholesky decomposition
        n_vars = len(variables)
        
        # Build correlation matrix
        corr_matrix = np.eye(n_vars)
        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                corr_matrix[i, j] = self.get_correlation(var1, var2)
        
        # Generate correlated samples
        try:
            L = np.linalg.cholesky(corr_matrix)
            uncorr_samples = np.random.standard_normal((samples, n_vars))
            corr_samples = uncorr_samples @ L.T
            
            # Transform to actual distributions
            var_samples = []
            for i, var_name in enumerate(variables):
                var = self.variables[var_name]
                if var.distribution == "normal":
                    samples_i = var.nominal + var.uncertainty * corr_samples[:, i]
                else:
                    # For non-normal, use inverse CDF transformation
                    uniform_samples = stats.norm.cdf(corr_samples[:, i])
                    if var.distribution == "uniform":
                        half_width = var.uncertainty * math.sqrt(3)
                        samples_i = stats.uniform.ppf(
                            uniform_samples, 
                            var.nominal - half_width, 
                            2 * half_width
                        )
                    else:  # Default to normal
                        samples_i = var.nominal + var.uncertainty * corr_samples[:, i]
                
                var_samples.append(samples_i)
            
            # Evaluate expression for all samples
            var_samples = np.array(var_samples).T
            results = np.array([expression(*sample) for sample in var_samples])
            
            # Calculate statistics
            mean_result = np.mean(results)
            std_result = np.std(results, ddof=1)
            
            return UncertainValue(mean_result, std_result)
            
        except np.linalg.LinAlgError:
            warnings.warn("Correlation matrix is not positive definite, using uncorrelated propagation")
            return self._propagate_uncorrelated(expression, variables, samples)
    
    def _propagate_uncorrelated(self, expression: Callable, variables: List[str], 
                               samples: int) -> UncertainValue:
        """Fallback for uncorrelated propagation."""
        var_samples = []
        for var_name in variables:
            var = self.variables[var_name]
            var_samples.append(var.sample(samples))
        
        var_samples = np.array(var_samples).T
        results = np.array([expression(*sample) for sample in var_samples])
        
        mean_result = np.mean(results)
        std_result = np.std(results, ddof=1)
        
        return UncertainValue(mean_result, std_result)


class UncertaintyEngine:
    """Main uncertainty quantification engine."""
    
    def __init__(self, config: Optional[UncertaintyConfig] = None):
        self.config = config or UncertaintyConfig()
        self.correlation_matrix = CorrelationMatrix()
        self.variables = {}
        self.cache = {}
    
    def create_uncertain(self, nominal: float, uncertainty: float, 
                        distribution: str = "normal", name: Optional[str] = None) -> UncertainValue:
        """Create an uncertain value."""
        uval = UncertainValue(nominal, uncertainty, distribution)
        if name:
            self.variables[name] = uval
            self.correlation_matrix.add_variable(name, uval)
        return uval
    
    def set_correlation(self, var1: str, var2: str, correlation: float):
        """Set correlation between variables."""
        self.correlation_matrix.set_correlation(var1, var2, correlation)
    
    def propagate(self, expression: Callable, variables: Union[List[str], Dict[str, UncertainValue]], 
                  method: Optional[PropagationMethod] = None) -> UncertainValue:
        """Propagate uncertainties through an expression."""
        method = method or self.config.method
        
        if isinstance(variables, dict):
            var_names = list(variables.keys())
            for name, var in variables.items():
                self.correlation_matrix.add_variable(name, var)
        else:
            var_names = variables
        
        cache_key = (str(expression), tuple(sorted(var_names)), method.value)
        if self.config.cache_results and cache_key in self.cache:
            return self.cache[cache_key]
        
        if method == PropagationMethod.LINEAR:
            result = self._linear_propagation(expression, var_names)
        elif method == PropagationMethod.MONTE_CARLO:
            result = self._monte_carlo_propagation(expression, var_names)
        elif method == PropagationMethod.BAYESIAN:
            result = self._bayesian_propagation(expression, var_names)
        elif method == PropagationMethod.INTERVAL:
            result = self._interval_propagation(expression, var_names)
        else:
            result = self._monte_carlo_propagation(expression, var_names)  # Default
        
        if self.config.cache_results:
            self.cache[cache_key] = result
        
        return result
    
    def _linear_propagation(self, expression: Callable, var_names: List[str]) -> UncertainValue:
        """First-order Taylor approximation propagation."""
        # Get nominal values
        nominals = [self.correlation_matrix.variables[name].nominal for name in var_names]
        
        # Evaluate function at nominal point
        f_nominal = expression(*nominals)
        
        # Compute partial derivatives numerically
        h = 1e-8  # Step size for numerical differentiation
        derivatives = []
        
        for i, var_name in enumerate(var_names):
            point_plus = nominals.copy()
            point_minus = nominals.copy()
            point_plus[i] += h
            point_minus[i] -= h
            
            try:
                f_plus = expression(*point_plus)
                f_minus = expression(*point_minus)
                derivative = (f_plus - f_minus) / (2 * h)
            except:
                # Forward difference if central fails
                try:
                    f_plus = expression(*point_plus)
                    derivative = (f_plus - f_nominal) / h
                except:
                    derivative = 0.0
            
            derivatives.append(derivative)
        
        # Calculate uncertainty using error propagation formula
        variance = 0.0
        for i, var1 in enumerate(var_names):
            for j, var2 in enumerate(var_names):
                uncertainty1 = self.correlation_matrix.variables[var1].uncertainty
                uncertainty2 = self.correlation_matrix.variables[var2].uncertainty
                correlation = self.correlation_matrix.get_correlation(var1, var2)
                
                variance += (derivatives[i] * derivatives[j] * 
                           uncertainty1 * uncertainty2 * correlation)
        
        uncertainty = math.sqrt(abs(variance))
        return UncertainValue(f_nominal, uncertainty)
    
    def _monte_carlo_propagation(self, expression: Callable, var_names: List[str]) -> UncertainValue:
        """Monte Carlo uncertainty propagation."""
        return self.correlation_matrix.propagate_correlated(
            expression, var_names, self.config.samples
        )
    
    def _bayesian_propagation(self, expression: Callable, var_names: List[str]) -> UncertainValue:
        """Bayesian uncertainty propagation (simplified implementation)."""
        # For now, fall back to Monte Carlo
        # In a full implementation, this would use Bayesian inference
        return self._monte_carlo_propagation(expression, var_names)
    
    def _interval_propagation(self, expression: Callable, var_names: List[str]) -> UncertainValue:
        """Interval arithmetic propagation."""
        # Find min/max bounds by sampling extreme points
        n_vars = len(var_names)
        
        # Sample corners of uncertainty hypercube
        results = []
        for i in range(2**n_vars):
            point = []
            for j, var_name in enumerate(var_names):
                var = self.correlation_matrix.variables[var_name]
                if (i >> j) & 1:
                    # Upper bound
                    point.append(var.nominal + var.uncertainty)
                else:
                    # Lower bound
                    point.append(var.nominal - var.uncertainty)
            
            try:
                result = expression(*point)
                results.append(result)
            except:
                pass  # Skip points where function is undefined
        
        if not results:
            return UncertainValue(0, float('inf'))
        
        min_val = min(results)
        max_val = max(results)
        center = (min_val + max_val) / 2
        half_width = (max_val - min_val) / 2
        
        return UncertainValue(center, half_width)
    
    # Mathematical functions for uncertain values
    @staticmethod
    def sin(x: UncertainValue) -> UncertainValue:
        return x.sin()
    
    @staticmethod
    def cos(x: UncertainValue) -> UncertainValue:
        return x.cos()
    
    @staticmethod
    def exp(x: UncertainValue) -> UncertainValue:
        return x.exp()
    
    @staticmethod
    def log(x: UncertainValue) -> UncertainValue:
        return x.log()
    
    @staticmethod
    def sqrt(x: UncertainValue) -> UncertainValue:
        return x.sqrt()
    
    def sensitivity_analysis(self, expression: Callable, var_names: List[str]) -> Dict[str, float]:
        """Perform sensitivity analysis to identify most important variables."""
        # Use Sobol indices or local sensitivity
        sensitivities = {}
        
        base_result = self._linear_propagation(expression, var_names)
        base_variance = base_result.uncertainty ** 2
        
        for var_name in var_names:
            # Calculate first-order Sobol index (simplified)
            # Remove this variable and see variance reduction
            other_vars = [v for v in var_names if v != var_name]
            if other_vars:
                reduced_result = self._linear_propagation(expression, other_vars)
                reduced_variance = reduced_result.uncertainty ** 2
                sensitivity = max(0, (base_variance - reduced_variance) / base_variance)
            else:
                sensitivity = 1.0
            
            sensitivities[var_name] = sensitivity
        
        return sensitivities


# High-level convenience functions
def uncertain(nominal: float, uncertainty: float, distribution: str = "normal") -> UncertainValue:
    """Create an uncertain value."""
    return UncertainValue(nominal, uncertainty, distribution)

def propagate_uncertainty(func: Callable, **kwargs) -> UncertainValue:
    """Propagate uncertainty through a function."""
    engine = UncertaintyEngine()
    variables = {}
    
    for name, value in kwargs.items():
        if isinstance(value, UncertainValue):
            variables[name] = value
        else:
            variables[name] = UncertainValue(value, 0)
    
    return engine.propagate(func, variables)

# Decorator for uncertainty propagation
def uncertain_function(method: PropagationMethod = PropagationMethod.LINEAR):
    """Decorator to automatically propagate uncertainties."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if any arguments are uncertain
            uncertain_args = {}
            regular_args = []
            
            for i, arg in enumerate(args):
                if isinstance(arg, UncertainValue):
                    uncertain_args[f'arg_{i}'] = arg
                    regular_args.append(arg.nominal)
                else:
                    regular_args.append(arg)
            
            if not uncertain_args:
                # No uncertain arguments, call normally
                return func(*args, **kwargs)
            
            # Create wrapper function for propagation
            def wrapper_func(*nominal_args):
                combined_args = list(args)
                for i, (name, _) in enumerate(uncertain_args.items()):
                    combined_args[int(name.split('_')[1])] = nominal_args[i]
                return func(*combined_args, **kwargs)
            
            engine = UncertaintyEngine(UncertaintyConfig(method=method))
            return engine.propagate(wrapper_func, uncertain_args)
        
        return wrapper
    return decorator