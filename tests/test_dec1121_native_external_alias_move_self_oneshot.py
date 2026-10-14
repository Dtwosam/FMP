from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1121", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "requires real native Linux inotify")
class NativeExternalAliasMoveSelfOneShotRegression(unittest.TestCase):
    def test_external_alias_rename_moves_source_inode_without_original_parent_event(self):
        one_fd = None
        continuing_fd = None
        outside_fd = None

        def events(data):
            self.assertIs(type(data), bytes)
            result = []
            cursor = 0
            while cursor < len(data):
                self.assertGreaterEqual(len(data) - cursor, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, cursor)
                cursor += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - cursor)
                name = data[cursor:cursor + nbytes].split(b"\x00", 1)[0]
                cursor += nbytes
                result.append((wd, mask, cookie, name))
            self.assertEqual(cursor, len(data))
            return result

        def genuine_write(path, contents):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, contents), len(contents))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_unsafe_write(stream, source_wd, parent_wd, after):
            observed = events(stream)
            for event in (
                (source_wd, module.IN_MODIFY, 0, b""),
                (parent_wd, module.IN_MODIFY, 0, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, 0, b""),
                (parent_wd, module.IN_CLOSE_WRITE, 0, b"sample"),
            ):
                self.assertIn(event, observed)
            parsed = module._classify_stream(stream, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            outcome = module._evaluate(
                module.BEFORE, after, stream, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(outcome["status"], "BLOCKED")
            self.assertIs(outcome["can_authorize_dispatch"], False)
            self.assertIs(outcome["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1121-public-external-alias-rename-", dir="/tmp"
        ) as tmp:
            root = Path(tmp)
            parent = root / "parent"
            outside = root / "outside"
            parent.mkdir()
            outside.mkdir()
            sample = parent / "sample"
            alias = outside / "alias"
            alternate = outside / "renamed-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            os.link(sample, alias)
            initial = (os.lstat(sample), os.lstat(alias),
                       os.lstat(parent), os.lstat(outside))
            self.assertEqual(initial[0].st_dev, initial[1].st_dev)
            self.assertEqual(initial[0].st_ino, initial[1].st_ino)
            self.assertEqual(initial[0].st_nlink, 2)
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            self.assertEqual(module._bounded_inventory_names(outside),
                             ("alias",))
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
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(outside_wd, 0)
                for fd in (one_fd, continuing_fd, outside_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Rename a DIFFERENT hard-link name in the OTHER directory.
                # The watched source pathname remains 'parent/sample'.
                os.rename(alias, alternate)
                self.assertTrue(sample.is_file())
                self.assertTrue(alternate.is_file())
                self.assertFalse(alias.exists())
                self.assertEqual(os.lstat(sample).st_ino,
                                 os.lstat(alternate).st_ino)
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                self.assertEqual(
                    events(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_MOVE_SELF, 0, b""),
                     (one_wd, module.IN_IGNORED, 0, b"")],
                )
                first = module._read_receipt_pending(continuing_fd)
                self.assertEqual(
                    events(first),
                    [(source_wd, module.IN_MOVE_SELF, 0, b"")],
                )
                classified = module._classify_stream(
                    first, source_wd, parent_wd,
                )
                self.assertTrue(classified["well_formed"])
                self.assertTrue(classified["invalidated"])
                verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, first, source_wd, True,
                    False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)
                observed_outside = events(
                    module._read_receipt_pending(outside_fd)
                )
                self.assertEqual(len(observed_outside), 2)
                self.assertGreater(observed_outside[0][2], 0)
                forward_cookie = observed_outside[0][2]
                self.assertEqual(observed_outside, [
                    (outside_wd, module.IN_MOVED_FROM, forward_cookie,
                     b"alias"),
                    (outside_wd, module.IN_MOVED_TO, forward_cookie,
                     b"renamed-alias"),
                ])
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                # Rename back. Continuing source sees another MOVE_SELF
                # despite sample never disappearing; original parent quiet.
                os.rename(alternate, alias)
                self.assertTrue(sample.is_file())
                self.assertTrue(alias.is_file())
                self.assertFalse(alternate.exists())
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                returned = module._read_receipt_pending(continuing_fd)
                self.assertEqual(
                    events(returned),
                    [(source_wd, module.IN_MOVE_SELF, 0, b"")],
                )
                classified = module._classify_stream(
                    returned, source_wd, parent_wd,
                )
                self.assertTrue(classified["well_formed"])
                self.assertTrue(classified["invalidated"])
                verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, returned, source_wd, True,
                    False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)
                observed_outside = events(
                    module._read_receipt_pending(outside_fd)
                )
                self.assertEqual(len(observed_outside), 2)
                backward_cookie = observed_outside[0][2]
                self.assertGreater(backward_cookie, 0)
                self.assertNotEqual(backward_cookie, forward_cookie)
                self.assertEqual(observed_outside, [
                    (outside_wd, module.IN_MOVED_FROM, backward_cookie,
                     b"renamed-alias"),
                    (outside_wd, module.IN_MOVED_TO, backward_cookie,
                     b"alias"),
                ])

                genuine_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_unsafe_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd), b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                genuine_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_unsafe_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd), b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                final = (os.lstat(sample), os.lstat(alias),
                         os.lstat(parent), os.lstat(outside))
                for old, new in zip(initial, final):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(alias.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("alias",))
            finally:
                if alternate.exists() and not alias.exists():
                    os.rename(alternate, alias)
                for fd in (one_fd, continuing_fd, outside_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
