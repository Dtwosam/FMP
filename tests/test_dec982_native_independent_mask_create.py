from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec982", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_MASK_CREATE = 0x10000000  # Linux registration-only flag.


@unittest.skipUnless(sys.platform == "linux", "IN_MASK_CREATE is Linux-only")
class NativeIndependentMaskCreateRegression(unittest.TestCase):
    def test_real_create_only_same_inode_succeeds_in_independent_instances(self):
        fds = []
        with tempfile.TemporaryDirectory(
            prefix="dec982-public-independent-create-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_init1.argtypes = [module.ctypes.c_int]
                lib.inotify_init1.restype = module.ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int

                # Exclusivity is per inotify *instance*, not global to
                # the target inode. Each new FD may create its first WD.
                for _ in range(2):
                    fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                    self.assertGreater(fd, 2)
                    fds.append(fd)
                created_wds = []
                for fd in fds:
                    module.ctypes.set_errno(0)
                    wd = lib.inotify_add_watch(
                        fd, module._checked_watch_path_bytes(sample),
                        IN_MASK_CREATE | module.IN_MODIFY |
                        module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW,
                    )
                    self.assertGreater(wd, 0)
                    self.assertLessEqual(wd, module.MAX_WATCH_DESCRIPTOR)
                    created_wds.append(wd)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Each FD separately rejects its own second create-only
                # registration, leaving its original write mask intact.
                for fd in fds:
                    module.ctypes.set_errno(0)
                    refused = lib.inotify_add_watch(
                        fd, module._checked_watch_path_bytes(sample),
                        IN_MASK_CREATE | module.IN_ATTRIB |
                        module.IN_DONT_FOLLOW,
                    )
                    self.assertEqual(refused, -1)
                    self.assertEqual(module.ctypes.get_errno(), errno.EEXIST)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())

                    # Draining the first instance never drains or consumes
                    # the second independent instance's queued events.
                    first = module._read_receipt_pending(fds[0])
                    self.assertTrue(first)
                    self.assertEqual(module._read_receipt_pending(fds[0]), b"")
                    second = module._read_receipt_pending(fds[1])
                    self.assertTrue(second)
                    self.assertEqual(module._read_receipt_pending(fds[1]), b"")
                    for wd, stream in zip(created_wds, (first, second)):
                        parsed = module._classify_stream(stream, wd)
                        self.assertTrue(parsed["well_formed"])
                        self.assertFalse(parsed["invalidated"])
                        self.assertGreaterEqual(parsed["source_modify_events"], 1)
                        self.assertGreaterEqual(
                            parsed["source_content_write_events"], 1
                        )
                        verdict = module._evaluate(
                            module.BEFORE, content, stream, wd, True,
                            False, directory_inventory_names=("sample",),
                        )
                        self.assertEqual(verdict["status"], "BLOCKED")
                        self.assertIn(
                            "synthetic inotify property missing: both_watches_identified",
                            verdict["findings"],
                        )
                        self.assertIs(verdict["can_authorize_dispatch"], False)
                        self.assertIs(
                            verdict["independent_os_proof_verified"], False
                        )

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino, parent_final.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in fds:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
