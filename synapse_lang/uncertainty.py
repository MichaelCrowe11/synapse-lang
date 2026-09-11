"""UncertaintyEngine - Complete uncertainty quantification for Synapse language."""

from __future__ import annotations

import functools
import importlib.util
import math
import warnings
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy import stats

UNCERTAINTIES_AVAILABLE = importlib.util.find_spec("uncertainties") is not None


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


class _Latent:
    """One independent source of uncertainty, standard normal by construction."""

    __slots__ = ("label",)

    def __init__(self, label: str | None = None):
        self.label = label

    def __repr__(self) -> str:
        return f"_Latent({self.label!r})" if self.label else f"_Latent(0x{id(self):x})"


def _source_key(correlation_id: str | None):
    # Values that share a correlation_id share one source and are perfectly correlated.
    return ("corr", correlation_id) if correlation_id is not None else _Latent()


_SCALARS = (int, float, np.integer, np.floating)


class UncertainValue:
    """A value with a standard uncertainty that remembers where the uncertainty came from.

    Every UncertainValue is, to first order, ``nominal + sum_k c_k Z_k`` over independent
    standard-normal sources ``Z_k``. The coefficients ``c_k`` (output units per standard
    deviation of the source) live in ``_linear``. Arithmetic combines coefficient maps
    with the chain rule, so a variable that appears twice in one formula is the same
    variable: ``x - x`` is exactly ``0 ± 0``, ``x / x`` is ``1 ± 0`` and ``t * b / (t + c)``
    carries the exact first-order derivative instead of treating the two ``t`` as
    independent. The reported uncertainty is ``sqrt(sum c_k^2)``; the covariance of two
    results is the sum over shared sources of ``c_k d_k``.

    ``correlation_id`` keeps the earlier contract: two values created with the same id
    share one source and are perfectly (+1) correlated.
    """

    __slots__ = ("nominal", "distribution", "_linear", "_correlation_id", "_samples_cache")

    def __init__(self, nominal: float, uncertainty: float = 0.0,
                 distribution: str = "normal", correlation_id: str | None = None,
                 *, _linear: dict | None = None):
        self.nominal = float(nominal)
        self.distribution = distribution.lower()
        self._correlation_id = correlation_id
        self._samples_cache = None
        if _linear is not None:
            self._linear = {k: float(c) for k, c in _linear.items() if c != 0.0}
        else:
            sigma = abs(float(uncertainty))
            if math.isnan(sigma):
                raise ValueError("uncertainty must be a number, not nan")
            self._linear = {_source_key(correlation_id): sigma} if sigma > 0.0 else {}

    # ── identity and size ────────────────────────────────────────────────────

    @property
    def uncertainty(self) -> float:
        """Standard uncertainty: the root sum of squares of the source coefficients."""
        if not self._linear:
            return 0.0
        if len(self._linear) == 1:
            return abs(next(iter(self._linear.values())))
        return math.sqrt(math.fsum(c * c for c in self._linear.values()))

    @uncertainty.setter
    def uncertainty(self, value: float) -> None:
        sigma = abs(float(value))
        current = self.uncertainty
        if sigma == 0.0:
            self._linear = {}
        elif current > 0.0:
            factor = sigma / current
            self._linear = {k: c * factor for k, c in self._linear.items()}
        else:
            self._linear = {_source_key(self._correlation_id): sigma}
        self._samples_cache = None

    @property
    def std_dev(self) -> float:
        return self.uncertainty

    @property
    def value(self) -> float:
        """Alias for nominal (API compatibility)."""
        return self.nominal

    @property
    def correlation_id(self) -> str | None:
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, name: str | None) -> None:
        # Re-key a plain source so that later values built with the same id share it.
        if len(self._linear) == 1:
            (key, coef), = self._linear.items()
            if isinstance(key, _Latent) or (isinstance(key, tuple) and key[0] == "corr"):
                self._linear = {_source_key(name): coef}
        self._correlation_id = name

    @property
    def sources(self) -> int:
        """Number of independent sources this value depends on."""
        return len(self._linear)

    @classmethod
    def from_string(cls, text: str) -> UncertainValue:
        """Parse 'value ± uncertainty' notation."""
        import re

        match = re.match(
            r"^\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*±\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*$",
            text.strip(),
        )
        if not match:
            raise ValueError(f"Invalid uncertain value format: {text!r}")
        return cls(float(match.group(1)), float(match.group(2)))

    @property
    def relative_uncertainty(self) -> float:
        """Relative uncertainty as fraction."""
        if self.nominal == 0:
            return float("inf") if self.uncertainty > 0 else 0.0
        return abs(self.uncertainty / self.nominal)

    @property
    def confidence_interval(self) -> tuple[float, float]:
        """95 percent interval bounds under the declared marginal distribution."""
        if self.distribution == "uniform":
            half_width = self.uncertainty * math.sqrt(3)
            return (self.nominal - half_width, self.nominal + half_width)
        z_score = stats.norm.ppf(0.975)
        margin = z_score * self.uncertainty
        return (self.nominal - margin, self.nominal + margin)

    def sample(self, n_samples: int = 1000) -> np.ndarray:
        """Random samples from the marginal distribution of this value."""
        if self._samples_cache is not None and len(self._samples_cache) >= n_samples:
            return self._samples_cache[:n_samples]

        sigma = self.uncertainty
        if self.distribution == "uniform":
            half_width = sigma * math.sqrt(3)
            samples = np.random.uniform(self.nominal - half_width, self.nominal + half_width, n_samples)
        elif self.distribution == "lognormal":
            mu = np.log(self.nominal)
            s = np.log(1 + sigma / self.nominal)
            samples = np.random.lognormal(mu, s, n_samples)
        elif self.distribution == "triangular":
            half_width = sigma * math.sqrt(6)
            samples = np.random.triangular(self.nominal - half_width, self.nominal, self.nominal + half_width, n_samples)
        else:
            samples = np.random.normal(self.nominal, sigma, n_samples)

        self._samples_cache = samples
        return samples

    # ── covariance between results ───────────────────────────────────────────

    def covariance_with(self, other: UncertainValue) -> float:
        """First-order covariance with another value through their shared sources."""
        if not isinstance(other, UncertainValue):
            return 0.0
        a, b = self._linear, other._linear
        if len(b) < len(a):
            a, b = b, a
        return math.fsum(c * b[k] for k, c in a.items() if k in b)

    def correlation_with(self, other: UncertainValue) -> float:
        """Pearson correlation coefficient with another value; 0 when either is exact."""
        if not isinstance(other, UncertainValue):
            return 0.0
        denominator = self.uncertainty * other.uncertainty
        if denominator == 0.0:
            return 0.0
        return max(-1.0, min(1.0, self.covariance_with(other) / denominator))

    def derivative_wrt(self, source: UncertainValue) -> float:
        """d(self)/d(source) for a source created directly with a nonzero uncertainty."""
        if not isinstance(source, UncertainValue) or len(source._linear) != 1:
            raise ValueError("derivative_wrt needs a directly declared uncertain value")
        (key, coef), = source._linear.items()
        return self._linear.get(key, 0.0) / coef

    # ── arithmetic ───────────────────────────────────────────────────────────

    @staticmethod
    def _combine(nominal: float, terms) -> UncertainValue:
        """Build a result from (operand, partial derivative) pairs with the chain rule."""
        linear: dict = {}
        for operand, partial in terms:
            if partial == 0.0 or not operand._linear:
                continue
            for key, coef in operand._linear.items():
                linear[key] = linear.get(key, 0.0) + partial * coef
        return UncertainValue(nominal, _linear=linear)

    def __add__(self, other) -> UncertainValue:
        if isinstance(other, UncertainValue):
            return self._combine(self.nominal + other.nominal, ((self, 1.0), (other, 1.0)))
        if isinstance(other, _SCALARS):
            return self._combine(self.nominal + float(other), ((self, 1.0),))
        return NotImplemented

    def __radd__(self, other) -> UncertainValue:
        return self.__add__(other)

    def __sub__(self, other) -> UncertainValue:
        if isinstance(other, UncertainValue):
            return self._combine(self.nominal - other.nominal, ((self, 1.0), (other, -1.0)))
        if isinstance(other, _SCALARS):
            return self._combine(self.nominal - float(other), ((self, 1.0),))
        return NotImplemented

    def __rsub__(self, other) -> UncertainValue:
        if isinstance(other, _SCALARS):
            return self._combine(float(other) - self.nominal, ((self, -1.0),))
        return NotImplemented

    def __mul__(self, other) -> UncertainValue:
        if isinstance(other, UncertainValue):
            return self._combine(self.nominal * other.nominal, ((self, other.nominal), (other, self.nominal)))
        if isinstance(other, _SCALARS):
            k = float(other)
            return self._combine(self.nominal * k, ((self, k),))
        return NotImplemented

    def __rmul__(self, other) -> UncertainValue:
        return self.__mul__(other)

    def __truediv__(self, other) -> UncertainValue:
        if isinstance(other, UncertainValue):
            if other.nominal == 0:
                raise ZeroDivisionError("Division by uncertain zero")
            return self._combine(self.nominal / other.nominal,
                                 ((self, 1.0 / other.nominal), (other, -self.nominal / other.nominal ** 2)))
        if isinstance(other, _SCALARS):
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            k = float(other)
            return self._combine(self.nominal / k, ((self, 1.0 / k),))
        return NotImplemented

    def __rtruediv__(self, other) -> UncertainValue:
        if isinstance(other, _SCALARS):
            if self.nominal == 0:
                raise ZeroDivisionError("Division by uncertain zero")
            k = float(other)
            return self._combine(k / self.nominal, ((self, -k / self.nominal ** 2),))
        return NotImplemented

    def __pow__(self, exponent) -> UncertainValue:
        if isinstance(exponent, UncertainValue):
            # a ** b with both uncertain: d/da = b a^(b-1), d/db = a^b ln a
            if self.nominal <= 0:
                raise ValueError("Cannot raise non-positive uncertain number to uncertain power")
            value = self.nominal ** exponent.nominal
            return self._combine(value, ((self, value * exponent.nominal / self.nominal),
                                         (exponent, value * math.log(self.nominal))))
        if not isinstance(exponent, _SCALARS):
            return NotImplemented
        if exponent == 0:
            return UncertainValue(1, 0)
        value = self.nominal ** exponent
        derivative = exponent * self.nominal ** (exponent - 1)
        if isinstance(value, complex) or isinstance(derivative, complex):
            raise ValueError("Uncertain powers must be real-valued")
        return self._combine(value, ((self, float(derivative)),))

    def __rpow__(self, base) -> UncertainValue:
        if not isinstance(base, _SCALARS):
            return NotImplemented
        if base <= 0:
            raise ValueError("Cannot raise a non-positive base to an uncertain power")
        value = float(base) ** self.nominal
        return self._combine(value, ((self, value * math.log(float(base))),))

    def __neg__(self) -> UncertainValue:
        return self._combine(-self.nominal, ((self, -1.0),))

    def __pos__(self) -> UncertainValue:
        return self._combine(self.nominal, ((self, 1.0),))

    def __abs__(self) -> UncertainValue:
        sign = -1.0 if self.nominal < 0 else 1.0
        return self._combine(abs(self.nominal), ((self, sign),))

    def __float__(self) -> float:
        return self.nominal

    def __int__(self) -> int:
        return int(self.nominal)

    def __round__(self, ndigits=None):
        return round(self.nominal, ndigits)

    @staticmethod
    def _nominal_of(other) -> float:
        return other.nominal if isinstance(other, UncertainValue) else float(other)

    def __lt__(self, other) -> bool:
        return self.nominal < self._nominal_of(other)

    def __le__(self, other) -> bool:
        return self.nominal <= self._nominal_of(other)

    def __gt__(self, other) -> bool:
        return self.nominal > self._nominal_of(other)

    def __ge__(self, other) -> bool:
        return self.nominal >= self._nominal_of(other)

    # ── elementary functions ─────────────────────────────────────────────────

    def sin(self) -> UncertainValue:
        return self._combine(math.sin(self.nominal), ((self, math.cos(self.nominal)),))

    def cos(self) -> UncertainValue:
        return self._combine(math.cos(self.nominal), ((self, -math.sin(self.nominal)),))

    def tan(self) -> UncertainValue:
        value = math.tan(self.nominal)
        return self._combine(value, ((self, 1.0 + value * value),))

    def exp(self) -> UncertainValue:
        value = math.exp(self.nominal)
        return self._combine(value, ((self, value),))

    def log(self) -> UncertainValue:
        if self.nominal <= 0:
            raise ValueError("Cannot take logarithm of non-positive uncertain number")
        return self._combine(math.log(self.nominal), ((self, 1.0 / self.nominal),))

    def log10(self) -> UncertainValue:
        if self.nominal <= 0:
            raise ValueError("Cannot take logarithm of non-positive uncertain number")
        return self._combine(math.log10(self.nominal), ((self, 1.0 / (self.nominal * math.log(10.0))),))

    def sqrt(self) -> UncertainValue:
        if self.nominal < 0:
            raise ValueError("Cannot take square root of negative uncertain number")
        if self.nominal == 0:
            return UncertainValue(0, 0)
        value = math.sqrt(self.nominal)
        return self._combine(value, ((self, 0.5 / value),))

    # ── comparison and display ───────────────────────────────────────────────

    def significantly_different_from(
        self, other: UncertainValue, sigma: float = 2.0
    ) -> bool:
        if not isinstance(other, UncertainValue):
            other = UncertainValue(other, 0.0)
        # The difference accounts for shared sources, so x against x is never significant.
        difference = self - other
        if difference.uncertainty == 0:
            return difference.nominal != 0
        return abs(difference.nominal) > sigma * difference.uncertainty

    def format(self, decimals: int = 3) -> str:
        return f"{self.nominal:.{decimals}f} ± {self.uncertainty:.{decimals}f}"

    def format_scientific(self) -> str:
        return f"{self.nominal:.3e} ± {self.uncertainty:.3e}"

    def __repr__(self) -> str:
        return f"{self.nominal} ± {self.uncertainty}"

    def __str__(self) -> str:
        return self.__repr__()


def covariance(a: UncertainValue, b: UncertainValue) -> float:
    """First-order covariance of two results through the sources they share."""
    if not isinstance(a, UncertainValue) or not isinstance(b, UncertainValue):
        return 0.0
    return a.covariance_with(b)


def correlation(a: UncertainValue, b: UncertainValue) -> float:
    """Pearson correlation of two results; 0 when either is exact."""
    if not isinstance(a, UncertainValue) or not isinstance(b, UncertainValue):
        return 0.0
    return a.correlation_with(b)


def covariance_matrix(values) -> np.ndarray:
    """First-order covariance matrix of a sequence of results."""
    values = list(values)
    matrix = np.zeros((len(values), len(values)))
    for i, a in enumerate(values):
        for j, b in enumerate(values):
            if j < i:
                matrix[i, j] = matrix[j, i]
            else:
                matrix[i, j] = covariance(a, b)
    return matrix


class CorrelationMatrix:
    """Manages correlations between uncertain variables."""

    def __init__(self):
        self.correlations: dict[tuple[str, str], float] = {}
        self.variables: dict[str, UncertainValue] = {}

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

    def propagate_correlated(self, expression: Callable, variables: list[str],
                           samples: int = 10000, *, rng=None, parallel=False, n_cores=4) -> UncertainValue:
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
            uncorr_samples = (rng if rng is not None else np.random).standard_normal((samples, n_vars))
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
            if parallel:
                from .parallel import ParallelBlock, ParallelConfig
                tasks = (functools.partial(expression, *sample) for sample in var_samples)
                results = np.array(ParallelBlock(ParallelConfig(max_workers=n_cores)).execute(tasks))
            else:
                results = np.array([expression(*sample) for sample in var_samples])

            # Calculate statistics
            mean_result = np.mean(results)
            std_result = np.std(results, ddof=1)

            return UncertainValue(mean_result, std_result)

        except np.linalg.LinAlgError:
            warnings.warn("Correlation matrix is not positive definite, using uncorrelated propagation", stacklevel=2)
            return self._propagate_uncorrelated(expression, variables, samples)

    def _propagate_uncorrelated(self, expression: Callable, variables: list[str],
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

    def __init__(self, config: UncertaintyConfig | None = None):
        self.config = config or UncertaintyConfig()
        self.correlation_matrix = CorrelationMatrix()
        self.variables = {}
        self.cache = {}

    def create_uncertain(self, nominal: float, uncertainty: float,
                        distribution: str = "normal", name: str | None = None) -> UncertainValue:
        """Create an uncertain value."""
        uval = UncertainValue(nominal, uncertainty, distribution)
        if name:
            self.variables[name] = uval
            self.correlation_matrix.add_variable(name, uval)
        return uval

    def set_correlation(self, var1: str, var2: str, correlation: float):
        """Set correlation between variables."""
        self.correlation_matrix.set_correlation(var1, var2, correlation)

    def propagate(self, expression: Callable, variables: list[str] | dict[str, UncertainValue],
                  method: PropagationMethod | None = None) -> UncertainValue:
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

    def _linear_propagation(self, expression: Callable, var_names: list[str]) -> UncertainValue:
        """First-order Taylor approximation propagation."""
        # Get nominal values
        nominals = [self.correlation_matrix.variables[name].nominal for name in var_names]

        # Evaluate function at nominal point
        f_nominal = expression(*nominals)

        # Compute partial derivatives numerically with a step relative to the
        # variable's magnitude. A fixed absolute step of 1e-8 left roundoff of
        # about one part in a million in every propagated uncertainty (measured
        # 2026-09-10 against hand-derived partials); 1e-5 * max(1, |x|) keeps
        # both truncation and roundoff below one part in 1e9 for smooth functions.
        derivatives = []

        for i, var_name in enumerate(var_names):
            h = 1e-5 * max(1.0, abs(nominals[i]))
            point_plus = nominals.copy()
            point_minus = nominals.copy()
            point_plus[i] += h
            point_minus[i] -= h

            try:
                f_plus = expression(*point_plus)
                f_minus = expression(*point_minus)
                derivative = (f_plus - f_minus) / (2 * h)
            except (ArithmeticError, ValueError):
                # One-sided difference if the expression is undefined on one side.
                try:
                    f_plus = expression(*point_plus)
                    derivative = (f_plus - f_nominal) / h
                except (ArithmeticError, ValueError):
                    try:
                        f_minus = expression(*point_minus)
                        derivative = (f_nominal - f_minus) / h
                    except (ArithmeticError, ValueError) as exc:
                        # Never report a zero derivative for a variable we could
                        # not differentiate: that would silently understate the
                        # propagated uncertainty.
                        raise ValueError(
                            f"cannot differentiate the expression with respect to {var_name!r} "
                            f"at {nominals[i]!r}: {exc}"
                        ) from exc

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
        has_explicit_correlations = any(
            self.correlation_matrix.get_correlation(a, b) != 0.0
            for i, a in enumerate(var_names) for b in var_names[i + 1:]
        )
        if has_explicit_correlations:
            # Correlations declared on the matrix are not expressible as shared sources.
            return UncertainValue(f_nominal, uncertainty)
        # Otherwise the result keeps its dependence on the inputs, so it composes with them.
        return UncertainValue._combine(
            float(f_nominal),
            ((self.correlation_matrix.variables[name], float(d)) for name, d in zip(var_names, derivatives, strict=True)),
        )

    def _monte_carlo_propagation(self, expression: Callable, var_names: list[str]) -> UncertainValue:
        """Monte Carlo uncertainty propagation."""
        return self.correlation_matrix.propagate_correlated(
            expression, var_names, self.config.samples
        )

    def _bayesian_propagation(self, expression: Callable, var_names: list[str]) -> UncertainValue:
        """Bayesian uncertainty propagation (simplified implementation)."""
        # For now, fall back to Monte Carlo
        # In a full implementation, this would use Bayesian inference
        return self._monte_carlo_propagation(expression, var_names)

    def _interval_propagation(self, expression: Callable, var_names: list[str]) -> UncertainValue:
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
            except Exception:
                pass  # Skip points where function is undefined

        if not results:
            return UncertainValue(0, float("inf"))

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

    def sensitivity_analysis(self, expression: Callable, var_names: list[str]) -> dict[str, float]:
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

def propagate_uncertainty(
    func: Callable | None = None,
    *,
    expression: Callable | None = None,
    variables: dict[str, UncertainValue] | None = None,
    method: str | None = None,
    **kwargs,
) -> UncertainValue:
    """Propagate uncertainty through a function."""
    if func is None and "function" in kwargs:
        func = kwargs.pop("function")
    func = func or expression
    if func is None:
        raise TypeError("propagate_uncertainty requires a function")

    var_map: dict[str, UncertainValue] = {}
    source = variables if variables is not None else kwargs
    for name, value in source.items():
        if isinstance(value, UncertainValue):
            var_map[name] = value
        else:
            var_map[name] = UncertainValue(float(value), 0.0)

    var_names = list(var_map.keys())

    def expr(*args: float) -> float:
        bound = {var_names[i]: args[i] for i in range(len(var_names))}
        try:
            return float(func(**bound))
        except TypeError:
            return float(func(*args))

    propagation = PropagationMethod.LINEAR
    if method in ("monte_carlo",):
        propagation = PropagationMethod.MONTE_CARLO
    elif method in ("analytical", "linear", "numerical"):
        propagation = PropagationMethod.LINEAR

    engine = UncertaintyEngine(UncertaintyConfig(method=propagation))
    return engine.propagate(expr, var_map)


def monte_carlo(
    function,
    inputs=None,
    samples=10000,
    parallel=False,
    n_cores=4,
    seed=None,
    **kwargs,
):
    if samples < 2 or n_cores < 1:
        raise ValueError("samples must be at least 2 and n_cores must be positive")
    rng = np.random.default_rng(seed)
    inputs = dict(inputs or {})
    inputs.update(kwargs)
    if not inputs:
        raise ValueError("monte_carlo requires at least one uncertain input")
    var_names = list(inputs.keys())
    matrix = CorrelationMatrix()
    for name, val in inputs.items():
        if not isinstance(val, UncertainValue):
            val = UncertainValue(float(val), 0.0)
        matrix.add_variable(name, UncertainValue(val.nominal, val.uncertainty, val.distribution))

    def expression(*args):
        bound = {var_names[i]: args[i] for i in range(len(var_names))}
        try:
            return float(function(**bound))
        except TypeError:
            return float(function(*args))

    return matrix.propagate_correlated(
        expression, var_names, samples, rng=rng, parallel=parallel, n_cores=n_cores
    )

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
                    uncertain_args[f"arg_{i}"] = arg
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
                    combined_args[int(name.split("_")[1])] = nominal_args[i]
                return func(*combined_args, **kwargs)

            engine = UncertaintyEngine(UncertaintyConfig(method=method))
            return engine.propagate(wrapper_func, uncertain_args)

        return wrapper
    return decorator


def chi_squared_test(observed, expected):
    """Chi-squared goodness-of-fit with measurement uncertainties."""

    def _nominal_and_sigma(x):
        if isinstance(x, UncertainValue):
            return x.nominal, x.uncertainty
        return float(x), 0.0

    obs_vals = []
    obs_sigmas = []
    for item in observed:
        v, s = _nominal_and_sigma(item)
        obs_vals.append(v)
        obs_sigmas.append(s)

    if isinstance(expected, (list, tuple, np.ndarray)):
        exp_vals = []
        exp_sigmas = []
        for item in expected:
            v, s = _nominal_and_sigma(item)
            exp_vals.append(v)
            exp_sigmas.append(s)
    else:
        exp_nom, exp_sigma = _nominal_and_sigma(expected)
        exp_vals = [exp_nom] * len(obs_vals)
        exp_sigmas = [exp_sigma] * len(obs_vals)

    obs = np.asarray(obs_vals, dtype=float)
    exp = np.asarray(exp_vals, dtype=float)
    sigma = np.sqrt(np.asarray(obs_sigmas, dtype=float) ** 2 + np.asarray(exp_sigmas, dtype=float) ** 2)
    sigma = np.where(sigma > 0, sigma, 1e-12)

    chi2 = float(np.sum(((obs - exp) / sigma) ** 2))
    df = max(len(obs) - 1, 1)
    p_value = float(stats.chi2.sf(chi2, df))
    return chi2, p_value


def weighted_mean(values, weights=None, *, uncertainties=None):
    """Weighted mean; supports explicit weights or inverse-variance from uncertainties."""
    if weights is None and all(isinstance(v, UncertainValue) for v in values):
        weights = [1.0 / (v.uncertainty**2) if v.uncertainty else 1.0 for v in values]
    if weights is None and uncertainties is not None:
        weights = [1.0 / (u**2) if u else 1.0 for u in uncertainties]
    if weights is None:
        raise TypeError("weighted_mean() missing required argument: 'weights'")

    v = np.asarray(
        [val.nominal if isinstance(val, UncertainValue) else float(val) for val in values],
        dtype=float,
    )
    w = np.asarray(weights, dtype=float)
    w_sum = float(np.sum(w))
    if w_sum == 0:
        raise ValueError("Sum of weights must be non-zero")

    mean = float(np.sum(w * v) / w_sum)
    combined_uncertainty = float(1.0 / np.sqrt(w_sum))
    return UncertainValue(mean, combined_uncertainty)


class MultivariateUncertain:
    """Correlated multivariate uncertain variables."""

    def __init__(
        self,
        means=None,
        uncertainties=None,
        correlations=None,
        labels=None,
        *,
        values=None,
        covariance=None,
    ):
        if means is not None:
            labels = labels or [f"x{i}" for i in range(len(means))]
            self.labels = list(labels)
            self._vars = {
                label: UncertainValue(m, u)
                for label, m, u in zip(self.labels, means, uncertainties or [], strict=False)
            }
            if correlations is not None:
                corr = np.asarray(correlations, dtype=float)
                std = np.asarray(uncertainties, dtype=float)
                self._cov = corr * np.outer(std, std)
            else:
                self._cov = np.diag(np.asarray(uncertainties, dtype=float) ** 2)
        else:
            self._vars = values or {}
            self.labels = list(self._vars.keys())
            self._cov = np.asarray(covariance) if covariance is not None else np.eye(len(self.labels))

    def __len__(self) -> int:
        return len(self._vars)

    def __getitem__(self, key: str) -> UncertainValue:
        return self._vars[key]

    def sample(self, n_samples: int) -> np.ndarray:
        n = len(self.labels)
        if n == 0:
            return np.empty((n_samples, 0))
        means = np.array([self._vars[k].nominal for k in self.labels])
        try:
            chol = np.linalg.cholesky(self._cov)
            z = np.random.standard_normal((n_samples, n))
            return means + z @ chol.T
        except np.linalg.LinAlgError:
            return np.random.multivariate_normal(means, self._cov, size=n_samples)
