"""SymbolicEngine - Advanced symbolic mathematics for Synapse language."""

import sympy as sp
from sympy import symbols, Function, Eq, solve, diff, integrate, limit, series
from sympy import simplify, expand, factor, cancel, apart, together
from sympy import Matrix, det, eigenvals, eigenvects
from sympy.logic import satisfiable, And, Or, Not, Implies, Equivalent
from sympy.stats import Normal, Uniform, density, expectation, variance
from typing import Union, List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
import warnings

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class SymbolicType(Enum):
    """Types of symbolic expressions."""
    EXPRESSION = "expression"
    EQUATION = "equation"
    INEQUALITY = "inequality" 
    FUNCTION = "function"
    MATRIX = "matrix"
    LOGIC = "logic"
    PROBABILITY = "probability"


@dataclass
class SymbolicConfig:
    """Configuration for symbolic engine."""
    auto_simplify: bool = True
    numerical_precision: int = 50
    symbolic_timeout: int = 30  # seconds
    plot_backend: str = "matplotlib"
    assumptions_enabled: bool = True
    cache_results: bool = True


class SymbolicExpression:
    """Wrapper for SymPy expressions with enhanced functionality."""
    
    def __init__(self, expr: Union[str, sp.Expr], variables: Optional[List[str]] = None):
        if isinstance(expr, str):
            # Parse string expression
            if variables:
                local_dict = {var: sp.Symbol(var) for var in variables}
                self.expr = sp.sympify(expr, locals=local_dict)
            else:
                self.expr = sp.sympify(expr)
        else:
            self.expr = expr
            
        self.variables = list(self.expr.free_symbols) if not variables else variables
        self._latex_cache = None
        
    @property
    def latex(self) -> str:
        """LaTeX representation of the expression."""
        if self._latex_cache is None:
            self._latex_cache = sp.latex(self.expr)
        return self._latex_cache
    
    @property 
    def complexity(self) -> int:
        """Measure of expression complexity."""
        return sp.count_ops(self.expr)
    
    def simplify(self) -> 'SymbolicExpression':
        """Simplify the expression."""
        return SymbolicExpression(sp.simplify(self.expr))
    
    def expand(self) -> 'SymbolicExpression':
        """Expand the expression."""
        return SymbolicExpression(sp.expand(self.expr))
    
    def factor(self) -> 'SymbolicExpression':
        """Factor the expression."""
        return SymbolicExpression(sp.factor(self.expr))
    
    def substitute(self, substitutions: Dict[str, Union[float, str, 'SymbolicExpression']]) -> 'SymbolicExpression':
        """Substitute values into the expression."""
        subs_dict = {}
        for var, value in substitutions.items():
            if isinstance(value, SymbolicExpression):
                subs_dict[sp.Symbol(var)] = value.expr
            elif isinstance(value, str):
                subs_dict[sp.Symbol(var)] = sp.sympify(value)
            else:
                subs_dict[sp.Symbol(var)] = value
        
        return SymbolicExpression(self.expr.subs(subs_dict))
    
    def differentiate(self, variable: str, order: int = 1) -> 'SymbolicExpression':
        """Differentiate with respect to a variable."""
        var = sp.Symbol(variable)
        return SymbolicExpression(sp.diff(self.expr, var, order))
    
    def integrate(self, variable: str, limits: Optional[Tuple[float, float]] = None) -> 'SymbolicExpression':
        """Integrate with respect to a variable."""
        var = sp.Symbol(variable)
        if limits:
            result = sp.integrate(self.expr, (var, limits[0], limits[1]))
        else:
            result = sp.integrate(self.expr, var)
        return SymbolicExpression(result)
    
    def limit(self, variable: str, point: Union[float, str], direction: str = "both") -> 'SymbolicExpression':
        """Compute limit as variable approaches point."""
        var = sp.Symbol(variable)
        point_val = sp.sympify(point) if isinstance(point, str) else point
        
        if direction == "left":
            result = sp.limit(self.expr, var, point_val, '-')
        elif direction == "right":
            result = sp.limit(self.expr, var, point_val, '+')
        else:
            result = sp.limit(self.expr, var, point_val)
            
        return SymbolicExpression(result)
    
    def series_expansion(self, variable: str, point: float = 0, order: int = 6) -> 'SymbolicExpression':
        """Taylor series expansion around a point."""
        var = sp.Symbol(variable)
        result = sp.series(self.expr, var, point, order).removeO()
        return SymbolicExpression(result)
    
    def solve_for(self, variable: str) -> List['SymbolicExpression']:
        """Solve equation for a variable."""
        var = sp.Symbol(variable)
        solutions = sp.solve(self.expr, var)
        return [SymbolicExpression(sol) for sol in solutions]
    
    def evaluate(self, substitutions: Dict[str, float]) -> float:
        """Evaluate expression numerically."""
        subs_dict = {sp.Symbol(var): value for var, value in substitutions.items()}
        result = self.expr.subs(subs_dict)
        
        if result.is_real:
            return float(result)
        elif result.is_complex:
            return complex(result)
        else:
            raise ValueError(f"Cannot evaluate expression numerically: {result}")
    
    def lambdify(self, variables: Optional[List[str]] = None) -> Callable:
        """Convert to numerical function."""
        vars_to_use = variables or [str(s) for s in self.expr.free_symbols]
        var_symbols = [sp.Symbol(var) for var in vars_to_use]
        return sp.lambdify(var_symbols, self.expr, 'numpy')
    
    def plot(self, variable: str, range_tuple: Tuple[float, float], 
             num_points: int = 1000, **kwargs) -> None:
        """Plot the expression."""
        if not MATPLOTLIB_AVAILABLE:
            warnings.warn("Matplotlib not available for plotting")
            return
            
        var = sp.Symbol(variable)
        func = sp.lambdify(var, self.expr, 'numpy')
        
        x_vals = np.linspace(range_tuple[0], range_tuple[1], num_points)
        y_vals = func(x_vals)
        
        plt.figure(figsize=kwargs.get('figsize', (10, 6)))
        plt.plot(x_vals, y_vals, label=str(self.expr), **kwargs)
        plt.xlabel(variable)
        plt.ylabel(f'f({variable})')
        plt.title(f'Plot of {self.expr}')
        plt.grid(True)
        plt.legend()
        plt.show()
    
    def __add__(self, other) -> 'SymbolicExpression':
        if isinstance(other, SymbolicExpression):
            return SymbolicExpression(self.expr + other.expr)
        return SymbolicExpression(self.expr + other)
    
    def __radd__(self, other) -> 'SymbolicExpression':
        return SymbolicExpression(other + self.expr)
    
    def __sub__(self, other) -> 'SymbolicExpression':
        if isinstance(other, SymbolicExpression):
            return SymbolicExpression(self.expr - other.expr)
        return SymbolicExpression(self.expr - other)
    
    def __rsub__(self, other) -> 'SymbolicExpression':
        return SymbolicExpression(other - self.expr)
    
    def __mul__(self, other) -> 'SymbolicExpression':
        if isinstance(other, SymbolicExpression):
            return SymbolicExpression(self.expr * other.expr)
        return SymbolicExpression(self.expr * other)
    
    def __rmul__(self, other) -> 'SymbolicExpression':
        return SymbolicExpression(other * self.expr)
    
    def __truediv__(self, other) -> 'SymbolicExpression':
        if isinstance(other, SymbolicExpression):
            return SymbolicExpression(self.expr / other.expr)
        return SymbolicExpression(self.expr / other)
    
    def __rtruediv__(self, other) -> 'SymbolicExpression':
        return SymbolicExpression(other / self.expr)
    
    def __pow__(self, other) -> 'SymbolicExpression':
        if isinstance(other, SymbolicExpression):
            return SymbolicExpression(self.expr ** other.expr)
        return SymbolicExpression(self.expr ** other)
    
    def __eq__(self, other) -> 'SymbolicEquation':
        if isinstance(other, SymbolicExpression):
            return SymbolicEquation(sp.Eq(self.expr, other.expr))
        return SymbolicEquation(sp.Eq(self.expr, other))
    
    def __repr__(self) -> str:
        return str(self.expr)
    
    def __str__(self) -> str:
        return str(self.expr)


class SymbolicEquation:
    """Represents a symbolic equation."""
    
    def __init__(self, equation: Union[sp.Eq, str]):
        if isinstance(equation, str):
            # Parse equation string (e.g., "x^2 + y^2 = 1")
            if '=' in equation:
                left, right = equation.split('=', 1)
                self.equation = sp.Eq(sp.sympify(left.strip()), sp.sympify(right.strip()))
            else:
                # Assume equation equals zero
                self.equation = sp.Eq(sp.sympify(equation), 0)
        else:
            self.equation = equation
    
    @property
    def lhs(self) -> SymbolicExpression:
        """Left-hand side of equation."""
        return SymbolicExpression(self.equation.lhs)
    
    @property
    def rhs(self) -> SymbolicExpression:
        """Right-hand side of equation."""
        return SymbolicExpression(self.equation.rhs)
    
    def solve(self, variables: Optional[List[str]] = None) -> Dict[str, List[SymbolicExpression]]:
        """Solve the equation for specified variables."""
        if variables is None:
            variables = [str(s) for s in self.equation.free_symbols]
        
        solutions = {}
        for var in variables:
            var_symbol = sp.Symbol(var)
            sols = sp.solve(self.equation, var_symbol)
            solutions[var] = [SymbolicExpression(sol) for sol in sols]
        
        return solutions
    
    def is_identity(self) -> bool:
        """Check if equation is an identity."""
        return sp.simplify(self.equation.lhs - self.equation.rhs) == 0
    
    def substitute(self, substitutions: Dict[str, Union[float, str, SymbolicExpression]]) -> 'SymbolicEquation':
        """Substitute values into the equation."""
        subs_dict = {}
        for var, value in substitutions.items():
            if isinstance(value, SymbolicExpression):
                subs_dict[sp.Symbol(var)] = value.expr
            elif isinstance(value, str):
                subs_dict[sp.Symbol(var)] = sp.sympify(value)
            else:
                subs_dict[sp.Symbol(var)] = value
        
        return SymbolicEquation(self.equation.subs(subs_dict))
    
    def __repr__(self) -> str:
        return str(self.equation)


class SymbolicMatrix:
    """Symbolic matrix operations."""
    
    def __init__(self, matrix: Union[List[List], sp.Matrix, str]):
        if isinstance(matrix, str):
            # Parse matrix string representation
            self.matrix = sp.Matrix(sp.sympify(matrix))
        elif isinstance(matrix, list):
            self.matrix = sp.Matrix(matrix)
        else:
            self.matrix = matrix
    
    @property
    def shape(self) -> Tuple[int, int]:
        """Matrix dimensions."""
        return self.matrix.shape
    
    def determinant(self) -> SymbolicExpression:
        """Calculate determinant."""
        return SymbolicExpression(self.matrix.det())
    
    def trace(self) -> SymbolicExpression:
        """Calculate trace."""
        return SymbolicExpression(self.matrix.trace())
    
    def transpose(self) -> 'SymbolicMatrix':
        """Matrix transpose."""
        return SymbolicMatrix(self.matrix.T)
    
    def inverse(self) -> 'SymbolicMatrix':
        """Matrix inverse."""
        return SymbolicMatrix(self.matrix.inv())
    
    def eigenvalues(self) -> List[SymbolicExpression]:
        """Calculate eigenvalues."""
        evals = self.matrix.eigenvals()
        return [SymbolicExpression(eval_expr) for eval_expr in evals.keys()]
    
    def eigenvectors(self) -> List[Tuple[SymbolicExpression, int, List[SymbolicMatrix]]]:
        """Calculate eigenvectors."""
        evects = self.matrix.eigenvects()
        result = []
        for eval_expr, multiplicity, vects in evects:
            eval_sym = SymbolicExpression(eval_expr)
            vects_sym = [SymbolicMatrix(v) for v in vects]
            result.append((eval_sym, multiplicity, vects_sym))
        return result
    
    def __add__(self, other) -> 'SymbolicMatrix':
        if isinstance(other, SymbolicMatrix):
            return SymbolicMatrix(self.matrix + other.matrix)
        return SymbolicMatrix(self.matrix + other)
    
    def __sub__(self, other) -> 'SymbolicMatrix':
        if isinstance(other, SymbolicMatrix):
            return SymbolicMatrix(self.matrix - other.matrix)
        return SymbolicMatrix(self.matrix - other)
    
    def __mul__(self, other) -> 'SymbolicMatrix':
        if isinstance(other, SymbolicMatrix):
            return SymbolicMatrix(self.matrix * other.matrix)
        return SymbolicMatrix(self.matrix * other)
    
    def __repr__(self) -> str:
        return str(self.matrix)


class LogicalExpression:
    """Symbolic logical expressions."""
    
    def __init__(self, expr: Union[str, sp.Basic]):
        if isinstance(expr, str):
            # Parse logical expression
            # Convert common logical operators
            expr = expr.replace('&&', ' & ').replace('||', ' | ')
            expr = expr.replace('!', '~').replace('^', ' ^ ')
            self.expr = sp.sympify(expr)
        else:
            self.expr = expr
    
    def is_satisfiable(self) -> bool:
        """Check if expression is satisfiable."""
        return sp.satisfiable(self.expr) is not False
    
    def is_tautology(self) -> bool:
        """Check if expression is a tautology."""
        return sp.satisfiable(~self.expr) is False
    
    def simplify(self) -> 'LogicalExpression':
        """Simplify logical expression."""
        return LogicalExpression(sp.simplify_logic(self.expr))
    
    def to_cnf(self) -> 'LogicalExpression':
        """Convert to conjunctive normal form."""
        return LogicalExpression(sp.to_cnf(self.expr))
    
    def to_dnf(self) -> 'LogicalExpression':
        """Convert to disjunctive normal form."""
        return LogicalExpression(sp.to_dnf(self.expr))
    
    def __and__(self, other) -> 'LogicalExpression':
        if isinstance(other, LogicalExpression):
            return LogicalExpression(sp.And(self.expr, other.expr))
        return LogicalExpression(sp.And(self.expr, other))
    
    def __or__(self, other) -> 'LogicalExpression':
        if isinstance(other, LogicalExpression):
            return LogicalExpression(sp.Or(self.expr, other.expr))
        return LogicalExpression(sp.Or(self.expr, other))
    
    def __invert__(self) -> 'LogicalExpression':
        return LogicalExpression(sp.Not(self.expr))
    
    def __repr__(self) -> str:
        return str(self.expr)


class SymbolicEngine:
    """Main symbolic mathematics engine."""
    
    def __init__(self, config: Optional[SymbolicConfig] = None):
        self.config = config or SymbolicConfig()
        self.variables = {}
        self.functions = {}
        self.equations = {}
        self.cache = {} if self.config.cache_results else None
        
        # Set global SymPy settings
        if self.config.auto_simplify:
            sp.init_printing()
        
    def symbol(self, name: str, **assumptions) -> SymbolicExpression:
        """Create a symbolic variable."""
        if self.config.assumptions_enabled:
            var = sp.Symbol(name, **assumptions)
        else:
            var = sp.Symbol(name)
        
        self.variables[name] = var
        return SymbolicExpression(var)
    
    def symbols(self, names: Union[str, List[str]], **assumptions) -> Union[SymbolicExpression, List[SymbolicExpression]]:
        """Create multiple symbolic variables."""
        if isinstance(names, str):
            if ' ' in names:
                names = names.split()
            else:
                names = [names]
        
        if len(names) == 1:
            return self.symbol(names[0], **assumptions)
        
        return [self.symbol(name, **assumptions) for name in names]
    
    def function(self, name: str, *args: str) -> SymbolicExpression:
        """Create a symbolic function."""
        arg_symbols = [sp.Symbol(arg) for arg in args]
        func = sp.Function(name)(*arg_symbols)
        self.functions[name] = func
        return SymbolicExpression(func)
    
    def expression(self, expr: Union[str, sp.Expr], variables: Optional[List[str]] = None) -> SymbolicExpression:
        """Create a symbolic expression."""
        return SymbolicExpression(expr, variables)
    
    def equation(self, eq: Union[str, sp.Eq]) -> SymbolicEquation:
        """Create a symbolic equation."""
        return SymbolicEquation(eq)
    
    def matrix(self, data: Union[List[List], str]) -> SymbolicMatrix:
        """Create a symbolic matrix."""
        return SymbolicMatrix(data)
    
    def logical(self, expr: Union[str, sp.Basic]) -> LogicalExpression:
        """Create a logical expression."""
        return LogicalExpression(expr)
    
    # Mathematical operations
    def differentiate(self, expr: Union[SymbolicExpression, str], 
                     variable: str, order: int = 1) -> SymbolicExpression:
        """Differentiate expression."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        
        return expr.differentiate(variable, order)
    
    def integrate(self, expr: Union[SymbolicExpression, str], 
                  variable: str, limits: Optional[Tuple[float, float]] = None) -> SymbolicExpression:
        """Integrate expression."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        
        return expr.integrate(variable, limits)
    
    def solve(self, equations: Union[SymbolicEquation, List[SymbolicEquation], str], 
              variables: Optional[List[str]] = None) -> Dict[str, List[SymbolicExpression]]:
        """Solve equations."""
        if isinstance(equations, str):
            equations = SymbolicEquation(equations)
        
        if isinstance(equations, SymbolicEquation):
            return equations.solve(variables)
        
        # Multiple equations
        eq_list = [eq.equation for eq in equations]
        if variables is None:
            all_symbols = set()
            for eq in eq_list:
                all_symbols.update(eq.free_symbols)
            variables = [str(s) for s in all_symbols]
        
        var_symbols = [sp.Symbol(var) for var in variables]
        solutions = sp.solve(eq_list, var_symbols)
        
        # Format results
        result = {}
        if isinstance(solutions, dict):
            for var_sym, sol in solutions.items():
                result[str(var_sym)] = [SymbolicExpression(sol)]
        elif isinstance(solutions, list):
            for i, sol_dict in enumerate(solutions):
                for var_sym, sol in sol_dict.items():
                    var_name = str(var_sym)
                    if var_name not in result:
                        result[var_name] = []
                    result[var_name].append(SymbolicExpression(sol))
        
        return result
    
    def limit(self, expr: Union[SymbolicExpression, str], 
              variable: str, point: Union[float, str]) -> SymbolicExpression:
        """Compute limit."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        
        return expr.limit(variable, point)
    
    def series(self, expr: Union[SymbolicExpression, str], 
               variable: str, point: float = 0, order: int = 6) -> SymbolicExpression:
        """Taylor series expansion."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        
        return expr.series_expansion(variable, point, order)
    
    # Simplification operations
    def simplify(self, expr: Union[SymbolicExpression, str]) -> SymbolicExpression:
        """Simplify expression."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        return expr.simplify()
    
    def expand(self, expr: Union[SymbolicExpression, str]) -> SymbolicExpression:
        """Expand expression."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        return expr.expand()
    
    def factor(self, expr: Union[SymbolicExpression, str]) -> SymbolicExpression:
        """Factor expression."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        return expr.factor()
    
    # Special functions
    def create_polynomial(self, coefficients: List[float], variable: str = 'x') -> SymbolicExpression:
        """Create polynomial from coefficients."""
        x = sp.Symbol(variable)
        poly = sum(coeff * x**i for i, coeff in enumerate(coefficients))
        return SymbolicExpression(poly)
    
    def partial_fractions(self, expr: Union[SymbolicExpression, str], 
                         variable: str = 'x') -> SymbolicExpression:
        """Partial fraction decomposition."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        
        var = sp.Symbol(variable)
        result = sp.apart(expr.expr, var)
        return SymbolicExpression(result)
    
    def trigsimp(self, expr: Union[SymbolicExpression, str]) -> SymbolicExpression:
        """Simplify trigonometric expressions."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        
        result = sp.trigsimp(expr.expr)
        return SymbolicExpression(result)
    
    # Probability and statistics
    def normal_distribution(self, mean: Union[float, SymbolicExpression], 
                           std: Union[float, SymbolicExpression], 
                           variable: str = 'X') -> SymbolicExpression:
        """Create normal distribution."""
        if isinstance(mean, SymbolicExpression):
            mean = mean.expr
        if isinstance(std, SymbolicExpression):
            std = std.expr
        
        X = sp.Symbol(variable)
        dist = Normal(variable, mean, std)
        return SymbolicExpression(density(dist)(X))
    
    def expectation(self, expr: Union[SymbolicExpression, str], 
                   distribution: str = "normal", **params) -> SymbolicExpression:
        """Calculate expectation of expression."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        
        # For now, return symbolic expectation
        # In full implementation, would handle specific distributions
        return SymbolicExpression(f"E[{expr.expr}]")
    
    # Utility methods
    def latex(self, expr: Union[SymbolicExpression, str]) -> str:
        """Convert to LaTeX."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        return expr.latex
    
    def lambdify(self, expr: Union[SymbolicExpression, str], 
                variables: Optional[List[str]] = None) -> Callable:
        """Convert to numerical function."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        return expr.lambdify(variables)
    
    def plot(self, expr: Union[SymbolicExpression, str], 
             variable: str, range_tuple: Tuple[float, float], **kwargs) -> None:
        """Plot expression."""
        if isinstance(expr, str):
            expr = SymbolicExpression(expr)
        expr.plot(variable, range_tuple, **kwargs)
    
    # Proof assistance
    def prove(self, statement: Union[SymbolicEquation, LogicalExpression, str]) -> bool:
        """Attempt to prove a mathematical statement."""
        if isinstance(statement, str):
            # Try to parse as equation first, then logical
            try:
                statement = SymbolicEquation(statement)
                return statement.is_identity()
            except:
                statement = LogicalExpression(statement)
                return statement.is_tautology()
        
        elif isinstance(statement, SymbolicEquation):
            return statement.is_identity()
        
        elif isinstance(statement, LogicalExpression):
            return statement.is_tautology()
        
        return False
    
    def disprove(self, statement: Union[SymbolicEquation, LogicalExpression, str]) -> bool:
        """Attempt to disprove a mathematical statement."""
        if isinstance(statement, str):
            try:
                statement = LogicalExpression(statement)
                return not statement.is_satisfiable()
            except:
                return False
        
        elif isinstance(statement, LogicalExpression):
            return not statement.is_satisfiable()
        
        return False


# High-level convenience functions
def symbolic_var(name: str, **assumptions) -> SymbolicExpression:
    """Create symbolic variable."""
    engine = SymbolicEngine()
    return engine.symbol(name, **assumptions)

def symbolic_vars(*names: str, **assumptions) -> List[SymbolicExpression]:
    """Create multiple symbolic variables."""
    engine = SymbolicEngine()
    return [engine.symbol(name, **assumptions) for name in names]

def symbolic_function(name: str, *args: str) -> SymbolicExpression:
    """Create symbolic function."""
    engine = SymbolicEngine()
    return engine.function(name, *args)

# Mathematical constants and functions
def create_constants_engine() -> SymbolicEngine:
    """Create engine with common mathematical constants."""
    engine = SymbolicEngine()
    
    # Add common constants
    engine.variables['pi'] = sp.pi
    engine.variables['e'] = sp.E
    engine.variables['i'] = sp.I
    engine.variables['oo'] = sp.oo  # infinity
    
    return engine