from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec969", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Linux inotify.h registration flag, not an inotify event record mask.
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native inotify one-shot is Linux-only")
class NativeParentOneShotRegression(unittest.TestCase):
    def test_real_parent_oneshot_auto_removes_watch_source_survives(self):
        fd = None
        with tempfile.TemporaryDirectory(
            prefix="dec969-public-native-oneshot-parent-", dir="/tmp"
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

                # Replace ONLY the parent's mask with one-shot IN_CREATE.
                # The sample's source watch remains installed throughout.
                same_parent_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(sample.parent),
                    module.IN_CREATE | module.IN_DONT_FOLLOW |
                    module.IN_ONLYDIR | IN_ONESHOT,
                )
                self.assertEqual(same_parent_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                sibling = sample.parent / "public-parent-oneshot-sibling"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-SIBLING"),
                                 len(b"PUBLIC-SIBLING"))
                create_stream = module._read_receipt_pending(fd)
                self.assertTrue(create_stream)
                parsed_create = module._classify_stream(
                    create_stream, source_wd, parent_wd
                )
                self.assertTrue(parsed_create["well_formed"])
                self.assertTrue(parsed_create["invalidated"])
                self.assertEqual(parsed_create["directory_changes"], 1)
                records = []
                offset = 0
                while offset < len(create_stream):
                    wd, mask, cookie, length = module.EVENT.unpack_from(
                        create_stream, offset
                    )
                    offset += module.EVENT.size
                    name = create_stream[offset:offset + length].split(b"\x00", 1)[0]
                    offset += length
                    self.assertEqual(cookie, 0)
                    records.append((wd, mask, name))
                self.assertEqual(offset, len(create_stream))
                self.assertEqual(records, [
                    (parent_wd, module.IN_CREATE, b"public-parent-oneshot-sibling"),
                    (parent_wd, module.IN_IGNORED, b""),
                ])
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # The parent registration is now absent; removing this
                # sibling has no parent-WD event despite an actual unlink.
                os.unlink(sibling)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                # The separate source registration continues observing real
                # source writes even though parent inventory events are lost.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                source_stream = module._read_receipt_pending(fd)
                self.assertTrue(source_stream)
                parsed_source = module._classify_stream(
                    source_stream, source_wd, parent_wd
                )
                self.assertTrue(parsed_source["well_formed"])
                self.assertFalse(parsed_source["invalidated"])
                self.assertGreaterEqual(parsed_source["source_modify_events"], 1)
                self.assertGreaterEqual(parsed_source["source_content_write_events"], 1)
                self.assertEqual(parsed_source["directory_changes"], 0)
                offset = 0
                while offset < len(source_stream):
                    wd, mask, cookie, length = module.EVENT.unpack_from(
                        source_stream, offset
                    )
                    offset += module.EVENT.size + length
                    self.assertEqual(wd, source_wd)
                    self.assertTrue(mask & (module.IN_MODIFY | module.IN_CLOSE_WRITE))
                self.assertEqual(offset, len(source_stream))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE), len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                restored = module._read_receipt_pending(fd)
                self.assertTrue(restored)
                self.assertTrue(module._classify_stream(
                    restored, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)

                after = os.lstat(sample)
                parent_after = os.lstat(sample.parent)
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
                for data, stream in (
                    (module.BEFORE, create_stream),
                    (module.AFTER, source_stream),
                ):
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
