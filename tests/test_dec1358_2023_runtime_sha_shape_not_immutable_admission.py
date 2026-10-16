from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/"src"/"fmp"/"discovery"/(
    "annual_pattern_catalogue_2023_runtime_authorization.py")
WORKFLOW=ROOT/".github"/"workflows"/(
    "phase8a-annual-pattern-catalogue.yml")


class AnnualRuntimeShaShapeIsNotImmutableDispatchAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=RUNTIME.read_text(encoding="utf-8")
        cls.workflow=subprocess.check_output(["git", "show",
            "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True)
        cls.module=ast.parse(cls.source)

    def _func(self,name):
        hits=[node for node in self.module.body if (
            isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))
            and node.name==name)]
        self.assertEqual(len(hits),1)
        return hits[0]

    def test_source_validate_commit_checks_shape_not_approved_commit_identity(self):
        func=self._func("_validate_commit")
        body=ast.get_source_segment(self.source,func)
        self.assertIn("len(value) != 40",body)
        self.assertIn("int(value, 16)",body)
        self.assertIn("return value.lower()",body)
        self.assertNotIn("APPROVED_COMMIT_SHA",body)
        self.assertNotIn("EXPECTED_APPROVED_SHA",body)

    def test_2023_gate_invokes_shape_check_without_independent_sha_equality(self):
        func=self._func("require_2023_execution_authorized")
        body=ast.get_source_segment(self.source,func)
        self.assertIn("_validate_commit(code_commit)",body)
        self.assertIn("run_number",body)
        self.assertIn("run_attempt",body)
        self.assertNotIn("approved_commit",body.lower())
        self.assertNotIn("expected_sha",body.lower())
        self.assertNotIn("independent_os_proof_verified",body)

    def test_2023_run_and_predecessor_constants_are_not_unique_server_lock(self):
        self.assertIn("EXPECTED_RUN_NUMBER = 385",self.source)
        self.assertIn("EXPECTED_RUN_ATTEMPT = 1",self.source)
        self.assertIn("EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37663157285",
                      self.source)
        self.assertIn("RUNTIME_AUTHORIZATION_INSTALLED = True",self.source)
        self.assertIn("ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = True",self.source)
        self.assertIn("refs/heads/main",self.workflow)
        self.assertIn("workflow_dispatch:",self.workflow)

    def test_source_disallows_second_attempt_and_broader_strategy_activity(self):
        for line in (
            "RERUN_AUTHORIZED = False",
            "RETRY_AUTHORIZED = False",
            "REPLACEMENT_RUN_AUTHORIZED = False",
            "RUN_386_OR_LATER_AUTHORIZED = False",
            "STRATEGY_V1_SYNTHESIS_AUTHORIZED = False",
            "BROKER_MUTATION_AUTHORIZED = False",
            "TRADING_AUTHORIZED = False",
        ):
            with self.subTest(line=line):
                self.assertIn(line,self.source)

    def test_runtime_source_does_not_claim_external_write_policy_authentication(self):
        func=self._func("require_2023_execution_authorized")
        body=ast.get_source_segment(self.source,func)
        for expression in (
            "mount_namespace", "read_only_mount", "independent_os",
            "landlock_restrict_self", "reviewer_signature",
            "no_bypass_main_lock", "server_side_dispatch_lock",
        ):
            self.assertNotIn(expression,body)
        self.assertIn("require_2023_execution_authorized(",self.source)

    def test_runtime_gate_is_job_step_after_checkout_and_install(self):
        for section in ("annual_preflight","annual_cell","annual_freeze"):
            with self.subTest(job=section):
                job=self.workflow.split("  "+section+":",1)[1]
                if section=="annual_preflight":
                    job=job.split("  annual_cell:",1)[0]
                elif section=="annual_cell":
                    job=job.split("  annual_freeze:",1)[0]
                self.assertLess(job.index("- name: Checkout"),
                                job.index("Install pinned annual catalogue runtime"))
                self.assertLess(job.index("Install pinned annual catalogue runtime"),
                                job.index("authorized annual catalogue execution"))
