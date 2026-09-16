from __future__ import annotations

import unittest

from fmp.shadow.review_compiler import _distribution


class Phase8ReviewSpreadPrecisionTests(unittest.TestCase):
    def test_binary_float_noise_does_not_leak_into_canonical_spread_evidence(self) -> None:
        self.assertEqual(
            _distribution([0.2999999999994]),
            {"median_pips": 0.3, "p95_pips": 0.3},
        )
        self.assertEqual(
            _distribution([0.3999999999994]),
            {"median_pips": 0.4, "p95_pips": 0.4},
        )


if __name__ == "__main__":
    unittest.main()
