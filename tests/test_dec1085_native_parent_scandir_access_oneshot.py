from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1085", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ACCESS = 0x00000001
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeParentSelfAccessScandirOneShotRegression(unittest.TestCase):
    def test_scandir_of_watched_directory_consumes_access_oneshot_before_write(self):
        one_fd = None
        benign_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            pos = 0
            parsed = []
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(data) - pos)
                name = data[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return parsed

        def write_real(path, data):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, data), len(data))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_mutation(receipt, source_wd, parent_wd, after):
            native = records(receipt)
            for expected in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(expected, native)
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
            prefix="dec1085-public-self-scandir-access-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = (os.lstat(sample), os.lstat(parent))
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
                benign_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                self.assertGreater(benign_fd, 2)
                self.assertNotEqual(one_fd, benign_fd)
                for fd in (one_fd, benign_fd):
                    self.assertNotEqual(fd, independent_fd)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    IN_ACCESS | module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_CREATE | module.IN_DELETE | IN_ONESHOT |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                benign_wd = libc.inotify_add_watch(
                    benign_fd, module._checked_watch_path_bytes(parent),
                    IN_ACCESS | module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(benign_wd, 0)
                for fd in (one_fd, benign_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Actual enumeration of the WATCHED DIRECTORY itself
                # generates an unnamed native IN_ACCESS|IN_ISDIR.
                # Neither OPEN nor CLOSE_NOWRITE is subscribed.
                with os.scandir(parent) as entries:
                    names = tuple(entry.name for entry in entries)
                self.assertEqual(names, ("sample",))
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, IN_ACCESS | module.IN_ISDIR, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(benign_fd)),
                    [(benign_wd, IN_ACCESS | module.IN_ISDIR, b"")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                write_real(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                verify_mutation(changed, source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                write_real(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                verify_mutation(restored, source_wd, parent_wd, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = (os.lstat(sample), os.lstat(parent))
                for before, after in zip(initial, final):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode),
                        (after.st_dev, after.st_ino, after.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                for fd in (one_fd, benign_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
