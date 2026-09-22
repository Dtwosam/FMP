from __future__ import annotations

import hashlib
import inspect
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fmp.contracts import Direction, OrderIntent
from fmp.phase8b.design import MT5_BRIDGE_PROTOCOL, MT5_PROVIDER, MT5_TRANSPORT
from fmp.phase9.arming import build_phase9_demo_execution_arm
from fmp.phase9.design import (
    PHASE9_DEMO_DESIGN_FROZEN,
    PHASE9_DEMO_DESIGN_PROTOCOL,
    PHASE9_EXPERIMENT_ID,
    PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
)
import fmp.phase9.launch_preflight as launch_preflight
from fmp.phase9.launch_preflight import (
    PHASE9_DEMO_LAUNCH_PREFLIGHT_PROTOCOL,
    PHASE9_DEMO_LAUNCH_PREFLIGHT_READY,
    Phase9DemoLaunchPreflightBackend,
    run_phase9_demo_launch_preflight,
    validate_phase9_demo_launch_preflight,
    write_phase9_demo_launch_preflight,
)
from fmp.phase9.protocol import build_phase9_demo_order_request
from fmp.phase9.runtime_authority import build_phase9_demo_runtime_authority
from fmp.phase9.session import (
    build_phase9_demo_session_arm,
    build_phase9_demo_session_journal_event,
    build_phase9_demo_session_ready,
)
from fmp.risk import RiskConfig


UTC = timezone.utc
NOW = datetime(2026, 9, 22, 19, 0, tzinfo=UTC)
COMMIT = "c" * 40


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
        "champion_set_id": "phase9-dec063-test",
        "champion_set_fingerprint": "6" * 64,
        "strategy_fingerprints": ["1" * 64],
        "strategies": [{
            "fingerprint": "1" * 64,
            "identity_json": "{}",
            "family": "family-a",
            "symbol": "EURUSD",
            "timeframe": "5m",
            "code_commit": "a" * 40,
            "lifecycle": "SHADOW_VALIDATED",
        }],
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


def _inputs():
    design = _design()
    intent = OrderIntent(
        decision_id="decision-063",
        symbol="EURUSD",
        direction=Direction.LONG,
        units=10_000,
        reserved_risk_usd=100.0,
        stop_price=1.095,
        target_price=1.11,
        decision_timestamp_utc=NOW - timedelta(minutes=4),
        earliest_executable_timestamp_utc=NOW - timedelta(minutes=3),
    )
    request = build_phase9_demo_order_request(
        design=design,
        intent=intent,
        strategy_fingerprint="1" * 64,
        reference_entry_price=1.10,
    )
    session_arm = build_phase9_demo_session_arm(
        design=design,
        request=request,
        not_before_utc=NOW - timedelta(minutes=10),
        expires_at_utc=NOW + timedelta(hours=1),
        operator_approval_reference="approval-fixture-063",
    )
    session_ready = build_phase9_demo_session_ready(
        design=design,
        request=request,
        arm=session_arm,
        local_requests=[request],
        broker_orders=[],
        broker_positions=[],
        now_utc=NOW - timedelta(minutes=2),
        daily_halt_active=False,
    )
    execution_arm = build_phase9_demo_execution_arm(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        code_commit=COMMIT,
    )
    runtime_authority = build_phase9_demo_runtime_authority(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        journal_rows=[],
        now_utc=NOW - timedelta(minutes=1),
        daily_halt_active=False,
        code_commit=COMMIT,
    )
    return (
        design,
        request,
        session_arm,
        session_ready,
        execution_arm,
        runtime_authority,
    )


def _session_opened(session_arm, request):
    return build_phase9_demo_session_journal_event(
        arm=session_arm,
        request=request,
        sequence=1,
        event_time_utc=NOW - timedelta(seconds=30),
        event_type="SESSION_OPENED",
        payload={"practice_only": True},
        prior_event_fingerprint=None,
    )


class FakeBackend:
    def __init__(
        self,
        *,
        retcode: int = 0,
        broker_orders=None,
        broker_positions=None,
    ):
        self.retcode = retcode
        self.orders = [] if broker_orders is None else list(broker_orders)
        self.positions = (
            [] if broker_positions is None else list(broker_positions)
        )
        self.calls = []

    def account_snapshot(self):
        self.calls.append("account_snapshot")
        return {
            "account_mode": "DEMO",
            "account_fingerprint": "7" * 64,
            "server": "FPMarketsSC-Demo",
            "trade_allowed": True,
        }

    def symbol_snapshot(self, symbol):
        self.calls.append("symbol_snapshot")
        self.assert_symbol(symbol)
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

    def tick_snapshot(self, symbol):
        self.calls.append("tick_snapshot")
        self.assert_symbol(symbol)
        return {
            "symbol": "EURUSD",
            "source_time_utc": NOW.isoformat().replace("+00:00", "Z"),
            "bid": 1.0998,
            "ask": 1.1000,
        }

    def order_check(self, mt5_request):
        self.calls.append("order_check")
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

    def broker_orders(self):
        self.calls.append("broker_orders")
        return list(self.orders)

    def broker_positions(self):
        self.calls.append("broker_positions")
        return list(self.positions)

    @staticmethod
    def assert_symbol(symbol):
        if symbol != "EURUSD":
            raise AssertionError(f"unexpected symbol {symbol}")


class Phase9DemoLaunchPreflightTests(unittest.TestCase):
    def test_backend_protocol_exposes_no_mutation_method(self) -> None:
        names = set(Phase9DemoLaunchPreflightBackend.__dict__)
        for forbidden in (
            "order_send",
            "submit",
            "cancel_order",
            "modify_order",
            "close_position",
        ):
            self.assertNotIn(forbidden, names)

    def test_healthy_launch_preflight_performs_reads_and_check_only(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
        ) = _inputs()
        opened = _session_opened(session_arm, request)
        backend = FakeBackend()
        result = run_phase9_demo_launch_preflight(
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            execution_arm=execution_arm,
            runtime_authority=runtime_authority,
            journal_rows=[opened],
            backend=backend,
            now_utc=NOW,
            daily_halt_active=False,
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["protocol"],
            PHASE9_DEMO_LAUNCH_PREFLIGHT_PROTOCOL,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_DEMO_LAUNCH_PREFLIGHT_READY,
        )
        self.assertEqual(
            backend.calls,
            [
                "account_snapshot",
                "symbol_snapshot",
                "tick_snapshot",
                "order_check",
                "broker_orders",
                "broker_positions",
            ],
        )
        self.assertEqual(result["journal_event_count"], 1)
        self.assertEqual(
            result["journal_tip_fingerprint"],
            opened["event_fingerprint"],
        )
        self.assertTrue(result["broker_reads_performed"])
        self.assertTrue(result["order_check_performed"])
        self.assertFalse(result["order_send_attempted"])
        self.assertTrue(result["demo_launch_preflight_ready"])
        for field in (
            "demo_execution_source_armed",
            "demo_execution_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "phase10_authorized",
        ):
            self.assertFalse(result[field])
        validate_phase9_demo_launch_preflight(
            result,
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            execution_arm=execution_arm,
            runtime_authority=runtime_authority,
            journal_rows=[opened],
        )

    def test_halt_expiry_and_send_attempt_fail_before_broker_access(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
        ) = _inputs()
        backend = FakeBackend()
        common = {
            "design": design,
            "request": request,
            "session_arm": session_arm,
            "session_ready": session_ready,
            "execution_arm": execution_arm,
            "runtime_authority": runtime_authority,
            "backend": backend,
            "code_commit": COMMIT,
        }

        with self.assertRaisesRegex(ValueError, "daily halt"):
            run_phase9_demo_launch_preflight(
                **common,
                journal_rows=[],
                now_utc=NOW,
                daily_halt_active=True,
            )
        self.assertEqual(backend.calls, [])

        with self.assertRaisesRegex(ValueError, "outside arm window"):
            run_phase9_demo_launch_preflight(
                **common,
                journal_rows=[],
                now_utc=NOW + timedelta(hours=2),
                daily_halt_active=False,
            )
        self.assertEqual(backend.calls, [])

        attempt = build_phase9_demo_session_journal_event(
            arm=session_arm,
            request=request,
            sequence=1,
            event_time_utc=NOW - timedelta(seconds=10),
            event_type="SEND_ATTEMPTED",
            payload={"checked_mt5_request_sha256": "8" * 64},
            prior_event_fingerprint=None,
        )
        with self.assertRaisesRegex(ValueError, "zero SEND_ATTEMPTED"):
            run_phase9_demo_launch_preflight(
                **common,
                journal_rows=[attempt],
                now_utc=NOW,
                daily_halt_active=False,
            )
        self.assertEqual(backend.calls, [])

    def test_failed_order_check_stops_before_reconciliation_reads(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
        ) = _inputs()
        backend = FakeBackend(retcode=10027)
        with self.assertRaisesRegex(ValueError, "10027"):
            run_phase9_demo_launch_preflight(
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                runtime_authority=runtime_authority,
                journal_rows=[],
                backend=backend,
                now_utc=NOW,
                daily_halt_active=False,
                code_commit=COMMIT,
            )
        self.assertEqual(
            backend.calls,
            [
                "account_snapshot",
                "symbol_snapshot",
                "tick_snapshot",
                "order_check",
            ],
        )

    def test_unhealthy_reconciliation_fails_without_mutation(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
        ) = _inputs()
        backend = FakeBackend(
            broker_orders=[
                {
                    "broker_order_id": "unknown-order",
                    "client_order_id": "fmp9-unknown",
                    "protective_stop_id": "sl-unknown",
                }
            ]
        )
        with self.assertRaisesRegex(ValueError, "reconciliation is unhealthy"):
            run_phase9_demo_launch_preflight(
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                runtime_authority=runtime_authority,
                journal_rows=[],
                backend=backend,
                now_utc=NOW,
                daily_halt_active=False,
                code_commit=COMMIT,
            )
        self.assertEqual(backend.calls[-2:], ["broker_orders", "broker_positions"])

    def test_tampered_checked_state_copy_fails_even_if_refingerprinted(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
        ) = _inputs()
        result = run_phase9_demo_launch_preflight(
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            execution_arm=execution_arm,
            runtime_authority=runtime_authority,
            journal_rows=[],
            backend=FakeBackend(),
            now_utc=NOW,
            daily_halt_active=False,
            code_commit=COMMIT,
        )
        changed = dict(result)
        changed["account"] = dict(result["account"])
        changed["account"]["server"] = "Different-Demo"
        changed.pop("launch_preflight_fingerprint")
        changed["launch_preflight_fingerprint"] = _digest(changed)
        with self.assertRaisesRegex(ValueError, "account snapshot mismatch"):
            validate_phase9_demo_launch_preflight(
                changed,
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                runtime_authority=runtime_authority,
                journal_rows=[],
            )

    def test_writer_is_create_only_and_source_never_calls_order_send(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
        ) = _inputs()
        result = run_phase9_demo_launch_preflight(
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            execution_arm=execution_arm,
            runtime_authority=runtime_authority,
            journal_rows=[],
            backend=FakeBackend(),
            now_utc=NOW,
            daily_halt_active=False,
            code_commit=COMMIT,
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_phase9_demo_launch_preflight(
                result,
                out_dir=root,
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                runtime_authority=runtime_authority,
                journal_rows=[],
            )
            self.assertTrue((root / "launch-preflight.json").is_file())
            self.assertTrue((root / "manifest.json").is_file())
            self.assertFalse(manifest["order_send_attempted"])
            self.assertFalse(manifest["broker_mutation_authorized"])
            with self.assertRaises(FileExistsError):
                write_phase9_demo_launch_preflight(
                    result,
                    out_dir=root,
                    design=design,
                    request=request,
                    session_arm=session_arm,
                    session_ready=session_ready,
                    execution_arm=execution_arm,
                    runtime_authority=runtime_authority,
                    journal_rows=[],
                )

        source = inspect.getsource(launch_preflight)
        self.assertNotIn("backend.order_send(", source)
        self.assertNotIn("MetaTrader5PythonDemoBackend", source)


if __name__ == "__main__":
    unittest.main()
