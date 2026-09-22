from __future__ import annotations

import hashlib
import inspect
import io
import json
import unittest
from contextlib import redirect_stderr
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fmp.contracts import Direction, OrderIntent
from fmp.phase8b.design import MT5_BRIDGE_PROTOCOL, MT5_PROVIDER, MT5_TRANSPORT
from fmp.phase9.arming import (
    PHASE9_DEMO_EXECUTION_ARM_CONTRACT_READY,
    PHASE9_DEMO_EXECUTION_ARM_PROTOCOL,
    build_phase9_demo_execution_arm,
    validate_phase9_demo_execution_arm,
    write_phase9_demo_execution_arm,
)
from fmp.phase9.cli import build_parser
from fmp.phase9.design import (
    PHASE9_DEMO_DESIGN_FROZEN,
    PHASE9_DEMO_DESIGN_PROTOCOL,
    PHASE9_EXPERIMENT_ID,
    PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
)
from fmp.phase9.protocol import build_phase9_demo_order_request
from fmp.phase9.session import (
    build_phase9_demo_session_arm,
    build_phase9_demo_session_ready,
)
from fmp.risk import RiskConfig


UTC = timezone.utc
NOW = datetime(2026, 9, 22, 18, 0, tzinfo=UTC)
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
        "champion_set_id": "phase9-dec060-test",
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
        decision_id="decision-060",
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
    session_arm = build_phase9_demo_session_arm(
        design=design,
        request=request,
        not_before_utc=NOW - timedelta(minutes=5),
        expires_at_utc=NOW + timedelta(hours=2),
        operator_approval_reference="approval-fixture-060",
    )
    session_ready = build_phase9_demo_session_ready(
        design=design,
        request=request,
        arm=session_arm,
        local_requests=[request],
        broker_orders=[],
        broker_positions=[],
        now_utc=NOW,
        daily_halt_active=False,
    )
    return design, request, session_arm, session_ready


class Phase9DemoExecutionArmTests(unittest.TestCase):
    def test_arm_contract_is_deterministic_and_copies_exact_session_identity(self) -> None:
        design, request, session_arm, session_ready = _inputs()
        kwargs = {
            "design": design,
            "request": request,
            "session_arm": session_arm,
            "session_ready": session_ready,
            "code_commit": COMMIT,
        }
        first = build_phase9_demo_execution_arm(**kwargs)
        second = build_phase9_demo_execution_arm(**kwargs)
        self.assertEqual(first, second)
        self.assertEqual(first["protocol"], PHASE9_DEMO_EXECUTION_ARM_PROTOCOL)
        self.assertEqual(
            first["outcome"],
            PHASE9_DEMO_EXECUTION_ARM_CONTRACT_READY,
        )
        self.assertEqual(
            first["not_before_utc"],
            session_arm["not_before_utc"],
        )
        self.assertEqual(
            first["expires_at_utc"],
            session_arm["expires_at_utc"],
        )
        self.assertEqual(
            first["operator_approval_reference"],
            session_arm["operator_approval_reference"],
        )
        self.assertEqual(first["max_new_orders"], 1)
        self.assertTrue(first["practice_only"])
        self.assertTrue(first["demo_execution_arm_artifact_ready"])
        for field in (
            "demo_execution_source_armed",
            "demo_execution_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "phase10_authorized",
        ):
            self.assertFalse(first[field])
        validate_phase9_demo_execution_arm(first, **{
            "design": design,
            "request": request,
            "session_arm": session_arm,
            "session_ready": session_ready,
        })

        parameters = inspect.signature(
            build_phase9_demo_execution_arm
        ).parameters
        for forbidden in (
            "not_before_utc",
            "expires_at_utc",
            "operator_approval_reference",
            "account_fingerprint",
            "server",
            "symbol",
            "units",
        ):
            self.assertNotIn(forbidden, parameters)

    def test_mismatched_session_ready_fails_closed_even_if_refingerprinted(self) -> None:
        design, request, session_arm, session_ready = _inputs()
        changed = dict(session_ready)
        changed["request_fingerprint"] = "8" * 64
        changed.pop("session_ready_fingerprint")
        changed["session_ready_fingerprint"] = _digest(changed)
        with self.assertRaisesRegex(ValueError, "request_fingerprint"):
            build_phase9_demo_execution_arm(
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=changed,
                code_commit=COMMIT,
            )

    def test_already_armed_source_fails_closed(self) -> None:
        design, request, session_arm, session_ready = _inputs()
        with patch("fmp.phase9.arming.DEMO_EXECUTION_SOURCE_ARMED", True):
            with self.assertRaisesRegex(ValueError, "requires demo execution unarmed"):
                build_phase9_demo_execution_arm(
                    design=design,
                    request=request,
                    session_arm=session_arm,
                    session_ready=session_ready,
                    code_commit=COMMIT,
                )

    def test_tampered_approval_reference_fails_even_if_refingerprinted(self) -> None:
        design, request, session_arm, session_ready = _inputs()
        value = build_phase9_demo_execution_arm(
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            code_commit=COMMIT,
        )
        changed = dict(value)
        changed["operator_approval_reference"] = "different-approval"
        changed.pop("execution_arm_fingerprint")
        changed["execution_arm_fingerprint"] = _digest(changed)
        with self.assertRaisesRegex(ValueError, "operator_approval_reference"):
            validate_phase9_demo_execution_arm(
                changed,
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
            )

    def test_writer_is_create_only_and_authorizes_nothing(self) -> None:
        design, request, session_arm, session_ready = _inputs()
        value = build_phase9_demo_execution_arm(
            design=design,
            request=request,
            session_arm=session_arm,
            session_ready=session_ready,
            code_commit=COMMIT,
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_phase9_demo_execution_arm(
                value,
                out_dir=root,
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
            )
            self.assertTrue((root / "execution-arm.json").is_file())
            self.assertTrue((root / "manifest.json").is_file())
            self.assertFalse(manifest["demo_execution_source_armed"])
            self.assertFalse(manifest["demo_order_authorized"])
            with self.assertRaises(FileExistsError):
                write_phase9_demo_execution_arm(
                    value,
                    out_dir=root,
                    design=design,
                    request=request,
                    session_arm=session_arm,
                    session_ready=session_ready,
                )

    def test_phase9_cli_still_has_no_arm_or_execution_command(self) -> None:
        parser = build_parser()
        for forbidden in ("arm-demo", "run-demo", "submit-order", "broker"):
            with self.subTest(forbidden=forbidden):
                with redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        parser.parse_args([forbidden])


if __name__ == "__main__":
    unittest.main()
