"""DEC-1375: TEMPORARY-DIRECTORY-ONLY ordinary Python output alias probes.

No original annual source or protected evidence is opened or written. No
annual CLI/function is imported/executed, and no workflow is dispatched.
The stdlib Path behaviors tested here correspond only to a checked-in
source-only writer structure; this is NOT independent protected OS proof.
"""
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TempOnlyOutputAliasWriteThroughProvesNothingAboutProtectedOS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = subprocess.check_output(
            ["git", "show", "HEAD:scripts/phase8a_annual_pattern_catalogue.py"],
            cwd=ROOT, text=True,
        )
        cls.json_writer = cls.source.split("def _write_json(", 1)[1].split(
            "\ndef _write_bytes(", 1)[0]
        cls.bytes_writer = cls.source.split("def _write_bytes(", 1)[1].split(
            "\ndef _cmd_status(", 1)[0]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dec1375-only-synthetic-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scratch = self.root / "scratch"
        self.original = self.root / "synthetic-target"
        self.scratch.mkdir()
        self.original.mkdir()

    def test_committed_json_writer_uses_exists_then_direct_write(self):
        self.assertIn("destination.exists()", self.json_writer)
        self.assertIn("destination.write_text(payload", self.json_writer)

    def test_committed_bytes_writer_uses_exists_then_direct_write(self):
        self.assertIn("destination.exists() and destination.read_bytes()", self.bytes_writer)
        self.assertIn("destination.write_bytes(value)", self.bytes_writer)

    @unittest.skipUnless(os.name == "posix", "Linux/POSIX symlink behavior")
    def test_synthetic_dangling_json_output_symlink_can_create_target(self):
        target = self.original / "not-yet-existing.json"
        alias = self.scratch / "out.json"
        alias.symlink_to(target)
        self.assertFalse(alias.exists())
        alias.write_text('{"synthetic":true}\n', encoding="utf-8")
        self.assertEqual(target.read_text(encoding="utf-8"),
                         '{"synthetic":true}\n')

    @unittest.skipUnless(os.name == "posix", "Linux/POSIX symlink behavior")
    def test_synthetic_dangling_byte_output_symlink_can_create_target(self):
        target = self.original / "not-yet-existing.bin"
        alias = self.scratch / "out.bin"
        alias.symlink_to(target)
        self.assertFalse(alias.exists())
        alias.write_bytes(b"offline-synthetic-bytes")
        self.assertEqual(target.read_bytes(), b"offline-synthetic-bytes")

    @unittest.skipUnless(os.name == "posix", "Linux/POSIX symlink behavior")
    def test_synthetic_parent_directory_symlink_redirects_text_output(self):
        (self.scratch / "dir").symlink_to(self.original, target_is_directory=True)
        output = self.scratch / "dir" / "evidence.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("synthetic", encoding="utf-8")
        self.assertEqual((self.original / "evidence.json").read_text(), "synthetic")

    @unittest.skipUnless(os.name == "posix", "Linux/POSIX symlink behavior")
    def test_synthetic_parent_directory_symlink_redirects_byte_output(self):
        (self.scratch / "dir").symlink_to(self.original, target_is_directory=True)
        output = self.scratch / "dir" / "payload.bin"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"synthetic")
        self.assertEqual((self.original / "payload.bin").read_bytes(), b"synthetic")

    def test_synthetic_dot_dot_path_escapes_scratch_without_confinement(self):
        output = self.scratch / ".." / "synthetic-target" / "result.json"
        output.write_text('{"offline":true}\n', encoding="utf-8")
        self.assertEqual((self.original / "result.json").read_text(),
                         '{"offline":true}\n')

    @unittest.skipUnless(os.name == "posix", "Linux/POSIX symlink behavior")
    def test_synthetic_existing_symlink_alias_shares_target_bytes(self):
        target = self.original / "original.txt"
        target.write_text("first", encoding="utf-8")
        alias = self.scratch / "result.txt"
        alias.symlink_to(target)
        self.assertTrue(alias.exists())
        alias.write_text("second", encoding="utf-8")
        self.assertEqual(target.read_text(encoding="utf-8"), "second")

    def test_two_synthetic_outputs_are_not_atomic_as_a_pair(self):
        evidence = self.scratch / "cell-evidence.json"
        payload = self.scratch / "catalogue-payload.json"
        evidence.write_text('{"synthetic":true}', encoding="utf-8")
        # Model a crash before a separate payload write, without invoking
        # the real CLI or touching anything outside our temporary root.
        self.assertTrue(evidence.is_file())
        self.assertFalse(payload.exists())

    def test_synthetic_probe_objects_remain_under_temp_root(self):
        self.assertEqual(self.original.parent, self.root)
        self.assertEqual(self.scratch.parent, self.root)
        self.assertNotEqual(self.original, self.scratch)
