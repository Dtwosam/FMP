"""DEC-1721: static source-bound checklist integrity, NEVER an admin proof.

Tests only documentation and fixed upstream offline constants. A PASS shows
the reviewer handoff is complete as text, not that GitHub is protected.
"""
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_admin_lock_handoff import (
    REQUIRED_HUMAN_PROOFS,
)
from fmp.discovery.annual_pattern_catalogue_2023_lock_witness_coverage import (
    INTERVALS,
    REQUIRED_CLAIMS,
)


DOC = (Path(__file__).resolve().parents[1] /
       "docs/dec1721-independent-admin-witness-handoff-contract.md")


class IndependentAdminWitnessHandoffSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = DOC.read_text(encoding="utf-8")

    def test_all_dec613_human_proof_ids_are_in_document(self):
        self.assertEqual(len(REQUIRED_HUMAN_PROOFS), 10)
        for proof in REQUIRED_HUMAN_PROOFS:
            with self.subTest(proof=proof):
                self.assertIn("- [ ] `" + proof + "`", self.document)

    def test_all_dec620_continuity_intervals_are_listed(self):
        self.assertEqual(len(INTERVALS), 4)
        for interval in INTERVALS:
            with self.subTest(interval=interval):
                self.assertIn("- `" + interval + "`", self.document)

    def test_all_dec620_enforcement_claims_are_listed(self):
        self.assertEqual(len(REQUIRED_CLAIMS), 6)
        for claim in REQUIRED_CLAIMS:
            with self.subTest(claim=claim):
                self.assertIn("- `" + claim + "`", self.document)

    def test_frozen_historical_run_and_distinct_one_shot_identity(self):
        self.assertIn("2022 run 384", self.document)
        self.assertIn("2023/run385/attempt1", self.document)
        self.assertIn("no retry, rerun, replacement or attempt 2", self.document)

    def test_independent_expected_identity_not_runner_self_attestation(self):
        for marker in ("independently of", "github.ref", "github.sha",
                       "runtime SHA", "GitHub Actions write identities"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.document)

    def test_all_three_required_jobs_and_stages(self):
        for marker in ("annual_preflight", "annual_cell", "annual_freeze",
                       "precheckout", "preinstall", "preaccess",
                       "18 cell jobs"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.document)

    def test_actual_runner_os_isolation_is_not_synthetic_ci(self):
        for marker in ("runner-host isolation", "mount/UID/namespace",
                       "artifact publisher", "container test skips"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.document)

    def test_human_review_packet_cannot_claim_authorization(self):
        for marker in ("release_status=BLOCKED", "MISSING — BLOCKED",
                       "UNVERIFIED — BLOCKED", "NOT GIVEN — BLOCKED",
                       "cannot verify", "incapable of producing"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.document)

    def test_no_executable_dispatch_examples_in_review_packet(self):
        for forbidden in ("gh workflow run ", "gh api --method POST",
                          "git push", "git tag -f", "git push --force"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.document)

    def test_do_not_request_secret_values(self):
        for marker in ("Do not submit production tokens", "no retry",
                       "No protected 2023 research"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.document)

    def test_no_phase8b_or_demo_auto_promotion(self):
        for marker in ("No automatic Phase 8B", "live Phase 11",
                       "strategy", "BLOCKED"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.document)

    def test_handoff_is_draft_not_release(self):
        self.assertIn("DRAFT / NEVER MERGE / NEVER PROMOTE", self.document)
        self.assertIn("SOURCE-ONLY PREPARATION", self.document)
