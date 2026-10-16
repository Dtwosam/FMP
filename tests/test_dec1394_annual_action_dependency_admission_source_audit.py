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


def supply_chain_notes(workflow: str, requirements: str) -> tuple[str, ...]:
    notes = []
    for job in JOBS:
        part = job_text(workflow, job)
        checkout, install, authorize = step_positions(part)
        if checkout < install < authorize:
            notes.append("EXTERNAL_SETUP_BEFORE_RUNTIME_RECHECK_" + job)
    uses = re.findall(r"(?m)^\s+uses: ([^\n]+)$", workflow)
    if uses and all(re.fullmatch(r"actions/[a-z-]+@v[0-9]+", action) for action in uses):
        notes.append("EXTERNAL_ACTIONS_TAGGED_NOT_IMMUTABLE_SHA")
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

    def test_in_memory_install_after_gate_changes_order_diagnostic(self):
        a = job_text(self.workflow, "annual_preflight")
        # A synthetic move can change source ordering, but is not an approved
        # alternative installed workflow or a verified safe admission design.
        install_step = "      - name: Install pinned annual catalogue runtime\n"
        gate_step = "      - name: Require separately authorized annual catalogue execution\n"
        moved = a.replace(install_step, gate_step, 1).replace(
            gate_step + "        run: python -m pip install",
            install_step + "        run: python -m pip install", 1
        )
        # Do not interpret this superficial string mutation as runtime safety.
        self.assertIn("      - name: Checkout\n", moved)

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
