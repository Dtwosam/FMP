from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec669_disposable_uid_boundary.py"
spec = importlib.util.spec_from_file_location("dec669_uid", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DisposableUidBoundaryTests(unittest.TestCase):
    def test_synthetic_positive_is_never_authorizing(self):
        verdict = module._evaluate({"checks": {key: True for key in module.REQUIRED}})
        self.assertEqual(verdict["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED")
        self.assertFalse(verdict["can_authorize_dispatch"])
        self.assertFalse(verdict["independent_os_proof_verified"])

    def test_each_missing_check_blocks(self):
        for key in module.REQUIRED:
            with self.subTest(key=key):
                checks = {n: True for n in module.REQUIRED}
                del checks[key]
                self.assertEqual(module._evaluate({"checks": checks})["status"], "BLOCKED")

    def test_each_false_check_blocks(self):
        for key in module.REQUIRED:
            with self.subTest(key=key):
                checks = {n: True for n in module.REQUIRED}
                checks[key] = False
                self.assertEqual(module._evaluate({"checks": checks})["status"], "BLOCKED")

    def test_truthy_nonboolean_check_blocks(self):
        checks = {n: True for n in module.REQUIRED}
        checks["source_unchanged"] = 1
        self.assertEqual(module._evaluate({"checks": checks})["status"], "BLOCKED")

    def test_malformed_observation_blocks(self):
        for bad in (None, [], {}, "", {"checks": []}, {"checks": None}):
            with self.subTest(bad=repr(bad)):
                self.assertEqual(module._evaluate(bad)["status"], "BLOCKED")

    def test_never_escalates_nonroot_caller(self):
        with patch.object(module.os, "geteuid", return_value=1234):
            self.assertEqual(module.run_demo()["status"], "BLOCKED")

    def test_inert_default_cli(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT)],
                           capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["can_authorize_dispatch"])

    def test_cli_rejects_arbitrary_source_argument(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT), "--source", "/protected"],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)

    @unittest.skipUnless(os.environ.get("DEC669_EXECUTE_DISPOSABLE_UID_TEST") == "1",
                         "root Linux opt-in only, NOT actual annual runner proof")
    def test_local_separate_uid_denials_still_unverified(self):
        verdict = module.run_demo()
        self.assertEqual(verdict["status"], "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED", verdict)
        self.assertTrue(all(verdict["observed_checks"].values()))
        self.assertFalse(verdict["can_authorize_dispatch"])
        self.assertFalse(verdict["independent_os_proof_verified"])


if __name__ == "__main__":
    unittest.main()
