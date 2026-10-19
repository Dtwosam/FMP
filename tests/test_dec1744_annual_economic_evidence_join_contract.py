"""DEC-1744: source-only annual, economics and approval-path consistency.

A consistent document inventory is not a live administrator witness, a
StrategyV1 profitability proof, protected-run approval or broker authority.
"""
import json
from pathlib import Path
import unittest


DOCS = Path(__file__).resolve().parents[1] / "docs"
YEAR = DOCS / "dec1726-phase8a-sourceonly-segment-gate-ledger.json"
ECON = DOCS / "dec1739-phase8a-economic-evidence-before-shadow.json"
DAG = DOCS / "dec1742-phase8a-blocked-dependency-graph.json"


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


class AnnualToEconomicSourceOnlyReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.year = json.loads(YEAR.read_text(encoding="utf-8"),
                              object_pairs_hook=_no_duplicate_keys)
        cls.econ = json.loads(ECON.read_text(encoding="utf-8"),
                              object_pairs_hook=_no_duplicate_keys)
        cls.graph = json.loads(DAG.read_text(encoding="utf-8"),
                               object_pairs_hook=_no_duplicate_keys)
        cls.nodes = {node["id"]: node for node in cls.graph["nodes"]}

    def test_schema_types_are_distinct(self):
        self.assertEqual(self.year["decision"], "DEC-1726")
        self.assertEqual(self.econ["decision"], "DEC-1739")
        self.assertEqual(self.graph["decision"], "DEC-1742")

    def test_historical_predecessor_is_the_same(self):
        self.assertEqual(self.year["previous_annual_freeze"]["segment"], "2022")
        self.assertEqual(self.year["previous_annual_freeze"]["run_number"], self.econ["annual_series"]["historical_last_run_number"])
        self.assertEqual(self.graph["last_frozen_historical_segment"], "2022")

    def test_next_one_shot_identity_matches(self):
        row = self.year["yearly_catalogue_status"][8]
        annual = self.econ["annual_series"]
        self.assertEqual((row["segment"], row["expected_run_number"], row["expected_attempt"]), ("2023", 385, 1))
        self.assertEqual((annual["next_protected_segment"], annual["next_protected_run_number"], annual["next_attempt"]), ("2023", 385, 1))
        self.assertEqual((self.graph["next_protected_segment"], self.graph["next_expected_run_number"], self.graph["next_expected_attempt"]), ("2023", 385, 1))

    def test_run_attempts_are_strict_integer(self):
        self.assertIs(type(self.year["yearly_catalogue_status"][8]["expected_attempt"]), int)
        self.assertIs(type(self.econ["annual_series"]["next_attempt"]), int)
        self.assertIs(type(self.graph["next_expected_attempt"]), int)

    def test_all_later_years_are_still_blocked(self):
        self.assertTrue(all(row["research_evidence"].startswith("BLOCKED_") and row["promotion_eligible"] is False for row in self.year["yearly_catalogue_status"][8:]))
        self.assertIs(self.econ["annual_series"]["full_year_series_frozen"], False)

    def test_external_gate_has_no_live_witness(self):
        self.assertEqual(self.year["external_gate_status"], "BLOCKED")
        self.assertIs(self.year["live_administration_evidence_verified"], False)
        self.assertIs(self.econ["annual_series"]["independent_fresh_inventory_present"], False)
        self.assertIs(self.graph["external_authorization_established"], False)

    def test_all_source_authorizations_stay_false(self):
        self.assertEqual(len(self.year["authority_flags"]), 14)
        self.assertTrue(all(value is False for value in self.year["authority_flags"].values()))
        self.assertTrue(all(node["status"] == "BLOCKED" and node["authorizes_execution"] is False and node["verified_current_evidence"] is False for node in self.graph["nodes"]))

    def test_all_strategy_v1_economic_metrics_unknown(self):
        self.assertTrue(all(value is None for value in self.econ["reported_economic_measurements"].values()))
        self.assertIsNone(self.graph["live_strategy_v1_profit_evidence"])
        self.assertIs(self.year["phase8a_economic_edge_proven"], False)

    def test_cross_year_research_requires_annual_freeze(self):
        self.assertEqual(self.nodes["cross_year_pattern_economics"]["prerequisites"], ["accepted_remaining_annual_freezes"])
        self.assertIs(self.econ["cross_year_comparison_authorized"], False)
        self.assertIs(self.year["authority_flags"]["cross_year_synthesis_authorized"], False)

    def test_strategy_v1_freeze_requires_cross_year_economics(self):
        self.assertEqual(self.nodes["strategy_v1_freeze"]["prerequisites"], ["cross_year_pattern_economics"])
        self.assertIs(self.econ["strategy_v1_frozen"], False)
        self.assertIs(self.year["phase8a_strategy_v1_frozen"], False)

    def test_shadow_is_order_impossible_and_separately_locked(self):
        self.assertEqual(self.nodes["prospective_order_impossible_shadow"]["prerequisites"], ["strategy_v1_freeze"])
        self.assertIs(self.econ["phase8b_shadow_approved"], False)
        self.assertIs(self.year["authority_flags"]["phase8b_authorized"], False)
        self.assertIs(self.year["authority_flags"]["broker_mutation_authorized"], False)

    def test_demo_requires_shadow_and_remains_unapproved(self):
        self.assertEqual(self.nodes["fixed_version_demo_review"]["prerequisites"], ["prospective_order_impossible_shadow"])
        self.assertIs(self.econ["demo_approved"], False)
        self.assertIs(self.year["authority_flags"]["demo_orders_authorized"], False)

    def test_phase11_requires_phase10_and_live_stays_blocked(self):
        self.assertEqual(self.nodes["separate_phase11_real_money_approval"]["prerequisites"], ["phase10_live_readiness_approval"])
        self.assertIs(self.econ["live_real_money_approved"], False)
        self.assertIs(self.year["authority_flags"]["real_money_authorized"], False)

    def test_all_sources_have_empty_execution_actions(self):
        self.assertEqual(self.year["authorized_actions"], [])
        self.assertEqual(self.econ["allowed_execution_actions"], [])
        self.assertEqual(self.graph["already_authorized_actions"], [])
        self.assertIsNone(self.econ["human_approved_action"])

