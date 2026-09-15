from __future__ import annotations

import unittest

import numpy as np

from fmp.models.contracts import ModelFamily


class Phase6EstimatorTests(unittest.TestCase):
    def test_logistic_regression_parameters_are_exact(self) -> None:
        from fmp.models.estimators import build_estimator

        model = build_estimator(ModelFamily.LOGISTIC_REGRESSION)
        params = model.get_params()
        expected = {
            "penalty": "l2",
            "C": 1.0,
            "solver": "lbfgs",
            "tol": 1e-8,
            "fit_intercept": True,
            "class_weight": None,
            "max_iter": 2000,
            "warm_start": False,
            "random_state": None,
        }
        self.assertEqual({key: params[key] for key in expected}, expected)

    def test_histogram_boosting_parameters_and_seed_are_exact(self) -> None:
        from fmp.models.estimators import build_estimator

        model = build_estimator(ModelFamily.HIST_GRADIENT_BOOSTING)
        params = model.get_params()
        expected = {
            "loss": "log_loss",
            "learning_rate": 0.05,
            "max_iter": 100,
            "max_leaf_nodes": 15,
            "max_depth": 3,
            "min_samples_leaf": 20,
            "l2_regularization": 1.0,
            "max_features": 1.0,
            "max_bins": 255,
            "early_stopping": False,
            "warm_start": False,
            "class_weight": None,
            "random_state": 20260915,
        }
        self.assertEqual({key: params[key] for key in expected}, expected)

    def test_repeated_fits_produce_identical_score_digests(self) -> None:
        from fmp.models.estimators import fit_estimator, score_digest, score_estimator

        X = np.array(
            [
                [-2.0, 0.0],
                [-1.0, 0.5],
                [-0.5, 1.0],
                [0.5, 0.0],
                [1.0, 0.5],
                [2.0, 1.0],
            ],
            dtype=float,
        )
        y = np.array([0, 0, 0, 1, 1, 1], dtype=int)
        ids = tuple(f"C{i}" for i in range(len(y)))

        for family in ModelFamily:
            first = fit_estimator(family, X, y)
            second = fit_estimator(family, X, y)
            first_scores = score_estimator(first, X)
            second_scores = score_estimator(second, X)
            self.assertEqual(
                score_digest(ids, first_scores),
                score_digest(ids, second_scores),
                family.value,
            )
            np.testing.assert_allclose(first_scores, second_scores, rtol=0.0, atol=0.0)

    def test_score_digest_binds_candidate_ids_and_scores(self) -> None:
        from fmp.models.estimators import score_digest

        ids = ("A", "B")
        scores = np.array([0.25, 0.75], dtype=float)
        digest = score_digest(ids, scores)
        self.assertEqual(digest, score_digest(ids, scores.copy()))
        self.assertNotEqual(digest, score_digest(("B", "A"), scores))
        self.assertNotEqual(digest, score_digest(ids, np.array([0.25, 0.76])))

    def test_hidden_model_family_is_rejected(self) -> None:
        from fmp.models.estimators import build_estimator

        with self.assertRaises((TypeError, ValueError)):
            build_estimator("random_forest")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
