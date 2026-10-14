from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1114", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "requires native Linux inotify")
class NativeCrossParentHardlinkCreationOneShotRegression(unittest.TestCase):
    def test_external_alias_creation_consumes_source_oneshot_without_parent_entry_events(self):
        source_oneshot_fd = None
        continuing_fd = None
        outside_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            observed = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                observed.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return observed

        def real_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_write(receipt, source_wd, parent_wd, after):
            observed = records(receipt)
            for expected in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(expected, observed)
            classified = module._classify_stream(receipt, source_wd, parent_wd)
            self.assertTrue(classified["well_formed"])
            self.assertFalse(classified["invalidated"])
            self.assertGreaterEqual(classified["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, receipt, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1114-public-cross-parent-hardlink-", dir="/tmp"
        ) as tmp:
            root = Path(tmp)
            parent = root / "parent"
            outside = root / "outside"
            parent.mkdir()
            outside.mkdir()
            sample = parent / "sample"
            alias = outside / "alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = (os.lstat(sample), os.lstat(parent), os.lstat(outside))
            self.assertEqual(initial[0].st_nlink, 1)
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
                source_oneshot_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                outside_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(source_oneshot_fd, 2)
                self.assertGreater(outside_fd, 2)
                self.assertEqual(
                    len({source_oneshot_fd, continuing_fd, outside_fd}), 3
                )
                original_wd = libc.inotify_add_watch(
                    source_oneshot_fd,
                    module._checked_watch_path_bytes(sample),
                    module.IN_ATTRIB | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                outside_wd = libc.inotify_add_watch(
                    outside_fd, module._checked_watch_path_bytes(outside),
                    module.IN_CREATE | module.IN_DELETE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(original_wd, 0)
                self.assertGreater(outside_wd, 0)
                for fd in (source_oneshot_fd, continuing_fd, outside_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Real alias creation changes the watched SOURCE inode's
                # link count, but changes an entry in a DIFFERENT directory.
                os.link(sample, alias)
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                self.assertEqual(os.lstat(alias).st_ino,
                                 os.lstat(sample).st_ino)
                self.assertEqual(
                    records(module._read_receipt_pending(source_oneshot_fd)),
                    [(original_wd, module.IN_ATTRIB, b""),
                     (original_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(continuing_fd)),
                    [(source_wd, module.IN_ATTRIB, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, module.IN_CREATE, b"alias")],
                )
                self.assertEqual(module._read_receipt_pending(source_oneshot_fd),
                                 b"")

                os.unlink(alias)
                self.assertEqual(os.lstat(sample).st_nlink, 1)
                self.assertFalse(alias.exists())
                self.assertEqual(
                    records(module._read_receipt_pending(continuing_fd)),
                    [(source_wd, module.IN_ATTRIB, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, module.IN_DELETE, b"alias")],
                )
                self.assertEqual(module._read_receipt_pending(source_oneshot_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                # Actual writes in the original parent are captured by its
                # continuing watcher despite destroyed source one-shot.
                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(source_oneshot_fd),
                                 b"")
                verify_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd), b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(source_oneshot_fd),
                                 b"")
                verify_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd), b"")

                final = (os.lstat(sample), os.lstat(parent),
                         os.lstat(outside))
                for before, after in zip(initial, final):
                    self.assertEqual(
                        (before.st_dev, before.st_ino,
                         before.st_mode, before.st_nlink),
                        (after.st_dev, after.st_ino,
                         after.st_mode, after.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(outside), ())
            finally:
                for fd in (source_oneshot_fd, continuing_fd, outside_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
