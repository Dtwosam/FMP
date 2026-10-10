from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import tempfile
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec653_disposable_mount_witness.py"
spec = importlib.util.spec_from_file_location("dec653_witness", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def synthetic_report():
    return {
        "checks": {key: True for key in module.CHECKS},
        "status": {**{key: "0000000000000000" for key in module.CAPS}, "NoNewPrivs": "1"},
        "inherited_fd_probe": "closed_before_consumer",
        "stdio_probe": "not_provided",
        "stdin_probe": "safe_eof",
    }


class DisposableOSWitnessTests(unittest.TestCase):
    def test_consistent_synthetic_claims_are_not_authorization(self):
        result = module._evaluate(synthetic_report(), True)
        self.assertEqual(result["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED")
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])

    def test_each_missing_os_denial_blocks(self):
        for key in module.CHECKS:
            with self.subTest(key=key):
                report = synthetic_report()
                del report["checks"][key]
                self.assertEqual(module._evaluate(report, True)["status"], "BLOCKED")

    def test_each_false_os_denial_blocks(self):
        for key in module.CHECKS:
            with self.subTest(key=key):
                report = synthetic_report()
                report["checks"][key] = False
                self.assertEqual(module._evaluate(report, True)["status"], "BLOCKED")

    def test_truthy_nonboolean_denial_blocks(self):
        report = synthetic_report()
        report["checks"]["create"] = 1
        self.assertEqual(module._evaluate(report, True)["status"], "BLOCKED")

    def test_nonzero_capabilities_block(self):
        for key in module.CAPS:
            with self.subTest(key=key):
                report = synthetic_report()
                report["status"][key] = "0000000000000001"
                self.assertEqual(module._evaluate(report, True)["status"], "BLOCKED")

    def test_missing_capability_blocks(self):
        for key in module.CAPS:
            with self.subTest(key=key):
                report = synthetic_report()
                del report["status"][key]
                self.assertEqual(module._evaluate(report, True)["status"], "BLOCKED")

    def test_no_new_privs_blocks_when_disabled(self):
        report = synthetic_report()
        report["status"]["NoNewPrivs"] = "0"
        self.assertEqual(module._evaluate(report, True)["status"], "BLOCKED")

    def test_missing_stdio_probe_blocks(self):
        raw = synthetic_report()
        del raw["stdio_probe"]
        self.assertEqual(module._evaluate(raw, True)["status"], "BLOCKED")

    def test_injected_writable_stdout_blocks(self):
        raw = synthetic_report()
        raw["stdio_probe"] = "write_succeeded"
        result = module._evaluate(raw, True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("checkout-writable standard stream inherited or unaccounted for", result["findings"])
        self.assertFalse(result["can_authorize_dispatch"])

    def test_conflicting_injected_fd_modes_block(self):
        result = module.run_demo(inject_checkout_fd=True, inject_stdout_fd=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["can_authorize_dispatch"])

    def test_cli_injection_modes_are_mutually_exclusive(self):
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT),
                              "--execute-fd-counterexample", "--execute-stdio-counterexample"],
                              capture_output=True, text=True, timeout=4, check=False)
        self.assertNotEqual(proc.returncode, 0)

    def test_missing_stdin_provenance_blocks(self):
        raw = synthetic_report()
        del raw["stdin_probe"]
        self.assertEqual(module._evaluate(raw, True)["status"], "BLOCKED")

    def test_inherited_stdin_canary_blocks_without_source_change(self):
        raw = synthetic_report()
        raw["stdin_probe"] = "canary_received"
        result = module._evaluate(raw, True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("standard input descriptor exposed data or lacks safe provenance", result["findings"])
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])

    def test_arbitrary_stdin_claim_blocks(self):
        raw = synthetic_report()
        raw["stdin_probe"] = "unexpected_input"
        self.assertEqual(module._evaluate(raw, True)["status"], "BLOCKED")

    def test_stdio_and_stdin_injection_conflict_blocks(self):
        result = module.run_demo(inject_stdout_fd=True, inject_stdin_fd=True)
        self.assertEqual(result["status"], "BLOCKED")

    def test_cli_stdin_mode_conflicts_with_high_fd_mode(self):
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT),
                              "--execute-fd-counterexample", "--execute-stdin-counterexample"],
                              capture_output=True, text=True, timeout=4)
        self.assertNotEqual(proc.returncode, 0)

    def test_inventory_change_blocks(self):
        self.assertEqual(module._evaluate(synthetic_report(), False)["status"], "BLOCKED")

    def test_missing_fd_observation_not_enough(self):
        report = synthetic_report()
        report["inherited_fd_probe"] = "not_provided"
        self.assertEqual(module._evaluate(report, True)["status"], "BLOCKED")

    def test_missing_fd_provenance_blocks(self):
        report = synthetic_report()
        del report["inherited_fd_probe"]
        self.assertEqual(module._evaluate(report, True)["status"], "BLOCKED")

    def test_injected_writable_fd_blocks_even_if_other_checks_pass(self):
        report = synthetic_report()
        report["inherited_fd_probe"] = "write_succeeded"
        result = module._evaluate(report, True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["can_authorize_dispatch"])

    def test_denied_inherited_fd_still_needs_explicit_provenance(self):
        report = synthetic_report()
        report["inherited_fd_probe"] = "write_denied"
        self.assertEqual(module._evaluate(report, True)["status"], "BLOCKED")

    def test_malformed_synthetic_outputs_block(self):
        for value in (None, {}, [], "hello", {"checks": {}, "status": []}):
            with self.subTest(value=str(value)):
                self.assertEqual(module._evaluate(value, True)["status"], "BLOCKED")

    def test_pinned_directory_detects_unexpected_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample").write_bytes(b"synthetic")
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                baseline_dir, baseline = os.fstat(fd), module._sample_snapshot(fd)
                self.assertIsNotNone(baseline)
                self.assertTrue(module._unchanged_disposable_source(root, fd, baseline_dir, baseline))
                (root / "unexpected").write_bytes(b"changed")
                self.assertFalse(module._unchanged_disposable_source(root, fd, baseline_dir, baseline))
            finally:
                os.close(fd)

    def test_swapped_symlink_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample").write_bytes(b"fake")
            (root / "other").write_bytes(b"do not open")
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                (root / "sample").unlink()
                (root / "sample").symlink_to(root / "other")
                with self.assertRaises(OSError):
                    module._sample_snapshot(fd)
                self.assertEqual((root / "other").read_bytes(), b"do not open")
            finally:
                os.close(fd)

    def test_oversized_sample_snapshot_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample").write_bytes(b"X" * 4097)
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                self.assertIsNone(module._sample_snapshot(fd))
            finally:
                os.close(fd)

    def test_fifo_leaf_snapshot_never_blocks(self):
        # A prior regular-file-to-FIFO swap must not hang CI or exhaust worker slots.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            os.mkfifo(root / "sample")
            program = (
                "import importlib.util,os,sys; "
                "s=importlib.util.spec_from_file_location('w',sys.argv[1]); "
                "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                "fd=os.open(sys.argv[2],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW); "
                "print(m._sample_snapshot(fd) is None)"
            )
            proc = subprocess.run([sys.executable, "-B", "-c", program, str(SCRIPT), str(root)],
                                  capture_output=True, text=True, timeout=3, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "True")

    def test_swapped_disposable_directory_blocks_without_following_link(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "checkout"
            root.mkdir()
            (root / "sample").write_bytes(b"synthetic")
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                original_dir = os.fstat(fd)
                before = module._sample_snapshot(fd)
                (parent / "other").mkdir()
                root.rename(parent / "old")
                root.symlink_to(parent / "other", target_is_directory=True)
                self.assertFalse(module._unchanged_disposable_source(root, fd, original_dir, before))
            finally:
                os.close(fd)

    def test_tmpdir_override_does_not_redirect_demo(self):
        class StopBeforeCreating(Exception):
            pass
        with patch.dict(os.environ, {"TMPDIR": "/caller-selected"}):
            with patch.object(module.shutil, "which", return_value="/usr/bin/utility"):
                with patch.object(module.sys, "platform", "linux"):
                    with patch.object(module.tempfile, "TemporaryDirectory", side_effect=StopBeforeCreating) as create:
                        with self.assertRaises(StopBeforeCreating):
                            module.run_demo()
                        self.assertEqual(create.call_args.kwargs["dir"], "/tmp")

    def test_cli_without_optin_is_blocked(self):
        cmd = [sys.executable, "-B", str(SCRIPT)]
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
        self.assertEqual(process.returncode, 2)
        result = json.loads(process.stdout)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["can_authorize_dispatch"])

    def test_help_cannot_return_zero(self):
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "--help"],
                              capture_output=True, text=True, timeout=4)
        self.assertNotEqual(proc.returncode, 0)

    def test_rejects_caller_selected_source(self):
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "--source", "/protected"],
                              capture_output=True, text=True, timeout=4)
        self.assertNotEqual(proc.returncode, 0)

    def test_unsupported_platform_blocks(self):
        with patch.object(module.sys, "platform", "win32"):
            self.assertEqual(module.run_demo()["status"], "BLOCKED")

    @unittest.skipUnless(os.environ.get("DEC653_EXECUTE_DISPOSABLE_OS_TEST") == "1",
                         "manual opt-in only; not CI acceptance")
    def test_optin_disposable_os_witness_remains_nonauthorizing(self):
        result = module.run_demo()
        self.assertEqual(result["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED", result)
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])


    @unittest.skipUnless(os.environ.get("DEC653_EXECUTE_DISPOSABLE_OS_TEST") == "1",
                         "manual opt-in only; not CI acceptance")
    def test_optin_inherited_fd_counterexample_remains_blocked(self):
        result = module.run_demo(inject_checkout_fd=True)
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertIn("disposable checkout inventory changed", result["findings"])
        self.assertIn("writable checkout descriptor inherited or unaccounted for", result["findings"])
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])

    @unittest.skipUnless(os.environ.get("DEC653_EXECUTE_DISPOSABLE_OS_TEST") == "1",
                         "manual opt-in only; not CI acceptance")
    def test_optin_standard_stream_counterexample_is_blocked(self):
        result = module.run_demo(inject_stdout_fd=True)
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertIn("disposable checkout inventory changed", result["findings"])
        self.assertIn("checkout-writable standard stream inherited or unaccounted for", result["findings"])
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])

    @unittest.skipUnless(os.environ.get("DEC653_EXECUTE_DISPOSABLE_OS_TEST") == "1",
                         "manual opt-in only; not CI acceptance")
    def test_optin_inherited_stdin_canary_is_blocked_without_checkout_write(self):
        result = module.run_demo(inject_stdin_fd=True)
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertIn("standard input descriptor exposed data or lacks safe provenance", result["findings"])
        self.assertNotIn("disposable checkout inventory changed", result["findings"])
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])


if __name__ == "__main__":
    unittest.main()
