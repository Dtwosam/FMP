"""DEC-1713: source AST integrity guard for duplicate-key and root gates.

No test imports, protected-source access, workflow dispatch or remote reads.
"""
import ast
from pathlib import Path
import unittest


class StrictPreflightFailclosedModuleGuardTests(unittest.TestCase):
    def test_early_failure_modules_parse_and_keep_unique_methods(self):
        root = Path(__file__).resolve().parent
        expected = {
            "test_dec1711_duplicate_decoded_key_preflight.py": 25,
            "test_dec1712_root_preflight_skips_nested_review.py": 37,
        }
        methods_seen = set()
        total = 0
        for filename, count in sorted(expected.items()):
            path = root / filename
            tree = ast.parse(path.read_text(encoding="utf-8"),
                             filename=str(path))
            methods = []
            for cls in tree.body:
                if isinstance(cls, ast.ClassDef):
                    methods.extend(
                        item.name for item in cls.body
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and item.name.startswith("test_"))
            self.assertEqual(len(methods), count, filename)
            self.assertEqual(len(set(methods)), count, filename)
            for name in methods:
                self.assertNotIn(name, methods_seen)
                methods_seen.add(name)
            total += len(methods)
        self.assertEqual(total, 62)
        self.assertEqual(len(methods_seen), 62)
