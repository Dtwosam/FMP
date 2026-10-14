from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1069", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "requires real native Linux inotify")
class NativeSourceOpenFirstOneshotRegression(unittest.TestCase):
    def test_read_only_open_or_write_open_disarms_full_source_mask(self):
        one_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            pos = 0
            found = []
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

        def real_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def assert_independent_write(data, source_wd, parent_wd):
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

        with tempfile.TemporaryDirectory(
            prefix="dec1069-public-open-first-oneshot-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(parent)
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
                self.assertGreater(one_fd, 2)

                def register():
                    wd = libc.inotify_add_watch(
                        one_fd, module._checked_watch_path_bytes(sample),
                        IN_OPEN | module.IN_MODIFY | module.IN_CLOSE_WRITE |
                        module.IN_DONT_FOLLOW | IN_ONESHOT,
                    )
                    self.assertGreater(wd, 0)
                    return wd

                first_wd = register()
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # A harmless real read-only open matches IN_OPEN and
                # destroys the watch BEFORE any mutation has occurred.
                read_fd = os.open(sample, os.O_RDONLY)
                try:
                    self.assertEqual(os.read(read_fd, len(module.BEFORE)),
                                     module.BEFORE)
                finally:
                    os.close(read_fd)
                self.assertEqual(records(module._read_receipt_pending(one_fd)), [
                    (first_wd, IN_OPEN, b""),
                    (first_wd, module.IN_IGNORED, b""),
                ])
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                # Independent full source+parent instance excludes read-only
                # OPEN/CLOSE_NOWRITE and correctly stays quiet so far.
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Real changed-byte write and writable close are BOTH
                # in original one-shot mask but the watch is gone.
                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                first_actual = module._read_receipt_pending(independent_fd)
                assert_independent_write(first_actual, source_wd, parent_wd)
                blocked = module._evaluate(
                    module.BEFORE, module.AFTER, first_actual, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(blocked["status"], "BLOCKED")
                self.assertIs(blocked["can_authorize_dispatch"], False)
                self.assertIs(blocked["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # A SECOND native registration with precisely the same mask
                # is consumed by the OPEN of its own later writable handle.
                second_wd = register()
                self.assertNotEqual(first_wd, second_wd)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                real_write(sample, module.BEFORE)
                self.assertEqual(records(module._read_receipt_pending(one_fd)), [
                    (second_wd, IN_OPEN, b""),
                    (second_wd, module.IN_IGNORED, b""),
                ])
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                second_actual = module._read_receipt_pending(independent_fd)
                assert_independent_write(second_actual, source_wd, parent_wd)
                restored = module._evaluate(
                    module.BEFORE, module.BEFORE, second_actual, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(restored["status"], "BLOCKED")
                self.assertIs(restored["can_authorize_dispatch"], False)
                self.assertIs(
                    restored["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                parent_last = os.lstat(parent)
                for before, after in (
                    (initial, last), (parent_initial, parent_last)
                ):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode),
                        (after.st_dev, after.st_ino, after.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
