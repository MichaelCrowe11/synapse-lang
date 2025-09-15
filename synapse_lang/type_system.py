"""
Static type checking system for Synapse Language.

This module provides a comprehensive type system with support for:
- Primitive types (numbers, strings, booleans)
- Scientific types (uncertain values, tensors)
- Quantum types (qubits, circuits, gates)
- Composite types (lists, dictionaries, functions)
- Generic types and constraints
"""

from typing import Optional, List, Dict, Any, Union, Tuple, Set, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import math

from .errors import TypeError, SemanticError, SourceLocation


class TypeKind(Enum):
    """Categories of types in Synapse."""
    PRIMITIVE = "primitive"
    SCIENTIFIC = "scientific"
    QUANTUM = "quantum"
    COMPOSITE = "composite"
    FUNCTION = "function"
    GENERIC = "generic"
    UNKNOWN = "unknown"


@dataclass
class TypeConstraint:
    """Represents a constraint on a type."""
    name: str
    predicate: callable
    message: str

    def check(self, value: Any) -> bool:
        """Check if value satisfies this constraint."""
        try:
            return self.predicate(value)
        except:
            return False


class SynapseType(ABC):
    """Base class for all types in Synapse."""

    def __init__(self, name: str, kind: TypeKind):
        self.name = name
        self.kind = kind
        self.constraints: List[TypeConstraint] = []

    @abstractmethod
    def is_assignable_from(self, other: 'SynapseType') -> bool:
        """Check if this type can accept values of another type."""
        pass

    @abstractmethod
    def size_bytes(self) -> int:
        """Estimate memory size in bytes."""
        pass

    def add_constraint(self, constraint: TypeConstraint):
        """Add a constraint to this type."""
        self.constraints.append(constraint)

    def check_constraints(self, value: Any) -> List[str]:
        """Check all constraints and return violation messages."""
        violations = []
        for constraint in self.constraints:
            if not constraint.check(value):
                violations.append(constraint.message)
        return violations

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if not isinstance(other, SynapseType):
            return False
        return self.name == other.name and self.kind == other.kind


class PrimitiveType(SynapseType):
    """Primitive types like numbers, strings, booleans."""

    def __init__(self, name: str, python_type: type):
        super().__init__(name, TypeKind.PRIMITIVE)
        self.python_type = python_type

    def is_assignable_from(self, other: SynapseType) -> bool:
        if isinstance(other, PrimitiveType):
            return self.python_type == other.python_type
        return False

    def size_bytes(self) -> int:
        if self.python_type == int:
            return 8  # 64-bit integer
        elif self.python_type == float:
            return 8  # 64-bit float
        elif self.python_type == str:
            return 50  # Estimated average string size
        elif self.python_type == bool:
            return 1
        return 8  # Default


class UncertainType(SynapseType):
    """Type for uncertain values with error bounds."""

    def __init__(self, base_type: SynapseType):
        super().__init__(f"uncertain<{base_type.name}>", TypeKind.SCIENTIFIC)
        self.base_type = base_type

        # Add constraint for positive uncertainty
        self.add_constraint(TypeConstraint(
            "positive_uncertainty",
            lambda v: hasattr(v, 'uncertainty') and v.uncertainty >= 0,
            "Uncertainty must be non-negative"
        ))

    def is_assignable_from(self, other: SynapseType) -> bool:
        if isinstance(other, UncertainType):
            return self.base_type.is_assignable_from(other.base_type)
        # Can assign certain values to uncertain ones
        return self.base_type.is_assignable_from(other)

    def size_bytes(self) -> int:
        return self.base_type.size_bytes() + 8  # Base value + uncertainty


class TensorType(SynapseType):
    """Type for multi-dimensional arrays."""

    def __init__(self, element_type: SynapseType, shape: Optional[Tuple[int, ...]] = None):
        shape_str = f"[{','.join(map(str, shape))}]" if shape else "[?]"
        super().__init__(f"tensor<{element_type.name}>{shape_str}", TypeKind.SCIENTIFIC)
        self.element_type = element_type
        self.shape = shape

        # Add shape constraints
        if shape:
            self.add_constraint(TypeConstraint(
                "valid_shape",
                lambda v: hasattr(v, 'shape') and v.shape == shape,
                f"Tensor must have shape {shape}"
            ))

    def is_assignable_from(self, other: SynapseType) -> bool:
        if isinstance(other, TensorType):
            if not self.element_type.is_assignable_from(other.element_type):
                return False
            # Shape compatibility
            if self.shape is None or other.shape is None:
                return True  # Dynamic shapes are compatible
            return self.shape == other.shape
        return False

    def size_bytes(self) -> int:
        if self.shape:
            elements = math.prod(self.shape)
            return elements * self.element_type.size_bytes()
        return 1000  # Estimated for unknown shape


class QuantumType(SynapseType):
    """Base class for quantum types."""

    def __init__(self, name: str):
        super().__init__(name, TypeKind.QUANTUM)


class QubitType(QuantumType):
    """Type for quantum bits."""

    def __init__(self, num_qubits: Optional[int] = None):
        name = f"qubit[{num_qubits}]" if num_qubits else "qubit"
        super().__init__(name)
        self.num_qubits = num_qubits

    def is_assignable_from(self, other: SynapseType) -> bool:
        if isinstance(other, QubitType):
            if self.num_qubits is None or other.num_qubits is None:
                return True
            return self.num_qubits == other.num_qubits
        return False

    def size_bytes(self) -> int:
        n = self.num_qubits or 1
        return 2**n * 16  # Complex amplitudes for 2^n states


class CircuitType(QuantumType):
    """Type for quantum circuits."""

    def __init__(self, num_qubits: Optional[int] = None):
        name = f"circuit[{num_qubits}]" if num_qubits else "circuit"
        super().__init__(name)
        self.num_qubits = num_qubits

    def is_assignable_from(self, other: SynapseType) -> bool:
        if isinstance(other, CircuitType):
            if self.num_qubits is None or other.num_qubits is None:
                return True
            return self.num_qubits == other.num_qubits
        return False

    def size_bytes(self) -> int:
        n = self.num_qubits or 4
        return 100 * n  # Estimated gate storage


class ListType(SynapseType):
    """Type for lists/arrays."""

    def __init__(self, element_type: SynapseType):
        super().__init__(f"list<{element_type.name}>", TypeKind.COMPOSITE)
        self.element_type = element_type

    def is_assignable_from(self, other: SynapseType) -> bool:
        if isinstance(other, ListType):
            return self.element_type.is_assignable_from(other.element_type)
        return False

    def size_bytes(self) -> int:
        return 50 * self.element_type.size_bytes()  # Estimated 50 elements


class DictType(SynapseType):
    """Type for dictionaries/maps."""

    def __init__(self, key_type: SynapseType, value_type: SynapseType):
        super().__init__(f"dict<{key_type.name}, {value_type.name}>", TypeKind.COMPOSITE)
        self.key_type = key_type
        self.value_type = value_type

    def is_assignable_from(self, other: SynapseType) -> bool:
        if isinstance(other, DictType):
            return (self.key_type.is_assignable_from(other.key_type) and
                    self.value_type.is_assignable_from(other.value_type))
        return False

    def size_bytes(self) -> int:
        return 20 * (self.key_type.size_bytes() + self.value_type.size_bytes())


class FunctionType(SynapseType):
    """Type for functions."""

    def __init__(self, param_types: List[SynapseType], return_type: SynapseType):
        param_str = ", ".join(t.name for t in param_types)
        super().__init__(f"({param_str}) -> {return_type.name}", TypeKind.FUNCTION)
        self.param_types = param_types
        self.return_type = return_type

    def is_assignable_from(self, other: SynapseType) -> bool:
        if isinstance(other, FunctionType):
            if len(self.param_types) != len(other.param_types):
                return False
            # Check parameter compatibility (contravariant)
            for self_param, other_param in zip(self.param_types, other.param_types):
                if not other_param.is_assignable_from(self_param):
                    return False
            # Check return type compatibility (covariant)
            return self.return_type.is_assignable_from(other.return_type)
        return False

    def size_bytes(self) -> int:
        return 64  # Function pointer size


class GenericType(SynapseType):
    """Generic/parametric type."""

    def __init__(self, name: str, type_params: List[str]):
        super().__init__(f"{name}<{', '.join(type_params)}>", TypeKind.GENERIC)
        self.type_params = type_params
        self.concrete_types: Dict[str, SynapseType] = {}

    def instantiate(self, type_args: Dict[str, SynapseType]) -> SynapseType:
        """Create concrete instance with type arguments."""
        if set(type_args.keys()) != set(self.type_params):
            raise TypeError(f"Generic type {self.name} requires parameters: {self.type_params}")

        # Store concrete types for this instantiation
        instance = GenericType(self.name, self.type_params)
        instance.concrete_types = type_args.copy()
        return instance

    def is_assignable_from(self, other: SynapseType) -> bool:
        if isinstance(other, GenericType) and self.name == other.name:
            # Check if concrete type arguments are compatible
            for param in self.type_params:
                if param in self.concrete_types and param in other.concrete_types:
                    if not self.concrete_types[param].is_assignable_from(other.concrete_types[param]):
                        return False
            return True
        return False

    def size_bytes(self) -> int:
        if self.concrete_types:
            return sum(t.size_bytes() for t in self.concrete_types.values())
        return 64  # Default generic size


class TypeChecker:
    """Static type checker for Synapse programs."""

    def __init__(self):
        self.types: Dict[str, SynapseType] = {}
        self.variables: Dict[str, SynapseType] = {}
        self.functions: Dict[str, FunctionType] = {}
        self.errors: List[TypeError] = []

        # Initialize built-in types
        self._init_builtin_types()

    def _init_builtin_types(self):
        """Initialize built-in primitive types."""
        self.types['int'] = PrimitiveType('int', int)
        self.types['float'] = PrimitiveType('float', float)
        self.types['string'] = PrimitiveType('string', str)
        self.types['bool'] = PrimitiveType('bool', bool)

        # Scientific types
        self.types['uncertain_int'] = UncertainType(self.types['int'])
        self.types['uncertain_float'] = UncertainType(self.types['float'])

        # Quantum types
        self.types['qubit'] = QubitType()
        self.types['circuit'] = CircuitType()

    def register_type(self, name: str, type_obj: SynapseType):
        """Register a new type."""
        self.types[name] = type_obj

    def get_type(self, name: str) -> Optional[SynapseType]:
        """Get type by name."""
        return self.types.get(name)

    def infer_type(self, node: Any) -> Optional[SynapseType]:
        """Infer type of an AST node."""
        from .ast_consolidated import (
            NumberNode, StringNode, BooleanNode, IdentifierNode,
            BinaryOpNode, UnaryOpNode, UncertainValueNode,
            QuantumCircuitNode, ListNode, DictNode
        )

        if isinstance(node, NumberNode):
            if isinstance(node.value, int):
                return self.types['int']
            else:
                return self.types['float']

        elif isinstance(node, StringNode):
            return self.types['string']

        elif isinstance(node, BooleanNode):
            return self.types['bool']

        elif isinstance(node, IdentifierNode):
            return self.variables.get(node.name)

        elif isinstance(node, UncertainValueNode):
            base_type = self.infer_type(node.value)
            if base_type:
                return UncertainType(base_type)

        elif isinstance(node, BinaryOpNode):
            return self._infer_binary_op_type(node)

        elif isinstance(node, UnaryOpNode):
            return self._infer_unary_op_type(node)

        elif isinstance(node, QuantumCircuitNode):
            return CircuitType()

        elif isinstance(node, ListNode):
            if node.elements:
                element_type = self.infer_type(node.elements[0])
                if element_type:
                    return ListType(element_type)

        elif isinstance(node, DictNode):
            if node.pairs:
                key_node, value_node = node.pairs[0]
                key_type = self.infer_type(key_node)
                value_type = self.infer_type(value_node)
                if key_type and value_type:
                    return DictType(key_type, value_type)

        return None

    def _infer_binary_op_type(self, node) -> Optional[SynapseType]:
        """Infer type for binary operations."""
        left_type = self.infer_type(node.left)
        right_type = self.infer_type(node.right)

        if not left_type or not right_type:
            return None

        op = node.operator

        # Arithmetic operations
        if op in ['+', '-', '*', '/', '%', '**']:
            return self._infer_arithmetic_type(left_type, right_type, op)

        # Comparison operations
        elif op in ['==', '!=', '<', '>', '<=', '>=']:
            return self.types['bool']

        # Logical operations
        elif op in ['&&', '||']:
            if left_type == self.types['bool'] and right_type == self.types['bool']:
                return self.types['bool']

        return None

    def _infer_arithmetic_type(self, left: SynapseType, right: SynapseType, op: str) -> Optional[SynapseType]:
        """Infer type for arithmetic operations."""
        # Handle uncertain types
        if isinstance(left, UncertainType) or isinstance(right, UncertainType):
            base_left = left.base_type if isinstance(left, UncertainType) else left
            base_right = right.base_type if isinstance(right, UncertainType) else right
            result_base = self._infer_arithmetic_type(base_left, base_right, op)
            if result_base:
                return UncertainType(result_base)

        # Numeric type promotion
        if left == self.types['int'] and right == self.types['int']:
            if op == '/':
                return self.types['float']  # Division produces float
            return self.types['int']

        elif (left in [self.types['int'], self.types['float']] and
              right in [self.types['int'], self.types['float']]):
            return self.types['float']

        return None

    def _infer_unary_op_type(self, node) -> Optional[SynapseType]:
        """Infer type for unary operations."""
        operand_type = self.infer_type(node.operand)
        if not operand_type:
            return None

        op = node.operator

        if op in ['+', '-']:
            if operand_type in [self.types['int'], self.types['float']]:
                return operand_type
            elif isinstance(operand_type, UncertainType):
                return operand_type

        elif op == '!':
            return self.types['bool']

        return None

    def check_assignment(self, var_name: str, value_type: SynapseType, location: Optional[SourceLocation] = None):
        """Check if assignment is type-safe."""
        if var_name in self.variables:
            current_type = self.variables[var_name]
            if not current_type.is_assignable_from(value_type):
                self.errors.append(TypeError(
                    f"Cannot assign {value_type.name} to variable '{var_name}' of type {current_type.name}",
                    expected_type=current_type.name,
                    actual_type=value_type.name,
                    location=location
                ))
        else:
            # New variable declaration
            self.variables[var_name] = value_type

    def check_function_call(self, func_name: str, arg_types: List[SynapseType], location: Optional[SourceLocation] = None) -> Optional[SynapseType]:
        """Check function call type safety and return result type."""
        if func_name not in self.functions:
            self.errors.append(TypeError(
                f"Unknown function '{func_name}'",
                location=location
            ))
            return None

        func_type = self.functions[func_name]

        if len(arg_types) != len(func_type.param_types):
            self.errors.append(TypeError(
                f"Function '{func_name}' expects {len(func_type.param_types)} arguments, got {len(arg_types)}",
                location=location
            ))
            return None

        # Check parameter types
        for i, (expected, actual) in enumerate(zip(func_type.param_types, arg_types)):
            if not expected.is_assignable_from(actual):
                self.errors.append(TypeError(
                    f"Argument {i+1} of function '{func_name}' expects {expected.name}, got {actual.name}",
                    expected_type=expected.name,
                    actual_type=actual.name,
                    location=location
                ))

        return func_type.return_type

    def check_program(self, ast_node) -> List[TypeError]:
        """Check types for entire program."""
        self.errors = []
        self._check_node(ast_node)
        return self.errors

    def _check_node(self, node):
        """Recursively check types for AST node."""
        # This would be implemented with visitor pattern for all AST node types
        # For now, just infer the type to catch basic errors
        self.infer_type(node)

        # Recursively check child nodes
        if hasattr(node, 'children'):
            for child in node.children:
                if child:
                    self._check_node(child)

    def get_memory_usage(self) -> int:
        """Estimate memory usage of all variables."""
        return sum(var_type.size_bytes() for var_type in self.variables.values())


# Export main components
__all__ = [
    'SynapseType', 'TypeKind', 'TypeConstraint',
    'PrimitiveType', 'UncertainType', 'TensorType',
    'QuantumType', 'QubitType', 'CircuitType',
    'ListType', 'DictType', 'FunctionType', 'GenericType',
    'TypeChecker'
]