from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1021", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native WD namespaces require Linux")
class NativeCrossInstanceDescriptorRoleCollisionRegression(unittest.TestCase):
    def test_source_wd_integer_in_other_instance_can_name_parent_watch(self):
        primary_fd = None
        reverse_fd = None

        def records(raw):
            self.assertIs(type(raw), bytes)
            pos = 0
            parsed = []
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

        with tempfile.TemporaryDirectory(
            prefix="dec1021-public-cross-instance-wd-role-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first_stat = os.lstat(sample)
            parent_stat = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                primary_fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")

                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                libc.inotify_rm_watch.argtypes = [
                    ctypes.c_int, ctypes.c_int
                ]
                libc.inotify_rm_watch.restype = ctypes.c_int

                # A GENUINELY independent instance reverses registration
                # order: its first WD belongs to the PARENT, not source.
                reverse_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(reverse_fd, 2)
                self.assertNotEqual(reverse_fd, primary_fd)
                reverse_parent_wd = libc.inotify_add_watch(
                    reverse_fd,
                    module._checked_watch_path_bytes(sample.parent),
                    module.DIRECTORY_MASK | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW,
                )
                reverse_source_wd = libc.inotify_add_watch(
                    reverse_fd, module._checked_watch_path_bytes(sample),
                    module.MASK | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(reverse_parent_wd, 0)
                self.assertGreater(reverse_source_wd, 0)
                self.assertEqual(reverse_parent_wd, source_wd)
                self.assertEqual(reverse_source_wd, parent_wd)
                self.assertNotEqual(reverse_parent_wd, reverse_source_wd)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(reverse_fd), b"")

                # Passing the PRIMARY SOURCE WD integer alongside the
                # SECOND instance FD removes SECOND PARENT, not source.
                self.assertEqual(
                    libc.inotify_rm_watch(reverse_fd, source_wd), 0
                )
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                invalidated = module._read_receipt_pending(reverse_fd)
                self.assertEqual(records(invalidated), [
                    (reverse_parent_wd, module.IN_IGNORED, b"")
                ])
                self.assertTrue(module._classify_stream(
                    invalidated, reverse_source_wd, reverse_parent_wd
                )["invalidated"])
                self.assertEqual(module._read_receipt_pending(reverse_fd), b"")

                # Real transient sibling entry activity appears on the
                # original parent's WD but NOT on the second instance
                # whose parent was accidentally removed.
                sibling = sample.parent / "public-reversed-wd-sibling"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-SIBLING"),
                                 len(b"PUBLIC-SIBLING"))
                os.unlink(sibling)
                primary_siblings = module._read_receipt_pending(primary_fd)
                sibling_records = records(primary_siblings)
                for mask in (module.IN_CREATE, module.IN_DELETE):
                    self.assertIn(
                        (parent_wd, mask, b"public-reversed-wd-sibling"),
                        sibling_records,
                    )
                self.assertTrue(module._classify_stream(
                    primary_siblings, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(reverse_fd), b"")
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")

                # A real write/restore still reaches both source inodes.
                # Only the first instance retains the named parent census;
                # the second retains just a source-WD subscription.
                for payload in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(payload), len(payload))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    full = module._read_receipt_pending(primary_fd)
                    full_records = records(full)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in full_records
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample" for wd, mask, name in full_records
                    ))
                    full_parse = module._classify_stream(
                        full, source_wd, parent_wd
                    )
                    self.assertTrue(full_parse["well_formed"])
                    self.assertFalse(full_parse["invalidated"])
                    self.assertGreaterEqual(full_parse["source_modify_events"], 1)

                    source_only = module._read_receipt_pending(reverse_fd)
                    source_records = records(source_only)
                    self.assertTrue(any(
                        wd == reverse_source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in source_records
                    ))
                    self.assertFalse(any(
                        wd == reverse_parent_wd for wd, mask, name in source_records
                    ))
                    partial = module._classify_stream(
                        source_only, reverse_source_wd, reverse_parent_wd
                    )
                    self.assertTrue(partial["well_formed"])
                    self.assertGreaterEqual(partial["source_modify_events"], 1)

                    for stream, swd, pwd in (
                        (full, source_wd, parent_wd),
                        (source_only, reverse_source_wd, reverse_parent_wd),
                    ):
                        verdict = module._evaluate(
                            module.BEFORE, payload, stream, swd,
                            True, False, directory_watch=pwd,
                            directory_inventory_names=("sample",),
                        )
                        self.assertEqual(verdict["status"], "BLOCKED")
                        self.assertIs(verdict["can_authorize_dispatch"], False)
                        self.assertIs(
                            verdict["independent_os_proof_verified"], False
                        )
                    self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                    self.assertEqual(module._read_receipt_pending(reverse_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                final_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (first_stat.st_dev, first_stat.st_ino, first_stat.st_mode),
                )
                self.assertEqual(
                    (final_parent.st_dev, final_parent.st_ino,
                     final_parent.st_mode),
                    (parent_stat.st_dev, parent_stat.st_ino, parent_stat.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (reverse_fd, primary_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
