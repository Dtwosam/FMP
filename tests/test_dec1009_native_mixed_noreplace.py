from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1009", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

RENAME_NOREPLACE = 1
AT_FDCWD = -100


@unittest.skipUnless(sys.platform == "linux", "Linux native mixed-type NOREPLACE only")
class NativeMixedTypeNoreplaceRegression(unittest.TestCase):
    def test_both_mixed_type_noreplace_directions_fail_without_watch_events(self):
        fd = None

        def records(data):
            offset = 0
            result = []
            self.assertIs(type(data), bytes)
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - offset)
                name = data[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                result.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(data))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1009-public-mixed-type-noreplace-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            directory = sample.parent / "public-other-dir"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial_file = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                directory.mkdir()
                initial_directory = os.lstat(directory)
                created = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR, 0,
                     b"public-other-dir"), created
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                if not hasattr(lib, "renameat2"):
                    self.skipTest("libc renameat2 unavailable")
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                lib.renameat2.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint,
                ]
                lib.renameat2.restype = module.ctypes.c_int
                dir_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(directory),
                    module.IN_MOVE_SELF | module.IN_DELETE_SELF |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(dir_wd, 0)
                self.assertNotIn(dir_wd, (source_wd, parent_wd))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                file_bytes = module._checked_watch_path_bytes(sample)
                dir_bytes = module._checked_watch_path_bytes(directory)
                # Both destinations are occupied. NOREPLACE must refuse
                # in either direction rather than swap inode types.
                for src, dst in (
                    (file_bytes, dir_bytes),
                    (dir_bytes, file_bytes),
                ):
                    module.ctypes.set_errno(0)
                    result = lib.renameat2(
                        AT_FDCWD, src, AT_FDCWD, dst, RENAME_NOREPLACE,
                    )
                    self.assertEqual(result, -1)
                    self.assertEqual(module.ctypes.get_errno(), errno.EEXIST)
                    self.assertEqual(module._read_receipt_pending(fd), b"")
                    self.assertEqual(os.lstat(sample).st_ino,
                                     initial_file.st_ino)
                    self.assertEqual(os.lstat(directory).st_ino,
                                     initial_directory.st_ino)
                    self.assertTrue(stat.S_ISREG(os.lstat(sample).st_mode))
                    self.assertTrue(stat.S_ISDIR(os.lstat(directory).st_mode))

                # Neither an actual rename nor a watch-mask replacement
                # occurred. Native source and parent write subscriptions
                # must still observe genuine changed bytes and restore.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    write_stream = module._read_receipt_pending(fd)
                    writes = records(write_stream)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, cookie, name in writes
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, cookie, name in writes
                    ))
                    self.assertFalse(any(
                        wd == dir_wd for wd, mask, cookie, name in writes
                    ))
                    parsed = module._classify_stream(
                        write_stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    self.assertGreaterEqual(
                        parsed["source_content_write_events"], 1
                    )
                    verdict = module._evaluate(
                        module.BEFORE, content, write_stream,
                        source_wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=("public-other-dir", "sample"),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Only actual directory removal invalidates the directory
                # WD, after both refused native syscalls and source writes.
                directory.rmdir()
                removed = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR, 0,
                     b"public-other-dir"), removed
                )
                self.assertIn(
                    (dir_wd, module.IN_DELETE_SELF, 0, b""), removed
                )
                self.assertIn(
                    (dir_wd, module.IN_IGNORED, 0, b""), removed
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final_file = os.lstat(sample)
                final_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (final_file.st_dev, final_file.st_ino,
                     final_file.st_mode),
                    (initial_file.st_dev, initial_file.st_ino,
                     initial_file.st_mode),
                )
                self.assertEqual(
                    (final_parent.st_dev, final_parent.st_ino,
                     final_parent.st_mode),
                    (initial_parent.st_dev, initial_parent.st_ino,
                     initial_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
