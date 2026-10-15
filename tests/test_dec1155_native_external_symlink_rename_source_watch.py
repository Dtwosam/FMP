from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1155", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeExternalSymlinkRenameSourceWatchRegression(unittest.TestCase):
    def test_symlink_rename_does_not_consume_source_move_self_oneshot(self):
        one_fd = None
        normal_fd = None
        outside_fd = None

        def events(data):
            self.assertIs(type(data), bytes)
            out = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(data) - pos)
                name = data[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                out.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(data))
            return out

        def check_move_pair(raw, wd, old, new):
            observed = events(raw)
            self.assertEqual(len(observed), 2)
            self.assertEqual(observed[0][:2],
                             (wd, module.IN_MOVED_FROM))
            self.assertEqual(observed[1][:2],
                             (wd, module.IN_MOVED_TO))
            self.assertEqual(observed[0][3], old)
            self.assertEqual(observed[1][3], new)
            self.assertGreater(observed[0][2], 0)
            self.assertEqual(observed[0][2], observed[1][2])

        def real_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_normal_write(data, source_wd, parent_wd, after):
            seen = events(data)
            allowed = {
                (source_wd, module.IN_MODIFY, 0, b""),
                (parent_wd, module.IN_MODIFY, 0, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, 0, b""),
                (parent_wd, module.IN_CLOSE_WRITE, 0, b"sample"),
            }
            self.assertTrue(seen)
            self.assertTrue(all(e in allowed for e in seen))
            for expected in allowed:
                self.assertIn(expected, seen)
            parsed = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            result = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIs(result["can_authorize_dispatch"], False)
            self.assertIs(result["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1155-public-external-symlink-rename-", dir="/tmp"
        ) as temp:
            root = Path(temp)
            parent = root / "parent"
            outside = root / "outside"
            parent.mkdir()
            outside.mkdir()
            sample = parent / "sample"
            alias = outside / "alias-link"
            renamed = outside / "renamed-link"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            os.symlink(sample, alias)
            baseline = (os.lstat(sample), os.lstat(alias),
                        os.lstat(parent), os.lstat(outside))
            self.assertEqual(baseline[0].st_nlink, 1)
            self.assertTrue(stat.S_ISLNK(baseline[1].st_mode))
            self.assertEqual(os.stat(alias).st_ino, baseline[0].st_ino)
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            self.assertEqual(module._bounded_inventory_names(outside),
                             ("alias-link",))
            try:
                normal_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                outside_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertEqual(len({one_fd, normal_fd, outside_fd}), 3)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MOVE_SELF | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW |
                    IN_ONESHOT,
                )
                outside_wd = libc.inotify_add_watch(
                    outside_fd, module._checked_watch_path_bytes(outside),
                    module.IN_MOVED_FROM | module.IN_MOVED_TO |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(outside_wd, 0)
                for fd in (one_fd, normal_fd, outside_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Rename only the SYMLINK ENTRY in an unrelated directory.
                # Neither original source inode nor sample pathname moves.
                os.rename(alias, renamed)
                check_move_pair(module._read_receipt_pending(outside_fd),
                                outside_wd, b"alias-link", b"renamed-link")
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd),
                                 b"")
                self.assertEqual(os.lstat(sample).st_ino,
                                 baseline[0].st_ino)
                self.assertEqual(os.lstat(renamed).st_ino,
                                 baseline[1].st_ino)
                self.assertEqual(os.stat(renamed).st_ino,
                                 baseline[0].st_ino)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("renamed-link",))

                # Reverse actual rename, with another independent positive
                # same-directory named MOVED_FROM/MOVED_TO cookie pair.
                os.rename(renamed, alias)
                check_move_pair(module._read_receipt_pending(outside_fd),
                                outside_wd, b"renamed-link", b"alias-link")
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd),
                                 b"")

                # Original source MOVE_SELF|MODIFY|CLOSE_WRITE|ONESHOT has
                # survived both external SYMLINK renames; only a real
                # subsequent original-source WRITE consumes it.
                real_write(sample, module.AFTER)
                self.assertEqual(
                    events(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_MODIFY, 0, b""),
                     (one_wd, module.IN_IGNORED, 0, b"")],
                )
                verify_normal_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd),
                                 b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_normal_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                final = (os.lstat(sample), os.lstat(alias),
                         os.lstat(parent), os.lstat(outside))
                for old, new in zip(baseline, final):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(os.readlink(alias), str(sample))
                self.assertEqual(os.stat(alias).st_ino,
                                 os.lstat(sample).st_ino)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("alias-link",))
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(outside_fd),
                                 b"")
            finally:
                for fd in (one_fd, normal_fd, outside_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
