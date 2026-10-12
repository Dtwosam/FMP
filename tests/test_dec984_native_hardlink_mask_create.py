from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec984", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_MASK_CREATE = 0x10000000  # Linux inotify registration-only option.


@unittest.skipUnless(sys.platform == "linux", "native hardlink inotify is Linux-only")
class NativeHardlinkMaskCreateCollisionRegression(unittest.TestCase):
    def test_real_hardlink_alias_is_same_existing_watched_inode(self):
        fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            out = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, n = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(n, len(stream) - pos)
                name = stream[pos:pos + n].split(b"\x00", 1)[0]
                pos += n
                self.assertEqual(cookie, 0)
                out.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return out

        with tempfile.TemporaryDirectory(
            prefix="dec984-public-hardlink-inode-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            alias = Path(tmp) / "public-hardlink-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            original = os.lstat(sample)
            original_parent = os.lstat(sample.parent)
            self.assertEqual(original.st_nlink, 1)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                os.link(sample, alias)
                self.assertEqual(
                    (os.lstat(alias).st_dev, os.lstat(alias).st_ino),
                    (original.st_dev, original.st_ino),
                )
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                linked = module._read_receipt_pending(fd)
                self.assertTrue(module._classify_stream(
                    linked, source_wd, parent_wd
                )["well_formed"])
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_CREATE
                    and name == b"public-hardlink-alias"
                    for wd, mask, name in records(linked)
                ))
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_ATTRIB
                    for wd, mask, name in records(linked)
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int

                # Distinct names do NOT imply distinct watchable inodes:
                # IN_MASK_CREATE rejects this hardlink within this FD.
                module.ctypes.set_errno(0)
                refused = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(alias),
                    IN_MASK_CREATE | module.IN_ATTRIB |
                    module.IN_DONT_FOLLOW,
                )
                self.assertEqual(refused, -1)
                self.assertEqual(module.ctypes.get_errno(), errno.EEXIST)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Actual write through the other pathname is visible on
                # the original source WD and as named alias parent events.
                with alias.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER),
                                     len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                written = module._read_receipt_pending(fd)
                classified = module._classify_stream(
                    written, source_wd, parent_wd
                )
                self.assertTrue(classified["well_formed"])
                self.assertFalse(classified["invalidated"])
                self.assertGreaterEqual(classified["source_modify_events"], 1)
                self.assertTrue(any(
                    wd == parent_wd and mask & module.IN_MODIFY
                    and name == b"public-hardlink-alias"
                    for wd, mask, name in records(written)
                ))
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in records(written)
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(sample.read_bytes(), module.AFTER)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                os.unlink(alias)
                unlinked = module._read_receipt_pending(fd)
                self.assertTrue(module._classify_stream(
                    unlinked, source_wd, parent_wd
                )["well_formed"])
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_DELETE
                    and name == b"public-hardlink-alias"
                    for wd, mask, name in records(unlinked)
                ))
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_ATTRIB
                    for wd, mask, name in records(unlinked)
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(os.lstat(sample).st_nlink, 1)
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                verdict = module._evaluate(
                    module.BEFORE, module.AFTER, written,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                restored = module._read_receipt_pending(fd)
                self.assertTrue(module._classify_stream(
                    restored, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode, final.st_nlink),
                    (original.st_dev, original.st_ino, original.st_mode,
                     original.st_nlink),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino, parent_final.st_mode),
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
