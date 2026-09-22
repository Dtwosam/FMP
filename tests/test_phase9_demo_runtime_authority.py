from __future__ import annotations

import hashlib
import inspect
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
from fmp.phase9.protocol import build_phase9_demo_order_request
import fmp.phase9.runtime_authority as runtime_authority
from fmp.phase9.runtime_authority import (
    PHASE9_DEMO_RUNTIME_AUTHORITY_PROTOCOL,
    PHASE9_DEMO_RUNTIME_AUTHORITY_READY,
    build_phase9_demo_runtime_authority,
    validate_phase9_demo_runtime_authority,
    write_phase9_demo_runtime_authority,
)
from fmp.phase9.session import (
    build_phase9_demo_session_arm,
    build_phase9_demo_session_journal_event,
    build_phase9_demo_session_ready,
)
from fmp.risk import RiskConfig


UTC = timezone.utc
NOW = datetime(2026, 9, 22, 18, 30, tzinfo=UTC)
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
        "champion_set_id": "phase9-dec062-test",
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
        decision_id="decision-062",
        symbol="EURUSD",
        direction=Direction.LONG,
        units=10_000,
        reserved_risk_usd=100.0,
        stop_price=1.095,
        target_price=1.11,
        decision_timestamp_utc=NOW - timedelta(minutes=3),
        earliest_executable_timestamp_utc=NOW - timedelta(minutes=2),
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
        operator_approval_reference="approval-fixture-062",
    )
    session_ready = build_phase9_demo_session_ready(
        design=design,
        request=request,
        arm=session_arm,
        local_requests=[request],
        broker_orders=[],
        broker_positions=[],
        now_utc=NOW - timedelta(minutes=1),
        daily_halt_active=False,
    )
    execution_arm = build_phase9_demo_execution_arm(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        code_commit=COMMIT,
    )
    return design, request, session_arm, session_ready, execution_arm


class Phase9DemoRuntimeAuthorityTests(unittest.TestCase):
    def test_runtime_authority_binds_exact_chain_and_authorizes_nothing(self) -> None:
        design, request, session_arm, session_ready, execution_arm = _inputs()
        result = build_phase9_demo_runtime_authority(
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            execution_arm=execution_arm,
            journal_rows=[],
            now_utc=NOW,
            daily_halt_active=False,
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["protocol"],
            PHASE9_DEMO_RUNTIME_AUTHORITY_PROTOCOL,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_DEMO_RUNTIME_AUTHORITY_READY,
        )
        self.assertEqual(
            result["execution_arm_fingerprint"],
            execution_arm["execution_arm_fingerprint"],
        )
        self.assertEqual(result["journal_event_count"], 0)
        self.assertIsNone(result["journal_tip_fingerprint"])
        self.assertEqual(result["send_attempt_count"], 0)
        self.assertTrue(result["demo_runtime_arm_authority_ready"])
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
        validate_phase9_demo_runtime_authority(
            result,
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            execution_arm=execution_arm,
            journal_rows=[],
        )

    def test_nonempty_unspent_journal_binds_tip(self) -> None:
        design, request, session_arm, session_ready, execution_arm = _inputs()
        row = build_phase9_demo_session_journal_event(
            arm=session_arm,
            request=request,
            sequence=1,
            event_time_utc=NOW - timedelta(seconds=10),
            event_type="SESSION_OPENED",
            payload={"practice_only": True},
            prior_event_fingerprint=None,
        )
        result = build_phase9_demo_runtime_authority(
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            execution_arm=execution_arm,
            journal_rows=[row],
            now_utc=NOW,
            daily_halt_active=False,
            code_commit=COMMIT,
        )
        self.assertEqual(result["journal_event_count"], 1)
        self.assertEqual(
            result["journal_tip_fingerprint"],
            row["event_fingerprint"],
        )

    def test_prior_send_attempt_and_daily_halt_fail_closed(self) -> None:
        design, request, session_arm, session_ready, execution_arm = _inputs()
        attempt = build_phase9_demo_session_journal_event(
            arm=session_arm,
            request=request,
            sequence=1,
            event_time_utc=NOW - timedelta(seconds=5),
            event_type="SEND_ATTEMPTED",
            payload={"checked_mt5_request_sha256": "8" * 64},
            prior_event_fingerprint=None,
        )
        with self.assertRaisesRegex(ValueError, "zero prior SEND_ATTEMPTED"):
            build_phase9_demo_runtime_authority(
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                journal_rows=[attempt],
                now_utc=NOW,
                daily_halt_active=False,
                code_commit=COMMIT,
            )
        with self.assertRaisesRegex(ValueError, "daily halt"):
            build_phase9_demo_runtime_authority(
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                journal_rows=[],
                now_utc=NOW,
                daily_halt_active=True,
                code_commit=COMMIT,
            )

    def test_expired_or_pre_readiness_time_fails_closed(self) -> None:
        design, request, session_arm, session_ready, execution_arm = _inputs()
        with self.assertRaisesRegex(ValueError, "outside arm window"):
            build_phase9_demo_runtime_authority(
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                journal_rows=[],
                now_utc=NOW + timedelta(hours=2),
                daily_halt_active=False,
                code_commit=COMMIT,
            )
        with self.assertRaisesRegex(ValueError, "precedes session readiness"):
            build_phase9_demo_runtime_authority(
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                journal_rows=[],
                now_utc=NOW - timedelta(minutes=2),
                daily_halt_active=False,
                code_commit=COMMIT,
            )

    def test_already_armed_source_fails_before_runtime_authority(self) -> None:
        design, request, session_arm, session_ready, execution_arm = _inputs()
        with patch(
            "fmp.phase9.runtime_authority.DEMO_EXECUTION_SOURCE_ARMED",
            True,
        ):
            with self.assertRaisesRegex(ValueError, "source unarmed"):
                build_phase9_demo_runtime_authority(
                    design=design,
                    request=request,
                    session_arm=session_arm,
                    session_ready=session_ready,
                    execution_arm=execution_arm,
                    journal_rows=[],
                    now_utc=NOW,
                    daily_halt_active=False,
                    code_commit=COMMIT,
                )

    def test_writer_is_create_only_and_source_has_no_broker_dependency(self) -> None:
        design, request, session_arm, session_ready, execution_arm = _inputs()
        result = build_phase9_demo_runtime_authority(
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            execution_arm=execution_arm,
            journal_rows=[],
            now_utc=NOW,
            daily_halt_active=False,
            code_commit=COMMIT,
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_phase9_demo_runtime_authority(
                result,
                out_dir=root,
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                journal_rows=[],
            )
            self.assertTrue((root / "runtime-authority.json").is_file())
            self.assertTrue((root / "manifest.json").is_file())
            self.assertFalse(manifest["demo_execution_source_armed"])
            self.assertFalse(manifest["broker_mutation_authorized"])
            with self.assertRaises(FileExistsError):
                write_phase9_demo_runtime_authority(
                    result,
                    out_dir=root,
                    design=design,
                    request=request,
                    session_arm=session_arm,
                    session_ready=session_ready,
                    execution_arm=execution_arm,
                    journal_rows=[],
                )

        source = inspect.getsource(runtime_authority)
        self.assertNotIn("MetaTrader5", source)
        self.assertNotIn("GatedMT5DemoMutationAdapter", source)
        self.assertNotIn("order_send", source)
        self.assertNotIn("mt5_mutation", source)


if __name__ == "__main__":
    unittest.main()
