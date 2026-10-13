from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1033", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native pending inotify records need Linux")
class NativeQueuedWriteBeforeWatchRemovalRegression(unittest.TestCase):
    def test_queued_source_write_precedes_ignored_from_duplicate_removal(self):
        primary_fd = None
        alias_fd = None
        independent_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            result = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, size = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(size, len(stream) - pos)
                name = stream[pos:pos + size].split(b"\x00", 1)[0]
                pos += size
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1033-public-queued-watch-loss-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                primary_fd, source_wd, parent_wd = module._start_watch(sample)
                alias_fd = os.dup(primary_fd)
                independent_fd, other_source_wd, other_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(
                    len({primary_fd, alias_fd, independent_fd}), 3
                )
                for fd in (primary_fd, alias_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Queue an ACTUAL changed-byte write and close while all
                # source+parent watches are installed. Do not drain
                # either descriptor of the shared instance yet.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER),
                                     len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                self.assertEqual(sample.read_bytes(), module.AFTER)

                # Removing source through its duplicate appends genuine
                # IN_IGNORED AFTER the already queued source write.
                # Reading the whole original queue must retain BOTH.
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_rm_watch.argtypes = [
                    ctypes.c_int, ctypes.c_int
                ]
                libc.inotify_rm_watch.restype = ctypes.c_int
                self.assertEqual(
                    libc.inotify_rm_watch(alias_fd, source_wd), 0
                )
                combined = module._read_receipt_pending(primary_fd)
                actual = records(combined)
                self.assertTrue(actual)
                modify_indices = [
                    i for i, (wd, mask, name) in enumerate(actual)
                    if wd == source_wd and mask == module.IN_MODIFY
                ]
                close_indices = [
                    i for i, (wd, mask, name) in enumerate(actual)
                    if wd == source_wd and mask == module.IN_CLOSE_WRITE
                ]
                ignored_indices = [
                    i for i, (wd, mask, name) in enumerate(actual)
                    if wd == source_wd and mask == module.IN_IGNORED
                ]
                self.assertEqual(len(ignored_indices), 1)
                self.assertTrue(modify_indices)
                self.assertTrue(close_indices)
                self.assertLess(max(modify_indices), ignored_indices[0])
                self.assertLess(max(close_indices), ignored_indices[0])
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in actual
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_CLOSE_WRITE
                    and name == b"sample"
                    for wd, mask, name in actual
                ))
                parsed = module._classify_stream(
                    combined, source_wd, parent_wd
                )
                self.assertTrue(parsed["invalidated"])
                self.assertGreaterEqual(parsed["source_modify_events"], 1)
                self.assertGreaterEqual(
                    parsed["source_content_write_events"], 1
                )
                verdict = module._evaluate(
                    module.BEFORE, module.AFTER, combined,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",)
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")

                # The independent instance was never removed; its own
                # queue still contains the complete real source write,
                # and none of the other instance's IN_IGNORED.
                separate = module._read_receipt_pending(independent_fd)
                independent_events = records(separate)
                self.assertTrue(any(
                    wd == other_source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in independent_events
                ))
                self.assertFalse(any(
                    mask == module.IN_IGNORED
                    for wd, mask, name in independent_events
                ))
                independent_parse = module._classify_stream(
                    separate, other_source_wd, other_parent_wd
                )
                self.assertTrue(independent_parse["well_formed"])
                self.assertFalse(independent_parse["invalidated"])
                independent_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, separate,
                    other_source_wd, True, False,
                    directory_watch=other_parent_wd,
                    directory_inventory_names=("sample",)
                )
                self.assertEqual(independent_verdict["status"], "BLOCKED")
                self.assertIs(
                    independent_verdict["can_authorize_dispatch"], False
                )
                self.assertIs(
                    independent_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # A later real byte restoration reaches ONLY the parent
                # in the primary instance; the removed source WD cannot
                # become active merely because old writes were queued.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                primary_restore = module._read_receipt_pending(alias_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in records(primary_restore)
                ))
                self.assertFalse(any(
                    wd == source_wd for wd, mask, name
                    in records(primary_restore)
                ))
                untouched_restore = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    untouched_restore, other_source_wd, other_parent_wd
                )["source_modify_events"], 1)
                for stream, swd, pwd in (
                    (primary_restore, source_wd, parent_wd),
                    (untouched_restore, other_source_wd, other_parent_wd),
                ):
                    followup = module._evaluate(
                        module.BEFORE, module.BEFORE, stream,
                        swd, True, False, directory_watch=pwd,
                        directory_inventory_names=("sample",)
                    )
                    self.assertEqual(followup["status"], "BLOCKED")
                    self.assertIs(followup["can_authorize_dispatch"], False)
                    self.assertIs(
                        followup["independent_os_proof_verified"], False
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
