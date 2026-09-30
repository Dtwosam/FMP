from __future__ import annotations

import unittest

from fmp.discovery import pattern_protocol as base
from fmp.discovery.exp063_persistence_protocol import (
    AnnualPersistenceStat,
    DESIGN_YEAR_WINDOWS,
    EXP063_PERSISTENCE_PROTOCOL_DECISION,
    MAX_DIRECTIONAL_HYPOTHESES_TOTAL,
    MAX_FROZEN_PATTERN_HYPOTHESES,
    MAX_PERSISTENCE_SHORTLIST_GLOBAL,
    PERSISTENCE_BLOCKS,
    RESERVED_ROBUSTNESS_WINDOW,
    pattern_fingerprint,
    persistence_gate_passes,
    persistence_metrics,
    protocol_fingerprint,
    protocol_payload,
)


def _stats(
    means_0p5: tuple[float, ...],
    *,
    support: int = 100,
    stress_mean: float = 0.10,
) -> tuple[AnnualPersistenceStat, ...]:
    return tuple(
        AnnualPersistenceStat(
            year=year,
            support=support,
            total_net_pips_0p5=mean * support,
            total_net_pips_1p0=stress_mean * support,
        )
        for year, mean in zip(range(2015, 2023), means_0p5, strict=True)
    )


class Exp063PersistenceProtocolTests(unittest.TestCase):
    def test_universe_and_search_budget_do_not_expand(self) -> None:
        payload = protocol_payload()

        self.assertEqual(payload["symbols"], ["EURUSD", "GBPUSD", "USDJPY"])
        self.assertEqual(payload["timeframes"], ["5m", "15m", "1h"])
        self.assertEqual(payload["horizons_minutes"], [60, 240])
        self.assertEqual(MAX_DIRECTIONAL_HYPOTHESES_TOTAL, 74700)
        self.assertEqual(
            MAX_DIRECTIONAL_HYPOTHESES_TOTAL,
            base.MAX_DIRECTIONAL_HYPOTHESES_TOTAL,
        )
        self.assertEqual(MAX_PERSISTENCE_SHORTLIST_GLOBAL, 180)
        self.assertEqual(MAX_FROZEN_PATTERN_HYPOTHESES, 54)

    def test_chronology_is_eight_seen_years_with_reserved_block_closed(self) -> None:
        self.assertEqual(
            tuple(window.start.year for window in DESIGN_YEAR_WINDOWS),
            tuple(range(2015, 2023)),
        )
        self.assertEqual(
            tuple(window.end_exclusive.year for window in DESIGN_YEAR_WINDOWS),
            tuple(range(2016, 2024)),
        )
        self.assertEqual(
            PERSISTENCE_BLOCKS,
            ((2015, 2016), (2017, 2018), (2019, 2020), (2021, 2022)),
        )
        self.assertEqual(
            RESERVED_ROBUSTNESS_WINDOW.start.isoformat(),
            "2023-01-01",
        )
        self.assertEqual(
            RESERVED_ROBUSTNESS_WINDOW.end_exclusive.isoformat(),
            "2026-08-21",
        )

        chronology = protocol_payload()["chronology"]
        self.assertEqual(
            chronology["2015_2022_label"],
            "ALREADY_SEEN_DESIGN_EVIDENCE",
        )
        self.assertTrue(
            chronology["2019_2022_may_not_be_called_fresh_validation"]
        )
        self.assertTrue(chronology["reserved_2023_2026_remains_closed"])

    def test_persistence_metrics_equal_weight_years_for_stability(self) -> None:
        stats = _stats((0.4, 0.5, 0.3, 0.6, 0.35, 0.45, 0.25, 0.55))
        metrics = persistence_metrics(stats)

        self.assertEqual(metrics["total_support"], 800)
        self.assertEqual(metrics["minimum_year_support"], 100)
        self.assertEqual(metrics["positive_year_count"], 8)
        self.assertAlmostEqual(
            metrics["lower_half_annual_mean_net_pips_0p5"],
            (0.30 + 0.35 + 0.40 + 0.45) / 4.0,
        )
        self.assertAlmostEqual(
            metrics["minimum_two_year_block_mean_net_pips_0p5"],
            (0.30 + 0.35) / 2.0,
        )
        self.assertTrue(persistence_gate_passes(stats))

    def test_single_late_period_strength_cannot_rescue_weak_early_block(self) -> None:
        stats = _stats((-0.40, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 4.00))
        metrics = persistence_metrics(stats)

        self.assertGreater(metrics["aggregate_mean_net_pips_0p5"], 0.25)
        self.assertGreaterEqual(metrics["positive_year_count"], 6)
        self.assertLess(
            metrics["two_year_block_mean_net_pips_0p5"]["2015_2016"],
            0,
        )
        self.assertFalse(persistence_gate_passes(stats))

    def test_lower_half_gate_rejects_concentrated_edge_even_with_positive_blocks(
        self,
    ) -> None:
        stats = _stats((-0.40, 0.50, -0.30, 0.50, 0.10, 0.50, 0.10, 4.00))
        metrics = persistence_metrics(stats)

        self.assertEqual(metrics["positive_year_count"], 6)
        self.assertGreater(
            metrics["minimum_two_year_block_mean_net_pips_0p5"],
            0,
        )
        self.assertLessEqual(
            metrics["lower_half_annual_mean_net_pips_0p5"],
            0,
        )
        self.assertFalse(persistence_gate_passes(stats))

    def test_prior_discovery_support_and_mean_gates_are_not_relaxed(self) -> None:
        payload = protocol_payload()["persistence_gate"]
        self.assertGreaterEqual(
            payload["minimum_support_each_year"],
            base.MIN_DISCOVERY_YEAR_SUPPORT,
        )
        self.assertGreaterEqual(
            payload["minimum_aggregate_mean_net_pips_0p5"],
            base.MIN_DISCOVERY_AGGREGATE_MEAN_NET_PIPS,
        )
        self.assertEqual(payload["minimum_positive_years"], 6)
        self.assertEqual(payload["year_count"], 8)
        self.assertTrue(payload["require_positive_lower_half_annual_mean"])
        self.assertTrue(
            payload["require_positive_each_two_year_block_mean"]
        )

    def test_successor_pattern_identity_is_new_and_order_independent(self) -> None:
        first = pattern_fingerprint(
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=240,
            direction="LONG",
            predicates=(
                ("return_1h", "HIGH"),
                (base.SESSION_DIMENSION, "LONDON"),
            ),
        )
        second = pattern_fingerprint(
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=240,
            direction="LONG",
            predicates=(
                (base.SESSION_DIMENSION, "LONDON"),
                ("return_1h", "HIGH"),
            ),
        )
        predecessor = base.pattern_fingerprint(
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=240,
            direction="LONG",
            predicates=(
                ("return_1h", "HIGH"),
                (base.SESSION_DIMENSION, "LONDON"),
            ),
        )

        self.assertEqual(first, second)
        self.assertNotEqual(first, predecessor)
        self.assertEqual(len(first), 64)

    def test_protocol_is_source_only_and_deterministic(self) -> None:
        payload = protocol_payload()
        self.assertEqual(
            payload["decision"],
            EXP063_PERSISTENCE_PROTOCOL_DECISION,
        )
        self.assertEqual(
            payload["freeze"]["output_kind"],
            "RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED",
        )
        self.assertTrue(
            payload["freeze"]["reserved_2023_2026_window_remains_closed"]
        )
        for value in payload["authorizations"].values():
            self.assertFalse(value)

        self.assertEqual(protocol_fingerprint(), protocol_fingerprint())
        self.assertEqual(len(protocol_fingerprint()), 64)

    def test_annual_stat_contract_is_strict(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            AnnualPersistenceStat(
                year=2015,
                support=1.5,  # type: ignore[arg-type]
                total_net_pips_0p5=1.0,
                total_net_pips_1p0=1.0,
            )
        with self.assertRaisesRegex(ValueError, "outside 2015-2022"):
            AnnualPersistenceStat(
                year=2023,
                support=100,
                total_net_pips_0p5=1.0,
                total_net_pips_1p0=1.0,
            )


if __name__ == "__main__":
    unittest.main()
