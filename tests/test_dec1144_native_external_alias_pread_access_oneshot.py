from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1144", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ACCESS = 0x00000001
IN_OPEN = 0x00000020
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "pread"),
                     "requires native Linux inotify and pread")
class NativeExternalAliasPreadAccessOneShotRegression(unittest.TestCase):
    def test_external_alias_pread_disarms_source_access_oneshot_with_outside_name(self):
        one_fd = None
        normal_fd = None
        outside_fd = None
        read_fd = None

        def events(data):
            self.assertIs(type(data), bytes)
            output = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(
                    data, offset
                )
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - offset)
                name = data[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                output.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return output

        def actual_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_source_write(data, source_wd, parent_wd, after):
            native = events(data)
            allowed = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(native)
            self.assertTrue(all(e in allowed for e in native))
            for required in allowed:
                self.assertIn(required, native)
            classified = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(classified["well_formed"])
            self.assertFalse(classified["invalidated"])
            self.assertGreaterEqual(classified["source_content_write_events"], 1)
            decision = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(decision["status"], "BLOCKED")
            self.assertIs(decision["can_authorize_dispatch"], False)
            self.assertIs(decision["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1144-public-external-alias-pread-", dir="/tmp"
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
            first = (os.lstat(sample), os.lstat(alias),
                     os.lstat(parent), os.lstat(outside))
            self.assertEqual(first[0].st_dev, first[1].st_dev)
            self.assertEqual(first[0].st_ino, first[1].st_ino)
            self.assertEqual(first[0].st_nlink, 2)
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            self.assertEqual(module._bounded_inventory_names(outside),
                             ("alias",))
            try:
                normal_fd, source_wd, parent_wd = module._start_watch(sample)
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
                self.assertEqual(len({one_fd, normal_fd, outside_fd}), 3)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample),
                    IN_ACCESS | module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                outside_wd = libc.inotify_add_watch(
                    outside_fd, module._checked_watch_path_bytes(outside),
                    IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(outside_wd, 0)
                for fd in (one_fd, normal_fd, outside_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Real O_RDONLY open through the EXTERNAL alias emits a
                # named outside-directory OPEN. Source ACCESS one-shot
                # remains active because no read syscall has happened.
                read_fd = os.open(alias, os.O_RDONLY | os.O_CLOEXEC)
                self.assertEqual(os.fstat(read_fd).st_ino,
                                 first[0].st_ino)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(
                    events(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, IN_OPEN, b"alias")],
                )

                # Actual positional read on the shared watched source
                # inode consumes original unsafe ACCESS one-shot, while
                # the outside directory identifies the alias pathname.
                self.assertEqual(os.pread(read_fd, 6, 0), module.BEFORE[:6])
                self.assertEqual(
                    events(module._read_receipt_pending(one_fd)),
                    [(one_wd, IN_ACCESS, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(
                    events(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, IN_ACCESS, b"alias")],
                )

                os.close(read_fd)
                read_fd = None
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(
                    events(module._read_receipt_pending(outside_fd)),
                    [(outside_wd, IN_CLOSE_NOWRITE, b"alias")],
                )

                # The outside witness sees child events only for an alias
                # operation IN outside/. Do not read alias again for a
                # verification assertion; that would itself add events.
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(os.lstat(alias).st_ino,
                                 os.lstat(sample).st_ino)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(module._read_receipt_pending(outside_fd),
                                 b"")

                # Actual changed-byte and restoring writes use original
                # parent/sample. The normal continuing observer still
                # captures both source and named parent write receipts;
                # the removed original one-shot and outside witness do not.
                actual_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_source_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                actual_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_source_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(module._read_receipt_pending(outside_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                last = (os.lstat(sample), os.lstat(alias),
                        os.lstat(parent), os.lstat(outside))
                for before, after in zip(first, last):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                # The native outside-directory witness is subscribed to
                # read-side IN_OPEN and IN_ACCESS. The inventory helper
                # itself calls os.scandir(outside), which opens/accesses
                # that DIRECTORY and would create legitimate self events.
                # Finish the outside witness lifetime after its final
                # quiet check and BEFORE the verification scan.
                self.assertEqual(module._read_receipt_pending(outside_fd),
                                 b"")
                os.close(outside_fd)
                with self.assertRaises(OSError):
                    os.fstat(outside_fd)
                outside_fd = None
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("alias",))
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
            finally:
                if read_fd is not None:
                    os.close(read_fd)
                for fd in (one_fd, normal_fd, outside_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
