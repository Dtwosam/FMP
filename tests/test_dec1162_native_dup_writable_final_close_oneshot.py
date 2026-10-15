from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1162", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "pwrite"),
                     "requires native Linux inotify and pwrite")
class NativeDupWritableFinalCloseOneShotRegression(unittest.TestCase):
    def test_dup_writable_fd_defers_close_write_until_last_duplicate_closes(self):
        original_fd = None
        normal_fd = None
        writer_fd = None
        duplicate_fd = None

        def events(receipt):
            self.assertIs(type(receipt), bytes)
            parsed = []
            off = 0
            while off < len(receipt):
                self.assertGreaterEqual(len(receipt) - off, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(
                    receipt, off
                )
                off += module.EVENT.size
                self.assertLessEqual(nbytes, len(receipt) - off)
                name = receipt[off:off + nbytes].split(b"\x00", 1)[0]
                off += nbytes
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(off, len(receipt))
            return parsed

        def assert_stage(raw, source_wd, parent_wd, action):
            observed = events(raw)
            expected = {
                (source_wd, action, b""),
                (parent_wd, action, b"sample"),
            }
            self.assertTrue(observed)
            self.assertTrue(all(e in expected for e in observed))
            for e in expected:
                self.assertIn(e, observed)

        with tempfile.TemporaryDirectory(
            prefix="dec1162-public-writable-dup-close-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            first = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            self.assertEqual(len(module.BEFORE), len(module.AFTER))
            self.assertNotEqual(module.BEFORE, module.AFTER)
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

                writer_fd = os.open(
                    sample, os.O_WRONLY | os.O_CLOEXEC
                )
                duplicate_fd = os.dup(writer_fd)
                self.assertNotEqual(writer_fd, duplicate_fd)
                self.assertEqual(os.fstat(writer_fd).st_ino,
                                 os.fstat(duplicate_fd).st_ino)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # os.dup shares an open file description. Closing the
                # first O_WRONLY integer fd is NOT the final writable
                # reference and must not trigger native IN_CLOSE_WRITE.
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Genuine same-length changed-byte write via the surviving
                # duplicate is independently witnessed by normal source
                # and original parent MODIFY. The original CLOSE-only
                # ONESHOT remains armed because it excludes MODIFY.
                self.assertEqual(
                    os.pwrite(duplicate_fd, module.AFTER, 0),
                    len(module.AFTER),
                )
                os.fsync(duplicate_fd)
                modifications = module._read_receipt_pending(normal_fd)
                assert_stage(modifications, source_wd, parent_wd,
                             module.IN_MODIFY)
                outcome = module._evaluate(
                    module.BEFORE, module.AFTER, modifications,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(outcome["status"], "BLOCKED")
                self.assertIs(outcome["can_authorize_dispatch"], False)
                self.assertIs(outcome["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")

                # Final duplicate close releases the last writable file
                # description reference. Only NOW does native CLOSE_WRITE
                # arrive and consume original ONESHOT with IN_IGNORED.
                os.close(duplicate_fd)
                duplicate_fd = None
                self.assertEqual(
                    events(module._read_receipt_pending(original_fd)),
                    [(one_wd, module.IN_CLOSE_WRITE, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                closes = module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    events(closes),
                    [(source_wd, module.IN_CLOSE_WRITE, b""),
                     (parent_wd, module.IN_CLOSE_WRITE, b"sample")],
                )
                self.assertEqual(sample.read_bytes(), module.AFTER)
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # A separate real ordinary write restores disposable bytes.
                # The already-expired original source ONESHOT remains quiet,
                # whereas normal continuing source+parent stays registered.
                writer_fd = os.open(
                    sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC
                )
                self.assertEqual(os.write(writer_fd, module.BEFORE),
                                 len(module.BEFORE))
                os.fsync(writer_fd)
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                restore = module._read_receipt_pending(normal_fd)
                restore_events = events(restore)
                expected = {
                    (source_wd, module.IN_MODIFY, b""),
                    (parent_wd, module.IN_MODIFY, b"sample"),
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                }
                self.assertTrue(all(row in expected for row in restore_events))
                for row in expected:
                    self.assertIn(row, restore_events)
                result = module._evaluate(
                    module.AFTER, module.BEFORE, restore, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIs(result["can_authorize_dispatch"], False)
                self.assertIs(result["independent_os_proof_verified"], False)

                final = (os.lstat(sample), os.lstat(parent))
                for old, new in zip(first, final):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
            finally:
                for fd in (duplicate_fd, writer_fd, original_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
