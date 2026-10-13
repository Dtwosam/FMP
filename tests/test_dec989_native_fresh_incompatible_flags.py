from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec989", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_MASK_CREATE = 0x10000000
IN_MASK_ADD = 0x20000000


@unittest.skipUnless(sys.platform == "linux", "native Linux mask flags required")
class NativeFreshIncompatibleMaskFlagsRegression(unittest.TestCase):
    def test_real_invalid_combined_flags_do_not_create_initial_watches(self):
        fd = None
        with tempfile.TemporaryDirectory(
            prefix="dec989-public-fresh-invalid-flags-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            original = os.lstat(sample)
            original_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_init1.argtypes = [module.ctypes.c_int]
                lib.inotify_init1.restype = module.ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(fd, 2)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Unlike the already-watched collision case DEC-988,
                # there are NO WDs yet. Both invalid registration attempts
                # still return EINVAL; no watch is implicitly created.
                for candidate, extra in (
                    (sample, module.IN_DONT_FOLLOW),
                    (sample.parent, module.IN_DONT_FOLLOW | module.IN_ONLYDIR),
                ):
                    module.ctypes.set_errno(0)
                    result = lib.inotify_add_watch(
                        fd, module._checked_watch_path_bytes(candidate),
                        IN_MASK_ADD | IN_MASK_CREATE | module.IN_MODIFY | extra,
                    )
                    self.assertEqual(result, -1)
                    self.assertEqual(module.ctypes.get_errno(), errno.EINVAL)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # A genuine first create-only registration can still
                # succeed for EACH inode in the same fresh instance.
                source_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(sample),
                    IN_MASK_CREATE | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW,
                )
                parent_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(sample.parent),
                    IN_MASK_CREATE | module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_CREATE | module.IN_DELETE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(source_wd, 0)
                self.assertGreater(parent_wd, 0)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                sibling = sample.parent / "public-created-after-invalid"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-SIBLING"),
                                 len(b"PUBLIC-SIBLING"))
                created = module._read_receipt_pending(fd)
                self.assertTrue(created)
                parsed_created = module._classify_stream(
                    created, source_wd, parent_wd
                )
                self.assertTrue(parsed_created["well_formed"])
                self.assertGreaterEqual(parsed_created["directory_changes"], 1)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                os.unlink(sibling)
                deleted = module._read_receipt_pending(fd)
                self.assertTrue(deleted)
                parsed_deleted = module._classify_stream(
                    deleted, source_wd, parent_wd
                )
                self.assertTrue(parsed_deleted["well_formed"])
                self.assertGreaterEqual(parsed_deleted["directory_changes"], 1)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # The valid subscriptions now observe real distinct-byte
                # writes and a full restoration of the public sample.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    stream = module._read_receipt_pending(fd)
                    self.assertTrue(stream)
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    self.assertGreaterEqual(
                        parsed["source_content_write_events"], 1
                    )
                    offset = 0
                    named_parent_modify = False
                    while offset < len(stream):
                        wd, mask, cookie, n = module.EVENT.unpack_from(
                            stream, offset
                        )
                        offset += module.EVENT.size
                        name = stream[offset:offset + n].split(b"\0", 1)[0]
                        offset += n
                        if (wd == parent_wd and mask & module.IN_MODIFY
                                and name == b"sample"):
                            named_parent_modify = True
                    self.assertEqual(offset, len(stream))
                    self.assertTrue(named_parent_modify)
                    self.assertEqual(module._read_receipt_pending(fd), b"")
                    verdict = module._evaluate(
                        module.BEFORE, content, stream, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                parent_last = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (original.st_dev, original.st_ino, original.st_mode),
                )
                self.assertEqual(
                    (parent_last.st_dev, parent_last.st_ino, parent_last.st_mode),
                    (original_parent.st_dev, original_parent.st_ino,
                     original_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
