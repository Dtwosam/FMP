"""DEC-1377: read-only DEC-603 vs installed DEC-604 source review.

No annual module is imported; no private source, workflow dispatch,
runner, protected artifact or trading system is accessed.
"""
from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEC603 = "src/fmp/discovery/annual_pattern_catalogue_2023_execution_authorization.py"
DEC604 = "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py"
WORKFLOW = ".github/workflows/phase8a-annual-pattern-catalogue.yml"


def tracked(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", "HEAD:" + path], cwd=ROOT, text=True
    )


def constant(source: str, name: str):
    module = ast.parse(source)
    found = [
        ast.literal_eval(node.value)
        for node in module.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == name
    ]
    if len(found) != 1:
        raise ValueError("source constant absent or duplicate: " + name)
    return found[0]


class SourceInstallerReceiptsDoNotSupplyImmutableServerSideAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = tracked(DEC603)
        cls.installed = tracked(DEC604)
        cls.workflow = tracked(WORKFLOW)
        cls.live_blob = subprocess.check_output(
            ["git", "rev-parse", "HEAD:" + WORKFLOW],
            cwd=ROOT, text=True,
        ).strip()

    def test_dec603_pins_original_workflow_blob_source_only(self):
        pin = constant(self.before, "EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA")
        self.assertEqual(pin, self.live_blob)

    def test_dec603_preinstall_source_validator_requires_target_absent(self):
        src = self.before
        self.assertIn('RUNTIME_GATE_SOURCE_PATH = (', src)
        self.assertIn('if (root / RUNTIME_GATE_SOURCE_PATH).exists():', src)
        self.assertIn("2023 runtime gate target must remain absent", src)

    def test_installed_runtime_gate_target_is_present_in_git(self):
        self.assertIn("def require_2023_execution_authorized(", self.installed)
        self.assertIn("RUNTIME_AUTHORIZATION_INSTALLED = True", self.installed)

    def test_603_preinstall_status_cannot_be_reused_as_live_admission(self):
        self.assertIn("RUNTIME_AUTHORIZATION_INSTALLED = False", self.before)
        self.assertIn("DISPATCH_ACTION_EXECUTED = False", self.before)
        self.assertIn("RUNTIME_AUTHORIZATION_INSTALLED = True", self.installed)

    def test_603_and_604_agree_on_exact_one_shot_run_number(self):
        self.assertEqual(constant(self.before, "EXPECTED_RUN_NUMBER"), 385)
        self.assertEqual(constant(self.installed, "EXPECTED_RUN_NUMBER"), 385)
        self.assertEqual(constant(self.before, "EXPECTED_RUN_ATTEMPT"), 1)
        self.assertEqual(constant(self.installed, "EXPECTED_RUN_ATTEMPT"), 1)

    def test_603_and_604_agree_on_predecessor_run_identity(self):
        self.assertEqual(constant(self.before, "PREVIOUS_ANNUAL_FREEZE_RUN_ID"),
                         37663157285)
        self.assertEqual(constant(self.installed,
                                  "EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID"),
                         37663157285)

    def test_installed_gate_commit_validation_is_only_hex_shape(self):
        s = self.installed.split("def _validate_commit(", 1)[1].split(
            "\ndef _positive_int(", 1)[0]
        self.assertIn("len(value) != 40", s)
        self.assertIn("int(value, 16)", s)
        self.assertNotIn("EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA", s)

    def test_installed_gate_does_not_compare_to_603_workflow_blob_pin(self):
        s = self.installed.split("def require_2023_execution_authorized(", 1)[1].split(
            "\ndef runtime_authorization_payload(", 1)[0]
        self.assertIn("_validate_commit(code_commit)", s)
        self.assertNotIn("EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA", s)
        self.assertNotIn("approved_dispatch_sha", s)

    def test_2023_retries_and_broader_trading_remain_disallowed_in_both_sources(self):
        for content in (self.before, self.installed):
            for declaration in ("RERUN_AUTHORIZED = False",
                                "RETRY_AUTHORIZED = False",
                                "REPLACEMENT_RUN_AUTHORIZED = False",
                                "RUN_386_OR_LATER_AUTHORIZED = False",
                                "TRADING_AUTHORIZED = False"):
                with self.subTest(content=content[:24], flag=declaration):
                    self.assertIn(declaration, content)

    def test_immutable_workflow_blob_pin_can_detect_offline_mismatch_only(self):
        pin = constant(self.before, "EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA")
        self.assertEqual(len(pin), 40)
        self.assertNotEqual("0" * 40, pin)
        self.assertNotEqual("0" * 40, self.live_blob)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', self.workflow)
