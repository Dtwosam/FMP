from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec670_disposable_20_job_uid_coverage.py"
spec = importlib.util.spec_from_file_location("dec670_matrix", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CHECKS = ("checkout_create", "capabilities_zero")


def complete():
    return {name: {
        "status": module.UNVERIFIED, "findings": [],
        "can_authorize_dispatch": False, "independent_os_proof_verified": False,
        "observed_checks": {key: True for key in CHECKS},
    } for name in module.JOBS}


class SyntheticTwentyJobCoverageTests(unittest.TestCase):
    def test_exact_20_jobs_and_boundaries(self):
        self.assertEqual(len(module.JOBS), 20)
        self.assertEqual(len(set(module.JOBS)), 20)
        self.assertEqual(module.JOBS[0], "annual_preflight")
        self.assertEqual(module.JOBS[-1], "annual_freeze")
        self.assertEqual(len([job for job in module.JOBS if job.startswith("annual_cell:")]), 18)

    def test_fabricated_consistent_jobs_still_never_authorize(self):
        result = module.assess(complete(), CHECKS)
        self.assertEqual(result["status"], module.UNVERIFIED)
        self.assertEqual(result["covered_synthetic_jobs"], 20)
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])

    def test_each_missing_job_blocks(self):
        for job in module.JOBS:
            with self.subTest(job=job):
                data = complete()
                del data[job]
                self.assertEqual(module.assess(data, CHECKS)["status"], "BLOCKED")

    def test_each_job_denial_failure_blocks(self):
        for job in module.JOBS:
            with self.subTest(job=job):
                data = complete()
                data[job]["observed_checks"]["checkout_create"] = False
                result = module.assess(data, CHECKS)
                self.assertEqual(result["status"], "BLOCKED")
                self.assertEqual(result["covered_synthetic_jobs"], 19)

    def test_unknown_job_blocks(self):
        data = complete()
        data["annual_cell:19"] = data["annual_cell:18"]
        self.assertEqual(module.assess(data, CHECKS)["status"], "BLOCKED")

    def test_any_authorization_claim_blocks(self):
        data = complete()
        data["annual_freeze"]["can_authorize_dispatch"] = True
        self.assertEqual(module.assess(data, CHECKS)["status"], "BLOCKED")

    def test_missing_required_check_blocks(self):
        data = complete()
        del data["annual_preflight"]["observed_checks"]["capabilities_zero"]
        self.assertEqual(module.assess(data, CHECKS)["status"], "BLOCKED")

    def test_malformed_input_blocks(self):
        for bad in (None, [], {}, "", 1):
            with self.subTest(bad=repr(bad)):
                self.assertEqual(module.assess(bad, CHECKS)["status"], "BLOCKED")

    def test_default_cli_is_inert(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT)],
                           capture_output=True, text=True, timeout=4)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)["covered_synthetic_jobs"], 0)

    def test_cli_rejects_arbitrary_checkout_path(self):
        p = subprocess.run([sys.executable, "-B", str(SCRIPT), "--checkout", "/protected"],
                           capture_output=True, text=True, timeout=4)
        self.assertNotEqual(p.returncode, 0)

    @unittest.skipUnless(os.environ.get("DEC670_EXECUTE_DISPOSABLE_20") == "1",
                         "root Linux opt-in only; synthetic 20-job demo, not annual runner")
    def test_local_disposable_20_job_composition_unverified(self):
        result = module.run_demo()
        self.assertEqual(result["status"], module.UNVERIFIED, result)
        self.assertEqual(result["covered_synthetic_jobs"], 20)
        self.assertFalse(result["can_authorize_dispatch"])
        self.assertFalse(result["independent_os_proof_verified"])


if __name__ == "__main__":
    unittest.main()
