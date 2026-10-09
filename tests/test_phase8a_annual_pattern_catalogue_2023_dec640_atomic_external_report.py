from __future__ import annotations

"""DEC-640: concurrent complete-leaf publication without clobbering."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest import mock

from fmp.discovery.annual_pattern_catalogue_2023_external_report_create import write_once_external_report


class AtomicExternalReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.target = self.root / "reports" / "proof.json"
        self.conflict = "DEC-640 conflicting external report"

    def test_complete_bytes_exist_before_final_name_appears(self):
        content = "complete-proof\n" * 1000
        real_link = os.link
        observations = []
        def observe_link(source, destination, *args, **kwargs):
            self.assertFalse(Path(destination).exists())
            self.assertEqual(Path(source).read_text(), content)
            observations.append(True)
            return real_link(source, destination, *args, **kwargs)
        with mock.patch(
            "fmp.discovery.annual_pattern_catalogue_2023_external_report_create.os.link",
            side_effect=observe_link,
        ):
            write_once_external_report(self.target, content, self.conflict)
        self.assertEqual(observations, [True])
        self.assertEqual(self.target.read_text(), content)
        self.assertEqual(sorted(p.name for p in self.target.parent.iterdir()), ["proof.json"])

    def test_competing_conflicting_leaf_at_publish_is_untouched(self):
        real_link = os.link
        def competing_link(source, destination, *args, **kwargs):
            Path(destination).write_text("competitor\n")
            return real_link(source, destination, *args, **kwargs)
        with mock.patch(
            "fmp.discovery.annual_pattern_catalogue_2023_external_report_create.os.link",
            side_effect=competing_link,
        ):
            with self.assertRaisesRegex(ValueError, "conflicting external report"):
                write_once_external_report(self.target, "ours\n", self.conflict)
        self.assertEqual(self.target.read_text(), "competitor\n")
        self.assertEqual(sorted(p.name for p in self.target.parent.iterdir()), ["proof.json"])

    def test_competing_identical_leaf_at_publish_is_accepted(self):
        real_link = os.link
        def competing_link(source, destination, *args, **kwargs):
            Path(destination).write_text("proof\n")
            return real_link(source, destination, *args, **kwargs)
        with mock.patch(
            "fmp.discovery.annual_pattern_catalogue_2023_external_report_create.os.link",
            side_effect=competing_link,
        ):
            write_once_external_report(self.target, "proof\n", self.conflict)
        self.assertEqual(self.target.read_text(), "proof\n")
        self.assertEqual(sorted(p.name for p in self.target.parent.iterdir()), ["proof.json"])

    def test_concurrent_identical_reports_all_succeed(self):
        count = 12
        barrier = threading.Barrier(count)
        content = "large identical publication\n" * 10000
        def writer(_):
            barrier.wait(timeout=30)
            write_once_external_report(self.target, content, self.conflict)
        with ThreadPoolExecutor(max_workers=count) as pool:
            list(pool.map(writer, range(count)))
        self.assertEqual(self.target.read_text(), content)
        self.assertEqual(sorted(p.name for p in self.target.parent.iterdir()), ["proof.json"])

    def test_concurrent_conflicts_never_replace_first_leaf(self):
        count = 12
        barrier = threading.Barrier(count)
        def writer(i):
            barrier.wait(timeout=30)
            try:
                write_once_external_report(self.target, f"writer-{i}\n", self.conflict)
                return (i, "ok")
            except ValueError:
                return (i, "conflict")
        with ThreadPoolExecutor(max_workers=count) as pool:
            results = list(pool.map(writer, range(count)))
        winners = [i for i, status in results if status == "ok"]
        self.assertEqual(len(winners), 1)
        self.assertEqual(self.target.read_text(), f"writer-{winners[0]}\n")
        self.assertEqual(sorted(p.name for p in self.target.parent.iterdir()), ["proof.json"])

    def test_existing_hardlink_keeps_inode_sha256_and_mtime(self):
        checkout = self.root / "checkout.txt"
        checkout.write_text("preserved\n")
        self.target.parent.mkdir(parents=True)
        self.target.hardlink_to(checkout)
        before = (hashlib.sha256(checkout.read_bytes()).digest(), checkout.stat().st_mtime_ns)
        write_once_external_report(self.target, "preserved\n", self.conflict)
        self.assertEqual(
            (hashlib.sha256(checkout.read_bytes()).digest(), checkout.stat().st_mtime_ns),
            before,
        )

    def test_dangling_symlink_fails_closed(self):
        self.target.parent.mkdir(parents=True)
        missing = self.root / "missing"
        self.target.symlink_to(missing)
        with self.assertRaisesRegex(ValueError, "conflicting external report"):
            write_once_external_report(self.target, "report\n", self.conflict)
        self.assertTrue(self.target.is_symlink())
        self.assertFalse(missing.exists())
        self.assertEqual(sorted(p.name for p in self.target.parent.iterdir()), ["proof.json"])

    def test_existing_conflict_preserved(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text("original\n")
        with self.assertRaisesRegex(ValueError, "conflicting external report"):
            write_once_external_report(self.target, "conflict\n", self.conflict)
        self.assertEqual(self.target.read_text(), "original\n")


if __name__ == "__main__":
    unittest.main()
