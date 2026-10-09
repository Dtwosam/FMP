from __future__ import annotations

import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / "scripts"
MOD = runpy.run_path(str(ROOT / "dec645_mount_boundary_diagnostic.py"), run_name="dec645_test")
parse = MOD["parse_mountinfo"]
cover = MOD["_covering_mount"]
inspect = MOD["inspect_checkout_boundary"]


class MountDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.checkout = self.base / "checkout"
        self.output = self.base / "external"
        self.checkout.mkdir()
        self.output.mkdir()
        self.mountinfo = (
            f"42 1 1:1 / / rw,relatime - ext4 /dev/host rw\n"
            f"43 42 1:1 / {self.checkout} ro - bind bind rw\n"
            f"44 42 1:2 / {self.output} rw - tmpfs tmpfs rw\n"
        )

    def test_even_separate_mounts_readonly_checkout_remain_unauthorized(self):
        result = inspect(self.checkout, self.output, self.mountinfo)
        self.assertIs(result["authorized"], False)
        self.assertTrue(result["observation"]["distinct_mount_ids"])
        self.assertTrue(result["observation"]["checkout_vfs_mount_readonly"])

    def test_same_mount_remains_unauthorized(self):
        result = inspect(self.checkout, self.output, "42 1 1:1 / / rw - ext4 /dev/root rw")
        self.assertFalse(result["authorized"])
        self.assertFalse(result["observation"]["distinct_mount_ids"])

    def test_inside_checkout_flag_cannot_authorize(self):
        nested = self.checkout / "inside"
        nested.mkdir()
        result = inspect(self.checkout, nested, self.mountinfo)
        self.assertTrue(result["observation"]["output_parent_resolves_into_checkout"])
        self.assertFalse(result["authorized"])

    def test_symlink_output_into_checkout_flagged(self):
        alias = self.base / "alias"
        alias.symlink_to(self.checkout, target_is_directory=True)
        result = inspect(self.checkout, alias, self.mountinfo)
        self.assertTrue(result["observation"]["output_parent_resolves_into_checkout"])
        self.assertFalse(result["authorized"])

    def test_mountinfo_escaped_space(self):
        result = parse("9 8 0:1 / /a\\040b rw - tmpfs none rw")
        self.assertEqual(result[0]["mount_point"], Path("/a b"))

    def test_prefix_confusion_no_false_mount_match(self):
        entries = parse("1 0 1:1 / / rw - ext4 none rw\n2 1 1:2 / /external rw - tmpfs none rw")
        self.assertEqual(cover(Path("/external-other"), entries)["mount_id"], 1)

    def test_duplicate_mount_identities_ambiguous(self):
        entries = parse("1 0 1:1 / / rw - ext4 none rw\n2 1 1:2 / / rw - tmpfs none rw")
        self.assertIsNone(cover(Path("/checkout"), entries))

    def test_missing_checkout_fails_closed(self):
        result = inspect(self.base / "missing", self.output, self.mountinfo)
        self.assertFalse(result["authorized"])
        self.assertEqual(result["observation_error"], "FileNotFoundError")

    def test_invalid_mountinfo_fails_closed(self):
        result = inspect(self.checkout, self.output, "malformed\n")
        self.assertFalse(result["authorized"])
        self.assertEqual(result["observation_error"], "ValueError")

    def test_oversized_mountinfo_fails_closed(self):
        with self.assertRaises(ValueError):
            parse("A" * 2_000_001)

    def test_cli_prints_advisory_json_and_exits_nonzero(self):
        outcome = subprocess.run(
            [sys.executable, "-B", str(ROOT / "dec645_mount_boundary_diagnostic.py"),
             "--checkout", str(self.checkout), "--output-parent", str(self.output)],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(outcome.returncode, 2)
        msg = json.loads(outcome.stdout)
        self.assertFalse(msg["authorized"])
        self.assertEqual(msg["classification"], "NOT_AN_AUTHORIZATION")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires POSIX FIFO")
    def test_mountinfo_fifo_never_hangs_and_never_authorizes(self):
        fifo = self.base / "blocked-mountinfo"
        os.mkfifo(fifo)
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "dec645_mount_boundary_diagnostic.py"),
             "--checkout", str(self.checkout), "--output-parent", str(self.output),
             "--mountinfo", str(fifo)],
            capture_output=True, text=True, timeout=3,
        )
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertFalse(report["authorized"])
        self.assertEqual(report["observation_error"], "ValueError")

    def test_no_broker_dispatch_network_or_checkout_write_primitives(self):
        source = (ROOT / "dec645_mount_boundary_diagnostic.py").read_text()
        for banned in (
            "requests.", "subprocess.", "gh workflow run", "workflow_dispatch(",
            "place_order(", ".write_text(", "os.rename(", "os.link(", "os.mkdir(",
        ):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
