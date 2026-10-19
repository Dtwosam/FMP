"""DEC-1741: exact nonauthorizing economic evidence packet inventory.

Only local source documents. A matching packet cannot enable annual or
broker activity and does not independently establish trading alpha.
"""
import json
from pathlib import Path
import unittest

import test_dec1739_economic_evidence_before_shadow_contract as contract


ROOT_KEYS = {
    "schema", "decision", "provenance", "research_method", "phase",
    "annual_series", "required_evidence_groups",
    "reported_economic_measurements", "all_years_accepted",
    "cross_year_comparison_authorized", "strategy_v1_frozen",
    "phase8b_shadow_approved", "demo_approved", "phase10_approved",
    "live_real_money_approved", "has_forward_profit_evidence",
    "human_approved_action", "allowed_execution_actions", "caveat",
}
ANNUAL_KEYS = {
    "historical_last_segment", "historical_last_run_number",
    "next_protected_segment", "next_protected_run_number",
    "next_attempt", "independent_fresh_inventory_present",
    "full_year_series_frozen",
}
STAGES = {
    "all_years_accepted", "cross_year_comparison_authorized",
    "strategy_v1_frozen", "phase8b_shadow_approved", "demo_approved",
    "phase10_approved", "live_real_money_approved",
    "has_forward_profit_evidence",
}
PHASE8A_LEDGER = (
    Path(__file__).resolve().parents[1]
    / "docs/dec1726-phase8a-sourceonly-segment-gate-ledger.json"
)


class Phase8AEconomicRequirementExactSchemaGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(
            contract.PATH.read_text(encoding="utf-8"),
            object_pairs_hook=contract._no_duplicates,
        )
        cls.ledger = json.loads(PHASE8A_LEDGER.read_text(encoding="utf-8"))

    def test_exact_root_members_no_silent_authorization_field(self):
        self.assertEqual(set(self.doc), ROOT_KEYS)

    def test_exact_annual_series_field_inventory(self):
        self.assertEqual(set(self.doc["annual_series"]), ANNUAL_KEYS)

    def test_external_proof_booleans_remain_false(self):
        for name in ("independent_fresh_inventory_present",
                     "full_year_series_frozen"):
            self.assertIs(self.doc["annual_series"][name], False)

    def test_all_progress_booleans_are_real_false_not_zero(self):
        self.assertEqual(set(STAGES & set(self.doc)), STAGES)
        for name in STAGES:
            with self.subTest(name=name):
                self.assertIs(type(self.doc[name]), bool)
                self.assertIs(self.doc[name], False)

    def test_exact_requirement_groups_and_no_duplicates(self):
        requirements = self.doc["required_evidence_groups"]
        self.assertEqual(set(requirements), set(contract.REQUIREMENTS))
        for group, members in contract.REQUIREMENTS.items():
            with self.subTest(group=group):
                self.assertEqual(tuple(requirements[group]), members)
                self.assertEqual(len(set(requirements[group])),
                                 len(requirements[group]))

    def test_unreported_metrics_exact_names_and_null_values(self):
        reported = self.doc["reported_economic_measurements"]
        self.assertEqual(set(reported), set(contract.MEASUREMENTS))
        self.assertTrue(all(value is None for value in reported.values()))

    def test_nobody_has_approved_an_action_or_broker_access(self):
        self.assertIsNone(self.doc["human_approved_action"])
        self.assertIs(type(self.doc["allowed_execution_actions"]), list)
        self.assertEqual(self.doc["allowed_execution_actions"], [])

    def test_future_phase_not_at_odds_with_original_blocked_ledger(self):
        self.assertIs(self.ledger["phase8a_strategy_v1_frozen"], False)
        self.assertIs(self.ledger["phase8a_economic_edge_proven"], False)
        self.assertIs(self.ledger["authority_flags"]["phase8b_authorized"],
                      False)
        self.assertIs(self.ledger["authority_flags"]["real_money_authorized"],
                      False)
        self.assertEqual(self.doc["phase"],
                         "PHASE8A_BLOCKED_AT_2023_RUN385")

    def test_no_return_is_claimed_by_source_requirements(self):
        self.assertEqual(self.doc["provenance"],
                         "SOURCE_ONLY_REQUIREMENTS_NOT_OBSERVATIONS")
        self.assertIs(self.doc["has_forward_profit_evidence"], False)
        self.assertIs(self.doc["live_real_money_approved"], False)
        self.assertIn("not performance evidence", self.doc["caveat"])
