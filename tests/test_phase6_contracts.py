from __future__ import annotations

from datetime import date
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase6ContractTests(unittest.TestCase):
    def test_split_surface_is_only_fit_selection_validation(self) -> None:
        from fmp.models.contracts import allowed_phase6_split

        fit = allowed_phase6_split("fit")
        selection = allowed_phase6_split("selection")
        validation = allowed_phase6_split("validation")

        self.assertEqual((fit.start, fit.end_exclusive), (date(2015, 1, 1), date(2019, 1, 1)))
        self.assertEqual(
            (selection.start, selection.end_exclusive),
            (date(2019, 1, 1), date(2021, 1, 1)),
        )
        self.assertEqual(
            (validation.start, validation.end_exclusive),
            (date(2021, 1, 1), date(2024, 1, 1)),
        )
        for forbidden in ("final", "development", "2024", ""):
            with self.subTest(forbidden=forbidden):
                with self.assertRaises(ValueError):
                    allowed_phase6_split(forbidden)

    def test_two_frozen_strategies_are_exact_and_immutable(self) -> None:
        from fmp.models.contracts import FROZEN_STRATEGIES

        self.assertEqual(tuple(FROZEN_STRATEGIES), ("session_breakout", "volatility_breakout"))

        session = FROZEN_STRATEGIES["session_breakout"]
        self.assertEqual(session.symbol, "USDJPY")
        self.assertEqual(session.timeframe, "15m")
        self.assertEqual(session.family, "session_breakout")
        self.assertEqual(dict(session.parameters), {"buffer_pips": 5, "target_range_multiple": 1.5})

        volatility = FROZEN_STRATEGIES["volatility_breakout"]
        self.assertEqual(volatility.symbol, "USDJPY")
        self.assertEqual(volatility.timeframe, "1h")
        self.assertEqual(volatility.family, "volatility_breakout")
        self.assertEqual(dict(volatility.parameters), {"range_multiplier": 2.0, "target_r": 1.0})

        with self.assertRaises(TypeError):
            session.parameters["buffer_pips"] = 2  # type: ignore[index]

    def test_protocol_identity_constants_and_model_family_surface_are_exact(self) -> None:
        from fmp.models.contracts import (
            EXPERIMENT_ID,
            FEATURE_SET_VERSION,
            PHASE5_CHECKPOINT_SHA,
            USDJPY_PROCESSED_MANIFEST_SHA256,
            ModelFamily,
        )

        self.assertEqual(EXPERIMENT_ID, "EXP-20260915-007")
        self.assertEqual(FEATURE_SET_VERSION, "fmp-feature-v1")
        self.assertEqual(PHASE5_CHECKPOINT_SHA, "e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0")
        self.assertEqual(
            USDJPY_PROCESSED_MANIFEST_SHA256,
            "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
        )
        self.assertEqual(
            tuple(member.value for member in ModelFamily),
            ("logistic_regression", "hist_gradient_boosting"),
        )

    def test_sklearn_dependency_is_exactly_pinned(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('"scikit-learn==1.9.1"', pyproject)


if __name__ == "__main__":
    unittest.main()
