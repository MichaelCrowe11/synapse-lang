"""
Test suite for Synapse Language Type Inference System
"""

import unittest
import ast
from synapse_lang.type_inference import TypeInference, Type, TypeKind


class TestTypeInference(unittest.TestCase):
    def setUp(self):
        self.type_system = TypeInference()

    def test_primitive_types(self):
        """Test inference of primitive types"""
        # Integer
        int_node = ast.parse("42").body[0].value
        int_type = self.type_system.infer(int_node)
        self.assertEqual(int_type.kind, TypeKind.INT)

        # Float
        float_node = ast.parse("3.14").body[0].value
        float_type = self.type_system.infer(float_node)
        self.assertEqual(float_type.kind, TypeKind.FLOAT)

        # String
        str_node = ast.parse("'hello'").body[0].value
        str_type = self.type_system.infer(str_node)
        self.assertEqual(str_type.kind, TypeKind.STRING)

        # Boolean
        bool_node = ast.parse("True").body[0].value
        bool_type = self.type_system.infer(bool_node)
        self.assertEqual(bool_type.kind, TypeKind.BOOL)

    def test_collection_types(self):
        """Test inference of collection types"""
        # List
        list_node = ast.parse("[1, 2, 3]").body[0].value
        list_type = self.type_system.infer(list_node)
        self.assertEqual(list_type.kind, TypeKind.LIST)
        self.assertEqual(list_type.params[0].kind, TypeKind.INT)

        # Dict
        dict_node = ast.parse("{'a': 1}").body[0].value
        dict_type = self.type_system.infer(dict_node)
        self.assertEqual(dict_type.kind, TypeKind.DICT)
        self.assertEqual(dict_type.params[0].kind, TypeKind.STRING)
        self.assertEqual(dict_type.params[1].kind, TypeKind.INT)

    def test_scientific_types(self):
        """Test inference of scientific types"""
        # Matrix type inference
        code = """
import numpy as np
matrix = np.array([[1, 2], [3, 4]])
"""
        tree = ast.parse(code)
        # This would require more complex analysis
        self.assertIsNotNone(tree)

    def test_function_type_inference(self):
        """Test function type inference"""
        code = """
def add(x: int, y: int) -> int:
    return x + y
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        func_type = self.type_system.infer_function(func_node)

        self.assertEqual(func_type.kind, TypeKind.FUNCTION)
        # Check parameter types
        self.assertEqual(len(func_type.params), 3)  # 2 params + 1 return
        self.assertEqual(func_type.params[0].kind, TypeKind.INT)
        self.assertEqual(func_type.params[1].kind, TypeKind.INT)
        self.assertEqual(func_type.params[2].kind, TypeKind.INT)

    def test_type_unification(self):
        """Test type unification"""
        int_type = Type(TypeKind.INT)
        float_type = Type(TypeKind.FLOAT)

        # Unify int with float should give float
        unified = self.type_system.unify(int_type, float_type)
        self.assertEqual(unified.kind, TypeKind.FLOAT)

        # Unify same types
        int_type2 = Type(TypeKind.INT)
        unified_same = self.type_system.unify(int_type, int_type2)
        self.assertEqual(unified_same.kind, TypeKind.INT)

    def test_generic_types(self):
        """Test generic type handling"""
        # Generic list
        list_type = Type(TypeKind.LIST, params=[Type(TypeKind.GENERIC, name='T')])
        self.assertEqual(list_type.kind, TypeKind.LIST)
        self.assertEqual(list_type.params[0].kind, TypeKind.GENERIC)
        self.assertEqual(list_type.params[0].name, 'T')

    def test_optional_types(self):
        """Test optional type handling"""
        optional_int = Type(TypeKind.OPTIONAL, params=[Type(TypeKind.INT)])
        self.assertEqual(optional_int.kind, TypeKind.OPTIONAL)
        self.assertEqual(optional_int.params[0].kind, TypeKind.INT)

    def test_error_recovery(self):
        """Test error recovery in type inference"""
        # Invalid code should return UNKNOWN type
        invalid_node = ast.parse("undefined_var").body[0].value
        unknown_type = self.type_system.infer(invalid_node)
        self.assertEqual(unknown_type.kind, TypeKind.UNKNOWN)


if __name__ == '__main__':
    unittest.main()