from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec993", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_MASK_CREATE = 0x10000000  # Native Linux registration flag.


@unittest.skipUnless(sys.platform == "linux", "native symlink inotify is Linux-only")
class NativeResolvedSymlinkDentryRegression(unittest.TestCase):
    def test_real_symlink_write_uses_target_name_and_link_watch_is_separate(self):
        original_fd = None
        symlink_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            parsed = []
            index = 0
            while index < len(data):
                self.assertGreaterEqual(len(data) - index, module.EVENT.size)
                wd, mask, cookie, size = module.EVENT.unpack_from(data, index)
                index += module.EVENT.size
                self.assertLessEqual(size, len(data) - index)
                name = data[index:index + size].split(b"\x00", 1)[0]
                index += size
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(index, len(data))
            return parsed

        with tempfile.TemporaryDirectory(
            prefix="dec993-public-symlink-dentry-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            alias = sample.parent / "public-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            first_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                alias.symlink_to("sample")
                created = module._read_receipt_pending(original_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_CREATE
                    and name == b"public-alias"
                    for wd, mask, name in records(created)
                ))
                self.assertTrue(module._classify_stream(
                    created, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                # A distinct inotify instance observes only the SYMLINK
                # inode, never the regular-file target or its parent.
                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_init1.argtypes = [module.ctypes.c_int]
                lib.inotify_init1.restype = module.ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                symlink_fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(symlink_fd, 2)
                link_wd = lib.inotify_add_watch(
                    symlink_fd, module._checked_watch_path_bytes(alias),
                    IN_MASK_CREATE | module.IN_DELETE_SELF |
                    module.IN_DONT_FOLLOW,
                )
                self.assertGreater(link_wd, 0)
                self.assertEqual(module._read_receipt_pending(symlink_fd), b"")

                with alias.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                changed = module._read_receipt_pending(original_fd)
                kernel_events = records(changed)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY and not name
                    for wd, mask, name in kernel_events
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in kernel_events
                ))
                # The resolved target gets named file-write records. An
                # IN_MODIFY under the alias name would be the wrong inode.
                self.assertFalse(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"public-alias"
                    for wd, mask, name in kernel_events
                ))
                self.assertEqual(module._read_receipt_pending(symlink_fd), b"")
                observed = module._classify_stream(changed, source_wd, parent_wd)
                self.assertTrue(observed["well_formed"])
                self.assertFalse(observed["invalidated"])
                self.assertGreaterEqual(observed["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                verdict = module._evaluate(
                    module.BEFORE, module.AFTER, changed, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)

                os.unlink(alias)
                parent_deletion = module._read_receipt_pending(original_fd)
                link_deletion = module._read_receipt_pending(symlink_fd)
                self.assertIn(
                    (parent_wd, module.IN_DELETE, b"public-alias"),
                    records(parent_deletion),
                )
                self.assertEqual(records(link_deletion), [
                    (link_wd, module.IN_DELETE_SELF, b""),
                    (link_wd, module.IN_IGNORED, b""),
                ])
                self.assertTrue(module._classify_stream(
                    parent_deletion, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(symlink_fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                restored = module._read_receipt_pending(original_fd)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in records(restored)
                ))
                self.assertTrue(module._classify_stream(
                    restored, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(symlink_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

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
                for fd in (symlink_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
