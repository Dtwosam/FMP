from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1117", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeSourceCrossParentMoveSelfOneShotRegression(unittest.TestCase):
    def test_source_move_self_removes_oneshot_before_path_restoration_and_writes(self):
        one_fd = None
        continuing_fd = None
        outside_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            found = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(data) - pos)
                name = data[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                found.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(data))
            return found

        def genuine_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def check_write(data, source_wd, parent_wd, after):
            observed = records(data)
            # O_TRUNC can emit a genuine MODIFY before the subsequent
            # write(), yielding more than one source/parent MODIFY.
            # Every native record must still be one of the four expected
            # source/parent mutation identities. Enforce both writes and
            # exactly one writable close per descriptor, but do not forge
            # an arbitrary "exactly one MODIFY" kernel guarantee.
            source_modify = (source_wd, module.IN_MODIFY, 0, b"")
            parent_modify = (parent_wd, module.IN_MODIFY, 0, b"sample")
            source_close = (source_wd, module.IN_CLOSE_WRITE, 0, b"")
            parent_close = (parent_wd, module.IN_CLOSE_WRITE, 0, b"sample")
            permitted = (source_modify, parent_modify, source_close,
                         parent_close)
            self.assertTrue(all(event in permitted for event in observed))
            self.assertGreaterEqual(observed.count(source_modify), 1)
            self.assertGreaterEqual(observed.count(parent_modify), 1)
            self.assertEqual(observed.count(source_close), 1)
            self.assertEqual(observed.count(parent_close), 1)
            parsed = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd, directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1117-public-source-rename-", dir="/tmp"
        ) as tmp:
            root = Path(tmp)
            parent = root / "parent"
            outside = root / "outside"
            parent.mkdir()
            outside.mkdir()
            sample = parent / "sample"
            moved = outside / "relocated"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = (os.lstat(sample), os.lstat(parent), os.lstat(outside))
            self.assertEqual(module._bounded_inventory_names(parent), ("sample",))
            self.assertEqual(module._bounded_inventory_names(outside), ())
            try:
                continuing_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                outside_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                self.assertGreater(outside_fd, 2)
                self.assertEqual(len({one_fd, continuing_fd, outside_fd}), 3)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MOVE_SELF | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                outside_wd = libc.inotify_add_watch(
                    outside_fd, module._checked_watch_path_bytes(outside),
                    module.IN_MOVED_FROM | module.IN_MOVED_TO |
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(outside_wd, 0)
                for fd in (one_fd, continuing_fd, outside_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Move the watched source regular-file INODE, not the parent
                # directory or a second hard-link alias. Two different
                # directory watches provide paired native rename cookies.
                os.rename(sample, moved)
                self.assertFalse(sample.exists())
                self.assertTrue(moved.is_file())
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_MOVE_SELF, 0, b""),
                     (one_wd, module.IN_IGNORED, 0, b"")],
                )
                first_native = records(
                    module._read_receipt_pending(continuing_fd)
                )
                self.assertEqual(len(first_native), 2)
                self.assertIn(
                    (source_wd, module.IN_MOVE_SELF, 0, b""), first_native,
                )
                from_events = [e for e in first_native
                               if e[0] == parent_wd]
                self.assertEqual(len(from_events), 1)
                self.assertEqual(from_events[0][1], module.IN_MOVED_FROM)
                self.assertEqual(from_events[0][3], b"sample")
                self.assertGreater(from_events[0][2], 0)
                self.assertEqual(
                    records(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, module.IN_MOVED_TO, from_events[0][2],
                      b"relocated")],
                )

                # Restoring original pathname emits another self MOVE on
                # the continuing source watch and a new cookie-paired rename.
                os.rename(moved, sample)
                self.assertTrue(sample.is_file())
                self.assertFalse(moved.exists())
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                returned = records(module._read_receipt_pending(continuing_fd))
                self.assertEqual(len(returned), 2)
                self.assertIn(
                    (source_wd, module.IN_MOVE_SELF, 0, b""), returned
                )
                to_events = [e for e in returned if e[0] == parent_wd]
                self.assertEqual(len(to_events), 1)
                self.assertEqual(to_events[0][1], module.IN_MOVED_TO)
                self.assertEqual(to_events[0][3], b"sample")
                self.assertGreater(to_events[0][2], 0)
                self.assertEqual(
                    records(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, module.IN_MOVED_FROM, to_events[0][2],
                      b"relocated")],
                )

                # Two actual byte-changing/restoring writes at the original
                # pathname remain unseen by the removed source one-shot.
                genuine_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                check_write(module._read_receipt_pending(continuing_fd),
                            source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(outside_fd), b"")

                genuine_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                check_write(module._read_receipt_pending(continuing_fd),
                            source_wd, parent_wd, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(outside_fd), b"")

                final = (os.lstat(sample), os.lstat(parent), os.lstat(outside))
                for before, after in zip(initial, final):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(outside), ())
            finally:
                if moved.exists() and not sample.exists():
                    os.rename(moved, sample)
                for fd in (one_fd, continuing_fd, outside_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
