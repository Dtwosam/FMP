"""DEC-1748: static consistency of four unapproved Phase8A evidence sources.

This independently compares the annual ledger, economic requirements, blocked
dependency graph and unfilled StrategyV1 research preregistration. It does NOT
attest to real GitHub controls, execute an annual job, or approve broker orders.
"""
import json
from pathlib import Path
import unittest

import test_dec1746_economic_preregistration_strict_source_guards as prereg


DOCS = Path(__file__).resolve().parents[1] / "docs"
SOURCES = {
    "annual": "dec1726-phase8a-sourceonly-segment-gate-ledger.json",
    "economic": "dec1739-phase8a-economic-evidence-before-shadow.json",
    "dependency": "dec1742-phase8a-blocked-dependency-graph.json",
    "preregistration": "dec1745-strategy-v1-economic-review-preregistration-template.json",
}
ANNUAL_SEGMENTS = tuple(map(str, range(2015, 2026))) + (
    "2026_YTD_TO_2026_08_20",
)
ANNUAL_AUTHORITY_FLAGS = {
    "annual_workflow_dispatch_authorized",
    "protected_history_access_authorized",
    "run385_authorized",
    "run385_executed",
    "retry_or_rerun_authorized",
    "later_years_research_authorized",
    "cross_year_synthesis_authorized",
    "strategy_promotion_authorized",
    "phase8b_authorized",
    "broker_mutation_authorized",
    "demo_orders_authorized",
    "real_money_authorized",
    "live_orders_authorized",
    "trading_authorized",
}
ECONOMIC_DENIAL_FLAGS = {
    "all_years_accepted", "cross_year_comparison_authorized",
    "strategy_v1_frozen", "phase8b_shadow_approved", "demo_approved",
    "phase10_approved", "live_real_money_approved", "has_forward_profit_evidence",
}
RESEARCH_COMPONENTS = {
    "negative_pattern_and_failure_years":
        ("annual_catalogue_and_selection", "failed_and_negative_pattern_inventory"),
    "multiplicity_and_winner_selection":
        ("annual_catalogue_and_selection", "pattern_search_budget_and_multiplicity"),
    "holdout_contamination_accounting":
        ("annual_catalogue_and_selection", "unseen_years_not_touched_as_future_final_test"),
    "trade_support_and_pnl_concentration":
        ("cross_year_failure_and_concentration", "trade_count_and_independent_observation_support"),
    "costs_under_adverse_conditions":
        ("after_cost_economics", "slippage_sensitivity"),
    "portfolio_usd_correlation_and_exposure":
        ("after_cost_economics", "portfolio_correlated_usd_exposure"),
    "drawdown_and_tail_risk":
        ("after_cost_economics", "drawdown_and_tail_events"),
    "time_safe_signal_and_execution":
        ("prospective_follow_through", "leakage_safe_signal_execution_timing"),
    "prospective_order_impossible_shadow":
        ("prospective_follow_through", "predeclared_live_shadow_no_order_policy"),
    "separate_demo_live_decisions":
        ("prospective_follow_through", "phase10_and_phase11_separate_human_authorizations"),
}


class PreregistrationFourSourceBoundaryConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {
            key: json.loads(
                (DOCS / filename).read_text(encoding="utf-8"),
                object_pairs_hook=prereg._strict_pairs,
            )
            for key, filename in SOURCES.items()
        }
        cls.annual = cls.sources["annual"]
        cls.economic = cls.sources["economic"]
        cls.graph = cls.sources["dependency"]
        cls.packet = cls.sources["preregistration"]
        cls.nodes = {node["id"]: node for node in cls.graph["nodes"]}

    def test_exact_distinct_document_decisions(self):
        self.assertEqual(
            [self.sources[key]["decision"] for key in SOURCES],
            ["DEC-1726", "DEC-1739", "DEC-1742", "DEC-1745"])

    def test_all_four_documents_are_source_only_not_authorization(self):
        self.assertEqual(self.annual["external_gate_status"], "BLOCKED")
        self.assertEqual(self.economic["provenance"],
                         "SOURCE_ONLY_REQUIREMENTS_NOT_OBSERVATIONS")
        self.assertIn("STATIC_DOCUMENTARY_DEPENDENCIES",
                      self.graph["provenance"])
        self.assertEqual(self.packet["type"],
                         "RESEARCH_REVIEW_TEMPLATE_NONAUTHORIZING")

    def test_historical_2022_run384_predecessor_consistent(self):
        self.assertEqual(self.annual["previous_annual_freeze"]["segment"], "2022")
        self.assertEqual(self.graph["last_frozen_historical_segment"], "2022")
        self.assertEqual(self.packet["source_segments_historical_through"], "2022")
        e = self.economic["annual_series"]
        self.assertEqual(e["historical_last_segment"], "2022")
        self.assertEqual(
            [self.annual["previous_annual_freeze"]["run_number"],
             e["historical_last_run_number"]], [384, 384])

    def test_2023_run385_attempt1_identity_agrees_across_four_documents(self):
        a = self.annual["yearly_catalogue_status"][8]
        e = self.economic["annual_series"]
        g = self.graph
        p = self.packet
        ids = [
            (a["segment"], a["expected_run_number"], a["expected_attempt"]),
            (e["next_protected_segment"], e["next_protected_run_number"], e["next_attempt"]),
            (g["next_protected_segment"], g["next_expected_run_number"],
             g["next_expected_attempt"]),
            (p["next_one_shot_segment"], p["next_run_number"], p["attempt_number"]),
        ]
        self.assertEqual(ids, [("2023", 385, 1)] * 4)

    def test_run385_and_attempt_numbers_are_real_integers_not_booleans(self):
        fields = (
            self.annual["yearly_catalogue_status"][8]["expected_run_number"],
            self.annual["yearly_catalogue_status"][8]["expected_attempt"],
            self.economic["annual_series"]["next_protected_run_number"],
            self.economic["annual_series"]["next_attempt"],
            self.graph["next_expected_run_number"],
            self.graph["next_expected_attempt"],
            self.packet["next_run_number"],
            self.packet["attempt_number"],
        )
        self.assertTrue(all(type(value) is int for value in fields))

    def test_exact_2015_to_partial_2026_catalogue_inventory(self):
        self.assertEqual(
            tuple(row["segment"] for row in self.annual["yearly_catalogue_status"]),
            ANNUAL_SEGMENTS)
        self.assertEqual(len(ANNUAL_SEGMENTS), 12)

    def test_unfinished_years_are_blocked_not_auto_selected(self):
        yearly = self.annual["yearly_catalogue_status"]
        self.assertTrue(all(row["research_evidence"] == "HISTORICALLY_FROZEN"
                            for row in yearly[:8]))
        self.assertTrue(all(row["research_evidence"].startswith("BLOCKED_")
                            for row in yearly[8:]))
        self.assertTrue(all(row["promotion_eligible"] is False for row in yearly))
        self.assertIs(self.economic["annual_series"]["full_year_series_frozen"], False)

    def test_unfilled_preregistration_has_exact_research_category_order(self):
        gates = self.packet["gates"]
        self.assertEqual(tuple(g["id"] for g in gates), prereg.EXPECTED)
        self.assertEqual(len({g["id"] for g in gates}), 15)

    def test_all_preregistration_categories_have_no_evidence_or_signoff(self):
        for gate in self.packet["gates"]:
            with self.subTest(category=gate["id"]):
                self.assertEqual(gate["status"], "NOT_EVALUATED")
                self.assertIsNone(gate["evidence_ref"])
                self.assertIsNone(gate["signoff"])

    def test_ten_preregistered_risks_have_matching_economic_evidence_requirements(self):
        groups = self.economic["required_evidence_groups"]
        gate_ids = {entry["id"] for entry in self.packet["gates"]}
        for category, (group, evidence) in RESEARCH_COMPONENTS.items():
            with self.subTest(category=category):
                self.assertIn(category, gate_ids)
                self.assertIn(evidence, groups[group])

    def test_external_administrator_and_fresh_inventory_remain_unproven(self):
        self.assertIs(self.annual["live_administration_evidence_verified"], False)
        self.assertIs(self.annual["live_annual_run_385_inventory_verified"], False)
        self.assertIs(self.economic["annual_series"]["independent_fresh_inventory_present"],
                      False)
        self.assertIs(self.graph["external_authorization_established"], False)
        self.assertIs(self.packet["protected_annual_execution_authorized"], False)

    def test_eighteen_claimed_outcomes_cannot_override_false_authority(self):
        self.assertEqual(set(self.annual["authority_flags"]), ANNUAL_AUTHORITY_FLAGS)
        self.assertTrue(all(value is False
                            for value in self.annual["authority_flags"].values()))
        self.assertTrue(all(self.economic[field] is False
                            for field in ECONOMIC_DENIAL_FLAGS))
        self.assertTrue(all(self.packet[field] is False
                            for field in prereg.DENIAL_FLAGS))

    def test_no_economic_result_is_zero_filled_or_reused(self):
        self.assertEqual(
            set(self.economic["reported_economic_measurements"]),
            {"strategy_v1_net_return", "strategy_v1_expected_value",
             "strategy_v1_drawdown", "strategy_v1_cost_sensitivity",
             "strategy_v1_out_of_sample_years",
             "strategy_v1_forward_shadow_return"})
        self.assertTrue(all(value is None for value in
                            self.economic["reported_economic_measurements"].values()))
        self.assertIsNone(self.packet["profitability_measurements"])
        self.assertIsNone(self.packet["candidate_strategy_identity"])
        self.assertIsNone(self.graph["live_strategy_v1_profit_evidence"])
        self.assertIs(self.annual["phase8a_economic_edge_proven"], False)

    def test_source_only_dependency_graph_fails_closed_for_every_stage(self):
        self.assertEqual(len(self.graph["nodes"]), 14)
        self.assertEqual(len(self.nodes), 14)
        self.assertTrue(all(
            node["status"] == "BLOCKED"
            and node["verified_current_evidence"] is False
            and node["authorizes_execution"] is False
            for node in self.graph["nodes"]
        ))

    def test_run385_requires_five_independent_witnesses_before_one_shot(self):
        required = {
            "admin_exclusive_no_bypass_lock",
            "independent_approved_sha_workflow_runtime",
            "installed_three_job_preaccess_admission",
            "privileged_runner_os_isolation",
            "fresh_authoritative_annual_inventory",
        }
        self.assertEqual(
            set(self.nodes["separate_2023_run385_one_shot_decision"]["prerequisites"]),
            required)
        self.assertEqual(
            self.nodes["accepted_2023_run385_freeze"]["prerequisites"],
            ["separate_2023_run385_one_shot_decision"])

    def test_annual_evidence_precedes_cross_year_analysis_and_strategy_v1(self):
        self.assertEqual(
            self.nodes["accepted_remaining_annual_freezes"]["prerequisites"],
            ["accepted_2023_run385_freeze"])
        self.assertEqual(
            self.nodes["cross_year_pattern_economics"]["prerequisites"],
            ["accepted_remaining_annual_freezes"])
        self.assertEqual(
            self.nodes["strategy_v1_freeze"]["prerequisites"],
            ["cross_year_pattern_economics"])
        self.assertIs(self.packet["cross_year_analysis_permitted"], False)
        self.assertIs(self.economic["cross_year_comparison_authorized"], False)

    def test_shadow_after_strategy_is_order_impossible_and_separately_blocked(self):
        self.assertEqual(
            self.nodes["prospective_order_impossible_shadow"]["prerequisites"],
            ["strategy_v1_freeze"])
        self.assertIs(self.annual["fresh_prospective_shadow_accepted"], False)
        self.assertIs(self.economic["phase8b_shadow_approved"], False)
        self.assertIs(self.packet["prospective_shadow_authorized"], False)
        self.assertIs(self.annual["authority_flags"]["broker_mutation_authorized"],
                      False)

    def test_demo_phase10_and_phase11_are_three_separate_dependencies(self):
        self.assertEqual(self.nodes["fixed_version_demo_review"]["prerequisites"],
                         ["prospective_order_impossible_shadow"])
        self.assertEqual(self.nodes["phase10_live_readiness_approval"]["prerequisites"],
                         ["fixed_version_demo_review"])
        self.assertEqual(
            self.nodes["separate_phase11_real_money_approval"]["prerequisites"],
            ["phase10_live_readiness_approval"])
        self.assertIs(self.economic["phase10_approved"], False)
        self.assertIs(self.economic["live_real_money_approved"], False)
        self.assertIs(self.packet["live_trading_authorized"], False)

    def test_phase7_benchmark_not_a_phase8a_return_or_forward_forecast(self):
        past = self.packet["known_historical_context"]
        self.assertEqual(past["source"], "docs/phase7-walk-forward-evidence.md")
        self.assertIs(past["not_phase8a_strategy_v1_results"], True)
        self.assertEqual(
            past["reported_phase7_net_return_pct_by_slippage_pips"]["1.0"],
            "-0.562118")
        self.assertIsNone(past["live_return_forecast"])
        self.assertEqual(self.annual["economic_evidence"],
                         "PHASE7_HISTORICAL_BENCHMARK_ONLY")

    def test_no_retrospective_pass_thresholds_or_invented_selection(self):
        self.assertIs(self.packet["predefined_thresholds_documented"], False)
        self.assertEqual(self.packet["current_disposition"],
                         "MORE_INDEPENDENT_EVIDENCE_REQUIRED")
        self.assertIn("REJECT", self.packet["possible_dispositions"])
        self.assertIs(self.packet["strategy_v1_selected"], False)

    def test_all_four_sources_have_zero_authorized_actions(self):
        self.assertEqual(self.annual["authorized_actions"], [])
        self.assertEqual(self.economic["allowed_execution_actions"], [])
        self.assertEqual(self.graph["already_authorized_actions"], [])
        self.assertEqual(self.packet["allowed_actions"], [])
        self.assertIsNone(self.economic["human_approved_action"])

    def test_all_real_money_and_demo_flags_still_false_everywhere(self):
        for field in ("demo_trading_approved", "live_trading_approved"):
            self.assertIs(self.annual[field], False)
        for field in ("demo_approved", "live_real_money_approved"):
            self.assertIs(self.economic[field], False)
        for field in ("demo_order_authorized", "live_trading_authorized"):
            self.assertIs(self.packet[field], False)
        self.assertIs(self.annual["authority_flags"]["real_money_authorized"],
                      False)

    def test_actual_strict_loader_refuses_nested_duplicate_member_names(self):
        with self.assertRaises(ValueError):
            json.loads(
                '{"gates":[{"signoff":null,"signoff":"fake"}]}',
                object_pairs_hook=prereg._strict_pairs,
            )
