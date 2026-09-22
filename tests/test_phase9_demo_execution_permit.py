from __future__ import annotations

import hashlib
import inspect
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fmp.phase9.permit as permit_module
from fmp.phase9.permit import (
    PHASE9_DEMO_EXECUTION_PERMIT_CONTRACT_READY,
    PHASE9_DEMO_EXECUTION_PERMIT_PROTOCOL,
    build_phase9_demo_execution_permit,
    validate_phase9_demo_execution_permit,
    write_phase9_demo_execution_permit,
)


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


def _inputs():
    design = {
        "demo_design_fingerprint": "1" * 64,
        "champion_set_fingerprint": "2" * 64,
        "execution_path": {
            "account_fingerprint": "3" * 64,
            "server": "FPMarketsSC-Demo",
        },
    }
    request = {
        "request_fingerprint": "4" * 64,
        "client_order_id": "fmp9-permit-fixture",
        "strategy_fingerprint": "5" * 64,
        "symbol": "EURUSD",
    }
    session_arm = {"session_arm_fingerprint": "6" * 64}
    session_ready = {"session_ready_fingerprint": "7" * 64}
    execution_arm = {
        "execution_arm_fingerprint": "8" * 64,
        "not_before_utc": "2026-09-22T18:00:00Z",
        "expires_at_utc": "2026-09-22T20:00:00Z",
        "operator_approval_reference": "approval-fixture-064",
    }
    runtime_authority = {"runtime_authority_fingerprint": "9" * 64}
    checked_request = {
        "action": "TRADE_ACTION_DEAL",
        "symbol": "EURUSD",
        "volume": 0.1,
        "type": "ORDER_TYPE_BUY",
        "price": 1.1,
        "sl": 1.095,
        "tp": 1.11,
        "deviation": 0,
        "type_time": "ORDER_TIME_GTC",
        "type_filling": "ORDER_FILLING_RETURN",
        "comment": "fmp9-permit-fixture",
    }
    launch_preflight = {
        "launch_preflight_fingerprint": "a" * 64,
        "launch_preflight_time_utc": "2026-09-22T19:00:00Z",
        "order_check_request": {
            "order_check_request_fingerprint": "b" * 64,
            "mt5_request": checked_request,
        },
        "order_check": {
            "order_check_fingerprint": "c" * 64,
            "check_passed": True,
        },
        "reconciliation": {
            "reconciliation_fingerprint": "d" * 64,
            "healthy": True,
        },
        "journal_event_count": 0,
        "journal_tip_fingerprint": None,
        "demo_launch_preflight_ready": True,
        "order_check_performed": True,
        "order_send_attempted": False,
        "send_attempt_count": 0,
        "daily_halt_active": False,
    }
    return (
        design,
        request,
        session_arm,
        session_ready,
        execution_arm,
        runtime_authority,
        launch_preflight,
    )


class Phase9DemoExecutionPermitTests(unittest.TestCase):
    def _build(self):
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch_preflight,
        ) = _inputs()
        with patch(
            "fmp.phase9.permit.validate_phase9_demo_launch_preflight"
        ):
            result = build_phase9_demo_execution_permit(
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                runtime_authority=runtime_authority,
                launch_preflight=launch_preflight,
                journal_rows=[],
                code_commit=COMMIT,
            )
        return (
            result,
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch_preflight,
        )

    def test_permit_binds_exact_checked_request_and_authorizes_nothing(self) -> None:
        (
            result,
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch_preflight,
        ) = self._build()
        self.assertEqual(
            result["protocol"],
            PHASE9_DEMO_EXECUTION_PERMIT_PROTOCOL,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_DEMO_EXECUTION_PERMIT_CONTRACT_READY,
        )
        self.assertEqual(
            result["launch_preflight_fingerprint"],
            launch_preflight["launch_preflight_fingerprint"],
        )
        self.assertEqual(
            result["checked_mt5_request_sha256"],
            _digest(launch_preflight["order_check_request"]["mt5_request"]),
        )
        self.assertEqual(result["max_new_orders"], 1)
        self.assertTrue(result["practice_only"])
        self.assertTrue(result["demo_execution_permit_artifact_ready"])
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

        with patch(
            "fmp.phase9.permit.validate_phase9_demo_launch_preflight"
        ):
            validate_phase9_demo_execution_permit(
                result,
                design=design,
                request=request,
                session_arm=session_arm,
                session_ready=session_ready,
                execution_arm=execution_arm,
                runtime_authority=runtime_authority,
                launch_preflight=launch_preflight,
                journal_rows=[],
            )

    def test_checked_request_mutation_fails_even_if_launch_input_is_accepted(self) -> None:
        (
            result,
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch_preflight,
        ) = self._build()
        changed_launch = dict(launch_preflight)
        changed_launch["order_check_request"] = dict(
            launch_preflight["order_check_request"]
        )
        changed_launch["order_check_request"]["mt5_request"] = dict(
            launch_preflight["order_check_request"]["mt5_request"]
        )
        changed_launch["order_check_request"]["mt5_request"]["volume"] = 0.2
        with patch(
            "fmp.phase9.permit.validate_phase9_demo_launch_preflight"
        ):
            with self.assertRaisesRegex(
                ValueError,
                "checked_mt5_request_sha256 mismatch",
            ):
                validate_phase9_demo_execution_permit(
                    result,
                    design=design,
                    request=request,
                    session_arm=session_arm,
                    session_ready=session_ready,
                    execution_arm=execution_arm,
                    runtime_authority=runtime_authority,
                    launch_preflight=changed_launch,
                    journal_rows=[],
                )

    def test_failed_launch_state_and_armed_source_fail_closed(self) -> None:
        (
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch_preflight,
        ) = _inputs()

        changed = dict(launch_preflight)
        changed["order_send_attempted"] = True
        with patch(
            "fmp.phase9.permit.validate_phase9_demo_launch_preflight"
        ):
            with self.assertRaisesRegex(ValueError, "already attempted"):
                build_phase9_demo_execution_permit(
                    design=design,
                    request=request,
                    session_arm=session_arm,
                    session_ready=session_ready,
                    execution_arm=execution_arm,
                    runtime_authority=runtime_authority,
                    launch_preflight=changed,
                    journal_rows=[],
                    code_commit=COMMIT,
                )

        with (
            patch(
                "fmp.phase9.permit.validate_phase9_demo_launch_preflight"
            ),
            patch("fmp.phase9.permit.DEMO_EXECUTION_SOURCE_ARMED", True),
        ):
            with self.assertRaisesRegex(ValueError, "source unarmed"):
                build_phase9_demo_execution_permit(
                    design=design,
                    request=request,
                    session_arm=session_arm,
                    session_ready=session_ready,
                    execution_arm=execution_arm,
                    runtime_authority=runtime_authority,
                    launch_preflight=launch_preflight,
                    journal_rows=[],
                    code_commit=COMMIT,
                )

    def test_writer_is_create_only(self) -> None:
        (
            result,
            design,
            request,
            session_arm,
            session_ready,
            execution_arm,
            runtime_authority,
            launch_preflight,
        ) = self._build()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch(
                "fmp.phase9.permit.validate_phase9_demo_launch_preflight"
            ):
                manifest = write_phase9_demo_execution_permit(
                    result,
                    out_dir=root,
                    design=design,
                    request=request,
                    session_arm=session_arm,
                    session_ready=session_ready,
                    execution_arm=execution_arm,
                    runtime_authority=runtime_authority,
                    launch_preflight=launch_preflight,
                    journal_rows=[],
                )
            self.assertTrue((root / "execution-permit.json").is_file())
            self.assertTrue((root / "manifest.json").is_file())
            self.assertFalse(manifest["demo_execution_source_armed"])
            self.assertFalse(manifest["broker_mutation_authorized"])
            with patch(
                "fmp.phase9.permit.validate_phase9_demo_launch_preflight"
            ):
                with self.assertRaises(FileExistsError):
                    write_phase9_demo_execution_permit(
                        result,
                        out_dir=root,
                        design=design,
                        request=request,
                        session_arm=session_arm,
                        session_ready=session_ready,
                        execution_arm=execution_arm,
                        runtime_authority=runtime_authority,
                        launch_preflight=launch_preflight,
                        journal_rows=[],
                    )

    def test_permit_source_has_no_broker_or_order_runner_dependency(self) -> None:
        source = inspect.getsource(permit_module)
        self.assertNotIn("MetaTrader5", source)
        self.assertNotIn("GatedMT5DemoMutationAdapter", source)
        self.assertNotIn("mt5_mutation", source)
        self.assertNotIn("backend.", source)
        self.assertNotIn("order_send(", source)

        parameters = inspect.signature(
            build_phase9_demo_execution_permit
        ).parameters
        for forbidden in (
            "units",
            "volume",
            "stop_price",
            "target_price",
            "account_fingerprint",
            "server",
            "symbol",
            "operator_approval_reference",
            "not_before_utc",
            "expires_at_utc",
        ):
            self.assertNotIn(forbidden, parameters)


if __name__ == "__main__":
    unittest.main()
