from __future__ import annotations

import math
import random
import unittest

from fmp.research.multiple_testing import benjamini_yekutieli


class BenjaminiYekutieliTests(unittest.TestCase):
    def test_known_four_hypothesis_family(self) -> None:
        result = benjamini_yekutieli(
            {"d": 0.5, "b": 0.01, "a": 0.001, "c": 0.03},
            family_id="frozen-synthetic-four",
            total_hypotheses=4,
        )
        self.assertEqual(result.method, "benjamini_yekutieli")
        self.assertEqual(result.total_hypotheses, 4)
        self.assertEqual(result.rejected_hypotheses, ("a", "b"))
        q = dict(result.adjusted_p_values)
        self.assertAlmostEqual(q["a"], 0.001 * 4 * (25 / 12))
        self.assertAlmostEqual(q["b"], 0.01 * 2 * (25 / 12))
        self.assertAlmostEqual(q["c"], 0.03 * 4 / 3 * (25 / 12))
        self.assertEqual(q["d"], 1.0)

    def test_input_order_does_not_change_adjusted_values(self) -> None:
        a = benjamini_yekutieli(
            {"beta": 0.2, "alpha": 0.02, "gamma": 0.01},
            family_id="frozen", total_hypotheses=3,
        )
        b = benjamini_yekutieli(
            {"gamma": 0.01, "beta": 0.2, "alpha": 0.02},
            family_id="frozen", total_hypotheses=3,
        )
        self.assertEqual(a, b)
        self.assertEqual(tuple(k for k, _ in a.adjusted_p_values),
                         ("alpha", "beta", "gamma"))

    def test_ties_have_same_adjusted_value(self) -> None:
        result = benjamini_yekutieli(
            {"a": 0.01, "b": 0.01, "c": 0.2},
            family_id="tied", total_hypotheses=3,
        )
        q = dict(result.adjusted_p_values)
        self.assertAlmostEqual(q["a"], 0.0275)
        self.assertAlmostEqual(q["b"], 0.0275)
        self.assertAlmostEqual(q["c"], 0.2 * (11 / 6))
        self.assertEqual(result.rejected_hypotheses, ("a", "b"))

    def test_historical_unknown_or_incomplete_trial_family_is_rejected(self) -> None:
        p = {"one": 0.001, "two": 0.02}
        for count in (None, 0, 1, 3, False, 2.0):
            with self.subTest(count=count):
                with self.assertRaises(ValueError):
                    benjamini_yekutieli(
                        p, family_id="unverified-census", total_hypotheses=count,
                    )

    def test_invalid_p_values_are_not_silently_dropped(self) -> None:
        for value in (float("nan"), float("inf"), -0.01, 1.01, True, None, "0.01"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    benjamini_yekutieli(
                        {"bad": value}, family_id="invalid-p", total_hypotheses=1,
                    )

    def test_family_identity_and_significance_level_are_validated(self) -> None:
        with self.assertRaises(ValueError):
            benjamini_yekutieli({"a": 0.1}, family_id=" ", total_hypotheses=1)
        with self.assertRaises(ValueError):
            benjamini_yekutieli({" a": 0.1}, family_id="frozen", total_hypotheses=1)
        with self.assertRaises(ValueError):
            benjamini_yekutieli({}, family_id="frozen", total_hypotheses=0)
        for level in (float("nan"), -0.1, 0.0, 1.0, True):
            with self.subTest(level=level):
                with self.assertRaises(ValueError):
                    benjamini_yekutieli(
                        {"a": 0.01}, family_id="frozen",
                        total_hypotheses=1, alpha=level,
                    )

    def test_boundary_probabilities_and_all_null_family(self) -> None:
        result = benjamini_yekutieli(
            {"zero": 0.0, "one": 1.0},
            family_id="boundaries", total_hypotheses=2,
        )
        self.assertEqual(dict(result.adjusted_p_values), {"one": 1.0, "zero": 0.0})
        self.assertEqual(result.rejected_hypotheses, ("zero",))
        empty = benjamini_yekutieli(
            {f"h{i}": 0.5 for i in range(10)},
            family_id="all-high-p", total_hypotheses=10,
        )
        self.assertEqual(empty.rejected_hypotheses, ())

    def test_seeded_independent_null_smoke_only(self) -> None:
        # A code smoke check, NOT the annual catalogue's null calibration.
        rng = random.Random(7)
        families_with_any_rejection = 0
        for i in range(800):
            result = benjamini_yekutieli(
                {f"h{k}": rng.random() for k in range(12)},
                family_id=f"synthetic-null-{i}", total_hypotheses=12,
            )
            families_with_any_rejection += bool(result.rejected_hypotheses)
        self.assertLessEqual(families_with_any_rejection, 30)


if __name__ == "__main__":
    unittest.main()
