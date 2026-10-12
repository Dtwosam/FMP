from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec972", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Native Linux inotify registration bit; never an event mask.
IN_MASK_CREATE = 0x10000000


@unittest.skipUnless(sys.platform == "linux", "inotify mask-create collision is Linux-only")
class NativeMaskCreateCollisionRegression(unittest.TestCase):
    def test_real_mask_create_collision_preserves_both_existing_watches(self):
        fd = None
        with tempfile.TemporaryDirectory(
            prefix="dec972-public-mask-create-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
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

                # IN_MASK_CREATE, unlike IN_MASK_ADD and mask replacement,
                # declines an existing inode registration with EEXIST.
                for path, flags in (
                    (sample, module.IN_DONT_FOLLOW),
                    (sample.parent, module.IN_DONT_FOLLOW | module.IN_ONLYDIR),
                ):
                    module.ctypes.set_errno(0)
                    attempt = lib.inotify_add_watch(
                        fd, module._checked_watch_path_bytes(path),
                        module.IN_ATTRIB | IN_MASK_CREATE | flags,
                    )
                    actual_errno = module.ctypes.get_errno()
                    self.assertEqual(attempt, -1)
                    self.assertEqual(actual_errno, errno.EEXIST)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Failed create-only registrations do not remove original
                # content-write subscriptions or create an extra watch.
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
                    self.assertGreaterEqual(parsed["source_content_write_events"], 1)
                    self.assertEqual(parsed["directory_changes"], 0)
                    pos = 0
                    named_parent_writes = 0
                    while pos < len(stream):
                        wd, mask, cookie, length = module.EVENT.unpack_from(
                            stream, pos
                        )
                        pos += module.EVENT.size
                        name = stream[pos:pos + length].split(b"\x00", 1)[0]
                        pos += length
                        self.assertIn(wd, (source_wd, parent_wd))
                        if wd == parent_wd and mask & (
                            module.IN_MODIFY | module.IN_CLOSE_WRITE
                        ):
                            self.assertEqual(name, b"sample")
                            named_parent_writes += 1
                    self.assertEqual(pos, len(stream))
                    self.assertGreaterEqual(named_parent_writes, 1)
                    self.assertEqual(module._read_receipt_pending(fd), b"")
                    verdict = module._evaluate(
                        module.BEFORE, content, stream, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)

                sibling = sample.parent / "public-create-collision-sibling"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-EXTRA"),
                                 len(b"PUBLIC-EXTRA"))
                created_stream = module._read_receipt_pending(fd)
                self.assertTrue(created_stream)
                created = module._classify_stream(
                    created_stream, source_wd, parent_wd
                )
                self.assertTrue(created["well_formed"])
                self.assertGreaterEqual(created["directory_changes"], 1)
                os.unlink(sibling)
                removed_stream = module._read_receipt_pending(fd)
                self.assertTrue(removed_stream)
                removed = module._classify_stream(
                    removed_stream, source_wd, parent_wd
                )
                self.assertTrue(removed["well_formed"])
                self.assertGreaterEqual(removed["directory_changes"], 1)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                parent_last = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_last.st_dev, parent_last.st_ino, parent_last.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
