from __future__ import annotations

import unittest

from fmp.discovery.annual_pattern_catalogue_protocol import (
    ANNUAL_CATALOGUE_PROTOCOL_DECISION,
    ANNUAL_CATALOGUE_PROTOCOL_VERSION,
    ANNUAL_SEGMENT_COUNT,
    CANONICAL_CROSS_YEAR_HYPOTHESIS_COUNT,
    DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
    EXPERIMENT_ID,
    FULL_COLLECTION_CATALOGUE_USE_AUTHORIZED,
    MIN_ANNUAL_EVALUABLE_SUPPORT,
    PATTERN_CONDITION_COUNT,
    PATTERN_FAMILY_COUNTS,
    TOTAL_ANNUAL_DIRECTIONAL_RECORDS,
    TRANSITION_LAGS_MINUTES,
    annual_prior_tertile_cutpoints,
    annual_quantile_state,
    annual_record_identity,
    canonical_pattern_fingerprint,
    cross_year_gate_passes,
    enumerate_pattern_definitions,
    protocol_payload,
)


class AnnualPatternCatalogueProtocolTests(unittest.TestCase):
    def test_protocol_identity_and_method_binding(self) -> None:
        value = protocol_payload()

        self.assertEqual(ANNUAL_CATALOGUE_PROTOCOL_DECISION, "DEC-470")
        self.assertEqual(
            ANNUAL_CATALOGUE_PROTOCOL_VERSION,
            "fmp-annual-pattern-catalogue-protocol-v1",
        )
        self.assertEqual(EXPERIMENT_ID, "EXP-20261002-067")
        self.assertEqual(value["source_method_decision"], "DEC-469")
        self.assertEqual(
            value["source_method_merge_sha"],
            "248ee27036d54c2ce3ad3ad051dcc8b0cbbbcfd1",
        )
        self.assertEqual(
            value["governing_research_method"],
            "DISCOVERY_FIRST_ANNUAL_PATTERN_CATALOGUE",
        )

    def test_exact_pattern_grammar_and_search_volume_are_frozen(self) -> None:
        patterns = enumerate_pattern_definitions()

        self.assertEqual(
            PATTERN_FAMILY_COUNTS,
            {
                "SNAPSHOT_SINGLE": 65,
                "SNAPSHOT_PAIR": 2010,
                "SAME_DIMENSION_TRANSITION": 410,
            },
        )
        self.assertEqual(PATTERN_CONDITION_COUNT, 2485)
        self.assertEqual(len(patterns), 2485)
        self.assertEqual(len(set(patterns)), 2485)
        self.assertEqual(TRANSITION_LAGS_MINUTES, (60, 240))
        self.assertEqual(ANNUAL_SEGMENT_COUNT, 12)
        self.assertEqual(DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT, 89460)
        self.assertEqual(TOTAL_ANNUAL_DIRECTIONAL_RECORDS, 1073520)
        self.assertEqual(CANONICAL_CROSS_YEAR_HYPOTHESIS_COUNT, 89460)

    def test_annual_catalogue_preserves_every_pattern_record(self) -> None:
        annual = protocol_payload()["annual_evidence"]

        self.assertTrue(annual["preserve_every_nominal_pattern_record"])
        self.assertEqual(
            annual["minimum_support_for_evaluable_label"],
            MIN_ANNUAL_EVALUABLE_SUPPORT,
        )
        self.assertTrue(annual["insufficient_support_records_are_preserved"])
        self.assertFalse(annual["annual_catalogue_selects_winners"])
        self.assertFalse(annual["annual_catalogue_reranks_patterns"])
        self.assertIn("mean_net_pips_0p5", annual["required_statistics"])
        self.assertIn("mean_net_pips_1p0", annual["required_statistics"])

    def test_state_calibration_requires_prior_only_minimum(self) -> None:
        too_short = [float(i) for i in range(299)]
        enough = [float(i) for i in range(300)]

        self.assertIsNone(annual_prior_tertile_cutpoints(too_short))
        cuts = annual_prior_tertile_cutpoints(enough)
        self.assertIsNotNone(cuts)
        assert cuts is not None
        self.assertEqual(annual_quantile_state(-1.0, enough), "LOW")
        self.assertEqual(annual_quantile_state(1000.0, enough), "HIGH")

    def test_canonical_pattern_identity_excludes_year(self) -> None:
        pattern = enumerate_pattern_definitions()[0]
        fingerprint = canonical_pattern_fingerprint(
            pattern=pattern,
            symbol="EURUSD",
            timeframe="5m",
            horizon_minutes=60,
            direction="LONG",
        )
        left = annual_record_identity(
            canonical_pattern_fingerprint_value=fingerprint,
            annual_segment_label="2015",
        )
        right = annual_record_identity(
            canonical_pattern_fingerprint_value=fingerprint,
            annual_segment_label="2016",
        )

        self.assertNotEqual(left, right)
        self.assertEqual(len(fingerprint), 64)
        self.assertEqual(
            fingerprint,
            canonical_pattern_fingerprint(
                pattern=pattern,
                symbol="EURUSD",
                timeframe="5m",
                horizon_minutes=60,
                direction="LONG",
            ),
        )

    def test_cross_year_gate_is_predeclared_before_results(self) -> None:
        self.assertTrue(
            cross_year_gate_passes(
                evaluable_segments=12,
                base_positive_segments=10,
                stress_positive_segments=8,
                median_annual_mean_net_pips_0p5=0.20,
                pooled_mean_net_pips_0p5=0.30,
                pooled_mean_net_pips_1p0=0.05,
                sign_flips=2,
            )
        )
        self.assertFalse(
            cross_year_gate_passes(
                evaluable_segments=12,
                base_positive_segments=9,
                stress_positive_segments=8,
                median_annual_mean_net_pips_0p5=0.20,
                pooled_mean_net_pips_0p5=0.30,
                pooled_mean_net_pips_1p0=0.05,
                sign_flips=2,
            )
        )
        self.assertFalse(
            cross_year_gate_passes(
                evaluable_segments=8,
                base_positive_segments=8,
                stress_positive_segments=8,
                median_annual_mean_net_pips_0p5=0.20,
                pooled_mean_net_pips_0p5=0.30,
                pooled_mean_net_pips_1p0=0.05,
                sign_flips=0,
            )
        )

    def test_2023_2026_are_explicitly_repurposed_for_catalogue_research(self) -> None:
        access = protocol_payload()["historical_access_decision"]

        self.assertTrue(FULL_COLLECTION_CATALOGUE_USE_AUTHORIZED)
        self.assertTrue(access["full_collection_catalogue_use_authorized"])
        self.assertTrue(
            access["former_exp061_reserved_2023_2026_catalogue_use_authorized"]
        )
        self.assertFalse(
            access[
                "former_exp061_reserved_2023_2026_remains_untouched_oos_for_strategy_v1"
            ]
        )
        self.assertTrue(
            access["fresh_strategy_v1_evidence_begins_after_strategy_v1_freeze"]
        )
        self.assertIn("does_not_reopen", access["scope"])

    def test_annual_boundaries_keep_each_year_independent(self) -> None:
        value = protocol_payload()

        self.assertEqual(len(value["annual_segments"]), 12)
        self.assertIn(
            "exit_timestamp_utc",
            value["annual_boundary_rule"],
        )
        self.assertIn(
            "same annual segment",
            value["annual_boundary_rule"],
        )

    def test_no_execution_strategy_or_trading_authority_is_opened(self) -> None:
        value = protocol_payload()
        access = value["historical_access_decision"]

        self.assertFalse(access["historical_artifact_read_authorized_now"])
        self.assertFalse(access["historical_catalogue_execution_authorized_now"])
        for field, enabled in value["authorizations"].items():
            self.assertFalse(enabled, field)

    def test_next_gate_is_source_only_miner(self) -> None:
        self.assertEqual(
            protocol_payload()["next_gate"],
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_MINER",
        )


if __name__ == "__main__":
    unittest.main()
