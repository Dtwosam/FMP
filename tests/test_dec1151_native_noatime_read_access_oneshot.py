from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1151", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_ACCESS = 0x00000001
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "O_PATH")
                     and hasattr(os, "O_NOATIME"),
                     "requires Linux inotify, O_PATH and O_NOATIME")
class NativeNoAtimeReadAccessOneShotRegression(unittest.TestCase):
    def test_noatime_real_read_emits_access_without_advancing_atime(self):
        one_fd = None
        continuing_fd = None
        read_witness_fd = None
        path_fd = None
        read_fd = None

        def events(data):
            self.assertIs(type(data), bytes)
            found = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                found.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return found

        def real_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_real_write(data, source_wd, parent_wd, after):
            native = events(data)
            permitted = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(native)
            self.assertTrue(all(item in permitted for item in native))
            for expected in permitted:
                self.assertIn(expected, native)
            classified = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(classified["well_formed"])
            self.assertFalse(classified["invalidated"])
            self.assertGreaterEqual(classified["source_content_write_events"], 1)
            outcome = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(outcome["status"], "BLOCKED")
            self.assertIs(outcome["can_authorize_dispatch"], False)
            self.assertIs(outcome["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            dir="/tmp", prefix="dec1151-public-noatime-access-source-"
        ) as temp:
            parent = Path(temp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            first = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
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
                read_witness_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(one_fd, 2)
                self.assertGreater(read_witness_fd, 2)
                self.assertEqual(
                    len({one_fd, continuing_fd, read_witness_fd}), 3
                )
                original_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample),
                    IN_ACCESS | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW |
                    IN_ONESHOT,
                )
                witness_wd = libc.inotify_add_watch(
                    read_witness_fd,
                    module._checked_watch_path_bytes(sample),
                    IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE |
                    module.IN_DONT_FOLLOW,
                )
                self.assertGreater(original_wd, 0)
                self.assertGreater(witness_wd, 0)
                for fd in (one_fd, continuing_fd, read_witness_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Linux O_PATH obtains a path-only inode reference, not a
                # conventional read descriptor. It does not emit IN_OPEN
                # or CLOSE_NOWRITE, and cannot itself read content.
                path_fd = os.open(sample, os.O_PATH | os.O_CLOEXEC)
                self.assertEqual(os.fstat(path_fd).st_ino,
                                 first[0].st_ino)
                for fd in (one_fd, continuing_fd, read_witness_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")
                os.close(path_fd)
                path_fd = None
                for fd in (one_fd, continuing_fd, read_witness_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # A real O_RDONLY descriptor emits IN_OPEN, but the
                # original unsafe one-shot is subscribed to IN_ACCESS
                # instead; it must remain active until actual read().
                # The PUBLIC file belongs to this test process. O_NOATIME
                # suppresses inode access-time updates, not native ACCESS.
                atime_before = os.lstat(sample).st_atime_ns
                read_fd = os.open(
                    sample, os.O_RDONLY | os.O_CLOEXEC | os.O_NOATIME
                )
                self.assertEqual(os.fstat(read_fd).st_size,
                                 len(module.BEFORE))
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(
                    events(module._read_receipt_pending(read_witness_fd)),
                    [(witness_wd, IN_OPEN, b"")],
                )
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                # Native IN_ACCESS occurs when real bytes are READ, not
                # merely when the read-only file is opened. First ACCESS
                # consumes original one-shot even though bytes stay same.
                self.assertEqual(os.read(read_fd, 6), module.BEFORE[:6])
                self.assertEqual(
                    events(module._read_receipt_pending(one_fd)),
                    [(original_wd, IN_ACCESS, b""),
                     (original_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    events(module._read_receipt_pending(read_witness_fd)),
                    [(witness_wd, IN_ACCESS, b"")],
                )
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                # Original is already gone BEFORE CLOSE_NOWRITE arrives;
                # the separate read-event witness sees the real close.
                os.close(read_fd)
                read_fd = None
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(
                    events(module._read_receipt_pending(read_witness_fd)),
                    [(witness_wd, IN_CLOSE_NOWRITE, b"")],
                )
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                # Check timestamps before any incidental verification
                # read without O_NOATIME might itself change access time.
                after_noatime = os.lstat(sample)
                self.assertEqual(after_noatime.st_atime_ns, atime_before)
                self.assertEqual(after_noatime.st_mtime_ns,
                                 first[0].st_mtime_ns)
                self.assertEqual(after_noatime.st_ctime_ns,
                                 first[0].st_ctime_ns)

                # Stop the positive read-side witness BEFORE verifying
                # bytes. sample.read_bytes itself would generate more read
                # events; it must not contaminate the event assertions.
                os.close(read_witness_fd)
                with self.assertRaises(OSError):
                    os.fstat(read_witness_fd)
                read_witness_fd = None
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                # Real later writes remain invisible to the removed
                # alternative ONESHOT, while unchanged continuing normal
                # source+parent helper positively captures them.
                real_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_real_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")
                real_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_real_write(
                    module._read_receipt_pending(continuing_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                last = (os.lstat(sample), os.lstat(parent))
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
            finally:
                for fd in (path_fd, read_fd, read_witness_fd, one_fd,
                           continuing_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
