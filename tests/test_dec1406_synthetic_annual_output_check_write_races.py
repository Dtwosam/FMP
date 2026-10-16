"""DEC-1406: deterministic TEMP-ONLY output-check/write race witness.

The tiny illustrative Python stdlib writers mirror only the checked-in
annual CLI's exists/read/write sequence. No annual code is imported or
called. Every synthetic source and target is inside TemporaryDirectory.
"""
from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def model_write_text(destination: Path, payload: str, *, before_write=None):
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError("synthetic conflicting output")
    if before_write is not None:
        before_write()
    destination.write_text(payload, encoding="utf-8")


def model_write_bytes(destination: Path, payload: bytes, *, before_write=None):
    if destination.exists() and destination.read_bytes() != payload:
        raise ValueError("synthetic conflicting output")
    if before_write is not None:
        before_write()
    destination.write_bytes(payload)


class SyntheticCheckThenWriteIsNotOriginalProtectedNoWrite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = subprocess.check_output(
            ["git", "show", "HEAD:scripts/phase8a_annual_pattern_catalogue.py"],
            cwd=ROOT, text=True,
        )
        module = ast.parse(source)
        cls.functions = {
            node.name: ast.get_source_segment(source, node)
            for node in module.body if isinstance(node, ast.FunctionDef)
        }

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(
            prefix="dec1406-synthetic-exists-write-"
        )
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.scratch = self.root / "scratch"
        self.target = self.root / "synthetic-target"
        self.scratch.mkdir()
        self.target.mkdir()

    def test_committed_text_writer_has_read_then_write_gap(self):
        src = self.functions["_write_json"]
        self.assertLess(src.index("destination.exists()"),
                        src.index("destination.read_text("))
        self.assertLess(src.index("destination.read_text("),
                        src.index("destination.write_text("))

    def test_committed_byte_writer_has_read_then_write_gap(self):
        src = self.functions["_write_bytes"]
        self.assertLess(src.index("destination.exists()"),
                        src.index("destination.read_bytes("))
        self.assertLess(src.index("destination.read_bytes("),
                        src.index("destination.write_bytes("))

    def test_synthetic_text_writer_rejects_preexisting_different_data(self):
        dest = self.scratch / "output.json"
        dest.write_text("different", encoding="utf-8")
        with self.assertRaises(ValueError):
            model_write_text(dest, "expected")
        self.assertEqual(dest.read_text(encoding="utf-8"), "different")

    def test_synthetic_byte_writer_rejects_preexisting_different_data(self):
        dest = self.scratch / "output.bin"
        dest.write_bytes(b"different")
        with self.assertRaises(ValueError):
            model_write_bytes(dest, b"expected")
        self.assertEqual(dest.read_bytes(), b"different")

    def test_synthetic_text_check_before_create_can_be_invalidated(self):
        dest = self.scratch / "output.json"
        model_write_text(dest, "expected", before_write=lambda:
                         dest.write_text("inserted", encoding="utf-8"))
        self.assertEqual(dest.read_text(encoding="utf-8"), "expected")

    def test_synthetic_bytes_check_before_create_can_be_invalidated(self):
        dest = self.scratch / "output.bin"
        model_write_bytes(dest, b"expected",
                          before_write=lambda: dest.write_bytes(b"inserted"))
        self.assertEqual(dest.read_bytes(), b"expected")

    def test_synthetic_existing_matching_text_can_change_after_compare(self):
        dest = self.scratch / "output.json"
        dest.write_text("expected", encoding="utf-8")
        model_write_text(dest, "expected", before_write=lambda:
                         dest.write_text("swapped", encoding="utf-8"))
        self.assertEqual(dest.read_text(encoding="utf-8"), "expected")

    def test_synthetic_existing_matching_bytes_can_change_after_compare(self):
        dest = self.scratch / "output.bin"
        dest.write_bytes(b"expected")
        model_write_bytes(dest, b"expected",
                          before_write=lambda: dest.write_bytes(b"swapped"))
        self.assertEqual(dest.read_bytes(), b"expected")

    def test_synthetic_missing_output_replaced_by_symlink_before_write(self):
        dest = self.scratch / "output.json"
        original = self.target / "original.json"
        original.write_text("untouched", encoding="utf-8")
        def redirect():
            dest.symlink_to(original)
        model_write_text(dest, "expected", before_write=redirect)
        self.assertEqual(original.read_text(encoding="utf-8"), "expected")
        self.assertTrue(dest.is_symlink())

    def test_synthetic_missing_output_replaced_by_byte_symlink(self):
        dest = self.scratch / "output.bin"
        original = self.target / "original.bin"
        original.write_bytes(b"untouched")
        model_write_bytes(dest, b"expected",
                          before_write=lambda: dest.symlink_to(original))
        self.assertEqual(original.read_bytes(), b"expected")

    def test_synthetic_no_interference_creates_disposable_output(self):
        dest = self.scratch / "safe.json"
        model_write_text(dest, '{"synthetic":true}\n')
        self.assertEqual(dest.read_text(encoding="utf-8"),
                         '{"synthetic":true}\n')

    def test_synthetic_fixtures_are_confined_to_disposable_root(self):
        self.assertEqual(self.scratch.parent, self.root)
        self.assertEqual(self.target.parent, self.root)
        self.assertNotEqual(self.scratch, self.target)
