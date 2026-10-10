from __future__ import annotations

"""DEC-665 synthetic observer tests. Real Linux demonstration opt-in only."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec665_live_proc_fd_observer.py"
spec = importlib.util.spec_from_file_location("dec665_observer", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def synthetic_good():
    return {name: True for name in module._REQUIRED}


class LiveProcFdObserverTests(unittest.TestCase):
    def test_fake_complete_observation_never_authorizes(self):
        result = module._evaluate(synthetic_good(), injected=False)
        self.assertEqual(result["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED")
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])

    def test_missing_observer_fields_fail_closed(self):
        for field in module._REQUIRED:
            with self.subTest(field=field):
                case = synthetic_good()
                del case[field]
                self.assertEqual(module._evaluate(case, False)["status"], "BLOCKED")

    def test_each_false_observer_check_blocks(self):
        for field in module._REQUIRED:
            with self.subTest(field=field):
                case = synthetic_good()
                case[field] = False
                self.assertEqual(module._evaluate(case, False)["status"], "BLOCKED")

    def test_truthy_nonboolean_observer_check_blocks(self):
        case = synthetic_good()
        case["safe_cwd"] = 1
        self.assertEqual(module._evaluate(case, False)["status"], "BLOCKED")

    def test_malformed_observer_data_blocks(self):
        for data in (None, "good", [], {}, 1, True):
            with self.subTest(raw=repr(data)):
                self.assertEqual(module._evaluate(data, False)["status"], "BLOCKED")

    def test_injected_mode_never_reports_unverified_clean(self):
        result = module._evaluate(synthetic_good(), injected=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("expected synthetic leaked checkout FD was not observed", result["findings"])
        self.assertFalse(result["can_authorize_dispatch"])

    def test_injected_checkout_handle_is_rejected(self):
        case = synthetic_good()
        case["no_checkout_fd"] = False
        case["no_extra_fd"] = False
        result = module._evaluate(case, injected=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["independent_os_proof_verified"])

    def test_stdstream_claim_must_be_pipe(self):
        case = synthetic_good()
        case["stdio_pipes"] = False
        self.assertEqual(module._evaluate(case, False)["status"], "BLOCKED")

    def test_checkout_cwd_not_accepted(self):
        case = synthetic_good()
        case["safe_cwd"] = False
        self.assertEqual(module._evaluate(case, False)["status"], "BLOCKED")

    def test_stable_two_procfd_snapshots_are_accepted_structurally(self):
        table = {0: "pipe:[1]", 1: "pipe:[2]", 2: "pipe:[3]"}
        observed, cwd = module._require_stable_snapshot(table, table.copy(), "/tmp/a", "/tmp/a")
        self.assertEqual(observed, table)
        self.assertEqual(cwd, "/tmp/a")

    def test_changed_fd_target_between_live_scans_blocks(self):
        before = {0: "pipe:[1]", 1: "pipe:[2]", 2: "pipe:[3]"}
        after = before.copy()
        after[4] = "/tmp/disposable/checkout/sample"
        with self.assertRaises(OSError):
            module._require_stable_snapshot(before, after, "/tmp/scratch", "/tmp/scratch")

    def test_changed_cwd_between_live_scans_blocks(self):
        table = {0: "pipe:[1]", 1: "pipe:[2]", 2: "pipe:[3]"}
        with self.assertRaises(OSError):
            module._require_stable_snapshot(table, table.copy(), "/tmp/scratch", "/tmp/checkout")

    def test_proc_fd_relative_reader_uses_only_symlink_targets(self):
        # The reader must never follow/invoke an inherited FD target.
        with patch.object(module.os, "listdir", return_value=["0", "1", "2"]):
            with patch.object(module.os, "readlink", side_effect=lambda name, dir_fd=None: "pipe:[" + name + "]") as readlink:
                found = module._read_fd_targets(123)
        self.assertEqual(found, {0: "pipe:[0]", 1: "pipe:[1]", 2: "pipe:[2]"})
        self.assertEqual(readlink.call_count, 3)
        for call in readlink.call_args_list:
            self.assertEqual(call.kwargs, {"dir_fd": 123})

    def test_default_cli_does_not_launch_or_authorize(self):
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT)],
                              capture_output=True, text=True, timeout=4, check=False)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["can_authorize_dispatch"])

    def test_help_is_not_an_authorization_success(self):
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "--help"],
                              capture_output=True, text=True, timeout=4, check=False)
        self.assertNotEqual(proc.returncode, 0)

    def test_caller_cannot_choose_checkout_path(self):
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "--source", "/protected"],
                              capture_output=True, text=True, timeout=4, check=False)
        self.assertNotEqual(proc.returncode, 0)

    def test_mutually_exclusive_cli_modes(self):
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--execute-disposable-demo",
             "--execute-fd-negative-control"],
            capture_output=True, text=True, timeout=4, check=False,
        )
        self.assertNotEqual(proc.returncode, 0)

    def test_unsupported_platform_fails_closed(self):
        with patch.object(module.sys, "platform", "win32"):
            self.assertEqual(module.run_demo()["status"], "BLOCKED")

    @unittest.skipUnless(os.environ.get("DEC665_EXECUTE_LIVE_PROC_TEST") == "1",
                         "manual opt-in; cannot certify annual runner isolation")
    def test_real_live_fd_snapshot_clean_is_locally_unverified(self):
        result = module.run_demo()
        self.assertEqual(result["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED", result)
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])

    @unittest.skipUnless(os.environ.get("DEC665_EXECUTE_LIVE_PROC_TEST") == "1",
                         "manual opt-in; cannot certify annual runner isolation")
    def test_real_live_checkout_fd_negative_control_blocks(self):
        result = module.run_demo(inject_checkout_fd=True)
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertFalse(result["observed_checks"]["no_checkout_fd"])
        self.assertFalse(result["observed_checks"]["no_extra_fd"])
        self.assertFalse(result["can_authorize_dispatch"])


if __name__ == "__main__":
    unittest.main()
