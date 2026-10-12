from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec968", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Linux inotify.h registration flag, deliberately NOT an event mask.
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native inotify one-shot is Linux-only")
class NativeSourceOneShotRegression(unittest.TestCase):
    def test_real_source_oneshot_auto_removes_watch_parent_survives(self):
        fd = None
        with tempfile.TemporaryDirectory(
            prefix="dec968-public-native-oneshot-source-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            original = os.lstat(sample)
            parent_original = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent), ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int

                # Reuse the same genuine source WD, replacing its subscription
                # with a single-event watch. The independent parent stays live.
                updated_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertEqual(updated_wd, source_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                first = module._read_receipt_pending(fd)
                self.assertTrue(first)
                parsed = module._classify_stream(first, source_wd, parent_wd)
                self.assertTrue(parsed["well_formed"])
                self.assertTrue(parsed["invalidated"])
                records = []
                offset = 0
                while offset < len(first):
                    wd, mask, cookie, length = module.EVENT.unpack_from(first, offset)
                    offset += module.EVENT.size
                    name = first[offset:offset + length].split(b"\x00", 1)[0]
                    offset += length
                    self.assertEqual(cookie, 0)
                    records.append((wd, mask, name))
                self.assertEqual(offset, len(first))
                self.assertEqual(
                    [mask for wd, mask, name in records if wd == source_wd],
                    [module.IN_MODIFY, module.IN_IGNORED],
                )
                self.assertTrue(any(
                    wd == parent_wd and mask & module.IN_MODIFY and name == b"sample"
                    for wd, mask, name in records
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # The source WD has genuinely gone; a subsequent write and
                # restoration are reported by the surviving parent only.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE), len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                second = module._read_receipt_pending(fd)
                self.assertTrue(second)
                followup = module._classify_stream(second, source_wd, parent_wd)
                self.assertTrue(followup["well_formed"])
                self.assertFalse(followup["invalidated"])
                self.assertGreaterEqual(followup["write_events"], 1)
                self.assertEqual(followup["directory_changes"], 0)
                offset = 0
                while offset < len(second):
                    wd, mask, cookie, length = module.EVENT.unpack_from(second, offset)
                    offset += module.EVENT.size
                    name = second[offset:offset + length].split(b"\x00", 1)[0]
                    offset += length
                    self.assertEqual(wd, parent_wd)
                    self.assertEqual(name, b"sample")
                    self.assertTrue(mask & (module.IN_MODIFY | module.IN_CLOSE_WRITE))
                self.assertEqual(offset, len(second))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                after = os.lstat(sample)
                parent_after = os.lstat(sample.parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (after.st_dev, after.st_ino, after.st_mode),
                    (original.st_dev, original.st_ino, original.st_mode),
                )
                self.assertEqual(
                    (parent_after.st_dev, parent_after.st_ino, parent_after.st_mode),
                    (parent_original.st_dev, parent_original.st_ino,
                     parent_original.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
                for data, stream in ((module.AFTER, first), (module.BEFORE, second)):
                    verdict = module._evaluate(
                        module.BEFORE, data, stream, source_wd, True, False,
                        directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
