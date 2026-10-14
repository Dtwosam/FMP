from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1093", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "requires native Linux inotify")
class NativeParentUnrelatedSiblingAttribOneShotRegression(unittest.TestCase):
    def test_sibling_chmod_consumes_parent_oneshot_before_real_sample_writes(self):
        one_fd = None
        independent_fd = None

        def records(data):
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

        def genuine_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_independent_sample_write(data, source_wd, parent_wd, after):
            seen = records(data)
            for event in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(event, seen)
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
            prefix="dec1093-public-sibling-attrib-oneshot-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            sibling = parent / "public-sibling"
            sibling_content = b"DEC1093_PUBLIC_SIBLING\n"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            self.assertEqual(sibling.write_bytes(sibling_content),
                             len(sibling_content))
            first = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
            original_mode = stat.S_IMODE(first[1].st_mode)
            modified_mode = original_mode ^ stat.S_IXUSR
            self.assertNotEqual(modified_mode, original_mode)
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
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_ATTRIB | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_CREATE |
                    module.IN_DELETE | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # The first real operation is on a DIFFERENT public inode.
                # This must be a NAMED parent IN_ATTRIB, not an unnamed
                # watched-directory self IN_ATTRIB|IN_ISDIR record.
                os.chmod(sibling, modified_mode)
                self.assertEqual(stat.S_IMODE(os.stat(sibling).st_mode),
                                 modified_mode)
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_ATTRIB, b"public-sibling"),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_ATTRIB, b"public-sibling")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                # A second real chmod restores original sibling metadata,
                # but never recreates the automatically removed one-shot.
                os.chmod(sibling, original_mode)
                self.assertEqual(stat.S_IMODE(os.stat(sibling).st_mode),
                                 original_mode)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_ATTRIB, b"public-sibling")],
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                genuine_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                verify_independent_sample_write(changed, source_wd, parent_wd,
                                                module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                genuine_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                verify_independent_sample_write(restored, source_wd, parent_wd,
                                                module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(sibling.read_bytes(), sibling_content)
                final = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
                for before, after in zip(first, final):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode),
                        (after.st_dev, after.st_ino, after.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("public-sibling", "sample"))
            finally:
                os.chmod(sibling, original_mode)
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
