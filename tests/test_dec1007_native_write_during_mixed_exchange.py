from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1007", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

RENAME_EXCHANGE = 2
AT_FDCWD = -100


@unittest.skipUnless(sys.platform == "linux", "Linux native file/directory exchange only")
class NativeSwappedPathContentWriteRegression(unittest.TestCase):
    def test_original_source_watch_sees_write_under_directory_name_during_exchange(self):
        fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            offset = 0
            output = []
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - offset)
                name = data[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                output.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(data))
            return output

        with tempfile.TemporaryDirectory(
            prefix="dec1007-public-swapped-path-write-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            directory_path = sample.parent / "public-other-dir"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial_file = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                directory_path.mkdir()
                initial_directory = os.lstat(directory_path)
                created = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR, 0,
                     b"public-other-dir"), created
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
                original_name = module._checked_watch_path_bytes(sample)
                alternative_name = module._checked_watch_path_bytes(
                    directory_path
                )

                # The original watched source file moves to the pathname
                # previously used by the directory. The old sample name
                # now denotes an actual directory, not the watched file.
                module.ctypes.set_errno(0)
                swapped = lib.renameat2(
                    AT_FDCWD, original_name,
                    AT_FDCWD, alternative_name, RENAME_EXCHANGE,
                )
                self.assertEqual(
                    swapped, 0,
                    f"exchange errno {module.ctypes.get_errno()}",
                )
                self.assertTrue(stat.S_ISDIR(os.lstat(sample).st_mode))
                self.assertTrue(stat.S_ISREG(os.lstat(directory_path).st_mode))
                self.assertEqual(os.lstat(sample).st_ino,
                                 initial_directory.st_ino)
                self.assertEqual(os.lstat(directory_path).st_ino,
                                 initial_file.st_ino)
                swap_stream = module._read_receipt_pending(fd)
                swap_events = records(swap_stream)
                self.assertIn(
                    (source_wd, module.IN_MOVE_SELF, 0, b""), swap_events
                )
                regular_from = [
                    c for wd, mask, c, name in swap_events
                    if (wd == parent_wd and mask == module.IN_MOVED_FROM
                        and name == b"sample")
                ]
                regular_to = [
                    c for wd, mask, c, name in swap_events
                    if (wd == parent_wd and mask == module.IN_MOVED_TO
                        and name == b"public-other-dir")
                ]
                dir_from = [
                    c for wd, mask, c, name in swap_events
                    if (wd == parent_wd
                        and mask == (module.IN_MOVED_FROM | module.IN_ISDIR)
                        and name == b"public-other-dir")
                ]
                dir_to = [
                    c for wd, mask, c, name in swap_events
                    if (wd == parent_wd
                        and mask == (module.IN_MOVED_TO | module.IN_ISDIR)
                        and name == b"sample")
                ]
                self.assertEqual(len(regular_from), 1)
                self.assertEqual(regular_from, regular_to)
                self.assertEqual(len(dir_from), 1)
                self.assertEqual(dir_from, dir_to)
                self.assertGreater(regular_from[0], 0)
                self.assertGreater(dir_from[0], 0)
                self.assertNotEqual(regular_from[0], dir_from[0])
                swap_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, swap_stream,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("public-other-dir", "sample"),
                )
                self.assertEqual(swap_verdict["status"], "BLOCKED")
                self.assertIs(swap_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    swap_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # The watched file inode is now reached via the formerly
                # DIRECTORY pathname. A real write must be reported on the
                # ORIGINAL source WD, with the NEW directory-entry name.
                with directory_path.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER),
                                     len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                changed = module._read_receipt_pending(fd)
                changed_records = records(changed)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, cookie, name in changed_records
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"public-other-dir"
                    for wd, mask, cookie, name in changed_records
                ))
                self.assertFalse(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, cookie, name in changed_records
                ))
                parsed_changed = module._classify_stream(
                    changed, source_wd, parent_wd
                )
                self.assertTrue(parsed_changed["well_formed"])
                self.assertFalse(parsed_changed["invalidated"])
                self.assertGreaterEqual(
                    parsed_changed["source_modify_events"], 1
                )
                self.assertGreaterEqual(
                    parsed_changed["source_content_write_events"], 1
                )
                self.assertEqual(directory_path.read_bytes(), module.AFTER)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                changed_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, changed,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("public-other-dir", "sample"),
                )
                self.assertEqual(changed_verdict["status"], "BLOCKED")
                self.assertIs(changed_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    changed_verdict["independent_os_proof_verified"], False
                )

                # The second atomic swap restores original pathname types,
                # but cannot erase the earlier witnessed content write.
                module.ctypes.set_errno(0)
                restored_names = lib.renameat2(
                    AT_FDCWD, original_name,
                    AT_FDCWD, alternative_name, RENAME_EXCHANGE,
                )
                self.assertEqual(
                    restored_names, 0,
                    f"reverse exchange errno {module.ctypes.get_errno()}",
                )
                self.assertEqual(os.lstat(sample).st_ino,
                                 initial_file.st_ino)
                self.assertEqual(os.lstat(directory_path).st_ino,
                                 initial_directory.st_ino)
                self.assertTrue(stat.S_ISREG(os.lstat(sample).st_mode))
                self.assertTrue(stat.S_ISDIR(os.lstat(directory_path).st_mode))
                reverse = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (source_wd, module.IN_MOVE_SELF, 0, b""), reverse
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")
                directory_path.rmdir()
                deleted = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR, 0,
                     b"public-other-dir"), deleted
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                restore_stream = module._read_receipt_pending(fd)
                restored_events = records(restore_stream)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, cookie, name in restored_events
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, cookie, name in restored_events
                ))
                final_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, restore_stream,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(final_verdict["status"], "BLOCKED")
                self.assertIs(final_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    final_verdict["independent_os_proof_verified"], False
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
