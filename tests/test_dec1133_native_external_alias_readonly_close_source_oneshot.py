from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1133", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "real native Linux inotify required")
class NativeExternalAliasReadOnlyCloseSourceOneShotRegression(unittest.TestCase):
    def test_external_alias_readclose_consumes_source_oneshot_without_original_parent_event(self):
        original_fd = None
        continuing_fd = None
        outside_fd = None
        read_fd = None

        def native(data):
            self.assertIs(type(data), bytes)
            events = []
            position = 0
            while position < len(data):
                self.assertGreaterEqual(len(data) - position,
                                        module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(
                    data, position
                )
                position += module.EVENT.size
                self.assertLessEqual(length, len(data) - position)
                name = data[position:position + length].split(b"\x00", 1)[0]
                position += length
                self.assertEqual(cookie, 0)
                events.append((wd, mask, name))
            self.assertEqual(position, len(data))
            return events

        def real_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_actual_write(stream, source_wd, parent_wd, after):
            observed = native(stream)
            allowed = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(observed)
            self.assertTrue(all(event in allowed for event in observed))
            for expected in allowed:
                self.assertIn(expected, observed)
            parsed = module._classify_stream(stream, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, stream, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1133-public-external-alias-readclose-", dir="/tmp"
        ) as temp:
            root = Path(temp)
            parent = root / "parent"
            outside = root / "outside"
            parent.mkdir()
            outside.mkdir()
            sample = parent / "sample"
            alias = outside / "alias"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            os.link(sample, alias)
            first = (os.lstat(sample), os.lstat(alias), os.lstat(parent),
                     os.lstat(outside))
            self.assertEqual(first[0].st_dev, first[1].st_dev)
            self.assertEqual(first[0].st_ino, first[1].st_ino)
            self.assertEqual(first[0].st_nlink, 2)
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            self.assertEqual(module._bounded_inventory_names(outside),
                             ("alias",))
            try:
                continuing_fd, source_wd, parent_wd = module._start_watch(
                    sample
                )
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                original_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                outside_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(original_fd, 2)
                self.assertGreater(outside_fd, 2)
                self.assertEqual(
                    len({original_fd, continuing_fd, outside_fd}), 3
                )
                original_wd = libc.inotify_add_watch(
                    original_fd,
                    module._checked_watch_path_bytes(sample),
                    IN_CLOSE_NOWRITE | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                outside_wd = libc.inotify_add_watch(
                    outside_fd,
                    module._checked_watch_path_bytes(outside),
                    IN_CLOSE_NOWRITE | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW,
                )
                self.assertGreater(original_wd, 0)
                self.assertGreater(outside_wd, 0)
                for fd in (original_fd, continuing_fd, outside_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # The ALIAS is in another directory but refers to the
                # SAME inode as sample. No bytes are read or written.
                read_fd = os.open(alias, os.O_RDONLY | os.O_CLOEXEC)
                self.assertEqual(os.fstat(read_fd).st_ino,
                                 os.lstat(sample).st_ino)
                for fd in (original_fd, continuing_fd, outside_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")
                os.close(read_fd)
                read_fd = None

                # Source-inode watch gets an UNNAMED read close, consumed
                # even though sample path remains present and unmodified.
                self.assertEqual(
                    native(module._read_receipt_pending(original_fd)),
                    [(original_wd, IN_CLOSE_NOWRITE, b""),
                     (original_wd, module.IN_IGNORED, b"")],
                )
                # The real normal source+original-parent watcher does not
                # subscribe to CLOSE_NOWRITE and must remain fully quiet.
                self.assertEqual(
                    module._read_receipt_pending(continuing_fd), b""
                )
                # A separate outside-directory watcher identifies the alias
                # basename, which is NOT a child of the original parent.
                self.assertEqual(
                    native(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, IN_CLOSE_NOWRITE, b"alias")],
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(alias.read_bytes(), module.BEFORE)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(outside_fd),
                                 b"")

                # Later genuine changed-byte and restoring writes through
                # SAMPLE reach normal source+original-parent watches. The
                # consumed original source ONE_SHOT cannot see either.
                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                verify_actual_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd), b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                verify_actual_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd), b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                final = (os.lstat(sample), os.lstat(alias), os.lstat(parent),
                         os.lstat(outside))
                for original, latest in zip(first, final):
                    self.assertEqual(
                        (original.st_dev, original.st_ino, original.st_mode,
                         original.st_nlink),
                        (latest.st_dev, latest.st_ino, latest.st_mode,
                         latest.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(alias.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("alias",))
            finally:
                if read_fd is not None:
                    os.close(read_fd)
                for fd in (original_fd, continuing_fd, outside_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
