"""
Advanced Type Inference System for Synapse Language
Implements Hindley-Milner type inference with extensions for scientific types
"""

from typing import Dict, List, Optional, Set, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import ast


class TypeKind(Enum):
    """Categories of types in Synapse"""
    SCALAR = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    LIST = auto()
    DICT = auto()
    OPTIONAL = auto()
    UNKNOWN = auto()
    UNCERTAIN = auto()
    TENSOR = auto()
    QUANTUM = auto()
    FUNCTION = auto()
    GENERIC = auto()
    UNION = auto()
    STRUCT = auto()


@dataclass
class Type:
    """Base type representation"""
    kind: TypeKind
    name: str = ""
    params: List['Type'] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            self.name = self.kind.name.lower()

    def __str__(self):
        if self.params:
            params_str = f"[{', '.join(str(p) for p in self.params)}]"
            return f"{self.name}{params_str}"
        return self.name

    def __hash__(self):
        return hash((self.kind, self.name, tuple(self.params)))


@dataclass
class TypeVar:
    """Type variable for polymorphic types"""
    id: int
    name: str
    constraints: Set[Type] = field(default_factory=set)

    def __str__(self):
        return f"'{self.name}"

    def __hash__(self):
        return hash(self.id)


class TypeEnvironment:
    """Type environment for tracking variable types"""

    def __init__(self, parent: Optional['TypeEnvironment'] = None):
        self.bindings: Dict[str, Type] = {}
        self.parent = parent
        self.type_vars: Dict[str, TypeVar] = {}
        self._next_var_id = 0

    def bind(self, name: str, type_: Type):
        """Bind a variable to a type"""
        self.bindings[name] = type_

    def lookup(self, name: str) -> Optional[Type]:
        """Look up a variable's type"""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def fresh_type_var(self, prefix: str = "T") -> TypeVar:
        """Create a fresh type variable"""
        var = TypeVar(self._next_var_id, f"{prefix}{self._next_var_id}")
        self._next_var_id += 1
        return var

    def child(self) -> 'TypeEnvironment':
        """Create child environment"""
        return TypeEnvironment(parent=self)


class TypeInference:
    """Hindley-Milner type inference with scientific extensions"""

    def __init__(self):
        self.env = TypeEnvironment()
        self.substitutions: Dict[TypeVar, Type] = {}
        self.constraints: List[Tuple[Type, Type]] = []
        self._init_builtin_types()

    def _init_builtin_types(self):
        """Initialize built-in types"""
        # Scalar types
        self.int_type = Type(TypeKind.INT, "int")
        self.float_type = Type(TypeKind.FLOAT, "float")
        self.bool_type = Type(TypeKind.BOOL, "bool")
        self.string_type = Type(TypeKind.STRING, "string")
        self.unknown_type = Type(TypeKind.UNKNOWN, "unknown")

        # Scientific types
        self.uncertain_type = lambda t: Type(
            TypeKind.UNCERTAIN, "uncertain", [t]
        )
        self.tensor_type = lambda t, *dims: Type(
            TypeKind.TENSOR, "tensor", [t] + list(dims)
        )
        self.quantum_type = lambda n: Type(
            TypeKind.QUANTUM, "quantum", [],
            {"qubits": n}
        )

        # Function type
        self.function_type = lambda args, ret: Type(
            TypeKind.FUNCTION, "function", args + [ret]
        )

        # Register built-in functions
        self._register_builtins()

    def _register_builtins(self):
        """Register built-in function types"""
        # Math functions
        self.env.bind("sin", self.function_type([self.float_type], self.float_type))
        self.env.bind("cos", self.function_type([self.float_type], self.float_type))
        self.env.bind("exp", self.function_type([self.float_type], self.float_type))
        self.env.bind("log", self.function_type([self.float_type], self.float_type))
        self.env.bind("sqrt", self.function_type([self.float_type], self.float_type))

        # Type constructors
        T = self.env.fresh_type_var("T")
        self.env.bind("uncertain", self.function_type([T], self.uncertain_type(T)))

    def infer(self, node: ast.AST) -> Type:
        """Infer type of an AST node"""
        method_name = f"infer_{node.__class__.__name__}"
        method = getattr(self, method_name, self.infer_generic)
        return method(node)

    def infer_generic(self, node: ast.AST) -> Type:
        """Generic inference fallback"""
        return self.unknown_type

    def infer_Constant(self, node: ast.Constant) -> Type:
        """Infer type of constant"""
        value = node.value
        if isinstance(value, bool):
            return self.bool_type
        elif isinstance(value, int):
            return self.int_type
        elif isinstance(value, float):
            return self.float_type
        elif isinstance(value, str):
            return self.string_type
        else:
            return self.env.fresh_type_var("Const")

    def infer_Name(self, node: ast.Name) -> Type:
        """Infer type of variable"""
        type_ = self.env.lookup(node.id)
        if type_ is None:
            return self.unknown_type
        if isinstance(type_, TypeVar):
            return self.apply_substitutions(type_)
        return type_

    def infer_List(self, node: ast.List) -> Type:
        """Infer homogeneous list type."""
        if not node.elts:
            elem = Type(TypeKind.GENERIC, "T")
            return Type(TypeKind.LIST, "list", [elem])
        elem_type = self.infer(node.elts[0])
        for elt in node.elts[1:]:
            self.unify(elem_type, self.infer(elt))
        return Type(TypeKind.LIST, "list", [self.apply_substitutions(elem_type)])

    def infer_Dict(self, node: ast.Dict) -> Type:
        """Infer dictionary key/value types."""
        if not node.keys or node.keys[0] is None:
            return Type(TypeKind.DICT, "dict", [
                Type(TypeKind.STRING, "str"),
                self.unknown_type,
            ])
        key_type = self.infer(node.keys[0])
        val_type = self.infer(node.values[0])
        for key, val in zip(node.keys[1:], node.values[1:], strict=False):
            if key is not None:
                self.unify(key_type, self.infer(key))
            if val is not None:
                self.unify(val_type, self.infer(val))
        return Type(
            TypeKind.DICT,
            "dict",
            [self.apply_substitutions(key_type), self.apply_substitutions(val_type)],
        )

    def infer_BinOp(self, node: ast.BinOp) -> Type:
        """Infer type of binary operation"""
        left_type = self.infer(node.left)
        right_type = self.infer(node.right)

        # Numeric operations
        if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            # Unify operand types
            self.unify(left_type, right_type)

            # Handle uncertainty propagation
            if left_type.kind == TypeKind.UNCERTAIN:
                return left_type
            elif right_type.kind == TypeKind.UNCERTAIN:
                return right_type

            # Handle tensor operations
            if left_type.kind == TypeKind.TENSOR:
                return left_type

            return left_type

        # Comparison operations
        elif isinstance(node.op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)):
            self.unify(left_type, right_type)
            return self.bool_type

        return self.env.fresh_type_var("BinOp")

    def infer_Call(self, node: ast.Call) -> Type:
        """Infer type of function call"""
        func_type = self.infer(node.func)

        # Get argument types
        arg_types = [self.infer(arg) for arg in node.args]

        # If function type is known
        if func_type.kind == TypeKind.FUNCTION:
            # Check arity
            expected_args = func_type.params[:-1]
            return_type = func_type.params[-1]

            if len(arg_types) != len(expected_args):
                raise TypeError(f"Function expects {len(expected_args)} arguments, got {len(arg_types)}")

            # Unify argument types
            for arg_type, expected in zip(arg_types, expected_args):
                self.unify(arg_type, expected)

            return return_type

        # Unknown function - create fresh type
        return_type = self.env.fresh_type_var("Return")
        self.unify(func_type, self.function_type(arg_types, return_type))
        return return_type

    def infer_If(self, node: ast.If) -> Type:
        """Infer type of if expression"""
        # Condition must be boolean
        cond_type = self.infer(node.test)
        self.unify(cond_type, self.bool_type)

        # Both branches must have same type
        then_type = self.infer_block(node.body)
        else_type = self.infer_block(node.orelse) if node.orelse else None

        if else_type:
            self.unify(then_type, else_type)

        return then_type

    def infer_For(self, node: ast.For) -> Type:
        """Infer type of for loop"""
        # Infer iterator type
        iter_type = self.infer(node.iter)

        # Bind loop variable
        if isinstance(node.target, ast.Name):
            elem_type = self.env.fresh_type_var("Elem")
            self.env.bind(node.target.id, elem_type)

        # Infer body type
        body_type = self.infer_block(node.body)

        return body_type

    def infer_function(self, node: ast.FunctionDef) -> Type:
        """Infer function type from annotations when present."""
        param_types: list[Type] = []
        for arg in node.args.args:
            if arg.annotation:
                param_types.append(self._type_from_annotation(arg.annotation))
            else:
                param_types.append(self.int_type)

        if node.returns:
            return_type = self._type_from_annotation(node.returns)
        else:
            return_type = self.infer_block(node.body)

        func_type = self.function_type(param_types, return_type)
        return Type(
            TypeKind.FUNCTION,
            "function",
            param_types + [return_type],
        )

    def _type_from_annotation(self, annotation: ast.AST) -> Type:
        if isinstance(annotation, ast.Name):
            mapping = {
                "int": self.int_type,
                "float": self.float_type,
                "str": self.string_type,
                "bool": self.bool_type,
            }
            return mapping.get(annotation.id, self.unknown_type)
        return self.unknown_type

    def infer_FunctionDef(self, node: ast.FunctionDef) -> Type:
        """Infer type of function definition"""
        # Create child environment for function scope
        func_env = self.env.child()
        old_env = self.env
        self.env = func_env

        # Bind parameter types
        param_types = []
        for arg in node.args.args:
            param_type = self.env.fresh_type_var(arg.arg)
            self.env.bind(arg.arg, param_type)
            param_types.append(param_type)

        # Infer return type from body
        return_type = self.infer_block(node.body)

        # Restore environment
        self.env = old_env

        # Create function type
        func_type = self.function_type(param_types, return_type)
        self.env.bind(node.name, func_type)

        return func_type

    def infer_block(self, stmts: List[ast.AST]) -> Type:
        """Infer type of statement block"""
        if not stmts:
            return Type(TypeKind.SCALAR, "void")

        result_type = None
        for stmt in stmts:
            result_type = self.infer(stmt)

        return result_type

    def unify(self, type1: Type, type2: Type) -> Type:
        """Unify two types and return the unified result."""
        type1 = self.apply_substitutions(type1)
        type2 = self.apply_substitutions(type2)

        if type1 == type2:
            return type1

        if isinstance(type1, TypeVar):
            self.bind_type_var(type1, type2)
            return self.apply_substitutions(type2)
        if isinstance(type2, TypeVar):
            self.bind_type_var(type2, type1)
            return self.apply_substitutions(type1)

        # Promote int to float
        if type1.kind == TypeKind.INT and type2.kind == TypeKind.FLOAT:
            return type2
        if type1.kind == TypeKind.FLOAT and type2.kind == TypeKind.INT:
            return type1

        if type1.kind == type2.kind and type1.name == type2.name:
            if len(type1.params) != len(type2.params):
                raise TypeError(f"Cannot unify {type1} with {type2}")
            for p1, p2 in zip(type1.params, type2.params):
                self.unify(p1, p2)
            return self.apply_substitutions(type1)

        raise TypeError(f"Cannot unify {type1} with {type2}")

    def bind_type_var(self, var: TypeVar, type_: Type):
        """Bind type variable to type"""
        # Occurs check
        if self.occurs(var, type_):
            raise TypeError(f"Infinite type: {var} = {type_}")

        self.substitutions[var] = type_

    def occurs(self, var: TypeVar, type_: Type) -> bool:
        """Check if type variable occurs in type"""
        if isinstance(type_, TypeVar):
            return var == type_
        return any(self.occurs(var, p) for p in type_.params)

    def apply_substitutions(self, type_: Union[Type, TypeVar]) -> Type:
        """Apply substitutions to type"""
        if isinstance(type_, TypeVar):
            if type_ in self.substitutions:
                return self.apply_substitutions(self.substitutions[type_])
            return Type(TypeKind.UNKNOWN, type_.name)

        # Apply to parameters
        new_params = [self.apply_substitutions(p) for p in type_.params]
        return Type(type_.kind, type_.name, new_params, type_.constraints)

    def infer_program(self, source: str) -> Dict[str, Type]:
        """Infer types for entire program"""
        tree = ast.parse(source)
        types = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_type = self.infer(node)
                types[node.name] = func_type
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        value_type = self.infer(node.value)
                        self.env.bind(target.id, value_type)
                        types[target.id] = value_type

        # Apply final substitutions
        for name, type_ in types.items():
            types[name] = self.apply_substitutions(type_)

        return types


class ScientificTypeChecker:
    """Type checker with scientific computing extensions"""

    def __init__(self):
        self.inference = TypeInference()

    def check_uncertainty_propagation(self, expr: ast.AST) -> bool:
        """Check if uncertainty propagates correctly"""
        type_ = self.inference.infer(expr)
        return type_.kind == TypeKind.UNCERTAIN

    def check_tensor_shapes(self, op: ast.BinOp) -> bool:
        """Check tensor shape compatibility"""
        left = self.inference.infer(op.left)
        right = self.inference.infer(op.right)

        if left.kind != TypeKind.TENSOR or right.kind != TypeKind.TENSOR:
            return True

        # Check shape compatibility
        left_shape = left.params[1:]
        right_shape = right.params[1:]

        if isinstance(op.op, ast.Add):
            return left_shape == right_shape
        elif isinstance(op.op, ast.MatMult):
            return left_shape[-1] == right_shape[0]

        return True

    def check_quantum_operations(self, call: ast.Call) -> bool:
        """Check quantum operation validity"""
        if not isinstance(call.func, ast.Name):
            return True

        func_name = call.func.id
        if func_name in ["H", "CNOT", "measure"]:
            # Check qubit arguments
            for arg in call.args:
                arg_type = self.inference.infer(arg)
                if arg_type.kind != TypeKind.QUANTUM:
                    return False

        return True


# Example usage and testing
if __name__ == "__main__":
    # Test type inference
    code = """
def calculate(x, y):
    z = x + y
    uncertain_z = uncertain(z)
    return uncertain_z

a = 10
b = 20.5
result = calculate(a, b)
"""

    inference = TypeInference()
    types = inference.infer_program(code)

    print("Type Inference Results:")
    print("=" * 40)
    for name, type_ in types.items():
        print(f"{name}: {type_}")

    # Test scientific type checking
    checker = ScientificTypeChecker()

    # Test uncertainty propagation
    uncertain_expr = ast.parse("uncertain(10.5) + 5").body[0].value
    has_uncertainty = checker.check_uncertainty_propagation(uncertain_expr)
    print(f"\nUncertainty propagation: {has_uncertainty}")

    print("\n✅ Advanced type inference system implemented!")