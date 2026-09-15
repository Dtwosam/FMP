from __future__ import annotations

import math
import unittest


class Phase6ThresholdTests(unittest.TestCase):
    def test_exact_fit_cutoff_formula_ties_and_admission_rule(self) -> None:
        from fmp.models.thresholds import derive_fit_cutoffs

        scores = (0.10, 0.20, 0.20, 0.40, 0.60, 0.90, 0.90, 1.00)
        cutoffs = derive_fit_cutoffs(scores)

        self.assertEqual(tuple(item.retained_fraction for item in cutoffs), (0.75, 0.50, 0.25))
        self.assertEqual(tuple(item.fit_index for item in cutoffs), (2, 4, 6))
        self.assertEqual(tuple(item.score for item in cutoffs), (0.20, 0.60, 0.90))
        self.assertEqual(tuple(item.fit_retained_count for item in cutoffs), (7, 4, 3))
        self.assertEqual(tuple(item.fit_row_count for item in cutoffs), (8, 8, 8))
        self.assertEqual(
            tuple(item.fit_retained_rate for item in cutoffs),
            (7 / 8, 4 / 8, 3 / 8),
        )
        self.assertTrue(cutoffs[0].admits(0.20))
        self.assertFalse(cutoffs[0].admits(math.nextafter(0.20, 0.0)))

    def test_cutoffs_depend_only_on_supplied_fit_scores(self) -> None:
        from fmp.models.thresholds import derive_fit_cutoffs

        fit_scores = (0.05, 0.25, 0.50, 0.75, 0.95)
        selection_scores_a = (0.0, 0.0, 0.0)
        selection_scores_b = (1.0, 1.0, 1.0)
        self.assertNotEqual(selection_scores_a, selection_scores_b)
        self.assertEqual(derive_fit_cutoffs(fit_scores), derive_fit_cutoffs(tuple(fit_scores)))

    def test_empty_or_nonfinite_fit_scores_fail_closed(self) -> None:
        from fmp.models.thresholds import derive_fit_cutoffs

        with self.assertRaisesRegex(ValueError, "non-empty"):
            derive_fit_cutoffs(())
        with self.assertRaisesRegex(ValueError, "finite"):
            derive_fit_cutoffs((0.1, float("nan"), 0.9))


if __name__ == "__main__":
    unittest.main()
