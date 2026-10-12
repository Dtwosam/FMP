from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec981", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Linux UAPI bits. The unchanged observer intentionally does NOT accept IN_OPEN.
IN_OPEN = 0x00000020
IN_MASK_ADD = 0x20000000


@unittest.skipUnless(sys.platform == "linux", "parent IN_MASK_ADD is Linux-only")
class NativeParentAdditiveOpenRegression(unittest.TestCase):
    def test_real_parent_add_open_preserves_writes_and_namespace_subscriptions(self):
        fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            output = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, n = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(n, len(stream) - pos)
                name = stream[pos:pos + n].split(b"\x00", 1)[0]
                pos += n
                self.assertEqual(cookie, 0)
                output.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return output

        with tempfile.TemporaryDirectory(
            prefix="dec981-public-parent-mask-add-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int

                # Unlike mask replacement in DEC-966, IN_MASK_ADD retains
                # the original parent CREATE/DELETE/MODIFY/CLOSE_WRITE bits.
                same_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(sample.parent),
                    IN_OPEN | IN_MASK_ADD | module.IN_DONT_FOLLOW |
                    module.IN_ONLYDIR,
                )
                self.assertEqual(same_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # A directory self-open is reported with IN_ISDIR as a
                # native modifier. This new action is outside the current
                # observer's accepted event parser.
                directory_fd = os.open(
                    sample.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC
                )
                os.close(directory_fd)
                directory_open = module._read_receipt_pending(fd)
                self.assertEqual(records(directory_open), [
                    (parent_wd, IN_OPEN | module.IN_ISDIR, b"")
                ])
                self.assertFalse(module._classify_stream(
                    directory_open, source_wd, parent_wd
                )["well_formed"])
                local = module._evaluate(
                    module.BEFORE, module.BEFORE, directory_open,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(local["status"], "BLOCKED")
                self.assertIs(local["can_authorize_dispatch"], False)
                self.assertIs(local["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                sibling = sample.parent / "public-added-parent-open"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-SIBLING"),
                                 len(b"PUBLIC-SIBLING"))
                created = module._read_receipt_pending(fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_CREATE
                    and name == b"public-added-parent-open"
                    for wd, mask, name in records(created)
                ))
                os.unlink(sibling)
                deleted = module._read_receipt_pending(fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_DELETE
                    and name == b"public-added-parent-open"
                    for wd, mask, name in records(deleted)
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Parent still gets named sample events. Added IN_OPEN on
                # its parent also observes the child's actual open, and
                # the unchanged parser must not silently discard it.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    stream = module._read_receipt_pending(fd)
                    events = records(stream)
                    self.assertTrue(any(
                        wd == parent_wd and mask == IN_OPEN
                        and name == b"sample"
                        for wd, mask, name in events
                    ))
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in events
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in events
                    ))
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_CLOSE_WRITE
                        for wd, mask, name in events
                    ))
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertFalse(parsed["well_formed"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    self.assertEqual(module._read_receipt_pending(fd), b"")
                    verdict = module._evaluate(
                        module.BEFORE, content, stream,
                        source_wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                # read_bytes() itself opens the sample and is visible to
                # parent IN_OPEN even though it is not a write.
                read_open = module._read_receipt_pending(fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == IN_OPEN and name == b"sample"
                    for wd, mask, name in records(read_open)
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")

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
