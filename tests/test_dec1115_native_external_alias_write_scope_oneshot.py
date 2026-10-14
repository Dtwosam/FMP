from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1115", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeOutsideAliasWriteScopeOneShotRegression(unittest.TestCase):
    def test_external_unlink_disarms_source_oneshot_and_alias_writes_have_no_original_parent_event(self):
        one_fd = None
        continuing_fd = None
        outside_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            out = []
            cursor = 0
            while cursor < len(data):
                self.assertGreaterEqual(len(data) - cursor, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, cursor)
                cursor += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - cursor)
                name = data[cursor:cursor + nbytes].split(b"\x00", 1)[0]
                cursor += nbytes
                self.assertEqual(cookie, 0)
                out.append((wd, mask, name))
            self.assertEqual(cursor, len(data))
            return out

        def real_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_source_evidence(receipt, source_wd, parent_wd, after,
                                   named_in_parent):
            actual = records(receipt)
            self.assertIn((source_wd, module.IN_MODIFY, b""), actual)
            self.assertIn((source_wd, module.IN_CLOSE_WRITE, b""), actual)
            if named_in_parent:
                self.assertIn((parent_wd, module.IN_MODIFY, b"sample"), actual)
                self.assertIn(
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"), actual
                )
            else:
                self.assertEqual(
                    actual,
                    [(source_wd, module.IN_MODIFY, b""),
                     (source_wd, module.IN_CLOSE_WRITE, b"")],
                )
            classified = module._classify_stream(receipt, source_wd, parent_wd)
            self.assertTrue(classified["well_formed"])
            self.assertFalse(classified["invalidated"])
            self.assertGreaterEqual(classified["source_content_write_events"], 1)
            result = module._evaluate(
                module.BEFORE, after, receipt, source_wd, True, False,
                directory_watch=parent_wd, directory_inventory_names=("sample",),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIs(result["can_authorize_dispatch"], False)
            self.assertIs(result["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1115-public-external-alias-write-", dir="/tmp"
        ) as tmp:
            root = Path(tmp)
            parent = root / "parent"
            outside = root / "outside"
            parent.mkdir()
            outside.mkdir()
            sample = parent / "sample"
            alias = outside / "alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            os.link(sample, alias)
            initial = (os.lstat(sample), os.lstat(alias),
                       os.lstat(parent), os.lstat(outside))
            self.assertEqual(initial[0].st_ino, initial[1].st_ino)
            self.assertEqual(initial[0].st_nlink, 2)
            self.assertEqual(module._bounded_inventory_names(parent), ("sample",))
            self.assertEqual(module._bounded_inventory_names(outside), ("alias",))
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
                    module.IN_ATTRIB | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                outside_wd = libc.inotify_add_watch(
                    outside_fd, module._checked_watch_path_bytes(outside),
                    module.IN_CREATE | module.IN_DELETE |
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(outside_wd, 0)
                for fd in (one_fd, continuing_fd, outside_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Unlink existing EXTERNAL hard-link name. Source inode
                # survives at sample; original parent namespace stays quiet.
                os.unlink(alias)
                self.assertEqual(os.lstat(sample).st_nlink, 1)
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_ATTRIB, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(continuing_fd)),
                    [(source_wd, module.IN_ATTRIB, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, module.IN_DELETE, b"alias")],
                )

                os.link(sample, alias)
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                self.assertEqual(os.lstat(alias).st_ino,
                                 os.lstat(sample).st_ino)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(
                    records(module._read_receipt_pending(continuing_fd)),
                    [(source_wd, module.IN_ATTRIB, b"")],
                )
                self.assertEqual(
                    records(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, module.IN_CREATE, b"alias")],
                )

                # Alias pathname is OUTSIDE the source parent watch.
                # Source inode still receives write events; original parent
                # receives no named alias write event.
                real_write(alias, module.AFTER)
                self.assertEqual(sample.read_bytes(), module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_source_evidence(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.AFTER, False,
                )
                self.assertEqual(
                    records(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, module.IN_MODIFY, b"alias"),
                     (outside_wd, module.IN_CLOSE_WRITE, b"alias")],
                )

                # Restoring through the ORIGINAL parent name changes the
                # same source inode, and *does* produce named parent writes.
                real_write(sample, module.BEFORE)
                self.assertEqual(alias.read_bytes(), module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_source_evidence(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.BEFORE, True,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd), b"")

                final = (os.lstat(sample), os.lstat(alias),
                         os.lstat(parent), os.lstat(outside))
                for old, new in zip(initial, final):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("alias",))
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(alias.read_bytes(), module.BEFORE)
            finally:
                if sample.exists() and not alias.exists():
                    os.link(sample, alias)
                for fd in (one_fd, continuing_fd, outside_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
