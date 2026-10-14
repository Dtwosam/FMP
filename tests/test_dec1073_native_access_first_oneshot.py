from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1073", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ACCESS = 0x00000001
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeSourceReadAccessFirstOneShotRegression(unittest.TestCase):
    def test_access_without_open_subscription_removes_write_watch_before_actual_write(self):
        one_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            found = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                found.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return found

        def write_real(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_independent(receipt, source_wd, parent_wd, after):
            found = records(receipt)
            for expected in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(expected, found)
            parsed = module._classify_stream(receipt, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, receipt, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1073-public-access-first-oneshot-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent), ("sample",))
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
                    one_fd, module._checked_watch_path_bytes(sample),
                    IN_ACCESS | module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # This mask deliberately excludes IN_OPEN: opening for read
                # does not itself consume the one-shot registration.
                read_fd = os.open(sample, os.O_RDONLY)
                try:
                    self.assertEqual(module._read_receipt_pending(one_fd), b"")
                    self.assertEqual(os.read(read_fd, len(module.BEFORE)),
                                     module.BEFORE)
                    # The non-mutating *read* is first matching IN_ACCESS;
                    # native IN_IGNORED shows the kernel removed the watch.
                    self.assertEqual(
                        records(module._read_receipt_pending(one_fd)),
                        [
                            (one_wd, IN_ACCESS, b""),
                            (one_wd, module.IN_IGNORED, b""),
                        ],
                    )
                finally:
                    os.close(read_fd)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # A genuine later write is masked out by watch lifetime,
                # NOT an omitted IN_MODIFY / IN_CLOSE_WRITE subscription.
                write_real(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                verify_independent(changed, source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Restoring original bytes cannot retroactively recover
                # the lost history of the disarmed source one-shot.
                write_real(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                verify_independent(restored, source_wd, parent_wd, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = (os.lstat(sample), os.lstat(parent))
                for old, new in zip(first, last):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode),
                        (new.st_dev, new.st_ino, new.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
