"""DEC-1751: cross-check stale read-only admin snapshot against source ledgers.

This is not a live security audit and never invokes dispatch or a broker.
"""
import json
from pathlib import Path
import unittest

import test_dec1748_preregistration_four_source_reconciliation as prior
import test_dec1750_phase8a_admin_blocker_snapshot as snapshot


class FiveSourceNoAuthorityReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        prior.PreregistrationFourSourceBoundaryConsistencyTests.setUpClass()
        snapshot.AdminBlockerSourceOnlySnapshotTests.setUpClass()
        cls.year = prior.PreregistrationFourSourceBoundaryConsistencyTests.annual
        cls.econ = prior.PreregistrationFourSourceBoundaryConsistencyTests.economic
        cls.dag = prior.PreregistrationFourSourceBoundaryConsistencyTests.graph
        cls.prereg = prior.PreregistrationFourSourceBoundaryConsistencyTests.packet
        cls.observation = snapshot.AdminBlockerSourceOnlySnapshotTests.doc
        cls.nodes = {item["id"]: item for item in cls.dag["nodes"]}

    def test_snapshot_decision_does_not_replace_annual_governing_method(self):
        self.assertEqual(self.observation["decision"], "DEC-1750")
        self.assertEqual(self.prereg["method"],
                         "DEC-268_DEC-469_YEAR_BY_YEAR_ANNUAL_FIRST")

    def test_main_sha_is_a_historical_observation_not_a_validated_dispatch_ref(self):
        public = self.observation["public_observation"]
        old = self.year["main_branch_last_public_observation"]
        self.assertEqual(public["observed_main_sha"], old["sha"])
        self.assertIs(public["observation_current_at_future_action_time"], False)
        self.assertIs(old["is_current_at_action_time"], False)

    def test_unprotected_main_matches_both_source_only_records(self):
        public = self.observation["public_observation"]
        old = self.year["main_branch_last_public_observation"]
        self.assertIs(public["main_branch_protected"], False)
        self.assertIs(old["protected"], False)

    def test_zero_repository_rulesets_not_administrator_exclusivity(self):
        public = self.observation["public_observation"]
        self.assertEqual(public["repo_rulesets_count"], 0)
        self.assertIs(public["inherited_org_ruleset_scope_verified"], False)
        self.assertIs(public["independent_admin_scope_verified"], False)
        self.assertIs(self.dag["external_authorization_established"], False)

    def test_snapshot_run384_historical_predecessor_matches_sources(self):
        hist = self.observation["historical_provenance"]
        self.assertEqual(hist["historical_freeze_segment"], "2022")
        self.assertEqual(hist["historical_freeze_run"],
                         self.year["previous_annual_freeze"]["run_number"])
        self.assertEqual(hist["historical_freeze_run"],
                         self.econ["annual_series"]["historical_last_run_number"])
        self.assertEqual(hist["historical_freeze_segment"],
                         self.dag["last_frozen_historical_segment"])
        self.assertIs(hist["independently_reauthenticated_for_future_dispatch"], False)

    def test_snapshot_one_shot_run385_identity_matches_four_other_sources(self):
        action = self.observation["next_protected_action"]
        actual = (action["segment"], action["run_number"], action["attempt_number"])
        references = (
            (self.year["yearly_catalogue_status"][8]["segment"],
             self.year["yearly_catalogue_status"][8]["expected_run_number"],
             self.year["yearly_catalogue_status"][8]["expected_attempt"]),
            (self.econ["annual_series"]["next_protected_segment"],
             self.econ["annual_series"]["next_protected_run_number"],
             self.econ["annual_series"]["next_attempt"]),
            (self.dag["next_protected_segment"],
             self.dag["next_expected_run_number"],
             self.dag["next_expected_attempt"]),
            (self.prereg["next_one_shot_segment"],
             self.prereg["next_run_number"], self.prereg["attempt_number"]),
        )
        self.assertEqual(actual, ("2023", 385, 1))
        self.assertTrue(all(item == actual for item in references))

    def test_run385_attempt1_identifiers_are_strict_integer_not_bool_alias(self):
        p = self.observation["next_protected_action"]
        self.assertIs(type(p["run_number"]), int)
        self.assertIs(type(p["attempt_number"]), int)

    def test_no_reauthenticated_fresh_inventory_in_any_packet(self):
        p = self.observation["next_protected_action"]
        self.assertIs(p["run_inventory_currently_independently_verified"], False)
        self.assertIs(p["run_385_unconsumed_currently_independently_proven"], False)
        self.assertIs(self.year["live_annual_run_385_inventory_verified"], False)
        self.assertIs(self.econ["annual_series"]["independent_fresh_inventory_present"],
                      False)

    def test_eight_source_proofs_cover_separate_human_2023_decision(self):
        proof_ids = [p["id"] for p in self.observation["external_proofs"]]
        self.assertEqual(tuple(proof_ids), snapshot.PROOF_IDS)
        self.assertIn("separate_2023_run385_attempt1_human_execution_decision",
                      proof_ids)
        self.assertIn("fresh_complete_authoritative_one_shot_annual_run_inventory",
                      proof_ids)

    def test_eight_external_proofs_cannot_masquerade_as_verified(self):
        self.assertTrue(all(
            item["status"] == "MISSING" and item["evidence_ref"] is None
            and item["reviewer_signoff"] is None
            for item in self.observation["external_proofs"]))
        self.assertIs(self.dag["external_authorization_established"], False)

    def test_five_independent_upstream_dag_nodes_still_blocked(self):
        self.assertTrue(all(
            self.dag["nodes"][i]["status"] == "BLOCKED"
            and self.dag["nodes"][i]["verified_current_evidence"] is False
            for i in range(5)))

    def test_two_mitigation_routes_are_unselected_and_not_approved(self):
        routes = self.observation["remediation_routes"]
        self.assertEqual(len(routes), 2)
        self.assertTrue(all(
            item["status"] == "BLOCKED" and item["selected"] is False
            and item["independently_reviewed"] is False for item in routes))

    def test_one_shot_run_and_retry_are_not_implicitly_authorized(self):
        action = self.observation["next_protected_action"]
        self.assertIs(action["dispatch_authorized"], False)
        self.assertIs(action["retry_authorized"], False)
        self.assertIs(self.year["authority_flags"]["run385_authorized"], False)
        self.assertIs(self.year["authority_flags"]["retry_or_rerun_authorized"], False)
        self.assertIs(self.prereg["protected_annual_execution_authorized"], False)

    def test_2023_and_later_annual_research_require_prior_witness(self):
        self.assertEqual(self.observation["downstream_gate_state"]["annual_2023"],
                         "BLOCKED")
        self.assertEqual(
            self.observation["downstream_gate_state"]["remaining_annual_years"],
            "BLOCKED")
        self.assertTrue(all(
            item["promotion_eligible"] is False
            for item in self.year["yearly_catalogue_status"][8:]))

    def test_cross_year_strategy_shadow_demo_and_live_remain_blocked(self):
        statuses = self.observation["downstream_gate_state"]
        for gate in ("cross_year_economics", "strategy_v1", "prospective_shadow",
                     "demo", "phase10", "phase11_real_money"):
            with self.subTest(gate=gate):
                self.assertEqual(statuses[gate], "BLOCKED")
        self.assertIs(self.econ["phase8b_shadow_approved"], False)
        self.assertIs(self.econ["live_real_money_approved"], False)

    def test_unknown_strategy_profit_consistent_with_all_sources(self):
        self.assertIsNone(self.observation["measured_strategy_v1_profit"])
        self.assertIsNone(self.observation["candidate_strategy_identity"])
        self.assertIsNone(self.prereg["profitability_measurements"])
        self.assertIsNone(self.prereg["candidate_strategy_identity"])
        self.assertIsNone(self.dag["live_strategy_v1_profit_evidence"])
        self.assertTrue(all(x is None for x in
                            self.econ["reported_economic_measurements"].values()))

    def test_action_lists_empty_across_five_documents(self):
        self.assertEqual(self.observation["approved_actions"], [])
        self.assertEqual(self.year["authorized_actions"], [])
        self.assertEqual(self.econ["allowed_execution_actions"], [])
        self.assertEqual(self.dag["already_authorized_actions"], [])
        self.assertEqual(self.prereg["allowed_actions"], [])

    def test_source_docs_cannot_directly_authorize_annual_or_broker_action(self):
        self.assertIs(self.observation["one_shot_annual_action_authorized"], False)
        self.assertIs(self.observation["broker_action_authorized"], False)
        self.assertIs(self.observation["trading_authorized"], False)
        self.assertIs(self.observation["snapshot_authorizes_anything"], False)
        self.assertIs(self.prereg["live_trading_authorized"], False)

    def test_unfilled_preregistration_never_inherits_admin_snapshot_approval(self):
        self.assertEqual(len(self.prereg["gates"]), 15)
        self.assertTrue(all(p["status"] == "NOT_EVALUATED"
                            and p["evidence_ref"] is None
                            and p["signoff"] is None
                            for p in self.prereg["gates"]))
        self.assertIs(self.prereg["predefined_thresholds_documented"], False)

    def test_source_only_closure_requires_external_fresh_authority(self):
        self.assertEqual(self.observation["release_status"], "BLOCKED")
        self.assertIn("cannot authorize", self.observation["caveat"])
        self.assertEqual(self.econ["provenance"],
                         "SOURCE_ONLY_REQUIREMENTS_NOT_OBSERVATIONS")
        self.assertIs(self.year["live_administration_evidence_verified"], False)
