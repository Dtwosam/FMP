"""DEC-1746: fail-closed source review of unfilled StrategyV1 preregistration.

No private research data, annual runner, broker, current market input
or execution permission is implied by this nonauthorizing source check.
"""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / "docs"
PACKET = ROOT / "dec1745-strategy-v1-economic-review-preregistration-template.json"
EXPLANATION = ROOT / "dec1745-strategy-v1-economic-review-preregistration-packet.md"
EXPECTED = (
    "pre_registered_hypothesis_space",
    "time_safe_signal_and_execution",
    "complete_annual_pattern_catalogue",
    "negative_pattern_and_failure_years",
    "multiplicity_and_winner_selection",
    "independence_and_uncertainty",
    "trade_support_and_pnl_concentration",
    "costs_under_adverse_conditions",
    "portfolio_usd_correlation_and_exposure",
    "drawdown_and_tail_risk",
    "execution_and_capacity",
    "holdout_contamination_accounting",
    "immutable_strategy_v1_spec",
    "prospective_order_impossible_shadow",
    "separate_demo_live_decisions",
)
DENIAL_FLAGS = (
    "protected_annual_execution_authorized",
    "annual_catalogues_complete",
    "cross_year_analysis_permitted",
    "strategy_v1_selected",
    "strategy_v1_frozen",
    "profitability_accepted",
    "prospective_shadow_authorized",
    "demo_order_authorized",
    "live_trading_authorized",
    "market_data_read_by_packet",
    "predefined_thresholds_documented",
)


def _strict_pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate preregistration member")
        value[key] = item
    return value


class EconomicPreregistrationSourceIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = PACKET.read_text(encoding="utf-8")
        cls.doc = json.loads(cls.raw, object_pairs_hook=_strict_pairs)
        cls.prose = EXPLANATION.read_text(encoding="utf-8")

    def test_schema_and_decision_are_explicit_source_only(self):
        self.assertEqual(
            self.doc["schema"],
            "fmp_dec1745_strategy_v1_economic_review_preregistration_template_v1",
        )
        self.assertEqual(self.doc["decision"], "DEC-1745")
        self.assertEqual(self.doc["type"],
                         "RESEARCH_REVIEW_TEMPLATE_NONAUTHORIZING")

    def test_exact_fifteen_required_evidence_categories(self):
        ids = [item["id"] for item in self.doc["gates"]]
        self.assertEqual(tuple(ids), EXPECTED)
        self.assertEqual(len(ids), len(set(ids)))

    def test_all_evidence_groups_still_not_evaluated_or_signed(self):
        for group in self.doc["gates"]:
            with self.subTest(group=group["id"]):
                self.assertEqual(set(group), {
                    "id", "required_evidence", "status",
                    "evidence_ref", "signoff",
                })
                self.assertTrue(group["required_evidence"])
                self.assertEqual(group["status"], "NOT_EVALUATED")
                self.assertIsNone(group["evidence_ref"])
                self.assertIsNone(group["signoff"])

    def test_human_run385_identity_strict_integer_and_not_authorized(self):
        self.assertEqual(self.doc["source_segments_historical_through"], "2022")
        self.assertEqual(self.doc["next_one_shot_segment"], "2023")
        self.assertIs(type(self.doc["next_run_number"]), int)
        self.assertIs(type(self.doc["attempt_number"]), int)
        self.assertEqual(self.doc["next_run_number"], 385)
        self.assertEqual(self.doc["attempt_number"], 1)
        self.assertIs(self.doc["protected_annual_execution_authorized"], False)

    def test_year_by_year_governing_method_not_strategy_family_shortcut(self):
        self.assertEqual(self.doc["method"],
                         "DEC-268_DEC-469_YEAR_BY_YEAR_ANNUAL_FIRST")
        self.assertIn("2015–2025 annual pattern catalogues", self.prose)

    def test_all_unreviewed_stages_use_strict_false_not_numeric_zero(self):
        for field in DENIAL_FLAGS:
            with self.subTest(field=field):
                self.assertIs(type(self.doc[field]), bool)
                self.assertIs(self.doc[field], False)

    def test_candidate_rule_and_return_numbers_are_missing_not_fabricated(self):
        self.assertIsNone(self.doc["candidate_strategy_identity"])
        self.assertIsNone(self.doc["profitability_measurements"])
        self.assertIs(self.doc["strategy_v1_selected"], False)
        self.assertIs(self.doc["profitability_accepted"], False)

    def test_multiple_testing_and_holdout_contamination_are_required(self):
        self.assertIn("multiplicity_and_winner_selection", EXPECTED)
        self.assertIn("holdout_contamination_accounting", EXPECTED)
        self.assertIn("multiple comparisons", self.prose)
        self.assertIn("pristine final holdout", self.prose)

    def test_cost_correlated_usd_and_tail_risks_are_required(self):
        for category in ("costs_under_adverse_conditions",
                         "portfolio_usd_correlation_and_exposure",
                         "drawdown_and_tail_risk"):
            self.assertIn(category, EXPECTED)

    def test_historical_phase7_benchmark_is_not_strategy_v1_evidence(self):
        historic = self.doc["known_historical_context"]
        self.assertEqual(
            historic["source"], "docs/phase7-walk-forward-evidence.md")
        self.assertIs(historic["not_phase8a_strategy_v1_results"], True)
        self.assertEqual(
            historic["reported_phase7_net_return_pct_by_slippage_pips"],
            {"0.2": "0.757266", "0.5": "0.262176",
             "1.0": "-0.562118"},
        )
        self.assertIsNone(historic["live_return_forecast"])

    def test_thresholds_not_chosen_after_candidate_data_review(self):
        self.assertIs(self.doc["predefined_thresholds_documented"], False)
        self.assertIn("before reviewing candidate economics",
                      self.doc["rationale"])
        self.assertIn("numerical pass thresholds remain unset",
                      self.prose)

    def test_rejection_is_still_possible_and_no_pass_disposition(self):
        self.assertIn("REJECT", self.doc["possible_dispositions"])
        self.assertEqual(
            self.doc["current_disposition"],
            "MORE_INDEPENDENT_EVIDENCE_REQUIRED",
        )
        self.assertNotIn("APPROVED_FOR_LIVE", self.doc["possible_dispositions"])

    def test_no_any_authorized_execution_actions_or_signed_orders(self):
        self.assertEqual(self.doc["allowed_actions"], [])
        self.assertIs(self.doc["live_trading_authorized"], False)
        self.assertIs(self.doc["demo_order_authorized"], False)
        self.assertIs(self.doc["prospective_shadow_authorized"], False)

    def test_packet_has_no_dispatch_or_broker_execution_commands(self):
        for forbidden in ("gh workflow run ", "gh api --method POST",
                          "place_order(", "git push --force"):
            self.assertNotIn(forbidden, self.raw)
        self.assertIn("cannot authorize", self.doc["caveat"])
        self.assertIn("Issue #779", self.prose)

    def test_strict_json_refuses_duplicate_approval_member_names(self):
        with self.assertRaises(ValueError):
            json.loads('{"live_trading_authorized":false,'
                       '"live_trading_authorized":true}',
                       object_pairs_hook=_strict_pairs)
