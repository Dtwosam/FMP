from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1022", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native dup2 inotify requires Linux")
class NativeDup2DestroysObserverIndependenceRegression(unittest.TestCase):
    def test_dup2_replaces_independent_instance_with_shared_queue(self):
        primary_fd = None
        second_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            pos = 0
            result = []
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1022-public-dup2-instance-alias-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            parent_first = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent), ("sample",))
            try:
                primary_fd, source_wd, parent_wd = module._start_watch(sample)
                second_fd, second_source_wd, second_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertNotEqual(primary_fd, second_fd)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(second_fd), b"")

                # BEFORE dup2, TWO independent instances have separate
                # receipt queues despite watching the same public inode.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                first_stream = module._read_receipt_pending(primary_fd)
                second_stream = module._read_receipt_pending(second_fd)
                for data, swd, pwd in (
                    (first_stream, source_wd, parent_wd),
                    (second_stream, second_source_wd, second_parent_wd),
                ):
                    parsed = module._classify_stream(data, swd, pwd)
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    verdict = module._evaluate(
                        module.BEFORE, module.AFTER, data, swd,
                        True, False, directory_watch=pwd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(second_fd), b"")

                # dup2 atomically closes the ORIGINAL independent second
                # inotify FD and makes its SAME numeric FD refer to the
                # first instance instead. No second event queue remains.
                self.assertEqual(os.dup2(primary_fd, second_fd), second_fd)
                os.fstat(primary_fd)
                os.fstat(second_fd)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(second_fd), b"")

                # A real restore produces ONE shared queue. Draining
                # through second_fd makes primary_fd immediately quiet.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                shared = module._read_receipt_pending(second_fd)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in records(shared)
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in records(shared)
                ))
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(second_fd), b"")
                self.assertTrue(module._classify_stream(
                    shared, source_wd, parent_wd
                )["well_formed"])
                shared_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, shared,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(shared_verdict["status"], "BLOCKED")
                self.assertIs(shared_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    shared_verdict["independent_os_proof_verified"], False
                )

                # Removing source WD via the former second FD now
                # invalidates PRIMARY instance, not an independent
                # watcher. IN_IGNORED is read through primary_fd.
                lib = ctypes.CDLL(None, use_errno=True)
                lib.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
                lib.inotify_rm_watch.restype = ctypes.c_int
                self.assertEqual(lib.inotify_rm_watch(second_fd, source_wd), 0)
                invalidated = module._read_receipt_pending(primary_fd)
                self.assertEqual(records(invalidated), [
                    (source_wd, module.IN_IGNORED, b"")
                ])
                self.assertTrue(module._classify_stream(
                    invalidated, source_wd, parent_wd
                )["invalidated"])
                self.assertEqual(module._read_receipt_pending(second_fd), b"")

                # Real write still occurs; shared queue now has only
                # original parent's named events. No independent source
                # witness exists on the aliased second descriptor.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                parent_only = module._read_receipt_pending(primary_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in records(parent_only)
                ))
                self.assertFalse(any(
                    wd == source_wd for wd, mask, name in records(parent_only)
                ))
                self.assertEqual(module._read_receipt_pending(second_fd), b"")
                partial_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, parent_only,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(partial_verdict["status"], "BLOCKED")
                self.assertIs(partial_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    partial_verdict["independent_os_proof_verified"], False
                )

                # Closing replaced/aliased second FD does NOT restore
                # the destroyed independent watcher; primary remains.
                os.close(second_fd)
                second_fd = None
                os.fstat(primary_fd)
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                restored = module._read_receipt_pending(primary_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in records(restored)
                ))
                self.assertFalse(any(
                    wd == source_wd for wd, mask, name in records(restored)
                ))
                restore_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, restored,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(restore_verdict["status"], "BLOCKED")
                self.assertIs(restore_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    restore_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                last_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (last_parent.st_dev, last_parent.st_ino, last_parent.st_mode),
                    (parent_first.st_dev, parent_first.st_ino,
                     parent_first.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (second_fd, primary_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
