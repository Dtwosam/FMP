"""DEC-1739: unknown Phase8A economics stay unknown until reviewed evidence.

Reads documentation only. No strategy, market input, original archive,
protected annual catalogue, workflow dispatch, broker or trading operation.
"""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs/dec1739-phase8a-economic-evidence-before-shadow.json"
REQUIREMENTS = {
    "annual_catalogue_and_selection": (
        "exact_frozen_year_identity", "all_18_cells_per_annual_segment",
        "failed_and_negative_pattern_inventory",
        "pattern_search_budget_and_multiplicity",
        "canonical_cross_year_pattern_identity",
        "unseen_years_not_touched_as_future_final_test",
    ),
    "cross_year_failure_and_concentration": (
        "recurrence_and_absent_years", "sign_reversals_and_failure_years",
        "year_by_pair_by_timeframe_support",
        "winner_selection_and_search_volume",
        "trade_count_and_independent_observation_support",
        "year_and_session_return_concentration",
    ),
    "after_cost_economics": (
        "bid_ask_price_side_and_spread", "slippage_sensitivity",
        "commission_and_rollover_when_relevant",
        "net_expected_pnl_by_year", "drawdown_and_tail_events",
        "portfolio_correlated_usd_exposure",
        "symbol_and_timeframe_contribution",
        "adverse_cost_and_failure_scenarios",
    ),
    "prospective_follow_through": (
        "exact_frozen_strategy_v1_identity",
        "registered_entry_exit_no_trade_protocol",
        "leakage_safe_signal_execution_timing",
        "predeclared_live_shadow_no_order_policy",
        "future_market_observations_not_looked_ahead",
        "broker_demo_after_separate_review_only",
        "phase10_and_phase11_separate_human_authorizations",
    ),
}
MEASUREMENTS = (
    "strategy_v1_net_return",
    "strategy_v1_expected_value",
    "strategy_v1_drawdown",
    "strategy_v1_cost_sensitivity",
    "strategy_v1_out_of_sample_years",
    "strategy_v1_forward_shadow_return",
)
FLAGS = (
    "all_years_accepted", "cross_year_comparison_authorized",
    "strategy_v1_frozen", "phase8b_shadow_approved",
    "demo_approved", "phase10_approved",
    "live_real_money_approved", "has_forward_profit_evidence",
)


def _no_duplicates(pairs):
    result = {}
    for key, val in pairs:
        if key in result:
            raise ValueError("duplicate economic review member")
        result[key] = val
    return result


class UnprovenPhase8AEconomicReviewContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PATH.read_text(encoding="utf-8")
        cls.doc = json.loads(cls.source, object_pairs_hook=_no_duplicates)

    def test_contract_is_static_non_authorizing(self):
        self.assertEqual(
            self.doc["schema"],
            "fmp_phase8a_non_authorizing_economic_review_contract_v1")
        self.assertEqual(self.doc["provenance"],
                         "SOURCE_ONLY_REQUIREMENTS_NOT_OBSERVATIONS")

    def test_discovery_first_method_is_unmodified(self):
        self.assertEqual(
            self.doc["research_method"],
            "ANNUAL_DISCOVERY_FIRST_DEC268_DEC469",
        )

    def test_annual_predecessor_and_next_one_shot_identity(self):
        series = self.doc["annual_series"]
        self.assertEqual(series["historical_last_segment"], "2022")
        self.assertIs(type(series["historical_last_run_number"]), int)
        self.assertEqual(series["historical_last_run_number"], 384)
        self.assertEqual(series["next_protected_segment"], "2023")
        self.assertIs(type(series["next_protected_run_number"]), int)
        self.assertEqual(series["next_protected_run_number"], 385)
        self.assertIs(type(series["next_attempt"]), int)
        self.assertEqual(series["next_attempt"], 1)

    def test_current_annual_provenance_missing_not_invented(self):
        series = self.doc["annual_series"]
        self.assertIs(series["independent_fresh_inventory_present"], False)
        self.assertIs(series["full_year_series_frozen"], False)

    def test_all_four_evidence_groups_and_exact_requirements(self):
        groups = self.doc["required_evidence_groups"]
        self.assertEqual(set(groups), set(REQUIREMENTS))
        for name, expected in REQUIREMENTS.items():
            with self.subTest(group=name):
                self.assertEqual(tuple(groups[name]), expected)
                self.assertEqual(len(set(groups[name])), len(expected))

    def test_all_strategy_v1_measurements_are_missing_not_zero(self):
        metrics = self.doc["reported_economic_measurements"]
        self.assertEqual(set(metrics), set(MEASUREMENTS))
        self.assertTrue(all(val is None for val in metrics.values()))

    def test_no_fabricated_approval_flags(self):
        for field in FLAGS:
            with self.subTest(flag=field):
                self.assertIs(self.doc[field], False)

    def test_action_fields_are_empty_and_not_signed(self):
        self.assertIsNone(self.doc["human_approved_action"])
        self.assertEqual(self.doc["allowed_execution_actions"], [])

    def test_not_even_shadow_before_independent_review(self):
        self.assertEqual(self.doc["phase"], "PHASE8A_BLOCKED_AT_2023_RUN385")
        self.assertIs(self.doc["strategy_v1_frozen"], False)
        self.assertIs(self.doc["phase8b_shadow_approved"], False)

    def test_strict_duplicate_json_member_denied(self):
        with self.assertRaises(ValueError):
            json.loads('{"strategy_v1_frozen":false,'
                       '"strategy_v1_frozen":true}',
                       object_pairs_hook=_no_duplicates)

    def test_no_dispatch_or_broker_commands_in_source(self):
        for forbidden in ("gh workflow run ", "gh api --method POST",
                          "git push --force", "place_order", "api_key"):
            self.assertNotIn(forbidden, self.source)

    def test_review_contract_cannot_count_as_actual_profit(self):
        self.assertIs(self.doc["has_forward_profit_evidence"], False)
        self.assertIs(self.doc["live_real_money_approved"], False)
        self.assertIn("not performance evidence", self.doc["caveat"])
