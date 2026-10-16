"""DEC-1416: fail closed on unexpected annual workflow dispatch triggers.

Only reads committed source via git show. Never dispatches any workflow,
authenticates an admin lock, fetches original archives, or opens trading.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_OPTIONS = tuple(str(y) for y in range(2015, 2026)) + (
    "2026_YTD_TO_2026_08_20",
)
EXPECTED_INPUTS = ("annual_segment_label", "previous_annual_freeze_run_id")


def event_source_review(source: object) -> tuple[str, ...]:
    if type(source) is not str:
        return ("NON_TEXT",)
    if source.count("\npermissions:\n") != 1:
        return ("WORKFLOW_EVENT_BOUNDARY_UNREVIEWED",)
    header = source.split("\npermissions:\n", 1)[0]
    issues = []
    if re.findall(r"(?m)^on:$", header) != ["on:"]:
        return ("WORKFLOW_EVENT_TRIGGER_SHAPE_UNREVIEWED",)
    event = header.split("\non:\n", 1)[1]
    triggers = re.findall(r"(?m)^  ([a-z0-9_-]+):\s*$", event)
    if triggers != ["workflow_dispatch"]:
        issues.append("UNEXPECTED_WORKFLOW_TRIGGER_SOURCE")
    if re.findall(r"(?m)^    inputs:$", event) != ["    inputs:"]:
        issues.append("EVENT_INPUT_CONTAINER_UNREVIEWED")
    inputs = re.findall(r"(?m)^      ([a-z0-9_]+):$", event)
    if tuple(inputs) != EXPECTED_INPUTS:
        issues.append("EVENT_INPUT_INVENTORY_UNREVIEWED")
    options = tuple(re.findall(r'(?m)^          - "([^"]+)"$', event))
    if options != EXPECTED_OPTIONS:
        issues.append("EVENT_SEGMENT_OPTIONS_DRIFT")
    try:
        segment = event.split("      annual_segment_label:\n", 1)[1].split(
            "      previous_annual_freeze_run_id:\n", 1)[0]
        previous = event.split("      previous_annual_freeze_run_id:\n", 1)[1]
        if segment.count("        required: true\n") != 1 or (
                segment.count("        type: choice\n") != 1):
            issues.append("EVENT_SEGMENT_INPUT_SHAPE_DRIFT")
        if previous.count("        required: false\n") != 1 or (
                previous.count("        type: string\n") != 1):
            issues.append("EVENT_PREDECESSOR_INPUT_SHAPE_DRIFT")
    except IndexError:
        issues.append("EVENT_INPUT_BLOCKS_UNREVIEWED")
    return tuple(sorted(set(issues)))


class AnnualManualTriggerListCannotAuthorizeRun385(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )

    def test_checked_in_event_gate_inventory_matches_reviewed_source(self):
        self.assertEqual(event_source_review(self.workflow), ())

    def test_current_manual_dispatch_is_only_source_trigger(self):
        head = self.workflow.split("\npermissions:\n", 1)[0]
        self.assertEqual(
            re.findall(r"(?m)^  ([a-z0-9_-]+):$", head),
            ["workflow_dispatch"],
        )

    def test_added_push_trigger_requires_review(self):
        changed = self.workflow.replace(
            "  workflow_dispatch:\n",
            "  push:\n  workflow_dispatch:\n", 1)
        self.assertIn("UNEXPECTED_WORKFLOW_TRIGGER_SOURCE",
                      event_source_review(changed))

    def test_added_schedule_trigger_requires_review(self):
        changed = self.workflow.replace(
            "  workflow_dispatch:\n",
            "  schedule:\n  workflow_dispatch:\n", 1)
        self.assertIn("UNEXPECTED_WORKFLOW_TRIGGER_SOURCE",
                      event_source_review(changed))

    def test_added_pull_request_trigger_requires_review(self):
        changed = self.workflow.replace(
            "  workflow_dispatch:\n",
            "  pull_request:\n  workflow_dispatch:\n", 1)
        self.assertIn("UNEXPECTED_WORKFLOW_TRIGGER_SOURCE",
                      event_source_review(changed))

    def test_added_workflow_call_requires_review(self):
        changed = self.workflow.replace(
            "  workflow_dispatch:\n",
            "  workflow_call:\n  workflow_dispatch:\n", 1)
        self.assertIn("UNEXPECTED_WORKFLOW_TRIGGER_SOURCE",
                      event_source_review(changed))

    def test_duplicate_event_root_does_not_pass(self):
        changed = self.workflow.replace(
            "\npermissions:\n", "\non:\n  push:\n\npermissions:\n", 1)
        self.assertIn("WORKFLOW_EVENT_TRIGGER_SHAPE_UNREVIEWED",
                      event_source_review(changed))

    def test_replacing_event_root_with_inline_list_requires_review(self):
        changed = self.workflow.replace(
            "\non:\n", "\non: [workflow_dispatch, push]\n", 1)
        self.assertIn("WORKFLOW_EVENT_TRIGGER_SHAPE_UNREVIEWED",
                      event_source_review(changed))

    def test_extra_input_name_requires_review(self):
        changed = self.workflow.replace(
            "      previous_annual_freeze_run_id:\n",
            "      unreviewed_input:\n"
            "      previous_annual_freeze_run_id:\n", 1)
        self.assertIn("EVENT_INPUT_INVENTORY_UNREVIEWED",
                      event_source_review(changed))

    def test_new_segment_option_requires_review(self):
        changed = self.workflow.replace(
            '          - "2025"\n',
            '          - "2025"\n          - "2030"\n', 1)
        self.assertIn("EVENT_SEGMENT_OPTIONS_DRIFT",
                      event_source_review(changed))

    def test_previous_freeze_id_becoming_required_requires_review(self):
        changed = self.workflow.replace(
            "      previous_annual_freeze_run_id:\n"
            "        description: Required prior annual-catalogue run id for every segment after 2015\n"
            "        required: false\n",
            "      previous_annual_freeze_run_id:\n"
            "        description: Required prior annual-catalogue run id for every segment after 2015\n"
            "        required: true\n", 1)
        self.assertIn("EVENT_PREDECESSOR_INPUT_SHAPE_DRIFT",
                      event_source_review(changed))

    def test_nontext_review_input_is_rejected(self):
        self.assertEqual(event_source_review(None), ("NON_TEXT",))
