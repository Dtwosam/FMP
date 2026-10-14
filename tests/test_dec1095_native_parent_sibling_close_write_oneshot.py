from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1095", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "requires native Linux inotify")
class NativeParentSiblingCloseWriteOneShotRegression(unittest.TestCase):
    def test_unrelated_sibling_close_write_disarms_parent_before_sample_writes(self):
        one_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            found = []
            cursor = 0
            while cursor < len(data):
                self.assertGreaterEqual(len(data) - cursor, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, cursor)
                cursor += module.EVENT.size
                self.assertLessEqual(length, len(data) - cursor)
                name = data[cursor:cursor + length].split(b"\x00", 1)[0]
                cursor += length
                self.assertEqual(cookie, 0)
                found.append((wd, mask, name))
            self.assertEqual(cursor, len(data))
            return found

        def genuine_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def assert_source_write(data, source_wd, parent_wd, after):
            native = records(data)
            for expected in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(expected, native)
            parsed = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("public-sibling", "sample"),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1095-public-sibling-close-write-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            sibling = parent / "public-sibling"
            sibling_before = b"DEC1095_PUBLIC_SIBLING_ORIGINAL\n"
            sibling_changed = b"DEC1095_PUBLIC_SIBLING_CHANGED\n"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            self.assertEqual(sibling.write_bytes(sibling_before),
                             len(sibling_before))
            first = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("public-sibling", "sample"))
            try:
                independent_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                self.assertNotEqual(one_fd, independent_fd)
                # Deliberately OMIT MODIFY from this one-shot. The real
                # sibling mutation cannot trigger it until writable CLOSE.
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_CLOSE_WRITE | module.IN_CREATE |
                    module.IN_DELETE | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # A genuine write to another public child emits MODIFY
                # independently, then named CLOSE_WRITE removes the one-shot.
                genuine_write(sibling, sibling_changed)
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_CLOSE_WRITE, b"public-sibling"),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_MODIFY, b"public-sibling"),
                     (parent_wd, module.IN_CLOSE_WRITE, b"public-sibling")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                # A second real sibling write restores its original bytes;
                # independent full parent sees it but removed one-shot cannot.
                genuine_write(sibling, sibling_before)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_MODIFY, b"public-sibling"),
                     (parent_wd, module.IN_CLOSE_WRITE, b"public-sibling")],
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Later writes to a DIFFERENT child are also subscribed as
                # CLOSE_WRITE but no live original watch is left.
                genuine_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                assert_source_write(changed, source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                genuine_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                assert_source_write(restored, source_wd, parent_wd,
                                    module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(sibling.read_bytes(), sibling_before)
                final = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
                for before, after in zip(first, final):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode),
                        (after.st_dev, after.st_ino, after.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("public-sibling", "sample"))
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
