from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1098", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "requires native Linux inotify")
class NativeParentSiblingNoopWritableCloseOneShotRegression(unittest.TestCase):
    def test_noop_sibling_writable_close_consumes_parent_before_actual_sample_write(self):
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

        def real_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def assert_real_sample_write(data, source_wd, parent_wd, after):
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
            result = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("public-sibling", "sample"),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIs(result["can_authorize_dispatch"], False)
            self.assertIs(result["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1098-public-sibling-noop-writable-close-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            sibling = parent / "public-sibling"
            sibling_bytes = b"DEC1098_PUBLIC_SIBLING_UNCHANGED\n"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            self.assertEqual(sibling.write_bytes(sibling_bytes),
                             len(sibling_bytes))
            before = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("public-sibling", "sample"))
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
                self.assertNotEqual(one_fd, independent_fd)
                # Even with both mutation categories subscribed, a merely
                # writable (never written) descriptor will produce CLOSE_WRITE.
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_CREATE | module.IN_DELETE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # No O_TRUNC, no write(), no fsync(): this sibling operation
                # makes no content change and emits no native IN_MODIFY.
                writable_fd = os.open(sibling, os.O_WRONLY | os.O_CLOEXEC)
                try:
                    self.assertEqual(os.fstat(writable_fd).st_size,
                                     len(sibling_bytes))
                    self.assertEqual(module._read_receipt_pending(one_fd), b"")
                    self.assertEqual(module._read_receipt_pending(independent_fd),
                                     b"")
                finally:
                    os.close(writable_fd)

                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_CLOSE_WRITE, b"public-sibling"),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_CLOSE_WRITE, b"public-sibling")],
                )
                self.assertEqual(sibling.read_bytes(), sibling_bytes)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                # A genuinely changed-byte write to a DIFFERENT child occurs
                # later, but its full native mutation history is invisible
                # to the original, already removed parent one-shot.
                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                assert_real_sample_write(changed, source_wd, parent_wd,
                                         module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                assert_real_sample_write(restored, source_wd, parent_wd,
                                         module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(sibling.read_bytes(), sibling_bytes)
                final = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
                for earlier, later in zip(before, final):
                    self.assertEqual(
                        (earlier.st_dev, earlier.st_ino, earlier.st_mode),
                        (later.st_dev, later.st_ino, later.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("public-sibling", "sample"))
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
