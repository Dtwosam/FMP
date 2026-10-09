from __future__ import annotations

"""DEC-643: validate real shared helper delegates to anchored POSIX writer."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fmp.discovery import annual_pattern_catalogue_2023_dirfd_publication_preview as anchored
from fmp.discovery.annual_pattern_catalogue_2023_external_report_create import (
    write_once_external_report,
)


class AnchoredSharedReportIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.external = self.root / "external"
        self.external.mkdir()
        self.checkout = self.root / "checkout"
        self.checkout.mkdir()
        (self.checkout / "locked.txt").write_text("immutable\n")
        self.target = self.external / "report.json"

    def assert_checkout_unchanged(self):
        self.assertEqual(
            sorted(p.name for p in self.checkout.iterdir()), ["locked.txt"]
        )
        self.assertEqual((self.checkout / "locked.txt").read_text(), "immutable\n")

    def test_all_23_cli_callers_still_use_shared_guarded_helper(self):
        root = Path(__file__).resolve().parents[1]
        scripts = sorted(
            (root / "scripts").glob("phase8a_annual_pattern_catalogue_2023_*.py")
        )
        self.assertEqual(len(scripts), 23)
        for script in scripts:
            with self.subTest(script=script.name):
                src = script.read_text(encoding="utf-8")
                self.assertIn("write_once_external_report(", src)
                self.assertIn("target.is_relative_to(", src)
                self.assertIn("sys.dont_write_bytecode = True", src)
                self.assertNotIn("target.write_text(", src)
        wrapper = (
            root / "src/fmp/discovery/"
            "annual_pattern_catalogue_2023_external_report_create.py"
        ).read_text(encoding="utf-8")
        preview = (
            root / "src/fmp/discovery/"
            "annual_pattern_catalogue_2023_dirfd_publication_preview.py"
        ).read_text(encoding="utf-8")
        self.assertIn("preview_write_once_external_report(target, content, conflict_message)", wrapper)
        for guard in (
            "os.O_DIRECTORY", "os.O_NOFOLLOW", "os.O_NONBLOCK",
            "dir_fd=fd", "src_dir_fd=fd", "dst_dir_fd=fd",
            "os.O_EXCL", "follow_symlinks=False", "os.fsync(output.fileno())",
        ):
            with self.subTest(guard=guard):
                self.assertIn(guard, preview)

    def test_real_helper_rejects_preexisting_parent_directory_symlink(self):
        alias = self.root / "external-alias"
        alias.symlink_to(self.checkout, target_is_directory=True)
        with self.assertRaises(OSError):
            write_once_external_report(
                alias / "report.json", "proof\n", "conflict"
            )
        self.assert_checkout_unchanged()

    def test_real_helper_parent_swap_after_fd_open_uses_pinned_inode(self):
        real_open = os.open
        moved = self.root / "moved-original"
        triggered = []
        def swapping_open(path, flags, *args, **kwargs):
            if str(path).startswith(".fmp-audit-") and not triggered:
                triggered.append(True)
                self.external.rename(moved)
                self.external.symlink_to(self.checkout, target_is_directory=True)
            return real_open(path, flags, *args, **kwargs)
        flags = anchored._safe_flags()
        with (
            mock.patch.object(anchored, "_safe_flags", return_value=flags),
            mock.patch.object(anchored.os, "open", side_effect=swapping_open),
        ):
            write_once_external_report(self.target, "proof\n", "conflict")
        self.assertEqual(triggered, [True])
        self.assertEqual((moved / "report.json").read_text(), "proof\n")
        self.assert_checkout_unchanged()


if __name__ == "__main__":
    unittest.main()
