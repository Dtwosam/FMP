from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1034", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native inotify requires Linux")
class NativeQueuedSiblingBeforeParentRemovalRegression(unittest.TestCase):
    def test_pending_sibling_lifecycle_survives_parent_watch_removal(self):
        primary_fd = None
        alias_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            offset = 0
            parsed = []
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(length, len(data) - offset)
                name = data[offset:offset + length].split(b"\x00", 1)[0]
                offset += length
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return parsed

        with tempfile.TemporaryDirectory(
            prefix="dec1034-public-pending-sibling-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent), ("sample",))
            try:
                primary_fd, source_wd, parent_wd = module._start_watch(sample)
                alias_fd = os.dup(primary_fd)
                independent_fd, other_source_wd, other_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(len({primary_fd, alias_fd, independent_fd}), 3)
                for fd in (primary_fd, alias_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Queue actual CREATE and DELETE while both parent WDs
                # still exist. Do not read the first queue before removal.
                sibling = sample.parent / "public-prequeued-sibling"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-SIBLING"),
                                 len(b"PUBLIC-SIBLING"))
                os.unlink(sibling)
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
                libc.inotify_rm_watch.restype = ctypes.c_int
                self.assertEqual(libc.inotify_rm_watch(alias_fd, parent_wd), 0)

                # Complete native queue must preserve prior real sibling
                # events followed by parent WD IN_IGNORED.
                queued = module._read_receipt_pending(primary_fd)
                native = records(queued)
                created = [
                    index for index, (wd, mask, name) in enumerate(native)
                    if wd == parent_wd and mask == module.IN_CREATE
                    and name == b"public-prequeued-sibling"
                ]
                deleted = [
                    index for index, (wd, mask, name) in enumerate(native)
                    if wd == parent_wd and mask == module.IN_DELETE
                    and name == b"public-prequeued-sibling"
                ]
                ignored = [
                    index for index, (wd, mask, name) in enumerate(native)
                    if wd == parent_wd and mask == module.IN_IGNORED
                    and name == b""
                ]
                self.assertEqual(len(created), 1)
                self.assertEqual(len(deleted), 1)
                self.assertEqual(len(ignored), 1)
                self.assertLess(created[0], deleted[0])
                self.assertLess(deleted[0], ignored[0])
                self.assertFalse(any(wd == source_wd for wd, _, _ in native))
                parsed = module._classify_stream(queued, source_wd, parent_wd)
                self.assertTrue(parsed["invalidated"])
                self.assertGreaterEqual(parsed["directory_changes"], 2)
                result = module._evaluate(
                    module.BEFORE, module.BEFORE, queued,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",)
                )
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIs(result["can_authorize_dispatch"], False)
                self.assertIs(result["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")

                other_queued = module._read_receipt_pending(independent_fd)
                independent = records(other_queued)
                self.assertIn(
                    (other_parent_wd, module.IN_CREATE,
                     b"public-prequeued-sibling"), independent
                )
                self.assertIn(
                    (other_parent_wd, module.IN_DELETE,
                     b"public-prequeued-sibling"), independent
                )
                self.assertFalse(any(
                    mask == module.IN_IGNORED for _, mask, _ in independent
                ))
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # NEW sibling activity after parent removal is silent
                # in first instance but not in the true independent one.
                later = sample.parent / "public-later-sibling"
                self.assertEqual(later.write_bytes(b"PUBLIC-LATER"),
                                 len(b"PUBLIC-LATER"))
                os.unlink(later)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                later_events = records(module._read_receipt_pending(independent_fd))
                for mask in (module.IN_CREATE, module.IN_DELETE):
                    self.assertIn(
                        (other_parent_wd, mask, b"public-later-sibling"),
                        later_events
                    )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Source watch remains bound in the first instance:
                # content writes continue despite parent census loss.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    first_stream = module._read_receipt_pending(alias_fd)
                    first_events = records(first_stream)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in first_events
                    ))
                    self.assertFalse(any(
                        wd == parent_wd for wd, mask, name in first_events
                    ))
                    other_stream = module._read_receipt_pending(independent_fd)
                    other_events = records(other_stream)
                    self.assertTrue(any(
                        wd == other_source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in other_events
                    ))
                    self.assertTrue(any(
                        wd == other_parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in other_events
                    ))
                    for stream, wd, parent in (
                        (first_stream, source_wd, parent_wd),
                        (other_stream, other_source_wd, other_parent_wd),
                    ):
                        verdict = module._evaluate(
                            module.BEFORE, content, stream,
                            wd, True, False, directory_watch=parent,
                            directory_inventory_names=("sample",)
                        )
                        self.assertEqual(verdict["status"], "BLOCKED")
                        self.assertIs(verdict["can_authorize_dispatch"], False)
                        self.assertIs(
                            verdict["independent_os_proof_verified"], False
                        )
                    self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                    self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode)
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino, parent_final.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode)
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (independent_fd, alias_fd, primary_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
