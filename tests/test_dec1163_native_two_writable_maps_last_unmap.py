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
spec = importlib.util.spec_from_file_location("dec677_native_dec1163", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "requires real native Linux inotify")
class NativeTwoWritableMapsLastUnmapRegression(unittest.TestCase):
    def test_two_shared_mmaps_delay_close_write_until_second_final_unmap(self):
        one_fd = None
        normal_fd = None
        writer_fd = None
        first_mapping = None
        second_mapping = None

        def records(receipt):
            self.assertIs(type(receipt), bytes)
            observed = []
            at = 0
            while at < len(receipt):
                self.assertGreaterEqual(len(receipt) - at, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(receipt, at)
                at += module.EVENT.size
                self.assertLessEqual(nbytes, len(receipt) - at)
                name = receipt[at:at + nbytes].split(b"\x00", 1)[0]
                at += nbytes
                self.assertEqual(cookie, 0)
                observed.append((wd, mask, name))
            self.assertEqual(at, len(receipt))
            return observed

        def verify_restoration(raw, source_wd, parent_wd):
            observed = records(raw)
            allowed = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(observed)
            self.assertTrue(all(row in allowed for row in observed))
            for essential in allowed:
                self.assertIn(essential, observed)
            evaluated = module._evaluate(
                changed, module.BEFORE, raw, source_wd,
                True, False, directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(evaluated["status"], "BLOCKED")
            self.assertIs(evaluated["can_authorize_dispatch"], False)
            self.assertIs(evaluated["independent_os_proof_verified"], False)

        first_byte = module.BEFORE.find(b"SOURCE")
        self.assertGreaterEqual(first_byte, 0)
        self.assertNotEqual(module.BEFORE[first_byte:first_byte + 1], b"X")
        changed = (module.BEFORE[:first_byte] + b"X" +
                   module.BEFORE[first_byte + 1:])
        self.assertEqual(len(changed), len(module.BEFORE))

        with tempfile.TemporaryDirectory(
            prefix="dec1163-public-two-mappings-last-unmap-", dir="/tmp"
        ) as temp:
            parent = Path(temp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            initial = (os.lstat(sample), os.lstat(parent))
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
                self.assertGreater(one_fd, 2)
                self.assertNotEqual(one_fd, normal_fd)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample),
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW |
                    IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                writer_fd = os.open(sample, os.O_RDWR | os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Both mappings reference the same writable file
                # description. Closing the userspace FD leaves two live
                # writable mapping references; no native CLOSE_WRITE.
                first_mapping = mmap.mmap(
                    writer_fd, len(module.BEFORE), access=mmap.ACCESS_WRITE
                )
                second_mapping = mmap.mmap(
                    writer_fd, len(module.BEFORE), access=mmap.ACCESS_WRITE
                )
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Unmap just the FIRST one. The second writable mapping
                # still keeps file lifetime alive. Original CLOSE-only
                # one-shot and normal continuing watcher remain quiet.
                first_mapping.close()
                first_mapping = None
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Real byte mutation AFTER descriptor and first mapping
                # close, via remaining MAP_SHARED mapping. Native inotify
                # does not provide MODIFY for this mapped memory store.
                second_mapping[first_byte:first_byte + 1] = b"X"
                self.assertEqual(second_mapping[:], changed)
                second_mapping.flush()
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Only FINAL writable mapping release produces source and
                # named-parent CLOSE_WRITE; original alternative ONESHOT
                # receives CLOSE_WRITE followed by IN_IGNORED.
                second_mapping.close()
                second_mapping = None
                self.assertEqual(
                    records(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_CLOSE_WRITE, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                close_only = module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    records(close_only),
                    [(source_wd, module.IN_CLOSE_WRITE, b""),
                     (parent_wd, module.IN_CLOSE_WRITE, b"sample")],
                )
                self.assertEqual(sample.read_bytes(), changed)
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                result = module._evaluate(
                    module.BEFORE, changed, close_only, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIs(result["can_authorize_dispatch"], False)
                self.assertIs(result["independent_os_proof_verified"], False)

                # A separate real ordinary write restores the PUBLIC
                # source bytes and emits MODIFY and CLOSE_WRITE; the
                # consumed original one-shot can no longer see them.
                writer_fd = os.open(
                    sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC
                )
                self.assertEqual(os.write(writer_fd, module.BEFORE),
                                 len(module.BEFORE))
                os.fsync(writer_fd)
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_restoration(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd,
                )
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = (os.lstat(sample), os.lstat(parent))
                for before, after in zip(initial, final):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                for active_mapping in (first_mapping, second_mapping):
                    if active_mapping is not None:
                        active_mapping.close()
                if writer_fd is not None:
                    os.close(writer_fd)
                for fd in (one_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
