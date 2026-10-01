from __future__ import annotations

import unittest

from fmp.discovery.exp064_continuous_stability_protocol import (
    AnnualContinuousEffectStat,
    EXP064_CONTINUOUS_STABILITY_PROTOCOL_DECISION,
    EXP064_CONTINUOUS_STABILITY_PROTOCOL_VERSION,
    HYPOTHESES_PER_CELL_HORIZON,
    MAX_DIRECTIONAL_HYPOTHESES_TOTAL,
    MAX_FROZEN_GLOBAL,
    MAX_SHORTLIST_GLOBAL,
    continuous_stability_gate_passes,
    continuous_stability_metrics,
    effect_hypothesis_fingerprint,
    empirical_midrank_percentile,
    protocol_fingerprint,
    protocol_payload,
    rank_calibration_values,
    selected_tail_accepts,
    signed_rank_slope,
)


def _stats(
    *,
    slope: float = 0.5,
    tail_half: float = 0.5,
    tail_stress: float = 0.1,
) -> tuple[AnnualContinuousEffectStat, ...]:
    return tuple(
        AnnualContinuousEffectStat(
            year=year,
            evaluable_support=400,
            selected_tail_support=100,
            signed_rank_slope_net_pips_0p5=slope,
            selected_tail_mean_net_pips_0p5=tail_half,
            selected_tail_mean_net_pips_1p0=tail_stress,
        )
        for year in range(2015, 2023)
    )


class Exp064ContinuousStabilityProtocolTests(unittest.TestCase):
    def test_identity_and_search_bound_are_exact(self) -> None:
        payload = protocol_payload()

        self.assertEqual(
            EXP064_CONTINUOUS_STABILITY_PROTOCOL_DECISION,
            "DEC-452",
        )
        self.assertEqual(
            EXP064_CONTINUOUS_STABILITY_PROTOCOL_VERSION,
            "fmp-exp064-continuous-stability-protocol-v1",
        )
        self.assertEqual(payload["experiment_id"], "EXP-20261001-064")
        self.assertEqual(
            payload["source_direction_merge_sha"],
            "e55df61f766ae49c72f04ac6259928252ae113dc",
        )
        self.assertEqual(
            payload["source_direction_blob_sha"],
            "6a7de1e93515fd3771e3763641ee6a07e425ee8a",
        )
        self.assertEqual(HYPOTHESES_PER_CELL_HORIZON, 80)
        self.assertEqual(MAX_DIRECTIONAL_HYPOTHESES_TOTAL, 1440)
        self.assertEqual(MAX_SHORTLIST_GLOBAL, 90)
        self.assertEqual(MAX_FROZEN_GLOBAL, 36)
        self.assertEqual(
            payload["hypothesis"]["unit"],
            "single_feature_direction_polarity",
        )
        self.assertFalse(payload["hypothesis"]["interactions_authorized"])

    def test_rank_calibration_requires_rows_and_distinct_values(self) -> None:
        self.assertIsNone(rank_calibration_values([float(i) for i in range(599)]))
        self.assertIsNone(rank_calibration_values([1.0] * 600))

        calibration = rank_calibration_values(
            [float(i % 100) for i in range(600)]
        )
        self.assertIsNotNone(calibration)
        assert calibration is not None
        self.assertEqual(len(calibration), 600)
        self.assertEqual(calibration, tuple(sorted(calibration)))

    def test_empirical_midrank_ties_and_tail_rules_are_deterministic(self) -> None:
        calibration = tuple(
            float(value)
            for value in (
                [0] * 150
                + [1] * 150
                + [2] * 150
                + [3] * 150
            )
        )

        self.assertEqual(empirical_midrank_percentile(calibration, -1.0), 0.0)
        self.assertEqual(empirical_midrank_percentile(calibration, 4.0), 1.0)
        self.assertEqual(
            empirical_midrank_percentile(calibration, 0.0),
            0.125,
        )
        self.assertEqual(
            empirical_midrank_percentile(calibration, 3.0),
            0.875,
        )
        self.assertTrue(
            selected_tail_accepts(percentile=0.875, polarity="INCREASING")
        )
        self.assertFalse(
            selected_tail_accepts(percentile=0.125, polarity="INCREASING")
        )
        self.assertTrue(
            selected_tail_accepts(percentile=0.125, polarity="DECREASING")
        )
        self.assertFalse(
            selected_tail_accepts(percentile=0.875, polarity="DECREASING")
        )

    def test_signed_rank_slope_respects_polarity(self) -> None:
        percentiles = (0.0, 0.25, 0.5, 0.75, 1.0)
        outcomes = (-2.0, -1.0, 0.0, 1.0, 2.0)

        increasing = signed_rank_slope(
            percentiles,
            outcomes,
            polarity="INCREASING",
        )
        decreasing = signed_rank_slope(
            percentiles,
            outcomes,
            polarity="DECREASING",
        )

        self.assertEqual(increasing, 4.0)
        self.assertEqual(decreasing, -4.0)

    def test_strong_stable_effect_passes_frozen_gate(self) -> None:
        annual = _stats()

        metrics = continuous_stability_metrics(annual)

        self.assertEqual(metrics["total_selected_tail_support"], 800)
        self.assertEqual(metrics["minimum_year_selected_tail_support"], 100)
        self.assertEqual(metrics["positive_slope_year_count"], 8)
        self.assertEqual(metrics["positive_tail_mean_year_count"], 8)
        self.assertEqual(
            metrics["equal_year_signed_rank_slope_net_pips_0p5"],
            0.5,
        )
        self.assertEqual(
            metrics["equal_year_selected_tail_mean_net_pips_0p5"],
            0.5,
        )
        self.assertEqual(
            metrics["equal_year_selected_tail_mean_net_pips_1p0"],
            0.1,
        )
        self.assertTrue(continuous_stability_gate_passes(annual))

    def test_weak_two_year_block_fails_even_with_positive_aggregate(self) -> None:
        annual = list(_stats())
        for index in (6, 7):
            row = annual[index]
            annual[index] = AnnualContinuousEffectStat(
                year=row.year,
                evaluable_support=row.evaluable_support,
                selected_tail_support=row.selected_tail_support,
                signed_rank_slope_net_pips_0p5=-0.1,
                selected_tail_mean_net_pips_0p5=-0.1,
                selected_tail_mean_net_pips_1p0=0.1,
            )

        metrics = continuous_stability_metrics(tuple(annual))

        self.assertGreater(
            metrics["equal_year_signed_rank_slope_net_pips_0p5"],
            0.25,
        )
        self.assertLessEqual(
            metrics[
                "minimum_two_year_block_signed_rank_slope_net_pips_0p5"
            ],
            0.0,
        )
        self.assertFalse(continuous_stability_gate_passes(tuple(annual)))

    def test_non_positive_stress_mean_fails(self) -> None:
        annual = _stats(tail_stress=0.0)

        self.assertFalse(continuous_stability_gate_passes(annual))

    def test_fingerprint_is_deterministic_and_identity_sensitive(self) -> None:
        first = effect_hypothesis_fingerprint(
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
            feature_name="return_1h",
            direction="LONG",
            polarity="INCREASING",
        )
        second = effect_hypothesis_fingerprint(
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
            feature_name="return_1h",
            direction="LONG",
            polarity="INCREASING",
        )
        opposite = effect_hypothesis_fingerprint(
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
            feature_name="return_1h",
            direction="LONG",
            polarity="DECREASING",
        )

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        self.assertNotEqual(first, opposite)
        self.assertEqual(len(protocol_fingerprint()), 64)

    def test_chronology_evidence_semantics_and_authorities_are_locked(self) -> None:
        payload = protocol_payload()

        self.assertEqual(payload["evidence_label"], "RETROSPECTIVE_ALREADY_SEEN")
        self.assertFalse(payload["untouched_oos"])
        self.assertEqual(
            payload["chronology"]["design_role"],
            "ALREADY_SEEN_DESIGN_EVIDENCE",
        )
        self.assertEqual(
            payload["chronology"]["reserved_robustness_start"],
            "2023-01-01",
        )
        self.assertFalse(
            payload["chronology"]["reserved_robustness_opened"]
        )
        self.assertTrue(
            payload["rank_transform"]["reserve_rows_must_not_affect_calibration"]
        )
        for field, value in payload["authorizations"].items():
            self.assertFalse(value, field)


if __name__ == "__main__":
    unittest.main()
