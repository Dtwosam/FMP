from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1167", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "copy_file_range"),
                     "requires native Linux inotify and copy_file_range")
class NativeCopyFileRangeZeroPositiveTransferRegression(unittest.TestCase):
    def test_zero_transfer_quiet_then_kernel_copy_emits_source_modify(self):
        one_fd = None
        normal_fd = None
        donor_fd = None
        writer_fd = None

        def events(receipt):
            self.assertIs(type(receipt), bytes)
            found = []
            i = 0
            while i < len(receipt):
                self.assertGreaterEqual(len(receipt) - i, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(receipt, i)
                i += module.EVENT.size
                self.assertLessEqual(nbytes, len(receipt) - i)
                name = receipt[i:i + nbytes].split(b"\x00", 1)[0]
                i += nbytes
                self.assertEqual(cookie, 0)
                found.append((wd, mask, name))
            self.assertEqual(i, len(receipt))
            return found

        def require_stage(receipt, source_wd, parent_wd, mask):
            actual = events(receipt)
            allowed = {
                (source_wd, mask, b""),
                (parent_wd, mask, b"sample"),
            }
            self.assertTrue(actual)
            self.assertTrue(all(e in allowed for e in actual))
            for must in allowed:
                self.assertIn(must, actual)

        at = module.BEFORE.index(b"SOURCE")
        changed = (module.BEFORE[:at] + b"X" + module.BEFORE[at + 1:])
        self.assertEqual(len(changed), len(module.BEFORE))
        self.assertNotEqual(changed, module.BEFORE)

        with tempfile.TemporaryDirectory(
            dir="/tmp", prefix="dec1167-public-kernel-copy-range-"
        ) as tmp:
            root = Path(tmp)
            parent = root / "parent"
            outside = root / "outside"
            parent.mkdir()
            outside.mkdir()
            sample = parent / "sample"
            donor = outside / "donor"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            self.assertEqual(donor.write_bytes(changed), len(changed))
            first = (os.lstat(sample), os.lstat(donor),
                     os.lstat(parent), os.lstat(outside))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            self.assertEqual(module._bounded_inventory_names(outside),
                             ("donor",))
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
                self.assertGreater(one_fd, 2)
                self.assertNotEqual(one_fd, normal_fd)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Donor resides OUTSIDE original watched parent and on
                # same disposable /tmp filesystem. Both file descriptors
                # open before any positive-length data transfer.
                donor_fd = os.open(donor, os.O_RDONLY | os.O_CLOEXEC)
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Real zero-byte copy_file_range returns zero. Unlike an
                # actual data transfer it emits no native source MODIFY
                # and does not disarm the original MODIFY one-shot.
                self.assertEqual(os.copy_file_range(
                    donor_fd, writer_fd, 0, 0, 0
                ), 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Genuine kernel file-to-file data transfer writes changed
                # bytes into watched sample without os.write/pwrite, but
                # still creates native MODIFY on both normal watches.
                self.assertEqual(os.copy_file_range(
                    donor_fd, writer_fd, len(changed), 0, 0
                ), len(changed))
                self.assertEqual(
                    events(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_MODIFY, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                modify = module._read_receipt_pending(normal_fd)
                require_stage(modify, source_wd, parent_wd,
                              module.IN_MODIFY)
                evaluated = module._evaluate(
                    module.BEFORE, changed, modify, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(evaluated["status"], "BLOCKED")
                self.assertIs(evaluated["can_authorize_dispatch"], False)
                self.assertIs(evaluated["independent_os_proof_verified"], False)

                os.fsync(writer_fd)
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                os.close(donor_fd)
                donor_fd = None
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                require_stage(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.IN_CLOSE_WRITE
                )
                self.assertEqual(sample.read_bytes(), changed)
                self.assertEqual(donor.read_bytes(), changed)

                # A separate real source write restores original PUBLIC
                # bytes. The original test-only ONESHOT stays removed;
                # normal source+parent continue to receive write events.
                writer_fd = os.open(
                    sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC
                )
                self.assertEqual(os.write(writer_fd, module.BEFORE),
                                 len(module.BEFORE))
                os.fsync(writer_fd)
                os.close(writer_fd)
                writer_fd = None
                # Preserve the ACTUAL native write receipt bytes for
                # both native event identity assertions and the unchanged
                # evaluator. An empty synthesized stream would also yield
                # BLOCKED, but would not prove the witnessed real write.
                restore_receipt = module._read_receipt_pending(normal_fd)
                restore = events(restore_receipt)
                allowed = {
                    (source_wd, module.IN_MODIFY, b""),
                    (parent_wd, module.IN_MODIFY, b"sample"),
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                }
                self.assertTrue(all(e in allowed for e in restore))
                for row in allowed:
                    self.assertIn(row, restore)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                result = module._evaluate(
                    changed, module.BEFORE,
                    restore_receipt, source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIs(result["can_authorize_dispatch"], False)
                self.assertIs(result["independent_os_proof_verified"], False)

                final = (os.lstat(sample), os.lstat(donor),
                         os.lstat(parent), os.lstat(outside))
                for before, after in zip(first, final):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(donor.read_bytes(), changed)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("donor",))
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
            finally:
                for fd in (donor_fd, writer_fd, one_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
