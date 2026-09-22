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

from fmp.phase8b.bridge import Phase8BBridgeStartRecord
from fmp.phase8b.cli import main as phase8b_main
from fmp.phase8b.design import (
    BRIDGE_FILE_BY_SYMBOL,
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
)
from fmp.phase8b.readiness import (
    PHASE8B_CAMPAIGN_READINESS_PROTOCOL,
    Phase8BCampaignReadinessOutcome,
    build_phase8b_campaign_readiness,
    validate_phase8b_campaign_readiness,
)
from fmp.phase8b.registration import PHASE8B_REGISTRATION_PROTOCOL


UTC = timezone.utc
NOW = datetime(2026, 9, 22, 21, 30, tzinfo=UTC)
SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY"]
SESSIONS = {
    "EURUSD": "1" * 64,
    "GBPUSD": "2" * 64,
    "USDJPY": "3" * 64,
}
ACCOUNT = "4" * 64
SERVER = "FPMarketsSC-Demo"


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _registration() -> dict[str, object]:
    payload = {
        "protocol": PHASE8B_REGISTRATION_PROTOCOL,
        "experiment_id": "EXP-20260922-018",
        "design_sha256": "5" * 64,
        "qualification_sha256": "6" * 64,
        "design_fingerprint": "7" * 64,
        "qualification_code_commit": "a" * 40,
        "registration_code_commit": "b" * 40,
        "registered_at_utc": "2026-09-22T20:00:00Z",
        "champion_set_id": "champion-fixture",
        "champion_set_fingerprint": "8" * 64,
        "strategy_count": 3,
        "strategy_fingerprints": ["9" * 64, "a" * 64, "b" * 64],
        "strategies": [
            {"fingerprint": "9" * 64},
            {"fingerprint": "a" * 64},
            {"fingerprint": "b" * 64},
        ],
        "required_symbols": list(SYMBOLS),
        "required_timeframes": ["15m"],
        "provider": MT5_PROVIDER,
        "transport": MT5_TRANSPORT,
        "connector_protocol": MT5_BRIDGE_PROTOCOL,
        "bridge_file_by_symbol": {
            symbol: BRIDGE_FILE_BY_SYMBOL[symbol] for symbol in SYMBOLS
        },
        "allowed_servers": ["FPMarketsSC-Demo", "FPMarketsSC-Demo2"],
        "account_fingerprint": ACCOUNT,
        "server": SERVER,
        "bridge_session_id_by_symbol": dict(SESSIONS),
        "liveness": {
            "bridge_timeout_seconds": 15.0,
            "market_quiet_threshold_seconds": 15.0,
            "quote_deadline_seconds": 5.0,
        },
        "slippage_scenarios": [0.2, 0.5, 1.0],
        "campaign_start_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    return payload | {"registration_fingerprint": _digest(payload)}


class _Tail:
    def __init__(self, symbol: str, *, session: str | None = None) -> None:
        self.start_record = Phase8BBridgeStartRecord(
            protocol=MT5_BRIDGE_PROTOCOL,
            bridge_session_id=session or SESSIONS[symbol],
            symbol=symbol,
            server=SERVER,
            account_fingerprint=ACCOUNT,
            account_mode="DEMO",
            bridge_start_time_msc=1_795_000_000_000,
        )
        self.read_calls = 0

    def read_available(self):
        self.read_calls += 1
        raise AssertionError("readiness must not consume post-EOF records")


def _tails() -> dict[str, _Tail]:
    return {symbol: _Tail(symbol) for symbol in SYMBOLS}


def _identity_copy(registration: dict[str, object]) -> dict[str, object]:
    return {
        field: registration[field]
        for field in (
            "champion_set_id",
            "champion_set_fingerprint",
            "strategy_count",
            "strategy_fingerprints",
            "strategies",
            "required_symbols",
            "required_timeframes",
            "provider",
            "transport",
            "connector_protocol",
            "bridge_file_by_symbol",
            "account_fingerprint",
            "server",
            "liveness",
            "slippage_scenarios",
        )
    }


class Phase8BCampaignReadinessTests(unittest.TestCase):
    def test_registered_three_symbol_campaign_needs_start_without_consuming_ticks(self) -> None:
        registration = _registration()
        tails = _tails()
        result = build_phase8b_campaign_readiness(
            registration=registration,
            registration_sha256="c" * 64,
            start_authorization=None,
            start_authorization_sha256=None,
            capture_preflight=None,
            spread_reference=None,
            bridge_tails=tails,
            inspected_at_utc=NOW,
            campaign_terminal_present=False,
        )
        self.assertEqual(result["protocol"], PHASE8B_CAMPAIGN_READINESS_PROTOCOL)
        self.assertEqual(
            result["outcome"],
            Phase8BCampaignReadinessOutcome.NEEDS_START.value,
        )
        self.assertEqual(result["next_action"], "authorize-start")
        self.assertEqual(result["required_symbols"], SYMBOLS)
        self.assertFalse(result["capture_prerequisites_satisfied"])
        self.assertFalse(result["readiness_report_is_authorization"])
        self.assertFalse(result["bridge_liveness_proven"])
        self.assertFalse(result["quote_freshness_proven"])
        self.assertEqual(
            set(result["current_bridge_identity_by_symbol"]),
            set(SYMBOLS),
        )
        self.assertTrue(all(tail.read_calls == 0 for tail in tails.values()))
        validate_phase8b_campaign_readiness(result)

    def test_ready_chain_reports_capture_segment_but_authorizes_nothing(self) -> None:
        registration = _registration()
        registration_sha = "c" * 64
        start_sha = "d" * 64
        identity = _identity_copy(registration)
        start = {
            **identity,
            "registration_sha256": registration_sha,
            "registration_fingerprint": registration["registration_fingerprint"],
            "bridge_session_id_by_symbol": dict(SESSIONS),
            "start_authorization_fingerprint": "e" * 64,
        }
        preflight = {
            **identity,
            "registration_sha256": registration_sha,
            "registration_fingerprint": registration["registration_fingerprint"],
            "start_authorization_sha256": start_sha,
            "start_authorization_fingerprint": start[
                "start_authorization_fingerprint"
            ],
            "bridge_session_id_by_symbol": dict(SESSIONS),
            "capture_preflight_fingerprint": "f" * 64,
        }
        spread = {
            "capture_preflight_fingerprint": preflight[
                "capture_preflight_fingerprint"
            ],
            "champion_set_fingerprint": registration[
                "champion_set_fingerprint"
            ],
            "required_symbols": list(SYMBOLS),
            "slippage_scenarios": [0.2, 0.5, 1.0],
        }
        with (
            patch(
                "fmp.phase8b.readiness.validate_phase8b_campaign_start_authorization"
            ),
            patch("fmp.phase8b.readiness.validate_phase8b_capture_preflight"),
            patch("fmp.phase8b.readiness.validate_phase8b_spread_reference"),
        ):
            result = build_phase8b_campaign_readiness(
                registration=registration,
                registration_sha256=registration_sha,
                start_authorization=start,
                start_authorization_sha256=start_sha,
                capture_preflight=preflight,
                spread_reference=spread,
                bridge_tails=_tails(),
                inspected_at_utc=NOW,
                campaign_terminal_present=False,
            )
        self.assertEqual(
            result["outcome"],
            Phase8BCampaignReadinessOutcome.READY.value,
        )
        self.assertEqual(result["next_action"], "capture-segment")
        self.assertTrue(result["capture_prerequisites_satisfied"])
        for field in (
            "live_shadow_segment_started",
            "acceptance_authorized",
            "promotion_authorized",
            "demo_order_authorized",
            "live_order_authorized",
            "broker_mutation_authorized",
            "real_money_authorized",
            "phase9_authorized",
        ):
            self.assertFalse(result[field])

    def test_session_replacement_is_connector_rejected(self) -> None:
        registration = _registration()
        tails = _tails()
        tails["GBPUSD"] = _Tail("GBPUSD", session="e" * 64)
        result = build_phase8b_campaign_readiness(
            registration=registration,
            registration_sha256="c" * 64,
            start_authorization=None,
            start_authorization_sha256=None,
            capture_preflight=None,
            spread_reference=None,
            bridge_tails=tails,
            inspected_at_utc=NOW,
            campaign_terminal_present=False,
        )
        self.assertEqual(
            result["outcome"],
            Phase8BCampaignReadinessOutcome.CONNECTOR_REJECTED.value,
        )
        self.assertIsNone(result["next_action"])
        self.assertIn("GBPUSD bridge session mismatch", result["failure_code"])

    def test_terminal_campaign_needs_no_bridge_and_cannot_capture(self) -> None:
        registration = _registration()
        result = build_phase8b_campaign_readiness(
            registration=registration,
            registration_sha256="c" * 64,
            start_authorization=None,
            start_authorization_sha256=None,
            capture_preflight=None,
            spread_reference=None,
            bridge_tails={},
            inspected_at_utc=NOW,
            campaign_terminal_present=True,
        )
        self.assertEqual(
            result["outcome"],
            Phase8BCampaignReadinessOutcome.TERMINAL.value,
        )
        self.assertEqual(result["next_action"], "none-terminal")
        self.assertFalse(result["capture_prerequisites_satisfied"])

    def test_cli_readiness_is_stdout_only_and_directory_unchanged(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            registration_path = root / "registration.json"
            registration_path.write_text(
                json.dumps(
                    registration,
                    sort_keys=True,
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            before = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }

            def discover(symbols):
                self.assertEqual(tuple(symbols), tuple(SYMBOLS))
                return {
                    symbol: root / f"{symbol}.unused"
                    for symbol in symbols
                }

            tails = _tails()

            def tail_factory(path, symbol):
                return tails[symbol]

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = phase8b_main(
                    ["readiness", "--campaign-dir", str(root)],
                    utc_now=lambda: NOW,
                    bridge_discoverer=discover,
                    tail_factory=tail_factory,
                )
            result = json.loads(stdout.getvalue())
            after = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }

        self.assertEqual(exit_code, 2)
        self.assertEqual(
            result["outcome"],
            Phase8BCampaignReadinessOutcome.NEEDS_START.value,
        )
        self.assertEqual(before, after)
        self.assertTrue(all(tail.read_calls == 0 for tail in tails.values()))


if __name__ == "__main__":
    unittest.main()
