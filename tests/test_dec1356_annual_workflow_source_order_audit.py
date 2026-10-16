from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github"/"workflows"/"phase8a-annual-pattern-catalogue.yml"
SOURCE=ROOT/"scripts"/"dec1356_annual_workflow_source_order_audit.py"
spec=importlib.util.spec_from_file_location("dec1356_source_audit",SOURCE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ActualAnnualWorkflowSourceMustNotBeMistakenForAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=subprocess.check_output(["git", "show",
            "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True)

    def _blocked(self,source):
        report=module.audit_annual_workflow_source(source)
        self.assertEqual(report["status"],"BLOCKED")
        self.assertEqual(report["classification"],
                         "SOURCE_ONLY_WORKFLOW_ORDER_NONAUTHORITATIVE")
        self.assertEqual(report["gate_states"],
                         {"DEC-650/#820":"BLOCKED",
                          "DEC-651/#821/#779":"BLOCKED"})
        for name in ("can_authorize_dispatch","independent_os_proof_verified",
                     "immutable_annual_admission_verified",
                     "may_access_protected_evidence",
                     "may_install_workflow_or_policy","may_trade"):
            self.assertIs(report[name],False,name)
        return report

    def test_three_actual_jobs_require_independent_precheckout_admission(self):
        r=self._blocked(self.source)
        self.assertEqual(set(r["job_steps"]),set(module.JOBS))
        for job in module.JOBS:
            with self.subTest(job=job):
                self.assertEqual(r["job_steps"][job][0],"Checkout")
                self.assertIn(
                    "NO_INDEPENDENT_ADMISSION_BEFORE_CHECKOUT_"+job,
                    r["blockers"])

    def test_three_actual_jobs_have_install_before_separate_exec_check(self):
        r=self._blocked(self.source)
        for job in module.JOBS:
            with self.subTest(job=job):
                steps=r["job_steps"][job]
                install=steps.index("Install pinned annual catalogue runtime")
                recheck=next(i for i,v in enumerate(steps)
                             if "authorized annual catalogue execution" in v)
                self.assertLess(install,recheck)
                self.assertIn(
                    "RUNTIME_INSTALL_BEFORE_EXECUTION_RECHECK_"+job,
                    r["blockers"])

    def test_actual_preflight_fetches_snapshot_metadata_before_auth_check(self):
        r=self._blocked(self.source)
        steps=r["job_steps"]["annual_preflight"]
        fetch=steps.index("Fetch exact accepted EXP-044 source snapshots")
        auth=steps.index("Require separately authorized annual catalogue execution")
        self.assertLess(fetch,auth)
        self.assertIn("SOURCE_SNAPSHOT_METADATA_BEFORE_AUTHORIZATION",
                      r["blockers"])

    def test_current_three_jobs_still_check_mutable_main_ref(self):
        r=self._blocked(self.source)
        for job in module.JOBS:
            with self.subTest(job=job):
                self.assertIn("MUTABLE_MAIN_ONLY_GATE_"+job,r["blockers"])

    def test_actual_matrix_source_has_eighteen_not_a_proof_of_execution(self):
        r=self._blocked(self.source)
        self.assertNotIn("SOURCE_MATRIX_NOT_EXACTLY_18_CELLS",r["blockers"])
        self.assertIn(
            "RUN385_ATTEMPT1_SEPARATE_ONE_SHOT_AUTHORITY_NOT_VERIFIED",
            r["blockers"])

    def test_missing_job_and_changed_matrix_fail_closed(self):
        base=self.source
        for job in module.JOBS:
            with self.subTest(job=job):
                # Replace job heading only; no workflow is run.
                changed=base.replace("  "+job+":","  removed_"+job+":",1)
                r=self._blocked(changed)
                self.assertIn(
                    "REQUIRED_JOB_ABSENT_OR_DUPLICATED_"+job,r["blockers"])
        changed=base.replace("          - symbol: EURUSD",
                             "          - inactive_symbol: EURUSD",1)
        self.assertIn("SOURCE_MATRIX_NOT_EXACTLY_18_CELLS",
                      self._blocked(changed)["blockers"])

    def test_nontext_input_and_mock_precheckout_step_never_authorize(self):
        self.assertIn("WORKFLOW_SOURCE_NOT_TEXT",
                      self._blocked({})["blockers"])
        changed=self.source.replace(
            "      - name: Checkout",
            "      - name: Hypothetical independent precheckout gate\n"
            "      - name: Checkout",
            1)
        r=self._blocked(changed)
        self.assertNotIn(
            "NO_INDEPENDENT_ADMISSION_BEFORE_CHECKOUT_annual_preflight",
            r["blockers"])
        self.assertIn(
            "SERVER_SIDE_EXCLUSIVE_IMMUTABLE_REF_SHA_NOT_VERIFIED",
            r["blockers"])
