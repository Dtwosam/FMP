from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1017", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "Linux native watch lifetime only")
class NativeParentWatchReregistrationGapRegression(unittest.TestCase):
    def test_parent_rewatch_cannot_recover_transient_sibling_events_during_gap(self):
        primary_fd = None
        witness_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            offset = 0
            results = []
            while offset < len(stream):
                self.assertGreaterEqual(len(stream) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(stream, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(stream) - offset)
                name = stream[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                results.append((wd, mask, name))
            self.assertEqual(offset, len(stream))
            return results

        with tempfile.TemporaryDirectory(
            prefix="dec1017-public-parent-watch-gap-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            parent_first = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent), ("sample",))
            try:
                primary_fd, source_wd, original_parent_wd = module._start_watch(sample)
                witness_fd, witness_source_wd, witness_parent_wd = module._start_watch(sample)
                self.assertNotEqual(primary_fd, witness_fd)
                self.assertNotEqual(source_wd, original_parent_wd)
                self.assertNotEqual(witness_source_wd, witness_parent_wd)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                lib = ctypes.CDLL(None, use_errno=True)
                lib.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
                lib.inotify_rm_watch.restype = ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = ctypes.c_int

                self.assertEqual(lib.inotify_rm_watch(primary_fd, original_parent_wd), 0)
                ignored = module._read_receipt_pending(primary_fd)
                self.assertEqual(
                    records(ignored), [(original_parent_wd, module.IN_IGNORED, b"")]
                )
                self.assertTrue(module._classify_stream(
                    ignored, source_wd, original_parent_wd
                )["invalidated"])
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # A real sibling enters and leaves while the primary
                # parent watch is absent. Only an independent instance
                # can prove that the missing interval had real activity.
                transient = sample.parent / "public-parent-gap-sibling"
                self.assertEqual(transient.write_bytes(b"PUBLIC-GAP"),
                                 len(b"PUBLIC-GAP"))
                os.unlink(transient)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                witness_gap = module._read_receipt_pending(witness_fd)
                witness_events = records(witness_gap)
                self.assertIn(
                    (witness_parent_wd, module.IN_CREATE,
                     b"public-parent-gap-sibling"), witness_events
                )
                self.assertIn(
                    (witness_parent_wd, module.IN_DELETE,
                     b"public-parent-gap-sibling"), witness_events
                )
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # Original source WD survives and still sees genuine
                # changed-byte writes, but the removed parent emits none.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                gap_source = module._read_receipt_pending(primary_fd)
                gap_events = records(gap_source)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in gap_events
                ))
                self.assertFalse(any(
                    wd == original_parent_wd for wd, mask, name in gap_events
                ))
                second_source = module._read_receipt_pending(witness_fd)
                self.assertTrue(any(
                    wd == witness_source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in records(second_source)
                ))
                self.assertTrue(any(
                    wd == witness_parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in records(second_source)
                ))
                for stream, wd, directory_wd in (
                    (ignored, source_wd, original_parent_wd),
                    (gap_source, source_wd, original_parent_wd),
                    (second_source, witness_source_wd, witness_parent_wd),
                ):
                    result = module._evaluate(
                        module.BEFORE, module.AFTER, stream, wd,
                        True, False, directory_watch=directory_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertIs(result["can_authorize_dispatch"], False)
                    self.assertIs(result["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # Re-registering the same directory inode on the original
                # FD yields a NEW WD and no retroactive sibling receipts.
                replacement_parent_wd = lib.inotify_add_watch(
                    primary_fd, module._checked_watch_path_bytes(sample.parent),
                    module.DIRECTORY_MASK | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW,
                )
                self.assertGreater(replacement_parent_wd, 0)
                self.assertNotIn(replacement_parent_wd, (source_wd, original_parent_wd))
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(os.lstat(sample.parent).st_ino,
                                 parent_first.st_ino)

                later_sibling = sample.parent / "public-parent-restored-sibling"
                self.assertEqual(later_sibling.write_bytes(b"PUBLIC-LATER"),
                                 len(b"PUBLIC-LATER"))
                os.unlink(later_sibling)
                late_primary = module._read_receipt_pending(primary_fd)
                late_records = records(late_primary)
                for expected_mask in (module.IN_CREATE, module.IN_DELETE):
                    self.assertIn(
                        (replacement_parent_wd, expected_mask,
                         b"public-parent-restored-sibling"), late_records
                    )
                self.assertFalse(any(
                    wd == original_parent_wd for wd, mask, name in late_records
                ))
                self.assertFalse(module._classify_stream(
                    late_primary, source_wd, original_parent_wd
                )["well_formed"])
                self.assertTrue(module._classify_stream(
                    late_primary, source_wd, replacement_parent_wd
                )["well_formed"])
                other_late = records(module._read_receipt_pending(witness_fd))
                self.assertIn(
                    (witness_parent_wd, module.IN_CREATE,
                     b"public-parent-restored-sibling"), other_late
                )
                self.assertIn(
                    (witness_parent_wd, module.IN_DELETE,
                     b"public-parent-restored-sibling"), other_late
                )
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # A later real restore is visible on source and NEW
                # parent, but cannot erase the earlier unseen sibling.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE), len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                restored = module._read_receipt_pending(primary_fd)
                event_records = records(restored)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in event_records
                ))
                self.assertTrue(any(
                    wd == replacement_parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in event_records
                ))
                self.assertFalse(any(
                    wd == original_parent_wd for wd, mask, name in event_records
                ))
                for source, dir_wd, data in (
                    (source_wd, replacement_parent_wd, restored),
                    (witness_source_wd, witness_parent_wd,
                     module._read_receipt_pending(witness_fd)),
                ):
                    parsed = module._classify_stream(data, source, dir_wd)
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    verdict = module._evaluate(
                        module.BEFORE, module.BEFORE, data, source, True,
                        False, directory_watch=dir_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino, parent_final.st_mode),
                    (parent_first.st_dev, parent_first.st_ino, parent_first.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for current_fd in (witness_fd, primary_fd):
                    if current_fd is not None:
                        os.close(current_fd)
                        with self.assertRaises(OSError):
                            os.fstat(current_fd)
