from collections import Counter
import json
import unittest

from fmp.portfolio.challengers import build_opening_range_momentum_challengers
from fmp.portfolio import StrategyLifecycle


COMMIT = "a" * 40


class Phase8AChallengerCatalogTests(unittest.TestCase):
    def test_round1_contains_exactly_36_predeclared_challengers(self) -> None:
        records = build_opening_range_momentum_challengers(code_commit=COMMIT)

        self.assertEqual(len(records), 36)
        self.assertEqual(len({item.strategy.fingerprint for item in records}), 36)
        self.assertEqual(
            Counter(item.strategy.symbol for item in records),
            {"EURUSD": 12, "GBPUSD": 12, "USDJPY": 12},
        )
        self.assertEqual(
            Counter(item.strategy.timeframe for item in records),
            {"5m": 12, "15m": 12, "1h": 12},
        )
        self.assertTrue(
            all(item.lifecycle is StrategyLifecycle.CHALLENGER for item in records)
        )
        self.assertTrue(
            all(
                item.evidence_id == "EXP-20260922-013:PREDECLARED"
                for item in records
            )
        )
        self.assertTrue(
            all(
                item.strategy.family == "opening_range_momentum"
                for item in records
            )
        )
        self.assertTrue(
            all(
                item.strategy.version == "fmp-opening-range-momentum-v1"
                for item in records
            )
        )

    def test_each_pair_timeframe_cell_has_exact_four_parameter_points(self) -> None:
        records = build_opening_range_momentum_challengers(code_commit=COMMIT)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            for timeframe in ("5m", "15m", "1h"):
                cell = [
                    item
                    for item in records
                    if item.strategy.symbol == symbol
                    and item.strategy.timeframe == timeframe
                ]
                self.assertEqual(len(cell), 4)
                params = {
                    tuple(sorted(json.loads(item.strategy.parameters_json).items()))
                    for item in cell
                }
                self.assertEqual(
                    params,
                    {
                        (
                            ("body_fraction_threshold", 0.5),
                            ("target_r_multiple", 1.0),
                        ),
                        (
                            ("body_fraction_threshold", 0.5),
                            ("target_r_multiple", 1.5),
                        ),
                        (
                            ("body_fraction_threshold", 0.7),
                            ("target_r_multiple", 1.0),
                        ),
                        (
                            ("body_fraction_threshold", 0.7),
                            ("target_r_multiple", 1.5),
                        ),
                    },
                )

    def test_catalog_rejects_invalid_code_commit(self) -> None:
        with self.assertRaises(ValueError):
            build_opening_range_momentum_challengers(code_commit="not-a-sha")


if __name__ == "__main__":
    unittest.main()
