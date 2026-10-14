from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1087", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ACCESS = 0x00000001
IN_CLOSE_NOWRITE = 0x00000010
IN_OPEN = 0x00000020
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeParentScandirCombinedReadOneShotRegression(unittest.TestCase):
    def test_scandir_self_open_first_masks_own_access_close_and_later_sample_writes(self):
        one_fd = None
        benign_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            out = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                out.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return out

        def real_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_write(receipt, source_wd, parent_wd, after):
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
                directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1087-public-parent-self-scandir-mask-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            before = (os.lstat(sample), os.lstat(parent))
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

                read_mask = IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    read_mask | module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_CREATE | module.IN_DELETE | IN_ONESHOT |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                benign_wd = libc.inotify_add_watch(
                    benign_fd, module._checked_watch_path_bytes(parent),
                    read_mask | module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(benign_wd, 0)
                for fd in (one_fd, benign_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Genuine directory SELF enumeration emits OPEN then ACCESS
                # then CLOSE_NOWRITE, all flagged IN_ISDIR and unnamed.
                # The original IN_ONESHOT stops at the first self OPEN.
                with os.scandir(parent) as entries:
                    names = tuple(entry.name for entry in entries)
                self.assertEqual(names, ("sample",))
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, IN_OPEN | module.IN_ISDIR, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(benign_fd)),
                    [(benign_wd, IN_OPEN | module.IN_ISDIR, b""),
                     (benign_wd, IN_ACCESS | module.IN_ISDIR, b""),
                     (benign_wd, IN_CLOSE_NOWRITE | module.IN_ISDIR, b"")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                # The normal full mutation watcher omits all benign read
                # events, so genuine harmless enumeration leaves it quiet.
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                verify_write(changed, source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                verify_write(restored, source_wd, parent_wd, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                after = (os.lstat(sample), os.lstat(parent))
                for old, new in zip(before, after):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode),
                        (new.st_dev, new.st_ino, new.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                for fd in (one_fd, benign_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
