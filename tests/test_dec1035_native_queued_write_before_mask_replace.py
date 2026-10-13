from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1035", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020


@unittest.skipUnless(sys.platform == "linux", "native Linux watch masks required")
class NativePendingWriteThenSourceMaskReplacement(unittest.TestCase):
    def test_queued_write_survives_mask_change_but_later_writes_lose_source_modify(self):
        primary_fd = None
        alias_fd = None
        independent_fd = None

        def records(raw):
            self.assertIs(type(raw), bytes)
            offset = 0
            result = []
            while offset < len(raw):
                self.assertGreaterEqual(len(raw) - offset, module.EVENT.size)
                wd, mask, cookie, n = module.EVENT.unpack_from(raw, offset)
                offset += module.EVENT.size
                self.assertLessEqual(n, len(raw) - offset)
                name = raw[offset:offset + n].split(b"\x00", 1)[0]
                offset += n
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(offset, len(raw))
            return result

        def write(path, data):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(data), len(data))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        with tempfile.TemporaryDirectory(
            prefix="dec1035-public-prequeued-mask-change-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            start = os.lstat(sample)
            parent_start = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent), ("sample",))
            try:
                primary_fd, source_wd, parent_wd = module._start_watch(sample)
                alias_fd = os.dup(primary_fd)
                independent_fd, other_source_wd, other_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(len({primary_fd, alias_fd, independent_fd}), 3)
                for fd in (primary_fd, alias_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # A genuine write queues original source IN_MODIFY and
                # IN_CLOSE_WRITE while its full mask is still installed.
                # Do not drain either shared FD before replacing mask.
                write(sample, module.AFTER)

                lib = ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                lib.inotify_add_watch.restype = ctypes.c_int
                path = module._checked_watch_path_bytes(sample)
                replaced = lib.inotify_add_watch(
                    alias_fd, path, IN_OPEN | module.IN_DONT_FOLLOW
                )
                self.assertEqual(replaced, source_wd)

                # Changing mask doesn't discard already queued writes or
                # emit IN_IGNORED; it also keeps SAME source WD integer.
                old = module._read_receipt_pending(primary_fd)
                early = records(old)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, _ in early
                ))
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_CLOSE_WRITE
                    for wd, mask, _ in early
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in early
                ))
                self.assertFalse(any(
                    mask == module.IN_IGNORED for _, mask, _ in early
                ))
                self.assertTrue(module._classify_stream(
                    old, source_wd, parent_wd
                )["well_formed"])
                first_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, old,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",)
                )
                self.assertEqual(first_verdict["status"], "BLOCKED")
                self.assertIs(first_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    first_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")

                first_independent = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    first_independent, other_source_wd, other_parent_wd
                )["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # A SECOND real public write occurs DURING the reduced
                # source IN_OPEN-only mask. Its source MODIFY is absent
                # even though parent still sees actual changed bytes.
                write(sample, module.BEFORE)
                later = module._read_receipt_pending(alias_fd)
                late_events = records(later)
                self.assertIn((source_wd, IN_OPEN, b""), late_events)
                self.assertFalse(any(
                    wd == source_wd and mask &
                    (module.IN_MODIFY | module.IN_CLOSE_WRITE)
                    for wd, mask, _ in late_events
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in late_events
                ))
                self.assertFalse(any(
                    mask == module.IN_IGNORED for _, mask, _ in late_events
                ))
                parsed_later = module._classify_stream(
                    later, source_wd, parent_wd
                )
                self.assertFalse(parsed_later["well_formed"])
                self.assertEqual(parsed_later["source_modify_events"], 0)
                gap_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, later,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",)
                )
                self.assertEqual(gap_verdict["status"], "BLOCKED")
                self.assertIs(gap_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    gap_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                second_independent = module._read_receipt_pending(independent_fd)
                second_native = records(second_independent)
                self.assertTrue(any(
                    wd == other_source_wd and mask == module.IN_MODIFY
                    for wd, mask, _ in second_native
                ))
                self.assertTrue(any(
                    wd == other_parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in second_native
                ))
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Reinstall full source mask (SAME WD) without replay.
                restored_wd = lib.inotify_add_watch(
                    primary_fd, path, module.MASK | module.IN_DONT_FOLLOW
                )
                self.assertEqual(restored_wd, source_wd)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                for content in (module.AFTER, module.BEFORE):
                    write(sample, content)
                    stream = module._read_receipt_pending(primary_fd)
                    event_records = records(stream)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, _ in event_records
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in event_records
                    ))
                    self.assertFalse(any(
                        mask == IN_OPEN for _, mask, _ in event_records
                    ))
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    verdict = module._evaluate(
                        module.BEFORE, content, stream, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",)
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                    independent_stream = module._read_receipt_pending(independent_fd)
                    self.assertGreaterEqual(module._classify_stream(
                        independent_stream, other_source_wd, other_parent_wd
                    )["source_modify_events"], 1)
                    self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                after = os.lstat(sample)
                after_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (after.st_dev, after.st_ino, after.st_mode),
                    (start.st_dev, start.st_ino, start.st_mode)
                )
                self.assertEqual(
                    (after_parent.st_dev, after_parent.st_ino, after_parent.st_mode),
                    (parent_start.st_dev, parent_start.st_ino, parent_start.st_mode)
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (independent_fd, alias_fd, primary_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
