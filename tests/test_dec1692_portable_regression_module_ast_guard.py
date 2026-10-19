"""DEC-1692: syntactic and method-uniqueness guard for portable tests.

Test-only static AST validation, without importing protected review modules.
"""
import ast
from pathlib import Path
import unittest


class PortableRegressionSourceSyntaxTests(unittest.TestCase):
    def test_portable_regression_modules_parse_and_keep_unique_methods(self):
        root = Path(__file__).resolve().parent
        expected = {
            "test_dec1685_invalid_json_keywords.py": 97,
            "test_dec1686_invalid_json_keywords_array_evidence.py": 37,
            "test_dec1687_valid_json_escaped_values_array_evidence.py": 49,
            "test_dec1688_valid_json_escaped_keys_array_evidence.py": 49,
            "test_dec1689_decoded_duplicate_keys_array_evidence.py": 31,
            "test_dec1690_legal_json_whitespace_array_evidence.py": 37,
        }
        checked = 0
        # The legacy source is also parsed so its helper syntax cannot be
        # accidentally broken while these child drafts are under review.
        for name in ("test_dec1478_portable_ci_source_bundle_envelope.py",
                     *expected):
            path = root / name
            source = path.read_text(encoding="utf-8")
            parsed = ast.parse(source, filename=str(path))
            methods = 0
            for cls in ast.walk(parsed):
                if not isinstance(cls, ast.ClassDef):
                    continue
                names = [
                    member.name
                    for member in cls.body
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and member.name.startswith("test_")
                ]
                self.assertEqual(
                    len(names), len(set(names)),
                    msg="shadowed test method in " + name + ": " + cls.name)
                methods += len(names)
            if name in expected:
                self.assertEqual(methods, expected[name], name)
                checked += methods
        self.assertEqual(checked, 300)
