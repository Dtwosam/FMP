from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec994", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_MASK_CREATE = 0x10000000  # Linux registration flag, not an event action.


@unittest.skipUnless(sys.platform == "linux", "native dangling symlink is Linux-only")
class NativeDanglingSymlinkWatchRegression(unittest.TestCase):
    def test_dangling_target_enoent_but_nofollow_link_watch_can_be_created(self):
        fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            result = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, count = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(count, len(stream) - pos)
                name = stream[pos:pos + count].split(b"\x00", 1)[0]
                pos += count
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec994-public-dangling-symlink-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            alias = sample.parent / "public-dangling-alias"
            missing = sample.parent / "missing-public-target"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertFalse(missing.exists())
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                alias.symlink_to("missing-public-target")
                created = module._read_receipt_pending(fd)
                self.assertIn(
                    (parent_wd, module.IN_CREATE, b"public-dangling-alias"),
                    records(created),
                )
                self.assertTrue(module._classify_stream(
                    created, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertTrue(alias.is_symlink())
                self.assertFalse(alias.exists())

                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int

                # Default symlink-following resolves a target that DOES
                # NOT exist, so create-only must return genuine ENOENT.
                module.ctypes.set_errno(0)
                no_target = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(alias),
                    IN_MASK_CREATE | module.IN_DELETE_SELF,
                )
                self.assertEqual(no_target, -1)
                self.assertEqual(module.ctypes.get_errno(), errno.ENOENT)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # IN_DONT_FOLLOW instead registers the existing symlink
                # inode on a third real WD despite the broken target.
                link_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(alias),
                    IN_MASK_CREATE | module.IN_DONT_FOLLOW |
                    module.IN_DELETE_SELF,
                )
                self.assertGreater(link_wd, 0)
                self.assertNotIn(link_wd, (source_wd, parent_wd))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                os.unlink(alias)
                removed = module._read_receipt_pending(fd)
                removed_records = records(removed)
                self.assertIn(
                    (parent_wd, module.IN_DELETE, b"public-dangling-alias"),
                    removed_records,
                )
                self.assertEqual(
                    [(wd, mask, name) for wd, mask, name in removed_records
                     if wd == link_wd],
                    [(link_wd, module.IN_DELETE_SELF, b""),
                     (link_wd, module.IN_IGNORED, b"")],
                )
                # Only original source + parent WDs are trusted by the
                # unchanged parser: unexpected link-WD invalidation is NOT
                # silently accepted as a clean two-watch observation.
                self.assertFalse(module._classify_stream(
                    removed, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(fd), b"")
                blocked = module._evaluate(
                    module.BEFORE, module.BEFORE, removed,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(blocked["status"], "BLOCKED")
                self.assertIs(blocked["can_authorize_dispatch"], False)
                self.assertIs(blocked["independent_os_proof_verified"], False)

                # Neither failed default following nor the removed link
                # watch disturbed the original content subscriptions.
                for contents in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(contents), len(contents))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    stream = module._read_receipt_pending(fd)
                    native = records(stream)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in native
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in native
                    ))
                    self.assertFalse(any(wd == link_wd
                                         for wd, mask, name in native))
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    verdict = module._evaluate(
                        module.BEFORE, contents, stream, source_wd,
                        True, False, directory_watch=parent_wd,
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
                self.assertFalse(missing.exists())
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
