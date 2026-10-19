"""DEC-1732: reconcile published Phase8A boundaries across source-only docs.

This comparison is not independent current GitHub/admin or economic evidence.
No workflow, protected source, broker or annual data read.
"""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/dec1726-phase8a-sourceonly-segment-gate-ledger.json"
STATE = ROOT / "docs/project-state.md"
BUILD = ROOT / "docs/build-order.md"
OWNER = ROOT / "docs/dec1715-run385-owner-remediation-brief.md"
ECONOMICS = ROOT / "docs/dec1715-economic-evidence-milestone-ledger.md"
HANDOFF = ROOT / "docs/dec1721-independent-admin-witness-handoff-contract.md"


class Phase8ACrossDocumentSourceOnlyBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.state = STATE.read_text(encoding="utf-8")
        cls.build = BUILD.read_text(encoding="utf-8")
        cls.owner = OWNER.read_text(encoding="utf-8")
        cls.economics = ECONOMICS.read_text(encoding="utf-8")
        cls.handoff = HANDOFF.read_text(encoding="utf-8")

    def test_current_state_labels_phase8a_not_live_trading(self):
        self.assertIn("**Current phase:** Phase 8A", self.state)
        self.assertIn("Phase 8A annual catalogue discovery", self.owner)
        self.assertIs(self.ledger["live_trading_approved"], False)

    def test_phase_order_is_consistent_with_human_approval(self):
        labels = ("### Phase 8A", "### Phase 8B", "## Phase 9",
                  "## Phase 10", "## Phase 11")
        offsets = [self.build.index(label) for label in labels]
        self.assertEqual(offsets, sorted(offsets))
        self.assertIn("No real money before a separately approved Phase 11.",
                      self.build)

    def test_annual_first_discovery_is_governing_not_rule_family(self):
        self.assertIn("year-by-year discovery-first", self.build)
        self.assertIn("discovery-first **year-by-year annual pattern catalogue**",
                      self.owner)
        self.assertIn("independent year-by-year annual pattern discovery",
                      self.economics)

    def test_2022_historical_predecessor_is_not_a_current_attestation(self):
        prior = self.ledger["previous_annual_freeze"]
        self.assertEqual((prior["segment"], prior["run_number"]),
                         ("2022", 384))
        self.assertIn("2022 run 384", self.owner)
        self.assertIn("2022 run 384", self.handoff)
        self.assertEqual(
            prior["source_provenance"],
            "HISTORICALLY_ACCEPTED_NOT_REAUTHENTICATED_FOR_DISPATCH",
        )

    def test_2023_one_shot_expected_identity_is_not_an_action(self):
        row = self.ledger["yearly_catalogue_status"][8]
        self.assertEqual((row["segment"], row["expected_run_number"],
                          row["expected_attempt"]), ("2023", 385, 1))
        self.assertIn("2023, run 385, attempt 1", self.owner)
        self.assertIn("2023/run385/attempt1", self.handoff)
        self.assertIs(self.ledger["authority_flags"]["run385_authorized"],
                      False)
        self.assertEqual(self.ledger["authorized_actions"], [])

    def test_later_years_remain_unapproved_in_all_documents(self):
        segments = self.ledger["yearly_catalogue_status"][8:]
        self.assertEqual([x["segment"] for x in segments],
                         ["2023", "2024", "2025",
                          "2026_YTD_TO_2026_08_20"])
        self.assertTrue(all(x["research_evidence"].startswith("BLOCKED_")
                            for x in segments))
        self.assertIn("2024, 2025 and partial 2026 have not been accepted",
                      self.owner)
        self.assertIn("**Not complete**: 2015–2022 through run384",
                      self.economics)

    def test_old_main_public_snapshot_is_not_current_authority(self):
        old_sha = "53e203133bbc141b2f48c7b8b8241d56b35166a3"
        branch = self.ledger["main_branch_last_public_observation"]
        self.assertEqual(branch["sha"], old_sha)
        self.assertIn(old_sha, self.owner)
        self.assertIn(old_sha, self.handoff)
        self.assertIs(branch["protected"], False)
        self.assertIs(branch["is_current_at_action_time"], False)
        self.assertIs(branch["proves_exclusive_no_bypass_lock"], False)

    def test_read_only_repository_permissions_are_not_an_admin_lock(self):
        self.assertIn("read-only", self.owner)
        self.assertIn("no-bypass", self.owner)
        self.assertIn("no-bypass", self.handoff)
        self.assertEqual(self.ledger["external_gate_status"], "BLOCKED")

    def test_phase8a_economic_claims_are_not_phase7_profit(self):
        self.assertEqual(self.ledger["economic_evidence"],
                         "PHASE7_HISTORICAL_BENCHMARK_ONLY")
        self.assertIs(self.ledger["phase8a_strategy_v1_frozen"], False)
        self.assertIs(self.ledger["phase8a_economic_edge_proven"], False)
        self.assertIn("no frozen Phase 8A Strategy V1 economics", self.owner)
        self.assertIn("**No Phase 8A Strategy V1 verdict**", self.economics)

    def test_source_only_ci_and_pr_count_are_not_revenue(self):
        self.assertIn("Never count a PR, unittest method", self.economics)
        self.assertIn("not current earnings", self.owner)
        self.assertIn("No real money before a separately approved Phase 11.",
                      self.build)

    def test_prospective_shadow_and_demo_remain_separately_gated(self):
        self.assertIn("**Phase 8B locked**", self.economics)
        self.assertIn("**Phase 9 locked**", self.economics)
        for key in ("phase8b_authorized", "demo_orders_authorized",
                    "live_orders_authorized", "trading_authorized"):
            with self.subTest(key=key):
                self.assertIs(self.ledger["authority_flags"][key], False)

    def test_independent_admin_and_runner_evidence_not_synthetic(self):
        self.assertIn("administrator-led independent", self.owner)
        self.assertIn("runner-host isolation", self.handoff)
        self.assertIn("cannot verify", self.handoff)
        self.assertIs(self.ledger["live_administration_evidence_verified"],
                      False)

    def test_year_order_cannot_authorize_run_by_document_agreement(self):
        self.assertEqual(self.ledger["next_protected_segment"], "2023")
        self.assertEqual(self.ledger["authorized_actions"], [])
        self.assertIs(self.ledger["authority_flags"]
                      ["annual_workflow_dispatch_authorized"], False)
        self.assertIs(self.ledger["authority_flags"]
                      ["cross_year_synthesis_authorized"], False)
        self.assertIn("**Stop condition:**", self.owner)
