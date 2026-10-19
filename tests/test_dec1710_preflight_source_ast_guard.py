"""DEC-1710: syntax and test inventory for nested JSON preflight guards.

Static, offline AST checks, without importing the protected source reviewer.
"""
import ast
from pathlib import Path
import unittest


class ParserPreflightSourceMethodIntegrityTests(unittest.TestCase):
    def test_preflight_modules_parse_and_keep_unique_test_methods(self):
        root = Path(__file__).resolve().parent
        expected = {
            "test_dec1707_json_preflight_skips_nested_review.py": 37,
            "test_dec1708_lone_surrogate_preflight.py": 49,
            "test_dec1709_valid_astral_preflight.py": 25,
        }
        seen = set()
        total = 0
        for filename, count in sorted(expected.items()):
            path = root / filename
            module = ast.parse(path.read_text(encoding="utf-8"),
                               filename=str(path))
            methods = []
            for cls in module.body:
                if not isinstance(cls, ast.ClassDef):
                    continue
                methods.extend(
                    item.name for item in cls.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name.startswith("test_"))
            self.assertEqual(len(methods), count, filename)
            self.assertEqual(len(set(methods)), count, filename)
            for method in methods:
                self.assertNotIn(method, seen)
                seen.add(method)
            total += len(methods)
        self.assertEqual(total, 111)
        self.assertEqual(len(seen), 111)
