from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1001", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_MASK_CREATE = 0x10000000  # Native registration option.
RENAME_NOREPLACE = 1
AT_FDCWD = -100


@unittest.skipUnless(sys.platform == "linux", "renameat2 is Linux-only")
class NativeRenameNoreplaceCollisionRegression(unittest.TestCase):
    def test_failed_noreplace_preserves_both_link_watches_then_real_move(self):
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
                name = data[offset:offset + n].split(b"\0", 1)[0]
                offset += n
                result.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(data))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1001-public-rename-noreplace-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            first_alias = sample.parent / "public-first-alias"
            second_alias = sample.parent / "public-second-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                first_alias.symlink_to("sample")
                second_alias.symlink_to("sample")
                created = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-first-alias"),
                    created,
                )
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-second-alias"),
                    created,
                )
                link1_before = os.lstat(first_alias)
                link2_before = os.lstat(second_alias)
                self.assertNotEqual(link1_before.st_ino, link2_before.st_ino)
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
                link_mask = (
                    IN_MASK_CREATE | module.IN_DONT_FOLLOW |
                    module.IN_MOVE_SELF | module.IN_DELETE_SELF
                )
                first_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(first_alias), link_mask
                )
                second_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(second_alias), link_mask
                )
                self.assertEqual(
                    len({source_wd, parent_wd, first_wd, second_wd}), 4
                )
                self.assertGreater(min(first_wd, second_wd), 0)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # NOREPLACE MUST fail before moving any existing inode.
                module.ctypes.set_errno(0)
                refused = lib.renameat2(
                    AT_FDCWD,
                    module._checked_watch_path_bytes(first_alias),
                    AT_FDCWD,
                    module._checked_watch_path_bytes(second_alias),
                    RENAME_NOREPLACE,
                )
                self.assertEqual(refused, -1)
                self.assertEqual(module.ctypes.get_errno(), errno.EEXIST)
                self.assertEqual(os.lstat(first_alias).st_ino,
                                 link1_before.st_ino)
                self.assertEqual(os.lstat(second_alias).st_ino,
                                 link2_before.st_ino)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Actual writes through either still-existing alias reach
                # the original regular-file inode, not either symlink WD.
                for alias, content in (
                    (first_alias, module.AFTER),
                    (second_alias, module.BEFORE),
                ):
                    with alias.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    stream = module._read_receipt_pending(fd)
                    native = records(stream)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, cookie, name in native
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, cookie, name in native
                    ))
                    self.assertFalse(any(
                        wd in (first_wd, second_wd)
                        for wd, mask, cookie, name in native
                    ))
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    verdict = module._evaluate(
                        module.BEFORE, content, stream, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Free the conflicting destination in a real unlink:
                # only the SECOND link's existing watch is invalidated.
                os.unlink(second_alias)
                dest_removed = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, 0, b"public-second-alias"),
                    dest_removed,
                )
                self.assertIn(
                    (second_wd, module.IN_DELETE_SELF, 0, b""),
                    dest_removed,
                )
                self.assertIn(
                    (second_wd, module.IN_IGNORED, 0, b""),
                    dest_removed,
                )
                self.assertFalse(any(
                    wd == first_wd for wd, mask, cookie, name in dest_removed
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                module.ctypes.set_errno(0)
                moved = lib.renameat2(
                    AT_FDCWD,
                    module._checked_watch_path_bytes(first_alias),
                    AT_FDCWD,
                    module._checked_watch_path_bytes(second_alias),
                    RENAME_NOREPLACE,
                )
                self.assertEqual(
                    moved, 0,
                    f"renameat2 success failed: {module.ctypes.get_errno()}",
                )
                self.assertFalse(os.path.lexists(first_alias))
                self.assertEqual(os.lstat(second_alias).st_ino,
                                 link1_before.st_ino)
                real_move_stream = module._read_receipt_pending(fd)
                successful_move = records(real_move_stream)
                move_from = [
                    cookie for wd, mask, cookie, name in successful_move
                    if (wd == parent_wd and mask == module.IN_MOVED_FROM
                        and name == b"public-first-alias")
                ]
                move_to = [
                    cookie for wd, mask, cookie, name in successful_move
                    if (wd == parent_wd and mask == module.IN_MOVED_TO
                        and name == b"public-second-alias")
                ]
                self.assertEqual(len(move_from), 1)
                self.assertEqual(move_from, move_to)
                self.assertGreater(move_from[0], 0)
                self.assertIn(
                    (first_wd, module.IN_MOVE_SELF, 0, b""),
                    successful_move,
                )
                self.assertFalse(any(
                    wd == second_wd for wd, mask, cookie, name in successful_move
                ))
                # Feed the COMPLETE real kernel move stream to the
                # original two-WD observer. Its unknown link WD cannot
                # be silently filtered into an accepted source interval.
                self.assertFalse(module._classify_stream(
                    real_move_stream, source_wd, parent_wd
                )["well_formed"])
                native_move_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, real_move_stream,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("public-second-alias", "sample"),
                )
                self.assertEqual(native_move_verdict["status"], "BLOCKED")
                self.assertIs(
                    native_move_verdict["can_authorize_dispatch"], False
                )
                self.assertIs(
                    native_move_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                os.unlink(second_alias)
                last_delete = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, 0, b"public-second-alias"),
                    last_delete,
                )
                self.assertIn(
                    (first_wd, module.IN_DELETE_SELF, 0, b""),
                    last_delete,
                )
                self.assertIn(
                    (first_wd, module.IN_IGNORED, 0, b""),
                    last_delete,
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino, parent_final.st_mode),
                    (initial_parent.st_dev, initial_parent.st_ino,
                     initial_parent.st_mode),
                )
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
