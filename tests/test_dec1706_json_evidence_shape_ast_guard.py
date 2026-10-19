"""DEC-1706: static AST and method identity guard for evidence-shape tests.

No imported test modules or external/protected artifacts.
"""
import ast
from pathlib import Path
import unittest


class EvidenceShapeRegressionAstGuardTests(unittest.TestCase):
    def test_order_type_cardinality_modules_parse_with_unique_methods(self):
        root = Path(__file__).resolve().parent
        expected = {
            "test_dec1703_json_nested_member_order_evidence.py": 37,
            "test_dec1704_json_array_element_type_parity.py": 37,
            "test_dec1705_json_array_cardinality_review_parity.py": 31,
        }
        unique = set()
        count = 0
        for filename, expected_methods in sorted(expected.items()):
            path = root / filename
            parsed = ast.parse(path.read_text(encoding="utf-8"),
                               filename=str(path))
            methods = []
            for cls in parsed.body:
                if not isinstance(cls, ast.ClassDef):
                    continue
                methods.extend(
                    member.name for member in cls.body
                    if (isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and member.name.startswith("test_")))
            self.assertEqual(len(methods), expected_methods, filename)
            self.assertEqual(len(set(methods)), expected_methods, filename)
            for method in methods:
                self.assertNotIn(method, unique)
                unique.add(method)
            count += len(methods)
        self.assertEqual(count, 105)
        self.assertEqual(len(unique), 105)
