from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

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
from fmp.phase9.mt5_mutation import GatedMT5DemoMutationAdapter
from fmp.phase9.protocol import (
    DemoExecutionLockedError,
    build_phase9_demo_order_request,
)
from fmp.phase9.session import (
    BoundedDemoSessionController,
    PHASE9_DEMO_SESSION_ARM_PROTOCOL,
    PHASE9_DEMO_SESSION_CONTRACT_READY,
    PHASE9_DEMO_SESSION_JOURNAL_PROTOCOL,
    Phase9DemoSessionJournal,
    build_phase9_demo_session_arm,
    build_phase9_demo_session_ready,
    build_phase9_send_attempt_payload,
    phase9_demo_session_attempt_count,
    validate_phase9_demo_session_arm,
    validate_phase9_demo_session_journal,
    validate_phase9_demo_session_ready,
)
from fmp.risk import RiskConfig


UTC = timezone.utc
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
        "champion_set_id": "phase9-dec059-test",
        "champion_set_fingerprint": "6" * 64,
        "strategy_fingerprints": ["1" * 64],
        "strategies": [
            {
                "fingerprint": "1" * 64,
                "identity_json": "{}",
                "family": "family-a",
                "symbol": "EURUSD",
                "timeframe": "5m",
                "code_commit": "a" * 40,
                "lifecycle": "SHADOW_VALIDATED",
            }
        ],
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


def _request():
    design = _design()
    intent = OrderIntent(
        decision_id="decision-059",
        symbol="EURUSD",
        direction=Direction.LONG,
        units=10_000,
        reserved_risk_usd=100.0,
        stop_price=1.095,
        target_price=1.11,
        decision_timestamp_utc=NOW - timedelta(minutes=2),
        earliest_executable_timestamp_utc=NOW - timedelta(minutes=1),
    )
    request = build_phase9_demo_order_request(
        design=design,
        intent=intent,
        strategy_fingerprint="1" * 64,
        reference_entry_price=1.10,
    )
    return design, request


def _arm():
    design, request = _request()
    arm = build_phase9_demo_session_arm(
        design=design,
        request=request,
        not_before_utc=NOW - timedelta(minutes=5),
        expires_at_utc=NOW + timedelta(hours=2),
        operator_approval_reference="approval-fixture-059",
    )
    return design, request, arm


class CountingBackend:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def method(*args, **kwargs):
            self.calls.append(name)
            raise AssertionError(f"backend must stay untouched: {name}")

        return method


class Phase9BoundedDemoSessionTests(unittest.TestCase):
    def test_arm_is_one_request_one_order_and_deterministic(self) -> None:
        design, request = _request()
        kwargs = {
            "design": design,
            "request": request,
            "not_before_utc": NOW - timedelta(minutes=5),
            "expires_at_utc": NOW + timedelta(hours=2),
            "operator_approval_reference": "approval-fixture-059",
        }
        first = build_phase9_demo_session_arm(**kwargs)
        second = build_phase9_demo_session_arm(**kwargs)
        self.assertEqual(first, second)
        self.assertEqual(first["protocol"], PHASE9_DEMO_SESSION_ARM_PROTOCOL)
        self.assertEqual(first["request_fingerprint"], request["request_fingerprint"])
        self.assertEqual(first["max_new_orders"], 1)
        self.assertTrue(first["practice_only"])
        self.assertFalse(first["demo_execution_source_armed"])
        self.assertFalse(first["demo_order_authorized"])
        validate_phase9_demo_session_arm(
            first,
            design=design,
            request=request,
        )

    def test_arm_cannot_cross_utc_risk_day(self) -> None:
        design, request = _request()
        with self.assertRaisesRegex(ValueError, "one UTC date"):
            build_phase9_demo_session_arm(
                design=design,
                request=request,
                not_before_utc=datetime(
                    2026, 9, 22, 23, 50, tzinfo=UTC
                ),
                expires_at_utc=datetime(
                    2026, 9, 23, 0, 10, tzinfo=UTC
                ),
                operator_approval_reference="approval-fixture-059",
            )

    def test_session_ready_requires_healthy_reconciliation_and_unused_arm(self) -> None:
        design, request, arm = _arm()
        ready = build_phase9_demo_session_ready(
            design=design,
            request=request,
            arm=arm,
            local_requests=[request],
            broker_orders=[],
            broker_positions=[],
            now_utc=NOW,
            daily_halt_active=False,
        )
        self.assertEqual(
            ready["outcome"],
            PHASE9_DEMO_SESSION_CONTRACT_READY,
        )
        self.assertEqual(ready["max_new_orders"], 1)
        self.assertFalse(ready["demo_execution_source_armed"])
        validate_phase9_demo_session_ready(ready)

        with self.assertRaisesRegex(ValueError, "daily halt"):
            build_phase9_demo_session_ready(
                design=design,
                request=request,
                arm=arm,
                local_requests=[request],
                broker_orders=[],
                broker_positions=[],
                now_utc=NOW,
                daily_halt_active=True,
            )
        with self.assertRaisesRegex(ValueError, "already spent"):
            build_phase9_demo_session_ready(
                design=design,
                request=request,
                arm=arm,
                local_requests=[request],
                broker_orders=[],
                broker_positions=[],
                now_utc=NOW,
                daily_halt_active=False,
                new_order_attempt_count=1,
            )
        with self.assertRaisesRegex(ValueError, "outside arm window"):
            build_phase9_demo_session_ready(
                design=design,
                request=request,
                arm=arm,
                local_requests=[request],
                broker_orders=[],
                broker_positions=[],
                now_utc=NOW + timedelta(hours=3),
                daily_halt_active=False,
            )
        with self.assertRaisesRegex(ValueError, "unhealthy"):
            build_phase9_demo_session_ready(
                design=design,
                request=request,
                arm=arm,
                local_requests=[request],
                broker_orders=[
                    {
                        "broker_order_id": "unknown-1",
                        "client_order_id": "fmp9-unknown",
                        "protective_stop_id": "sl-1",
                    }
                ],
                broker_positions=[],
                now_utc=NOW,
                daily_halt_active=False,
            )

    def test_journal_is_create_only_fsynced_hash_chained_and_spends_arm(self) -> None:
        _design_value, request, arm = _arm()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.jsonl"
            with patch("fmp.phase9.session.os.fsync") as fsync:
                with Phase9DemoSessionJournal(
                    path=path,
                    arm=arm,
                    request=request,
                ) as journal:
                    journal.append(
                        event_time_utc=NOW,
                        event_type="SESSION_OPENED",
                        payload={"practice_only": True},
                    )
                    journal.append(
                        event_time_utc=NOW + timedelta(seconds=1),
                        event_type="RECONCILIATION_OK",
                        payload={"healthy": True},
                    )
                    attempt_payload = build_phase9_send_attempt_payload(
                        order_check_request_fingerprint="8" * 64,
                        order_check_fingerprint="9" * 64,
                        checked_mt5_request={
                            "action": "TRADE_ACTION_DEAL",
                            "symbol": "EURUSD",
                            "volume": 0.1,
                        },
                    )
                    journal.append(
                        event_time_utc=NOW + timedelta(seconds=2),
                        event_type="SEND_ATTEMPTED",
                        payload=attempt_payload,
                    )
                    rows = journal.rows
                self.assertEqual(fsync.call_count, 3)

            self.assertTrue(path.is_file())
            self.assertEqual(len(path.read_text().splitlines()), 3)
            validate_phase9_demo_session_journal(rows)
            self.assertEqual(phase9_demo_session_attempt_count(rows), 1)
            self.assertEqual(
                rows[1]["prior_event_fingerprint"],
                rows[0]["event_fingerprint"],
            )
            self.assertEqual(
                rows[2]["prior_event_fingerprint"],
                rows[1]["event_fingerprint"],
            )

            with self.assertRaises(FileExistsError):
                Phase9DemoSessionJournal(
                    path=path,
                    arm=arm,
                    request=request,
                )

    def test_journal_tamper_breaks_replay_even_if_row_is_refingerprinted(self) -> None:
        _design_value, request, arm = _arm()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.jsonl"
            with Phase9DemoSessionJournal(
                path=path,
                arm=arm,
                request=request,
            ) as journal:
                journal.append(
                    event_time_utc=NOW,
                    event_type="SESSION_OPENED",
                    payload={"practice_only": True},
                )
                journal.append(
                    event_time_utc=NOW + timedelta(seconds=1),
                    event_type="RECONCILIATION_OK",
                    payload={"healthy": True},
                )
                rows = [dict(row) for row in journal.rows]

            rows[0]["payload"] = {"practice_only": False}
            payload = dict(rows[0])
            payload.pop("event_fingerprint")
            rows[0]["event_fingerprint"] = _digest(payload)
            with self.assertRaisesRegex(ValueError, "hash chain"):
                validate_phase9_demo_session_journal(rows)

    def test_controller_still_hits_dec058_lock_before_backend_access(self) -> None:
        design, request, arm = _arm()
        backend = CountingBackend()
        adapter = GatedMT5DemoMutationAdapter(
            design=design,
            backend=backend,
        )
        controller = BoundedDemoSessionController(
            design=design,
            request=request,
            arm=arm,
            adapter=adapter,
        )
        with self.assertRaises(DemoExecutionLockedError):
            controller.submit()
        self.assertEqual(backend.calls, [])


if __name__ == "__main__":
    unittest.main()
