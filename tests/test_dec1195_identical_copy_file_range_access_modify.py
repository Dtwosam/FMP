from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1195", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_ACCESS = 0x00000001
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "copy_file_range"),
                     "requires native Linux inotify and copy_file_range")
class NativeIdenticalCopyFileRangeRegression(unittest.TestCase):
    def test_identical_kernel_copy_reads_donor_and_emits_dest_modify_without_delta(self):
        one_fd = None
        read_witness_fd = None
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
            dir="/tmp", prefix="dec1195-public-identical-copy-range-"
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
            self.assertEqual(donor.write_bytes(module.BEFORE), len(module.BEFORE))
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
                read_witness_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertEqual(len({one_fd, read_witness_fd, normal_fd}),
                                 3)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(donor),
                    IN_ACCESS | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                witness_wd = libc.inotify_add_watch(
                    read_witness_fd, module._checked_watch_path_bytes(donor),
                    IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE |
                    module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertGreater(witness_wd, 0)
                for native_fd in (one_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(native_fd),
                                     b"")

                # Donor resides OUTSIDE original watched parent and on
                # same disposable /tmp filesystem. Both file descriptors
                # open before any positive-length data transfer.
                donor_fd = os.open(donor, os.O_RDONLY | os.O_CLOEXEC)
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(
                    events(module._read_receipt_pending(read_witness_fd)),
                    [(witness_wd, IN_OPEN, b"")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # ZERO kernel transfer: original DONOR ACCESS one-shot,
                # donor read witness, and normal destination source and
                # parent mutation watcher are each quiet.
                self.assertEqual(
                    os.copy_file_range(donor_fd, writer_fd, 0, 0, 0), 0
                )
                for native_fd in (one_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(native_fd),
                                     b"")

                # Real positive-length kernel file-to-file transfer
                # simultaneously emits DONOR source ACCESS and watched
                # destination source+parent MODIFY. Their INOTIFY
                # witness identities and masks must NOT be conflated.
                self.assertEqual(os.copy_file_range(
                    donor_fd, writer_fd, len(changed), 0, 0
                ), len(changed))
                self.assertEqual(
                    events(module._read_receipt_pending(one_fd)),
                    [(one_wd, IN_ACCESS, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(
                    events(module._read_receipt_pending(read_witness_fd)),
                    [(witness_wd, IN_ACCESS, b"")],
                )
                modify = module._read_receipt_pending(normal_fd)
                require_stage(modify, source_wd, parent_wd,
                              module.IN_MODIFY)
                evaluated = module._evaluate(
                    module.BEFORE, module.BEFORE, modify, source_wd,
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
                self.assertEqual(
                    events(module._read_receipt_pending(read_witness_fd)),
                    [(witness_wd, IN_CLOSE_NOWRITE, b"")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                # End the positive donor READ watch before later
                # donor.read_bytes(), which itself emits real ACCESS.
                os.close(read_witness_fd)
                with self.assertRaises(OSError):
                    os.fstat(read_witness_fd)
                read_witness_fd = None
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                require_stage(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.IN_CLOSE_WRITE
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(donor.read_bytes(), module.BEFORE)

                # Genuine identical file-to-file copying generated
                # destination MODIFY with no actual destination delta.
                # Now independently write DIFFERENT bytes and restore
                # original bytes, so unchanged continuing mutation
                # observer remains positively proven on real changes.
                for previous, resulting in (
                    (module.BEFORE, changed),
                    (changed, module.BEFORE),
                ):
                    writer_fd = os.open(
                        sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC
                    )
                    self.assertEqual(os.write(writer_fd, resulting),
                                     len(resulting))
                    os.fsync(writer_fd)
                    os.close(writer_fd)
                    writer_fd = None
                    write_receipt = module._read_receipt_pending(normal_fd)
                    observed = events(write_receipt)
                    allowed = {
                        (source_wd, module.IN_MODIFY, b""),
                        (parent_wd, module.IN_MODIFY, b"sample"),
                        (source_wd, module.IN_CLOSE_WRITE, b""),
                        (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                    }
                    self.assertTrue(observed)
                    self.assertTrue(all(x in allowed for x in observed))
                    for needed in allowed:
                        self.assertIn(needed, observed)
                    self.assertEqual(
                        module._read_receipt_pending(one_fd), b""
                    )
                    outcome = module._evaluate(
                        previous, resulting, write_receipt, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(outcome["status"], "BLOCKED")
                    self.assertIs(
                        outcome["can_authorize_dispatch"], False
                    )
                    self.assertIs(
                        outcome["independent_os_proof_verified"], False
                    )
                    self.assertEqual(sample.read_bytes(), resulting)

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
                self.assertEqual(donor.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(outside),
                                 ("donor",))
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
            finally:
                for fd in (donor_fd, writer_fd, read_witness_fd, one_fd,
                           normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
