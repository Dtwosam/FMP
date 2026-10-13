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
spec = importlib.util.spec_from_file_location("dec677_native_dec1045", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native inotify only")
class NativeInotifyAttributeCoalescingRegression(unittest.TestCase):
    def test_six_real_chmods_coalesce_to_one_source_only_attrib(self):
        source_only_fd = None
        dual_fd = None

        def records(raw):
            self.assertIs(type(raw), bytes)
            pos = 0
            result = []
            while pos < len(raw):
                self.assertGreaterEqual(len(raw) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(raw, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(raw) - pos)
                name = raw[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                result.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(raw))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1045-public-attribute-coalescing-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            os.chmod(sample, 0o600)
            original = os.lstat(sample)
            parent_original = os.lstat(sample.parent)
            self.assertEqual(stat.S_IMODE(original.st_mode), 0o600)
            self.assertEqual(
                module._bounded_inventory_names(sample.parent), ("sample",)
            )
            try:
                dual_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                source_only_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(source_only_fd, 2)
                only_wd = libc.inotify_add_watch(
                    source_only_fd, module._checked_watch_path_bytes(sample),
                    module.IN_ATTRIB | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(only_wd, 0)
                self.assertEqual(module._read_receipt_pending(dual_fd), b"")
                self.assertEqual(
                    module._read_receipt_pending(source_only_fd), b""
                )

                # SIX real permission changes in ONE unread interval:
                # no files opened, no generated public content modified.
                # Restore original mode at end of sixth chmod.
                for mode in (0o640, 0o600, 0o640,
                             0o600, 0o640, 0o600):
                    os.chmod(sample, mode)
                    self.assertEqual(
                        stat.S_IMODE(os.lstat(sample).st_mode), mode
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    stat.S_IMODE(os.lstat(sample).st_mode), 0o600
                )

                # Consecutive unread source-only IN_ATTRIB records are
                # COALESCED by genuine Linux inotify into one record.
                source_only = module._read_receipt_pending(source_only_fd)
                self.assertEqual(records(source_only), [
                    (only_wd, module.IN_ATTRIB, 0, b"")
                ])
                parsed = module._classify_stream(source_only, only_wd)
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertEqual(parsed["source_attribute_events"], 1)
                self.assertEqual(parsed["source_modify_events"], 0)
                self.assertEqual(
                    module._read_receipt_pending(source_only_fd), b""
                )
                lone_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE,
                    source_only, only_wd, True, False,
                )
                self.assertEqual(lone_verdict["status"], "BLOCKED")
                self.assertIs(lone_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    lone_verdict["independent_os_proof_verified"], False
                )

                # The independent DUAL observer sees named parent and
                # source IN_ATTRIB for each chmod, so the source events
                # aren't adjacent and do not coalesce on its queue.
                independent = module._read_receipt_pending(dual_fd)
                native = records(independent)
                self.assertGreaterEqual(sum(
                    event == (source_wd, module.IN_ATTRIB, 0, b"")
                    for event in native
                ), 6)
                self.assertGreaterEqual(sum(
                    event == (parent_wd, module.IN_ATTRIB, 0, b"sample")
                    for event in native
                ), 6)
                parsed_independent = module._classify_stream(
                    independent, source_wd, parent_wd
                )
                self.assertTrue(parsed_independent["well_formed"])
                self.assertFalse(parsed_independent["invalidated"])
                self.assertGreaterEqual(
                    parsed_independent["source_attribute_events"], 6
                )
                self.assertEqual(
                    parsed_independent["source_modify_events"], 0
                )
                full_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, independent,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(full_verdict["status"], "BLOCKED")
                self.assertIs(full_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    full_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(dual_fd), b"")

                # Contrast with draining after each genuine chmod:
                # identical source-only event masks become separate
                # observable IN_ATTRIB records across queue reads.
                for mode in (0o640, 0o600):
                    os.chmod(sample, mode)
                    self.assertEqual(stat.S_IMODE(os.lstat(sample).st_mode),
                                     mode)
                    self.assertEqual(
                        records(module._read_receipt_pending(source_only_fd)),
                        [(only_wd, module.IN_ATTRIB, 0, b"")],
                    )
                    stream = module._read_receipt_pending(dual_fd)
                    dual_records = records(stream)
                    self.assertIn(
                        (source_wd, module.IN_ATTRIB, 0, b""),
                        dual_records,
                    )
                    self.assertIn(
                        (parent_wd, module.IN_ATTRIB, 0, b"sample"),
                        dual_records,
                    )
                    decision = module._evaluate(
                        module.BEFORE, module.BEFORE, stream,
                        source_wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(decision["status"], "BLOCKED")
                    self.assertIs(decision["can_authorize_dispatch"], False)
                    self.assertIs(
                        decision["independent_os_proof_verified"], False
                    )
                    self.assertEqual(
                        module._read_receipt_pending(source_only_fd), b""
                    )
                    self.assertEqual(module._read_receipt_pending(dual_fd), b"")

                last = os.lstat(sample)
                parent_last = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (original.st_dev, original.st_ino, original.st_mode),
                )
                self.assertEqual(
                    (parent_last.st_dev, parent_last.st_ino,
                     parent_last.st_mode),
                    (parent_original.st_dev, parent_original.st_ino,
                     parent_original.st_mode),
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent), ("sample",)
                )
            finally:
                if sample.exists():
                    os.chmod(sample, 0o600)
                for fd in (source_only_fd, dual_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
