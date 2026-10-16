"""DEC-1385: deterministic in-memory ref race, NEVER a GitHub dispatch.

The fake allocator below is not the Actions platform, an API client or a
usable protected run dispatcher. Every ref, SHA and allocation is synthetic.
Only git show of committed source text is used for contextual assertions.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
VETTED = "a" * 40
UNREVIEWED = "b" * 40


class SyntheticMutableMain:
    """A minimal state-machine counterexample, not an implementation recipe."""

    def __init__(self):
        self.main = VETTED
        self.allocated_shas: list[str] = []

    def check(self) -> bool:
        return self.main == VETTED

    def advance(self, sha: str) -> None:
        self.main = sha

    def allocate(self) -> tuple[int, str]:
        self.allocated_shas.append(self.main)
        return (len(self.allocated_shas), self.main)


def source(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", "HEAD:" + path], cwd=ROOT, text=True
    )


class OfflineMutableMainRaceCannotAuthorizeProtectedRun385(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = source(".github/workflows/phase8a-annual-pattern-catalogue.yml")
        cls.runtime = source(
            "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py"
        )

    def test_existing_workflow_source_uses_main_manual_dispatch(self):
        self.assertIn("  workflow_dispatch:", self.workflow)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', self.workflow)

    def test_existing_2023_source_has_one_shot_identity(self):
        self.assertIn("EXPECTED_RUN_NUMBER = 385", self.runtime)
        self.assertIn("EXPECTED_RUN_ATTEMPT = 1", self.runtime)
        self.assertIn("RETRY_AUTHORIZED = False", self.runtime)
        self.assertIn("RERUN_AUTHORIZED = False", self.runtime)

    def test_uncontended_synthetic_precheck_does_not_suffice_as_contract(self):
        m = SyntheticMutableMain()
        self.assertTrue(m.check())
        self.assertEqual(m.allocate(), (1, VETTED))

    def test_mutation_between_check_and_allocation_selects_different_sha(self):
        m = SyntheticMutableMain()
        self.assertTrue(m.check())
        m.advance(UNREVIEWED)
        self.assertEqual(m.allocate(), (1, UNREVIEWED))

    def test_after_allocation_mismatch_cannot_restore_synthetic_first_slot(self):
        m = SyntheticMutableMain()
        self.assertTrue(m.check())
        m.advance(UNREVIEWED)
        allocated = m.allocate()
        self.assertNotEqual(allocated[1], VETTED)
        self.assertEqual(len(m.allocated_shas), 1)

    def test_retry_changes_allocated_attempt_counter_in_model(self):
        m = SyntheticMutableMain()
        self.assertTrue(m.check())
        m.advance(UNREVIEWED)
        m.allocate()
        m.advance(VETTED)
        self.assertEqual(m.allocate(), (2, VETTED))
        self.assertEqual(len(m.allocated_shas), 2)

    def test_hex_shape_does_not_identify_approved_sha(self):
        for sha in (VETTED, UNREVIEWED):
            self.assertEqual(len(sha), 40)
            self.assertEqual(int(sha, 16) >= 0, True)
        self.assertNotEqual(VETTED, UNREVIEWED)

    def test_mutable_ref_observation_can_change_after_last_local_check(self):
        m = SyntheticMutableMain()
        self.assertTrue(m.check())
        m.advance(UNREVIEWED)
        self.assertFalse(m.check())
        m.advance(VETTED)
        self.assertTrue(m.check())
        # The returned true does not prove no intervening state existed.
        self.assertEqual(m.main, VETTED)

    def test_immutable_source_model_stays_stable_only_by_separate_assumption(self):
        immutable_tag_sha = VETTED
        mutable_main = SyntheticMutableMain()
        self.assertTrue(mutable_main.check())
        mutable_main.advance(UNREVIEWED)
        self.assertEqual(immutable_tag_sha, VETTED)
        self.assertNotEqual(mutable_main.main, immutable_tag_sha)

    def test_postcheckout_gate_is_not_preallocation_server_admission(self):
        for name in ("annual_preflight", "annual_cell", "annual_freeze"):
            section = self.workflow.split("  " + name + ":\n", 1)[1]
            if name == "annual_preflight":
                section = section.split("  annual_cell:\n", 1)[0]
            elif name == "annual_cell":
                section = section.split("  annual_freeze:\n", 1)[0]
            with self.subTest(job=name):
                self.assertLess(
                    section.index("- name: Checkout"),
                    section.index("- name: Require exact merged main manual dispatch"),
                )
