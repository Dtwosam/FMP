from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1002", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

RENAME_NOREPLACE = 1
AT_FDCWD = -100


@unittest.skipUnless(sys.platform == "linux", "native same-inode rename is Linux-only")
class NativeSameInodeHardlinkRenameRegression(unittest.TestCase):
    def test_noreplace_rejects_same_inode_hardlink_but_normal_rename_is_noop(self):
        fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            offset = 0
            output = []
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(length, len(data) - offset)
                name = data[offset:offset + length].split(b"\0", 1)[0]
                offset += length
                output.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(data))
            return output

        with tempfile.TemporaryDirectory(
            prefix="dec1002-public-same-inode-rename-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            alias = sample.parent / "public-hardlink-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            first_parent = os.lstat(sample.parent)
            self.assertEqual(first.st_nlink, 1)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                os.link(sample, alias)
                self.assertEqual(
                    (os.lstat(alias).st_dev, os.lstat(alias).st_ino),
                    (first.st_dev, first.st_ino),
                )
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                linked = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-hardlink-alias"),
                    linked,
                )
                self.assertIn(
                    (source_wd, module.IN_ATTRIB, 0, b""),
                    linked,
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                if not hasattr(lib, "renameat2"):
                    self.skipTest("libc renameat2 unavailable")
                lib.renameat2.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint,
                ]
                lib.renameat2.restype = module.ctypes.c_int
                source_bytes = module._checked_watch_path_bytes(sample)
                alias_bytes = module._checked_watch_path_bytes(alias)

                # Same inode at two distinct names. NOREPLACE is still
                # exclusive on the occupied DESTINATION DIRECTORY ENTRY.
                module.ctypes.set_errno(0)
                denied = lib.renameat2(
                    AT_FDCWD, source_bytes,
                    AT_FDCWD, alias_bytes, RENAME_NOREPLACE,
                )
                self.assertEqual(denied, -1)
                self.assertEqual(module.ctypes.get_errno(), errno.EEXIST)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # With NOREPLACE absent, the Linux same-inode hardlink
                # special case is a successful NO-OP, not a move event.
                module.ctypes.set_errno(0)
                no_op = lib.renameat2(
                    AT_FDCWD, source_bytes, AT_FDCWD, alias_bytes, 0
                )
                self.assertEqual(no_op, 0)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(os.lstat(sample).st_ino, first.st_ino)
                self.assertEqual(os.lstat(alias).st_ino, first.st_ino)
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent),
                    ("public-hardlink-alias", "sample"),
                )

                # The original watches still record true writes made
                # through either link; these operations are not no-ops.
                for candidate, content, expected_name in (
                    (alias, module.AFTER, b"public-hardlink-alias"),
                    (sample, module.BEFORE, b"sample"),
                ):
                    with candidate.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    stream = module._read_receipt_pending(fd)
                    actual = records(stream)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, cookie, name in actual
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == expected_name
                        for wd, mask, cookie, name in actual
                    ))
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    result = module._evaluate(
                        module.BEFORE, content, stream, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("public-hardlink-alias", "sample"),
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertIs(result["can_authorize_dispatch"], False)
                    self.assertIs(result["independent_os_proof_verified"], False)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                os.unlink(alias)
                link_removed = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, 0, b"public-hardlink-alias"),
                    link_removed,
                )
                self.assertIn(
                    (source_wd, module.IN_ATTRIB, 0, b""),
                    link_removed,
                )
                self.assertEqual(os.lstat(sample).st_nlink, 1)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                last_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode, last.st_nlink),
                    (first.st_dev, first.st_ino, first.st_mode, first.st_nlink),
                )
                self.assertEqual(
                    (last_parent.st_dev, last_parent.st_ino, last_parent.st_mode),
                    (first_parent.st_dev, first_parent.st_ino,
                     first_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
