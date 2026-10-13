from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec991", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_MASK_CREATE = 0x10000000  # Linux inotify registration-only bit.


@unittest.skipUnless(sys.platform == "linux", "inotify symlink creation is Linux-only")
class NativeCreateOnlySymlinkIdentityRegression(unittest.TestCase):
    def test_real_create_only_alias_collides_with_target_but_nofollow_succeeds(self):
        fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            result = []
            pos = 0
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, size = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(size, len(stream) - pos)
                name = stream[pos:pos + size].split(b"\0", 1)[0]
                pos += size
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec991-public-create-only-link-inode-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            alias = Path(tmp) / "public-symlink-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                alias.symlink_to("sample")
                self.assertNotEqual(os.lstat(alias).st_ino, initial.st_ino)
                added = module._read_receipt_pending(fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_CREATE
                    and name == b"public-symlink-alias"
                    for wd, mask, name in records(added)
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int

                # Default symlink following resolves the already-watched
                # original target inode; create-only must refuse EEXIST.
                module.ctypes.set_errno(0)
                followed = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(alias),
                    IN_MASK_CREATE | module.IN_MODIFY,
                )
                self.assertEqual(followed, -1)
                self.assertEqual(module.ctypes.get_errno(), errno.EEXIST)

                # IN_DONT_FOLLOW selects a different real symlink inode,
                # permitting a new WD in the SAME native inotify instance.
                link_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(alias),
                    IN_MASK_CREATE | module.IN_DONT_FOLLOW |
                    module.IN_DELETE_SELF,
                )
                self.assertGreater(link_wd, 0)
                self.assertNotIn(link_wd, (source_wd, parent_wd))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Writing via the alias modifies the underlying target.
                # The source and parent report the real activity; the
                # watched symlink inode has not itself changed.
                with alias.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER),
                                     len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                changed = module._read_receipt_pending(fd)
                changed_records = records(changed)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in changed_records
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"public-symlink-alias"
                    for wd, mask, name in changed_records
                ))
                self.assertFalse(any(
                    wd == link_wd for wd, mask, name in changed_records
                ))
                self.assertTrue(module._classify_stream(
                    changed, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(fd), b"")
                verdict = module._evaluate(
                    module.BEFORE, module.AFTER, changed,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)

                # Removing ONLY the alias invalidates its separate WD.
                # The original source WD stays live on the target inode.
                os.unlink(alias)
                removed = module._read_receipt_pending(fd)
                removed_records = records(removed)
                self.assertIn(
                    (parent_wd, module.IN_DELETE, b"public-symlink-alias"),
                    removed_records,
                )
                self.assertEqual(
                    [(wd, mask, name) for wd, mask, name in removed_records
                     if wd == link_wd],
                    [(link_wd, module.IN_DELETE_SELF, b""),
                     (link_wd, module.IN_IGNORED, b"")],
                )
                self.assertFalse(module._classify_stream(
                    removed, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(fd), b"")
                invalidated_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, removed,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(invalidated_verdict["status"], "BLOCKED")
                self.assertIs(invalidated_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    invalidated_verdict["independent_os_proof_verified"], False
                )

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
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in records(restored)
                ))
                self.assertFalse(any(
                    wd == link_wd for wd, mask, name in records(restored)
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")

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
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
