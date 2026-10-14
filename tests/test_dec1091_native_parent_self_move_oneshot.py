from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1091", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "real native Linux inotify required")
class NativeParentDirectorySelfMoveOneShotRegression(unittest.TestCase):
    def test_parent_self_rename_removes_oneshot_before_restored_child_writes(self):
        one_fd = None
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

        def assert_independent_write(receipt, source_wd, parent_wd, after):
            events = records(receipt)
            for expected in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(expected, events)
            classified = module._classify_stream(receipt, source_wd, parent_wd)
            self.assertTrue(classified["well_formed"])
            self.assertFalse(classified["invalidated"])
            self.assertGreaterEqual(classified["source_content_write_events"], 1)
            result = module._evaluate(
                module.BEFORE, after, receipt, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIs(result["can_authorize_dispatch"], False)
            self.assertIs(result["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1091-public-parent-self-move-", dir="/tmp"
        ) as tmp:
            root = Path(tmp)
            parent = root / "parent"
            moved = root / "parent-renamed"
            parent.mkdir()
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = (os.lstat(root), os.lstat(parent), os.lstat(sample))
            self.assertEqual(module._bounded_inventory_names(root), ("parent",))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
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
                self.assertGreater(one_fd, 2)
                self.assertNotEqual(one_fd, independent_fd)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_MOVE_SELF | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_CREATE |
                    module.IN_DELETE | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Rename the WATCHED DIRECTORY INODE ITSELF within the
                # disposable root. A directory self move is an unnamed
                # native IN_MOVE_SELF, not a child MOVED_FROM/TO record.
                os.rename(parent, moved)
                self.assertFalse(parent.exists())
                self.assertTrue((moved / "sample").is_file())
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_MOVE_SELF, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_MOVE_SELF, b"")],
                )

                # Restoring the original name is a second real native
                # MOVE_SELF on the still-active independent parent watch.
                os.rename(moved, parent)
                self.assertTrue(sample.is_file())
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(parent_wd, module.IN_MOVE_SELF, b"")],
                )
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                # Explicit original write categories cannot revive a
                # destroyed one-shot after the directory path is restored.
                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                assert_independent_write(changed, source_wd, parent_wd,
                                         module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                assert_independent_write(restored, source_wd, parent_wd,
                                         module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = (os.lstat(root), os.lstat(parent), os.lstat(sample))
                for old, new in zip(first, last):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode),
                        (new.st_dev, new.st_ino, new.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(root),
                                 ("parent",))
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertFalse(moved.exists())
            finally:
                # Do not leave a temporary renamed directory behind even
                # when an assertion fails between the two real renames.
                if moved.exists() and not parent.exists():
                    os.rename(moved, parent)
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
