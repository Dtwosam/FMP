from __future__ import annotations

import json
import unittest

from fmp.discovery.pattern_protocol import (
    CONTINUOUS_FEATURES,
    DISCOVERY_CELLS,
    DISCOVERY_RESULT_AUTHORIZED,
    DISCOVERY_WINDOW,
    CONFIRMATION_WINDOW,
    VALIDATION_WINDOW,
    RESERVED_ROBUSTNESS_WINDOW,
    MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON,
    MAX_ATOMIC_STATES,
    MAX_DIRECTIONAL_HYPOTHESES_PER_CELL_HORIZON,
    MAX_DIRECTIONAL_HYPOTHESES_TOTAL,
    MAX_DISCOVERY_SHORTLIST,
    MAX_DISCOVERY_SHORTLIST_PER_CELL_HORIZON,
    MAX_FROZEN_PATTERN_HYPOTHESES,
    MAX_PATTERN_DEPTH,
    QUANTILE_STATES,
    SESSION_DIMENSION,
    SESSION_STATES,
    SOURCE_ACCESS_AUTHORIZED,
    empirical_tertile_cutpoints,
    pattern_fingerprint,
    protocol_fingerprint,
    protocol_payload,
    quantile_state,
    session_state,
)


class Exp061PatternProtocolTests(unittest.TestCase):
    def test_exact_market_universe_and_chronology_are_frozen(self) -> None:
        self.assertEqual(len(DISCOVERY_CELLS), 18)
        self.assertEqual(
            set(DISCOVERY_CELLS),
            {
                (symbol, timeframe, horizon)
                for symbol in ("EURUSD", "GBPUSD", "USDJPY")
                for timeframe in ("5m", "15m", "1h")
                for horizon in (60, 240)
            },
        )
        self.assertEqual(
            (
                DISCOVERY_WINDOW.start.isoformat(),
                DISCOVERY_WINDOW.end_exclusive.isoformat(),
                CONFIRMATION_WINDOW.start.isoformat(),
                CONFIRMATION_WINDOW.end_exclusive.isoformat(),
                VALIDATION_WINDOW.start.isoformat(),
                VALIDATION_WINDOW.end_exclusive.isoformat(),
                RESERVED_ROBUSTNESS_WINDOW.start.isoformat(),
                RESERVED_ROBUSTNESS_WINDOW.end_exclusive.isoformat(),
            ),
            (
                "2015-01-01",
                "2018-01-01",
                "2018-01-01",
                "2019-01-01",
                "2019-01-01",
                "2023-01-01",
                "2023-01-01",
                "2026-08-21",
            ),
        )

    def test_search_is_bounded_without_predefined_strategy_families(self) -> None:
        self.assertEqual(len(CONTINUOUS_FEATURES), 20)
        self.assertEqual(QUANTILE_STATES, ("LOW", "MID", "HIGH"))
        self.assertEqual(len(SESSION_STATES), 5)
        self.assertEqual(MAX_ATOMIC_STATES, 65)
        self.assertEqual(MAX_PATTERN_DEPTH, 2)
        self.assertEqual(MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON, 2075)
        self.assertEqual(MAX_DIRECTIONAL_HYPOTHESES_PER_CELL_HORIZON, 4150)
        self.assertEqual(MAX_DIRECTIONAL_HYPOTHESES_TOTAL, 74700)
        self.assertEqual(MAX_DISCOVERY_SHORTLIST_PER_CELL_HORIZON, 10)
        self.assertEqual(MAX_DISCOVERY_SHORTLIST, 180)
        self.assertEqual(MAX_FROZEN_PATTERN_HYPOTHESES, 54)

        encoded = json.dumps(protocol_payload(), sort_keys=True)
        for old_family in (
            "session_breakout",
            "trend_continuation",
            "mean_reversion",
            "previous_day_rejection",
            "volatility_breakout",
            "session_sweep_rejection",
        ):
            self.assertNotIn(old_family, encoded)

    def test_empirical_tertiles_use_exact_order_statistics_and_skip_ties(self) -> None:
        values = list(range(300))
        self.assertEqual(empirical_tertile_cutpoints(values), (99.0, 199.0))
        cuts = empirical_tertile_cutpoints(values)
        self.assertEqual(quantile_state(99, cuts), "LOW")
        self.assertEqual(quantile_state(100, cuts), "MID")
        self.assertEqual(quantile_state(199, cuts), "MID")
        self.assertEqual(quantile_state(200, cuts), "HIGH")

        self.assertIsNone(empirical_tertile_cutpoints([1.0] * 300))
        self.assertIsNone(empirical_tertile_cutpoints(list(range(299))))
        self.assertIsNone(quantile_state(float("nan"), cuts))

    def test_session_state_has_exact_precedence(self) -> None:
        base = {
            "is_london_new_york_overlap": False,
            "is_london_session": False,
            "is_new_york_session": False,
            "is_asia_session": False,
        }
        self.assertEqual(session_state(base), "OFF_SESSION")
        self.assertEqual(
            session_state({**base, "is_asia_session": True}),
            "ASIA",
        )
        self.assertEqual(
            session_state(
                {
                    **base,
                    "is_asia_session": True,
                    "is_new_york_session": True,
                }
            ),
            "NEW_YORK",
        )
        self.assertEqual(
            session_state(
                {
                    **base,
                    "is_asia_session": True,
                    "is_new_york_session": True,
                    "is_london_session": True,
                }
            ),
            "LONDON",
        )
        self.assertEqual(
            session_state(
                {
                    **base,
                    "is_asia_session": True,
                    "is_new_york_session": True,
                    "is_london_session": True,
                    "is_london_new_york_overlap": True,
                }
            ),
            "LONDON_NEW_YORK_OVERLAP",
        )
        with self.assertRaisesRegex(ValueError, "must be boolean"):
            session_state({**base, "is_asia_session": 1})

    def test_pattern_identity_is_order_independent_but_strict(self) -> None:
        first = pattern_fingerprint(
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
            direction="LONG",
            predicates=(
                ("return_1h", "HIGH"),
                (SESSION_DIMENSION, "LONDON"),
            ),
        )
        second = pattern_fingerprint(
            symbol="EURUSD",
            timeframe="15m",
            horizon_minutes=60,
            direction="LONG",
            predicates=(
                (SESSION_DIMENSION, "LONDON"),
                ("return_1h", "HIGH"),
            ),
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

        with self.assertRaisesRegex(ValueError, "same dimension"):
            pattern_fingerprint(
                symbol="EURUSD",
                timeframe="15m",
                horizon_minutes=60,
                direction="LONG",
                predicates=(("return_1h", "LOW"), ("return_1h", "HIGH")),
            )
        with self.assertRaisesRegex(ValueError, "unsupported discovery pattern dimension"):
            pattern_fingerprint(
                symbol="EURUSD",
                timeframe="15m",
                horizon_minutes=60,
                direction="LONG",
                predicates=(("made_up_indicator", "HIGH"),),
            )
        with self.assertRaisesRegex(ValueError, "invalid state"):
            pattern_fingerprint(
                symbol="EURUSD",
                timeframe="15m",
                horizon_minutes=60,
                direction="LONG",
                predicates=(("return_1h", "VERY_HIGH"),),
            )

    def test_protocol_keeps_execution_and_reserved_window_locked(self) -> None:
        payload = protocol_payload()
        self.assertFalse(SOURCE_ACCESS_AUTHORIZED)
        self.assertFalse(DISCOVERY_RESULT_AUTHORIZED)
        self.assertTrue(payload["freeze"]["reserved_2023_2026_window_remains_closed"])
        self.assertEqual(
            payload["ranking"]["maximum_discovery_shortlist_global"],
            180,
        )
        self.assertTrue(payload["ranking"]["confirmation_does_not_rerank"])
        self.assertEqual(payload["confirmation_gate"]["freeze_order"], "preserve_discovery_rank")
        self.assertEqual(
            payload["freeze"]["output_kind"],
            "PATTERN_HYPOTHESIS_NOT_EXECUTABLE_STRATEGY",
        )
        for value in payload["authorizations"].values():
            self.assertFalse(value)

    def test_protocol_fingerprint_is_deterministic(self) -> None:
        self.assertEqual(protocol_fingerprint(), protocol_fingerprint())
        self.assertEqual(len(protocol_fingerprint()), 64)


if __name__ == "__main__":
    unittest.main()
