from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec673_disposable_sibling_writer.py"
spec = importlib.util.spec_from_file_location("dec673", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def good():
    return {"restricted_write_denied": True, "restricted_uid": True,
            "source_unchanged": True, "source_inventory_unchanged": True,
            "child_exited_cleanly": True}


class PrivilegedSiblingWriterTests(unittest.TestCase):
    def test_complete_but_fake_observation_never_authorizes(self):
        result = module._result(good(), False)
        self.assertEqual(result["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED")
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])

    def test_each_missing_check_blocks(self):
        for key in good():
            with self.subTest(key=key):
                data = good(); del data[key]
                self.assertEqual(module._result(data, False)["status"], "BLOCKED")

    def test_each_false_check_blocks(self):
        for key in good():
            with self.subTest(key=key):
                data = good(); data[key] = False
                self.assertEqual(module._result(data, False)["status"], "BLOCKED")

    def test_truthy_nonboolean_check_blocks(self):
        data = good(); data["source_unchanged"] = 1
        self.assertEqual(module._result(data, False)["status"], "BLOCKED")

    def test_injected_sibling_blocks_despite_child_denial(self):
        data = good(); data["source_unchanged"] = False
        result = module._result(data, True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(result["observed_checks"]["restricted_write_denied"])
        self.assertFalse(result["observed_checks"]["source_unchanged"])

    def test_injection_not_detected_still_blocks(self):
        result = module._result(good(), True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("synthetic sibling-write negative control not detected", result["findings"])

    def test_malformed_observations_block(self):
        for data in (None, [], 0, "", {"status": "PASS"}):
            with self.subTest(data=str(data)):
                self.assertEqual(module._result(data, False)["status"], "BLOCKED")

    def test_inert_default_nonzero(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT)],
                           capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)["status"], "BLOCKED")

    def test_conflicting_modes_nonzero(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT),
                            "--execute-disposable-control", "--execute-privileged-sibling-negative"],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)

    def test_reject_arbitrary_source(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT), "--source", "/protected"],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)

    def test_nonroot_blocks_without_attempt(self):
        with patch.object(module.os, "geteuid", return_value=1000):
            self.assertEqual(module.run_demo()["status"], "BLOCKED")

    @unittest.skipUnless(os.environ.get("DEC673_EXECUTE_LOCAL_OS") == "1", "manual local root disposable only")
    def test_actual_kernel_denial_and_privileged_sibling_bypass(self):
        control = module.run_demo()
        self.assertEqual(control["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED", control)
        injected = module.run_demo(True)
        self.assertEqual(injected["status"], "BLOCKED", injected)
        self.assertTrue(injected["observed_checks"]["restricted_write_denied"])
        self.assertFalse(injected["observed_checks"]["source_unchanged"])
        self.assertFalse(injected["can_authorize_dispatch"])


if __name__ == "__main__":
    unittest.main()
