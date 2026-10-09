from __future__ import annotations

"""DEC-642 directory-fd parent swap race reproduction (inert preview only)."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest import mock

from fmp.discovery import annual_pattern_catalogue_2023_dirfd_publication_preview as lib
from fmp.discovery import annual_pattern_catalogue_2023_external_report_create as legacy


class AnchoredAuditOutputPreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.parent = self.root / "external" / "report"
        self.parent.mkdir(parents=True)
        self.target = self.parent / "proof.json"
        self.checkout = self.root / "checkout"
        self.checkout.mkdir()
        (self.checkout / "locked.txt").write_bytes(b"checkout-inventory")
        self.before = hashlib.sha256(
            (self.checkout / "locked.txt").read_bytes()
        ).hexdigest()

    def assert_checkout_untouched(self):
        self.assertEqual(
            hashlib.sha256((self.checkout / "locked.txt").read_bytes()).hexdigest(),
            self.before,
        )
        self.assertEqual(
            sorted(p.name for p in self.checkout.iterdir()), ["locked.txt"],
        )

    def test_new_identical_and_conflicting_leaf(self):
        lib.preview_write_once_external_report(self.target, "proof\n", "conflict")
        inode = self.target.stat().st_ino
        lib.preview_write_once_external_report(self.target, "proof\n", "conflict")
        self.assertEqual(self.target.stat().st_ino, inode)
        with self.assertRaisesRegex(ValueError, "conflict"):
            lib.preview_write_once_external_report(self.target, "other\n", "conflict")
        self.assertEqual(self.target.read_text(), "proof\n")
        self.assert_checkout_untouched()

    def test_dangling_leaf_symlink_fails_closed(self):
        self.target.symlink_to(self.checkout / "nonexistent")
        with self.assertRaises(ValueError):
            lib.preview_write_once_external_report(self.target, "proof\n", "conflict")
        self.assertTrue(self.target.is_symlink())
        self.assert_checkout_untouched()

    def test_parent_symlink_swap_before_open_fails_closed(self):
        real_open = os.open
        moved = self.root / "moved-parent"
        triggered = []
        def racing_open(path, flags, *args, **kwargs):
            if path == "report" and not triggered:
                triggered.append(True)
                self.parent.rename(moved)
                self.parent.symlink_to(self.checkout, target_is_directory=True)
            return real_open(path, flags, *args, **kwargs)
        flags = lib._safe_flags()
        with (
            mock.patch.object(lib, "_safe_flags", return_value=flags),
            mock.patch.object(lib.os, "open", side_effect=racing_open),
        ):
            with self.assertRaises(OSError):
                lib.preview_write_once_external_report(
                    self.target, "proof\n", "conflict"
                )
        self.assertEqual(triggered, [True])
        self.assert_checkout_untouched()

    def test_parent_symlink_swap_after_open_writes_only_old_directory(self):
        real_open = os.open
        moved = self.root / "moved-parent"
        triggered = []
        def racing_open(path, flags, *args, **kwargs):
            if str(path).startswith(".fmp-audit-") and not triggered:
                triggered.append(True)
                self.parent.rename(moved)
                self.parent.symlink_to(self.checkout, target_is_directory=True)
            return real_open(path, flags, *args, **kwargs)
        flags = lib._safe_flags()
        with (
            mock.patch.object(lib, "_safe_flags", return_value=flags),
            mock.patch.object(lib.os, "open", side_effect=racing_open),
        ):
            lib.preview_write_once_external_report(
                self.target, "proof\n", "conflict"
            )
        self.assertEqual(triggered, [True])
        self.assertEqual((moved / "proof.json").read_text(), "proof\n")
        self.assert_checkout_untouched()

    def test_live_shared_helper_rejects_parent_symlink_swap_before_open(self):
        """DEC-643: the actual CLI-imported helper must now pin the parent."""
        real_open = os.open
        moved = self.root / "moved-live-parent"
        triggered = []
        def racing_open(path, flags, *args, **kwargs):
            if path == "report" and not triggered:
                triggered.append(True)
                self.parent.rename(moved)
                self.parent.symlink_to(self.checkout, target_is_directory=True)
            return real_open(path, flags, *args, **kwargs)
        flags = lib._safe_flags()
        with (
            mock.patch.object(lib, "_safe_flags", return_value=flags),
            mock.patch.object(lib.os, "open", side_effect=racing_open),
        ):
            with self.assertRaises(OSError):
                legacy.write_once_external_report(
                    self.target, "proof\n", "conflict"
                )
        self.assertEqual(triggered, [True])
        self.assert_checkout_untouched()

    def test_concurrent_matching_content_is_idempotent(self):
        barrier = threading.Barrier(8)
        def worker(_):
            barrier.wait(timeout=10)
            lib.preview_write_once_external_report(
                self.target, "proof\n" * 40000, "conflict"
            )
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(worker, range(8)))
        self.assertEqual(self.target.read_text(), "proof\n" * 40000)
        self.assert_checkout_untouched()

    def test_concurrent_conflicts_only_one_wins(self):
        barrier = threading.Barrier(8)
        def worker(i):
            barrier.wait(timeout=10)
            try:
                lib.preview_write_once_external_report(
                    self.target, f"proof-{i}\n", "conflict"
                )
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            answers = list(pool.map(worker, range(8)))
        self.assertEqual(sum(answers), 1)
        self.assert_checkout_untouched()

    def test_valid_250_character_final_filename(self):
        target = self.parent / ("r" * 250)
        lib.preview_write_once_external_report(target, "report\n", "conflict")
        self.assertEqual(target.read_text(), "report\n")
        self.assert_checkout_untouched()


if __name__ == "__main__":
    unittest.main()
