"""
Symbolic mathematics engine for Synapse language
Integrates with SymPy for symbolic computation
"""

import sympy as sp
from sympy import symbols, Symbol, Function, Eq, solve, diff, integrate, limit, series
from sympy import simplify, expand, factor, collect, cancel, apart
from sympy.logic.boolalg import And, Or, Not, Implies
from sympy.stats import Normal, Uniform, Poisson, Exponential
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class SymbolicExpression:
    """Wrapper for symbolic expressions with metadata"""
    expr: sp.Expr
    variables: List[sp.Symbol]
    assumptions: Dict[str, Any] = None
    
    def __str__(self):
        return str(self.expr)
    
    def __repr__(self):
        return f"SymbolicExpression({self.expr})"
    
    def evaluate(self, **kwargs) -> Union[float, complex]:
        """Evaluate expression with given values"""
        return float(self.expr.subs(kwargs))
    
    def latex(self) -> str:
        """Get LaTeX representation"""
        return sp.latex(self.expr)
    
    def simplify(self) -> 'SymbolicExpression':
        """Simplify the expression"""
        return SymbolicExpression(
            sp.simplify(self.expr),
            self.variables,
            self.assumptions
        )
    
    def expand(self) -> 'SymbolicExpression':
        """Expand the expression"""
        return SymbolicExpression(
            sp.expand(self.expr),
            self.variables,
            self.assumptions
        )
    
    def factor(self) -> 'SymbolicExpression':
        """Factor the expression"""
        return SymbolicExpression(
            sp.factor(self.expr),
            self.variables,
            self.assumptions
        )


class SymbolicEngine:
    """Symbolic computation engine for Synapse"""
    
    def __init__(self):
        self.symbols: Dict[str, sp.Symbol] = {}
        self.functions: Dict[str, Union[sp.Function, SymbolicExpression]] = {}
        self.assumptions: Dict[str, Dict[str, Any]] = {}
        self.equations: List[sp.Eq] = []
        
        # Pre-define common symbols
        self._init_common_symbols()
    
    def _init_common_symbols(self):
        """Initialize commonly used symbols"""
        # Real variables
        for var in ['x', 'y', 'z', 't', 'r', 'θ', 'φ']:
            self.symbols[var] = sp.Symbol(var, real=True)
        
        # Complex variables
        for var in ['w', 'ζ']:
            self.symbols[var] = sp.Symbol(var, complex=True)
        
        # Integer variables
        for var in ['n', 'm', 'i', 'j', 'k']:
            self.symbols[var] = sp.Symbol(var, integer=True)
        
        # Constants
        self.symbols['π'] = sp.pi
        self.symbols['e'] = sp.E
        self.symbols['∞'] = sp.oo
        self.symbols['ι'] = sp.I  # imaginary unit
    
    def create_symbol(self, name: str, **assumptions) -> sp.Symbol:
        """Create a new symbol with assumptions"""
        symbol = sp.Symbol(name, **assumptions)
        self.symbols[name] = symbol
        self.assumptions[name] = assumptions
        return symbol
    
    def create_function(self, name: str, args: List[str], expr_str: str) -> SymbolicExpression:
        """Create a symbolic function"""
        # Parse arguments
        arg_symbols = []
        for arg in args:
            if arg not in self.symbols:
                self.symbols[arg] = sp.Symbol(arg)
            arg_symbols.append(self.symbols[arg])
        
        # Parse expression
        expr = self.parse_expression(expr_str)
        
        # Create function
        func_expr = SymbolicExpression(expr, arg_symbols)
        self.functions[name] = func_expr
        
        return func_expr
    
    def parse_expression(self, expr_str: str) -> sp.Expr:
        """Parse string expression to SymPy expression"""
        # Replace common operators
        expr_str = expr_str.replace('^', '**')
        expr_str = expr_str.replace('±', '+/-')
        
        # Parse using SymPy with local symbols
        try:
            expr = sp.sympify(expr_str, locals=self.symbols)
        except:
            # Fallback to basic parsing
            expr = sp.parse_expr(expr_str, local_dict=self.symbols)
        
        return expr
    
    def differentiate(self, expr: Union[str, sp.Expr, SymbolicExpression], 
                     var: Union[str, sp.Symbol], 
                     order: int = 1) -> SymbolicExpression:
        """Compute derivative"""
        # Parse expression if string
        if isinstance(expr, str):
            expr = self.parse_expression(expr)
        elif isinstance(expr, SymbolicExpression):
            expr = expr.expr
        
        # Parse variable if string
        if isinstance(var, str):
            var = self.symbols.get(var, sp.Symbol(var))
        
        # Compute derivative
        result = sp.diff(expr, var, order)
        
        return SymbolicExpression(result, [var])
    
    def integrate(self, expr: Union[str, sp.Expr, SymbolicExpression],
                 var: Union[str, sp.Symbol],
                 limits: Optional[Tuple[Any, Any]] = None) -> SymbolicExpression:
        """Compute integral"""
        # Parse expression if string
        if isinstance(expr, str):
            expr = self.parse_expression(expr)
        elif isinstance(expr, SymbolicExpression):
            expr = expr.expr
        
        # Parse variable if string
        if isinstance(var, str):
            var = self.symbols.get(var, sp.Symbol(var))
        
        # Compute integral
        if limits:
            result = sp.integrate(expr, (var, limits[0], limits[1]))
        else:
            result = sp.integrate(expr, var)
        
        return SymbolicExpression(result, [var])
    
    def solve_equation(self, equation: Union[str, sp.Eq], 
                      variable: Optional[Union[str, sp.Symbol]] = None) -> List[Any]:
        """Solve equation or system of equations"""
        # Parse equation if string
        if isinstance(equation, str):
            # Handle equation format "expr = value" or "expr == value"
            if '==' in equation:
                left, right = equation.split('==')
            elif '=' in equation:
                left, right = equation.split('=')
            else:
                # Assume equation equals zero
                left = equation
                right = '0'
            
            left_expr = self.parse_expression(left.strip())
            right_expr = self.parse_expression(right.strip())
            equation = sp.Eq(left_expr, right_expr)
        
        # Parse variable if string
        if isinstance(variable, str):
            variable = self.symbols.get(variable, sp.Symbol(variable))
        
        # Solve equation
        if variable:
            solutions = sp.solve(equation, variable)
        else:
            # Solve for all free symbols
            solutions = sp.solve(equation)
        
        return solutions
    
    def prove_statement(self, statement: Union[str, sp.Expr], 
                       domain: Optional[str] = None) -> Dict[str, Any]:
        """Attempt to prove a mathematical statement"""
        # Parse statement if string
        if isinstance(statement, str):
            statement = self.parse_expression(statement)
        
        result = {
            'statement': statement,
            'domain': domain,
            'proven': False,
            'counterexample': None,
            'method': None
        }
        
        try:
            # Try simplification
            simplified = sp.simplify(statement)
            
            if simplified == sp.true:
                result['proven'] = True
                result['method'] = 'simplification'
            elif simplified == sp.false:
                result['proven'] = False
                result['method'] = 'simplification'
            else:
                # Try to find counterexample for inequalities
                if statement.is_Relational:
                    # Check at specific points
                    test_points = [0, 1, -1, 2, -2, 0.5, -0.5]
                    for point in test_points:
                        try:
                            subs_dict = {s: point for s in statement.free_symbols}
                            if not statement.subs(subs_dict):
                                result['counterexample'] = subs_dict
                                result['proven'] = False
                                result['method'] = 'counterexample'
                                break
                        except:
                            pass
                
                # Try interval analysis for continuous functions
                if not result['proven'] and not result['counterexample']:
                    # This is a simplified approach
                    result['method'] = 'undecidable'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def compute_limit(self, expr: Union[str, sp.Expr, SymbolicExpression],
                     var: Union[str, sp.Symbol],
                     point: Any,
                     direction: str = '+-') -> SymbolicExpression:
        """Compute limit"""
        # Parse expression if string
        if isinstance(expr, str):
            expr = self.parse_expression(expr)
        elif isinstance(expr, SymbolicExpression):
            expr = expr.expr
        
        # Parse variable if string
        if isinstance(var, str):
            var = self.symbols.get(var, sp.Symbol(var))
        
        # Parse point
        if point == '∞' or point == 'inf':
            point = sp.oo
        elif point == '-∞' or point == '-inf':
            point = -sp.oo
        
        # Compute limit
        if direction == '+':
            result = sp.limit(expr, var, point, '+')
        elif direction == '-':
            result = sp.limit(expr, var, point, '-')
        else:
            result = sp.limit(expr, var, point)
        
        return SymbolicExpression(result, [var])
    
    def taylor_series(self, expr: Union[str, sp.Expr, SymbolicExpression],
                     var: Union[str, sp.Symbol],
                     point: Any = 0,
                     order: int = 6) -> SymbolicExpression:
        """Compute Taylor series expansion"""
        # Parse expression if string
        if isinstance(expr, str):
            expr = self.parse_expression(expr)
        elif isinstance(expr, SymbolicExpression):
            expr = expr.expr
        
        # Parse variable if string
        if isinstance(var, str):
            var = self.symbols.get(var, sp.Symbol(var))
        
        # Compute series
        result = sp.series(expr, var, point, order)
        
        return SymbolicExpression(result.removeO(), [var])
    
    def laplace_transform(self, expr: Union[str, sp.Expr, SymbolicExpression],
                         t_var: Union[str, sp.Symbol],
                         s_var: Union[str, sp.Symbol]) -> SymbolicExpression:
        """Compute Laplace transform"""
        # Parse expression if string
        if isinstance(expr, str):
            expr = self.parse_expression(expr)
        elif isinstance(expr, SymbolicExpression):
            expr = expr.expr
        
        # Parse variables if strings
        if isinstance(t_var, str):
            t_var = self.symbols.get(t_var, sp.Symbol(t_var))
        if isinstance(s_var, str):
            s_var = self.symbols.get(s_var, sp.Symbol(s_var))
        
        # Compute Laplace transform
        result = sp.laplace_transform(expr, t_var, s_var)[0]
        
        return SymbolicExpression(result, [s_var])
    
    def fourier_transform(self, expr: Union[str, sp.Expr, SymbolicExpression],
                         x_var: Union[str, sp.Symbol],
                         k_var: Union[str, sp.Symbol]) -> SymbolicExpression:
        """Compute Fourier transform"""
        # Parse expression if string
        if isinstance(expr, str):
            expr = self.parse_expression(expr)
        elif isinstance(expr, SymbolicExpression):
            expr = expr.expr
        
        # Parse variables if strings
        if isinstance(x_var, str):
            x_var = self.symbols.get(x_var, sp.Symbol(x_var))
        if isinstance(k_var, str):
            k_var = self.symbols.get(k_var, sp.Symbol(k_var))
        
        # Compute Fourier transform
        result = sp.fourier_transform(expr, x_var, k_var)
        
        return SymbolicExpression(result, [k_var])
    
    def matrix_operations(self, operation: str, *matrices) -> sp.Matrix:
        """Perform matrix operations symbolically"""
        # Convert inputs to SymPy matrices
        sympy_matrices = []
        for m in matrices:
            if isinstance(m, list):
                sympy_matrices.append(sp.Matrix(m))
            elif isinstance(m, np.ndarray):
                sympy_matrices.append(sp.Matrix(m.tolist()))
            else:
                sympy_matrices.append(m)
        
        if operation == 'multiply':
            result = sympy_matrices[0]
            for m in sympy_matrices[1:]:
                result = result * m
            return result
        
        elif operation == 'add':
            result = sympy_matrices[0]
            for m in sympy_matrices[1:]:
                result = result + m
            return result
        
        elif operation == 'determinant':
            return sympy_matrices[0].det()
        
        elif operation == 'inverse':
            return sympy_matrices[0].inv()
        
        elif operation == 'eigenvalues':
            return sympy_matrices[0].eigenvals()
        
        elif operation == 'eigenvectors':
            return sympy_matrices[0].eigenvects()
        
        elif operation == 'transpose':
            return sympy_matrices[0].T
        
        elif operation == 'trace':
            return sympy_matrices[0].trace()
        
        elif operation == 'rank':
            return sympy_matrices[0].rank()
        
        else:
            raise ValueError(f"Unknown matrix operation: {operation}")
    
    def differential_equation(self, eq_str: str, 
                            func_name: str = 'y',
                            var_name: str = 'x') -> Dict[str, Any]:
        """Solve differential equation"""
        # Create function symbol
        var = self.symbols.get(var_name, sp.Symbol(var_name))
        func = sp.Function(func_name)
        
        # Parse equation
        eq_str = eq_str.replace(f"{func_name}'", f"Derivative({func_name}({var_name}), {var_name})")
        eq_str = eq_str.replace(f"{func_name}''", f"Derivative({func_name}({var_name}), {var_name}, 2)")
        
        # Convert to SymPy equation
        eq = self.parse_expression(eq_str)
        
        # Solve ODE
        try:
            solution = sp.dsolve(eq, func(var))
            return {
                'equation': eq,
                'solution': solution,
                'general': True
            }
        except Exception as e:
            return {
                'equation': eq,
                'error': str(e)
            }
    
    def probability_distribution(self, dist_type: str, **params) -> Any:
        """Create probability distribution"""
        if dist_type == 'normal':
            mean = params.get('mean', 0)
            std = params.get('std', 1)
            var_name = params.get('var', 'X')
            return Normal(var_name, mean, std)
        
        elif dist_type == 'uniform':
            a = params.get('a', 0)
            b = params.get('b', 1)
            var_name = params.get('var', 'X')
            return Uniform(var_name, a, b)
        
        elif dist_type == 'poisson':
            lam = params.get('lambda', 1)
            var_name = params.get('var', 'X')
            return Poisson(var_name, lam)
        
        elif dist_type == 'exponential':
            rate = params.get('rate', 1)
            var_name = params.get('var', 'X')
            return Exponential(var_name, rate)
        
        else:
            raise ValueError(f"Unknown distribution type: {dist_type}")
    
    def logical_inference(self, premises: List[str], conclusion: str) -> Dict[str, Any]:
        """Perform logical inference"""
        # Parse premises
        premise_exprs = []
        for p in premises:
            # Handle implication
            if '=>' in p:
                ant, cons = p.split('=>')
                premise_exprs.append(Implies(
                    self.parse_expression(ant.strip()),
                    self.parse_expression(cons.strip())
                ))
            else:
                premise_exprs.append(self.parse_expression(p))
        
        # Parse conclusion
        conclusion_expr = self.parse_expression(conclusion)
        
        # Combine premises
        if premise_exprs:
            combined_premises = And(*premise_exprs)
        else:
            combined_premises = sp.true
        
        # Check if conclusion follows from premises
        implication = Implies(combined_premises, conclusion_expr)
        
        try:
            # Try to simplify the implication
            simplified = sp.simplify(implication)
            
            result = {
                'premises': premises,
                'conclusion': conclusion,
                'valid': simplified == sp.true,
                'implication': implication,
                'simplified': simplified
            }
        except:
            result = {
                'premises': premises,
                'conclusion': conclusion,
                'valid': None,
                'error': 'Could not determine validity'
            }
        
        return result
    
    def optimize_expression(self, expr: Union[str, sp.Expr, SymbolicExpression],
                          var: Union[str, sp.Symbol],
                          constraint: Optional[str] = None) -> Dict[str, Any]:
        """Find extrema of expression"""
        # Parse expression if string
        if isinstance(expr, str):
            expr = self.parse_expression(expr)
        elif isinstance(expr, SymbolicExpression):
            expr = expr.expr
        
        # Parse variable if string
        if isinstance(var, str):
            var = self.symbols.get(var, sp.Symbol(var))
        
        # Find critical points
        derivative = sp.diff(expr, var)
        critical_points = sp.solve(derivative, var)
        
        # Find second derivative for classification
        second_derivative = sp.diff(derivative, var)
        
        extrema = []
        for point in critical_points:
            second_deriv_value = second_derivative.subs(var, point)
            
            if second_deriv_value > 0:
                extrema.append({
                    'point': point,
                    'value': expr.subs(var, point),
                    'type': 'minimum'
                })
            elif second_deriv_value < 0:
                extrema.append({
                    'point': point,
                    'value': expr.subs(var, point),
                    'type': 'maximum'
                })
            else:
                extrema.append({
                    'point': point,
                    'value': expr.subs(var, point),
                    'type': 'inflection'
                })
        
        return {
            'expression': expr,
            'derivative': derivative,
            'critical_points': critical_points,
            'extrema': extrema
        }