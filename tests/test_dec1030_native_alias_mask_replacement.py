from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1030", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020


@unittest.skipUnless(sys.platform == "linux", "native Linux mask replacement only")
class NativeAliasMaskReplacementGap(unittest.TestCase):
    def test_dup_replace_source_mask_suppresses_writes_without_changing_wd(self):
        original_fd = None
        duplicate_fd = None
        independent_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            found = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(stream) - pos)
                name = stream[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                found.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return found

        with tempfile.TemporaryDirectory(
            prefix="dec1030-public-mask-replace-gap-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent), ("sample",))
            try:
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                duplicate_fd = os.dup(original_fd)
                independent_fd, other_source_wd, other_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(
                    len({original_fd, duplicate_fd, independent_fd}), 3
                )
                for fd in (original_fd, duplicate_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = ctypes.c_int
                source_path = module._checked_watch_path_bytes(sample)

                # WITHOUT IN_MASK_ADD, this replaces the existing watch
                # mask rather than adding events to it. Source WD number
                # stays identical but source IN_MODIFY/CLOSE_WRITE vanish.
                ctypes.set_errno(0)
                replaced_wd = lib.inotify_add_watch(
                    duplicate_fd, source_path,
                    IN_OPEN | module.IN_DONT_FOLLOW,
                )
                self.assertEqual(replaced_wd, source_wd)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(duplicate_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                degraded = module._read_receipt_pending(original_fd)
                degraded_records = records(degraded)
                self.assertIn((source_wd, IN_OPEN, b""), degraded_records)
                self.assertFalse(any(
                    wd == source_wd and mask &
                    (module.IN_MODIFY | module.IN_CLOSE_WRITE)
                    for wd, mask, name in degraded_records
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in degraded_records
                ))
                self.assertFalse(module._classify_stream(
                    degraded, source_wd, parent_wd
                )["well_formed"])
                degraded_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, degraded, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(degraded_verdict["status"], "BLOCKED")
                self.assertIs(degraded_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    degraded_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(duplicate_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                independent = module._read_receipt_pending(independent_fd)
                independent_events = records(independent)
                self.assertTrue(any(
                    wd == other_source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in independent_events
                ))
                self.assertTrue(any(
                    wd == other_parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in independent_events
                ))
                independently_parsed = module._classify_stream(
                    independent, other_source_wd, other_parent_wd
                )
                self.assertTrue(independently_parsed["well_formed"])
                self.assertFalse(independently_parsed["invalidated"])
                self.assertGreaterEqual(independently_parsed["source_modify_events"], 1)
                independent_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, independent,
                    other_source_wd, True, False,
                    directory_watch=other_parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(independent_verdict["status"], "BLOCKED")
                self.assertIs(independent_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    independent_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Replacing the original mask later does NOT replay the
                # earlier source IN_MODIFY records. The same WD is not
                # evidence of continuous original mask or provenance.
                restored_wd = lib.inotify_add_watch(
                    original_fd, source_path,
                    module.MASK | module.IN_DONT_FOLLOW,
                )
                self.assertEqual(restored_wd, source_wd)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE), len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                restoration = module._read_receipt_pending(duplicate_fd)
                restoration_events = records(restoration)
                self.assertFalse(any(
                    mask == IN_OPEN for wd, mask, name in restoration_events
                ))
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in restoration_events
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in restoration_events
                ))
                final_parsed = module._classify_stream(
                    restoration, source_wd, parent_wd
                )
                self.assertTrue(final_parsed["well_formed"])
                self.assertFalse(final_parsed["invalidated"])
                self.assertGreaterEqual(final_parsed["source_modify_events"], 1)
                final_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, restoration,
                    source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(final_verdict["status"], "BLOCKED")
                self.assertIs(final_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    final_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                independent_restore = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    independent_restore, other_source_wd, other_parent_wd
                )["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino, parent_final.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (independent_fd, duplicate_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
