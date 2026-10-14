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
spec = importlib.util.spec_from_file_location("dec677_native_dec1089", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "real native Linux inotify only")
class NativeParentSelfAttributeOneShotRegression(unittest.TestCase):
    def test_parent_mode_change_disarms_oneshot_before_real_child_writes(self):
        one_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            found = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, count = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(count, len(data) - pos)
                name = data[pos:pos + count].split(b"\x00", 1)[0]
                pos += count
                self.assertEqual(cookie, 0)
                found.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return found

        def real_write(path, contents):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, contents), len(contents))
                os.fsync(fd)
            finally:
                os.close(fd)

        def assert_independent_write(stream, source_wd, parent_wd, after):
            native = records(stream)
            for expected in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(expected, native)
            parsed = module._classify_stream(stream, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, stream, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1089-public-parent-attr-oneshot-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = (os.lstat(sample), os.lstat(parent))
            first_mode = stat.S_IMODE(first[1].st_mode)
            different_mode = first_mode ^ stat.S_IXGRP
            self.assertNotEqual(different_mode, first_mode)
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
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

                # Mutate ONLY the generated-PUBLIC directory's mode.
                # It triggers a self IN_ATTRIB|IN_ISDIR, not a child write.
                os.chmod(parent, different_mode)
                self.assertEqual(stat.S_IMODE(os.stat(parent).st_mode),
                                 different_mode)
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_ATTRIB | module.IN_ISDIR, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_ATTRIB | module.IN_ISDIR, b"")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                # Restore the original parent mode: the continuing observer
                # sees the reversal, but the removed one-shot stays silent.
                os.chmod(parent, first_mode)
                self.assertEqual(stat.S_IMODE(os.stat(parent).st_mode),
                                 first_mode)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_ATTRIB | module.IN_ISDIR, b"")],
                )
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                # Real child write categories were in the original mask,
                # yet watch removal prevents all subsequent observation.
                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                assert_independent_write(changed, source_wd, parent_wd,
                                         module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                assert_independent_write(restored, source_wd, parent_wd,
                                         module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

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
                os.chmod(parent, first_mode)
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
