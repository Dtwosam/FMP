from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from fmp.shadow.cli import build_parser, main
from fmp.shadow.qualification import QualificationOutcome


UTC = timezone.utc
NOW = datetime(2026, 9, 17, 20, 0, tzinfo=UTC)
CODE_COMMIT = "c" * 40
SESSION = "a" * 64
FINGERPRINT = "b" * 64
SERVER = "FPMarketsSC-Demo2"


class FakeQualification:
    outcome = QualificationOutcome.PASS

    def to_record(self) -> dict[str, object]:
        return {
            "outcome": "PASS",
            "account_fingerprint": FINGERPRINT,
            "bridge_session_id": SESSION,
            "server": SERVER,
            "price_count": 100,
            "heartbeat_count": 6,
            "boundary_audit": {
                "connector_protocol": "fmp-mt5-demo-file-bridge-v1",
                "provider": "FP_MARKETS_MT5_DEMO",
                "transport": "MT5_FILE_COMMON_JSONL",
                "bridge_file": "FMP/phase8-usdjpy-feed.jsonl",
                "instrument": "USDJPY",
                "allowed_servers": ["FPMarketsSC-Demo", "FPMarketsSC-Demo2"],
            },
        }


class Phase8CliTests(unittest.TestCase):
    def test_parser_exposes_no_credentials_or_transport_overrides(self) -> None:
        parser = build_parser()
        help_text = parser.format_help()
        self.assertIn("qualify", help_text)
        self.assertIn("run", help_text)
        for forbidden in (
            "--account-id",
            "--token",
            "--host",
            "--base-url",
            "--method",
            "--path",
            "--filename",
            "--server",
            "--instrument",
        ):
            self.assertNotIn(forbidden, help_text)

        for forbidden in (
            "--account-id",
            "--token",
            "--host",
            "--path",
            "--filename",
            "--server",
            "--instrument",
        ):
            with self.subTest(forbidden=forbidden), self.assertRaises(SystemExit):
                parser.parse_args(["qualify", "--out", "out", forbidden, "x"])

    def test_qualify_auto_discovers_fixed_bridge_and_requires_no_credentials(self) -> None:
        discovered: list[Path] = []
        tail = object()
        qualification_calls: list[object] = []

        with tempfile.TemporaryDirectory() as tmp:
            rc = main(
                ["qualify", "--out", tmp],
                environ={
                    "OANDA_PRACTICE_ACCOUNT_ID": "must-be-ignored",
                    "OANDA_PRACTICE_TOKEN": "must-be-ignored",
                },
                bridge_discoverer=lambda: Path("/fixed/common/FMP/phase8-usdjpy-feed.jsonl"),
                tail_factory=lambda path: discovered.append(path) or tail,
                qualify_command=lambda value, **_: qualification_calls.append(value) or FakeQualification(),
                utc_now=lambda: NOW,
                monotonic_ns=lambda: 1,
            )
            self.assertEqual(rc, 0)
            self.assertEqual(
                discovered,
                [Path("/fixed/common/FMP/phase8-usdjpy-feed.jsonl")],
            )
            self.assertEqual(qualification_calls, [tail])

            path = Path(tmp) / "qualification.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(record["outcome"], "PASS")
            self.assertEqual(record["price_count"], 100)
            self.assertEqual(record["heartbeat_count"], 6)
            self.assertEqual(record["account_fingerprint"], FINGERPRINT)
            self.assertEqual(record["bridge_session_id"], SESSION)
            self.assertEqual(record["server"], SERVER)
            self.assertEqual(record["boundary_audit"]["provider"], "FP_MARKETS_MT5_DEMO")
            raw = path.read_text(encoding="utf-8")
            self.assertNotIn("must-be-ignored", raw)

    def test_run_auto_discovers_same_fixed_bridge_and_passes_no_secret_surface(self) -> None:
        discovered: list[Path] = []
        tail = object()
        calls: list[dict[str, object]] = []
        with tempfile.TemporaryDirectory() as tmp:
            campaign = Path(tmp)
            rc = main(
                ["run", "--campaign-dir", str(campaign)],
                environ={"OANDA_PRACTICE_TOKEN": "ignored"},
                bridge_discoverer=lambda: Path("/fixed/common/FMP/phase8-usdjpy-feed.jsonl"),
                tail_factory=lambda path: discovered.append(path) or tail,
                run_command=lambda **kwargs: calls.append(kwargs) or 0,
                code_commit_resolver=lambda: CODE_COMMIT,
                utc_now=lambda: NOW,
                monotonic_ns=lambda: 1,
            )
            self.assertEqual(rc, 0)
            self.assertEqual(len(calls), 1)
            self.assertIs(calls[0]["bridge_tail"], tail)
            self.assertEqual(calls[0]["campaign_dir"], campaign)
            self.assertEqual(calls[0]["code_commit"], CODE_COMMIT)
            for forbidden in ("account_id", "token", "stream_factory", "server", "path"):
                self.assertNotIn(forbidden, calls[0])
            self.assertEqual(
                discovered,
                [Path("/fixed/common/FMP/phase8-usdjpy-feed.jsonl")],
            )

    def test_active_cli_source_has_no_oanda_secret_or_transport_surface(self) -> None:
        source = Path("src/fmp/shadow/cli.py").read_text(encoding="utf-8")
        for forbidden in (
            "OANDA_PRACTICE_ACCOUNT_ID",
            "OANDA_PRACTICE_TOKEN",
            "OandaPracticePricingStream",
            "qualify_stream",
            "account_id=",
            "token=",
            "stream_factory=",
        ):
            self.assertNotIn(forbidden, source)

    def test_script_delegates_to_shadow_cli_and_contains_no_order_surface(self) -> None:
        source = Path("scripts/phase8_shadow.py").read_text(encoding="utf-8")
        self.assertIn("from fmp.shadow.cli import main", source)
        self.assertIn("raise SystemExit(main())", source)
        for forbidden in ("order_send", "/orders", "/trades", "/positions"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
