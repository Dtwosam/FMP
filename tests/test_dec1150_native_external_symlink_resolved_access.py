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
spec = importlib.util.spec_from_file_location("dec677_native_dec1150", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ACCESS = 0x00000001
IN_OPEN = 0x00000020
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "pread"),
                     "native Linux inotify and pread required")
class NativeExternalSymlinkResolvedAccessRegression(unittest.TestCase):
    def test_external_symlink_read_resolves_to_original_source_and_parent(self):
        original_fd = None
        normal_fd = None
        original_parent_read_fd = None
        outside_read_fd = None
        read_fd = None

        def events(data):
            self.assertIs(type(data), bytes)
            observed = []
            index = 0
            while index < len(data):
                self.assertGreaterEqual(len(data) - index, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, index)
                index += module.EVENT.size
                self.assertLessEqual(length, len(data) - index)
                name = data[index:index + length].split(b"\x00", 1)[0]
                index += length
                self.assertEqual(cookie, 0)
                observed.append((wd, mask, name))
            self.assertEqual(index, len(data))
            return observed

        def add_watch(libc, fd, path, mask):
            wd = libc.inotify_add_watch(
                fd, module._checked_watch_path_bytes(path), mask
            )
            self.assertGreater(wd, 0)
            return wd

        def write_bytes(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def assert_source_write(receipt, source_wd, parent_wd, after):
            observed = events(receipt)
            allowed = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(observed)
            self.assertTrue(all(e in allowed for e in observed))
            for e in allowed:
                self.assertIn(e, observed)
            parsed = module._classify_stream(receipt, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            result = module._evaluate(
                module.BEFORE, after, receipt, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIs(result["can_authorize_dispatch"], False)
            self.assertIs(result["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1150-public-external-symlink-access-", dir="/tmp"
        ) as temp:
            root = Path(temp)
            parent = root / "parent"
            outside = root / "outside"
            parent.mkdir()
            outside.mkdir()
            sample = parent / "sample"
            link = outside / "alias-link"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            os.symlink(sample, link)
            original = (os.lstat(sample), os.lstat(link),
                        os.lstat(parent), os.lstat(outside))
            self.assertEqual(original[0].st_nlink, 1)
            self.assertTrue(stat.S_ISLNK(original[1].st_mode))
            self.assertEqual(os.readlink(link), str(sample))
            self.assertEqual(os.stat(link).st_ino, original[0].st_ino)
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
                original_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                original_parent_read_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                outside_read_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertEqual(
                    len({original_fd, normal_fd, original_parent_read_fd,
                         outside_read_fd}), 4,
                )
                one_wd = add_watch(
                    libc, original_fd, sample,
                    IN_ACCESS | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW |
                    IN_ONESHOT,
                )
                read_parent_wd = add_watch(
                    libc, original_parent_read_fd, parent,
                    IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                read_outside_wd = add_watch(
                    libc, outside_read_fd, outside,
                    IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(read_outside_wd, 0)
                for fd in (original_fd, normal_fd, original_parent_read_fd,
                           outside_read_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Following an external SYMLINK resolves the actual target
                # dentry parent/sample. The outside directory contains
                # only the symlink path and sees no child read operations.
                read_fd = os.open(link, os.O_RDONLY | os.O_CLOEXEC)
                self.assertEqual(os.fstat(read_fd).st_ino,
                                 original[0].st_ino)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(
                    events(module._read_receipt_pending(
                        original_parent_read_fd
                    )), [(read_parent_wd, IN_OPEN, b"sample")],
                )
                self.assertEqual(module._read_receipt_pending(outside_read_fd),
                                 b"")

                # Genuine positive-byte read consumes SOURCE ACCESS one-shot;
                # original parent positively sees name "sample", and
                # external symlink directory still sees no named event.
                self.assertEqual(os.pread(read_fd, 6, 0),
                                 module.BEFORE[:6])
                self.assertEqual(
                    events(module._read_receipt_pending(original_fd)),
                    [(one_wd, IN_ACCESS, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    events(module._read_receipt_pending(
                        original_parent_read_fd
                    )), [(read_parent_wd, IN_ACCESS, b"sample")],
                )
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(module._read_receipt_pending(outside_read_fd),
                                 b"")

                os.close(read_fd)
                read_fd = None
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(
                    events(module._read_receipt_pending(
                        original_parent_read_fd
                    )), [(read_parent_wd, IN_CLOSE_NOWRITE, b"sample")],
                )
                self.assertEqual(module._read_receipt_pending(outside_read_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Close both read-side witnesses before verification reads
                # and final scandir inventories could generate self-events.
                for fd in (original_parent_read_fd, outside_read_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
                original_parent_read_fd = None
                outside_read_fd = None

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                write_bytes(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                assert_source_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                write_bytes(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                assert_source_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                final = (os.lstat(sample), os.lstat(link),
                         os.lstat(parent), os.lstat(outside))
                for old, new in zip(original, final):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(os.readlink(link), str(sample))
                self.assertEqual(os.stat(link).st_ino, os.lstat(sample).st_ino)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("alias-link",))
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
            finally:
                if read_fd is not None:
                    os.close(read_fd)
                for fd in (original_fd, normal_fd, original_parent_read_fd,
                           outside_read_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
