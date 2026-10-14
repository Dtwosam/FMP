from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1111", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeSourceHardlinkUnlinkAttributeOneShotRegression(unittest.TestCase):
    def test_unlink_second_name_removes_source_oneshot_before_alias_and_source_writes(self):
        one_fd = None
        independent_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            result = []
            offset = 0
            while offset < len(stream):
                self.assertGreaterEqual(len(stream) - offset, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(stream, offset)
                offset += module.EVENT.size
                self.assertLessEqual(length, len(stream) - offset)
                name = stream[offset:offset + length].split(b"\x00", 1)[0]
                offset += length
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(offset, len(stream))
            return result

        def write_bytes(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_write(stream, source_wd, parent_wd, name, after):
            observed = records(stream)
            for event in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, name),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, name),
            ):
                self.assertIn(event, observed)
            classified = module._classify_stream(stream, source_wd, parent_wd)
            self.assertTrue(classified["well_formed"])
            self.assertFalse(classified["invalidated"])
            self.assertGreaterEqual(classified["source_content_write_events"], 1)
            outcome = module._evaluate(
                module.BEFORE, after, stream, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("alias", "sample"),
            )
            self.assertEqual(outcome["status"], "BLOCKED")
            self.assertIs(outcome["can_authorize_dispatch"], False)
            self.assertIs(outcome["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1111-public-hardlink-attribute-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            alias = parent / "alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            os.link(sample, alias)
            first = (os.lstat(sample), os.lstat(alias), os.lstat(parent))
            self.assertEqual(first[0].st_ino, first[1].st_ino)
            self.assertEqual(first[0].st_dev, first[1].st_dev)
            self.assertEqual(first[0].st_nlink, 2)
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("alias", "sample"))
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
                    one_fd, module._checked_watch_path_bytes(sample),
                    module.IN_ATTRIB | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW |
                    IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                # Removing only the SECOND name changes nlink 2 -> 1.
                # Source inode still exists as sample; no source bytes move.
                os.unlink(alias)
                self.assertEqual(os.lstat(sample).st_nlink, 1)
                self.assertFalse(alias.exists())
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_ATTRIB, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertCountEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(source_wd, module.IN_ATTRIB, b""),
                     (parent_wd, module.IN_DELETE, b"alias")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                # Restoring that exact hard-link identity does not re-arm
                # the removed source-only one-shot.
                os.link(sample, alias)
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                self.assertEqual(os.lstat(alias).st_ino,
                                 os.lstat(sample).st_ino)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertCountEqual(
                    records(module._read_receipt_pending(independent_fd)),
                    [(source_wd, module.IN_ATTRIB, b""),
                     (parent_wd, module.IN_CREATE, b"alias")],
                )
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                # A real write through ALIAS changes the original sample
                # inode. Source events are unnamed, parent writes name alias.
                write_bytes(alias, module.AFTER)
                self.assertEqual(sample.read_bytes(), module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                changed = module._read_receipt_pending(independent_fd)
                verify_write(changed, source_wd, parent_wd, b"alias",
                             module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                # A separate real write via the ORIGINAL pathname restores
                # the original sample and alias bytes.
                write_bytes(sample, module.BEFORE)
                self.assertEqual(alias.read_bytes(), module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                verify_write(restored, source_wd, parent_wd, b"sample",
                             module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                final = (os.lstat(sample), os.lstat(alias), os.lstat(parent))
                for old, new in zip(first, final):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(alias.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("alias", "sample"))
            finally:
                if sample.exists() and not alias.exists():
                    os.link(sample, alias)
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
