"""DEC-1394 offline audit of source-order and dependency identity limitations.

This reads two committed Git blobs only; it neither installs dependencies nor
runs any annual workflow or touches protected data, runner policy, or trading.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
JOBS = ("annual_preflight", "annual_cell", "annual_freeze")
INSTALL = "python -m pip install -r requirements/exp061-discovery-run.txt -e ."
SETUP = "actions/setup-python@v6"
CHECKOUT = "actions/checkout@v6"


def job_text(source: str, name: str) -> str:
    if name not in JOBS:
        raise ValueError("unsupported job")
    i = JOBS.index(name)
    block = source.split("  " + name + ":\n", 1)[1]
    if i + 1 < len(JOBS):
        block = block.split("  " + JOBS[i + 1] + ":\n", 1)[0]
    return block


def step_positions(job: str) -> tuple[int, int, int]:
    check = ("- name: Require separately authorized annual catalogue execution"
             if "- name: Require separately authorized annual catalogue execution" in job
             else "- name: Recheck separately authorized annual catalogue execution")
    return (job.index("- name: Checkout"),
            job.index("- name: Install pinned annual catalogue runtime"),
            job.index(check))


def move_named_step_before(job: str, selected: str, before: str) -> str:
    """In-memory source-step reordering, never applied to installed YAML."""
    marker = "      - name: " + selected + "\n"
    destination = "      - name: " + before + "\n"
    start = job.index(marker)
    end = job.find("      - name: ", start + len(marker))
    if end < 0:
        end = len(job)
    chunk = job[start:end]
    remainder = job[:start] + job[end:]
    position = remainder.index(destination)
    return remainder[:position] + chunk + remainder[position:]


def supply_chain_notes(workflow: str, requirements: str) -> tuple[str, ...]:
    notes = []
    for job in JOBS:
        part = job_text(workflow, job)
        required_steps = (
            "Checkout",
            "Install pinned annual catalogue runtime",
            ("Require separately authorized annual catalogue execution"
             if job == "annual_preflight"
             else "Recheck separately authorized annual catalogue execution"),
        )
        if any(part.count("      - name: " + step + "\n") != 1
               for step in required_steps):
            notes.append("MISSING_OR_DUPLICATE_RUNTIME_STEP_" + job)
            continue
        checkout, install, authorize = step_positions(part)
        if checkout < install < authorize:
            notes.append("EXTERNAL_SETUP_BEFORE_RUNTIME_RECHECK_" + job)
    uses = re.findall(r"(?m)^\s+uses: ([^\n]+)$", workflow)
    expected = {
        "actions/checkout@v6": 3,
        "actions/setup-python@v6": 3,
        "actions/upload-artifact@v6": 3,
        "actions/download-artifact@v6": 1,
    }
    if len(uses) != 10 or {
            action: uses.count(action) for action in expected} != expected:
        notes.append("EXTERNAL_ACTION_REFERENCE_INVENTORY_DRIFT")
    if uses and all(re.fullmatch(r"actions/[a-z-]+@v[0-9]+", action)
                    for action in uses):
        notes.append("EXTERNAL_ACTIONS_TAGGED_NOT_IMMUTABLE_SHA")
    else:
        notes.append("EXTERNAL_ACTION_REFERENCE_UNREVIEWED")
    lines = [x for x in requirements.splitlines() if x.strip()]
    if lines and all(re.fullmatch(r"[a-z0-9-]+==[0-9.]+", x) for x in lines):
        notes.append("DEPENDENCY_VERSIONS_PINNED_WITHOUT_HASHES")
    return tuple(notes)


class AnnualRunnerSetupCannotEstablishPreallocationTrust(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )
        cls.requirements = subprocess.check_output(
            ["git", "show", "HEAD:requirements/exp061-discovery-run.txt"],
            cwd=ROOT, text=True,
        )

    def test_all_three_jobs_checkout_and_install_before_runtime_recheck(self):
        for name in JOBS:
            with self.subTest(job=name):
                checkout, install, check = step_positions(
                    job_text(self.workflow, name))
                self.assertLess(checkout, install)
                self.assertLess(install, check)

    def test_all_three_jobs_install_same_pip_requirements_and_editable_project(self):
        for name in JOBS:
            self.assertEqual(job_text(self.workflow, name).count(INSTALL), 1)

    def test_current_setup_python_version_is_explicit_source_literal(self):
        for name in JOBS:
            self.assertIn('python-version: "3.12.14"', job_text(self.workflow, name))

    def test_current_external_actions_use_major_version_tags(self):
        matches = re.findall(r"(?m)^\s+uses: ([^\n]+)$", self.workflow)
        self.assertEqual(len(matches), 10)
        self.assertTrue(all(re.fullmatch(r"actions/[a-z-]+@v[0-9]+", s)
                            for s in matches))

    def test_current_dependency_versions_have_exact_reviewed_literals(self):
        self.assertEqual(self.requirements.splitlines(), [
            "polars==1.44.2", "polars-runtime-32==1.44.2",
        ])

    def test_current_pip_install_source_does_not_require_hashes(self):
        self.assertNotIn("--require-hashes", self.workflow)
        self.assertNotIn("--hash=sha256:", self.requirements)

    def test_source_risks_are_reported_distinctly_from_admission(self):
        notes = supply_chain_notes(self.workflow, self.requirements)
        for name in JOBS:
            self.assertIn("EXTERNAL_SETUP_BEFORE_RUNTIME_RECHECK_" + name, notes)
        self.assertIn("EXTERNAL_ACTIONS_TAGGED_NOT_IMMUTABLE_SHA", notes)
        self.assertIn("DEPENDENCY_VERSIONS_PINNED_WITHOUT_HASHES", notes)

    def test_in_memory_gate_moved_before_install_changes_order_diagnostic(self):
        part = job_text(self.workflow, "annual_preflight")
        moved = move_named_step_before(
            part,
            "Require separately authorized annual catalogue execution",
            "Install pinned annual catalogue runtime",
        )
        self.assertNotEqual(moved, part)
        checkout, install, gate = step_positions(moved)
        self.assertLess(checkout, gate)
        self.assertLess(gate, install)
        mutated = self.workflow.replace(part, moved, 1)
        self.assertNotIn(
            "EXTERNAL_SETUP_BEFORE_RUNTIME_RECHECK_annual_preflight",
            supply_chain_notes(mutated, self.requirements),
        )

    def test_unhashed_dependency_literals_are_not_protected_identity(self):
        changed = self.requirements.replace(
            "polars==1.44.2", "polars==1.44.3", 1
        )
        self.assertNotEqual(changed, self.requirements)
        self.assertNotIn("--hash=sha256:", changed)

    def test_no_synthetic_source_diagnostic_can_certify_dispatch(self):
        notes = supply_chain_notes(self.workflow, self.requirements)
        self.assertNotIn("PROTECTED_2023_DISPATCH_AUTHORIZED", notes)
        self.assertGreaterEqual(len(notes), 5)

    def test_duplicate_install_step_is_rejected_by_source_inventory(self):
        name = "      - name: Install pinned annual catalogue runtime\n"
        changed = self.workflow.replace(name, name + name, 1)
        self.assertIn("MISSING_OR_DUPLICATE_RUNTIME_STEP_annual_preflight",
                      supply_chain_notes(changed, self.requirements))

    def test_duplicate_runtime_recheck_is_rejected_by_source_inventory(self):
        name = "      - name: Recheck separately authorized annual catalogue execution\n"
        changed = self.workflow.replace(name, name + name, 1)
        self.assertIn("MISSING_OR_DUPLICATE_RUNTIME_STEP_annual_cell",
                      supply_chain_notes(changed, self.requirements))

    def test_missing_checkout_is_rejected_by_source_inventory(self):
        name = "      - name: Checkout\n"
        changed = self.workflow.replace(name, "      - name: Unknown\n", 1)
        self.assertIn("MISSING_OR_DUPLICATE_RUNTIME_STEP_annual_preflight",
                      supply_chain_notes(changed, self.requirements))

    def test_synthetic_cell_gate_move_changes_only_cell_order_diagnostic(self):
        part = job_text(self.workflow, "annual_cell")
        moved = move_named_step_before(
            part,
            "Recheck separately authorized annual catalogue execution",
            "Install pinned annual catalogue runtime",
        )
        changed = self.workflow.replace(part, moved, 1)
        notes = supply_chain_notes(changed, self.requirements)
        self.assertNotIn(
            "EXTERNAL_SETUP_BEFORE_RUNTIME_RECHECK_annual_cell", notes
        )
        self.assertIn(
            "EXTERNAL_SETUP_BEFORE_RUNTIME_RECHECK_annual_freeze", notes
        )

    def test_canonical_action_inventory_has_no_silent_drift(self):
        notes = supply_chain_notes(self.workflow, self.requirements)
        self.assertNotIn("EXTERNAL_ACTION_REFERENCE_INVENTORY_DRIFT", notes)
        self.assertNotIn("EXTERNAL_ACTION_REFERENCE_UNREVIEWED", notes)
        self.assertIn("EXTERNAL_ACTIONS_TAGGED_NOT_IMMUTABLE_SHA", notes)

    def test_changed_checkout_major_version_requires_review(self):
        changed = self.workflow.replace(
            "uses: actions/checkout@v6", "uses: actions/checkout@v7", 1)
        self.assertIn("EXTERNAL_ACTION_REFERENCE_INVENTORY_DRIFT",
                      supply_chain_notes(changed, self.requirements))

    def test_changed_setup_major_version_requires_review(self):
        changed = self.workflow.replace(
            "uses: actions/setup-python@v6", "uses: actions/setup-python@v7", 1)
        self.assertIn("EXTERNAL_ACTION_REFERENCE_INVENTORY_DRIFT",
                      supply_chain_notes(changed, self.requirements))

    def test_sha_pinned_candidate_is_unreviewed_not_automatically_authorized(self):
        changed = self.workflow.replace(
            "uses: actions/checkout@v6",
            "uses: actions/checkout@" + "a" * 40, 1)
        notes = supply_chain_notes(changed, self.requirements)
        self.assertIn("EXTERNAL_ACTION_REFERENCE_INVENTORY_DRIFT", notes)
        self.assertIn("EXTERNAL_ACTION_REFERENCE_UNREVIEWED", notes)
        self.assertNotIn("PROTECTED_2023_DISPATCH_AUTHORIZED", notes)

    def test_unknown_action_owner_does_not_erase_risk(self):
        changed = self.workflow.replace(
            "uses: actions/checkout@v6", "uses: unreviewed/checkout@v6", 1)
        notes = supply_chain_notes(changed, self.requirements)
        self.assertIn("EXTERNAL_ACTION_REFERENCE_INVENTORY_DRIFT", notes)
        self.assertIn("EXTERNAL_ACTION_REFERENCE_UNREVIEWED", notes)

    def test_duplicate_uses_scalar_is_not_silent(self):
        changed = self.workflow.replace(
            "        uses: actions/checkout@v6\n",
            "        uses: actions/checkout@v6\n"
            "        uses: actions/checkout@v6\n", 1)
        self.assertIn("EXTERNAL_ACTION_REFERENCE_INVENTORY_DRIFT",
                      supply_chain_notes(changed, self.requirements))

    def test_removed_action_reference_is_not_silent(self):
        changed = self.workflow.replace(
            "        uses: actions/checkout@v6\n", "", 1)
        self.assertIn("EXTERNAL_ACTION_REFERENCE_INVENTORY_DRIFT",
                      supply_chain_notes(changed, self.requirements))

    def test_malformed_tag_reference_is_unreviewed(self):
        changed = self.workflow.replace(
            "uses: actions/checkout@v6",
            "uses: actions/checkout@not-reviewed", 1)
        self.assertIn("EXTERNAL_ACTION_REFERENCE_UNREVIEWED",
                      supply_chain_notes(changed, self.requirements))

    def test_no_actions_reference_counterexample_establishes_run_admission(self):
        changed = self.workflow.replace(
            "uses: actions/upload-artifact@v6",
            "uses: actions/upload-artifact@v7", 1)
        notes = supply_chain_notes(changed, self.requirements)
        self.assertIn("EXTERNAL_ACTION_REFERENCE_INVENTORY_DRIFT", notes)
        self.assertNotIn("PROTECTED_2023_DISPATCH_AUTHORIZED", notes)
