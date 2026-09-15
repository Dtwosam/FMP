from __future__ import annotations

import unittest

import numpy as np
import polars as pl


class Phase6PreprocessingTests(unittest.TestCase):
    def test_fit_state_is_fit_only_and_transform_does_not_mutate_it(self) -> None:
        from fmp.models.preprocessing import fit_preprocessor, transform_features

        fit = pl.DataFrame(
            {
                "a": [1.0, 2.0, None, 4.0],
                "b": [True, False, True, False],
                "c": [10.0, float("inf"), 30.0, 40.0],
            }
        )
        state = fit_preprocessor(fit, standardize=True)
        snapshot = state

        selection_a = pl.DataFrame({"a": [1000.0], "b": [True], "c": [-999.0]})
        selection_b = pl.DataFrame({"a": [-1000.0], "b": [False], "c": [999.0]})
        _ = transform_features(selection_a, state)
        _ = transform_features(selection_b, state)

        self.assertEqual(state, snapshot)
        self.assertEqual(state.input_columns, ("a", "b", "c"))
        self.assertEqual(state.medians, (2.0, 0.5, 30.0))
        self.assertEqual(state.null_counts, (1, 0, 1))
        self.assertTrue(state.standardize)
        self.assertIsNotNone(state.scaler_mean)
        self.assertIsNotNone(state.scaler_scale)

    def test_nonfinite_and_booleans_have_deterministic_numeric_semantics(self) -> None:
        from fmp.models.preprocessing import fit_preprocessor, transform_features

        fit = pl.DataFrame(
            {
                "x": [1.0, float("nan"), float("inf"), -float("inf"), 5.0],
                "flag": [True, False, None, True, False],
            }
        )
        state = fit_preprocessor(fit, standardize=False)
        transformed = transform_features(fit, state)

        self.assertEqual(state.medians, (3.0, 0.5))
        self.assertEqual(state.null_counts, (3, 1))
        self.assertEqual(transformed.dtype, np.float64)
        self.assertTrue(np.isfinite(transformed).all())
        np.testing.assert_allclose(
            transformed,
            np.array(
                [
                    [1.0, 1.0],
                    [3.0, 0.0],
                    [3.0, 0.5],
                    [3.0, 1.0],
                    [5.0, 0.0],
                ],
                dtype=float,
            ),
        )

    def test_all_null_fit_column_fails_closed(self) -> None:
        from fmp.models.preprocessing import fit_preprocessor

        frame = pl.DataFrame({"a": [1.0, 2.0], "b": [None, None]})
        with self.assertRaisesRegex(ValueError, "all-null|entirely null"):
            fit_preprocessor(frame, standardize=False)

    def test_transform_requires_frozen_column_order(self) -> None:
        from fmp.models.preprocessing import fit_preprocessor, transform_features

        fit = pl.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0]})
        state = fit_preprocessor(fit, standardize=False)
        with self.assertRaisesRegex(ValueError, "column order"):
            transform_features(pl.DataFrame({"b": [3.0], "a": [1.0]}), state)


if __name__ == "__main__":
    unittest.main()
