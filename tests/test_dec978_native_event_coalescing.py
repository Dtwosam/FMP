from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec978", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native inotify coalescing is Linux-only")
class NativeEventCoalescingRegression(unittest.TestCase):
    def test_real_two_writes_coalesce_to_one_source_modify_record(self):
        source_only_fd = None
        original_fd = None
        with tempfile.TemporaryDirectory(
            prefix="dec978-public-coalescing-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            before = os.lstat(sample)
            parent_before = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                # A second, independent inotify instance has only one
                # subscribed inode, permitting consecutive equal MODIFY
                # records to be coalesced before userspace drains them.
                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_init1.argtypes = [module.ctypes.c_int]
                lib.inotify_init1.restype = module.ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                source_only_fd = lib.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(source_only_fd, 2)
                single_wd = lib.inotify_add_watch(
                    source_only_fd,
                    module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW,
                )
                self.assertGreater(single_wd, 0)
                self.assertEqual(module._read_receipt_pending(source_only_fd), b"")

                midpoint = len(module.AFTER) // 2
                self.assertGreater(midpoint, 0)
                self.assertLess(midpoint, len(module.AFTER))

                # Two real unbuffered write(2) calls. No userspace read of
                # either event queue occurs between the two syscalls.
                with sample.open("r+b", buffering=0) as writer:
                    self.assertEqual(
                        writer.write(module.AFTER[:midpoint]), midpoint
                    )
                    self.assertEqual(
                        writer.write(module.AFTER[midpoint:]),
                        len(module.AFTER) - midpoint,
                    )
                    os.fsync(writer.fileno())

                single_stream = module._read_receipt_pending(source_only_fd)
                original_stream = module._read_receipt_pending(original_fd)
                self.assertEqual(
                    single_stream,
                    module.EVENT.pack(single_wd, module.IN_MODIFY, 0, 0)
                    + module.EVENT.pack(single_wd, module.IN_CLOSE_WRITE, 0, 0),
                )
                single_parsed = module._classify_stream(
                    single_stream, single_wd
                )
                self.assertTrue(single_parsed["well_formed"])
                self.assertFalse(single_parsed["invalidated"])
                # The kernel coalesced two genuine writes into only one
                # IN_MODIFY record. This is not evidence of one write.
                self.assertEqual(single_parsed["source_modify_events"], 1)
                self.assertTrue(original_stream)
                original_parsed = module._classify_stream(
                    original_stream, source_wd, parent_wd
                )
                self.assertTrue(original_parsed["well_formed"])
                self.assertFalse(original_parsed["invalidated"])
                self.assertGreaterEqual(original_parsed["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(source_only_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                self.assertEqual(sample.read_bytes(), module.AFTER)
                for stream, wd, directory_wd in (
                    (single_stream, single_wd, None),
                    (original_stream, source_wd, parent_wd),
                ):
                    verdict = module._evaluate(
                        module.BEFORE, module.AFTER, stream, wd, True,
                        False, directory_watch=directory_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )

                # Restore the original public sample in a separate write,
                # drain the genuinely new events and check inode identity.
                with sample.open("r+b") as writer:
                    self.assertEqual(
                        writer.write(module.BEFORE), len(module.BEFORE)
                    )
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                source_restore = module._read_receipt_pending(source_only_fd)
                original_restore = module._read_receipt_pending(original_fd)
                self.assertTrue(source_restore)
                self.assertTrue(original_restore)
                self.assertTrue(module._classify_stream(
                    source_restore, single_wd
                )["well_formed"])
                self.assertTrue(module._classify_stream(
                    original_restore, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(source_only_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                after = os.lstat(sample)
                parent_after = os.lstat(sample.parent)
                self.assertEqual(
                    (after.st_dev, after.st_ino, after.st_mode),
                    (before.st_dev, before.st_ino, before.st_mode),
                )
                self.assertEqual(
                    (parent_after.st_dev, parent_after.st_ino,
                     parent_after.st_mode),
                    (parent_before.st_dev, parent_before.st_ino,
                     parent_before.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (source_only_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
