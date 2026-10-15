from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1149", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_ACCESS = 0x00000001
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeStatVersusScandirDirectoryReadRegression(unittest.TestCase):
    def test_stat_and_lstat_are_quiet_before_inventory_scandir_opens_directory(self):
        original_fd = None
        read_witness_fd = None
        normal_fd = None

        def native(data):
            self.assertIs(type(data), bytes)
            seen = []
            cursor = 0
            while cursor < len(data):
                self.assertGreaterEqual(len(data) - cursor, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(
                    data, cursor,
                )
                cursor += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - cursor)
                name = data[cursor:cursor + nbytes].split(b"\x00", 1)[0]
                cursor += nbytes
                self.assertEqual(cookie, 0)
                seen.append((wd, mask, name))
            self.assertEqual(cursor, len(data))
            return seen

        def real_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def check_genuine_write(receipt, source_wd, parent_wd, after):
            observed = native(receipt)
            allowed = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(observed)
            self.assertTrue(all(event in allowed for event in observed))
            for required in allowed:
                self.assertIn(required, observed)
            parsed = module._classify_stream(receipt, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            decision = module._evaluate(
                module.BEFORE, after, receipt, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(decision["status"], "BLOCKED")
            self.assertIs(decision["can_authorize_dispatch"], False)
            self.assertIs(decision["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1149-public-stat-vs-scandir-", dir="/tmp"
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
            initial = (os.lstat(sample), os.lstat(alias),
                       os.lstat(parent), os.lstat(outside))
            self.assertEqual(initial[0].st_ino, initial[1].st_ino)
            self.assertEqual(initial[0].st_nlink, 2)
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
                original_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                read_witness_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(original_fd, 2)
                self.assertGreater(read_witness_fd, 2)
                self.assertEqual(
                    len({original_fd, read_witness_fd, normal_fd}), 3
                )
                original_wd = libc.inotify_add_watch(
                    original_fd, module._checked_watch_path_bytes(outside),
                    IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE |
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                witness_wd = libc.inotify_add_watch(
                    read_witness_fd,
                    module._checked_watch_path_bytes(outside),
                    IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(original_wd, 0)
                self.assertGreater(witness_wd, 0)
                for fd in (original_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Repeated metadata lookups on both the watched directory
                # and its hard-link child do NOT open the directory for
                # enumeration, and therefore must NOT emit OPEN, ACCESS or
                # CLOSE_NOWRITE. Original alternative one-shot stays armed.
                for pathname in (outside, alias, parent, sample):
                    stat_view = os.stat(pathname, follow_symlinks=False)
                    lstat_view = os.lstat(pathname)
                    self.assertEqual(
                        (stat_view.st_dev, stat_view.st_ino,
                         stat_view.st_mode, stat_view.st_nlink),
                        (lstat_view.st_dev, lstat_view.st_ino,
                         lstat_view.st_mode, lstat_view.st_nlink),
                    )
                for fd in (original_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # The real bounded inventory helper uses os.scandir().
                # Its DIRECTORY opening is itself the original one-shot's
                # first subscribed event. It is NOT a sample content write.
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("alias",))
                self.assertEqual(
                    native(module._read_receipt_pending(original_fd)),
                    [(original_wd, IN_OPEN | module.IN_ISDIR, b""),
                     (original_wd, module.IN_IGNORED, b"")],
                )
                three_stages = [
                    (witness_wd, IN_OPEN | module.IN_ISDIR, b""),
                    (witness_wd, IN_ACCESS | module.IN_ISDIR, b""),
                    (witness_wd, IN_CLOSE_NOWRITE | module.IN_ISDIR, b""),
                ]
                self.assertEqual(
                    native(module._read_receipt_pending(read_witness_fd)),
                    three_stages,
                )
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Second bounded scan is independent positive proof of the
                # same three native directory read-side event identities,
                # while the original one-shot cannot re-register.
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("alias",))
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(
                    native(module._read_receipt_pending(read_witness_fd)),
                    three_stages,
                )
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Close the positive directory read witness BEFORE any
                # later directory inventory check; otherwise the inventory
                # verification itself would contaminate a quiet assertion.
                self.assertEqual(
                    module._read_receipt_pending(read_witness_fd), b""
                )
                os.close(read_witness_fd)
                with self.assertRaises(OSError):
                    os.fstat(read_witness_fd)
                read_witness_fd = None

                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                check_genuine_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                check_genuine_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                final = (os.lstat(sample), os.lstat(alias),
                         os.lstat(parent), os.lstat(outside))
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
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("alias",))
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
            finally:
                for fd in (original_fd, read_witness_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
