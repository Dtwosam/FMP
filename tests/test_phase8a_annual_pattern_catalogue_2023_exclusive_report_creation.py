from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fmp.discovery.annual_pattern_catalogue_2023_external_report_create import write_once_external_report


class ExclusiveAuditReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.target = self.root / 'reports' / 'proof.json'
        self.conflict = 'DEC-635 conflicting external report'

    def test_new_file_and_identical_repeated_report_no_rewrite(self):
        write_once_external_report(self.target, 'proof\n', self.conflict)
        stat = self.target.stat()
        write_once_external_report(self.target, 'proof\n', self.conflict)
        self.assertEqual(self.target.read_text(), 'proof\n')
        self.assertEqual(self.target.stat().st_ino, stat.st_ino)
        self.assertEqual(self.target.stat().st_mtime_ns, stat.st_mtime_ns)

    def test_existing_conflict_is_untouched(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text('original\n')
        with self.assertRaisesRegex(ValueError, 'conflicting external report'):
            write_once_external_report(self.target, 'replacement\n', self.conflict)
        self.assertEqual(self.target.read_text(), 'original\n')

    def test_competing_file_at_exclusive_open_is_not_overwritten(self):
        real_open = Path.open
        triggered = []
        def competing_open(path, mode='r', *args, **kwargs):
            if path == self.target and mode == 'x':
                triggered.append(True)
                with real_open(path, 'w', encoding='utf-8') as handle:
                    handle.write('competitor\n')
            return real_open(path, mode, *args, **kwargs)
        with mock.patch.object(Path, 'open', new=competing_open):
            with self.assertRaisesRegex(ValueError, 'conflicting external report'):
                write_once_external_report(self.target, 'ours\n', self.conflict)
        self.assertEqual(triggered, [True])
        self.assertEqual(self.target.read_text(), 'competitor\n')

    def test_competing_identical_file_is_not_rewritten(self):
        real_open = Path.open
        triggered = []
        def competing_open(path, mode='r', *args, **kwargs):
            if path == self.target and mode == 'x':
                triggered.append(True)
                with real_open(path, 'w', encoding='utf-8') as handle:
                    handle.write('proof\n')
            return real_open(path, mode, *args, **kwargs)
        with mock.patch.object(Path, 'open', new=competing_open):
            write_once_external_report(self.target, 'proof\n', self.conflict)
        self.assertEqual(triggered, [True])
        self.assertEqual(self.target.read_text(), 'proof\n')

    def test_dangling_symlink_never_creates_through_target(self):
        self.target.parent.mkdir(parents=True)
        destination = self.root / 'nonexistent-original'
        self.target.symlink_to(destination)
        with self.assertRaisesRegex(ValueError, 'conflicting external report'):
            write_once_external_report(self.target, 'proof\n', self.conflict)
        self.assertTrue(self.target.is_symlink())
        self.assertFalse(destination.exists())

    def test_existing_identical_checkout_hardlink_keeps_bytes_and_mtime(self):
        checkout = self.root / 'checkout.txt'
        checkout.write_text('inventory\n')
        before = (hashlib.sha256(checkout.read_bytes()).hexdigest(), checkout.stat().st_mtime_ns)
        self.target.parent.mkdir(parents=True)
        self.target.hardlink_to(checkout)
        write_once_external_report(self.target, 'inventory\n', self.conflict)
        self.assertEqual((hashlib.sha256(checkout.read_bytes()).hexdigest(), checkout.stat().st_mtime_ns), before)

    def test_helper_is_only_leaf_exclusive_create_not_annual_dispatch(self):
        src = (Path(__file__).resolve().parents[1] / 'src' / 'fmp' / 'discovery' / 'annual_pattern_catalogue_2023_external_report_create.py').read_text()
        self.assertIn('target.open("x", encoding="utf-8")', src)
        self.assertNotIn('target.write_text(', src)
        self.assertNotIn('subprocess', src)
        self.assertNotIn('requests', src)


if __name__ == '__main__':
    unittest.main()
