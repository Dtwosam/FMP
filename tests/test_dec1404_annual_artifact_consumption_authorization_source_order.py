"""DEC-1404 read-only annual job artifact admission order diagnostics.

Every workflow is parsed as source text from a committed Git blob, and
mutation cases exist only in Python memory. No real annual jobs, artifacts,
credentials, GitHub Actions control-plane calls, or trading are invoked.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
JOBS = ("annual_preflight", "annual_cell", "annual_freeze")
GATE = {
    "annual_preflight": "Require separately authorized annual catalogue execution",
    "annual_cell": "Recheck separately authorized annual catalogue execution",
    "annual_freeze": "Recheck separately authorized annual catalogue execution",
}
SENSITIVE = {
    "annual_preflight": "Fetch exact prior annual freeze evidence",
    "annual_cell": "Download exact accepted EXP-044 feature/outcome/evidence artifacts",
    "annual_freeze": "Download all 18 annual catalogue cell products",
}
UPLOAD = {
    "annual_preflight": "Upload annual catalogue preflight evidence",
    "annual_cell": "Upload annual catalogue cell product",
    "annual_freeze": "Upload annual segment freeze evidence",
}


def section(source: str, name: str) -> str:
    if name not in JOBS:
        raise ValueError("invalid job name")
    marker = "  " + name + ":\n"
    tail = source.split(marker, 1)[1]
    next_idx = JOBS.index(name) + 1
    if next_idx < len(JOBS):
        tail = tail.split("  " + JOBS[next_idx] + ":\n", 1)[0]
    return tail


def steps(source: str, name: str) -> tuple[list[str], dict[str, str]]:
    raw = section(source, name)
    pieces = re.split(r"(?m)^      - name: ([^\n]+)\n", raw)
    return pieces[1::2], dict(zip(pieces[1::2], pieces[2::2]))


def source_order_issues(source: object) -> tuple[str, ...]:
    if type(source) is not str:
        return ("NOT_SOURCE_TEXT",)
    issues = []
    try:
        for job in JOBS:
            names, bodies = steps(source, job)
            if len(names) != len(set(names)):
                issues.append(job + "_DUPLICATE_STEP_NAME")
            expected = (GATE[job], SENSITIVE[job], UPLOAD[job])
            if any(names.count(x) != 1 for x in expected):
                issues.append(job + "_REQUIRED_STEP_INVENTORY_DRIFT")
                continue
            if names.index(GATE[job]) >= names.index(SENSITIVE[job]):
                issues.append(job + "_SENSITIVE_INPUT_BEFORE_RUNTIME_GATE")
            if names.index(GATE[job]) >= names.index(UPLOAD[job]):
                issues.append(job + "_PUBLISH_BEFORE_RUNTIME_GATE")
            if names.index(SENSITIVE[job]) >= names.index(UPLOAD[job]):
                issues.append(job + "_PUBLISH_BEFORE_CONSUMPTION")
            if job != "annual_preflight":
                if re.search(r"(?m)^        if: always\(\)$", bodies[UPLOAD[job]]):
                    issues.append(job + "_ALWAYS_PUBLISH_AFTER_FAILURE")
    except (ValueError, IndexError):
        return ("WORKFLOW_JOB_SOURCE_SHAPE_INVALID",)
    return tuple(sorted(set(issues)))


def move_step_before(source: str, job: str, step: str, target: str) -> str:
    raw = section(source, job)
    marker = "      - name: " + step + "\n"
    destination = "      - name: " + target + "\n"
    left = raw.index(marker)
    right = raw.find("      - name: ", left + len(marker))
    if right == -1:
        right = len(raw)
    fragment = raw[left:right]
    remainder = raw[:left] + raw[right:]
    insert_at = remainder.index(destination)
    moved = remainder[:insert_at] + fragment + remainder[insert_at:]
    return source.replace(raw, moved, 1)


class AnnualSourceJobGatesDoNotConstituteServerSideAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )

    def test_current_sensitive_consumption_order_review_has_no_drift(self):
        self.assertEqual(source_order_issues(self.workflow), ())

    def test_prior_freeze_fetch_follows_separate_runtime_check(self):
        names, _ = steps(self.workflow, "annual_preflight")
        self.assertLess(names.index(GATE["annual_preflight"]),
                        names.index(SENSITIVE["annual_preflight"]))

    def test_cell_archive_download_follows_separate_runtime_recheck(self):
        names, _ = steps(self.workflow, "annual_cell")
        self.assertLess(names.index(GATE["annual_cell"]),
                        names.index(SENSITIVE["annual_cell"]))

    def test_freeze_product_download_follows_separate_runtime_recheck(self):
        names, _ = steps(self.workflow, "annual_freeze")
        self.assertLess(names.index(GATE["annual_freeze"]),
                        names.index(SENSITIVE["annual_freeze"]))

    def test_preflight_raw_metadata_fetch_still_precedes_runtime_check(self):
        names, _ = steps(self.workflow, "annual_preflight")
        self.assertLess(
            names.index("Fetch exact accepted EXP-044 source snapshots"),
            names.index(GATE["annual_preflight"]),
        )

    def test_prior_freeze_moved_before_gate_fails_source_review(self):
        changed = move_step_before(self.workflow, "annual_preflight",
                                   SENSITIVE["annual_preflight"],
                                   GATE["annual_preflight"])
        self.assertIn("annual_preflight_SENSITIVE_INPUT_BEFORE_RUNTIME_GATE",
                      source_order_issues(changed))

    def test_cell_archive_download_moved_before_gate_fails_source_review(self):
        changed = move_step_before(self.workflow, "annual_cell",
                                   SENSITIVE["annual_cell"], GATE["annual_cell"])
        self.assertIn("annual_cell_SENSITIVE_INPUT_BEFORE_RUNTIME_GATE",
                      source_order_issues(changed))

    def test_freeze_download_moved_before_gate_fails_source_review(self):
        changed = move_step_before(self.workflow, "annual_freeze",
                                   SENSITIVE["annual_freeze"], GATE["annual_freeze"])
        self.assertIn("annual_freeze_SENSITIVE_INPUT_BEFORE_RUNTIME_GATE",
                      source_order_issues(changed))

    def test_adding_always_to_cell_publication_is_detected(self):
        name = "      - name: " + UPLOAD["annual_cell"] + "\n"
        changed = self.workflow.replace(name, name + "        if: always()\n", 1)
        self.assertIn("annual_cell_ALWAYS_PUBLISH_AFTER_FAILURE",
                      source_order_issues(changed))

    def test_adding_always_to_freeze_publication_is_detected(self):
        name = "      - name: " + UPLOAD["annual_freeze"] + "\n"
        changed = self.workflow.replace(name, name + "        if: always()\n", 1)
        self.assertIn("annual_freeze_ALWAYS_PUBLISH_AFTER_FAILURE",
                      source_order_issues(changed))

    def test_missing_runtime_check_is_not_misreported_as_safe(self):
        marker = "      - name: " + GATE["annual_preflight"] + "\n"
        changed = self.workflow.replace(marker, "      - name: Unknown gate\n", 1)
        self.assertIn("annual_preflight_REQUIRED_STEP_INVENTORY_DRIFT",
                      source_order_issues(changed))

    def test_duplicate_cell_gate_is_not_misreported_as_safe(self):
        marker = "      - name: " + GATE["annual_cell"] + "\n"
        changed = self.workflow.replace(marker, marker + marker, 1)
        self.assertIn("annual_cell_DUPLICATE_STEP_NAME",
                      source_order_issues(changed))
        self.assertIn("annual_cell_REQUIRED_STEP_INVENTORY_DRIFT",
                      source_order_issues(changed))

    def test_unexpected_nontext_source_is_rejected(self):
        self.assertEqual(source_order_issues({}), ("NOT_SOURCE_TEXT",))
