from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1213", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(
    sys.platform == "linux" and hasattr(os, "posix_fallocate"),
    "Linux native inotify and posix_fallocate required",
)
class NativePosixFallocateEventsRegression(unittest.TestCase):
    def test_same_range_and_extended_allocation_emit_modify_and_zero_extend(self):
        original_fd = None
        normal_fd = None
        writer_fd = None
        restore_fd = None

        def events(data):
            self.assertIs(type(data), bytes)
            rows = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - offset)
                name = data[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                rows.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return rows

        before = module.BEFORE
        allocated_length = 4096
        self.assertLess(len(before), allocated_length)
        extended = before + b"\x00" * (allocated_length - len(before))

        with tempfile.TemporaryDirectory(
            prefix="dec1213-public-posix-fallocate-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(before), len(before))
            first = (os.lstat(sample), os.lstat(parent))
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
                original_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreaterEqual(original_fd, 0)
                original_wd = libc.inotify_add_watch(
                    original_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(original_wd, 0)
                self.assertNotEqual(original_fd, normal_fd)
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                def require_exact_modify(old_bytes, new_bytes):
                    receipt = module._read_receipt_pending(normal_fd)
                    self.assertCountEqual(
                        events(receipt),
                        [(source_wd, module.IN_MODIFY, b""),
                         (parent_wd, module.IN_MODIFY, b"sample")],
                    )
                    verdict = module._evaluate(
                        old_bytes, new_bytes, receipt,
                        source_wd, True, False,
                        directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                    self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)

                # This libc/POSIX allocation is NOT a userspace write()
                # or pwrite(), but produces native MODIFY even when the
                # full requested interval is already in existing data.
                os.posix_fallocate(writer_fd, 0, len(before))
                self.assertEqual(os.fstat(writer_fd).st_size, len(before))
                require_exact_modify(before, before)
                self.assertEqual(
                    events(module._read_receipt_pending(original_fd)),
                    [(original_wd, module.IN_MODIFY, b""),
                     (original_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(sample.read_bytes(), before)

                # Allocation beyond EOF genuinely extends logical length
                # and introduces a zero-filled suffix without pwrite().
                os.posix_fallocate(writer_fd, 0, allocated_length)
                self.assertEqual(os.fstat(writer_fd).st_size, allocated_length)
                require_exact_modify(before, extended)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(sample.read_bytes(), extended)

                # Even repeating the already-allocated interval still
                # emits another separately drained MODIFY on Linux.
                os.posix_fallocate(writer_fd, 0, allocated_length)
                self.assertEqual(os.fstat(writer_fd).st_size, allocated_length)
                require_exact_modify(extended, extended)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(sample.read_bytes(), extended)

                os.close(writer_fd)
                writer_fd = None
                self.assertCountEqual(
                    events(module._read_receipt_pending(normal_fd)),
                    [(source_wd, module.IN_CLOSE_WRITE, b""),
                     (parent_wd, module.IN_CLOSE_WRITE, b"sample")],
                )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                # Restore generated PUBLIC source using one real
                # truncating writable descriptor and observed write.
                restore_fd = os.open(
                    sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC
                )
                self.assertEqual(os.write(restore_fd, before), len(before))
                os.fsync(restore_fd)
                os.close(restore_fd)
                restore_fd = None
                receipt = module._read_receipt_pending(normal_fd)
                restored_events = events(receipt)
                allowed = {
                    (source_wd, module.IN_MODIFY, b""),
                    (parent_wd, module.IN_MODIFY, b"sample"),
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                }
                self.assertTrue(restored_events)
                self.assertTrue(all(row in allowed for row in restored_events))
                self.assertTrue(allowed.issubset(set(restored_events)))
                verdict = module._evaluate(
                    extended, before, receipt, source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)
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
                for fd in (writer_fd, restore_fd, original_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
