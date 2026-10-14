from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1051", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux one-shot deletion required")
class NativeParentDeleteOneshotRegression(unittest.TestCase):
    def test_create_and_write_do_not_disarm_delete_only_parent_oneshot(self):
        parent_only_fd = None
        independent_fd = None

        def records(raw):
            self.assertIs(type(raw), bytes)
            events = []
            offset = 0
            while offset < len(raw):
                self.assertGreaterEqual(len(raw) - offset, module.EVENT.size)
                wd, mask, cookie, size = module.EVENT.unpack_from(raw, offset)
                offset += module.EVENT.size
                self.assertLessEqual(size, len(raw) - offset)
                name = raw[offset:offset + size].split(b"\x00", 1)[0]
                offset += size
                self.assertEqual(cookie, 0)
                events.append((wd, mask, name))
            self.assertEqual(offset, len(raw))
            return events

        def write_file(path, payload):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(payload), len(payload))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        with tempfile.TemporaryDirectory(
            prefix="dec1051-public-parent-delete-oneshot-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            original = os.lstat(sample)
            parent_original = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                independent_fd, source_wd, independent_parent_wd = (
                    module._start_watch(sample)
                )
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                parent_only_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(parent_only_fd, 2)
                delete_wd = libc.inotify_add_watch(
                    parent_only_fd,
                    module._checked_watch_path_bytes(sample.parent),
                    module.IN_DELETE | module.IN_ONLYDIR
                    | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(delete_wd, 0)
                self.assertNotEqual(parent_only_fd, independent_fd)
                self.assertEqual(module._read_receipt_pending(parent_only_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # CREATE (and child write/close) do not match a
                # parent IN_DELETE-only one-shot. The watch remains
                # armed and its native queue stays genuinely empty.
                sibling = sample.parent / "public-first-sibling"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-SIBLING"),
                                 len(b"PUBLIC-SIBLING"))
                self.assertEqual(module._read_receipt_pending(parent_only_fd), b"")
                created = module._read_receipt_pending(independent_fd)
                self.assertIn(
                    (independent_parent_wd, module.IN_CREATE,
                     b"public-first-sibling"), records(created)
                )
                created_parse = module._classify_stream(
                    created, source_wd, independent_parent_wd
                )
                self.assertTrue(created_parse["well_formed"])
                self.assertGreaterEqual(created_parse["directory_changes"], 1)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Two actual source-byte writes are also nonmatching
                # events: the parent-only DELETE watch stays quiet
                # while independent source+parent observes both.
                for payload in (module.AFTER, module.BEFORE):
                    write_file(sample, payload)
                    self.assertEqual(module._read_receipt_pending(parent_only_fd), b"")
                    observed = module._read_receipt_pending(independent_fd)
                    native = records(observed)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in native
                    ))
                    self.assertTrue(any(
                        wd == independent_parent_wd
                        and mask == module.IN_MODIFY and name == b"sample"
                        for wd, mask, name in native
                    ))
                    verdict = module._evaluate(
                        module.BEFORE, payload, observed, source_wd,
                        True, False, directory_watch=independent_parent_wd,
                        directory_inventory_names=(
                            "public-first-sibling", "sample"
                        ),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(
                        module._read_receipt_pending(independent_fd), b""
                    )

                # Only the FIRST matching deletion triggers the
                # one-shot: the real parent name is followed by
                # kernel IN_IGNORED auto-watch invalidation.
                os.unlink(sibling)
                trigger = module._read_receipt_pending(parent_only_fd)
                self.assertEqual(records(trigger), [
                    (delete_wd, module.IN_DELETE, b"public-first-sibling"),
                    (delete_wd, module.IN_IGNORED, b""),
                ])
                self.assertEqual(module._read_receipt_pending(parent_only_fd), b"")
                independent_delete = module._read_receipt_pending(independent_fd)
                self.assertIn(
                    (independent_parent_wd, module.IN_DELETE,
                     b"public-first-sibling"),
                    records(independent_delete)
                )
                self.assertFalse(any(
                    mask == module.IN_IGNORED
                    for wd, mask, name in records(independent_delete)
                ))
                delete_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE,
                    independent_delete, source_wd,
                    True, False, directory_watch=independent_parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(delete_verdict["status"], "BLOCKED")
                self.assertIs(delete_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    delete_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Genuine later parent activity remains invisible to
                # disarmed one-shot, but the independent parent
                # supplies both real CREATE and DELETE records.
                later = sample.parent / "public-later-sibling"
                self.assertEqual(later.write_bytes(b"PUBLIC-LATER"),
                                 len(b"PUBLIC-LATER"))
                os.unlink(later)
                self.assertEqual(module._read_receipt_pending(parent_only_fd), b"")
                second = records(module._read_receipt_pending(independent_fd))
                self.assertIn(
                    (independent_parent_wd, module.IN_CREATE,
                     b"public-later-sibling"), second
                )
                self.assertIn(
                    (independent_parent_wd, module.IN_DELETE,
                     b"public-later-sibling"), second
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent), ("sample",)
                )

                last = os.lstat(sample)
                last_parent = os.lstat(sample.parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (original.st_dev, original.st_ino, original.st_mode)
                )
                self.assertEqual(
                    (last_parent.st_dev, last_parent.st_ino,
                     last_parent.st_mode),
                    (parent_original.st_dev, parent_original.st_ino,
                     parent_original.st_mode)
                )
            finally:
                for fd in (parent_only_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
