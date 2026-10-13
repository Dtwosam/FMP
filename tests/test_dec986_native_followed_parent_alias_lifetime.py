from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec986", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native inotify symlink lifetime is Linux-only")
class NativeDirectorySymlinkLifetimeRegression(unittest.TestCase):
    def test_followed_parent_survives_alias_unlink_nofollow_alias_invalidates(self):
        ordinary_fd = None
        followed_fd = None
        link_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            out = []
            offset = 0
            while offset < len(stream):
                self.assertGreaterEqual(len(stream) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(stream, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(stream) - offset)
                name = stream[offset:offset + nbytes].split(b"\0", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                out.append((wd, mask, name))
            self.assertEqual(offset, len(stream))
            return out

        with tempfile.TemporaryDirectory(
            prefix="dec986-public-followed-parent-lifetime-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            alias = Path(tmp) / "public-directory-symlink"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                ordinary_fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(ordinary_fd), b"")
                alias.symlink_to(sample.parent, target_is_directory=True)
                creation = module._read_receipt_pending(ordinary_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_CREATE
                    and name == b"public-directory-symlink"
                    for wd, mask, name in records(creation)
                ))
                self.assertEqual(module._read_receipt_pending(ordinary_fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_init1.argtypes = [module.ctypes.c_int]
                lib.inotify_init1.restype = module.ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                followed_fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                link_fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(followed_fd, 2)
                self.assertGreater(link_fd, 2)

                # One instance follows the symlink to its real parent.
                # The other instance watches the link inode itself.
                followed_wd = lib.inotify_add_watch(
                    followed_fd, module._checked_watch_path_bytes(alias),
                    module.IN_CREATE | module.IN_DELETE | module.IN_ONLYDIR,
                )
                link_wd = lib.inotify_add_watch(
                    link_fd, module._checked_watch_path_bytes(alias),
                    module.IN_DELETE_SELF | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(followed_wd, 0)
                self.assertGreater(link_wd, 0)
                for fd in (followed_fd, link_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                os.unlink(alias)
                ordinary_delete = module._read_receipt_pending(ordinary_fd)
                followed_delete = module._read_receipt_pending(followed_fd)
                link_delete = module._read_receipt_pending(link_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_DELETE
                    and name == b"public-directory-symlink"
                    for wd, mask, name in records(ordinary_delete)
                ))
                self.assertEqual(records(followed_delete), [
                    (followed_wd, module.IN_DELETE, b"public-directory-symlink")
                ])
                self.assertEqual(records(link_delete), [
                    (link_wd, module.IN_DELETE_SELF, b""),
                    (link_wd, module.IN_IGNORED, b""),
                ])
                self.assertEqual(module._read_receipt_pending(ordinary_fd), b"")
                self.assertEqual(module._read_receipt_pending(followed_fd), b"")
                self.assertEqual(module._read_receipt_pending(link_fd), b"")

                # The original alias pathname no longer exists. Nonetheless
                # the followed watch remains attached to the parent inode,
                # while the nofollow link watch has been auto-invalidated.
                sibling = sample.parent / "public-sibling-after-alias-removal"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-AFTER"),
                                 len(b"PUBLIC-AFTER"))
                follow_create = module._read_receipt_pending(followed_fd)
                self.assertEqual(records(follow_create), [
                    (followed_wd, module.IN_CREATE,
                     b"public-sibling-after-alias-removal")
                ])
                self.assertTrue(module._classify_stream(
                    module._read_receipt_pending(ordinary_fd),
                    source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(link_fd), b"")
                os.unlink(sibling)
                follow_remove = module._read_receipt_pending(followed_fd)
                self.assertEqual(records(follow_remove), [
                    (followed_wd, module.IN_DELETE,
                     b"public-sibling-after-alias-removal")
                ])
                self.assertTrue(module._classify_stream(
                    module._read_receipt_pending(ordinary_fd),
                    source_wd, parent_wd
                )["well_formed"])
                for fd in (ordinary_fd, followed_fd, link_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Parent followed-watches have only directory-entry masks.
                # A separate original source+parent instance sees true
                # content writes and remains fail-closed.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    self.assertEqual(module._read_receipt_pending(followed_fd), b"")
                    self.assertEqual(module._read_receipt_pending(link_fd), b"")
                    stream = module._read_receipt_pending(ordinary_fd)
                    parsed = module._classify_stream(stream, source_wd, parent_wd)
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    verdict = module._evaluate(
                        module.BEFORE, content, stream,
                        source_wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                    self.assertEqual(module._read_receipt_pending(ordinary_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                final_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
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
                for fd in (link_fd, followed_fd, ordinary_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
