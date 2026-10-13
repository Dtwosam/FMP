from __future__ import annotations

import ctypes
import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1014", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native watch removal is Linux-only")
class NativeExplicitWatchRemovalRegression(unittest.TestCase):
    def test_rm_watch_invalidates_one_subscription_without_silencing_other_fd(self):
        removed_fd = None
        witness_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            pos = 0
            output = []
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(data) - pos)
                name = data[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                self.assertEqual(cookie, 0)
                output.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return output

        with tempfile.TemporaryDirectory(
            prefix="dec1014-public-manual-watch-loss-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            source_before = os.lstat(sample)
            parent_before = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                removed_fd, source_wd, parent_wd = module._start_watch(sample)
                witness_fd, witness_source_wd, witness_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertNotEqual(removed_fd, witness_fd)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertNotEqual(witness_source_wd, witness_parent_wd)
                self.assertEqual(module._read_receipt_pending(removed_fd), b"")
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                lib = ctypes.CDLL(None, use_errno=True)
                lib.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
                lib.inotify_rm_watch.restype = ctypes.c_int

                # Real explicit native removal of ONE source watch produces
                # IN_IGNORED on its original descriptor. Parent survives.
                ctypes.set_errno(0)
                self.assertEqual(
                    lib.inotify_rm_watch(removed_fd, source_wd), 0
                )
                source_ignored = module._read_receipt_pending(removed_fd)
                self.assertEqual(records(source_ignored), [
                    (source_wd, module.IN_IGNORED, b"")
                ])
                self.assertTrue(module._classify_stream(
                    source_ignored, source_wd, parent_wd
                )["invalidated"])
                self.assertEqual(module._read_receipt_pending(removed_fd), b"")
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # Duplicate removal is EINVAL: it must not create fresh
                # events or destroy the parent watch.
                ctypes.set_errno(0)
                self.assertEqual(
                    lib.inotify_rm_watch(removed_fd, source_wd), -1
                )
                self.assertEqual(ctypes.get_errno(), errno.EINVAL)
                self.assertEqual(module._read_receipt_pending(removed_fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(
                        writer.write(module.AFTER), len(module.AFTER)
                    )
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                remaining_parent = module._read_receipt_pending(removed_fd)
                self.assertTrue(remaining_parent)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in records(remaining_parent)
                ))
                self.assertFalse(any(
                    wd == source_wd for wd, mask, name
                    in records(remaining_parent)
                ))
                source_still_watched = module._read_receipt_pending(witness_fd)
                surviving = module._classify_stream(
                    source_still_watched,
                    witness_source_wd, witness_parent_wd
                )
                self.assertTrue(surviving["well_formed"])
                self.assertFalse(surviving["invalidated"])
                self.assertGreaterEqual(surviving["source_modify_events"], 1)
                self.assertGreaterEqual(
                    surviving["source_content_write_events"], 1
                )
                for event_data, wd, dir_wd in (
                    (source_ignored, source_wd, parent_wd),
                    (remaining_parent, source_wd, parent_wd),
                    (source_still_watched,
                     witness_source_wd, witness_parent_wd),
                ):
                    verdict = module._evaluate(
                        module.BEFORE, module.AFTER, event_data,
                        wd, True, False, directory_watch=dir_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                for current_fd in (removed_fd, witness_fd):
                    self.assertEqual(module._read_receipt_pending(current_fd), b"")

                # Remove the remaining parent watch from only the first
                # instance; independent second FD must retain BOTH WDs.
                ctypes.set_errno(0)
                self.assertEqual(
                    lib.inotify_rm_watch(removed_fd, parent_wd), 0
                )
                parent_ignored = module._read_receipt_pending(removed_fd)
                self.assertEqual(records(parent_ignored), [
                    (parent_wd, module.IN_IGNORED, b"")
                ])
                self.assertTrue(module._classify_stream(
                    parent_ignored, source_wd, parent_wd
                )["invalidated"])
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")
                self.assertEqual(module._read_receipt_pending(removed_fd), b"")

                # An EMPTY queue on the now-watchless FD proves nothing
                # about writes: the independent dual instance sees restore.
                with sample.open("r+b") as writer:
                    self.assertEqual(
                        writer.write(module.BEFORE), len(module.BEFORE)
                    )
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                self.assertEqual(module._read_receipt_pending(removed_fd), b"")
                true_restore = module._read_receipt_pending(witness_fd)
                evidence = module._classify_stream(
                    true_restore, witness_source_wd, witness_parent_wd
                )
                self.assertTrue(evidence["well_formed"])
                self.assertFalse(evidence["invalidated"])
                self.assertGreaterEqual(evidence["source_modify_events"], 1)
                restore_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, true_restore,
                    witness_source_wd, True, False,
                    directory_watch=witness_parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(restore_verdict["status"], "BLOCKED")
                self.assertIs(
                    restore_verdict["can_authorize_dispatch"], False
                )
                self.assertIs(
                    restore_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                after = os.lstat(sample)
                parent_after = os.lstat(sample.parent)
                self.assertEqual(
                    (after.st_dev, after.st_ino, after.st_mode),
                    (source_before.st_dev, source_before.st_ino,
                     source_before.st_mode),
                )
                self.assertEqual(
                    (parent_after.st_dev, parent_after.st_ino,
                     parent_after.st_mode),
                    (parent_before.st_dev, parent_before.st_ino,
                     parent_before.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for current_fd in (witness_fd, removed_fd):
                    if current_fd is not None:
                        os.close(current_fd)
                        with self.assertRaises(OSError):
                            os.fstat(current_fd)
