from __future__ import annotations

import hashlib
import io
import json
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fmp.phase8b.cli import build_parser, main


class Phase8BCliBoundaryTests(unittest.TestCase):
    def test_cli_exposes_only_frozen_phase8b_commands(self) -> None:
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
        self.assertEqual(
            parser.parse_args(
                [
                    "freeze-spread-reference",
                    "--campaign-dir",
                    "campaign",
                    "--dataset-root",
                    "data",
                ]
            ).command,
            "freeze-spread-reference",
        )
        self.assertEqual(
            parser.parse_args(
                [
                    "capture-segment",
                    "--campaign-dir",
                    "campaign",
                    "--duration-seconds",
                    "60",
                ]
            ).command,
            "capture-segment",
        )
        self.assertEqual(
            parser.parse_args(
                [
                    "close-campaign",
                    "--campaign-dir",
                    "campaign",
                ]
            ).command,
            "close-campaign",
        )
        self.assertEqual(
            parser.parse_args(
                [
                    "review-campaign",
                    "--campaign-dir",
                    "campaign",
                    "--closure-id",
                    "9" * 64,
                ]
            ).command,
            "review-campaign",
        )
        for forbidden in ("run", "capture", "start", "review", "broker"):
            with self.subTest(command=forbidden):
                with self.assertRaises(SystemExit):
                    parser.parse_args([forbidden])


    def test_authorize_start_persists_preflight_before_capture(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            registration_path = root / "registration.json"
            registration_path.write_text(
                json.dumps({"required_symbols": ["EURUSD"]}) + "\n",
                encoding="utf-8",
            )
            tail = object()
            seen = {}

            def build_start(**kwargs):
                seen["start_tails"] = kwargs["bridge_tails"]
                return {"start_authorization_fingerprint": "a" * 64}

            def write_start(value, campaign_dir):
                payload = json.dumps(value, sort_keys=True).encode("utf-8")
                (campaign_dir / "start-authorization.json").write_bytes(payload)
                return {"artifacts": [{"path": "start-authorization.json"}]}

            def build_preflight(**kwargs):
                seen["preflight_tails"] = kwargs["bridge_tails"]
                seen["authorization_sha256"] = kwargs["authorization_sha256"]
                return {"capture_preflight_fingerprint": "b" * 64}

            def write_preflight(value, campaign_dir):
                (campaign_dir / "capture-preflight.json").write_text(
                    json.dumps(value),
                    encoding="utf-8",
                )
                return {"artifacts": [{"path": "capture-preflight.json"}]}

            with (
                patch(
                    "fmp.phase8b.cli.build_phase8b_campaign_start_authorization",
                    side_effect=build_start,
                ),
                patch(
                    "fmp.phase8b.cli.write_phase8b_campaign_start_authorization",
                    side_effect=write_start,
                ),
                patch(
                    "fmp.phase8b.cli.build_phase8b_capture_preflight",
                    side_effect=build_preflight,
                ),
                patch(
                    "fmp.phase8b.cli.write_phase8b_capture_preflight",
                    side_effect=write_preflight,
                ),
                redirect_stdout(io.StringIO()),
            ):
                code = main(
                    [
                        "authorize-start",
                        "--campaign-dir",
                        str(root),
                    ],
                    code_commit_resolver=lambda: "c" * 40,
                    utc_now=lambda: datetime(
                        2026, 9, 22, 14, 0, tzinfo=timezone.utc
                    ),
                    bridge_discoverer=lambda symbols: {
                        "EURUSD": Path("/fake")
                    },
                    tail_factory=lambda path, symbol: tail,
                )

            self.assertEqual(code, 0)
            self.assertIs(
                seen["start_tails"]["EURUSD"],
                seen["preflight_tails"]["EURUSD"],
            )
            self.assertEqual(
                seen["authorization_sha256"],
                hashlib.sha256(
                    (root / "start-authorization.json").read_bytes()
                ).hexdigest(),
            )
            self.assertTrue((root / "capture-preflight.json").is_file())

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
        freeze = parser.parse_args(
            [
                "freeze-spread-reference",
                "--campaign-dir",
                "campaign",
                "--dataset-root",
                "data",
            ]
        )
        capture = parser.parse_args(
            [
                "capture-segment",
                "--campaign-dir",
                "campaign",
                "--duration-seconds",
                "60",
            ]
        )
        close = parser.parse_args(
            [
                "close-campaign",
                "--campaign-dir",
                "campaign",
            ]
        )
        review = parser.parse_args(
            [
                "review-campaign",
                "--campaign-dir",
                "campaign",
                "--closure-id",
                "9" * 64,
            ]
        )
        for args in (
            qualify,
            register,
            authorize,
            freeze,
            capture,
            close,
            review,
        ):
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
