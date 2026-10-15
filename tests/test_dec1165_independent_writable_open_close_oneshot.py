from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1165", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "pwrite"),
                     "requires Linux native inotify and pwrite")
class NativeIndependentWritableOpenCloseOneShotRegression(unittest.TestCase):
    def test_independent_writable_opens_emit_separate_close_write_despite_other_fd(self):
        original_fd = None
        normal_fd = None
        first_fd = None
        second_fd = None

        def records(receipt):
            self.assertIs(type(receipt), bytes)
            result = []
            idx = 0
            while idx < len(receipt):
                self.assertGreaterEqual(len(receipt) - idx,
                                        module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(
                    receipt, idx
                )
                idx += module.EVENT.size
                self.assertLessEqual(nbytes, len(receipt) - idx)
                name = receipt[idx:idx + nbytes].split(b"\x00", 1)[0]
                idx += nbytes
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(idx, len(receipt))
            return result

        def check_write_stage(raw, source_wd, parent_wd, changed_from,
                              changed_to, with_close):
            observed = records(raw)
            allowed = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
            }
            if with_close:
                allowed.update({
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                })
            self.assertTrue(observed)
            self.assertTrue(all(e in allowed for e in observed))
            for required in allowed:
                self.assertIn(required, observed)
            result = module._evaluate(
                changed_from, changed_to, raw, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIs(result["can_authorize_dispatch"], False)
            self.assertIs(result["independent_os_proof_verified"], False)

        source_change_at = module.BEFORE.index(b"SOURCE")
        changed = (module.BEFORE[:source_change_at] + b"X" +
                   module.BEFORE[source_change_at + 1:])
        self.assertEqual(len(changed), len(module.BEFORE))
        self.assertNotEqual(changed, module.BEFORE)

        with tempfile.TemporaryDirectory(
            dir="/tmp", prefix="dec1165-public-independent-opens-"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            initial = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            try:
                normal_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                original_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(original_fd, 2)
                self.assertNotEqual(original_fd, normal_fd)
                one_wd = libc.inotify_add_watch(
                    original_fd, module._checked_watch_path_bytes(sample),
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW |
                    IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Two independent os.open calls create TWO distinct open
                # file descriptions, unlike os.dup of one open descriptor.
                # Both are writable but have not yet written any bytes.
                first_fd = os.open(
                    sample, os.O_WRONLY | os.O_CLOEXEC
                )
                second_fd = os.open(
                    sample, os.O_WRONLY | os.O_CLOEXEC
                )
                self.assertNotEqual(first_fd, second_fd)
                self.assertEqual(os.fstat(first_fd).st_ino,
                                 os.fstat(second_fd).st_ino)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Closing FIRST open description emits real CLOSE_WRITE,
                # even though another independent writer remains open.
                # No content write happened: CLOSE_WRITE is not sufficient
                # to conclude bytes were changed.
                os.close(first_fd)
                first_fd = None
                self.assertEqual(
                    records(module._read_receipt_pending(original_fd)),
                    [(one_wd, module.IN_CLOSE_WRITE, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertCountEqual(
                    records(module._read_receipt_pending(normal_fd)),
                    [(source_wd, module.IN_CLOSE_WRITE, b""),
                     (parent_wd, module.IN_CLOSE_WRITE, b"sample")],
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)

                # Surviving INDEPENDENT open description genuinely writes
                # changed bytes and later closes, producing normal source
                # +parent MODIFY and second CLOSE_WRITE. Original ONESHOT
                # is already removed after first open-description close.
                self.assertEqual(os.pwrite(second_fd, changed, 0),
                                 len(changed))
                os.fsync(second_fd)
                modify = module._read_receipt_pending(normal_fd)
                check_write_stage(modify, source_wd, parent_wd,
                                  module.BEFORE, changed, False)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")

                os.close(second_fd)
                second_fd = None
                self.assertCountEqual(
                    records(module._read_receipt_pending(normal_fd)),
                    [(source_wd, module.IN_CLOSE_WRITE, b""),
                     (parent_wd, module.IN_CLOSE_WRITE, b"sample")],
                )
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(sample.read_bytes(), changed)

                second_fd = os.open(
                    sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC
                )
                self.assertEqual(os.write(second_fd, module.BEFORE),
                                 len(module.BEFORE))
                os.fsync(second_fd)
                os.close(second_fd)
                second_fd = None
                restore = module._read_receipt_pending(normal_fd)
                check_write_stage(restore, source_wd, parent_wd,
                                  changed, module.BEFORE, True)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)

                last = (os.lstat(sample), os.lstat(parent))
                for before, after in zip(initial, last):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
            finally:
                for fd in (first_fd, second_fd, original_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
