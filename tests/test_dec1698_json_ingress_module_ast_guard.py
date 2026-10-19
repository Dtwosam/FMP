"""DEC-1698: static method-name and grammar test inventory guard.

This suite reads only synthetic test-source files from the working checkout.
"""
import ast
from pathlib import Path
import unittest


class NestedJsonIngressRegressionAstGuardTests(unittest.TestCase):
    def test_new_json_ingress_modules_parse_and_have_unique_test_names(self):
        root = Path(__file__).resolve().parent
        expected = {
            "test_dec1693_json_member_delimiters_array_evidence.py": 49,
            "test_dec1694_invalid_json_whitespace_array_evidence.py": 49,
            "test_dec1695_nonfinite_json_array_evidence.py": 49,
            "test_dec1696_underflow_json_array_evidence.py": 49,
            "test_dec1697_json_array_delimiters_evidence.py": 49,
        }
        seen_across_modules = set()
        total = 0
        for name, n in sorted(expected.items()):
            path = root / name
            module = ast.parse(path.read_text(encoding="utf-8"),
                               filename=str(path))
            methods = []
            for node in module.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                for child in node.body:
                    if (isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and child.name.startswith("test_")):
                        methods.append(child.name)
            self.assertEqual(len(methods), n, name)
            self.assertEqual(len(set(methods)), n, name)
            for method in methods:
                self.assertNotIn(method, seen_across_modules)
                seen_across_modules.add(method)
            total += len(methods)
        self.assertEqual(total, 245)
        self.assertEqual(len(seen_across_modules), 245)
