"""DEC-1409: actual checked-in annual Actions DAG and parallelism source.

No GitHub workflow is triggered, no annual job or protected evidence is
accessed, and all mutations are text-only source counterexamples.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
JOBS = ("annual_preflight", "annual_cell", "annual_freeze")


def job_source(source: str, name: str) -> str:
    if name not in JOBS:
        raise ValueError("unreviewed job")
    chunk = source.split("  " + name + ":\n", 1)[1]
    i = JOBS.index(name) + 1
    if i < len(JOBS):
        chunk = chunk.split("  " + JOBS[i] + ":\n", 1)[0]
    return chunk


def dependency_review(source: object) -> tuple[str, ...]:
    if type(source) is not str:
        return ("NON_TEXT",)
    expected = {"annual_preflight": [], "annual_cell": ["annual_preflight"],
                "annual_freeze": ["annual_cell"]}
    issues = []
    try:
        for name, valid in expected.items():
            job = job_source(source, name)
            # Require only the exact one-line dependency style in this
            # reviewed installed source; alternative YAML syntax needs review.
            needs = re.findall(r"(?m)^    needs: ([^\n]+)$", job)
            if needs != valid:
                issues.append(name + "_NEEDS_INVENTORY_DRIFT")
            if re.search(r"(?m)^    if:", job):
                issues.append(name + "_JOB_LEVEL_CONDITION_UNREVIEWED")
        cell = job_source(source, "annual_cell")
        fail_fast = re.findall(r"(?m)^      fail-fast: ([^\n]+)$", cell)
        parallel = re.findall(r"(?m)^      max-parallel: ([^\n]+)$", cell)
        if fail_fast != ["false"]:
            issues.append("CELL_FAIL_FAST_SOURCE_DRIFT")
        if parallel != ["3"]:
            issues.append("CELL_MAX_PARALLEL_SOURCE_DRIFT")
    except (IndexError, ValueError):
        return ("ANNUAL_JOB_SHAPE_MISSING",)
    return tuple(sorted(set(issues)))


class AnnualDagAndMatrixBoundDoNotAuthenticateProtectedRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )

    def test_current_workflow_has_no_dag_source_drift(self):
        self.assertEqual(dependency_review(self.workflow), ())

    def test_preflight_is_unconditional_job_source_with_no_needs(self):
        self.assertNotRegex(job_source(self.workflow, "annual_preflight"),
                            r"(?m)^    needs:")

    def test_cell_requires_preflight_and_freeze_requires_cell(self):
        self.assertIn("    needs: annual_preflight\n",
                      job_source(self.workflow, "annual_cell"))
        self.assertIn("    needs: annual_cell\n",
                      job_source(self.workflow, "annual_freeze"))

    def test_cell_is_at_most_three_parallel_with_failfast_false_in_source(self):
        cell = job_source(self.workflow, "annual_cell")
        self.assertIn("      max-parallel: 3\n", cell)
        self.assertIn("      fail-fast: false\n", cell)

    def test_cell_missing_preflight_dependency_fails_review(self):
        mutated = self.workflow.replace(
            "    needs: annual_preflight\n", "", 1,
        )
        self.assertIn("annual_cell_NEEDS_INVENTORY_DRIFT",
                      dependency_review(mutated))

    def test_freeze_unsupported_dependency_fails_review(self):
        mutated = self.workflow.replace(
            "    needs: annual_cell\n", "    needs: annual_preflight\n", 1,
        )
        self.assertIn("annual_freeze_NEEDS_INVENTORY_DRIFT",
                      dependency_review(mutated))

    def test_duplicate_needs_scalar_fails_review(self):
        mutated = self.workflow.replace(
            "    needs: annual_cell\n",
            "    needs: annual_cell\n    needs: annual_cell\n", 1,
        )
        self.assertIn("annual_freeze_NEEDS_INVENTORY_DRIFT",
                      dependency_review(mutated))

    def test_failfast_true_change_fails_source_review(self):
        mutated = self.workflow.replace(
            "      fail-fast: false\n", "      fail-fast: true\n", 1,
        )
        self.assertIn("CELL_FAIL_FAST_SOURCE_DRIFT",
                      dependency_review(mutated))

    def test_extra_parallel_workers_fail_source_review(self):
        mutated = self.workflow.replace(
            "      max-parallel: 3\n", "      max-parallel: 18\n", 1,
        )
        self.assertIn("CELL_MAX_PARALLEL_SOURCE_DRIFT",
                      dependency_review(mutated))

    def test_duplicate_parallelism_scalar_fails_source_review(self):
        mutated = self.workflow.replace(
            "      max-parallel: 3\n",
            "      max-parallel: 3\n      max-parallel: 3\n", 1,
        )
        self.assertIn("CELL_MAX_PARALLEL_SOURCE_DRIFT",
                      dependency_review(mutated))

    def test_unreviewed_job_level_always_condition_fails_review(self):
        mutated = self.workflow.replace(
            "  annual_freeze:\n",
            "  annual_freeze:\n    if: always()\n", 1,
        )
        self.assertIn("annual_freeze_JOB_LEVEL_CONDITION_UNREVIEWED",
                      dependency_review(mutated))

    def test_nontext_source_is_rejected(self):
        self.assertEqual(dependency_review([]), ("NON_TEXT",))
