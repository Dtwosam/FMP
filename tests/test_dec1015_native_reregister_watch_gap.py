from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1015", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "inotify re-registration is Linux-only")
class NativeWatchReregistrationGapRegression(unittest.TestCase):
    def test_source_watch_reregistration_does_not_recover_previous_write_gap(self):
        fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            offset = 0
            result = []
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, n = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(n, len(data) - offset)
                name = data[offset:offset + n].split(b"\x00", 1)[0]
                offset += n
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1015-public-reregister-gap-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            parent_first = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, original_wd, parent_wd = module._start_watch(sample)
                self.assertNotEqual(original_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = ctypes.CDLL(None, use_errno=True)
                lib.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
                lib.inotify_rm_watch.restype = ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = ctypes.c_int

                # Source subscription is manually removed while the
                # original parent subscription remains installed.
                self.assertEqual(lib.inotify_rm_watch(fd, original_wd), 0)
                removed = module._read_receipt_pending(fd)
                self.assertEqual(records(removed), [
                    (original_wd, module.IN_IGNORED, b"")
                ])
                self.assertTrue(module._classify_stream(
                    removed, original_wd, parent_wd
                )["invalidated"])
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # A real modified public source arrives DURING the gap.
                # Only the parent can record the changed inode's basename.
                with sample.open("r+b") as writer:
                    self.assertEqual(
                        writer.write(module.AFTER), len(module.AFTER)
                    )
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                gap_stream = module._read_receipt_pending(fd)
                gap_events = records(gap_stream)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in gap_events
                ))
                self.assertFalse(any(
                    wd == original_wd for wd, mask, name in gap_events
                ))
                partial = module._classify_stream(
                    gap_stream, original_wd, parent_wd
                )
                self.assertTrue(partial["well_formed"])
                self.assertEqual(partial["source_modify_events"], 0)
                gap_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, gap_stream,
                    original_wd, False, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(gap_verdict["status"], "BLOCKED")
                self.assertIs(gap_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    gap_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Re-register on the same exact inode and same native FD.
                # The new WD does not retroactively report the gap write.
                replacement_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(sample),
                    module.MASK | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(replacement_wd, 0)
                self.assertNotIn(replacement_wd, (original_wd, parent_wd))
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(
                    (os.lstat(sample).st_dev, os.lstat(sample).st_ino),
                    (first.st_dev, first.st_ino),
                )

                # This later restoration IS observed by the new WD,
                # but an old-WD observer must fail closed on unexpected
                # replacement identity instead of silently accepting it.
                with sample.open("r+b") as writer:
                    self.assertEqual(
                        writer.write(module.BEFORE), len(module.BEFORE)
                    )
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                restored_stream = module._read_receipt_pending(fd)
                later_events = records(restored_stream)
                self.assertTrue(any(
                    wd == replacement_wd and mask == module.IN_MODIFY
                    for wd, mask, name in later_events
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in later_events
                ))
                self.assertFalse(any(
                    wd == original_wd for wd, mask, name in later_events
                ))
                stale = module._classify_stream(
                    restored_stream, original_wd, parent_wd
                )
                self.assertFalse(stale["well_formed"])
                accepted_identity_only = module._classify_stream(
                    restored_stream, replacement_wd, parent_wd
                )
                self.assertTrue(accepted_identity_only["well_formed"])
                self.assertFalse(accepted_identity_only["invalidated"])
                self.assertGreaterEqual(
                    accepted_identity_only["source_modify_events"], 1
                )
                for wd in (original_wd, replacement_wd):
                    result = module._evaluate(
                        module.BEFORE, module.BEFORE, restored_stream,
                        wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertIs(result["can_authorize_dispatch"], False)
                    self.assertIs(
                        result["independent_os_proof_verified"], False
                    )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                parent_last = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (parent_last.st_dev, parent_last.st_ino,
                     parent_last.st_mode),
                    (parent_first.st_dev, parent_first.st_ino,
                     parent_first.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
