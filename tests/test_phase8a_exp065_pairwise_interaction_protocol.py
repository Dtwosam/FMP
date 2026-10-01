from __future__ import annotations

import unittest

from fmp.discovery.exp065_pairwise_interaction_protocol import (
    AnnualPairwiseInteractionStat,
    DEC459_DIRECTION_BLOB_SHA,
    DEC459_MERGE_SHA,
    HYPOTHESES_PER_CELL_HORIZON,
    MAX_DIRECTIONAL_HYPOTHESES_TOTAL,
    MAX_FROZEN_GLOBAL,
    MAX_FROZEN_PER_CELL_HORIZON,
    MAX_SHORTLIST_GLOBAL,
    MAX_SHORTLIST_PER_CELL_HORIZON,
    PAIR_COUNT,
    canonical_feature_pair,
    feature_pairs,
    interaction_calibration_values,
    interaction_percentile,
    pair_hypothesis_fingerprint,
    pairwise_interaction_gate_passes,
    pairwise_interaction_raw,
    partial_interaction_slope,
    protocol_payload,
    selected_tail_accepts,
    validate_protocol,
)
from fmp.discovery.pattern_protocol import CONTINUOUS_FEATURES


class Exp065PairwiseInteractionProtocolTests(unittest.TestCase):
    def test_protocol_binds_dec459_and_exact_market_search_bounds(self) -> None:
        value = validate_protocol()

        self.assertEqual(
            DEC459_MERGE_SHA,
            "c0d8ba052cc0cd662149aa787722874c7207ce4a",
        )
        self.assertEqual(
            DEC459_DIRECTION_BLOB_SHA,
            "7d9350f714bfec7cc39ebf76b2e6e313261e9a68",
        )
        self.assertEqual(value["decision"], "DEC-460")
        self.assertEqual(value["experiment_id"], "EXP-20261001-065")
        self.assertEqual(value["source_experiment_id"], "EXP-20261001-064")
        self.assertEqual(
            value["bounded_universe"]["symbols"],
            ["EURUSD", "GBPUSD", "USDJPY"],
        )
        self.assertEqual(value["bounded_universe"]["timeframes"], ["5m", "15m", "1h"])
        self.assertEqual(value["bounded_universe"]["horizons_minutes"], [60, 240])
        self.assertEqual(len(value["bounded_universe"]["continuous_features"]), 20)
        self.assertEqual(PAIR_COUNT, 190)
        self.assertEqual(HYPOTHESES_PER_CELL_HORIZON, 760)
        self.assertEqual(MAX_DIRECTIONAL_HYPOTHESES_TOTAL, 13680)

    def test_feature_pairs_are_unordered_distinct_and_complete(self) -> None:
        pairs = feature_pairs()

        self.assertEqual(len(pairs), 190)
        self.assertEqual(len(set(pairs)), 190)
        self.assertTrue(all(left != right for left, right in pairs))
        for left, right in pairs:
            self.assertLess(
                CONTINUOUS_FEATURES.index(left),
                CONTINUOUS_FEATURES.index(right),
            )

        first = pairs[0]
        self.assertEqual(canonical_feature_pair(*first), first)
        self.assertEqual(canonical_feature_pair(first[1], first[0]), first)
        with self.assertRaisesRegex(ValueError, "distinct"):
            canonical_feature_pair(first[0], first[0])

    def test_interaction_raw_transform_is_symmetric_and_bounded(self) -> None:
        self.assertEqual(pairwise_interaction_raw(0.0, 0.0), 0.5)
        self.assertEqual(pairwise_interaction_raw(1.0, 1.0), 0.5)
        self.assertEqual(pairwise_interaction_raw(0.0, 1.0), -0.5)
        self.assertEqual(pairwise_interaction_raw(1.0, 0.0), -0.5)
        self.assertEqual(pairwise_interaction_raw(0.5, 0.9), 0.0)
        self.assertEqual(
            pairwise_interaction_raw(0.2, 0.8),
            pairwise_interaction_raw(0.8, 0.2),
        )

    def test_interaction_percentile_composes_dec452_midrank_helper_correctly(self) -> None:
        calibration = (-0.5, 0.0, 0.5)

        self.assertEqual(interaction_percentile(-0.5, calibration), 1.0 / 6.0)
        self.assertEqual(interaction_percentile(0.0, calibration), 0.5)
        self.assertEqual(interaction_percentile(0.5, calibration), 5.0 / 6.0)

    def test_interaction_calibration_fails_closed_below_frozen_minimum(self) -> None:
        feature_a = [0.10, 0.20, 0.30, 0.40]
        feature_b = [0.15, 0.25, 0.35, 0.45]

        with self.assertRaisesRegex(
            ValueError,
            "does not satisfy frozen row/distinct requirements",
        ):
            interaction_calibration_values(feature_a, feature_b)

    def test_selected_tail_semantics_are_exact(self) -> None:
        self.assertTrue(
            selected_tail_accepts(
                interaction_percentile_value=0.75,
                polarity="INCREASING",
            )
        )
        self.assertFalse(
            selected_tail_accepts(
                interaction_percentile_value=0.749,
                polarity="INCREASING",
            )
        )
        self.assertTrue(
            selected_tail_accepts(
                interaction_percentile_value=0.25,
                polarity="DECREASING",
            )
        )
        self.assertFalse(
            selected_tail_accepts(
                interaction_percentile_value=0.251,
                polarity="DECREASING",
            )
        )

    def test_partial_interaction_slope_controls_constituent_main_effects(self) -> None:
        feature_a = [0.10, 0.20, 0.35, 0.45, 0.60, 0.70, 0.85, 0.95]
        feature_b = [0.15, 0.40, 0.25, 0.80, 0.55, 0.90, 0.35, 0.65]
        interaction = [0.20, 0.75, 0.45, 0.95, 0.10, 0.65, 0.35, 0.85]
        outcomes = [
            1.0
            + 2.0 * (left - 0.5)
            - 1.5 * (right - 0.5)
            + 3.0 * (pair - 0.5)
            for left, right, pair in zip(feature_a, feature_b, interaction)
        ]

        slope = partial_interaction_slope(
            feature_a,
            feature_b,
            interaction,
            outcomes,
        )

        self.assertAlmostEqual(slope, 3.0, places=10)

    def test_stable_incremental_interaction_gate_can_pass(self) -> None:
        stats = [
            AnnualPairwiseInteractionStat(
                year=year,
                evaluable_support=400,
                selected_tail_support=80,
                signed_partial_interaction_slope_net_pips_0p5=0.40,
                selected_tail_mean_net_pips_0p5=0.50,
                selected_tail_incremental_residual_mean_net_pips_0p5=0.10,
                selected_tail_mean_net_pips_1p0=0.10,
            )
            for year in range(2015, 2023)
        ]

        self.assertTrue(pairwise_interaction_gate_passes(stats))

    def test_negative_incremental_block_fails_closed(self) -> None:
        stats = [
            AnnualPairwiseInteractionStat(
                year=year,
                evaluable_support=400,
                selected_tail_support=80,
                signed_partial_interaction_slope_net_pips_0p5=0.40,
                selected_tail_mean_net_pips_0p5=0.50,
                selected_tail_incremental_residual_mean_net_pips_0p5=(
                    -0.20 if year in (2019, 2020) else 0.10
                ),
                selected_tail_mean_net_pips_1p0=0.10,
            )
            for year in range(2015, 2023)
        ]

        self.assertFalse(pairwise_interaction_gate_passes(stats))

    def test_fingerprint_is_pair_order_invariant_but_identity_sensitive(self) -> None:
        left, right = feature_pairs()[0]
        first = pair_hypothesis_fingerprint(
            symbol="EURUSD",
            timeframe="5m",
            horizon_minutes=60,
            feature_a=left,
            feature_b=right,
            direction="LONG",
            polarity="INCREASING",
        )
        reverse = pair_hypothesis_fingerprint(
            symbol="EURUSD",
            timeframe="5m",
            horizon_minutes=60,
            feature_a=right,
            feature_b=left,
            direction="LONG",
            polarity="INCREASING",
        )
        changed = pair_hypothesis_fingerprint(
            symbol="EURUSD",
            timeframe="5m",
            horizon_minutes=60,
            feature_a=left,
            feature_b=right,
            direction="SHORT",
            polarity="INCREASING",
        )

        self.assertEqual(first, reverse)
        self.assertNotEqual(first, changed)

    def test_search_expansion_is_countered_by_tighter_freeze_caps(self) -> None:
        value = protocol_payload()

        self.assertEqual(MAX_SHORTLIST_PER_CELL_HORIZON, 3)
        self.assertEqual(MAX_SHORTLIST_GLOBAL, 54)
        self.assertEqual(MAX_FROZEN_PER_CELL_HORIZON, 1)
        self.assertEqual(MAX_FROZEN_GLOBAL, 18)
        self.assertEqual(
            value["ranking"]["selected_tail_event_jaccard_threshold"],
            0.95,
        )

    def test_chronology_and_all_execution_paths_remain_locked(self) -> None:
        value = validate_protocol()

        self.assertEqual(value["chronology"]["design_start"], "2015-01-01")
        self.assertEqual(value["chronology"]["design_end_exclusive"], "2023-01-01")
        self.assertEqual(
            value["chronology"]["design_role"],
            "ALREADY_SEEN_DESIGN_EVIDENCE",
        )
        self.assertEqual(
            value["chronology"]["reserved_robustness_start"],
            "2023-01-01",
        )
        self.assertEqual(
            value["chronology"]["reserved_robustness_end"],
            "2026-08-20",
        )
        self.assertFalse(value["chronology"]["reserved_robustness_opened"])

        for field in (
            "source_access_authorized",
            "historical_execution_authorized",
            "historical_result_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(value[field], field)

        self.assertEqual(
            value["next_gate"],
            "SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_MINER",
        )


if __name__ == "__main__":
    unittest.main()
