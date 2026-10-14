from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1084", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeParentSelfCloseNowriteOneShotRegression(unittest.TestCase):
    def test_parent_directory_read_only_close_removes_write_oneshot_without_open_access(self):
        one_fd = None
        benign_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            out = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, count = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(count, len(data) - pos)
                name = data[pos:pos + count].split(b"\x00", 1)[0]
                pos += count
                self.assertEqual(cookie, 0)
                out.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return out

        def write_real(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_write(data, source_wd, parent_wd, after):
            events = records(data)
            for expected in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(expected, events)
            parsed = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1084-public-self-close-nowrite-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            before = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent), ("sample",))
            try:
                independent_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                benign_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                for fd in (one_fd, benign_fd):
                    self.assertGreater(fd, 2)
                    self.assertNotEqual(fd, independent_fd)
                self.assertNotEqual(one_fd, benign_fd)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    IN_CLOSE_NOWRITE | module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_CREATE | module.IN_DELETE | IN_ONESHOT |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                benign_wd = libc.inotify_add_watch(
                    benign_fd, module._checked_watch_path_bytes(parent),
                    IN_CLOSE_NOWRITE | module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(benign_wd, 0)
                for fd in (one_fd, benign_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # No OPEN/ACCESS bit is subscribed; opening the watched
                # directory inode for read leaves both queues quiet.
                directory_fd = os.open(
                    parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC
                )
                try:
                    self.assertEqual(os.fstat(directory_fd).st_ino,
                                     before[1].st_ino)
                    self.assertEqual(module._read_receipt_pending(one_fd), b"")
                    self.assertEqual(module._read_receipt_pending(benign_fd), b"")
                finally:
                    os.close(directory_fd)

                # The harmless DIRECTORY SELF CLOSE is the first match.
                expected = IN_CLOSE_NOWRITE | module.IN_ISDIR
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, expected, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(benign_fd)),
                    [(benign_wd, expected, b"")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                write_real(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                verify_write(changed, source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                write_real(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                verify_write(restored, source_wd, parent_wd, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                after = (os.lstat(sample), os.lstat(parent))
                for old, new in zip(before, after):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode),
                        (new.st_dev, new.st_ino, new.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                for fd in (one_fd, benign_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
