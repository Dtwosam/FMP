from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec995", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_MASK_CREATE = 0x10000000  # Linux inotify registration-only option.


@unittest.skipUnless(sys.platform == "linux", "native symlink target materialization is Linux-only")
class NativeDanglingSymlinkMaterializationRegression(unittest.TestCase):
    def test_nofollow_watch_does_not_retarget_when_missing_target_appears(self):
        fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            result = []
            pos = 0
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, n = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(n, len(stream) - pos)
                name = stream[pos:pos + n].split(b"\x00", 1)[0]
                pos += n
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec995-public-link-target-appears-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            target = sample.parent / "public-late-target"
            alias = sample.parent / "public-dangling-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            first_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                alias.symlink_to("public-late-target")
                self.assertFalse(alias.exists())
                alias_create = module._read_receipt_pending(fd)
                self.assertIn(
                    (parent_wd, module.IN_CREATE, b"public-dangling-alias"),
                    records(alias_create),
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int

                link_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(alias),
                    IN_MASK_CREATE | module.IN_DONT_FOLLOW |
                    module.IN_DELETE_SELF,
                )
                self.assertGreater(link_wd, 0)
                self.assertNotIn(link_wd, (source_wd, parent_wd))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # The target was absent when the symlink inode watch
                # registered. Creating it later cannot magically
                # convert this WD into a watch on the new target.
                original_target = b"PUBLIC-TARGET-ONE"
                changed_target = b"PUBLIC-TARGET-TWO"
                self.assertEqual(target.write_bytes(original_target),
                                 len(original_target))
                creation = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE, b"public-late-target"),
                    creation,
                )
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"public-late-target"
                    for wd, mask, name in creation
                ))
                self.assertFalse(any(wd == link_wd for wd, mask, name in creation))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertTrue(alias.exists())
                with alias.open("r+b") as writer:
                    self.assertEqual(writer.write(changed_target),
                                     len(changed_target))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                target_write = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_MODIFY, b"public-late-target"),
                    target_write,
                )
                self.assertFalse(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"public-dangling-alias"
                    for wd, mask, name in target_write
                ))
                self.assertFalse(any(
                    wd in (source_wd, link_wd) for wd, mask, name in target_write
                ))
                self.assertEqual(target.read_bytes(), changed_target)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                os.unlink(alias)
                unlink_stream = module._read_receipt_pending(fd)
                unlink_events = records(unlink_stream)
                self.assertIn(
                    (parent_wd, module.IN_DELETE, b"public-dangling-alias"),
                    unlink_events,
                )
                self.assertEqual(
                    [(wd, mask, name) for wd, mask, name in unlink_events
                     if wd == link_wd],
                    [(link_wd, module.IN_DELETE_SELF, b""),
                     (link_wd, module.IN_IGNORED, b"")],
                )
                self.assertFalse(module._classify_stream(
                    unlink_stream, source_wd, parent_wd
                )["well_formed"])
                verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, unlink_stream,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                os.unlink(target)
                target_remove = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, b"public-late-target"),
                    target_remove,
                )
                self.assertFalse(any(
                    wd == link_wd for wd, mask, name in target_remove
                ))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                for value in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(value), len(value))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    original_events = module._read_receipt_pending(fd)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in records(original_events)
                    ))
                    parsed = module._classify_stream(
                        original_events, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    original_verdict = module._evaluate(
                        module.BEFORE, value, original_events, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(original_verdict["status"], "BLOCKED")
                    self.assertIs(original_verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        original_verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                last_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (last_parent.st_dev, last_parent.st_ino, last_parent.st_mode),
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
