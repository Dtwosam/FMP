"""DEC-1386: committed source-only manual input inventory.

Read-only git show; no Actions or annual CLI execution, protected inputs, or
actual workflow dispatch. Test mutations are in-memory strings.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ("annual_segment_label", "previous_annual_freeze_run_id")


def input_diagnostics(value: object) -> tuple[str, ...]:
    if type(value) is not str:
        return ("NON_TEXT",)
    if value.count("\non:\n") != 1 or value.count("\npermissions:\n") != 1:
        return ("TRIGGER_SHAPE",)
    trigger = value.split("\non:\n", 1)[1].split("\npermissions:\n", 1)[0]
    if trigger.count("    inputs:\n") != 1:
        return ("INPUT_BLOCK_SHAPE",)
    block = trigger.split("    inputs:\n", 1)[1]
    names = re.findall(r"(?m)^      ([a-z_][a-z0-9_]*):$", block)
    problems = []
    if tuple(names) != EXPECTED:
        problems.append("UNREVIEWED_MANUAL_INPUT")
    references = set(re.findall(
        r"\$\{\{\s*inputs\.([a-z_][a-z0-9_]*)\s*\}\}", value
    ))
    if not references <= set(EXPECTED):
        problems.append("UNREVIEWED_INPUT_EXPRESSION")
    if tuple(names) == EXPECTED:
        first, second = block.split("      previous_annual_freeze_run_id:\n", 1)
        if ("        required: true" not in first
                or "        type: choice" not in first
                or "        required: false" not in second
                or "        type: string" not in second):
            problems.append("INPUT_REQUIREMENT_TYPE_DRIFT")
    return tuple(problems)


class AnnualManualInputSourceDoesNotBindServerSideDispatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )

    def test_actual_source_has_exact_two_input_inventory(self):
        self.assertEqual(input_diagnostics(self.workflow), ())

    def test_annual_segment_is_required_choice(self):
        section = self.workflow.split("      annual_segment_label:\n", 1)[1].split(
            "      previous_annual_freeze_run_id:\n", 1
        )[0]
        self.assertIn("        required: true", section)
        self.assertIn("        type: choice", section)

    def test_prior_run_id_is_optional_string(self):
        section = self.workflow.split(
            "      previous_annual_freeze_run_id:\n", 1
        )[1].split("\npermissions:\n", 1)[0]
        self.assertIn("        required: false", section)
        self.assertIn("        type: string", section)

    def test_unreviewed_manual_ref_input_fails_review(self):
        tampered = self.workflow.replace(
            "      previous_annual_freeze_run_id:\n",
            "      unreviewed_ref:\n        type: string\n"
            "      previous_annual_freeze_run_id:\n", 1
        )
        self.assertIn("UNREVIEWED_MANUAL_INPUT", input_diagnostics(tampered))

    def test_duplicate_manual_input_fails_review(self):
        tampered = self.workflow.replace(
            "      previous_annual_freeze_run_id:\n",
            "      annual_segment_label:\n"
            "      previous_annual_freeze_run_id:\n", 1
        )
        self.assertIn("UNREVIEWED_MANUAL_INPUT", input_diagnostics(tampered))

    def test_missing_predecessor_input_fails_review(self):
        tampered = self.workflow.replace(
            "      previous_annual_freeze_run_id:\n",
            "      changed_predecessor:\n", 1
        )
        self.assertIn("UNREVIEWED_MANUAL_INPUT", input_diagnostics(tampered))

    def test_unreviewed_sha_input_expression_fails_review(self):
        expression = "$" + "{{ inputs.unreviewed_sha }}"
        tampered = self.workflow.replace(
            '--code-commit "$GITHUB_SHA"',
            '--code-commit "' + expression + '"', 1
        )
        self.assertIn("UNREVIEWED_INPUT_EXPRESSION",
                      input_diagnostics(tampered))

    def test_choice_to_string_change_fails_review(self):
        tampered = self.workflow.replace("        type: choice\n",
                                         "        type: string\n", 1)
        self.assertIn("INPUT_REQUIREMENT_TYPE_DRIFT",
                      input_diagnostics(tampered))

    def test_predecessor_optional_to_required_change_fails_review(self):
        key = "      previous_annual_freeze_run_id:\n"
        before, after = self.workflow.split(key, 1)
        self.assertIn("        required: false\n", after)
        tampered = before + key + after.replace(
            "        required: false\n", "        required: true\n", 1
        )
        self.assertIn("INPUT_REQUIREMENT_TYPE_DRIFT",
                      input_diagnostics(tampered))

    def test_nontext_source_never_passes_review(self):
        self.assertIn("NON_TEXT", input_diagnostics({}))
