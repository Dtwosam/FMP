from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1060", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeParentDirectoryDeleteOneShotRegression(unittest.TestCase):
    def test_rmdir_isdir_triggers_delete_oneshot_after_nonmatching_writes(self):
        one_fd = None
        independent_fd = None

        def records(raw):
            self.assertIs(type(raw), bytes)
            parsed = []
            pos = 0
            while pos < len(raw):
                self.assertGreaterEqual(len(raw) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(raw, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(raw) - pos)
                name = raw[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(pos, len(raw))
            return parsed

        def sample_write(path, content):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(content), len(content))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        with tempfile.TemporaryDirectory(
            prefix="dec1060-public-parent-rmdir-oneshot-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            child = parent / "public-existing-dir"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            child.mkdir()
            original = os.lstat(sample)
            parent_original = os.lstat(parent)
            self.assertEqual(
                module._bounded_inventory_names(parent),
                ("public-existing-dir", "sample")
            )
            try:
                independent_fd, source_wd, parent_wd = (
                    module._start_watch(sample)
                )
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                one_parent_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_DELETE | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_parent_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Two real changed-byte source writes do NOT match
                # parent-only DELETE, leaving its one-shot armed.
                for content in (module.AFTER, module.BEFORE):
                    sample_write(sample, content)
                    self.assertEqual(module._read_receipt_pending(one_fd), b"")
                    witnessed = module._read_receipt_pending(independent_fd)
                    native = records(witnessed)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in native
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in native
                    ))
                    verdict = module._evaluate(
                        module.BEFORE, content, witnessed, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("public-existing-dir", "sample"),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # rmdir on a *directory entry* is the FIRST matching
                # event. Kernel emits named DELETE|ISDIR and then
                # auto-removes one-shot with genuine IN_IGNORED.
                child.rmdir()
                self.assertEqual(records(
                    module._read_receipt_pending(one_fd)
                ), [
                    (one_parent_wd, module.IN_DELETE | module.IN_ISDIR,
                     b"public-existing-dir"),
                    (one_parent_wd, module.IN_IGNORED, b""),
                ])
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                deletion = module._read_receipt_pending(independent_fd)
                self.assertIn(
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR,
                     b"public-existing-dir"),
                    records(deletion),
                )
                parsed = module._classify_stream(
                    deletion, source_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["directory_changes"], 1)
                result = module._evaluate(
                    module.BEFORE, module.BEFORE, deletion, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIs(result["can_authorize_dispatch"], False)
                self.assertIs(
                    result["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Later real mkdir/rmdir/mkdir updates are all invisible
                # to dead one-shot, while independent parent records
                # the original name with the correct directory bit.
                child.mkdir()
                child.rmdir()
                child.mkdir()
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                following = records(
                    module._read_receipt_pending(independent_fd)
                )
                self.assertEqual([
                    (wd, mask, name) for wd, mask, name in following
                    if wd == parent_wd and name == b"public-existing-dir"
                ], [
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR,
                     b"public-existing-dir"),
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR,
                     b"public-existing-dir"),
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR,
                     b"public-existing-dir"),
                ])
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                last = os.lstat(sample)
                parent_last = os.lstat(parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (original.st_dev, original.st_ino, original.st_mode),
                )
                self.assertEqual(
                    (parent_last.st_dev, parent_last.st_ino, parent_last.st_mode),
                    (parent_original.st_dev, parent_original.st_ino,
                     parent_original.st_mode),
                )
                self.assertEqual(
                    module._bounded_inventory_names(parent),
                    ("public-existing-dir", "sample"),
                )
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
