from __future__ import annotations

import unittest

from fmp.data.phase2.full_history_cli import build_parser


class FullHistoryCliTests(unittest.TestCase):
    def test_cli_has_fixed_pairs_workers_and_no_date_range(self) -> None:
        parser = build_parser()
        args = parser.parse_args([
            "--endpoint", "https://project.example/functions/v1/fmp-raw-read",
            "--pair", "EURUSD",
            "--out", ".out",
            "--workers", "4",
        ])
        self.assertEqual(args.pair, "EURUSD")
        self.assertEqual(args.workers, 4)
        self.assertFalse(hasattr(args, "start"))
        self.assertFalse(hasattr(args, "end"))

        for pair in ("EURUSD", "GBPUSD", "USDJPY"):
            parsed = parser.parse_args([
                "--endpoint", "https://project.example/functions/v1/fmp-raw-read",
                "--pair", pair,
                "--out", ".out",
            ])
            self.assertEqual(parsed.pair, pair)


if __name__ == "__main__":
    unittest.main()
