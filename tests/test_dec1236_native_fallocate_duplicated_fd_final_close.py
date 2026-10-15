from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1236", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeDupFallocateLifetimeRegression(unittest.TestCase):
    def test_duplicated_writer_modify_continues_until_last_close_write(self):
        normal_fd = original_fd = writer_fd = dup_fd = restore_fd = None
        before = b"A" * 16 + b"B" * 16 + b"C" * 16
        zeroed = b"A" * 16 + b"\x00" * 16 + b"C" * 16

        def rows(data):
            self.assertIs(type(data), bytes)
            output = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(data) - pos)
                name = data[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                self.assertEqual(cookie, 0)
                output.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return output

        with tempfile.TemporaryDirectory(
            prefix="dec1236-public-dup-fallocate-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(before), len(before))
            first = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent), ("sample",))
            try:
                normal_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                libc.fallocate.argtypes = [
                    ctypes.c_int, ctypes.c_int,
                    ctypes.c_longlong, ctypes.c_longlong
                ]
                libc.fallocate.restype = ctypes.c_int
                original_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreaterEqual(original_fd, 0)
                original_wd = libc.inotify_add_watch(
                    original_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(original_wd, 0)
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                dup_fd = os.dup(writer_fd)
                self.assertNotEqual(writer_fd, dup_fd)
                self.assertEqual((os.fstat(writer_fd).st_dev,
                                  os.fstat(writer_fd).st_ino),
                                 (os.fstat(dup_fd).st_dev,
                                  os.fstat(dup_fd).st_ino))

                for i, fd in enumerate((writer_fd, dup_fd)):
                    self.assertEqual(
                        libc.fallocate(fd, 0x11, 16, 16), 0,
                        os.strerror(ctypes.get_errno()),
                    )
                    receipt = module._read_receipt_pending(normal_fd)
                    self.assertCountEqual(
                        rows(receipt),
                        [(source_wd, module.IN_MODIFY, b""),
                         (parent_wd, module.IN_MODIFY, b"sample")],
                    )
                    outcome = module._evaluate(
                        before if i == 0 else zeroed,
                        zeroed, receipt, source_wd, True, False,
                        directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(outcome["status"], "BLOCKED")
                    self.assertIs(outcome["can_authorize_dispatch"], False)
                    self.assertIs(outcome["independent_os_proof_verified"], False)
                    if i == 0:
                        self.assertEqual(
                            rows(module._read_receipt_pending(original_fd)),
                            [(original_wd, module.IN_MODIFY, b""),
                             (original_wd, module.IN_IGNORED, b"")],
                        )
                    else:
                        self.assertEqual(module._read_receipt_pending(original_fd),
                                         b"")
                    self.assertEqual(sample.read_bytes(), zeroed)
                    self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                os.close(writer_fd)
                writer_fd = None
                # Closing the first duplicate does NOT release the
                # still-open shared Linux file description.
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(os.fstat(dup_fd).st_size, len(before))

                os.close(dup_fd)
                dup_fd = None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd, module.IN_CLOSE_WRITE, b""),
                     (parent_wd, module.IN_CLOSE_WRITE, b"sample")],
                )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                restore_fd = os.open(
                    sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC
                )
                self.assertEqual(os.write(restore_fd, before), len(before))
                os.fsync(restore_fd)
                os.close(restore_fd)
                restore_fd = None
                receipt = module._read_receipt_pending(normal_fd)
                actual = rows(receipt)
                expected = {
                    (source_wd, module.IN_MODIFY, b""),
                    (parent_wd, module.IN_MODIFY, b"sample"),
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                }
                self.assertTrue(actual)
                self.assertTrue(all(row in expected for row in actual))
                self.assertTrue(expected.issubset(set(actual)))
                result = module._evaluate(
                    zeroed, before, receipt, source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIs(result["can_authorize_dispatch"], False)
                self.assertIs(result["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                final = (os.lstat(sample), os.lstat(parent))
                for old, new in zip(first, final):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), before)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                for fd in (writer_fd, dup_fd, restore_fd, original_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
