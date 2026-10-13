from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec997", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_MASK_CREATE = 0x10000000  # Linux registration option.


@unittest.skipUnless(sys.platform == "linux", "native symlink rename requires Linux")
class NativeSymlinkPathnameReuseRegression(unittest.TestCase):
    def test_renamed_link_watch_tracks_old_inode_new_same_name_is_distinct(self):
        fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            result = []
            pos = 0
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(stream) - pos)
                name = stream[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                result.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec997-public-symlink-path-reuse-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            alias = sample.parent / "public-alias"
            moved = sample.parent / "public-moved-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            first_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                alias.symlink_to("sample")
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-alias"),
                    records(module._read_receipt_pending(fd)),
                )
                old_link_stat = os.lstat(alias)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                mask = (IN_MASK_CREATE | module.IN_DONT_FOLLOW
                        | module.IN_MOVE_SELF | module.IN_DELETE_SELF)
                old_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(alias), mask
                )
                self.assertGreater(old_wd, 0)
                self.assertNotIn(old_wd, (source_wd, parent_wd))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Move a watched symlink inode out of its initial pathname.
                os.rename(alias, moved)
                move_stream = module._read_receipt_pending(fd)
                move_events = records(move_stream)
                from_events = [
                    (cookie, mask & module.IN_ISDIR)
                    for wd, mask, cookie, name in move_events
                    if wd == parent_wd and mask == module.IN_MOVED_FROM
                    and name == b"public-alias"
                ]
                to_events = [
                    (cookie, mask & module.IN_ISDIR)
                    for wd, mask, cookie, name in move_events
                    if wd == parent_wd and mask == module.IN_MOVED_TO
                    and name == b"public-moved-alias"
                ]
                self.assertEqual(len(from_events), 1)
                self.assertEqual(to_events, from_events)
                self.assertGreater(from_events[0][0], 0)
                self.assertEqual(from_events[0][1], 0)
                self.assertIn(
                    (old_wd, module.IN_MOVE_SELF, 0, b""), move_events
                )
                self.assertEqual(os.lstat(moved).st_ino,
                                 old_link_stat.st_ino)
                self.assertFalse(alias.exists())
                self.assertFalse(module._classify_stream(
                    move_stream, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Recreate the SAME original pathname while the old
                # symlink inode remains live under its new name.
                alias.symlink_to("sample")
                new_link_stat = os.lstat(alias)
                self.assertNotEqual(new_link_stat.st_ino,
                                    old_link_stat.st_ino)
                recreated = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-alias"),
                    recreated,
                )
                self.assertFalse(any(
                    wd == old_wd for wd, mask, cookie, name in recreated
                ))
                new_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(alias), mask
                )
                self.assertGreater(new_wd, 0)
                self.assertNotIn(new_wd, (source_wd, parent_wd, old_wd))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # The two same-target links now have different inodes and
                # native WDs. Deleting one invalidates only its own watch.
                os.unlink(moved)
                old_del = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, 0,
                     b"public-moved-alias"), old_del
                )
                self.assertIn(
                    (old_wd, module.IN_DELETE_SELF, 0, b""), old_del
                )
                self.assertIn(
                    (old_wd, module.IN_IGNORED, 0, b""), old_del
                )
                self.assertFalse(any(
                    wd == new_wd for wd, mask, cookie, name in old_del
                ))
                os.unlink(alias)
                new_del = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, 0, b"public-alias"),
                    new_del
                )
                self.assertIn(
                    (new_wd, module.IN_DELETE_SELF, 0, b""), new_del
                )
                self.assertIn(
                    (new_wd, module.IN_IGNORED, 0, b""), new_del
                )
                self.assertFalse(any(
                    wd == old_wd for wd, mask, cookie, name in new_del
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    stream = module._read_receipt_pending(fd)
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    self.assertFalse(any(
                        wd in (old_wd, new_wd)
                        for wd, mask, cookie, name in records(stream)
                    ))
                    blocked = module._evaluate(
                        module.BEFORE, content, stream, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(blocked["status"], "BLOCKED")
                    self.assertIs(blocked["can_authorize_dispatch"], False)
                    self.assertIs(blocked["independent_os_proof_verified"], False)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                final_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (final_parent.st_dev, final_parent.st_ino,
                     final_parent.st_mode),
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
