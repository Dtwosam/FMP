from __future__ import annotations

import unittest
from datetime import date

from fmp.research.contracts import (
    DEVELOPMENT_SPLIT,
    FINAL_TEST_SPLIT,
    VALIDATION_SPLIT,
    ExperimentSpec,
    allowed_split,
)


class Phase4ResearchContractTests(unittest.TestCase):
    def test_frozen_splits_are_non_overlapping_and_exact(self) -> None:
        self.assertEqual(DEVELOPMENT_SPLIT.start, date(2015, 1, 1))
        self.assertEqual(DEVELOPMENT_SPLIT.end_exclusive, date(2021, 1, 1))
        self.assertEqual(VALIDATION_SPLIT.start, date(2021, 1, 1))
        self.assertEqual(VALIDATION_SPLIT.end_exclusive, date(2024, 1, 1))
        self.assertEqual(FINAL_TEST_SPLIT.start, date(2024, 1, 1))
        self.assertEqual(FINAL_TEST_SPLIT.end_exclusive, date(2026, 8, 21))
        self.assertEqual(DEVELOPMENT_SPLIT.end_exclusive, VALIDATION_SPLIT.start)
        self.assertEqual(VALIDATION_SPLIT.end_exclusive, FINAL_TEST_SPLIT.start)

    def test_normal_research_api_refuses_final_test(self) -> None:
        self.assertEqual(allowed_split("development"), DEVELOPMENT_SPLIT)
        self.assertEqual(allowed_split("validation"), VALIDATION_SPLIT)
        with self.assertRaisesRegex(ValueError, "final test"):
            allowed_split("final")

    def test_experiment_spec_hash_is_stable_and_mapping_order_independent(self) -> None:
        base = dict(
            experiment_id="EXP-20260914-001",
            hypothesis="session breakout may show continuation after costs",
            code_commit="test-commit",
            processed_manifest_sha256="a" * 64,
            schema_version="fmp-canonical-1m-v1",
            family_id="session-breakout",
            strategy_version="v1",
            symbol="EURUSD",
            timeframe="15m",
            split_name="development",
            slippage_pips=0.2,
            commission_config={"model": "zero"},
            financing_config={"model": "zero"},
            risk_config={"default_risk_fraction": 0.0025},
        )
        first = ExperimentSpec(parameters={"buffer_pips": 2, "target_range_multiple": 1.0}, **base)
        second = ExperimentSpec(parameters={"target_range_multiple": 1.0, "buffer_pips": 2}, **base)
        self.assertEqual(first.config_sha256(), first.config_sha256())
        self.assertEqual(first.config_sha256(), second.config_sha256())
        self.assertEqual(len(first.config_sha256()), 64)

    def test_experiment_spec_rejects_final_split(self) -> None:
        with self.assertRaisesRegex(ValueError, "final test"):
            ExperimentSpec(
                experiment_id="EXP-20260914-002",
                hypothesis="must remain untouched",
                code_commit="test-commit",
                processed_manifest_sha256="b" * 64,
                schema_version="fmp-canonical-1m-v1",
                family_id="session-breakout",
                strategy_version="v1",
                symbol="EURUSD",
                timeframe="15m",
                split_name="final",
                parameters={"buffer_pips": 0, "target_range_multiple": 1.0},
                slippage_pips=0.2,
                commission_config={"model": "zero"},
                financing_config={"model": "zero"},
                risk_config={"default_risk_fraction": 0.0025},
            )


if __name__ == "__main__":
    unittest.main()
