from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1020", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native WD identity requires Linux")
class NativeInstanceScopedWatchDescriptorRegression(unittest.TestCase):
    def test_same_numeric_watch_descriptor_can_remove_only_owning_instance_watch(self):
        first_fd = None
        second_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            parsed = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - offset)
                name = data[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return parsed

        with tempfile.TemporaryDirectory(
            prefix="dec1020-public-instance-scoped-wd-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                first_fd, first_source_wd, first_parent_wd = (
                    module._start_watch(sample)
                )
                second_fd, second_source_wd, second_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertNotEqual(first_fd, second_fd)
                self.assertEqual(first_source_wd, second_source_wd)
                self.assertEqual(first_parent_wd, second_parent_wd)
                self.assertNotEqual(first_source_wd, first_parent_wd)
                self.assertEqual(module._read_receipt_pending(first_fd), b"")
                self.assertEqual(module._read_receipt_pending(second_fd), b"")

                lib = ctypes.CDLL(None, use_errno=True)
                lib.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
                lib.inotify_rm_watch.restype = ctypes.c_int

                # Numeric WD from instance #1 happens to have the same
                # value as instance #2's WD. Passing that integer with
                # fd #2 removes ONLY fd #2's source subscription.
                self.assertEqual(
                    lib.inotify_rm_watch(second_fd, first_source_wd), 0
                )
                self.assertEqual(module._read_receipt_pending(first_fd), b"")
                removed = module._read_receipt_pending(second_fd)
                self.assertEqual(records(removed), [
                    (second_source_wd, module.IN_IGNORED, b"")
                ])
                self.assertEqual(module._read_receipt_pending(second_fd), b"")

                # Genuine writes are still seen fully by instance #1,
                # whereas instance #2 sees only parent named events.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    intact_stream = module._read_receipt_pending(first_fd)
                    intact = module._classify_stream(
                        intact_stream, first_source_wd, first_parent_wd
                    )
                    self.assertTrue(intact["well_formed"])
                    self.assertFalse(intact["invalidated"])
                    self.assertGreaterEqual(intact["source_modify_events"], 1)
                    self.assertGreaterEqual(
                        intact["source_content_write_events"], 1
                    )
                    self.assertTrue(any(
                        wd == first_source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in records(intact_stream)
                    ))
                    self.assertTrue(any(
                        wd == first_parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in records(intact_stream)
                    ))

                    partial_stream = module._read_receipt_pending(second_fd)
                    partial_records = records(partial_stream)
                    self.assertTrue(any(
                        wd == second_parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in partial_records
                    ))
                    self.assertFalse(any(
                        wd == second_source_wd for wd, mask, name in partial_records
                    ))
                    self.assertEqual(module._classify_stream(
                        partial_stream, second_source_wd, second_parent_wd
                    )["source_modify_events"], 0)

                    for stream, src, par in (
                        (intact_stream, first_source_wd, first_parent_wd),
                        (partial_stream, second_source_wd, second_parent_wd),
                    ):
                        verdict = module._evaluate(
                            module.BEFORE, content, stream, src,
                            True, False, directory_watch=par,
                            directory_inventory_names=("sample",),
                        )
                        self.assertEqual(verdict["status"], "BLOCKED")
                        self.assertIs(verdict["can_authorize_dispatch"], False)
                        self.assertIs(
                            verdict["independent_os_proof_verified"], False
                        )
                    self.assertEqual(module._read_receipt_pending(first_fd), b"")
                    self.assertEqual(module._read_receipt_pending(second_fd), b"")

                # The two underlying registrations are independent even
                # when their numeric WD values happen to be identical.
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent),
                    ("sample",),
                )
                after = os.lstat(sample)
                parent_after = os.lstat(sample.parent)
                self.assertEqual(
                    (after.st_dev, after.st_ino, after.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_after.st_dev, parent_after.st_ino,
                     parent_after.st_mode),
                    (initial_parent.st_dev, initial_parent.st_ino,
                     initial_parent.st_mode),
                )
            finally:
                for current_fd in (second_fd, first_fd):
                    if current_fd is not None:
                        os.close(current_fd)
                        with self.assertRaises(OSError):
                            os.fstat(current_fd)
