from __future__ import annotations

import unittest


class Phase7ContractTests(unittest.TestCase):
    def test_stage1_and_stage2_windows_are_exact(self) -> None:
        from fmp.walkforward.contracts import STAGE1_WINDOW, STAGE2_WINDOWS

        self.assertEqual(STAGE1_WINDOW.name, "stage1-2024")
        self.assertEqual(STAGE1_WINDOW.start.isoformat(), "2024-01-01")
        self.assertEqual(STAGE1_WINDOW.end_exclusive.isoformat(), "2025-01-01")
        self.assertEqual(
            tuple(window.name for window in STAGE2_WINDOWS),
            (
                "2025-Q1",
                "2025-Q2",
                "2025-Q3",
                "2025-Q4",
                "2026-Q1",
                "2026-Q2",
                "2026-partial-Q3",
            ),
        )
        self.assertEqual(STAGE2_WINDOWS[-1].end_exclusive.isoformat(), "2026-08-21")

    def test_candidate_surface_is_exactly_two_frozen_rules(self) -> None:
        from fmp.walkforward.contracts import FROZEN_CANDIDATES

        self.assertEqual(tuple(FROZEN_CANDIDATES), ("session_breakout", "volatility_breakout"))

        session = FROZEN_CANDIDATES["session_breakout"]
        self.assertEqual(session.candidate_id, "session_breakout")
        self.assertEqual(session.symbol, "USDJPY")
        self.assertEqual(session.timeframe, "15m")
        self.assertEqual(dict(session.parameters), {"buffer_pips": 5, "target_range_multiple": 1.5})

        volatility = FROZEN_CANDIDATES["volatility_breakout"]
        self.assertEqual(volatility.candidate_id, "volatility_breakout")
        self.assertEqual(volatility.symbol, "USDJPY")
        self.assertEqual(volatility.timeframe, "1h")
        self.assertEqual(dict(volatility.parameters), {"range_multiplier": 2.0, "target_r": 1.0})

    def test_protocol_constants_are_exact(self) -> None:
        from fmp.walkforward.contracts import (
            EXPERIMENT_ID,
            GATING_SLIPPAGE_SCENARIOS,
            MAX_WARMUP_DAYS,
            PHASE6_CHECKPOINT_SHA,
            REQUESTED_RISK_FRACTION,
            SLIPPAGE_SCENARIOS,
            STARTING_EQUITY_USD,
            USDJPY_PHASE2_ARTIFACT_ID,
            USDJPY_PHASE2_ZIP_SHA256,
            USDJPY_PROCESSED_MANIFEST_SHA256,
        )

        self.assertEqual(EXPERIMENT_ID, "EXP-20260915-008")
        self.assertEqual(PHASE6_CHECKPOINT_SHA, "5d387b7ca93d04c498eb04c376e0dd92f1fe1953")
        self.assertEqual(USDJPY_PHASE2_ARTIFACT_ID, 10327600628)
        self.assertEqual(
            USDJPY_PHASE2_ZIP_SHA256,
            "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72",
        )
        self.assertEqual(
            USDJPY_PROCESSED_MANIFEST_SHA256,
            "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
        )
        self.assertEqual(SLIPPAGE_SCENARIOS, (0.2, 0.5, 1.0))
        self.assertEqual(GATING_SLIPPAGE_SCENARIOS, (0.2, 0.5))
        self.assertEqual(MAX_WARMUP_DAYS, 7)
        self.assertEqual(STARTING_EQUITY_USD, 100_000.0)
        self.assertEqual(REQUESTED_RISK_FRACTION, 0.0025)

    def test_contract_mappings_are_immutable(self) -> None:
        from fmp.walkforward.contracts import FROZEN_CANDIDATES

        with self.assertRaises(TypeError):
            FROZEN_CANDIDATES["other"] = FROZEN_CANDIDATES["session_breakout"]  # type: ignore[index]
        with self.assertRaises(TypeError):
            FROZEN_CANDIDATES["session_breakout"].parameters["buffer_pips"] = 0  # type: ignore[index]

    def test_arbitrary_window_is_rejected(self) -> None:
        from fmp.walkforward.contracts import STAGE1_WINDOW, STAGE2_WINDOWS, allowed_phase7_window

        self.assertIs(allowed_phase7_window("stage1-2024"), STAGE1_WINDOW)
        for window in STAGE2_WINDOWS:
            self.assertIs(allowed_phase7_window(window.name), window)

        for forbidden in ("final", "2024-Q1", "custom", "development", ""):
            with self.assertRaises(ValueError):
                allowed_phase7_window(forbidden)


if __name__ == "__main__":
    unittest.main()
