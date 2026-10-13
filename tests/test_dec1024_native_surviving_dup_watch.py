from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1024", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native inotify alias lifetime is Linux-only")
class NativeClosedOriginalSurvivingDuplicateRegression(unittest.TestCase):
    def test_surviving_dup_retains_watches_after_original_fd_is_closed(self):
        original_fd = None
        surviving_fd = None
        independent_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            i = 0
            result = []
            while i < len(stream):
                self.assertGreaterEqual(len(stream) - i, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(stream, i)
                i += module.EVENT.size
                self.assertLessEqual(length, len(stream) - i)
                name = stream[i:i + length].split(b"\x00", 1)[0]
                i += length
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(i, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1024-public-surviving-dup-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            parent_before = os.lstat(sample.parent)
            self.assertEqual(
                module._bounded_inventory_names(sample.parent), ("sample",)
            )
            try:
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                surviving_fd = os.dup(original_fd)
                independent_fd, independent_source, independent_parent = (
                    module._start_watch(sample)
                )
                self.assertEqual(
                    len({original_fd, surviving_fd, independent_fd}), 3
                )
                for fd in (original_fd, surviving_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Closing the ORIGINAL FD cannot destroy an inotify
                # INSTANCE still held by a dup alias. The duplicate
                # retains BOTH original native source/parent watches.
                original_number = original_fd
                os.close(original_fd)
                original_fd = None
                with self.assertRaises(OSError):
                    os.fstat(original_number)
                os.fstat(surviving_fd)
                self.assertEqual(module._read_receipt_pending(surviving_fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                via_duplicate = module._read_receipt_pending(surviving_fd)
                native = records(via_duplicate)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in native
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in native
                ))
                classified = module._classify_stream(
                    via_duplicate, source_wd, parent_wd
                )
                self.assertTrue(classified["well_formed"])
                self.assertFalse(classified["invalidated"])
                self.assertGreaterEqual(classified["source_modify_events"], 1)
                self.assertGreaterEqual(
                    classified["source_content_write_events"], 1
                )
                self.assertEqual(module._read_receipt_pending(surviving_fd), b"")

                independently_seen = module._read_receipt_pending(independent_fd)
                other = module._classify_stream(
                    independently_seen, independent_source, independent_parent
                )
                self.assertTrue(other["well_formed"])
                self.assertFalse(other["invalidated"])
                self.assertGreaterEqual(other["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")
                for stream, source, directory in (
                    (via_duplicate, source_wd, parent_wd),
                    (independently_seen, independent_source, independent_parent),
                ):
                    verdict = module._evaluate(
                        module.BEFORE, module.AFTER, stream, source,
                        True, False, directory_watch=directory,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )

                # Manual watch removal through the surviving dup changes
                # that same original kernel instance, not the truly
                # independent second inotify instance.
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
                libc.inotify_rm_watch.restype = ctypes.c_int
                self.assertEqual(
                    libc.inotify_rm_watch(surviving_fd, source_wd), 0
                )
                ignored = module._read_receipt_pending(surviving_fd)
                self.assertEqual(records(ignored), [
                    (source_wd, module.IN_IGNORED, b"")
                ])
                self.assertTrue(module._classify_stream(
                    ignored, source_wd, parent_wd
                )["invalidated"])
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")
                self.assertEqual(module._read_receipt_pending(surviving_fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE), len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                parent_only = module._read_receipt_pending(surviving_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in records(parent_only)
                ))
                self.assertFalse(any(
                    wd == source_wd for wd, mask, name in records(parent_only)
                ))
                second_restored = module._read_receipt_pending(independent_fd)
                evidence = module._classify_stream(
                    second_restored, independent_source, independent_parent
                )
                self.assertTrue(evidence["well_formed"])
                self.assertFalse(evidence["invalidated"])
                self.assertGreaterEqual(evidence["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(surviving_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                for stream, wd, dir_wd in (
                    (ignored, source_wd, parent_wd),
                    (parent_only, source_wd, parent_wd),
                    (second_restored, independent_source, independent_parent),
                ):
                    result = module._evaluate(
                        module.BEFORE, module.BEFORE, stream, wd,
                        True, False, directory_watch=dir_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertIs(result["can_authorize_dispatch"], False)
                    self.assertIs(
                        result["independent_os_proof_verified"], False
                    )

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                after = os.lstat(sample)
                last_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (after.st_dev, after.st_ino, after.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (last_parent.st_dev, last_parent.st_ino,
                     last_parent.st_mode),
                    (parent_before.st_dev, parent_before.st_ino,
                     parent_before.st_mode),
                )
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent), ("sample",)
                )
            finally:
                for fd in (independent_fd, surviving_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
