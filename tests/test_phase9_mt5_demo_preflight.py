from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fmp.contracts import Direction, OrderIntent
from fmp.phase8b.design import (
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
)
from fmp.phase9.design import (
    PHASE9_DEMO_DESIGN_FROZEN,
    PHASE9_DEMO_DESIGN_PROTOCOL,
    PHASE9_EXPERIMENT_ID,
    PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
)
from fmp.phase9.mt5_preflight import (
    MT5DemoCheckBackend,
    PHASE9_MT5_DEMO_PREFLIGHT_READY,
    PHASE9_MT5_ORDER_CHECK_REQUEST_PROTOCOL,
    build_phase9_mt5_order_check_request,
    run_phase9_mt5_demo_preflight,
    validate_phase9_mt5_demo_preflight,
    write_phase9_mt5_demo_preflight,
)
from fmp.phase9.protocol import build_phase9_demo_order_request
from fmp.risk import RiskConfig


UTC = timezone.utc
COMMIT = "c" * 40
NOW = datetime(2026, 9, 22, 18, 0, tzinfo=UTC)


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


def _design():
    rows = [
        {
            "fingerprint": "1" * 64,
            "identity_json": "{}",
            "family": "family-a",
            "symbol": "EURUSD",
            "timeframe": "5m",
            "code_commit": "a" * 40,
            "lifecycle": "SHADOW_VALIDATED",
        }
    ]
    payload = {
        "protocol": PHASE9_DEMO_DESIGN_PROTOCOL,
        "experiment_id": PHASE9_EXPERIMENT_ID,
        "decision": "DEC-055",
        "outcome": PHASE9_DEMO_DESIGN_FROZEN,
        "demo_design_code_commit": "d" * 40,
        "phase8b_review_id": "2" * 64,
        "phase8b_acceptance_fingerprint": "3" * 64,
        "phase8b_shadow_validation_fingerprint": "4" * 64,
        "capture_preflight_fingerprint": "5" * 64,
        "champion_set_id": "phase9-dec057-test",
        "champion_set_fingerprint": "6" * 64,
        "strategy_fingerprints": ["1" * 64],
        "strategies": rows,
        "execution_path": {
            "provider": MT5_PROVIDER,
            "accepted_quote_transport": MT5_TRANSPORT,
            "accepted_quote_protocol": MT5_BRIDGE_PROTOCOL,
            "future_order_bridge_protocol": PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
            "account_mode": "DEMO",
            "account_fingerprint": "7" * 64,
            "server": "FPMarketsSC-Demo",
            "required_symbols": ["EURUSD"],
            "symbol_mapping": {"EURUSD": "EURUSD"},
            "auto_trading_change_authorized": False,
            "provider_change_authorized": False,
        },
        "risk_config": RiskConfig().to_config(),
        "required_controls": {
            "practice_account_assertion_before_order_session": True,
            "mandatory_protective_stop": True,
            "unprotected_position_healthy_state_allowed": False,
            "deterministic_client_order_ids": True,
            "duplicate_client_order_prevention": True,
            "requested_vs_fill_price_logging": True,
            "order_validation_journal": True,
            "order_ack_fill_rejection_journal": True,
            "startup_position_order_reconciliation": True,
            "orphan_unknown_position_fail_closed": True,
            "restart_recovery_required": True,
            "daily_halt_required": True,
            "secrets_in_git_allowed": False,
            "secrets_in_evidence_artifacts_allowed": False,
        },
        "demo_adapter_source_authorized": True,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    return payload | {"demo_design_fingerprint": _digest(payload)}


def _request(*, units: int = 10_000, stop: float = 1.095):
    design = _design()
    intent = OrderIntent(
        decision_id="decision-057",
        symbol="EURUSD",
        direction=Direction.LONG,
        units=units,
        reserved_risk_usd=100.0,
        stop_price=stop,
        target_price=1.11,
        decision_timestamp_utc=NOW,
        earliest_executable_timestamp_utc=NOW + timedelta(minutes=1),
    )
    return design, build_phase9_demo_order_request(
        design=design,
        intent=intent,
        strategy_fingerprint="1" * 64,
        reference_entry_price=1.10,
    )


def _account():
    return {
        "account_mode": "DEMO",
        "account_fingerprint": "7" * 64,
        "server": "FPMarketsSC-Demo",
        "trade_allowed": True,
    }


def _symbol():
    return {
        "symbol": "EURUSD",
        "trade_contract_size": 100_000.0,
        "volume_min": 0.01,
        "volume_step": 0.01,
        "volume_max": 100.0,
        "digits": 5,
        "point": 0.00001,
        "trade_stops_level_points": 20,
        "filling_mode": "RETURN",
        "trade_enabled": True,
    }


def _tick():
    return {
        "symbol": "EURUSD",
        "source_time_utc": NOW.isoformat().replace("+00:00", "Z"),
        "bid": 1.0998,
        "ask": 1.1000,
    }


class FakeBackend:
    def __init__(self, *, retcode: int = 0):
        self.retcode = retcode
        self.checked = []

    def account_snapshot(self):
        return _account()

    def symbol_snapshot(self, symbol):
        assert symbol == "EURUSD"
        return _symbol()

    def tick_snapshot(self, symbol):
        assert symbol == "EURUSD"
        return _tick()

    def order_check(self, mt5_request):
        self.checked.append(dict(mt5_request))
        return {
            "retcode": self.retcode,
            "comment": "Done" if self.retcode == 0 else "Rejected",
            "balance": 100000.0,
            "equity": 100000.0,
            "profit": 0.0,
            "margin": 100.0,
            "margin_free": 99900.0,
            "margin_level": 1000.0,
        }


class Phase9MT5DemoPreflightTests(unittest.TestCase):
    def test_backend_protocol_has_no_mutation_surface(self) -> None:
        names = set(MT5DemoCheckBackend.__dict__)
        for forbidden in (
            "order_send",
            "submit",
            "cancel_order",
            "modify_order",
            "close_position",
        ):
            self.assertNotIn(forbidden, names)

    def test_builds_exact_check_request_without_resizing(self) -> None:
        design, request = _request()
        result = build_phase9_mt5_order_check_request(
            design=design,
            request=request,
            account_snapshot=_account(),
            symbol_snapshot=_symbol(),
            tick_snapshot=_tick(),
        )
        self.assertEqual(
            result["protocol"],
            PHASE9_MT5_ORDER_CHECK_REQUEST_PROTOCOL,
        )
        self.assertEqual(result["volume_lots"], 0.1)
        self.assertEqual(result["side"], "BUY")
        self.assertEqual(result["mt5_request"]["price"], 1.1)
        self.assertEqual(result["mt5_request"]["sl"], 1.095)
        self.assertEqual(result["mt5_request"]["tp"], 1.11)
        self.assertEqual(
            result["mt5_request"]["type_filling"],
            "ORDER_FILLING_RETURN",
        )
        self.assertEqual(result["mt5_request"]["deviation"], 0)
        self.assertFalse(result["order_send_attempted"])

    def test_nonrepresentable_units_fail_closed(self) -> None:
        design, request = _request(units=10_500)
        with self.assertRaisesRegex(ValueError, "exactly representable"):
            build_phase9_mt5_order_check_request(
                design=design,
                request=request,
                account_snapshot=_account(),
                symbol_snapshot=_symbol(),
                tick_snapshot=_tick(),
            )

    def test_stop_distance_and_account_identity_fail_closed(self) -> None:
        design, request = _request(stop=1.0999)
        with self.assertRaisesRegex(ValueError, "minimum stop distance"):
            build_phase9_mt5_order_check_request(
                design=design,
                request=request,
                account_snapshot=_account(),
                symbol_snapshot=_symbol(),
                tick_snapshot=_tick(),
            )

        design, request = _request()
        account = _account()
        account["account_fingerprint"] = "8" * 64
        with self.assertRaisesRegex(ValueError, "account fingerprint"):
            build_phase9_mt5_order_check_request(
                design=design,
                request=request,
                account_snapshot=account,
                symbol_snapshot=_symbol(),
                tick_snapshot=_tick(),
            )

    def test_successful_preflight_is_non_mutating_and_create_only(self) -> None:
        design, request = _request()
        backend = FakeBackend()
        result = run_phase9_mt5_demo_preflight(
            design=design,
            request=request,
            backend=backend,
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_MT5_DEMO_PREFLIGHT_READY,
        )
        self.assertEqual(len(backend.checked), 1)
        self.assertTrue(result["check_passed"])
        self.assertTrue(result["mt5_demo_preflight_source_ready"])
        for field in (
            "demo_execution_authorized",
            "demo_order_authorized",
            "live_order_authorized",
            "broker_mutation_authorized",
            "real_money_authorized",
            "phase10_authorized",
        ):
            self.assertFalse(result[field])
        validate_phase9_mt5_demo_preflight(result)

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_phase9_mt5_demo_preflight(result, root)
            self.assertTrue((root / "preflight.json").is_file())
            self.assertTrue((root / "manifest.json").is_file())
            with self.assertRaises(FileExistsError):
                write_phase9_mt5_demo_preflight(result, root)

    def test_failed_order_check_does_not_create_ready_preflight(self) -> None:
        design, request = _request()
        backend = FakeBackend(retcode=10027)
        with self.assertRaisesRegex(ValueError, "10027"):
            run_phase9_mt5_demo_preflight(
                design=design,
                request=request,
                backend=backend,
                code_commit=COMMIT,
            )
        self.assertEqual(len(backend.checked), 1)


if __name__ == "__main__":
    unittest.main()
