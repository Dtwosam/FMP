from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fmp.contracts import Direction, OrderIntent
from fmp.phase8b.design import MT5_BRIDGE_PROTOCOL, MT5_PROVIDER, MT5_TRANSPORT
from fmp.phase9.arming import build_phase9_demo_execution_arm
from fmp.phase9.design import (
    PHASE9_DEMO_DESIGN_FROZEN,
    PHASE9_DEMO_DESIGN_PROTOCOL,
    PHASE9_EXPERIMENT_ID,
    PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
)
from fmp.phase9.launch_preflight import run_phase9_demo_launch_preflight
from fmp.phase9.permit import build_phase9_demo_execution_permit
from fmp.phase9.protocol import (
    DemoExecutionLockedError,
    build_phase9_demo_order_request,
)
from fmp.phase9.runner import (
    PHASE9_DEMO_ONE_SHOT_AMBIGUOUS,
    PHASE9_DEMO_ONE_SHOT_COMPLETED,
    PHASE9_DEMO_ONE_SHOT_NOT_COMPLETED,
    run_phase9_demo_one_shot,
    validate_phase9_demo_one_shot_run,
)
from fmp.phase9.runtime_authority import build_phase9_demo_runtime_authority
from fmp.phase9.session import (
    Phase9DemoSessionJournal,
    build_phase9_demo_session_arm,
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
        "champion_set_id": "phase9-dec065-test",
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


class LaunchBackend:
    def __init__(self):
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
        return {
            "symbol": symbol,
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
        return {
            "symbol": symbol,
            "source_time_utc": NOW.isoformat().replace("+00:00", "Z"),
            "bid": 1.0998,
            "ask": 1.1000,
        }

    def order_check(self, mt5_request):
        self.calls.append("order_check")
        return {
            "retcode": 0,
            "comment": "Done",
            "balance": 100000.0,
            "equity": 100000.0,
            "profit": 0.0,
            "margin": 100.0,
            "margin_free": 99900.0,
            "margin_level": 1000.0,
        }

    def broker_orders(self):
        self.calls.append("broker_orders")
        return []

    def broker_positions(self):
        self.calls.append("broker_positions")
        return []


def _chain():
    design = _design()
    intent = OrderIntent(
        decision_id="decision-065",
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
        not_before_utc=NOW - timedelta(minutes=15),
        expires_at_utc=NOW + timedelta(minutes=45),
        operator_approval_reference="approval-fixture-065",
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
    launch = run_phase9_demo_launch_preflight(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        journal_rows=[],
        backend=LaunchBackend(),
        now_utc=NOW,
        daily_halt_active=False,
        code_commit=COMMIT,
    )
    permit = build_phase9_demo_execution_permit(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        launch_preflight=launch,
        journal_rows=[],
        code_commit=COMMIT,
    )
    return (
        design,
        request,
        session_arm,
        session_ready,
        execution_arm,
        runtime_authority,
        launch,
        permit,
    )


class SendBackend:
    def __init__(
        self,
        *,
        retcode: int = 10009,
        volume: float = 0.1,
        send_error: Exception | None = None,
    ):
        self.retcode = retcode
        self.volume = volume
        self.send_error = send_error
        self.calls = []
        self.sent = []

    def order_send(self, mt5_request):
        self.calls.append("order_send")
        self.sent.append(dict(mt5_request))
        if self.send_error is not None:
            raise self.send_error
        return {
            "retcode": self.retcode,
            "retcode_external": 0,
            "deal": 101 if self.retcode == 10009 else 0,
            "order": 202 if self.retcode == 10009 else 0,
            "volume": self.volume,
            "price": 1.1000 if self.retcode == 10009 else 0.0,
            "bid": 1.0998,
            "ask": 1.1000,
            "comment": "Done" if self.retcode == 10009 else "Rejected",
            "request_id": 303,
        }

    def broker_orders(self):
        self.calls.append("broker_orders")
        return []

    def broker_positions(self):
        self.calls.append("broker_positions")
        if self.retcode == 10009 and self.send_error is None:
            return [{
                "broker_position_id": "202",
                "client_order_id": self._client_order_id,
                "protective_stop_id": "sl:202:1.095",
            }]
        return []

    @property
    def _client_order_id(self):
        if not self.sent:
            return ""
        return str(self.sent[0]["comment"])


class Phase9OneShotRunnerTests(unittest.TestCase):
    def _run(self, backend, journal, *, now=NOW + timedelta(seconds=1)):
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch,
            permit,
        ) = _chain()
        return run_phase9_demo_one_shot(
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            execution_arm=execution_arm,
            runtime_authority=runtime_authority,
            launch_preflight=launch,
            execution_permit=permit,
            journal=journal,
            backend=backend,
            now_utc=now,
            daily_halt_active=False,
        ), launch

    def test_source_gate_blocks_before_journal_or_backend_access(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch,
            permit,
        ) = _chain()
        backend = SendBackend()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.jsonl"
            with Phase9DemoSessionJournal(
                path=path,
                arm=session_arm,
                request=request,
            ) as journal:
                with self.assertRaises(DemoExecutionLockedError):
                    run_phase9_demo_one_shot(
                        design=design,
                        request=request,
                        session_arm=session_arm,
                        session_ready=session_ready,
                        execution_arm=execution_arm,
                        runtime_authority=runtime_authority,
                        launch_preflight=launch,
                        execution_permit=permit,
                        journal=journal,
                        backend=backend,
                        now_utc=NOW + timedelta(seconds=1),
                        daily_halt_active=False,
                    )
                self.assertEqual(journal.rows, ())
            self.assertEqual(path.read_bytes(), b"")
        self.assertEqual(backend.calls, [])

    def test_simulated_completed_send_is_exactly_once_and_reconciled(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch,
            permit,
        ) = _chain()
        backend = SendBackend()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.jsonl"
            with Phase9DemoSessionJournal(
                path=path,
                arm=session_arm,
                request=request,
            ) as journal:
                with (
                    patch("fmp.phase9.runner.DEMO_EXECUTION_SOURCE_ARMED", True),
                    patch("fmp.phase9.session.os.fsync") as fsync,
                ):
                    result = run_phase9_demo_one_shot(
                        design=design,
                        request=request,
                        session_arm=session_arm,
                        session_ready=session_ready,
                        execution_arm=execution_arm,
                        runtime_authority=runtime_authority,
                        launch_preflight=launch,
                        execution_permit=permit,
                        journal=journal,
                        backend=backend,
                        now_utc=NOW + timedelta(seconds=1),
                        daily_halt_active=False,
                    )
                rows = journal.rows
            self.assertEqual(fsync.call_count, 3)

        self.assertEqual(result["outcome"], PHASE9_DEMO_ONE_SHOT_COMPLETED)
        validate_phase9_demo_one_shot_run(result)
        self.assertEqual(
            backend.calls,
            ["order_send", "broker_orders", "broker_positions"],
        )
        self.assertEqual(
            backend.sent,
            [launch["order_check_request"]["mt5_request"]],
        )
        self.assertEqual(
            [row["event_type"] for row in rows],
            [
                "SEND_ATTEMPTED",
                "SEND_RESULT",
                "POST_SEND_RECONCILIATION_OK",
            ],
        )
        self.assertEqual(result["send_attempt_count"], 1)
        self.assertTrue(result["arm_spent"])

    def test_returned_rejection_is_terminal_not_completed(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch,
            permit,
        ) = _chain()
        backend = SendBackend(retcode=10021, volume=0.0)
        with TemporaryDirectory() as tmp:
            with Phase9DemoSessionJournal(
                path=Path(tmp) / "session.jsonl",
                arm=session_arm,
                request=request,
            ) as journal:
                with patch(
                    "fmp.phase9.runner.DEMO_EXECUTION_SOURCE_ARMED",
                    True,
                ):
                    result = run_phase9_demo_one_shot(
                        design=design,
                        request=request,
                        session_arm=session_arm,
                        session_ready=session_ready,
                        execution_arm=execution_arm,
                        runtime_authority=runtime_authority,
                        launch_preflight=launch,
                        execution_permit=permit,
                        journal=journal,
                        backend=backend,
                        now_utc=NOW + timedelta(seconds=1),
                        daily_halt_active=False,
                    )
        self.assertEqual(
            result["outcome"],
            PHASE9_DEMO_ONE_SHOT_NOT_COMPLETED,
        )
        self.assertEqual(backend.calls.count("order_send"), 1)

    def test_send_exception_is_ambiguous_and_never_retried(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch,
            permit,
        ) = _chain()
        backend = SendBackend(send_error=RuntimeError("transport lost"))
        with TemporaryDirectory() as tmp:
            with Phase9DemoSessionJournal(
                path=Path(tmp) / "session.jsonl",
                arm=session_arm,
                request=request,
            ) as journal:
                with patch(
                    "fmp.phase9.runner.DEMO_EXECUTION_SOURCE_ARMED",
                    True,
                ):
                    result = run_phase9_demo_one_shot(
                        design=design,
                        request=request,
                        session_arm=session_arm,
                        session_ready=session_ready,
                        execution_arm=execution_arm,
                        runtime_authority=runtime_authority,
                        launch_preflight=launch,
                        execution_permit=permit,
                        journal=journal,
                        backend=backend,
                        now_utc=NOW + timedelta(seconds=1),
                        daily_halt_active=False,
                    )
                rows = journal.rows

        self.assertEqual(result["outcome"], PHASE9_DEMO_ONE_SHOT_AMBIGUOUS)
        self.assertEqual(backend.calls.count("order_send"), 1)
        self.assertEqual(
            [row["event_type"] for row in rows],
            [
                "SEND_ATTEMPTED",
                "SESSION_HALTED",
                "POST_SEND_RECONCILIATION_OK",
            ],
        )

    def test_checked_request_tamper_fails_before_journal_or_backend(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch,
            permit,
        ) = _chain()
        changed_launch = dict(launch)
        changed_launch["order_check_request"] = dict(
            launch["order_check_request"]
        )
        changed_launch["order_check_request"]["mt5_request"] = dict(
            launch["order_check_request"]["mt5_request"]
        )
        changed_launch["order_check_request"]["mt5_request"]["volume"] = 0.2
        backend = SendBackend()
        with TemporaryDirectory() as tmp:
            with Phase9DemoSessionJournal(
                path=Path(tmp) / "session.jsonl",
                arm=session_arm,
                request=request,
            ) as journal:
                with (
                    patch(
                        "fmp.phase9.runner.validate_phase9_demo_execution_permit"
                    ),
                    patch(
                        "fmp.phase9.runner.DEMO_EXECUTION_SOURCE_ARMED",
                        True,
                    ),
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        "checked MT5 request changed",
                    ):
                        run_phase9_demo_one_shot(
                            design=design,
                            request=request,
                            session_arm=session_arm,
                            session_ready=session_ready,
                            execution_arm=execution_arm,
                            runtime_authority=runtime_authority,
                            launch_preflight=changed_launch,
                            execution_permit=permit,
                            journal=journal,
                            backend=backend,
                            now_utc=NOW + timedelta(seconds=1),
                            daily_halt_active=False,
                        )
                    self.assertEqual(journal.rows, ())
        self.assertEqual(backend.calls, [])


if __name__ == "__main__":
    unittest.main()
