from __future__ import annotations

import unittest


class Phase6DiagnosticsTests(unittest.TestCase):
    def test_hand_checkable_classification_metrics_and_reliability_bins(self) -> None:
        from fmp.models.evaluation import classification_diagnostics

        labels = (0, 0, 1, 1)
        scores = (0.10, 0.40, 0.35, 0.80)
        ids = ("A", "B", "C", "D")
        result = classification_diagnostics(labels, scores, ids)

        self.assertAlmostEqual(result["roc_auc"], 0.75)
        self.assertAlmostEqual(result["average_precision"], 5 / 6)
        self.assertAlmostEqual(result["brier_score"], 0.158125)
        self.assertAlmostEqual(result["prevalence"], 0.5)
        self.assertAlmostEqual(result["score_min"], 0.10)
        self.assertAlmostEqual(result["score_max"], 0.80)
        self.assertAlmostEqual(result["score_mean"], 0.4125)
        self.assertAlmostEqual(result["score_median"], 0.375)
        self.assertEqual(
            result["reliability_bins"],
            (
                {"row_count": 1, "mean_model_score": 0.10, "observed_positive_rate": 0.0},
                {"row_count": 1, "mean_model_score": 0.35, "observed_positive_rate": 1.0},
                {"row_count": 1, "mean_model_score": 0.40, "observed_positive_rate": 0.0},
                {"row_count": 1, "mean_model_score": 0.80, "observed_positive_rate": 1.0},
            ),
        )

    def test_reliability_ties_sort_by_candidate_id(self) -> None:
        from fmp.models.evaluation import classification_diagnostics

        result = classification_diagnostics(
            labels=(1, 0, 1),
            scores=(0.5, 0.5, 0.5),
            candidate_ids=("C", "A", "B"),
        )
        self.assertEqual(
            tuple(item["observed_positive_rate"] for item in result["reliability_bins"]),
            (0.0, 1.0, 1.0),
        )

    def test_ten_equal_frequency_bins_differ_by_at_most_one_row(self) -> None:
        from fmp.models.evaluation import classification_diagnostics

        labels = tuple(index % 2 for index in range(12))
        scores = tuple(index / 20 for index in range(12))
        ids = tuple(f"C{index:02d}" for index in range(12))
        result = classification_diagnostics(labels, scores, ids)
        sizes = tuple(item["row_count"] for item in result["reliability_bins"])
        self.assertEqual(len(sizes), 10)
        self.assertEqual(sum(sizes), 12)
        self.assertLessEqual(max(sizes) - min(sizes), 1)

    def test_one_class_or_invalid_inputs_fail_closed(self) -> None:
        from fmp.models.evaluation import classification_diagnostics

        with self.assertRaisesRegex(ValueError, "both.*classes|one class"):
            classification_diagnostics((1, 1), (0.2, 0.8), ("A", "B"))
        with self.assertRaisesRegex(ValueError, "align"):
            classification_diagnostics((0, 1), (0.2,), ("A", "B"))
        with self.assertRaisesRegex(ValueError, "unique"):
            classification_diagnostics((0, 1), (0.2, 0.8), ("A", "A"))


if __name__ == "__main__":
    unittest.main()
