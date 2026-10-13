from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec980", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native IN_ONLYDIR requires Linux")
class NativeOnlydirSymlinkFollowRegression(unittest.TestCase):
    def test_real_onlydir_follows_directory_symlink_unless_nofollow(self):
        alias_fd = None
        original_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            result = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(stream) - pos)
                name = stream[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec980-public-follow-directory-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            alias = Path(tmp) / "public-parent-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                alias.symlink_to(sample.parent, target_is_directory=True)
                creation = module._read_receipt_pending(original_fd)
                self.assertTrue(module._classify_stream(
                    creation, source_wd, parent_wd
                )["well_formed"])
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_CREATE
                    and name == b"public-parent-alias"
                    for wd, mask, name in records(creation)
                ))
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_init1.argtypes = [module.ctypes.c_int]
                lib.inotify_init1.restype = module.ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                alias_fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(alias_fd, 2)

                # Positive path: IN_ONLYDIR follows the alias's real parent.
                followed_wd = lib.inotify_add_watch(
                    alias_fd, module._checked_watch_path_bytes(alias),
                    module.IN_CREATE | module.IN_DELETE | module.IN_ONLYDIR,
                )
                self.assertGreater(followed_wd, 0)
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")

                # Same symlink, but NOFOLLOW checks the symlink inode itself.
                module.ctypes.set_errno(0)
                refused = lib.inotify_add_watch(
                    alias_fd, module._checked_watch_path_bytes(alias),
                    module.IN_CREATE | module.IN_DELETE | module.IN_ONLYDIR
                    | module.IN_DONT_FOLLOW,
                )
                self.assertEqual(refused, -1)
                self.assertEqual(module.ctypes.get_errno(), errno.ENOTDIR)
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")

                sibling = sample.parent / "public-followed-child"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-SIBLING"),
                                 len(b"PUBLIC-SIBLING"))
                created = module._read_receipt_pending(alias_fd)
                self.assertEqual(records(created), [
                    (followed_wd, module.IN_CREATE, b"public-followed-child")
                ])
                self.assertTrue(module._classify_stream(
                    module._read_receipt_pending(original_fd),
                    source_wd, parent_wd
                )["well_formed"])
                os.unlink(sibling)
                removed = module._read_receipt_pending(alias_fd)
                self.assertEqual(records(removed), [
                    (followed_wd, module.IN_DELETE, b"public-followed-child")
                ])
                self.assertTrue(module._classify_stream(
                    module._read_receipt_pending(original_fd),
                    source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                # The followed parent watch is still alive; it just does
                # not subscribe to content writes. Original dual WDs do.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                    stream = module._read_receipt_pending(original_fd)
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    self.assertTrue(any(
                        wd == parent_wd and mask & module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in records(stream)
                    ))
                    verdict = module._evaluate(
                        module.BEFORE, content, stream, source_wd, True, False,
                        directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                    self.assertEqual(module._read_receipt_pending(original_fd), b"")

                os.unlink(alias)
                # Alias removal is a directory entry mutation, not removal
                # of the followed parent inode or its live watch.
                original_alias_delete = module._read_receipt_pending(original_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_DELETE
                    and name == b"public-parent-alias"
                    for wd, mask, name in records(original_alias_delete)
                ))
                # The followed watch remains attached to the parent
                # inode, including the parent entry for this very alias.
                # Unlinking the pathname must therefore generate native
                # IN_DELETE on BOTH independently registered parent watches.
                followed_alias_delete = module._read_receipt_pending(alias_fd)
                self.assertEqual(records(followed_alias_delete), [
                    (followed_wd, module.IN_DELETE, b"public-parent-alias")
                ])
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino, parent_final.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (alias_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
