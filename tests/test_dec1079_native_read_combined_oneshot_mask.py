from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1079", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_ACCESS = 0x00000001
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeCombinedBenignReadOneShotMaskRegression(unittest.TestCase):
    def test_open_first_loses_subscribed_access_and_close_then_actual_write(self):
        one_fd = None
        independent_fd = None
        read_witness_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            cursor = 0
            parsed = []
            while cursor < len(data):
                self.assertGreaterEqual(len(data) - cursor, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, cursor)
                cursor += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - cursor)
                name = data[cursor:cursor + nbytes].split(b"\x00", 1)[0]
                cursor += nbytes
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(cursor, len(data))
            return parsed

        def real_write(path, data):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, data), len(data))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_write(data, source_wd, parent_wd, after):
            events = records(data)
            for item in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(item, events)
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
            prefix="dec1079-public-read-both-mask-oneshot-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = (os.lstat(sample), os.lstat(parent))
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
                read_witness_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(one_fd, 2)
                self.assertGreater(read_witness_fd, 2)
                self.assertNotEqual(one_fd, read_witness_fd)
                self.assertNotEqual(one_fd, independent_fd)
                self.assertNotEqual(read_witness_fd, independent_fd)
                read_actions = IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample),
                    read_actions | module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                read_wd = libc.inotify_add_watch(
                    read_witness_fd, module._checked_watch_path_bytes(sample),
                    read_actions | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(read_wd, 0)
                for fd in (one_fd, independent_fd, read_witness_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # One genuine read-only open/read/close produces ALL three
                # independently witnessed benign events. The complete-mask
                # one-shot sees ONLY the first OPEN then its removal receipt.
                read_fd = os.open(sample, os.O_RDONLY)
                try:
                    self.assertEqual(os.read(read_fd, len(module.BEFORE)),
                                     module.BEFORE)
                finally:
                    os.close(read_fd)
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, IN_OPEN, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(read_witness_fd)),
                    [(read_wd, IN_OPEN, b""),
                     (read_wd, IN_ACCESS, b""),
                     (read_wd, IN_CLOSE_NOWRITE, b"")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                # Normal full mutation witness intentionally omits benign
                # read categories and remains quiet before actual writes.
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                verify_write(changed, source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                verify_write(restored, source_wd, parent_wd, module.BEFORE)
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
                for fd in (one_fd, independent_fd, read_witness_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
