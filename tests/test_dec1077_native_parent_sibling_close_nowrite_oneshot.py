from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1077", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeParentSiblingCloseNowriteDisarmsOneShot(unittest.TestCase):
    def test_unrelated_sibling_read_only_close_disarms_parent_without_open_or_access(self):
        one_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            offset = 0
            found = []
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - offset)
                name = data[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                found.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return found

        def write_real(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def assert_independent_writes(stream, source_wd, parent_wd, after):
            observed = records(stream)
            for event in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(event, observed)
            parsed = module._classify_stream(stream, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, stream, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("public-read", "sample"),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1077-public-parent-read-close-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            sibling = parent / "public-read"
            sibling_bytes = b"PUBLIC-SIBLING-READ-CLOSE"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            self.assertEqual(sibling.write_bytes(sibling_bytes), len(sibling_bytes))
            initial = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("public-read", "sample"))
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
                one_parent_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    IN_CLOSE_NOWRITE | module.IN_CREATE | module.IN_DELETE |
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_parent_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Neither OPEN nor ACCESS is subscribed: a real open/read of
                # the UNRELATED public sibling must leave the one-shot armed.
                read_fd = os.open(sibling, os.O_RDONLY)
                try:
                    self.assertEqual(module._read_receipt_pending(one_fd), b"")
                    self.assertEqual(os.read(read_fd, len(sibling_bytes)),
                                     sibling_bytes)
                    self.assertEqual(module._read_receipt_pending(one_fd), b"")
                finally:
                    os.close(read_fd)

                # The harmless read-only close consumes the parent watch:
                # a named CLOSE_NOWRITE then the kernel's watch-removal event.
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [
                        (one_parent_wd, IN_CLOSE_NOWRITE, b"public-read"),
                        (one_parent_wd, module.IN_IGNORED, b""),
                    ],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Writes to a DIFFERENT child later are missed despite the
                # original parent's explicit MODIFY and CLOSE_WRITE bits.
                write_real(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                assert_independent_writes(changed, source_wd, parent_wd,
                                          module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                write_real(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                assert_independent_writes(restored, source_wd, parent_wd,
                                          module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(sibling.read_bytes(), sibling_bytes)
                final = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
                for old, new in zip(initial, final):
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
