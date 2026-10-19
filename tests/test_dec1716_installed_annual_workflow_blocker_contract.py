"""DEC-1716: source-pinned blocker contract for installed 2023 annual workflow.

Observes the frozen main-only, post-checkout source; never authorizes execution.
This test intentionally needs a separately reviewed rebaseline if workflow changes.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase8a-annual-pattern-catalogue.yml"
PINNED_GIT_BLOB = "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
JOBS = ("annual_preflight", "annual_cell", "annual_freeze")
AFTER_INSTALL_AUTH = {
    "annual_preflight": "Require separately authorized annual catalogue execution",
    "annual_cell": "Recheck separately authorized annual catalogue execution",
    "annual_freeze": "Recheck separately authorized annual catalogue execution",
}
FIRST_EVIDENCE = {
    "annual_preflight": "Fetch exact accepted EXP-044 source snapshots",
    "annual_cell": "Download exact accepted EXP-044 feature/outcome/evidence artifacts",
    "annual_freeze": "Download all 18 annual catalogue cell products",
}


def _source() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") +
                        b"\x00" + raw).hexdigest()


def _job_sections(source: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in source.splitlines():
        match = re.fullmatch(r"  (annual_[a-z]+):", line)
        if match:
            current = match.group(1)
            if current in sections:
                raise AssertionError("Duplicate job definition")
            sections[current] = []
        elif current is not None and line and not line.startswith(" "):
            current = None
        if current is not None:
            sections[current].append(line)
    return {job: "\n".join(lines) for job, lines in sections.items()}


def _steps(job_source: str) -> list[str]:
    return [match.group(1) for match in
            (re.fullmatch(r"      - name: (.+)", line)
             for line in job_source.splitlines())
            if match]


class InstalledAnnualWorkflowBlockerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = _source()
        cls.jobs = _job_sections(cls.source)

    def test_exact_installed_workflow_blob_is_pinned(self):
        self.assertEqual(_git_blob_sha(WORKFLOW.read_bytes()), PINNED_GIT_BLOB)

    def test_exact_three_job_inventory_and_no_duplicate_jobs(self):
        self.assertEqual(set(self.jobs), set(JOBS))
        self.assertEqual(len(self.jobs), 3)

    def test_manual_event_and_frozen_2023_input_remain_explicit(self):
        self.assertIn("  workflow_dispatch:", self.source)
        self.assertIn("      annual_segment_label:", self.source)
        self.assertIn('          - "2023"', self.source)
        self.assertIn("      previous_annual_freeze_run_id:", self.source)

    def test_read_only_github_job_permissions_are_not_a_ref_lock(self):
        before_jobs = self.source.split("\njobs:\n", 1)[0]
        self.assertIn("permissions:\\n  contents: read\\n  actions: read", before_jobs)
        self.assertNotIn("contents: write", before_jobs)
        self.assertNotIn("actions: write", before_jobs)

    def test_checkout_is_first_step_in_every_job(self):
        for job in JOBS:
            with self.subTest(job=job):
                steps = _steps(self.jobs[job])
                self.assertGreaterEqual(len(steps), 5)
                self.assertEqual(steps[0], "Checkout")
                self.assertEqual(len(steps), len(set(steps)))

    def test_main_ref_shell_guard_is_post_checkout_in_every_job(self):
        for job in JOBS:
            with self.subTest(job=job):
                steps = _steps(self.jobs[job])
                self.assertEqual(steps[1],
                                 "Require exact merged main manual dispatch")
                self.assertIn('test "$GITHUB_REF" = "refs/heads/main"',
                              self.jobs[job])
                self.assertLess(steps.index("Checkout"),
                                steps.index("Require exact merged main manual dispatch"))

    def test_jobs_lack_precheckout_job_level_admission_condition(self):
        for job in JOBS:
            with self.subTest(job=job):
                # A step-level `if` does not gate checkout.
                self.assertNotRegex(self.jobs[job], r"(?m)^    if:")

    def test_setup_and_install_precede_runtime_authorization_in_all_jobs(self):
        for job in JOBS:
            with self.subTest(job=job):
                steps = _steps(self.jobs[job])
                self.assertLess(steps.index("Set up Python"),
                                steps.index("Install pinned annual catalogue runtime"))
                self.assertLess(steps.index("Install pinned annual catalogue runtime"),
                                steps.index(AFTER_INSTALL_AUTH[job]))

    def test_preflight_metadata_fetch_is_before_execution_authorization(self):
        steps = _steps(self.jobs["annual_preflight"])
        self.assertLess(
            steps.index(FIRST_EVIDENCE["annual_preflight"]),
            steps.index(AFTER_INSTALL_AUTH["annual_preflight"]),
        )

    def test_cell_and_freeze_authorization_still_precede_download(self):
        for job in ("annual_cell", "annual_freeze"):
            with self.subTest(job=job):
                steps = _steps(self.jobs[job])
                self.assertLess(steps.index(AFTER_INSTALL_AUTH[job]),
                                steps.index(FIRST_EVIDENCE[job]))

    def test_exact_18_cell_matrix_inventory(self):
        block = self.jobs["annual_cell"]
        symbols = re.findall(r"(?m)^          - symbol: (\w+)$", block)
        timeframes = re.findall(r"(?m)^            timeframe: (\S+)$", block)
        horizons = re.findall(r"(?m)^            horizon: (\d+)$", block)
        self.assertEqual(len(symbols), 18)
        self.assertEqual(set(symbols), {"EURUSD", "GBPUSD", "USDJPY"})
        self.assertEqual(len(timeframes), 18)
        self.assertEqual(set(timeframes), {"5m", "15m", "1h"})
        self.assertEqual(len(horizons), 18)
        self.assertEqual(set(horizons), {"60", "240"})
        self.assertEqual(
            set(zip(symbols, timeframes, horizons)),
            {(symbol, timeframe, horizon)
             for symbol in ("EURUSD", "GBPUSD", "USDJPY")
             for timeframe in ("5m", "15m", "1h")
             for horizon in ("60", "240")},
        )

    def test_blocker_not_mistaken_for_dispatch_approval(self):
        # This is evidence of unsafe as-installed ordering, NOT an allow-list.
        assert set(self.jobs) == set(JOBS)
        must_still_be_blocked = all(
            _steps(self.jobs[job])[0] == "Checkout" for job in JOBS
        )
        self.assertTrue(must_still_be_blocked)
        self.assertTrue((ROOT / "docs/dec1715-run385-owner-remediation-brief.md").is_file())
        self.assertIn("**Stop condition:**",
                      (ROOT / "docs/dec1715-run385-owner-remediation-brief.md")
                      .read_text(encoding="utf-8"))
