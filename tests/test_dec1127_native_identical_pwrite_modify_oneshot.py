from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1127", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000
SAME_SIZE_CHANGE = b"DEC677_PUBLIC_CHOICE\n"


@unittest.skipUnless(sys.platform == "linux", "requires real Linux inotify")
class NativeIdenticalPwriteModifyOneShotRegression(unittest.TestCase):
    def test_identical_byte_pwrite_consumes_source_oneshot_before_actual_byte_change(self):
        original_fd = None
        continuing_fd = None
        writer_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            found = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - offset)
                name = data[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                found.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return found

        def check_stage(receipt, source_wd, parent_wd, action):
            native = records(receipt)
            permitted = ((source_wd, action, b""),
                         (parent_wd, action, b"sample"))
            self.assertTrue(native)
            self.assertTrue(all(event in permitted for event in native))
            self.assertGreaterEqual(native.count(permitted[0]), 1)
            self.assertGreaterEqual(native.count(permitted[1]), 1)
            return native

        def evaluate_write(receipt, source_wd, parent_wd, after):
            parsed = module._classify_stream(receipt, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, receipt, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1127-public-identical-pwrite-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            self.assertEqual(len(SAME_SIZE_CHANGE), len(module.BEFORE))
            self.assertNotEqual(SAME_SIZE_CHANGE, module.BEFORE)
            original_stats = (os.lstat(sample), os.lstat(parent))
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
                original_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(original_fd, 2)
                self.assertNotEqual(original_fd, continuing_fd)
                original_wd = libc.inotify_add_watch(
                    original_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(original_wd, 0)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                # Writable open without truncation does not alter file bytes.
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")

                # Write the EXACT current bytes back in place. The syscall
                # succeeds, but neither the size nor any byte value changes.
                self.assertEqual(os.pwrite(writer_fd, module.BEFORE, 0),
                                 len(module.BEFORE))
                os.fsync(writer_fd)
                self.assertEqual(os.fstat(writer_fd).st_size,
                                 len(module.BEFORE))
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    records(module._read_receipt_pending(original_fd)),
                    [(original_wd, module.IN_MODIFY, b""),
                     (original_wd, module.IN_IGNORED, b"")],
                )
                identical_stage = module._read_receipt_pending(continuing_fd)
                check_stage(identical_stage, source_wd, parent_wd,
                            module.IN_MODIFY)
                evaluate_write(identical_stage, source_wd, parent_wd,
                               module.BEFORE)

                # Descriptor closes only AFTER original one-shot disarms:
                # the original misses even this same pwrite's CLOSE_WRITE.
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertCountEqual(
                    records(module._read_receipt_pending(continuing_fd)),
                    [(source_wd, module.IN_CLOSE_WRITE, b""),
                     (parent_wd, module.IN_CLOSE_WRITE, b"sample")],
                )

                # Later genuine changed-byte write and restoration to the
                # same source inode reach only the continuing full observer.
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")
                self.assertEqual(os.pwrite(writer_fd, SAME_SIZE_CHANGE, 0),
                                 len(SAME_SIZE_CHANGE))
                os.fsync(writer_fd)
                changed = module._read_receipt_pending(continuing_fd)
                check_stage(changed, source_wd, parent_wd, module.IN_MODIFY)
                evaluate_write(changed, source_wd, parent_wd, SAME_SIZE_CHANGE)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                os.close(writer_fd)
                writer_fd = None
                self.assertCountEqual(
                    records(module._read_receipt_pending(continuing_fd)),
                    [(source_wd, module.IN_CLOSE_WRITE, b""),
                     (parent_wd, module.IN_CLOSE_WRITE, b"sample")],
                )
                self.assertEqual(sample.read_bytes(), SAME_SIZE_CHANGE)

                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")
                self.assertEqual(os.pwrite(writer_fd, module.BEFORE, 0),
                                 len(module.BEFORE))
                os.fsync(writer_fd)
                restored = module._read_receipt_pending(continuing_fd)
                check_stage(restored, source_wd, parent_wd, module.IN_MODIFY)
                evaluate_write(restored, source_wd, parent_wd, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                os.close(writer_fd)
                writer_fd = None
                self.assertCountEqual(
                    records(module._read_receipt_pending(continuing_fd)),
                    [(source_wd, module.IN_CLOSE_WRITE, b""),
                     (parent_wd, module.IN_CLOSE_WRITE, b"sample")],
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)

                final = (os.lstat(sample), os.lstat(parent))
                for old, new in zip(original_stats, final):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(continuing_fd),
                                 b"")
            finally:
                if writer_fd is not None:
                    os.close(writer_fd)
                for fd in (original_fd, continuing_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
