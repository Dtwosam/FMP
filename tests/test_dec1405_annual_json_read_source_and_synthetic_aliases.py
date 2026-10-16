"""DEC-1405: bounded synthetic JSON source-reader review.

The annual CLI module is never imported or called. Source is inspected
through git show of an exact tracked blob, and all file-path examples use
only synthetic TemporaryDirectory files, not protected historical data.
"""
from __future__ import annotations

import ast
import json
import math
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AnnualJsonInputReadSourceIsNotProtectedAuthenticity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        code = subprocess.check_output(
            ["git", "show", "HEAD:scripts/phase8a_annual_pattern_catalogue.py"],
            cwd=ROOT, text=True,
        )
        tree = ast.parse(code)
        cls.functions = {
            node.name: ast.get_source_segment(code, node)
            for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        cls.loader = cls.functions["_read_json"]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(
            prefix="dec1405-synthetic-json-only-"
        )
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.scratch = self.root / "scratch"
        self.other = self.root / "synthetic-other"
        self.scratch.mkdir()
        self.other.mkdir()

    def test_cli_reader_uses_caller_path_read_text_and_json_loads(self):
        self.assertIn('json.loads(Path(path).read_text(encoding="utf-8"))',
                      self.loader)
        self.assertIn("if not isinstance(value, dict):", self.loader)

    def test_reader_source_has_no_explicit_nofollow_or_inode_pinning(self):
        for token in ("O_NOFOLLOW", "os.open(", "fstat(", "is_symlink(",
                      "dir_fd=", "is_relative_to("):
            with self.subTest(token=token):
                self.assertNotIn(token, self.loader)

    def test_reader_source_has_no_explicit_byte_limit(self):
        for token in ("max_bytes", "max_size", "st_size", "getsize(",
                      "Content-Length", "read_bytes("):
            with self.subTest(token=token):
                self.assertNotIn(token, self.loader)

    def test_json_reader_source_uses_no_duplicate_key_rejection_hook(self):
        self.assertNotIn("object_pairs_hook", self.loader)
        self.assertNotIn("parse_constant=", self.loader)

    def test_synthetic_duplicate_object_keys_are_last_value_wins(self):
        text = '{"synthetic":1,"synthetic":2}'
        self.assertEqual(json.loads(text), {"synthetic": 2})

    def test_synthetic_nested_duplicate_keys_are_last_value_wins(self):
        text = '{"outer":{"source":"first","source":"second"}}'
        self.assertEqual(json.loads(text)["outer"]["source"], "second")

    def test_synthetic_nan_constant_is_accepted_by_default_json_loads(self):
        payload = json.loads('{"synthetic":NaN}')
        self.assertTrue(math.isnan(payload["synthetic"]))

    def test_synthetic_infinity_constant_is_accepted_by_default_json_loads(self):
        payload = json.loads('{"synthetic":Infinity}')
        self.assertEqual(payload["synthetic"], float("inf"))

    def test_synthetic_malformed_json_is_rejected_by_stdlib(self):
        with self.assertRaises(json.JSONDecodeError):
            json.loads('{"synthetic":} ')

    def test_synthetic_file_symlink_read_follows_sibling_target(self):
        target = self.other / "source.json"
        target.write_text('{"test":1}', encoding="utf-8")
        alias = self.scratch / "input.json"
        alias.symlink_to(target)
        self.assertEqual(json.loads(alias.read_text(encoding="utf-8")),
                         {"test": 1})

    def test_synthetic_parent_symlink_read_follows_target_directory(self):
        target = self.other / "source.json"
        target.write_text('{"test":2}', encoding="utf-8")
        (self.scratch / "linked").symlink_to(
            self.other, target_is_directory=True
        )
        self.assertEqual(
            json.loads((self.scratch / "linked" / "source.json").read_text(
                encoding="utf-8"
            )),
            {"test": 2},
        )

    def test_synthetic_larger_json_object_has_no_stdlib_byte_budget(self):
        value = {"synthetic": "x" * 16384}
        filename = self.scratch / "large.json"
        filename.write_text(json.dumps(value), encoding="utf-8")
        self.assertEqual(json.loads(filename.read_text(encoding="utf-8")),
                         value)

    def test_actual_preflight_passes_four_caller_paths_to_reader(self):
        source = self.functions["_cmd_preflight"]
        for name in ("feature_run_json", "feature_artifacts_json",
                     "outcome_run_json", "outcome_artifacts_json"):
            with self.subTest(name=name):
                self.assertIn("_read_json(args." + name + ")", source)

    def test_prior_freeze_reader_paths_are_caller_supplied_when_present(self):
        source = self.functions["_cmd_require_prior_freeze"]
        self.assertIn("_read_json(args.previous_run_json)", source)
        self.assertIn("_read_json(args.previous_freeze_evidence)", source)
        self.assertIn("if args.previous_run_json is not None", source)
