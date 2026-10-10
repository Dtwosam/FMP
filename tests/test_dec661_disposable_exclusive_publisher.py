from __future__ import annotations

"""DEC-661 synthetic-only tests: no annual data, no GitHub, no trading."""

import importlib.util
from concurrent.futures import ThreadPoolExecutor
import threading
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec661_disposable_exclusive_publisher.py"
spec = importlib.util.spec_from_file_location("dec661_disposable", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExclusiveSyntheticPublicationTests(unittest.TestCase):
    def _dirfd(self, parent):
        return os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)

    def test_default_cli_is_inert_and_nonauthorizing(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT)],
                           capture_output=True, text=True, timeout=4, check=False)
        self.assertEqual(p.returncode, 2)
        r = json.loads(p.stdout)
        self.assertEqual(r["status"], "BLOCKED")
        self.assertFalse(r["can_authorize_dispatch"])
        self.assertFalse(r["independent_os_proof_verified"])

    def test_explicit_disposable_demo_still_never_authorizes(self):
        r = module.run_demo()
        self.assertEqual(r["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED", r)
        self.assertTrue(all(r["observed_checks"].values()))
        self.assertFalse(r["can_authorize_dispatch"])
        self.assertFalse(r["independent_os_proof_verified"])

    def test_cli_disposable_demo_nonzero_unverified(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT), "--execute-disposable-demo"],
                           capture_output=True, text=True, timeout=8, check=False)
        self.assertEqual(p.returncode, 3, p.stderr)
        self.assertEqual(json.loads(p.stdout)["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED")

    def test_create_exact_bytes_once_and_reject_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            try:
                module._publish_once(fd, b"first")
                self.assertEqual(module._read_report(fd), b"first")
                with self.assertRaises(FileExistsError):
                    module._publish_once(fd, b"second")
                self.assertEqual(module._read_report(fd), b"first")
                self.assertEqual(os.listdir(fd), [module.REPORT_NAME])
            finally:
                os.close(fd)

    def test_two_simultaneous_publishers_have_one_winner_no_overwrite(self):
        # A small disposable scheduling witness for atomic link-if-absent.
        # It does not cover hostile cross-namespace or privileged writers.
        for _ in range(8):
            with tempfile.TemporaryDirectory() as directory:
                barrier = threading.Barrier(2, timeout=5)
                payloads = (b"writer-a", b"writer-b")
                def contender(payload):
                    ownfd = self._dirfd(directory)
                    try:
                        barrier.wait()
                        try:
                            module._publish_once(ownfd, payload)
                        except FileExistsError:
                            return "collision"
                        return "published"
                    finally:
                        os.close(ownfd)
                with ThreadPoolExecutor(max_workers=2) as pool:
                    a = pool.submit(contender, payloads[0])
                    b = pool.submit(contender, payloads[1])
                    outcomes = sorted((a.result(timeout=8), b.result(timeout=8)))
                self.assertEqual(outcomes, ["collision", "published"])
                dirfd = self._dirfd(directory)
                try:
                    self.assertIn(module._read_report(dirfd), payloads)
                    self.assertEqual(os.listdir(dirfd), [module.REPORT_NAME])
                finally:
                    os.close(dirfd)

    def test_post_link_directory_fsync_failure_is_ambiguous_not_aborted(self):
        # The name exists even though the publisher reports a failure.
        # Never turn this into an automatic retry signal.
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            original_fsync = os.fsync
            try:
                def injected_fsync(target_fd):
                    if target_fd == fd:
                        raise OSError("synthetic post-link durability failure")
                    return original_fsync(target_fd)
                with patch.object(module.os, "fsync", side_effect=injected_fsync):
                    with self.assertRaises(module.PublicationOutcomeUnknown) as caught:
                        module._publish_once(fd, b"first-durable-unknown")
                self.assertIn("DO NOT RETRY", str(caught.exception))
                self.assertEqual(module._read_report(fd), b"first-durable-unknown")
                self.assertEqual(os.listdir(fd), [module.REPORT_NAME])
                with self.assertRaises(FileExistsError):
                    module._publish_once(fd, b"no second publication")
                self.assertEqual(module._read_report(fd), b"first-durable-unknown")
            finally:
                os.close(fd)

    def test_post_link_pending_cleanup_failure_is_ambiguous(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            unlink_real = os.unlink
            pending_name = None
            try:
                def fail_cleanup(path, *args, **kwargs):
                    if isinstance(path, str) and path.startswith(".pending-"):
                        raise OSError("synthetic pending cleanup failure")
                    return unlink_real(path, *args, **kwargs)
                with patch.object(module.os, "unlink", side_effect=fail_cleanup):
                    with self.assertRaises(module.PublicationOutcomeUnknown) as caught:
                        module._publish_once(fd, b"fully-linked-but-pending-left")
                self.assertIn("DO NOT RETRY", str(caught.exception))
                entries = os.listdir(fd)
                self.assertEqual(len(entries), 2)
                pending = [name for name in entries if name.startswith(".pending-")]
                self.assertEqual(len(pending), 1)
                pending_name = pending[0]
                self.assertEqual(module._read_report(fd), b"fully-linked-but-pending-left")
            finally:
                if pending_name is not None:
                    unlink_real(pending_name, dir_fd=fd)
                os.close(fd)

    def test_pre_link_file_fsync_failure_never_creates_final_report(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            original_fsync = os.fsync
            try:
                def injected_fsync(target_fd):
                    if target_fd != fd:
                        raise OSError("synthetic staged-file fsync failure")
                    return original_fsync(target_fd)
                with patch.object(module.os, "fsync", side_effect=injected_fsync):
                    with self.assertRaises(OSError) as caught:
                        module._publish_once(fd, b"not-published")
                self.assertNotIsInstance(caught.exception, module.PublicationOutcomeUnknown)
                self.assertEqual(os.listdir(fd), [])
            finally:
                os.close(fd)

    def test_post_link_error_does_not_change_authorization_contract(self):
        report = module._result(["final name linked; durability unknown"])
        self.assertEqual(report["status"], "BLOCKED")
        self.assertFalse(report["can_authorize_dispatch"])
        self.assertFalse(report["independent_os_proof_verified"])

    def test_directory_fsync_repeated_after_pending_unlink(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            original_fsync = os.fsync
            calls = []
            try:
                def count_fsync(target_fd):
                    calls.append(target_fd)
                    return original_fsync(target_fd)
                with patch.object(module.os, "fsync", side_effect=count_fsync):
                    module._publish_once(fd, b"two-directory-syncs")
                self.assertEqual(calls.count(fd), 2)
                self.assertEqual(len(calls), 3)  # staging file once; directory twice
                self.assertEqual(module._read_report(fd), b"two-directory-syncs")
                self.assertEqual(os.listdir(fd), [module.REPORT_NAME])
            finally:
                os.close(fd)

    def test_post_cleanup_second_directory_fsync_failure_is_ambiguous(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            original_fsync = os.fsync
            directory_calls = 0
            try:
                def second_fsync_fails(target_fd):
                    nonlocal directory_calls
                    if target_fd == fd:
                        directory_calls += 1
                        if directory_calls == 2:
                            raise OSError("synthetic cleanup durability uncertainty")
                    return original_fsync(target_fd)
                with patch.object(module.os, "fsync", side_effect=second_fsync_fails):
                    with self.assertRaises(module.PublicationOutcomeUnknown) as caught:
                        module._publish_once(fd, b"report-cannot-be-retried")
                self.assertEqual(directory_calls, 2)
                self.assertIn("DO NOT RETRY", str(caught.exception))
                self.assertEqual(module._read_report(fd), b"report-cannot-be-retried")
                self.assertEqual(os.listdir(fd), [module.REPORT_NAME])
                with self.assertRaises(FileExistsError):
                    module._publish_once(fd, b"replay")
            finally:
                os.close(fd)

    def test_post_publication_peer_direct_write_is_not_prevented_by_exclusive_name(self):
        # Explicit negative counterexample: a same-user writer with the path
        # can modify *content* even though a second exclusive name is denied.
        # Real security needs a separate enforced publisher/reader boundary.
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            try:
                module._publish_once(fd, b"trusted-report")
                with self.assertRaises(FileExistsError):
                    module._publish_once(fd, b"second-publisher")
                with open(Path(directory) / module.REPORT_NAME, "wb") as writer:
                    writer.write(b"tampered")
                self.assertEqual(module._read_report(fd), b"tampered")
                self.assertNotEqual(module._read_report(fd), b"trusted-report")
                verdict = module._result(["peer content mutation is not prevented"])
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertFalse(verdict["can_authorize_dispatch"])
            finally:
                os.close(fd)

    def test_symlink_collision_cannot_overwrite_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "target").write_bytes(b"untouched")
            (root / module.REPORT_NAME).symlink_to(root / "target")
            fd = self._dirfd(root)
            try:
                with self.assertRaises(FileExistsError):
                    module._publish_once(fd, b"new")
                self.assertEqual((root / "target").read_bytes(), b"untouched")
                with self.assertRaises(OSError):
                    module._read_report(fd)
            finally:
                os.close(fd)

    def test_fifo_collision_rejected_without_blocking(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            os.mkfifo(root / module.REPORT_NAME)
            fd = self._dirfd(root)
            try:
                with self.assertRaises(FileExistsError):
                    module._publish_once(fd, b"payload")
                self.assertEqual(os.listdir(fd), [module.REPORT_NAME])
            finally:
                os.close(fd)

    def test_failed_writer_leaves_no_visible_report_or_pending(self):
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            try:
                def fail(_fd, _data):
                    raise OSError("synthetic failure only")
                with self.assertRaises(OSError):
                    module._publish_once(fd, b"payload", writer=fail)
                self.assertEqual(os.listdir(fd), [])
            finally:
                os.close(fd)

    def test_nonprogress_writer_fails_closed_and_cleans_pending(self):
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            try:
                with self.assertRaises(OSError):
                    module._publish_once(fd, b"payload", writer=lambda _fd, _chunk: 0)
                self.assertEqual(os.listdir(fd), [])
            finally:
                os.close(fd)

    def test_partial_writer_is_completed_before_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            try:
                def partial(out_fd, chunk):
                    return os.write(out_fd, chunk[:2])
                module._publish_once(fd, b"123456789", writer=partial)
                self.assertEqual(module._read_report(fd), b"123456789")
            finally:
                os.close(fd)

    def test_empty_and_oversized_payloads_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fd = self._dirfd(directory)
            try:
                for data in (b"", b"X" * (module.MAX_BYTES + 1), "text"):
                    with self.subTest(data_type=type(data).__name__, length=len(data)):
                        with self.assertRaises(ValueError):
                            module._publish_once(fd, data)
                self.assertEqual(os.listdir(fd), [])
            finally:
                os.close(fd)

    def test_cli_rejects_caller_selected_checkout(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT),
                            "--checkout", "/protected"], capture_output=True,
                           text=True, timeout=4, check=False)
        self.assertNotEqual(p.returncode, 0)

    def test_missing_required_os_features_fail_closed(self):
        original = module.sys.platform
        try:
            module.sys.platform = "win32"
            r = module.run_demo()
            self.assertEqual(r["status"], "BLOCKED")
            self.assertFalse(r["can_authorize_dispatch"])
        finally:
            module.sys.platform = original


if __name__ == "__main__":
    unittest.main()
