from __future__ import annotations

import ctypes
import importlib.util
import mmap
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1160", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "requires native Linux inotify")
class NativePrivateMmapCopyOnWriteRegression(unittest.TestCase):
    def test_private_mmap_mutation_does_not_touch_file_or_consume_modify_oneshot(self):
        one_fd = None
        normal_fd = None
        read_watch_fd = None
        source_fd = None

        def events(raw):
            self.assertIs(type(raw), bytes)
            observed = []
            i = 0
            while i < len(raw):
                self.assertGreaterEqual(len(raw) - i, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(raw, i)
                i += module.EVENT.size
                self.assertLessEqual(nbytes, len(raw) - i)
                name = raw[i:i + nbytes].split(b"\x00", 1)[0]
                i += nbytes
                self.assertEqual(cookie, 0)
                observed.append((wd, mask, name))
            self.assertEqual(i, len(raw))
            return observed

        def actual_write(path, data):
            f = os.open(path, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC)
            try:
                self.assertEqual(os.write(f, data), len(data))
                os.fsync(f)
            finally:
                os.close(f)

        def assert_genuine_write(raw, source_wd, parent_wd, before, after):
            e = events(raw)
            valid = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(e)
            self.assertTrue(all(x in valid for x in e))
            for x in valid:
                self.assertIn(x, e)
            result = module._evaluate(
                before, after, raw, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIs(result["can_authorize_dispatch"], False)
            self.assertIs(result["independent_os_proof_verified"], False)

        pos = module.BEFORE.find(b"SOURCE")
        self.assertGreaterEqual(pos, 0)
        changed = module.BEFORE[:pos] + b"X" + module.BEFORE[pos + 1:]
        self.assertNotEqual(changed, module.BEFORE)
        self.assertEqual(len(changed), len(module.BEFORE))

        with tempfile.TemporaryDirectory(
            prefix="dec1160-public-private-mmap-", dir="/tmp"
        ) as temp:
            parent = Path(temp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            original = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
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
                read_watch_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertEqual(len({one_fd, read_watch_fd, normal_fd}), 3)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                read_wd = libc.inotify_add_watch(
                    read_watch_fd,
                    module._checked_watch_path_bytes(sample),
                    IN_OPEN | IN_CLOSE_NOWRITE | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(read_wd, 0)
                for fd in (one_fd, read_watch_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # ACCESS_COPY uses a private COW map of a real O_RDONLY
                # source: modifying mapped memory changes the mapping
                # but must NOT mutate the underlying regular-file bytes.
                source_fd = os.open(sample, os.O_RDONLY | os.O_CLOEXEC)
                self.assertEqual(
                    events(module._read_receipt_pending(read_watch_fd)),
                    [(read_wd, IN_OPEN, b"")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                with mmap.mmap(
                    source_fd, len(module.BEFORE), access=mmap.ACCESS_COPY
                ) as mapping:
                    mapping[pos:pos + 1] = b"X"
                    self.assertEqual(mapping[:], changed)
                    mapping.flush()
                    self.assertEqual(module._read_receipt_pending(one_fd),
                                     b"")
                    self.assertEqual(
                        module._read_receipt_pending(normal_fd), b""
                    )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                os.close(source_fd)
                source_fd = None
                self.assertEqual(
                    events(module._read_receipt_pending(read_watch_fd)),
                    [(read_wd, IN_CLOSE_NOWRITE, b"")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Close read observer BEFORE content verification to avoid
                # producing additional read-open and read-close receipts.
                os.close(read_watch_fd)
                with self.assertRaises(OSError):
                    os.fstat(read_watch_fd)
                read_watch_fd = None
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Only genuine ordinary changed-byte file write, not
                # private mapped COW assignment, can consume the original
                # test-only source MODIFY|CLOSE_WRITE|ONESHOT.
                actual_write(sample, changed)
                self.assertEqual(
                    events(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_MODIFY, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                assert_genuine_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.BEFORE, changed,
                )
                self.assertEqual(sample.read_bytes(), changed)

                actual_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                assert_genuine_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, changed, module.BEFORE,
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                later = (os.lstat(sample), os.lstat(parent))
                for before, after in zip(original, later):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                if source_fd is not None:
                    os.close(source_fd)
                for fd in (one_fd, read_watch_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
