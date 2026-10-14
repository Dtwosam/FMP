from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1058", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native parent attribute one-shot requires Linux")
class NativeParentAttributeOneShotRegression(unittest.TestCase):
    def test_parent_attrib_oneshot_ignores_child_write_until_dir_chmod_isdir(self):
        one_fd = None
        independent_fd = None

        def records(raw):
            self.assertIs(type(raw), bytes)
            parsed = []
            pos = 0
            while pos < len(raw):
                self.assertGreaterEqual(len(raw) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(raw, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(raw) - pos)
                name = raw[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(pos, len(raw))
            return parsed

        def write(path, payload):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(payload), len(payload))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        with tempfile.TemporaryDirectory(
            prefix="dec1058-public-parent-attrib-isdir-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            source_initial = os.lstat(sample)
            parent_initial = os.lstat(parent)
            original_mode = stat.S_IMODE(parent_initial.st_mode)
            # Toggle only group-write permission on the *public
            # temporary directory*; keep the owner's rwx privileges.
            altered_mode = original_mode ^ stat.S_IWGRP
            self.assertNotEqual(original_mode, altered_mode)
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            try:
                independent_fd, source_wd, parent_wd = (
                    module._start_watch(sample)
                )
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                one_parent_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_ATTRIB | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_parent_wd, 0)
                for fd in (one_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Actual CHILD content writes have IN_MODIFY and
                # IN_CLOSE_WRITE, not parent-inode IN_ATTRIB. They
                # must NOT consume the parent one-shot.
                for payload in (module.AFTER, module.BEFORE):
                    write(sample, payload)
                    self.assertEqual(module._read_receipt_pending(one_fd), b"")
                    independent = module._read_receipt_pending(independent_fd)
                    native = records(independent)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in native
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in native
                    ))
                    result = module._evaluate(
                        module.BEFORE, payload, independent,
                        source_wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertIs(result["can_authorize_dispatch"], False)
                    self.assertIs(
                        result["independent_os_proof_verified"], False
                    )
                    self.assertEqual(
                        module._read_receipt_pending(independent_fd), b""
                    )

                # First MATCHING event is actual metadata change on
                # the watched PARENT inode itself. Linux marks it with
                # IN_ISDIR and auto-removes the one-shot subscription.
                os.chmod(parent, altered_mode)
                self.assertEqual(stat.S_IMODE(os.lstat(parent).st_mode),
                                 altered_mode)
                triggered = module._read_receipt_pending(one_fd)
                self.assertEqual(records(triggered), [
                    (one_parent_wd, module.IN_ATTRIB | module.IN_ISDIR, b""),
                    (one_parent_wd, module.IN_IGNORED, b""),
                ])
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                witness = module._read_receipt_pending(independent_fd)
                self.assertIn(
                    (parent_wd, module.IN_ATTRIB | module.IN_ISDIR, b""),
                    records(witness),
                )
                self.assertFalse(any(
                    mask == module.IN_IGNORED
                    for wd, mask, name in records(witness)
                ))
                self.assertTrue(module._classify_stream(
                    witness, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Restoring original DIRECTORY permissions is a real
                # second metadata change, invisible to disarmed
                # one-shot but visible to independent parent watch.
                os.chmod(parent, original_mode)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                independent_again = records(
                    module._read_receipt_pending(independent_fd)
                )
                self.assertIn(
                    (parent_wd, module.IN_ATTRIB | module.IN_ISDIR, b""),
                    independent_again,
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                source_final = os.lstat(sample)
                parent_final = os.lstat(parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (source_final.st_dev, source_final.st_ino,
                     source_final.st_mode),
                    (source_initial.st_dev, source_initial.st_ino,
                     source_initial.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino,
                     parent_final.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                # Restore only disposable public parent metadata, even
                # if an assertion above fails before normal cleanup.
                os.chmod(parent, original_mode)
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
