from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec653_disposable_mount_witness.py"
spec = importlib.util.spec_from_file_location("dec653_witness", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def synthetic_report():
    return {
        "checks": {key: True for key in module.CHECKS},
        "status": {**{key: "0000000000000000" for key in module.CAPS}, "NoNewPrivs": "1"},
        "inherited_fd_probe": "not_provided",
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

    def test_inventory_change_blocks(self):
        self.assertEqual(module._evaluate(synthetic_report(), False)["status"], "BLOCKED")

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

    def test_cli_without_optin_is_blocked(self):
        cmd = [sys.executable, "-B", str(SCRIPT)]
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
        self.assertEqual(process.returncode, 2)
        result = json.loads(process.stdout)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["can_authorize_dispatch"])

    @unittest.skipUnless(os.environ.get("DEC653_EXECUTE_DISPOSABLE_OS_TEST") == "1",
                         "manual opt-in only; not CI acceptance")
    def test_optin_disposable_os_witness_remains_nonauthorizing(self):
        result = module.run_demo()
        self.assertIn(result["status"], ("LOCAL_DISPOSABLE_WITNESS_UNVERIFIED", "BLOCKED"))
        self.assertFalse(result["can_authorize_dispatch"])


    @unittest.skipUnless(os.environ.get("DEC653_EXECUTE_DISPOSABLE_OS_TEST") == "1",
                         "manual opt-in only; not CI acceptance")
    def test_optin_inherited_fd_counterexample_remains_blocked(self):
        result = module.run_demo(inject_checkout_fd=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])


if __name__ == "__main__":
    unittest.main()
