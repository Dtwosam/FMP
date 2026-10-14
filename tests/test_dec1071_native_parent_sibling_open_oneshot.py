from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1071", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux parent inotify only")
class NativeParentUnrelatedReadDisarmsOneshotRegression(unittest.TestCase):
    def test_read_of_unrelated_sibling_disarms_full_parent_mask_before_source_write(self):
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

        def genuine_sample_write(sample, content):
            fd = os.open(sample, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def assert_independent_write(receipt, source_wd, parent_wd, after):
            native = records(receipt)
            for event in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(event, native)
            parsed = module._classify_stream(receipt, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, receipt, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("public-read", "sample"),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1071-public-parent-sibling-open-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            sibling = parent / "public-read"
            sibling_bytes = b"PUBLIC-SIBLING-READ"
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
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    IN_OPEN | module.IN_CREATE | module.IN_DELETE |
                    module.IN_MODIFY | module.IN_CLOSE_WRITE | IN_ONESHOT |
                    module.IN_DONT_FOLLOW | module.IN_ONLYDIR,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # The first event is a READ-ONLY open of a DIFFERENT child.
                # Although the mask includes source mutations, the parent
                # one-shot is removed before any write to sample occurs.
                read_fd = os.open(sibling, os.O_RDONLY)
                try:
                    self.assertEqual(os.read(read_fd, len(sibling_bytes)),
                                     sibling_bytes)
                finally:
                    os.close(read_fd)
                self.assertEqual(records(module._read_receipt_pending(one_fd)), [
                    (one_wd, IN_OPEN, b"public-read"),
                    (one_wd, module.IN_IGNORED, b""),
                ])
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                genuine_sample_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                assert_independent_write(changed, source_wd, parent_wd,
                                         module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Restoring sample does not revive the parent watch; the
                # continuously registered independent witness still sees it.
                genuine_sample_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                assert_independent_write(restored, source_wd, parent_wd,
                                         module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(sibling.read_bytes(), sibling_bytes)
                final = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
                for first, last in zip(initial, final):
                    self.assertEqual(
                        (first.st_dev, first.st_ino, first.st_mode),
                        (last.st_dev, last.st_ino, last.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("public-read", "sample"))
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
