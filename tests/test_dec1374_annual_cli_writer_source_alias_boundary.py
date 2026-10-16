"""DEC-1374: source-only annual writer path and atomicity review.

The CLI code is never imported or invoked. No paths, annual input/evidence,
broker interfaces or installed workflow are touched by these tests.
"""
from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AnnualCliWriterCannotProveProtectedNoWrite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = subprocess.check_output(
            ["git", "show", "HEAD:scripts/phase8a_annual_pattern_catalogue.py"],
            cwd=ROOT, text=True,
        )
        tree = ast.parse(cls.source)
        cls.functions = {
            n.name: ast.get_source_segment(cls.source, n)
            for n in tree.body if isinstance(n, ast.FunctionDef)
        }

    def test_json_writer_creates_parent_of_supplied_path(self):
        s = self.functions["_write_json"]
        self.assertIn("destination = Path(path)", s)
        self.assertIn("destination.parent.mkdir(parents=True, exist_ok=True)", s)

    def test_json_writer_reads_existing_output_then_writes_text(self):
        s = self.functions["_write_json"]
        self.assertIn("destination.exists()", s)
        self.assertIn('destination.read_text(encoding="utf-8") != payload', s)
        self.assertIn('destination.write_text(payload, encoding="utf-8")', s)
        self.assertLess(s.index("destination.exists()"), s.index("destination.write_text("))

    def test_byte_writer_creates_parent_and_writes_bytes(self):
        s = self.functions["_write_bytes"]
        self.assertIn("destination = Path(path)", s)
        self.assertIn("destination.parent.mkdir(parents=True, exist_ok=True)", s)
        self.assertIn("destination.exists() and destination.read_bytes() != value", s)
        self.assertIn("destination.write_bytes(value)", s)

    def test_writers_lack_explicit_symlink_or_nofollow_enforcement(self):
        for name in ("_write_json", "_write_bytes"):
            with self.subTest(name=name):
                s = self.functions[name]
                for marker in ("is_symlink(", "O_NOFOLLOW", "is_relative_to(",
                               "resolve(strict=True)", "os.open("):
                    self.assertNotIn(marker, s)

    def test_json_and_byte_writers_do_not_use_atomic_replacement(self):
        for name in ("_write_json", "_write_bytes"):
            with self.subTest(name=name):
                s = self.functions[name]
                for marker in ("os.replace(", "Path.replace(", "tempfile.",
                               "os.fsync(", "os.O_EXCL"):
                    self.assertNotIn(marker, s)

    def test_cell_command_writes_two_separate_outputs_in_sequence(self):
        s = self.functions["_cmd_cell"]
        self.assertLess(s.index("_write_json(args.evidence_out, product.evidence)"),
                        s.index("_write_bytes(args.catalogue_out, product.catalogue_payload_bytes)"))

    def test_preflight_and_prior_entrypoints_use_caller_output_arguments(self):
        self.assertIn("_write_json(args.out, value)", self.functions["_cmd_preflight"])
        self.assertIn("_write_json(args.out, report)",
                      self.functions["_cmd_require_prior_freeze"])
        self.assertIn("_write_json(args.out, evidence)", self.functions["_cmd_freeze"])

    def test_cli_parser_accepts_relative_output_paths_as_path_arguments(self):
        s = self.functions["build_parser"]
        self.assertIn('preflight.add_argument("--out", type=Path, required=True)', s)
        self.assertIn('cell.add_argument("--evidence-out", type=Path, required=True)', s)
        self.assertIn('cell.add_argument("--catalogue-out", type=Path, required=True)', s)
        self.assertIn('freeze.add_argument("--out", type=Path, required=True)', s)
