from __future__ import annotations

"""DEC-640 fail-closed publication error regressions (offline, never dispatch)."""

from pathlib import Path
import errno
import os
import tempfile
import unittest
from unittest import mock

from fmp.discovery.annual_pattern_catalogue_2023_external_report_create import (
    write_once_external_report,
)


class AtomicPublicationFailureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.target = self.directory / "output" / "report.json"
        self.conflict = "report conflict"

    def assert_no_files(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.target.parent.iterdir()), [])

    def test_fsync_failure_never_exposes_partial_final_and_cleans_sibling(self):
        with mock.patch(
            "fmp.discovery.annual_pattern_catalogue_2023_external_report_create.os.fsync",
            side_effect=OSError(errno.EIO, "disk sync failed"),
        ):
            with self.assertRaises(OSError):
                write_once_external_report(self.target, "large payload\n" * 1000, self.conflict)
        self.assert_no_files()

    def test_link_failure_without_fallback_never_leaves_final_or_temp(self):
        with mock.patch(
            "fmp.discovery.annual_pattern_catalogue_2023_external_report_create.os.link",
            side_effect=OSError(errno.EPERM, "hardlink unsupported"),
        ):
            with self.assertRaises(OSError):
                write_once_external_report(self.target, "payload\n", self.conflict)
        self.assert_no_files()

    def test_existing_empty_file_conflict_does_not_modify_file(self):
        self.target.parent.mkdir()
        self.target.write_bytes(b"")
        metadata = self.target.stat()
        with self.assertRaisesRegex(ValueError, "report conflict"):
            write_once_external_report(self.target, "payload\n", self.conflict)
        self.assertEqual(self.target.read_bytes(), b"")
        self.assertEqual(self.target.stat().st_mtime_ns, metadata.st_mtime_ns)

    def test_target_replaced_with_dangling_symlink_while_publishing_never_follows(self):
        real_link = os.link
        missing = self.directory / "would-be-outside"
        def race(source, destination):
            Path(destination).symlink_to(missing)
            return real_link(source, destination)
        with mock.patch(
            "fmp.discovery.annual_pattern_catalogue_2023_external_report_create.os.link",
            side_effect=race,
        ):
            with self.assertRaisesRegex(ValueError, "report conflict"):
                write_once_external_report(self.target, "content\n", self.conflict)
        self.assertTrue(self.target.is_symlink())
        self.assertFalse(missing.exists())
        self.assertEqual(list(self.target.parent.iterdir()), [self.target])

    def test_identical_second_write_leaves_no_sibling_and_preserves_inode(self):
        write_once_external_report(self.target, "payload\n", self.conflict)
        before = self.target.stat()
        write_once_external_report(self.target, "payload\n", self.conflict)
        after = self.target.stat()
        self.assertEqual(
            (before.st_ino, before.st_mtime_ns),
            (after.st_ino, after.st_mtime_ns),
        )
        self.assertEqual(list(self.target.parent.iterdir()), [self.target])


if __name__ == "__main__":
    unittest.main()
