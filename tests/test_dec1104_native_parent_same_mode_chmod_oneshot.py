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
spec = importlib.util.spec_from_file_location("dec677_native_dec1104", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "real native Linux inotify required")
class NativeParentSameModeChmodOneShotRegression(unittest.TestCase):
    def test_same_mode_parent_chmod_disarms_parent_oneshot_before_child_writes(self):
        one_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            found = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(data) - pos)
                name = data[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
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

        def check_real_write(data, source_wd, parent_wd, after):
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
            outcome = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(outcome["status"], "BLOCKED")
            self.assertIs(outcome["can_authorize_dispatch"], False)
            self.assertIs(outcome["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1104-public-parent-same-mode-chmod-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = (os.lstat(sample), os.lstat(parent))
            mode = stat.S_IMODE(initial[1].st_mode)
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

                # The real chmod supplies CURRENT PARENT DIRECTORY permission
                # bits. These mode bits remain equal; ctime may change.
                # This event is an unnamed IN_ATTRIB|IN_ISDIR self event.
                os.chmod(parent, mode)
                self.assertEqual(stat.S_IMODE(os.lstat(parent).st_mode), mode)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_ATTRIB | module.IN_ISDIR, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertCountEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_ATTRIB | module.IN_ISDIR, b"")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                # Second real same-mode chmod is seen only by continuing
                # native parent watch; source inode stays quiet.
                os.chmod(parent, mode)
                self.assertEqual(stat.S_IMODE(os.lstat(parent).st_mode), mode)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertCountEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_ATTRIB | module.IN_ISDIR, b"")],
                )
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                # Subsequent genuine child changed-byte and restoring writes
                # are invisible to removed PARENT one-shot despite originally
                # subscribed MODIFY, CLOSE_WRITE and namespace categories.
                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                check_real_write(changed, source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                check_real_write(restored, source_wd, parent_wd, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = (os.lstat(sample), os.lstat(parent))
                for old, new in zip(initial, final):
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
