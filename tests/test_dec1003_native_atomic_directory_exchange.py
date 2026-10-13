from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1003", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

RENAME_EXCHANGE = 2
AT_FDCWD = -100


@unittest.skipUnless(sys.platform == "linux", "directory rename exchange is Linux-only")
class NativeAtomicDirectoryExchangeRegression(unittest.TestCase):
    def test_exchange_directories_preserves_inodes_with_real_isdir_move_records(self):
        fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            offset = 0
            output = []
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, n = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(n, len(data) - offset)
                name = data[offset:offset + n].split(b"\x00", 1)[0]
                offset += n
                output.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(data))
            return output

        with tempfile.TemporaryDirectory(
            prefix="dec1003-public-directory-exchange-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            first_dir = sample.parent / "public-first-dir"
            second_dir = sample.parent / "public-second-dir"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                first_dir.mkdir()
                second_dir.mkdir()
                created = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR, 0,
                     b"public-first-dir"),
                    created,
                )
                self.assertIn(
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR, 0,
                     b"public-second-dir"),
                    created,
                )
                first_initial = os.lstat(first_dir)
                second_initial = os.lstat(second_dir)
                self.assertNotEqual(first_initial.st_ino, second_initial.st_ino)
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
                watch_mask = (
                    module.IN_MOVE_SELF | module.IN_DELETE_SELF |
                    module.IN_DONT_FOLLOW | module.IN_ONLYDIR
                )
                first_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(first_dir), watch_mask
                )
                second_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(second_dir), watch_mask
                )
                self.assertEqual(
                    len({source_wd, parent_wd, first_wd, second_wd}), 4
                )
                self.assertGreater(min(first_wd, second_wd), 0)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                module.ctypes.set_errno(0)
                rc = lib.renameat2(
                    AT_FDCWD, module._checked_watch_path_bytes(first_dir),
                    AT_FDCWD, module._checked_watch_path_bytes(second_dir),
                    RENAME_EXCHANGE,
                )
                self.assertEqual(
                    rc, 0,
                    f"native directory exchange errno {module.ctypes.get_errno()}",
                )
                self.assertEqual(os.lstat(first_dir).st_ino,
                                 second_initial.st_ino)
                self.assertEqual(os.lstat(second_dir).st_ino,
                                 first_initial.st_ino)
                stream = module._read_receipt_pending(fd)
                events = records(stream)
                from_moves = [
                    (cookie, name) for wd, mask, cookie, name in events
                    if wd == parent_wd and
                    mask == module.IN_MOVED_FROM | module.IN_ISDIR
                ]
                to_moves = [
                    (cookie, name) for wd, mask, cookie, name in events
                    if wd == parent_wd and
                    mask == module.IN_MOVED_TO | module.IN_ISDIR
                ]
                self.assertEqual(len(from_moves), 2)
                self.assertEqual(len(to_moves), 2)
                self.assertEqual(
                    sorted(name for cookie, name in from_moves),
                    [b"public-first-dir", b"public-second-dir"],
                )
                self.assertEqual(
                    sorted(name for cookie, name in to_moves),
                    [b"public-first-dir", b"public-second-dir"],
                )
                self.assertEqual(
                    sorted(cookie for cookie, name in from_moves),
                    sorted(cookie for cookie, name in to_moves),
                )
                self.assertEqual(len({cookie for cookie, name in from_moves}), 2)
                self.assertTrue(all(cookie > 0 for cookie, name in from_moves))
                for cookie, old_name in from_moves:
                    matching = [name for c, name in to_moves if c == cookie]
                    self.assertEqual(len(matching), 1)
                    self.assertNotEqual(matching[0], old_name)
                self.assertIn(
                    (first_wd, module.IN_MOVE_SELF, 0, b""), events
                )
                self.assertIn(
                    (second_wd, module.IN_MOVE_SELF, 0, b""), events
                )
                self.assertFalse(any(
                    mask & (module.IN_DELETE_SELF | module.IN_IGNORED)
                    for wd, mask, cookie, name in events
                ))
                self.assertFalse(module._classify_stream(
                    stream, source_wd, parent_wd
                )["well_formed"])
                blocked = module._evaluate(
                    module.BEFORE, module.BEFORE, stream,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=(
                        "public-first-dir", "public-second-dir", "sample"
                    ),
                )
                self.assertEqual(blocked["status"], "BLOCKED")
                self.assertIs(blocked["can_authorize_dispatch"], False)
                self.assertIs(blocked["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # After swap, first pathname refers to SECOND inode.
                first_dir.rmdir()
                first_removed = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR, 0,
                     b"public-first-dir"),
                    first_removed,
                )
                self.assertIn(
                    (second_wd, module.IN_DELETE_SELF, 0, b""),
                    first_removed,
                )
                self.assertIn(
                    (second_wd, module.IN_IGNORED, 0, b""),
                    first_removed,
                )
                self.assertFalse(any(
                    wd == first_wd
                    for wd, mask, cookie, name in first_removed
                ))
                second_dir.rmdir()
                second_removed = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR, 0,
                     b"public-second-dir"),
                    second_removed,
                )
                self.assertIn(
                    (first_wd, module.IN_DELETE_SELF, 0, b""),
                    second_removed,
                )
                self.assertIn(
                    (first_wd, module.IN_IGNORED, 0, b""),
                    second_removed,
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    source_stream = module._read_receipt_pending(fd)
                    parsed = module._classify_stream(
                        source_stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    verdict = module._evaluate(
                        module.BEFORE, content, source_stream,
                        source_wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                final_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (final_parent.st_dev, final_parent.st_ino, final_parent.st_mode),
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
