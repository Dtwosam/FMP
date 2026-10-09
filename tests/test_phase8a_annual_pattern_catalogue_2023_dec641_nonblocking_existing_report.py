from __future__ import annotations

"""DEC-641: fail-closed reads of existing offline report leaves."""

import os
import stat
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fmp.discovery.annual_pattern_catalogue_2023_external_report_create import write_once_external_report


class ExistingReportIdentitySafety(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.target = self.root / "report.json"
        self.error = "DENIED existing report"

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires POSIX named pipes")
    def test_named_pipe_as_existing_report_fails_without_open_block(self):
        os.mkfifo(self.target)
        code = (
            "from pathlib import Path; "
            "from fmp.discovery.annual_pattern_catalogue_2023_external_report_create "
            "import write_once_external_report; "
            "write_once_external_report(Path({!r}), {}, 'DENIED')"
        ).format(str(self.target), repr("proof\n"))
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=3,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError: DENIED", result.stderr)
        self.assertTrue(stat.S_ISFIFO(self.target.lstat().st_mode))

    def test_regular_matching_report_is_accepted_without_rewrite(self):
        self.target.write_text("proof\n")
        stat_before = self.target.stat()
        write_once_external_report(self.target, "proof\n", self.error)
        stat_after = self.target.stat()
        self.assertEqual(
            (stat_before.st_ino, stat_before.st_mtime_ns),
            (stat_after.st_ino, stat_after.st_mtime_ns),
        )

    def test_symlink_to_regular_matching_report_is_refused_by_helper(self):
        origin = self.root / "origin.json"
        origin.write_text("proof\n")
        self.target.symlink_to(origin)
        with self.assertRaisesRegex(ValueError, "DENIED"):
            write_once_external_report(self.target, "proof\n", self.error)
        self.assertEqual(origin.read_text(), "proof\n")

    def test_oversized_regular_existing_report_is_not_read_in_full(self):
        self.target.write_text("surplus\n" * 100000)
        prior = self.target.stat()
        with self.assertRaisesRegex(ValueError, "DENIED"):
            write_once_external_report(self.target, "proof\n", self.error)
        self.assertEqual(self.target.stat().st_size, prior.st_size)

    def test_mismatching_regular_report_is_refused_without_modification(self):
        self.target.write_text("other\n")
        with self.assertRaisesRegex(ValueError, "DENIED"):
            write_once_external_report(self.target, "proof\n", self.error)
        self.assertEqual(self.target.read_text(), "other\n")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires POSIX named pipes")
    def test_special_file_published_at_link_race_is_rejected(self):
        real_link = os.link
        def compete(source, destination, *args, **kwargs):
            os.mkfifo(destination, dir_fd=kwargs["dst_dir_fd"])
            return real_link(source, destination, *args, **kwargs)
        with mock.patch(
            "fmp.discovery.annual_pattern_catalogue_2023_external_report_create.os.link",
            side_effect=compete,
        ):
            with self.assertRaisesRegex(ValueError, "DENIED"):
                write_once_external_report(self.target, "proof\n", self.error)
        self.assertTrue(stat.S_ISFIFO(self.target.lstat().st_mode))
        self.assertEqual([p.name for p in self.root.iterdir()], ["report.json"])


if __name__ == "__main__":
    unittest.main()
