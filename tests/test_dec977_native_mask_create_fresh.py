from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec977", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Linux inotify registration-only flag, never an event mask.
IN_MASK_CREATE = 0x10000000


@unittest.skipUnless(sys.platform == "linux", "IN_MASK_CREATE requires Linux")
class NativeCreateOnlyWatchRegression(unittest.TestCase):
    def test_real_create_only_fresh_watch_then_eexist_does_not_replace_mask(self):
        fresh_fd = None
        original_fd = None
        with tempfile.TemporaryDirectory(
            prefix="dec977-public-create-only-fresh-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            before = os.lstat(sample)
            parent_before = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                # The original two-WD witness is completely independent of
                # the initially empty second inotify instance.
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_init1.argtypes = [module.ctypes.c_int]
                lib.inotify_init1.restype = module.ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                fresh_fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(fresh_fd, 2)
                self.assertEqual(module._read_receipt_pending(fresh_fd), b"")

                # The create-only flag succeeds when this independent
                # instance has no watch on the public source inode.
                module.ctypes.set_errno(0)
                created_wd = lib.inotify_add_watch(
                    fresh_fd, module._checked_watch_path_bytes(sample),
                    IN_MASK_CREATE | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(created_wd, 0)
                self.assertLessEqual(created_wd, module.MAX_WATCH_DESCRIPTOR)
                self.assertEqual(module._read_receipt_pending(fresh_fd), b"")

                # Repeating create-only against that same inode must
                # fail without replacing its working write subscriptions.
                module.ctypes.set_errno(0)
                refused = lib.inotify_add_watch(
                    fresh_fd, module._checked_watch_path_bytes(sample),
                    IN_MASK_CREATE | module.IN_ATTRIB |
                    module.IN_DONT_FOLLOW,
                )
                self.assertEqual(refused, -1)
                self.assertEqual(module.ctypes.get_errno(), errno.EEXIST)
                self.assertEqual(module._read_receipt_pending(fresh_fd), b"")

                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    fresh_stream = module._read_receipt_pending(fresh_fd)
                    original_stream = module._read_receipt_pending(original_fd)
                    self.assertTrue(fresh_stream)
                    self.assertTrue(original_stream)
                    fresh_events = module._classify_stream(
                        fresh_stream, created_wd
                    )
                    original_events = module._classify_stream(
                        original_stream, source_wd, parent_wd
                    )
                    self.assertTrue(fresh_events["well_formed"])
                    self.assertFalse(fresh_events["invalidated"])
                    self.assertGreaterEqual(
                        fresh_events["source_modify_events"], 1
                    )
                    self.assertGreaterEqual(
                        fresh_events["source_content_write_events"], 1
                    )
                    self.assertTrue(original_events["well_formed"])
                    self.assertFalse(original_events["invalidated"])
                    self.assertGreaterEqual(
                        original_events["source_modify_events"], 1
                    )
                    self.assertEqual(module._read_receipt_pending(fresh_fd), b"")
                    self.assertEqual(module._read_receipt_pending(original_fd), b"")
                    for stream, watched_wd, directory_wd in (
                        (fresh_stream, created_wd, None),
                        (original_stream, source_wd, parent_wd),
                    ):
                        verdict = module._evaluate(
                            module.BEFORE, content, stream, watched_wd,
                            True, False, directory_watch=directory_wd,
                            directory_inventory_names=("sample",),
                        )
                        self.assertEqual(verdict["status"], "BLOCKED")
                        self.assertIs(verdict["can_authorize_dispatch"], False)
                        self.assertIs(
                            verdict["independent_os_proof_verified"], False
                        )

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
                for fd in (fresh_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
