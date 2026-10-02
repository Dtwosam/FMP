from __future__ import annotations

import unittest
from pathlib import Path

from fmp.discovery.annual_pattern_catalogue_method import (
    ANNUAL_PATTERN_CATALOGUE_METHOD_DECISION,
    ANNUAL_PATTERN_CATALOGUE_METHOD_VERSION,
    CURRENTLY_OPEN_CATALOGUE_YEARS,
    GOVERNING_RESEARCH_METHOD,
    PROTECTED_CATALOGUE_YEARS,
    build_annual_pattern_catalogue_method,
    collection_segments,
)


class AnnualPatternCatalogueMethodTests(unittest.TestCase):
    def test_decision_and_governing_method_are_explicit(self) -> None:
        value = build_annual_pattern_catalogue_method()

        self.assertEqual(ANNUAL_PATTERN_CATALOGUE_METHOD_DECISION, "DEC-469")
        self.assertEqual(
            ANNUAL_PATTERN_CATALOGUE_METHOD_VERSION,
            "fmp-discovery-first-annual-pattern-catalogue-method-v1",
        )
        self.assertEqual(
            GOVERNING_RESEARCH_METHOD,
            "DISCOVERY_FIRST_ANNUAL_PATTERN_CATALOGUE",
        )
        self.assertEqual(value["parent_discovery_decision"], "DEC-268")
        self.assertEqual(value["source_terminal_result_decision"], "DEC-468")

    def test_collection_is_split_year_by_year_including_partial_2026(self) -> None:
        segments = collection_segments()

        self.assertEqual(len(segments), 12)
        self.assertEqual(segments[0].label, "2015")
        self.assertEqual(segments[0].start.isoformat(), "2015-01-01")
        self.assertEqual(segments[0].end_inclusive.isoformat(), "2015-12-31")
        self.assertTrue(segments[0].complete_calendar_year)
        self.assertEqual(segments[-1].label, "2026_YTD_TO_2026_08_20")
        self.assertEqual(segments[-1].end_inclusive.isoformat(), "2026-08-20")
        self.assertFalse(segments[-1].complete_calendar_year)

    def test_currently_open_and_protected_years_are_separate(self) -> None:
        value = build_annual_pattern_catalogue_method()
        collection = value["collection"]

        self.assertEqual(CURRENTLY_OPEN_CATALOGUE_YEARS, tuple(range(2015, 2023)))
        self.assertEqual(PROTECTED_CATALOGUE_YEARS, (2023, 2024, 2025, 2026))
        self.assertEqual(collection["currently_open_catalogue_years"], list(range(2015, 2023)))
        self.assertEqual(collection["protected_catalogue_years"], [2023, 2024, 2025, 2026])
        self.assertFalse(collection["protected_2023_2026_access_authorized"])

    def test_each_year_is_catalogued_before_cross_year_comparison(self) -> None:
        value = build_annual_pattern_catalogue_method()
        annual = value["annual_catalogue"]
        comparison = value["cross_year_comparison"]

        self.assertTrue(annual["process_each_year_independently_first"])
        self.assertTrue(annual["preserve_every_pattern_surfaced_by_frozen_search"])
        self.assertTrue(annual["preserve_failed_and_negative_patterns"])
        self.assertTrue(annual["freeze_each_year_catalogue_before_cross_year_comparison"])
        self.assertTrue(comparison["begins_only_after_required_annual_catalogues_are_frozen"])

    def test_narrow_representations_are_pattern_types_not_the_method(self) -> None:
        annual = build_annual_pattern_catalogue_method()["annual_catalogue"]

        self.assertTrue(annual["state_transitions_are_pattern_type_not_method"])
        self.assertTrue(annual["pairwise_interactions_are_pattern_type_not_method"])
        self.assertTrue(
            annual["named_strategy_families_are_pattern_type_or_benchmark_not_method"]
        )

    def test_cross_year_comparison_keeps_failure_evidence(self) -> None:
        comparison = build_annual_pattern_catalogue_method()["cross_year_comparison"]

        self.assertTrue(comparison["canonical_pattern_identity_required"])
        self.assertTrue(comparison["compare_recurrence_count"])
        self.assertTrue(comparison["compare_support_by_year"])
        self.assertTrue(comparison["compare_effect_direction_and_magnitude_by_year"])
        self.assertTrue(comparison["compare_after_cost_economics_by_year"])
        self.assertTrue(comparison["record_failure_years_and_sign_flips"])
        self.assertTrue(comparison["check_concentration_in_single_year_or_small_event_set"])
        self.assertTrue(comparison["single_best_year_cannot_define_strategy_v1"])

    def test_strategy_v1_requires_cross_year_synthesis_and_freeze(self) -> None:
        strategy = build_annual_pattern_catalogue_method()["strategy_v1"]

        self.assertTrue(strategy["synthesis_requires_cross_year_evidence"])
        self.assertTrue(strategy["synthesis_requires_complete_authorized_catalogue"])
        self.assertTrue(strategy["may_combine_multiple_recurring_patterns"])
        self.assertTrue(strategy["must_receive_new_immutable_version_identity"])
        self.assertTrue(strategy["must_be_frozen_before_prospective_evidence"])
        self.assertFalse(strategy["strategy_v1_synthesis_authorized_now"])

    def test_demo_learning_creates_new_challenger_not_live_self_modification(self) -> None:
        loop = build_annual_pattern_catalogue_method()["prospective_learning_loop"]

        self.assertTrue(loop["prospective_shadow_precedes_demo_orders"])
        self.assertTrue(loop["demo_uses_fixed_strategy_version"])
        self.assertFalse(loop["running_shadow_demo_may_self_modify"])
        self.assertTrue(loop["completed_demo_may_inform_new_challenger"])
        self.assertTrue(loop["demo_observations_used_for_revision_become_training_evidence"])
        self.assertTrue(loop["revised_strategy_gets_new_version_identity"])
        self.assertTrue(loop["new_challenger_requires_fresh_prospective_evidence"])

    def test_no_execution_or_trading_authority_is_opened(self) -> None:
        authorizations = build_annual_pattern_catalogue_method()["authorizations"]

        for field, value in authorizations.items():
            self.assertFalse(value, field)


    def test_mandatory_new_session_docs_pin_annual_first_method(self) -> None:
        root = Path(__file__).resolve().parents[1]
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        guardrail = (
            root / "docs" / "research-method-operating-guardrail.md"
        ).read_text(encoding="utf-8")
        project_state = (root / "docs" / "project-state.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("year-by-year annual pattern catalogue", agents)
        self.assertIn(
            "historical collection -> year-by-year pattern catalogues",
            guardrail,
        )
        self.assertIn(
            "State transitions",
            guardrail,
        )
        self.assertIn(
            "pattern types/tools inside the annual catalogue",
            project_state,
        )

    def test_core_source_of_truth_docs_agree_on_catalogue_then_strategy_v1(self) -> None:
        root = Path(__file__).resolve().parents[1]
        master = (root / "docs" / "master-spec.md").read_text(encoding="utf-8")
        build = (root / "docs" / "build-order.md").read_text(encoding="utf-8")
        standard = (root / "docs" / "research-testing-standard.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "build a frozen pattern catalogue for each authorized historical year/segment",
            master,
        )
        self.assertIn(
            "year-by-year discovery-first market-behaviour catalogues",
            build,
        )
        self.assertIn(
            "year-by-year pattern catalogues before cross-year strategy synthesis",
            standard,
        )
        for text in (master, build, standard):
            self.assertIn("Strategy V1", text)


    def test_next_gate_is_catalogue_protocol_and_protected_history_decision(self) -> None:
        value = build_annual_pattern_catalogue_method()

        self.assertEqual(
            value["next_gate"],
            (
                "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_PROTOCOL_AND_PROTECTED_HISTORY_"
                "ACCESS_DECISION"
            ),
        )


if __name__ == "__main__":
    unittest.main()
