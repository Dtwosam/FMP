from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1209", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeFtruncateNoopAndLengthRegression(unittest.TestCase):
    def test_ftruncate_same_size_shrink_and_reextend_all_emit_modify(self):
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
        short = before[:5]
        extended = short + b"\x00" * (len(before) - len(short))
        self.assertNotEqual(extended, before)
        self.assertEqual(len(extended), len(before))

        with tempfile.TemporaryDirectory(
            prefix="dec1209-public-native-ftruncate-", dir="/tmp"
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

                def require_modify(old_bytes, new_bytes):
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

                # A successful non-changing ftruncate still emits genuine
                # source + named-parent MODIFY; no write() is involved.
                os.ftruncate(writer_fd, len(before))
                self.assertEqual(os.fstat(writer_fd).st_size, len(before))
                require_modify(before, before)
                self.assertEqual(
                    events(module._read_receipt_pending(original_fd)),
                    [(original_wd, module.IN_MODIFY, b""),
                     (original_wd, module.IN_IGNORED, b"")],
                )
                self.assertEqual(sample.read_bytes(), before)

                # Shrink destroys the suffix. The already-removed unsafe
                # ONESHOT is blind, but the unchanged helper remains live.
                os.ftruncate(writer_fd, len(short))
                self.assertEqual(os.fstat(writer_fd).st_size, len(short))
                require_modify(before, short)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(sample.read_bytes(), short)

                # Extending length does not restore deleted data: the
                # newly exposed suffix reads as zero-filled bytes.
                os.ftruncate(writer_fd, len(before))
                self.assertEqual(os.fstat(writer_fd).st_size, len(before))
                require_modify(short, extended)
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

                # Restore the generated PUBLIC fixture with a separate
                # genuine O_TRUNC + write; this remains observable.
                restore_fd = os.open(
                    sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC
                )
                self.assertEqual(os.write(restore_fd, before), len(before))
                os.fsync(restore_fd)
                os.close(restore_fd)
                restore_fd = None
                restored_receipt = module._read_receipt_pending(normal_fd)
                restored_events = events(restored_receipt)
                expected = {
                    (source_wd, module.IN_MODIFY, b""),
                    (parent_wd, module.IN_MODIFY, b"sample"),
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                }
                self.assertTrue(restored_events)
                self.assertTrue(all(row in expected for row in restored_events))
                self.assertTrue(expected.issubset(set(restored_events)))
                result = module._evaluate(
                    extended, before, restored_receipt, source_wd,
                    True, False, directory_watch=parent_wd,
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
                for fd in (writer_fd, restore_fd, original_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
