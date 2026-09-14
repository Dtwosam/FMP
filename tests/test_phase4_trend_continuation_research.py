from __future__ import annotations

import unittest

from fmp.research.trend_continuation import SLIPPAGE_SCENARIOS, TREND_CONTINUATION_GRID


class Phase4TrendContinuationResearchTests(unittest.TestCase):
    def test_grid_and_slippage_scenarios_are_exactly_predeclared(self) -> None:
        self.assertEqual(
            TREND_CONTINUATION_GRID,
            (("A", 1.0), ("A", 1.5), ("B", 1.0), ("B", 1.5), ("C", 1.0), ("C", 1.5)),
        )
        self.assertEqual(SLIPPAGE_SCENARIOS, (0.2, 0.5, 1.0))


if __name__ == "__main__":
    unittest.main()
