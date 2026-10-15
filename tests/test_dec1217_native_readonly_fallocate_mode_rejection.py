from __future__ import annotations

import ctypes
import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1217", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeReadonlyFallocateModesRejectedRegression(unittest.TestCase):
    def test_four_readonly_fallocate_modes_reject_without_mutation(self):
        original_fd = None
        read_witness_fd = None
        normal_fd = None
        reader_fd = None
        writer_fd = None

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
        at = before.index(b"SOURCE")
        changed = before[:at] + b"X" + before[at + 1:]
        self.assertEqual(len(before), len(changed))
        self.assertNotEqual(before, changed)

        with tempfile.TemporaryDirectory(
            prefix="dec1217-public-readonly-fallocate-", dir="/tmp"
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
                original_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                read_witness_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertEqual(len({normal_fd, original_fd,
                                      read_witness_fd}), 3)
                original_wd = libc.inotify_add_watch(
                    original_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                witness_wd = libc.inotify_add_watch(
                    read_witness_fd, module._checked_watch_path_bytes(sample),
                    IN_OPEN | IN_CLOSE_NOWRITE | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(original_wd, 0)
                self.assertGreater(witness_wd, 0)
                for fd in (original_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # An ordinary O_RDONLY descriptor without O_TRUNC does
                # not mutate bytes at open, unlike DEC-1206 O_RDONLY|O_TRUNC.
                reader_fd = os.open(sample, os.O_RDONLY | os.O_CLOEXEC)
                self.assertEqual(
                    events(module._read_receipt_pending(read_witness_fd)),
                    [(witness_wd, IN_OPEN, b"")],
                )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Genuine libc fallocate on an ordinary O_RDONLY
                # descriptor rejects normal allocation, KEEP_SIZE,
                # PUNCH_HOLE|KEEP_SIZE, and ZERO_RANGE|KEEP_SIZE.
                # These failures are not interchangeable with O_RDONLY
                # plus O_TRUNC, which can mutate during os.open itself.
                libc.fallocate.argtypes = [
                    ctypes.c_int, ctypes.c_int,
                    ctypes.c_longlong, ctypes.c_longlong
                ]
                libc.fallocate.restype = ctypes.c_int
                for mode, offset, length in (
                    (0, 0, len(before)),
                    (0x01, 8192, 4096),
                    (0x03, 0, 4096),
                    (0x11, 0, 4096),
                ):
                    ctypes.set_errno(0)
                    self.assertEqual(
                        libc.fallocate(reader_fd, mode, offset, length), -1
                    )
                    self.assertEqual(ctypes.get_errno(), errno.EBADF)
                    self.assertEqual(os.fstat(reader_fd).st_size, len(before))
                    for fd in (original_fd, read_witness_fd, normal_fd):
                        self.assertEqual(module._read_receipt_pending(fd), b"")

                os.close(reader_fd)
                reader_fd = None
                self.assertEqual(
                    events(module._read_receipt_pending(read_witness_fd)),
                    [(witness_wd, IN_CLOSE_NOWRITE, b"")],
                )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Stop observing read opens before verifying fixture bytes.
                os.close(read_witness_fd)
                read_witness_fd = None
                self.assertEqual(sample.read_bytes(), before)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                def require_writable_receipt(old_bytes, new_bytes):
                    receipt = module._read_receipt_pending(normal_fd)
                    received = events(receipt)
                    expected = {
                        (source_wd, module.IN_MODIFY, b""),
                        (parent_wd, module.IN_MODIFY, b"sample"),
                        (source_wd, module.IN_CLOSE_WRITE, b""),
                        (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                    }
                    self.assertTrue(received)
                    self.assertTrue(all(row in expected for row in received))
                    self.assertTrue(expected.issubset(set(received)))
                    verdict = module._evaluate(
                        old_bytes, new_bytes, receipt,
                        source_wd, True, False,
                        directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)

                # First genuine writable pwrite consumes unsafe ONESHOT;
                # unchanged continuing source + parent watches see it.
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(os.pwrite(writer_fd, changed, 0),
                                 len(changed))
                os.fsync(writer_fd)
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(
                    events(module._read_receipt_pending(original_fd)),
                    [(original_wd, module.IN_MODIFY, b""),
                     (original_wd, module.IN_IGNORED, b"")],
                )
                require_writable_receipt(before, changed)
                self.assertEqual(sample.read_bytes(), changed)

                # A second independent real write restores generated data;
                # original ONESHOT stays silent throughout.
                writer_fd = os.open(
                    sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC
                )
                self.assertEqual(os.write(writer_fd, before), len(before))
                os.fsync(writer_fd)
                os.close(writer_fd)
                writer_fd = None
                require_writable_receipt(changed, before)
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
                for fd in (reader_fd, writer_fd, original_fd,
                           read_witness_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
