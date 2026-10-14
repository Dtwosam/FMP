from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1076", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ACCESS = 0x00000001
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeParentSiblingReadAccessDisarmsOneShotRegression(unittest.TestCase):
    def test_unrelated_child_access_without_open_subscription_hides_sample_writes(self):
        one_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            pos = 0
            events = []
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, count = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(count, len(data) - pos)
                name = data[pos:pos + count].split(b"\x00", 1)[0]
                pos += count
                self.assertEqual(cookie, 0)
                events.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return events

        def real_write(path, data):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, data), len(data))
                os.fsync(fd)
            finally:
                os.close(fd)

        def assert_independent(data, source_wd, parent_wd, after):
            actual = records(data)
            for expected in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(expected, actual)
            parsed = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            outcome = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("public-read", "sample"),
            )
            self.assertEqual(outcome["status"], "BLOCKED")
            self.assertIs(outcome["can_authorize_dispatch"], False)
            self.assertIs(outcome["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1076-public-parent-access-sibling-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            sibling = parent / "public-read"
            sibling_bytes = b"PUBLIC-SIBLING-ACCESS"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            self.assertEqual(sibling.write_bytes(sibling_bytes), len(sibling_bytes))
            first = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("public-read", "sample"))
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
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    IN_ACCESS | module.IN_CREATE | module.IN_DELETE |
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Opening an unrelated child cannot trigger this one-shot:
                # the mask deliberately contains NO IN_OPEN event.
                read_fd = os.open(sibling, os.O_RDONLY)
                try:
                    self.assertEqual(module._read_receipt_pending(one_fd), b"")
                    self.assertEqual(os.read(read_fd, len(sibling_bytes)),
                                     sibling_bytes)
                    self.assertEqual(
                        records(module._read_receipt_pending(one_fd)),
                        [
                            (one_wd, IN_ACCESS, b"public-read"),
                            (one_wd, module.IN_IGNORED, b""),
                        ],
                    )
                finally:
                    os.close(read_fd)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Reading a different inode removed ALL parent mutation
                # coverage before the actual watched sample was written.
                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                assert_independent(changed, source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                assert_independent(restored, source_wd, parent_wd, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(sibling.read_bytes(), sibling_bytes)
                last = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
                for old, new in zip(first, last):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode),
                        (new.st_dev, new.st_ino, new.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("public-read", "sample"))
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
