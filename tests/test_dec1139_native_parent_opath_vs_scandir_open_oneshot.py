from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1139", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000
IN_OPEN = 0x00000020


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "O_PATH"),
                     "native Linux inotify and O_PATH required")
class NativeParentOPathVersusScandirOpenOneShotRegression(unittest.TestCase):
    def test_opath_directory_quiet_before_scandir_consumes_parent_open_oneshot(self):
        original_fd = None
        continuing_fd = None
        path_fd = None

        def events(data):
            self.assertIs(type(data), bytes)
            seen = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset,
                                        module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(
                    data, offset
                )
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - offset)
                name = data[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                seen.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return seen

        def actual_write(path, content):
            writable_fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(writable_fd, content),
                                 len(content))
                os.fsync(writable_fd)
            finally:
                os.close(writable_fd)

        def verify_real_write(data, source_wd, parent_wd, after):
            native = events(data)
            for item in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(item, native)
            allowed = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(all(item in allowed for item in native))
            parsed = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(
                parsed["source_content_write_events"], 1,
            )
            result = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIs(result["can_authorize_dispatch"], False)
            self.assertIs(result["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            dir="/tmp", prefix="dec1139-public-parent-opath-scandir-"
        ) as temp:
            parent = Path(temp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            initial = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(
                module._bounded_inventory_names(parent), ("sample",)
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
                one_wd = libc.inotify_add_watch(
                    original_fd, module._checked_watch_path_bytes(parent),
                    IN_OPEN | module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_CREATE | module.IN_DELETE | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(
                    module._read_receipt_pending(original_fd), b""
                )
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )

                # Linux O_PATH|O_DIRECTORY obtains a path-only descriptor
                # for the watched parent inode. Unlike os.scandir, it does
                # NOT emit IN_OPEN|IN_ISDIR, either on open or close.
                path_fd = os.open(
                    parent, os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC
                )
                self.assertEqual(os.fstat(path_fd).st_ino,
                                 initial[1].st_ino)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")
                os.close(path_fd)
                path_fd = None
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                # The REAL bounded-inventory helper itself uses os.scandir
                # to open the watched DIRECTORY for enumeration. This
                # should disarm only the intentionally unsafe parent
                # IN_OPEN|IN_ONESHOT registration. No source file is opened.
                self.assertEqual(
                    module._bounded_inventory_names(parent), ("sample",)
                )
                self.assertEqual(
                    events(module._read_receipt_pending(original_fd)),
                    [(one_wd, IN_OPEN | module.IN_ISDIR, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                # The normal continuing helper deliberately subscribes to
                # source/parent mutation, not opening directories for reads.
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    module._bounded_inventory_names(parent), ("sample",)
                )
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )

                # Genuine later changed-byte and restoring writes on this
                # same inode must remain invisible to original one-shot,
                # but produce independent native source+parent evidence.
                actual_write(sample, module.AFTER)
                self.assertEqual(
                    module._read_receipt_pending(original_fd), b""
                )
                verify_real_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )
                actual_write(sample, module.BEFORE)
                self.assertEqual(
                    module._read_receipt_pending(original_fd), b""
                )
                verify_real_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )
                final = (os.lstat(sample), os.lstat(parent))
                for before, after in zip(initial, final):
                    self.assertEqual(
                        (before.st_dev, before.st_ino,
                         before.st_mode, before.st_nlink),
                        (after.st_dev, after.st_ino,
                         after.st_mode, after.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    module._bounded_inventory_names(parent), ("sample",)
                )
            finally:
                for fd in (path_fd, original_fd, continuing_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
