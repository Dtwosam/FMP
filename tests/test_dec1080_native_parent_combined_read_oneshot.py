from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1080", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_ACCESS = 0x00000001
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify only")
class NativeParentCompleteReadMaskOneShotRegression(unittest.TestCase):
    def test_sibling_open_first_loses_subscribed_access_close_and_later_sample_write(self):
        one_fd = None
        benign_fd = None
        independent_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            found = []
            offset = 0
            while offset < len(stream):
                self.assertGreaterEqual(len(stream) - offset, module.EVENT.size)
                wd, mask, cookie, count = module.EVENT.unpack_from(stream, offset)
                offset += module.EVENT.size
                self.assertLessEqual(count, len(stream) - offset)
                name = stream[offset:offset + count].split(b"\x00", 1)[0]
                offset += count
                self.assertEqual(cookie, 0)
                found.append((wd, mask, name))
            self.assertEqual(offset, len(stream))
            return found

        def write_real(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def prove_write(stream, source_wd, parent_wd, after):
            events = records(stream)
            for event in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(event, events)
            parsed = module._classify_stream(stream, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            decision = module._evaluate(
                module.BEFORE, after, stream, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("public-read", "sample"),
            )
            self.assertEqual(decision["status"], "BLOCKED")
            self.assertIs(decision["can_authorize_dispatch"], False)
            self.assertIs(decision["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1080-public-parent-all-read-mask-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            sibling = parent / "public-read"
            sibling_bytes = b"PUBLIC-READ-WITNESS"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            self.assertEqual(sibling.write_bytes(sibling_bytes), len(sibling_bytes))
            first = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("public-read", "sample"))
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
                for fd in (one_fd, benign_fd):
                    self.assertGreater(fd, 2)
                    self.assertNotEqual(fd, independent_fd)
                self.assertNotEqual(one_fd, benign_fd)
                read_mask = IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE
                one_parent_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    read_mask | module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_CREATE | module.IN_DELETE | IN_ONESHOT |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                benign_parent_wd = libc.inotify_add_watch(
                    benign_fd, module._checked_watch_path_bytes(parent),
                    read_mask | module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_parent_wd, 0)
                self.assertGreater(benign_parent_wd, 0)
                for fd in (one_fd, benign_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # A real OPEN/READ/CLOSE of a DIFFERENT child emits all three
                # read categories. One-shot sees only first OPEN then IGNORED.
                read_fd = os.open(sibling, os.O_RDONLY)
                try:
                    self.assertEqual(os.read(read_fd, len(sibling_bytes)),
                                     sibling_bytes)
                finally:
                    os.close(read_fd)
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_parent_wd, IN_OPEN, b"public-read"),
                     (one_parent_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(benign_fd)),
                    [(benign_parent_wd, IN_OPEN, b"public-read"),
                     (benign_parent_wd, IN_ACCESS, b"public-read"),
                     (benign_parent_wd, IN_CLOSE_NOWRITE, b"public-read")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                # Real changes to watched sample are invisible on the
                # removed parent one-shot despite subscribed write masks.
                write_real(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                prove_write(changed, source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                write_real(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                prove_write(restored, source_wd, parent_wd, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(sibling.read_bytes(), sibling_bytes)
                final = (os.lstat(sample), os.lstat(sibling), os.lstat(parent))
                for initial, latest in zip(first, final):
                    self.assertEqual(
                        (initial.st_dev, initial.st_ino, initial.st_mode),
                        (latest.st_dev, latest.st_ino, latest.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("public-read", "sample"))
            finally:
                for fd in (one_fd, benign_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
