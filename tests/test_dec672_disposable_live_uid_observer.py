from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec672_disposable_live_uid_observer.py"
spec = importlib.util.spec_from_file_location("dec672_live", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def all_good():
    return {key: True for key in module.PARENT_CHECKS + module.CHILD_CHECKS + module.POST_CHECKS}


class LiveUidObserverTests(unittest.TestCase):
    def test_fabricated_complete_observation_never_authorizes(self):
        result = module._evaluate(all_good())
        self.assertEqual(result["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED")
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])

    def test_missing_each_required_field_blocks(self):
        for key in all_good():
            with self.subTest(key=key):
                data = all_good()
                del data[key]
                self.assertEqual(module._evaluate(data)["status"], "BLOCKED")

    def test_false_each_required_field_blocks(self):
        for key in all_good():
            with self.subTest(key=key):
                data = all_good()
                data[key] = False
                self.assertEqual(module._evaluate(data)["status"], "BLOCKED")

    def test_truthy_nonboolean_check_blocks(self):
        data = all_good()
        data["live_uid"] = 1
        self.assertEqual(module._evaluate(data)["status"], "BLOCKED")

    def test_readlink_unavailable_always_blocks(self):
        data = all_good()
        data["live_fd_targets_readable"] = False
        data["live_cwd_readable"] = False
        self.assertEqual(module._evaluate(data)["status"], "BLOCKED")

    def test_injected_writable_fd_blocks_even_if_everything_claims_good(self):
        result = module._evaluate(all_good(), injected=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("injected descriptor failed to appear in independent observer", result["findings"])

    def test_injected_writable_fd_with_negative_observation_blocks(self):
        data = all_good()
        data["live_no_unexpected_fd"] = False
        data["live_no_checkout_or_report_fd"] = False
        result = module._evaluate(data, injected=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["can_authorize_dispatch"])

    def test_malformed_data_blocks(self):
        for data in (None, [], "good", {}, 3):
            with self.subTest(data=repr(data)):
                self.assertEqual(module._evaluate(data)["status"], "BLOCKED")

    def test_status_parser_avoids_duplicate_keys(self):
        r = module._parse_status("Uid:\t65534\t65534\t65534\t65534\nUid:\t0\nGroups:\t\n")
        self.assertEqual(r["Uid"], "65534\t65534\t65534\t65534")
        self.assertEqual(r["Groups"], "")

    def test_nonroot_does_not_attempt_privileged_demo(self):
        with patch.object(module.os, "geteuid", return_value=1000):
            self.assertEqual(module.run_demo()["status"], "BLOCKED")

    def test_default_cli_is_inert_and_nonzero(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT)],
                           capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)["status"], "BLOCKED")

    def test_conflicting_modes_fail(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT),
                            "--execute-disposable-demo", "--execute-leaked-fd-control"],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)

    def test_caller_selected_checkout_path_rejected(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT), "--checkout", "/protected"],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)

    @unittest.skipUnless(os.environ.get("DEC672_EXECUTE_LOCAL_OS") == "1",
                         "manual opt-in only; procfs permissions vary by host")
    def test_live_local_observer_can_fail_closed_if_procfd_unavailable(self):
        for injected in (False, True):
            with self.subTest(injected=injected):
                result = module.run_demo(inject_checkout_fd=injected)
                self.assertIn(result["status"], ("BLOCKED", "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED"))
                self.assertFalse(result["can_authorize_dispatch"])
                self.assertFalse(result["independent_os_proof_verified"])
                if injected:
                    self.assertEqual(result["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
