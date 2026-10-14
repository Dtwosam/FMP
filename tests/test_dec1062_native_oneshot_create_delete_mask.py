from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1062", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux parent inotify only")
class NativeParentCreateDeleteOneShotMaskRegression(unittest.TestCase):
    def test_oneshot_subscribes_create_and_delete_but_first_mkdir_loses_rmdir(self):
        one_fd = None
        independent_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            offset = 0
            result = []
            while offset < len(stream):
                self.assertGreaterEqual(len(stream) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(stream, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(stream) - offset)
                name = stream[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(offset, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1062-public-both-oneshot-events-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            sibling = parent / "public-cycle-dir"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            parent_first = os.lstat(parent)
            self.assertEqual(module._bounded_inventory_names(parent), ("sample",))
            try:
                independent_fd, source_wd, parent_wd = (
                    module._start_watch(sample)
                )
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_CREATE | module.IN_DELETE | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                for fd in (one_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # BOTH event types are included in original one-shot
                # mask. First mkdir auto-removes watcher before rmdir;
                # do not read queue until after BOTH real syscalls.
                sibling.mkdir()
                self.assertTrue(sibling.is_dir())
                sibling.rmdir()
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                primary = records(module._read_receipt_pending(one_fd))
                self.assertEqual(primary, [
                    (one_wd, module.IN_CREATE | module.IN_ISDIR,
                     b"public-cycle-dir"),
                    (one_wd, module.IN_IGNORED, b""),
                ])
                self.assertFalse(any(
                    mask & module.IN_DELETE for wd, mask, name in primary
                ))
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                actual = module._read_receipt_pending(independent_fd)
                independent = records(actual)
                self.assertIn(
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR,
                     b"public-cycle-dir"),
                    independent,
                )
                self.assertIn(
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR,
                     b"public-cycle-dir"),
                    independent,
                )
                self.assertLess(
                    independent.index((
                        parent_wd, module.IN_CREATE | module.IN_ISDIR,
                        b"public-cycle-dir"
                    )),
                    independent.index((
                        parent_wd, module.IN_DELETE | module.IN_ISDIR,
                        b"public-cycle-dir"
                    )),
                )
                parsed = module._classify_stream(
                    actual, source_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["directory_changes"], 2)
                verdict = module._evaluate(
                    module.BEFORE, module.BEFORE,
                    actual, source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # A second genuine directory lifecycle cannot
                # resurrect original one-shot despite both actions
                # still being present in its *registration mask*.
                sibling.mkdir()
                sibling.rmdir()
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                later = records(
                    module._read_receipt_pending(independent_fd)
                )
                self.assertIn(
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR,
                     b"public-cycle-dir"), later
                )
                self.assertIn(
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR,
                     b"public-cycle-dir"), later
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                last = os.lstat(sample)
                parent_last = os.lstat(parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (parent_last.st_dev, parent_last.st_ino,
                     parent_last.st_mode),
                    (parent_first.st_dev, parent_first.st_ino,
                     parent_first.st_mode),
                )
                self.assertEqual(
                    module._bounded_inventory_names(parent), ("sample",)
                )
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
