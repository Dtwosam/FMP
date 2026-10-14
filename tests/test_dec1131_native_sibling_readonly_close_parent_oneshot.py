from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1131", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000
IN_CLOSE_NOWRITE = 0x00000010
SIBLING_CONTENT = b"DEC1131_PUBLIC_SIBLING\n"


@unittest.skipUnless(sys.platform == "linux", "real native Linux inotify required")
class NativeSiblingReadOnlyCloseParentOneShotRegression(unittest.TestCase):
    def test_sibling_readonly_close_disarms_parent_oneshot_before_sample_writes(self):
        original_fd = None
        continuing_fd = None
        read_fd = None

        def native(data):
            self.assertIs(type(data), bytes)
            seen = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                seen.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return seen

        def changed_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def assert_observed_real_write(data, source_wd, parent_wd, after):
            observations = native(data)
            permitted = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(all(e in permitted for e in observations))
            for event in permitted:
                self.assertIn(event, observations)
            observed = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(observed["well_formed"])
            self.assertFalse(observed["invalidated"])
            self.assertGreaterEqual(
                observed["source_content_write_events"], 1
            )
            blocked = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("public-sibling", "sample"),
            )
            self.assertEqual(blocked["status"], "BLOCKED")
            self.assertIs(blocked["can_authorize_dispatch"], False)
            self.assertIs(blocked["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1131-public-sibling-read-close-", dir="/tmp"
        ) as temp:
            parent = Path(temp)
            sample = parent / "sample"
            sibling = parent / "public-sibling"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            self.assertEqual(sibling.write_bytes(SIBLING_CONTENT),
                             len(SIBLING_CONTENT))
            original_stat = (os.lstat(sample), os.lstat(sibling),
                             os.lstat(parent))
            self.assertNotEqual(
                (original_stat[0].st_dev, original_stat[0].st_ino),
                (original_stat[1].st_dev, original_stat[1].st_ino),
            )
            self.assertEqual(
                module._bounded_inventory_names(parent),
                ("public-sibling", "sample"),
            )
            try:
                continuing_fd, source_wd, parent_wd = module._start_watch(
                    sample
                )
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                original_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(original_fd, 2)
                self.assertNotEqual(original_fd, continuing_fd)
                original_wd = libc.inotify_add_watch(
                    original_fd, module._checked_watch_path_bytes(parent),
                    IN_CLOSE_NOWRITE | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_CREATE |
                    module.IN_DELETE | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(original_wd, 0)
                self.assertEqual(
                    module._read_receipt_pending(original_fd), b""
                )
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )

                # This is a DIFFERENT child regular-file inode from sample.
                # Read-only open neither writes nor truncates either file.
                read_fd = os.open(
                    sibling, os.O_RDONLY | os.O_CLOEXEC
                )
                self.assertEqual(os.fstat(read_fd).st_size,
                                 len(SIBLING_CONTENT))
                self.assertEqual(
                    module._read_receipt_pending(original_fd), b""
                )
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )
                os.close(read_fd)
                read_fd = None

                # First named read-side close exhausts parent ONESHOT,
                # BEFORE any content mutation in the source sibling sample.
                self.assertEqual(
                    native(module._read_receipt_pending(original_fd)),
                    [(original_wd, IN_CLOSE_NOWRITE, b"public-sibling"),
                     (original_wd, module.IN_IGNORED, b"")],
                )
                # The normal unchanged continuing source+parent helper
                # deliberately excludes CLOSE_NOWRITE. It stays quiet.
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(sibling.read_bytes(), SIBLING_CONTENT)
                self.assertEqual(
                    module._read_receipt_pending(original_fd), b""
                )

                # Subsequent real source content mutation is witnessed
                # independently, but not on the removed original parent.
                changed_write(sample, module.AFTER)
                self.assertEqual(
                    module._read_receipt_pending(original_fd), b""
                )
                assert_observed_real_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )
                changed_write(sample, module.BEFORE)
                self.assertEqual(
                    module._read_receipt_pending(original_fd), b""
                )
                assert_observed_real_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )
                final_stat = (os.lstat(sample), os.lstat(sibling),
                              os.lstat(parent))
                for old, new in zip(original_stat, final_stat):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(sibling.read_bytes(), SIBLING_CONTENT)
                self.assertEqual(
                    module._bounded_inventory_names(parent),
                    ("public-sibling", "sample"),
                )
            finally:
                if read_fd is not None:
                    os.close(read_fd)
                for fd in (original_fd, continuing_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
