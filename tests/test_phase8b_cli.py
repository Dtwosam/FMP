from __future__ import annotations

import unittest

from fmp.phase8b.cli import build_parser


class Phase8BCliBoundaryTests(unittest.TestCase):
    def test_cli_exposes_only_design_qualify_register_and_authorize_start(self) -> None:
        parser = build_parser()
        self.assertEqual(
            parser.parse_args(
                [
                    "design",
                    "--acceptance",
                    "acceptance.json",
                    "--code-commit",
                    "a" * 40,
                    "--out",
                    "design",
                ]
            ).command,
            "design",
        )
        self.assertEqual(
            parser.parse_args(
                [
                    "qualify",
                    "--design",
                    "design.json",
                    "--out",
                    "qualification",
                ]
            ).command,
            "qualify",
        )
        self.assertEqual(
            parser.parse_args(
                [
                    "register",
                    "--design",
                    "design.json",
                    "--qualification",
                    "qualification.json",
                    "--campaign-dir",
                    "campaign",
                ]
            ).command,
            "register",
        )
        self.assertEqual(
            parser.parse_args(
                [
                    "authorize-start",
                    "--campaign-dir",
                    "campaign",
                ]
            ).command,
            "authorize-start",
        )
        for forbidden in ("run", "capture", "start", "review"):
            with self.subTest(command=forbidden):
                with self.assertRaises(SystemExit):
                    parser.parse_args([forbidden])

    def test_qualification_and_registration_have_no_symbol_path_or_threshold_overrides(self) -> None:
        parser = build_parser()
        qualify = parser.parse_args(
            [
                "qualify",
                "--design",
                "design.json",
                "--out",
                "qualification",
            ]
        )
        register = parser.parse_args(
            [
                "register",
                "--design",
                "design.json",
                "--qualification",
                "qualification.json",
                "--campaign-dir",
                "campaign",
            ]
        )
        authorize = parser.parse_args(
            [
                "authorize-start",
                "--campaign-dir",
                "campaign",
            ]
        )
        for args in (qualify, register, authorize):
            for forbidden in (
                "symbol",
                "path",
                "server",
                "minimum_prices",
                "minimum_heartbeats",
                "liveness_timeout",
                "quote_deadline",
                "slippage",
            ):
                self.assertFalse(hasattr(args, forbidden))


if __name__ == "__main__":
    unittest.main()
