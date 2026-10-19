"""DEC-1702: static integrity check for numeric and precedence test modules.

Only reads source text from this checkout; no test imports or external I/O.
"""
import ast
from pathlib import Path
import unittest


class NumericIngressModuleSourceGuardTests(unittest.TestCase):
    def test_numeric_ingress_regression_modules_have_unique_methods(self):
        root = Path(__file__).resolve().parent
        expected = {
            "test_dec1699_nested_grammar_precedence_forged_evidence.py": 97,
            "test_dec1700_integer_digit_boundaries_array_evidence.py": 25,
            "test_dec1701_float_token_length_array_evidence.py": 25,
        }
        across = set()
        total = 0
        for name, expected_count in sorted(expected.items()):
            path = root / name
            module = ast.parse(path.read_text(encoding="utf-8"),
                               filename=str(path))
            methods = [
                item.name
                for cls in module.body if isinstance(cls, ast.ClassDef)
                for item in cls.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name.startswith("test_")
            ]
            self.assertEqual(len(methods), expected_count, name)
            self.assertEqual(len(set(methods)), expected_count, name)
            for method in methods:
                self.assertNotIn(method, across)
                across.add(method)
            total += len(methods)
        self.assertEqual(total, 147)
        self.assertEqual(len(across), total)
