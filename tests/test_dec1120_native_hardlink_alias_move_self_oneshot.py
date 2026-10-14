from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1120", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "requires native Linux inotify")
class NativeHardlinkAliasMoveSelfOneShotRegression(unittest.TestCase):
    def test_renaming_alias_moves_watched_inode_without_moving_source_path(self):
        one_fd = None
        continuing_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            observed = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, size = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(size, len(data) - offset)
                name = data[offset:offset + size].split(b"\x00", 1)[0]
                offset += size
                observed.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(data))
            return observed

        def assert_native_pair(data, source_wd, parent_wd, old, new):
            observed = records(data)
            self.assertEqual(len(observed), 3)
            self.assertIn((source_wd, module.IN_MOVE_SELF, 0, b""), observed)
            directory_entries = [event for event in observed
                                 if event[0] == parent_wd]
            self.assertEqual(len(directory_entries), 2)
            cookies = {event[2] for event in directory_entries}
            self.assertEqual(len(cookies), 1)
            cookie = cookies.pop()
            self.assertGreater(cookie, 0)
            self.assertCountEqual(directory_entries, [
                (parent_wd, module.IN_MOVED_FROM, cookie, old),
                (parent_wd, module.IN_MOVED_TO, cookie, new),
            ])
            classified = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(classified["well_formed"])
            self.assertTrue(classified["invalidated"])
            return cookie

        def real_write(path, contents):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, contents), len(contents))
                os.fsync(fd)
            finally:
                os.close(fd)

        def assert_source_write(data, source_wd, parent_wd, after):
            observed = records(data)
            for event in (
                (source_wd, module.IN_MODIFY, 0, b""),
                (parent_wd, module.IN_MODIFY, 0, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, 0, b""),
                (parent_wd, module.IN_CLOSE_WRITE, 0, b"sample"),
            ):
                self.assertIn(event, observed)
            parsed = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("alias", "sample"),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1120-public-hardlink-alias-move-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            alias = parent / "alias"
            alternate = parent / "renamed-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            os.link(sample, alias)
            original = (os.lstat(sample), os.lstat(alias),
                        os.lstat(parent))
            self.assertEqual(original[0].st_ino, original[1].st_ino)
            self.assertEqual(original[0].st_nlink, 2)
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("alias", "sample"))
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
                self.assertGreater(one_fd, 2)
                self.assertNotEqual(one_fd, continuing_fd)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MOVE_SELF | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                # Rename ANOTHER HARD-LINK NAME for the watched source inode.
                # The original 'sample' path never moves or disappears.
                os.rename(alias, alternate)
                self.assertTrue(sample.is_file())
                self.assertTrue(alternate.is_file())
                self.assertFalse(alias.exists())
                self.assertEqual(os.lstat(sample).st_ino,
                                 os.lstat(alternate).st_ino)
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_MOVE_SELF, 0, b""),
                     (one_wd, module.IN_IGNORED, 0, b"")],
                )
                forward = module._read_receipt_pending(continuing_fd)
                forward_cookie = assert_native_pair(
                    forward, source_wd, parent_wd,
                    b"alias", b"renamed-alias",
                )
                forward_outcome = module._evaluate(
                    module.BEFORE, module.BEFORE, forward, source_wd, True,
                    False, directory_watch=parent_wd,
                    directory_inventory_names=("renamed-alias", "sample"),
                )
                self.assertEqual(forward_outcome["status"], "BLOCKED")
                self.assertIs(forward_outcome["can_authorize_dispatch"], False)
                self.assertIs(
                    forward_outcome["independent_os_proof_verified"], False,
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                # Restore alias spelling and same source nlink=2, but the
                # original one-shot cannot be re-armed by path restoration.
                os.rename(alternate, alias)
                self.assertTrue(sample.is_file())
                self.assertTrue(alias.is_file())
                self.assertFalse(alternate.exists())
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                backward = module._read_receipt_pending(continuing_fd)
                backward_cookie = assert_native_pair(
                    backward, source_wd, parent_wd,
                    b"renamed-alias", b"alias",
                )
                self.assertNotEqual(forward_cookie, backward_cookie)
                backward_outcome = module._evaluate(
                    module.BEFORE, module.BEFORE, backward, source_wd, True,
                    False, directory_watch=parent_wd,
                    directory_inventory_names=("alias", "sample"),
                )
                self.assertEqual(backward_outcome["status"], "BLOCKED")
                self.assertIs(backward_outcome["can_authorize_dispatch"], False)
                self.assertIs(
                    backward_outcome["independent_os_proof_verified"], False,
                )

                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                assert_source_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                assert_source_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                final = (os.lstat(sample), os.lstat(alias),
                         os.lstat(parent))
                for before, after in zip(original, final):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(alias.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("alias", "sample"))
            finally:
                if alternate.exists() and not alias.exists():
                    os.rename(alternate, alias)
                for fd in (one_fd, continuing_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
